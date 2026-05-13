#!/usr/bin/env python3
"""
curate_primary_secondary.py

Curates the 16 primary NEEDS_EXTRACTION items and 12 secondary NEEDS_EXTRACTION items
in v3_evidence_map_v2.json. Primary items get appendix-length excerpts (~500-2000 chars).
Secondary items get 1-3 sentence summaries (~100-300 chars).

⚠ DEPRECATED: This script's data has been absorbed into evidence_index_canonical.json.
To update evidence data, edit directly in canonical and re-run: python3 scripts/build_canonical_evidence_index.py
"""

import json

# PRIMARY CURATIONS: appendix-length excerpts
PRIMARY_CURATIONS = [
    # B01 - Foursquare items
    ("B01", "Foursquare check-in",
     "Foursquare location check-in record showing Stephen Russell at Domodedovo International Airport, Moscow, May 2010. The check-in was made during a trip to Russia that included attending Victory Day celebrations in Red Square. The Foursquare record provides a timestamped, GPS-verified location marker establishing Steve's presence in Moscow — a detail that becomes significant because the same app later recorded his displacement from the location, and because the check-in ritual itself reveals the kind of person who documented everything, everywhere, reflexively.",
     "Evidence/screenshots/foursquare_checkin_domodedovo.png"),

    ("B01", "Foursquare 'Mayor",
     "Foursquare notification confirming Stephen Russell as 'Mayor of Domodedovo Airport' — the app's designation for the user who had checked in most frequently at a given location. The mayoralty was earned through repeated visits during 2010. The notification is a digital artifact of a man whose travel patterns were recorded automatically by a platform he used without considering that those records would one day constitute evidence of a life lived before the events that would define the next decade.",
     ""),

    ("B01", "Foursquare mayoralty loss",
     "Foursquare notification, approximately November 2010: 'Stephen Russell, you are no longer the Mayor of Domodedovo Airport.' Someone else had checked in more frequently. The title had moved on. The notification arrived on a phone on a desk in San Francisco — a small algorithmic demotion that, in retrospect, marked the closing of one chapter. The man who had been everywhere was about to become the man who could not leave.",
     ""),

    # B05 - Drill holes
    ("B05", "Photos of drill holes",
     "Photographs taken by Stephen Russell documenting the break-in at his residence. Images show: (1) the electrical closet on the building's exterior with its door forced open — hinges removed by extracting the pins carefully rather than breaking them; (2) breaker positions inside the closet, several switches flipped; (3) drill holes in the interior walls — small, round, clean, evenly spaced along the hallway, bedroom wall, baseboard, and floor. The holes were consistent with someone searching systematically for something specific within the walls. Nothing was stolen. The television was still on the wall. The laptop was on the desk. The only evidence of entry was structural — holes drilled into the building itself, and an electrical system that had been accessed and reconfigured.",
     "Evidence/photos/drill_holes"),

    # B13 - Ring dispute items
    ("B13", "EXHIBIT_P1",
     "Email chain, April–August 2018, between Stephen Russell, Ring's general counsel Leila Rouhi, and Ring's outside counsel Roxana Azizi regarding Steve's 205,308 stock options. In early April 2018, Steve's financial advisor contacted Ring to exercise the options following Amazon's acquisition of Ring for over $1 billion. Rouhi refused, claiming the options had been forfeited thirty days after Steve's October 31, 2016 offer to resign from the board. The emails document Ring's position that the options were void — a position that would be contested in the subsequent Los Angeles Superior Court litigation filed November 1, 2018.",
     ""),

    ("B13", "EXHIBIT_P2",
     "Email chain, March–August 2018, regarding the Amazon transmittal documentation required to receive acquisition proceeds. The transmittal required a general release of all claims. Steve's advisors requested a carve-out to preserve his claims against Ring while accepting the payout. Ring's outside counsel Roxana Azizi responded: the transmittal documentation was required by the merger agreement and could not be modified, and even if it could be modified, Ring was 'not willing to carve out or exclude any claims.' The ultimatum was explicit: sign everything and release all claims, or receive nothing from the acquisition.",
     ""),

    ("B13", "Steve to Jamie",
     "Email from Stephen Russell to Jamie Siminoff, July 6, 2018. Steve wrote: 'J — Sorry I didn't call you but I have been a little busy. Tara took the baby and ran off to NY after it was discovered she had done something very bad for which there is now a criminal investigation underway in SF.' The email is significant as a contemporaneous communication to a business associate documenting both Tara's departure with Evie and the existence of a criminal investigation — written weeks after the flight from San Francisco, before the custody litigation had fully commenced.",
     ""),

    # B17 - Communications
    ("B17", "Communications arranging flight",
     "Communications and travel records documenting the arrangement of the charter flight from Teterboro Airport (New Jersey) to SFO's private terminal. The flight carried Tara Walsh, seven-week-old Evie, and Saoira on a Wednesday morning. Steve was not on the flight — he was in San Francisco preparing the household: arranging the North Beach townhouse and hiring Abby Tedla as nanny through a referral network. The travel records establish the logistics of the cross-country relocation that brought Tara and Evie to San Francisco, where the events of the next several months would unfold.",
     ""),

    # B20 - Hospital records
    ("B20", "Hospital arrival records",
     "Hospital arrival and admission records documenting Stephen Russell's emergency presentation following a medical episode. After experiencing acute symptoms — consistent with involuntary drug exposure — Steve called his security team. A driver arrived and transported him to the hospital. The records establish the medical response timeline and the clinical documentation of symptoms that would later be corroborated by toxicology results showing substances Steve had not been prescribed and had not knowingly ingested.",
     ""),

    # B32 - Flight records
    ("B32", "Flight records",
     "Flight booking records documenting the overnight flight Stephen Russell took from California to New York the evening before a Family Court hearing. The court had denied his request for a continuance at five o'clock the evening before — the hour when flights become scarce and cross-country travel requires overnight redeye booking. Steve left Kelly in the hospital where she was recovering from surgery, drove to the airport, and flew through the night. He landed in New York in the early morning. The flight records establish that Steve made every effort to appear — and that the timing of the denial was calibrated to make his presence as difficult as possible.",
     ""),

    # B33 - Hearing transcripts
    ("B33", "Hearing transcripts",
     "Transcripts from the scheduled evidentiary hearings in which Tara Walsh and her attorneys failed to appear. The first hearing: Steve's legal team prepared, the courtroom was arranged for a proceeding, and Tara did not appear. A default was entered against her. The second hearing: again, Tara and her attorneys did not appear. A second default was entered. The transcripts document the procedural asymmetry at the heart of the case: Steve's single near-default (from flying overnight after a 5pm denial) produced a custody order that separated him from his daughter. Tara's two actual defaults produced nothing — except the departure of another judge (Humphreys recused, reason undisclosed).",
     ""),

    # B34 - Three discoveries
    ("B34", "A-1",
     "Laboratory report documenting lithium levels in Stephen Russell's system at six times the upper limit of normal. Steve had not been prescribed lithium. He had not ingested it knowingly. The lithium finding constituted Discovery 1 in the pattern of involuntary drug exposure — the first laboratory-confirmed evidence that substances were being administered without Steve's knowledge or consent. The report provides the quantitative basis for the poisoning allegations: not a marginal elevation, not a borderline result, but a level six times above the reference range maximum.",
     "Evidence/pdf/lab_reports/ExA_01_Lithium.pdf"),

    ("B34", "Hospital records",
     "Medical records from the Brooklyn psychiatric commitment, 2017. The evening in the apartment on Atlantic Avenue when Steve took his prescribed Adderall — the same Adderall he had taken for years — and the world detached. The tamper screws on the pill bottles had been at eleven o'clock when he left. They were not at eleven o'clock when he returned. The hospitalization records document the acute psychiatric episode that followed ingestion of what Steve believed was his regular medication — an episode that would later be understood as the result of pharmaceutical tampering rather than a spontaneous mental health crisis.",
     ""),

    ("B34", "ExA_02",
     "Laboratory report identifying mycophenolic acid in the wine sample from the Potrero Hill years — the bottle that had traveled from San Francisco to the bug-out apartment in Reno and been preserved for testing. The laboratory found mycophenolic acid at 349.87 nanograms per gram creatinine. The reference range is 5 to 50. Steve's level was seven times the upper bound of normal. Mycophenolic acid is an immunosuppressant prescribed exclusively to organ transplant recipients. Steve is not a transplant recipient. Discovery 4 — the wine bottle — provided the most dramatic quantitative evidence: a substance that had no legitimate reason to be present, at a concentration that precluded accidental contamination.",
     "Evidence/pdf/lab_reports/ExA_02_Mycophenolic_Acid.pdf"),

    # B43 - Family Court orders
    ("B43", "Family Court orders",
     "Compilation of Family Court orders issued between 2019 and 2023 that were built upon the default finding — the default that the Appellate Division, Second Department subsequently held did not occur (214 A.D.3d 890). These orders include: custody determinations, speech restrictions (the gag order prohibiting Steve from discussing the case), contact limitations governing Steve's access to Evie, and procedural orders that treated the default as an established fact. Under ordinary legal doctrine, orders built on a nonexistent jurisdictional foundation are void ab initio. The appellate court removed the foundation. The orders that rested on that foundation remained in effect — creating the paradox at the center of the post-reversal proceedings.",
     ""),

    # B44 - Text messages
    ("B44", "Text messages",
     "Text messages and communications between Stephen Russell and Tara Walsh, admitted as exhibits during the San Francisco civil trial. The messages were exchanged during the years of the marriage and the custody fight — communications that showed what was said in private, in contrast to what was represented in court filings. The messages were projected on a screen for the jury. They revealed the tone, the intent, and the distance between what was presented to courts and what was said in confidence. The exhibit collection documented the private record of a relationship that was simultaneously being adjudicated in public proceedings across multiple jurisdictions.",
     ""),
]

