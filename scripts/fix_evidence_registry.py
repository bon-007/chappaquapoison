#!/usr/bin/env python3
"""
fix_evidence_registry.py — Comprehensive evidence registry data quality fix.

Implements all 10 recommendations:
1. Replace opaque ExXX_ IDs with human-readable labels
2. Fix all titles (remove filename artifacts, make plain English)
3. Fix all descriptions (replace generic templates with specific content)
4. Consolidate duplicate categories and tiers
5. Fill phase gaps using evidence_map.json
6. Fix Tedla references
7. Add post_titles for cross-reference display
8. Standardize file_type values

⚠ DEPRECATED: This script's data has been absorbed into evidence_index_canonical.json.
To update evidence data, edit directly in canonical and re-run: python3 scripts/build_canonical_evidence_index.py
"""
import json, re, sys
from pathlib import Path

# ─── Load data ───────────────────────────────────────────────────────────────
with open('evidence_metadata.json') as f:
    registry = json.load(f)

with open('evidence_map.json') as f:
    emap = json.load(f)

with open('posts.json') as f:
    posts_data = json.load(f)

# Build post title lookup: "9" → "Lithium: Six Times the Reference Range"
post_titles = {}
for p in posts_data.get('posts', []):
    pid = str(p.get('id', ''))
    title = p.get('title', '')
    post_titles[pid] = title
    # Also store without P prefix
    if pid.startswith('P'):
        post_titles[pid[1:]] = title

# ─── 1. Build ExXX → canonical ID mapping ───────────────────────────────────
# From evidence_map's file_id_to_canonical
ex_to_canonical = emap.get('file_id_to_canonical', {})

# Also build reverse: canonical_id → evidence_map entry
canonical_entries = emap.get('canonical_ids', {})

# Build file_path → canonical mapping from evidence_map
filepath_to_canonical = {}
for cid, entry in canonical_entries.items():
    for fp in entry.get('files_on_disk', []):
        filepath_to_canonical[fp] = cid

# ─── 2. Category consolidation ──────────────────────────────────────────────
CATEGORY_MAP = {
    'Lab Reports': 'Lab Reports & Toxicology',
    'Lab Reports & Toxicology': 'Lab Reports & Toxicology',
    'Photos & Documents': 'Photos & Documents',
    'Motions': 'Court Filings',  # fold small category into Court Filings
    'iMessage Records': 'Communications',  # merge into Communications
}

# ─── 3. Reliability tier consolidation ───────────────────────────────────────
TIER_MAP = {
    'Documentary': 'Documented Record',  # merge 4-item tier
    'Court Filing': 'Court-Certified',   # was being used as both cat and tier
}

# ─── 4. Category from evidence_map letter codes ─────────────────────────────
EMAP_CATEGORY = {
    'A': 'Lab Reports & Toxicology',
    'B': 'Court Orders & Judgments',
    'C': 'Witness Declarations & Depositions',
    'D': 'Communications & Messages',
    'E': 'Police Reports & Investigations',
    'F': 'Published Media',
    'G': 'Compiled Court Exhibits',
    'H': 'Structural Complaints',
}

