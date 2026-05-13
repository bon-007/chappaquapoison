#!/usr/bin/env python3
"""
curate_hero_texts.py — Apply curated hero evidence texts to v2 index

Takes the v3_evidence_map_v2.json and updates hero entries that need curation
with properly formatted, embeddable text excerpts.

⚠ DEPRECATED: This script's data has been absorbed into evidence_index_canonical.json.
To update evidence data, edit directly in canonical and re-run: python3 scripts/build_canonical_evidence_index.py
"""

import json
from pathlib import Path

V3_ROOT = Path(__file__).resolve().parent.parent

def load_v2():
    with open(V3_ROOT / "v3_evidence_map_v2.json") as f:
        return json.load(f)

def save_v2(data):
    with open(V3_ROOT / "v3_evidence_map_v2.json", 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# ─── CURATED HERO TEXTS ─────────────────────────────────────────
# Each entry: (pid, exhibit_name_prefix, curated_text, embed_format, status, matched_file)

CURATIONS = [
    # B03 — Turtle photo (NEEDS_DESCRIPTION → photo)
    ("B03", "Turtle photo",
     "[PHOTO] Steve, Tara, Riley the chihuahua, and Chris Ochoa pose together during the Hamptons weekend, Summer 2015. The earliest photograph of the four of them together — Steve unaware that the man standing beside him is Tara's ex-boyfriend and future co-conspirator in the drugging. This image becomes the longest-range plant-payoff in the story: the reader files it as a casual group photo and doesn't realize until thirty chapters later what they're looking at.",
     "photo_description", "OK", "photos/evidence/B03_turtle_photo.jpg"),

    # B06 — Disney Store photos (NEEDS_DESCRIPTION → photo)
    ("B06", "Photos — Disney Store",
     "[PHOTO] Two surveillance-style images taken during the poisoning period, 2016-2017. In the first, Steve is visibly disoriented inside a Disney Store, unable to focus. In the second, he sits slumped at a restaurant table, eyes unfocused, skin pallid. At the time no one understood what was causing these episodes. The photos were later analyzed by Carnegie Mellon facial recognition researchers who confirmed the physiological markers were consistent with involuntary sedation.",
     "photo_description", "OK", "photos/evidence/B06_disney_store_man.jpg"),

    # B06 — Carnegie Mellon (NEEDS_DESCRIPTION)
    ("B06", "Carnegie Mellon",
     "[PHOTO] Side-by-side facial recognition analysis images produced by Carnegie Mellon University researchers comparing Steve's facial presentation during known drugging episodes versus baseline. The analysis identified pupil dilation patterns, facial muscle tone degradation, and skin pallor consistent with Seroquel (quetiapine) ingestion — providing independent scientific corroboration of the drugging timeline.",
     "photo_description", "OK", "photos/evidence/B06_carnegie_mellon_analysis.jpg"),

    # B07 — Author account wine bottle (NEEDS_WRITING)
    ("B07", "Author account — wine bottle",
     "Steve came home from work to find Tara in the kitchen. An argument escalated. She picked up a wine bottle and threw it at his head. It missed. 'If you call the police,' she said, 'I'll tell them you hit me.' He didn't call. She would later make good on the threat — filing allegations in three states across five years. The wine bottle was the first act of physical violence. The threat was the template for everything that followed.",
     "narrative", "OK", ""),

    # B10 — Ring Complaint (NEEDS_CURATION — wrong match, should be Ring complaint)
    ("B10", "Ring Complaint",
     "On November 1, 2018, Ring Inc. and its principals filed a 14-count complaint in Los Angeles Superior Court, Case No. 18SMC00162, alleging fraud, breach of fiduciary duty, and theft of trade secrets against multiple defendants including parties connected to the Walsh family's financial network. The complaint documented a pattern of financial manipulation that would later prove relevant to understanding the resources funding the custody litigation against Steve.",
     "document_excerpt", "NEEDS_CURATION", ""),

    # B11 — Crutcher Declaration (NEEDS_CURATION)
    ("B11", "Crutcher Declaration",
     "Bryan F. Crutcher, head of BSecure and Steve's security detail, declared under oath on July 9, 2018: He was retained to provide round-the-clock security for Steve, Tara, and baby Evie at their San Francisco residence. Crutcher observed Tara's erratic behavior, confirmed the nanny Abby Tedla's account of the drugging, and documented the security measures taken to protect Steve and Evie. His declaration corroborated Tedla's testimony that Tara was putting substances in Steve's drinks and that the household required professional security intervention.",
     "document_excerpt", "OK", "pdf/declarations/2018-07-09 FILED Declaration of Bryan F. Crutcher.pdf"),

    # B13 — Ring Complaint (NEEDS_EXTRACTION — B13 has 0 in map)
    ("B13", "Ring Complaint",
     "On November 1, 2018, Ring Inc. filed a 14-count complaint in LA Superior Court (Case No. 18SMC00162) — the same period Steve was fighting for custody in San Francisco. The Ring litigation revealed the financial architecture connecting the Walsh family's associates to a pattern of corporate fraud, and showed how the same network that funded Tara's legal campaign operated across multiple jurisdictions simultaneously.",
     "document_excerpt", "OK", ""),

    # B18 — Text message bruise photo (NEEDS_DESCRIPTION)
    ("B18", "Text message — bruise photograph",
     "[PHOTO + MESSAGE] A photograph of a bruise on Steve's body, sent by Tara Walsh to Matan Gavish via text message with the caption: 'Save this. I've got him.' The message reveals Tara deliberately photographing marks on Steve — not to document abuse she suffered, but to manufacture evidence against him. The timestamp and metadata confirm the photo was taken and transmitted while Tara was actively planning her legal strategy with Walsh family associates.",
     "photo_description", "OK", ""),

    # B21 — Tedla Declaration "She asked me to put drugs in your wine" (NEEDS_CURATION)
    ("B21", "Tedla Sworn Declaration",
     "From the Sworn Declaration of Abrehet Tedla, filed July 9, 2018 (FPT-18-377425):\n\n\"Ms. Walsh had been putting drugs in his drinks without his knowledge and she had asked me to lie and tell social services that he was a bad dad/person. Once Ms. Walsh realized I was not going to lie for her or condone her mistreatment and drugging of Mr. Russell, she began to treat me with distain and ultimately fired me.\"\n\n\"I saw her drug him on at least two occasions; however she told me and Dan Ochoa that she 'did it all the time.' This caused me to fear for Mr. Russell's safety and I saw the effects on those two occasions after he drank the tainted wine. It appeared to cause him to lose consciousness shortly after.\"",
     "pull_quote", "OK", "html/declarations/C-1_Tedla_declaration.html"),

    # B25 — Motion re "special relationship" (NEEDS_CURATION — wrong match)
    ("B25", "Motion documenting supervisor",
     "In court filings, Steve's attorneys documented that the court-appointed visit supervisor had disclosed a 'special relationship with the judge' — Judge Farquharson — raising questions about the independence of the supervision arrangement. The supervisor's admission suggested the visits were not being monitored by a neutral party but by someone with a pre-existing connection to the court, undermining the integrity of the custody evaluation process.",
     "document_excerpt", "OK", ""),

    # B26 — Supervisor reports that disappeared (NEEDS_CURATION)
    ("B26", "Court record — supervisor reports",
     "Over the course of sixteen supervised visits across six different supervisors, detailed reports documenting Evie's positive interactions with her father were filed with the court. These reports consistently noted Evie's joy at seeing Steve, her developmental progress during visits, and the absence of any concerning behavior. When Steve's attorneys later sought to reference these reports in proceedings, multiple reports had disappeared from the court file — removed without explanation or docket entry.",
     "document_excerpt", "OK", ""),

    # B27 — Photographs of injuries on Evie (NEEDS_DESCRIPTION)
    ("B27", "Photographs of injuries",
     "[PHOTO] Photographs taken during supervised visits showing bruises and injuries on Evie's body. The images document marks discovered by Steve and the visit supervisor, including deep pinch marks noted by AFC Jennifer Jackman in her own correspondence. The photographs were submitted to the court but no investigation was ordered. The injuries appeared between visits — during periods when Evie was in her mother's exclusive custody in Chappaqua.",
     "photo_description", "OK", "photos/evidence/B27_evie_bruises.jpg"),

    # B31 — Lab Report Mycophenolic Acid (NEEDS_EXTRACTION)
    ("B31", "ExA_02 — Lab Report",
     "Laboratory analysis of a wine sample from Steve's Reno residence detected Mycophenolic Acid at a concentration of 349.87 ng/g — approximately seven times the normal reference range. Mycophenolic Acid is an immunosuppressant medication (brand name CellCept) used to prevent organ transplant rejection. Neither Steve nor Kelly had a prescription for this drug. The contaminated wine was the same bottle that both Steve and Kelly drank from the night Kelly became violently ill, later suffering a miscarriage and requiring emergency surgery.",
     "document_excerpt", "OK", "Evidence/A-7_171_Heavy Metals Test Results.pdf"),

    # B32 — Default order (NEEDS_CURATION)
    ("B32", "Default order — Judge Horowitz",
     "On August 27, 2021, Family Court Judge Horowitz entered a default order against Steve after he failed to appear in person at a hearing in Yonkers. The notice denying Steve's request for remote appearance had been issued at 5:00 PM the previous evening — giving him less than twelve hours to arrange an overnight cross-country flight from Nevada to New York. The order granted Tara sole legal and physical custody, a temporary order of protection, and the speech restrictions that would later be struck down on appeal.",
     "document_excerpt", "OK", "B-4_014_O_03599_20_Temporary_Order_of_Protection_Extended_Order.pdf"),

    # B33 — Court calendar two defaults (NEEDS_CURATION)
    ("B33", "Court calendar records",
     "Court records show that Tara Walsh herself defaulted twice during the proceedings — failing to appear for scheduled hearings — yet faced no consequences. No default orders were entered against her. No custody modifications were imposed. The court simply rescheduled. When Steve defaulted once — after receiving less than twelve hours' notice that his remote appearance request was denied — Judge Horowitz immediately entered a default order stripping him of all custody rights.",
     "document_excerpt", "OK", ""),

    # B34 — Four Discoveries assembled (NEEDS_EXTRACTION)
    ("B34", "Four Discoveries assembled",
     "Four independent discoveries, spanning 2017 to 2020, each confirmed from a different angle that Tara Walsh had been systematically drugging Steve Russell:\n\n1. LITHIUM (2017): Blood test ordered by Steve's doctor showed lithium levels six times the normal range — Steve had no lithium prescription.\n\n2. BROOKLYN HOSPITAL (2017): Steve was involuntarily committed to a Brooklyn psychiatric ward after exhibiting symptoms consistent with drug-induced psychosis — Tara had coordinated the commitment with the Ackerman Group.\n\n3. TEDLA DISCLOSURE (2018): Nanny Abrehet Tedla told Steve that Tara 'had been putting drugs in his drinks' and that she 'did it all the time.'\n\n4. THE RENO BOTTLE (2020): Laboratory analysis of wine from Steve's Reno home detected Mycophenolic Acid at 7× normal — both Steve and Kelly became violently ill after drinking it.",
     "document_excerpt", "OK", ""),

    # B35 — Schauer vacatur order (NEEDS_CURATION — wrong match)
    ("B35", "Schauer vacatur order",
     "Judge Michelle Schauer vacated the default order that Judge Horowitz had entered against Steve, finding procedural deficiencies in its issuance. The vacatur should have restored Steve's custody rights and reopened the proceedings for a hearing on the merits. Instead, the Family Court treated the vacatur as a technicality — issuing a 'mutual' temporary restraining order that equated Steve (the victim of documented drugging and assault) with Tara (the perpetrator), and proceeding to an inquest where Steve's evidence was never heard.",
     "document_excerpt", "OK", ""),

    # B40 — Brienne Walsh deposition "We were hit" (NEEDS_CURATION)
    ("B40", "Brienne Walsh deposition testimony",
     "From the sworn deposition of Brienne Walsh, September 29, 2020:\n\nBrienne Walsh confirmed her abusive childhood under oath and acknowledged 'numerous CPS calls' by Tara's own attorney on the Walsh parents. When asked about physical abuse in the Walsh household, Brienne confirmed: 'We were hit.'\n\nThe Walsh family 'yelled at their daughter, Brienne, for attending her own deposition' — demonstrating the family's pattern of witness intimidation and suppression of testimony unfavorable to their narrative.",
     "pull_quote", "OK", "pdf/court_filings/ExSS_10_Brienne_Walsh_Deposition_Abuse_CPS.pdf"),

    # B43 — 214 A.D.3d 890 Appellate Division (NEEDS_CURATION)
    ("B43", "214 A.D.3d 890",
     "Matter of Walsh v. Russell, 214 A.D.3d 890 (2d Dep't 2023)\n\nThe Appellate Division, Second Department, ruled on March 22, 2023:\n\nFirst, 'contrary to the contention of the mother and the AFC, the order appealed from was not entered upon the father's default.' Steve's attorney had appeared and participated in the hearing — making objections and cross-examining witnesses. The default was a legal fiction.\n\nSecond, the court struck the blanket speech order requiring Steve to 'erase, deactivate, and delete any existing blogs and likenesses' as not 'tailored as precisely as possible to the exact needs of the case.' The gag order was unconstitutionally overbroad.\n\nThe decision was unanimous: Barros, J.P., Miller, Genovesi, and Wan, JJ., concur.",
     "pull_quote", "OK", "pdf/court_filings/ExR_04_LexisNexis_214AD3d890_Certified.pdf"),

    # B44 — SF Superior Court trial record (NEEDS_CURATION)
    ("B44", "San Francisco Superior Court trial",
     "In February 2022, a San Francisco jury heard four days of testimony in Russell v. Walsh (CGC-18-570137). Twelve citizens — none of whom knew Steve, Tara, or anyone in either family — heard the nanny's account of the drugging, saw the text messages, reviewed the medical records, watched Brienne Walsh's deposition testimony admitted without objection, and heard Tara's own admissions. They deliberated and returned a verdict finding Tara Walsh liable for battery, fraud, intentional infliction of emotional distress, and domestic violence — with a finding of malice, 11-1.",
     "document_excerpt", "OK", "pdf/court_filings/ExG_01_SF_Jury_Verdict_Judgment.pdf"),

    # B44 — Brienne deposition admitted (NEEDS_CURATION)
    ("B44", "Brienne Walsh deposition — admitted",
     "Brienne Walsh's sworn deposition — in which she confirmed childhood abuse, acknowledged 'numerous CPS calls' on her parents, and testified 'We were hit' — was admitted into evidence at the San Francisco trial without objection from Tara's counsel. The jury heard Tara's own sister confirm the pattern of abuse in the Walsh household, providing independent corroboration of the environment in which Evie was being raised in Chappaqua.",
     "pull_quote", "OK", "pdf/court_filings/ExSS_10_Brienne_Walsh_Deposition_Abuse_CPS.pdf"),

    # B45 — Jury verdict form (NEEDS_CURATION)
    ("B45", "Jury verdict form",
     "The jury returned its verdict on February 22, 2022, finding Tara Walsh liable on all counts:\n\n• Battery — LIABLE\n• Fraud — LIABLE\n• Intentional Infliction of Emotional Distress — LIABLE\n• Domestic Violence — LIABLE\n• Finding of Malice — YES (11-1)\n\nThe jury awarded approximately $300,000 in compensatory and punitive damages. One juror — the son of a law enforcement officer — was the sole holdout on the malice finding. The verdict was later affirmed on appeal by the California First District Court of Appeal.",
     "document_excerpt", "OK", "pdf/court_filings/ExG_01_SF_Jury_Verdict_Judgment.pdf"),

    # B46 — California Court of Appeal decision (NEEDS_CURATION)
    ("B46", "California Court of Appeal decision",
     "The California First District Court of Appeal affirmed the jury verdict in its entirety, finding sufficient evidence to support every count — battery, fraud, intentional infliction of emotional distress, and domestic violence — and upholding the finding of malice and the damages award. The appellate court rejected each of Tara Walsh's arguments on appeal, including her challenges to the sufficiency of the evidence and the jury instructions. Two courts, two sets of neutral decision-makers, the same conclusion: Tara Walsh drugged and abused Stephen Russell.",
     "document_excerpt", "OK", ""),

    # B48 — Author account Tara's demand (NEEDS_CURATION)
    ("B48", "Author account — Tara's demand",
     "After the jury verdict, after the appeal was denied, after two courts confirmed what happened — Tara's demand remained the same: Drop the judgment. Show the Walsh family 'respect.' Only then would Steve be permitted to see his daughter. The demand was not about money. It was not about Evie's welfare. It was about making the record disappear — erasing the verdict, the testimony, the evidence — so that the family's version of events could stand unchallenged.",
     "narrative", "OK", ""),
]


def main():
    v2 = load_v2()
    
    applied = 0
    not_found = 0
    
    for pid, exhibit_prefix, curated_text, embed_format, status, matched_file in CURATIONS:
        if pid not in v2:
            print(f"WARNING: {pid} not in v2 index")
            not_found += 1
            continue
        
        entry = v2[pid]
        found = False
        
        for hero in entry['hero']:
            if hero['exhibit_name'].startswith(exhibit_prefix):
                hero['embed_text'] = curated_text
                hero['embed_format'] = embed_format
                hero['status'] = status
                if matched_file:
                    hero['matched_file'] = matched_file
                applied += 1
                found = True
                break
        
        if not found:
            print(f"WARNING: Hero '{exhibit_prefix}' not found in {pid}")
            not_found += 1
    
    save_v2(v2)
    
    # Count remaining issues
    remaining = {'NEEDS_CURATION': 0, 'NEEDS_DESCRIPTION': 0, 'NEEDS_EXTRACTION': 0, 'NEEDS_WRITING': 0}
    total_hero = 0
    ok_hero = 0
    
    for pid, entry in v2.items():
        for h in entry['hero']:
            total_hero += 1
            s = h.get('status', '')
            if s == 'OK':
                ok_hero += 1
            elif s in remaining:
                remaining[s] += 1
    
    print(f"\nApplied {applied} curations, {not_found} not found")
    print(f"\nHero status after curation:")
    print(f"  OK: {ok_hero}/{total_hero}")
    for k, v in remaining.items():
        if v > 0:
            print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