# SECONDARY CURATIONS: 1-3 sentence summaries
SECONDARY_CURATIONS = [
    ("B01", "Hipstamatic photographs",
     "Two photographs taken with the Hipstamatic app in Red Square, Moscow, May 8–10, 2010, during Victory Day celebrations — military equipment and parade formations captured through the app's vintage filter."),

    ("B02", "Author account — Zar",
     "Tara showed Steve a photo of her friend Zar — a Russian man sitting at a table covered in cash from a construction site injury payout — then a news article about another friend whose apartment was hit by a wrecking ball, who also received a large settlement. 'Same thing happened to me two years ago,' she said, lightly, as if wrecking balls through apartments were coincidence."),

    ("B08", "Author account — ultrasound",
     "Standard ultrasound appointment at Zuckerberg Hospital, San Francisco. The technician moved the wand, and a shape appeared on the gray screen — small, moving, a heartbeat visible as a pulse of light. Evie."),

    ("B13", "Author account — Kelly",
     "Steve met Kelly at The Battery after the breakup with Tara. She helped organize the Ring case, fought alongside him through the stock option dispute and the transmittal release standoff, and helped him see the litigation through to settlement in February 2019 — while Tara's flight with Evie was already underway."),

    ("B15", "Author account — Motel 6",
     "First night in Chappaqua was the Motel 6 — a room with a bed, a bolted television, and plumbing from another decade. A local officer, separate from the security team, pulled Steve aside: 'Don't trust anyone.' He did not elaborate."),

    ("B19", "Author account — sinking building",
     "The Millennium Tower penthouse — floor-to-ceiling windows, views to the bay and bridges. The building was measurably sinking toward the bay. Steve sat at the kitchen island after midnight with Adderall working and fourteen camera feeds cycling on his laptop. The metaphor was not subtle, but the man inside it could not see it yet."),

    ("B21", "Author account — kitchen disclosure",
     "Abby Tedla walked into the kitchen with a different face. She had called her brother in the FBI, described what she had been seeing beneath the surface of the household. Her brother told her: tell Steve immediately. She told him Tara had been putting drugs in his wine. The confrontation that followed produced Tara's escalating deflections: 'I do it all the time.' Then: 'We all do it.' Then: 'They did it.'"),

    ("B24", "Abby Tedla account",
     "Abby Tedla — the nanny who had stayed for Evie through being fired and rehired and caught in the middle of something she never signed up for — was there when Steve brought Evie inside at Crabtree's Kittle House. Once alone with Steve and Abby, the child calmed down."),

    ("B32", "Author account — Kelly's surgery",
     "Kelly was in the hospital for surgery when the court denied Steve's continuance request at 5pm the evening before the hearing. He left her in recovery, drove to the airport, and flew overnight to New York — arriving at a courtroom door that was already closed. The clock had been set to make his presence impossible, and his impossibility was recorded as absence."),

    ("B33", "Author account — Humphreys recusal",
     "Judge Humphreys recused himself from the TOP proceeding — reason undisclosed, like Gordon-Oliver's recusal before it. Steve's single near-default produced a custody order; Tara's two actual defaults produced nothing except another judge's departure. The case file grew thicker. The distance between Evie and her father remained the same."),

    ("B37", "Author account — Jackman resignation",
     "Jennifer Jackman resigned as Attorney for the Child without explanation. Then Steve was declared in default on a motion he was not a party to — a visitation motion about Linda Russell's visits that had been converted without notice into a speech hearing. A default for a proceeding he was not a party to."),

    ("B49", "Author account — the house",
     "A three-story house where shoes are left by the door and mail accumulates on the counter. Simon quiets against Steve's chest. Kelly has been there through the Reno bottle, the miscarriage, the trial, the verdict. Upstairs, Evie's room is ready — books on shelves, board games in the closet, photographs on the wall. It has been ready for years. In the study, binders and hardbound volumes line the shelves: the StevieLovesEvie archive, physical and weighted, things that can be held."),
]