# ─── 5. Phase mapping from evidence_map ──────────────────────────────────────
# Map post numbers to phases based on the blog's chronological structure
POST_TO_PHASE = {
    # Phase I: Origins (2010-2017) - Posts 1-8
    '1': 'I', '2': 'I', '3': 'I', '4': 'I', '5': 'I', '6': 'I', '7': 'I', '8': 'I',
    # Phase II: Poisoning Discovery (2018) - Posts 9-23
    '9': 'II', '10': 'II', '11': 'II', '12': 'II', '13': 'II', '14': 'II',
    '15': 'II', '16': 'II', '17': 'II', '18': 'II', '19': 'II', '20': 'II',
    '21': 'II', '22': 'II', '22B': 'II', '23': 'II',
    # Phase III: Custody & Legal (2018-2019) - Posts 24-35
    '24': 'III', '25': 'III', '26': 'III', '27': 'III', '28': 'III', '29': 'III',
    '30': 'III', '31': 'III', '32': 'III', '33': 'III', '34': 'III', '35': 'III',
    # Phase IV: Court & Depositions (2019-2022) - Posts 36-50
    '36': 'IV', '37': 'IV', '38': 'IV', '39': 'IV', '40': 'IV', '41': 'IV',
    '41B': 'IV', '41C': 'IV', '41D': 'IV', '41E': 'IV', '41F': 'IV',
    '41G': 'IV', '41H': 'IV', '42': 'IV', '43': 'IV', '44': 'IV', '45': 'IV',
    '46': 'IV', '47': 'IV', '48': 'IV', '48B': 'IV', '48C': 'IV',
    '49': 'IV', '50': 'IV',
    # Phase V: Trial & Verdict (2022-2026) - Posts 51+
    '51': 'V', '52': 'V', '53': 'V', '54': 'V', '55': 'V', '56': 'V',
    '57': 'V', '58': 'V', '59': 'V', '60': 'V', '61': 'V', '62': 'V',
    '63': 'V', '64': 'V', '65': 'V', '66': 'V',
}

# ─── 6. Title fixes ─────────────────────────────────────────────────────────
def fix_title(title, exhibit_id, file_path):
    """Fix filename-derived titles to be human-readable."""
    # First check if evidence_map has a better title
    if exhibit_id in canonical_entries:
        return canonical_entries[exhibit_id]['title']

    # Check if the ExXX code maps to a canonical entry
    ex_prefix = re.match(r'^(Ex\w+_\d+)', exhibit_id)
    if ex_prefix:
        ex_code = ex_prefix.group(1)
        if ex_code in ex_to_canonical:
            cid = ex_to_canonical[ex_code]
            if cid in canonical_entries:
                return canonical_entries[cid]['title']

    # Manual title fixes for common patterns
    TITLE_FIXES = {
        'Worksforus Email': '"It Works for Us" Email — Walsh Family, June 2018',
        'Afc Jackman Billing Records': 'Attorney for the Child Billing Records — Jennifer Jackman',
        'Tedla Nanny Deposition': 'Abrehet Tedla Deposition — Nanny Eyewitness Testimony',
        'Tedla Cfs Supervisor Deposition': 'Abrehet Tedla Deposition — CFS Supervisor Testimony',
        'Tedla Deposition Medication': 'Abrehet Tedla Declaration — Medication Observations',
        '2018 07 09 Filed Declaration Of Abrehet Tedla': 'Abrehet Tedla Declaration — July 9, 2018 (DVRO Filing)',
        'Walsh Texts Pre': 'Stephen Walsh Sr. Text Messages — Pre-May 2018',
        'Gun Lie Text Rashmi': 'Text Messages re: False Gun Allegation — Rashmi, May 2018',
        'Kiara Text Message Lithium': 'Kiara Text Message — Lithium Discussion',
        'Walsh Dv 120 Response': 'Tara Walsh DV-120 Response — Admits Drugging',
        'Walsh DV-120 Response': 'Tara Walsh DV-120 Response — Admits Drugging',
        'Key Text Messages Compilation': 'Key Text Messages Compilation — Walsh/Russell',
        'Walsh Russell Conversations Screenshots': 'Walsh-Russell Conversation Screenshots',
        'Due Diligence Report': 'Gavish Due Diligence Report',
        'Tara Walsh Email to Gavish': 'Tara Walsh Email to Gavish — March 2018',
        'Tara Threats Compilation': 'Tara Walsh Threats Compilation',
        'Fbi Criminal Complaint Support': 'FBI Criminal Complaint — Supporting Documents, August 2021',
        'Farquharson Corruption Investigation': 'Farquharson Federal Corruption Investigation',
        'Farquharson Bribery Connection': 'Farquharson Bribery Connection Documentation',
        'Morales Horowitz Judicial Ratings': 'Morales-Horowitz Judicial Ratings',
        'ChappaquaPoison Blog Archive': 'ChappaquaPoison.com Blog Archive',
        'Kidnapping Blog Evidence': 'Blog Evidence — Kidnapping Allegations',
        'Poisoning Blog Evidence': 'Blog Evidence — Poisoning Documentation',
        'Child Abuse Documentation': 'Blog Evidence — Child Abuse Documentation',
        'Visitation Obstruction Evidence': 'Blog Evidence — Visitation Obstruction',
        'Retaliation Whistleblower': 'Blog Evidence — Retaliation Against Whistleblower',
        'Court Order Violations': 'Blog Evidence — Court Order Violations',
        'Russell Turnure Nycjc Letter': 'Russell/Turnure Letter to NYC Judicial Commission',
        'Tara Drugged Me Email': '"Tara Drugged Me" Email',
        'Lamelle Visitation Order': 'LaMelle Supervised Visitation Order',
        'Financial Pay Stubs Health': 'Financial Records — Pay Stubs & Health Insurance',
        'Gavish Deposition Clip Key Testimony': 'Gavish Deposition — Key Testimony',
        'Stephen Walsh Sr. Declaration': 'Stephen Walsh Sr. Declaration — October 2021',
        'Dr. Gopal Letter': 'Dr. Gopal Letter — July 2018',
        'Domestication Affidavit 55523': 'NY Domestication Affidavit — File No. 55523',
        'Redwood Toxicology Drug Screen': 'Redwood Toxicology Drug Screen — March 2018',
        'Labcorp Heavy Metals Toxicology': 'LabCorp Heavy Metals Toxicology Report',
        'Sanctions Motion Attorney Threats': 'Sanctions Motion — Attorney Threats',
        'Voicemail Exhibit Stephen Walsh Threat': 'Stephen Walsh Sr. Voicemail Threat',
        'Tara Admits Drugging To Dr Gopal': 'Tara Walsh Admits Drugging to Dr. Gopal',
        'Russell Declaration Court Ready': 'Russell Declaration — Court-Ready Version',
        'Russell Declaration 2026': 'Russell Declaration — 2026',
        'Support Modification Affidavit': 'Support Modification Affidavit',
        'Westchester Support Dec2025': 'Westchester Support Filing — December 2025',
        'Motion To Vacate 2026': 'Motion to Vacate — 2026',
        'Superset Working Draft': 'SUPERSET Working Draft Compilation',
        'Gelhaar Declaration Dvro': 'Gelhaar Declaration — DVRO Proceedings',
        'Tara Walsh Declaration Oct2021': 'Tara Walsh Declaration — October 2021',
        'Subpoena Enforcement Stephen Walsh': 'Subpoena Enforcement — Stephen Walsh Sr.',
        'Otsc Russell V Stephen Walsh': 'Order to Show Cause — Russell v. Stephen Walsh',
        'Demand For Prosecution Tara Walsh': 'Demand for Criminal Prosecution — Tara Walsh',
        'Summary Crime Ny Jan2018': 'Crime Summary — New York, January 2018',
        'Tara Appellate Brief Implied Consent': 'Tara Walsh Appellate Brief — "Implied Consent" Argument',
        'Tara Walsh Declaration Kidnapping Osc Mar2022': 'Tara Walsh Declaration — Kidnapping OSC, March 2022',
        'Tara Top Violation Entrapment': 'Tara Walsh — TOP Violation & Entrapment',
        'Reconsideration Motion Oct2025': 'Motion for Reconsideration — October 2025',
        'Russell Declaration Oct2025': 'Russell Declaration — October 2025',
        'Brienne Walsh Affidavit': 'Brienne Walsh Affidavit',
        'Lamelle Affidavit Sheer Fright': 'LaMelle Affidavit — "Sheer Fright" Incident',
        'Gelhaar Declaration Text': 'Gelhaar Declaration — Text Version',
        'San Francisco Dv Order Key Pages': 'San Francisco DV Order — Key Pages',
        'California Epo Jul2018': 'California Emergency Protective Order — July 2018',
        'Sf Dv Trial Transcript Aug2018': 'San Francisco DV Trial Transcript — August 2018',
        'Sf Battery Trial Transcript Part2': 'San Francisco Battery Trial Transcript — Part 2',
    }

    if title in TITLE_FIXES:
        return TITLE_FIXES[title]

    # Generic cleanup: Title Case artifacts from filenames
    # Remove "Ex" prefixes at start if they look like codes
    cleaned = title
    # Fix "Sf" → "San Francisco", "Ny" → "New York", "Ca" → "California"
    cleaned = re.sub(r'\bSf\b', 'San Francisco', cleaned)
    cleaned = re.sub(r'\bNy\b', 'New York', cleaned)
    cleaned = re.sub(r'\bCa\b', 'California', cleaned)
    cleaned = re.sub(r'\bAfc\b', 'AFC', cleaned)
    cleaned = re.sub(r'\bDvro\b', 'DVRO', cleaned)
    cleaned = re.sub(r'\bDv\b', 'DV', cleaned)
    cleaned = re.sub(r'\bFbi\b', 'FBI', cleaned)
    cleaned = re.sub(r'\bOasas\b', 'OASAS', cleaned)
    cleaned = re.sub(r'\bNycjc\b', 'NYCJC', cleaned)
    cleaned = re.sub(r'\bOsc\b', 'OSC', cleaned)
    cleaned = re.sub(r'\bOtsc\b', 'OTSC', cleaned)
    cleaned = re.sub(r'\bCfs\b', 'CFS', cleaned)
    cleaned = re.sub(r'\bCasac\b', 'CASAC', cleaned)
    cleaned = re.sub(r'\bPd\b', 'PD', cleaned)
    cleaned = re.sub(r'\bTop\b', 'TOP', cleaned)
    cleaned = re.sub(r'\bGpl\b', 'GPL', cleaned)
    cleaned = re.sub(r'\bOcr\b', '(OCR)', cleaned)
    cleaned = re.sub(r'\bBpd\b', 'BPD', cleaned)
    cleaned = re.sub(r'\bUccjea\b', 'UCCJEA', cleaned)
    cleaned = re.sub(r'\bIwo\b', 'IWO', cleaned)
    cleaned = re.sub(r'\bAtros\b', 'ATROS', cleaned)
    cleaned = re.sub(r'\bNcadd\b', 'NCADD', cleaned)

    # Fix date patterns: "Oct2021" → "October 2021"
    month_map = {
        'Jan': 'January', 'Feb': 'February', 'Mar': 'March', 'Apr': 'April',
        'May': 'May', 'Jun': 'June', 'Jul': 'July', 'Aug': 'August',
        'Sep': 'September', 'Oct': 'October', 'Nov': 'November', 'Dec': 'December'
    }
    for abbr, full in month_map.items():
        cleaned = re.sub(rf'\b{abbr}(\d{{4}})\b', rf'{full} \1', cleaned)
        cleaned = re.sub(rf'\b{abbr}(\d{{1,2}})[\s_](\d{{4}})\b', rf'{full} \1, \2', cleaned)

    return cleaned