def main():
    with open('v3_evidence_map_v2.json') as f:
        data = json.load(f)

    # Apply primary curations
    primary_applied = 0
    for pid, exhibit_prefix, curated_text, matched_file in PRIMARY_CURATIONS:
        if pid not in data:
            print(f"  WARNING: {pid} not in map")
            continue

        found = False
        for item in data[pid].get('primary', []):
            if exhibit_prefix.lower() in item['exhibit_name'].lower():
                item['appendix_text'] = curated_text
                item['status'] = 'OK'
                if matched_file:
                    item['matched_file'] = matched_file
                found = True
                primary_applied += 1
                print(f"  OK  {pid}: {item['exhibit_name'][:60]}")
                break

        if not found:
            print(f"  MISS {pid}: {exhibit_prefix}")

    # Apply secondary curations
    secondary_applied = 0
    for pid, exhibit_prefix, curated_text in SECONDARY_CURATIONS:
        if pid not in data:
            print(f"  WARNING: {pid} not in map")
            continue

        found = False
        for item in data[pid].get('secondary', []):
            if exhibit_prefix.lower() in item['exhibit_name'].lower():
                item['appendix_text'] = curated_text
                item['status'] = 'OK'
                found = True
                secondary_applied += 1
                print(f"  OK  {pid}: {item['exhibit_name'][:60]}")
                break

        if not found:
            print(f"  MISS {pid}: {exhibit_prefix}")

    # Write updated map
    with open('v3_evidence_map_v2.json', 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    # Final stats
    print(f"\n=== APPLIED ===")
    print(f"Primary curated: {primary_applied}")
    print(f"Secondary curated: {secondary_applied}")

    # Count remaining
    hero_ok = hero_need = 0
    pri_ok = pri_need = 0
    sec_ok = sec_need = 0

    for pid, post in data.items():
        for item in post.get('hero', []):
            if item.get('status') == 'OK':
                hero_ok += 1
            else:
                hero_need += 1
        for item in post.get('primary', []):
            if item.get('status') == 'OK':
                pri_ok += 1
            else:
                pri_need += 1
        for item in post.get('secondary', []):
            if item.get('status') == 'OK':
                sec_ok += 1
            else:
                sec_need += 1

    tert = sum(len(post.get('tertiary', [])) for post in data.values())

    print(f"\n=== FINAL STATUS ===")
    print(f"Hero:      {hero_ok} OK / {hero_need} remaining")
    print(f"Primary:   {pri_ok} OK / {pri_need} remaining")
    print(f"Secondary: {sec_ok} OK / {sec_need} remaining")
    print(f"Tertiary:  {tert} (carried)")
    print(f"TOTAL:     {hero_ok + pri_ok + sec_ok + tert} items indexed")


if __name__ == "__main__":
    main()