# ─── 7. Description generation ───────────────────────────────────────────────
GENERIC_DESCRIPTIONS = {
    'Court filing in Russell v. Walsh proceedings',
    'Court hearing transcript',
    'Evidence related to drugging allegations',
    'Written correspondence',
    'Video or audio recording',
    'Blog content from Brienne Walsh publications',
    'Text message evidence',
    'Email correspondence',
    'Deposition video clip excerpt',
    'Court judgment or verdict document',
    'Declaration by Abrehet Tedla (former nanny)',
    'Tedla deposition discussing medication observations',
    'Blog post about court proceedings',
}

def generate_description(entry, file_path, exhibit_id):
    """Generate a specific description based on file path, title, and context."""
    title = entry.get('title', '')
    cat = entry.get('category', '')
    fp = file_path

    # Check evidence_map for description hints
    if exhibit_id in canonical_entries:
        emap_title = canonical_entries[exhibit_id].get('title', '')
        if emap_title and len(emap_title) > len(title):
            return emap_title

    # File-path-based descriptions
    fname = Path(fp).stem if fp else ''

    # Deposition clips
    if 'Gavish' in fname and 'clip' in fname.lower():
        clip_part = re.search(r'clip_(\d+)', fname)
        clip_num = clip_part.group(1) if clip_part else ''
        return f'Video excerpt from the Gavish deposition — clip {clip_num}.' if clip_num else 'Video excerpt from the Gavish deposition testimony.'

    if 'Tedla' in fname or 'tedla' in fname.lower():
        if 'CFS' in fname:
            return 'Deposition of Abrehet Tedla (Evie\'s nanny in San Francisco) regarding CFS supervisor observations.'
        if 'declaration' in fname.lower():
            return 'Sworn declaration by Abrehet Tedla (Evie\'s nanny in San Francisco) detailing witnessed drugging of Russell by Tara Walsh.'
        return 'Testimony from Abrehet Tedla, Evie\'s nanny in San Francisco, who witnessed Tara Walsh drugging Russell.'

    if 'Walsh_Sr' in fname or 'Stephen_Walsh' in fname:
        if 'Depo' in fname:
            return 'Deposition testimony of Stephen Walsh Sr. (Tara\'s father) in custody proceedings.'
        if 'Declaration' in fname:
            return 'Sworn declaration by Stephen Walsh Sr. filed in court proceedings.'
        if 'Voicemail' in fname or 'Threat' in fname:
            return 'Voicemail recording of Stephen Walsh Sr. making threats against Russell\'s legal counsel.'
        if 'Texts' in fname:
            return 'Text messages from/to Stephen Walsh Sr. related to the custody dispute.'
        if 'Evaded' in fname:
            return 'Sheriff\'s certificate documenting Stephen Walsh Sr.\'s evasion of service of process.'

    if 'Brienne' in fname or 'brienne' in fname.lower():
        if 'Depo' in fname:
            return 'Deposition testimony of Brienne Walsh (Tara\'s sister) regarding family abuse and CPS history.'
        if 'Blog' in fname or 'Post' in fname:
            return 'Blog post by Brienne Walsh documenting Walsh family dynamics and childhood abuse.'
        if 'Letter' in fname:
            return 'Letter from Brienne Walsh to the court or family regarding the Walsh custody case.'
        if 'Affidavit' in fname:
            return 'Sworn affidavit from Brienne Walsh regarding family history.'

    if 'Tara' in fname or 'tara' in fname.lower():
        if 'Extortion' in fname:
            return 'Text messages from Tara Walsh conditioning access to Evie on financial payment.'
        if 'Declaration' in fname:
            return 'Sworn declaration by Tara Walsh filed in custody proceedings.'
        if 'Admits' in fname or 'Drugging' in fname:
            return 'Documentation of Tara Walsh\'s admission of administering drugs to Russell without his consent.'
        if 'Threat' in fname:
            return 'Compilation of threatening communications from Tara Walsh.'

    if 'Griffin' in fname:
        if 'CASAC' in fname:
            return 'Griffin\'s CASAC (substance abuse counselor) credential documentation.'
        if 'License' in fname or 'Surrender' in fname:
            return 'Documentation of Griffin\'s professional license surrender, reported by Lohud/Journal News.'
        if 'Stipulation' in fname:
            return 'Settlement stipulation involving Griffin\'s professional conduct.'
        if 'Gating' in fname:
            return 'Emails showing Griffin used visitation as a gating condition in her role as evaluator.'
        if 'Report' in fname:
            return 'Griffin\'s court-ordered evaluation report.'

    if 'GordonOliver' in fname or 'Gordon_Oliver' in fname:
        if 'Transcript' in fname or 'Hearing' in fname:
            date = re.search(r'(\w+\d+_\d{4})', fname)
            return f'Hearing transcript from Judge Gordon-Oliver\'s court proceedings.'
        if 'Custody' in fname or 'Order' in fname:
            return 'Judge Gordon-Oliver\'s custody order in Walsh v. Russell.'
        if 'Recus' in fname:
            return 'Documentation of Judge Gordon-Oliver\'s recusal from the case.'

    if 'Furman' in fname:
        if 'Transcript' in fname or 'Hearing' in fname:
            return 'Hearing transcript from Judge Furman\'s court in support/custody proceedings.'
        if 'Support' in fname:
            return 'Judge Furman\'s support order hearing transcript.'

    if 'Schauer' in fname:
        if 'Transcript' in fname or 'Hearing' in fname:
            return 'Hearing transcript from Judge Schauer\'s court proceedings.'
        if 'Vacatur' in fname:
            return 'Judge Schauer\'s vacatur of a prior default order.'
        if 'TempOP' in fname or 'Temp' in fname:
            return 'Judge Schauer\'s first appearance hearing regarding temporary order of protection.'

    if 'Humphrey' in fname:
        if 'Recusal' in fname:
            return 'Order documenting Judge Humphrey\'s recusal from the case.'
        return 'Hearing transcript from Judge Humphrey\'s court proceedings.'

    if 'Bowman' in fname:
        return 'Judge Bowman support hearing memorandum — February 2026.'

    if 'Mirror_Order' in fname:
        return 'Analysis of mirror orders issued across jurisdictions in the custody proceedings.'

    if 'Gag_Order' in fname or 'gag' in fname.lower():
        return 'Documentation of the gag order restricting Russell\'s speech about the case.'

    if 'Appellate' in fname or 'Appeal' in fname:
        if '214AD3d890' in fname:
            return 'Appellate Division ruling (214 AD3d 890) striking the gag order.'
        if 'Affirmed' in fname or 'A165356' in fname:
            return 'California Court of Appeal decision affirming the battery/IIED/DV jury verdict.'
        if 'Brief' in fname:
            return 'Appellate brief filed in the Walsh custody/DV proceedings.'

    if 'Verdict' in fname or 'Judgment' in fname:
        return 'San Francisco jury verdict and judgment in the battery/DV civil trial.'

    if 'Domestication' in fname:
        return 'Affidavit for domestication of the California judgment in New York courts.'

    if 'LabCorp' in fname or 'Heavy_Metal' in fname:
        return 'LabCorp heavy metals toxicology report documenting Russell\'s exposure levels.'

    if 'Redwood' in fname or 'Drug_Screen' in fname:
        return 'Redwood Toxicology drug screen results from March 2018.'

    if 'Drugging_Evidence' in fname:
        return 'Compiled evidence of the drugging — toxicology results, admissions, and witness testimony.'

    if 'Voicemail' in fname:
        return 'Voicemail recording filed as a court exhibit.'

    if 'Sanctions' in fname:
        return 'Sanctions motion documenting attorney misconduct and threats.'

    if 'Blog' in fname or 'Archive' in fname:
        return 'Archived blog content documenting the case chronologically.'

    if 'Kidnapping' in fname:
        return 'Documentation related to the kidnapping/abduction allegations in the custody dispute.'

    if 'DVRO' in fname or 'DV_Order' in fname or 'EPO' in fname:
        return 'Domestic violence restraining order documentation from San Francisco proceedings.'

    if 'Police' in fname or 'SFPD' in fname:
        return 'Police report or law enforcement documentation related to the case.'

    if 'Veneziano' in fname:
        return 'Correspondence documenting the Veneziano-Griffin pattern of coordinated misconduct.'

    if 'Spoliation' in fname:
        return 'Documentation of evidence spoliation (destruction or alteration of records).'

    if 'Guttridge' in fname:
        return 'Letter from Guttridge regarding observations of Evie\'s welfare.'

    if 'Enenstein' in fname:
        return 'Documentation of attorney Enenstein\'s withdrawal and related issues.'

    if 'Turnure' in fname:
        return 'Correspondence from Russell\'s attorney Turnure regarding the case.'

    if 'LaMelle' in fname or 'Lamelle' in fname:
        return 'Documentation of the LaMelle supervised visitation incident.'

    if 'Farquharson' in fname:
        return 'Records from the federal investigation into Farquharson\'s conduct.'

    if 'Complaint' in fname and 'RR' in exhibit_id:
        return 'Extract from the structural complaint documenting systemic court failures.'

    if 'Motion_to_Vacate' in fname:
        return 'Motion to vacate all prior orders in the Walsh custody proceedings.'

    if 'iMessage' in fname.lower() or 'IMSG' in exhibit_id:
        return 'iMessage conversation records relevant to the case.'

    # Fall back to category-based descriptions
    cat_descs = {
        'Court Filings': f'Court document filed in the Walsh v. Russell proceedings.',
        'Transcripts & Hearings': f'Official transcript of court proceedings.',
        'Correspondence': f'Correspondence related to the legal proceedings.',
        'Declarations & Affidavits': f'Sworn declaration filed in court.',
        'Video & Audio': f'Video or audio recording filed as evidence.',
        'Lab Reports & Toxicology': f'Laboratory test results documenting toxic substance levels.',
        'Published Media': f'Published media content relevant to the case.',
        'Communications & Messages': f'Communications documentation.',
        'Photos & Documents': f'Photographic or documentary evidence.',
    }
    return cat_descs.get(cat, f'Evidence document in the Walsh v. Russell proceedings.')


# ─── 8. Human-readable exhibit label ────────────────────────────────────────
def make_readable_id(exhibit_id, file_path):
    """Convert opaque ExXX_ codes to human-readable labels."""
    # Already canonical (A-1, B-9, C-6, etc.)
    if re.match(r'^[A-H]-\d+', exhibit_id):
        return exhibit_id

    # Check mapping
    ex_match = re.match(r'^(Ex\w+_\d+\w*)', exhibit_id)
    if ex_match:
        code = ex_match.group(1)
        if code in ex_to_canonical:
            return ex_to_canonical[code]

    # For unmapped ExXX codes, create a readable label
    # Extract the prefix letters
    prefix_match = re.match(r'^Ex([A-Z]+)_(\d+)([a-z]?)$', exhibit_id)
    if prefix_match:
        letters = prefix_match.group(1)
        num = prefix_match.group(2)
        suffix = prefix_match.group(3)

        # Map prefix letters to categories
        PREFIX_LABELS = {
            'A': 'Email',
            'AA': 'Financial',
            'B': 'Investigation',
            'BB': 'AFC Billing',
            'BCD': 'Messages',
            'C': 'Gun Allegation',
            'D': 'Text',
            'DD': 'Corruption',
            'E': 'Court Orders',
            'EE': 'Blog Archive',
            'F': 'Abuse Journal',
            'FF': 'Photos',
            'G': 'Verdict',
            'H': 'Trial Record',
            'HH': 'Supreme Court',
            'I': 'Toxicology',
            'J': 'Forensic',
            'JJ': 'Declaration',
            'K': 'Griffin License',
            'KK': 'FBI Complaint',
            'L': 'Custody Order',
            'M': 'Recantation',
            'N': 'Police Reports',
            'O': 'Attorney Letters',
            'OO': 'Exhibits Bundle',
            'P': 'AFC Records',
            'PP': 'Sworn Statements',
            'Q': 'Brienne Records',
            'QQ': 'Depositions',
            'R': 'Appellate',
            'RR': 'Structural Complaint',
            'S': 'Griffin CASAC',
            'SS': 'Pattern Evidence',
            'T': 'LaMelle',
            'TR': 'Transcript',
            'U': 'Gelhaar',
            'V': 'Brienne Depo',
            'W': 'Adderall Text',
            'X': 'Guttridge',
            'Y': 'CA Orders',
        }
        label = PREFIX_LABELS.get(letters, letters)
        return f'{label}-{num}{suffix}'

    # IMSG prefix
    if exhibit_id.startswith('IMSG-'):
        return exhibit_id.replace('IMSG-', 'iMsg-')

    # F- prefix (blog posts)
    if re.match(r'^F-\d+$', exhibit_id):
        return exhibit_id

    return exhibit_id


# ─── MAIN PROCESSING ────────────────────────────────────────────────────────
stats = {
    'titles_fixed': 0,
    'descriptions_fixed': 0,
    'ids_remapped': 0,
    'categories_consolidated': 0,
    'tiers_consolidated': 0,
    'phases_filled': 0,
    'file_types_fixed': 0,
    'post_titles_added': 0,
}

for path, entry in registry.items():
    old_id = entry.get('exhibit_id', '')
    fp = entry.get('file_path', path)
    old_title = entry.get('title', '')
    old_desc = entry.get('description', '')
    old_cat = entry.get('category', '')
    old_tier = entry.get('reliability', '')

    # 1. Fix exhibit ID
    new_id = make_readable_id(old_id, fp)
    if new_id != old_id:
        entry['exhibit_id'] = new_id
        entry['original_exhibit_id'] = old_id  # keep for reference
        stats['ids_remapped'] += 1

    # 2. Fix title
    new_title = fix_title(old_title, old_id, fp)
    if new_title != old_title:
        entry['title'] = new_title
        stats['titles_fixed'] += 1

    # 3. Fix description (if generic)
    if old_desc in GENERIC_DESCRIPTIONS or len(old_desc) < 30:
        new_desc = generate_description(entry, fp, old_id)
        if new_desc != old_desc:
            entry['description'] = new_desc
            stats['descriptions_fixed'] += 1

    # Fix Tedla references specifically
    if 'Tedla' in entry.get('description', '') or 'nanny' in entry.get('description', '').lower():
        desc = entry['description']
        desc = desc.replace('(former nanny)', "(Evie's nanny in San Francisco)")
        desc = desc.replace('former nanny', "Evie's nanny in San Francisco")
        if desc != entry['description']:
            entry['description'] = desc

    # 4. Consolidate categories
    if old_cat in CATEGORY_MAP:
        entry['category'] = CATEGORY_MAP[old_cat]
        stats['categories_consolidated'] += 1

    # 5. Consolidate tiers
    if old_tier in TIER_MAP:
        entry['reliability'] = TIER_MAP[old_tier]
        stats['tiers_consolidated'] += 1

    # 6. Fill phase gaps
    if not entry.get('phase'):
        # Try to infer from related posts
        related = entry.get('related_posts', [])
        if related:
            for post_id in related:
                pid = str(post_id).replace('P', '')
                if pid in POST_TO_PHASE:
                    entry['phase'] = POST_TO_PHASE[pid]
                    stats['phases_filled'] += 1
                    break

    # 7. Standardize file_type
    ft = entry.get('file_type', '')
    if ft == 'jpg':
        entry['file_type'] = 'photo'
        stats['file_types_fixed'] += 1

    # 8. Add post titles for cross-reference display
    related = entry.get('related_posts', [])
    if related:
        titles_list = []
        for pid in related:
            pid_str = str(pid).replace('P', '')
            pt = post_titles.get(pid_str, '')
            if pt:
                titles_list.append({'id': pid_str, 'title': pt})
            else:
                titles_list.append({'id': pid_str, 'title': f'Post {pid_str}'})
        entry['post_titles'] = titles_list
        stats['post_titles_added'] += 1


# ─── Save ────────────────────────────────────────────────────────────────────
with open('evidence_metadata.json', 'w') as f:
    json.dump(registry, f, indent=2)

print(f"\n✓ Registry updated: {len(registry)} entries")
print(f"  Titles fixed:          {stats['titles_fixed']}")
print(f"  Descriptions fixed:    {stats['descriptions_fixed']}")
print(f"  IDs remapped:          {stats['ids_remapped']}")
print(f"  Categories consolidated: {stats['categories_consolidated']}")
print(f"  Tiers consolidated:    {stats['tiers_consolidated']}")
print(f"  Phases filled:         {stats['phases_filled']}")
print(f"  File types fixed:      {stats['file_types_fixed']}")
print(f"  Post titles added:     {stats['post_titles_added']}")

# ─── Remaining gaps report ───────────────────────────────────────────────────
no_phase = sum(1 for v in registry.values() if not v.get('phase'))
no_posts = sum(1 for v in registry.values() if not v.get('related_posts'))
print(f"\n  Remaining without phase: {no_phase}")
print(f"  Remaining without posts: {no_posts}")
