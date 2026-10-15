# Research and positioning

Research cutoff: **2026-10-15**. This is a bounded public-document review and a product-scope decision, not customer validation. No interviews, adoption, measured time savings, production use, or universal uniqueness are claimed. Product pages describe vendor claims; they were not verified through paid accounts or demonstrations.

## Selected workflow

SeedStartGate compiles **fixed elapsed-day action offsets into permitted, excluded, and unknown start dates** against operator-supplied staffing calendars. Its beachhead is a small native-seed nursery or seed-preparation team that already has approved protocols and wants to check a block of possible starts before beginning work.

An action on day 30 happens exactly 30 calendar days after the start, including weekends. The operator supplies the protocol, its authority, every attendance action, staffed weekdays, exceptions, closures, and the dates through which each calendar has been checked. The tool neither chooses a treatment nor changes its timing. The complete technical boundary is in [the supported contract](contract.md).

The compelling reason to use this utility is prospective: an ordinary staffed start day can imply an unattended transfer or final action several weeks later. The proposed benefit is making those exclusions inspectable before a lot starts. Whether enough teams need a separate maintained tool for this remains an inference.

This product does not select durations, solve task graphs, allocate equipment or labor, optimize capacity, or replan from actual starts. It does not determine biological readiness or certify that a seed treatment is appropriate.

## Practitioner evidence and prior art

The decisive source is **“Scheduling Germination Tests,” pages 13–14 of the Canadian Forest Genetics Association Tree Seed Working Group News Bulletin 50, December 2009**. It describes the BC Tree Seed Centre's Excel **Do Not Start List**: staff enter future holidays and fixed offsets for attendance actions; the workbook subtracts those offsets to identify conflicting starts and the affected actions. Examples include warm-to-cold transfers, germinator entry, dryback, and final counts. The article says scheduling conflicts had already been addressed locally using this workbook, CONSEP workload prediction, and resource calendars. It also says the approach can accommodate other days with limited staffing. This is functioning prior art documented by 2009, not a newly discovered unsolved problem. SeedStartGate credits that method and implements its narrow exclusion-calendar workflow as a portable utility. [Primary bulletin](https://www2.gov.bc.ca/assets/gov/farming-natural-resources-and-industry/forestry/tree-seed/tree-seed-centre/tswgnewsbulletin50.pdf).

BC's current official [seed withdrawal, preparation and transport page](https://www2.gov.bc.ca/gov/content/industry/forestry/managing-our-forest-resources/tree-seed/tree-seed-centre/seed-withdrawal-prep-transport) describes daily request transfer from SPAR into CONSEP. That supports continuing official documentation of CONSEP, not continued use of the exact 2009 workbook or its present feature set. The live page text was retrieved during the lead's review.

The USDA [*Nursery Manual for Native Plants*, volume 1](https://www.govinfo.gov/content/pkg/GOVPUB-A-PURL-gpo52479/pdf/GOVPUB-A-PURL-gpo52479.pdf) describes planning pretreatment backward from target sowing dates, with different species requiring different lead times. It establishes why a nursery may manage heterogeneous preparation dates. It does not establish demand for SeedStartGate or supply protocols for this product.

## Alternatives checked at feature level

The review examined practitioner prior art, exact-workflow searches, and product documentation. A separate AI-agent adversarial review challenged the broader ideas and their differentiation. Search gaps are not treated as evidence that no alternative exists. The comparisons below distinguish documented features from an unconfirmed capability.

| Alternative | Documented capability | Assessment for this workflow |
| --- | --- | --- |
| **Maintained spreadsheet and calendar** | The BC bulletin documents a working offset-inversion workbook with action-level conflict explanations. | The principal market alternative, and a good choice for a few stable protocols. SeedStartGate must justify itself through explicit coverage, reusable validated inputs, complete reasons, portable outputs, and repeatable checking. The arithmetic is not novel. |
| **[Seedtime custom tasks](https://help.seedtime.us/en/articles/10426461-adding-custom-tasks) and [rescheduling](https://help.seedtime.us/en/articles/5715460-rescheduling-and-editing-tasks)** | User-named tasks can have offsets relative to another task, durations, repetitions, and reusable series. Dependent tasks move together at daily precision. | A strong product alternative for calendar and task-series management. Reviewed help documents do not establish compilation of every forbidden start in a range, explicit calendar-coverage uncertainty, or complete per-action exclusion reports. That is a documentation boundary, not proof these capabilities are absent. |
| **[GameBob Seed Stratification Calendar](https://www.gamebob.dev/en/utilities/categories/nature/seed-stratification-calendar/)** | Editable soak/warm/cold durations; forward or backward date calculation; phase timeline; local settings; calendar export, share link, and compact labels. | A good simpler tool for calculating preparation dates. These features invalidated basic backward stratification scheduling as differentiation. The retrieved page does not document staffed-calendar inversion or unknown calendar coverage. |
| **[Homestead Shelf seed-starting calculator](https://www.thehomesteadshelf.com/seed-starting-calculator)** | Backward stratification/sowing/transplanting dates for its species catalog, plus browser-generated ICS. | Good for its garden-planning scope. Date arithmetic and calendar export are already available; neither is a uniqueness claim here. Its retrieved page does not document arbitrary attendance-offset exclusion calendars. |
| **[TaskJuggler duration documentation](https://taskjuggler.org/tj3/manual/duration.html) and [manual](https://taskjuggler.org/tj3/manual/toc.html)** | General project scheduling distinguishes elapsed calendar duration from working time and provides extensive scheduling/reporting facilities. | A capable open-source general alternative. SeedStartGate is a smaller fixed-offset report compiler; it does not claim new calendar mathematics or replace project scheduling. No hands-on TaskJuggler implementation of this exact workflow was performed. |
| **[farmOS logging](https://farmos.org/guide/logs/) and [plan model](https://farmos.org/model/type/plan/)** | Future pending logs become tasks; logs can be assigned; specialized plans can associate records. | A good open-source operational record system. The reviewed core documentation does not establish this exclusion compiler; extensions could implement it. |
| **[ArcheWild SeedSource](https://archewild.com/seedsource-software/)** | Native-nursery/restoration management, seed collection scheduling, inventory through conditioning and germination, plant provenance, orders, and offline field collection. | A relevant whole-operation platform, not a generic inventory product to dismiss. Its public overview was retrieved; no product account was inspected. The overview does not establish the precise fixed-offset exclusion/coverage behavior. |
| **[Mprise Agriware planning](https://www.mprise-agriware.com/planning-forecasting)** | Forward/backward horticultural production planning, production schemes, labor, material, and space planning. | A strong broader production alternative. Public marketing does not settle its exact behavior for this small exclusion-calendar contract, so no categorical inability is claimed. |
| **[BRAHMS release notes](https://herbaria.plants.ox.ac.uk/bol/brahms/software/revisions) and [IrisBG modules](https://irisbg.com/overview-p.aspx)** | BRAHMS documents seed treatments, stratification data, and germination records; IrisBG documents detailed propagation protocols and collection management. | Relevant specialist systems. Recording protocols and results is already supported. Reviewed pages do not establish the proposed compiler; they are not evidence that a configured installation cannot reproduce it. |

These checks support only a narrow conclusion: the reviewed public material did not establish a readily available standalone tool with the **same complete explicit-coverage exclusion-report contract**. The documented spreadsheet already solves the central operational calculation. A free, maintained, installable implementation can still be useful; present-day demand and comparative ease of use remain unvalidated.

## Rejected and removed scope

**Tray consolidation and gapping.** Practitioner documentation establishes the physical operation, including removable-cell consolidation in the USDA manual. However, [Spriggo](https://spriggo.tech/features) advertises batch splits, merges, movements and lineage, while [TTA-ISO's Florensis case](https://tta-iso.com/index.php/cases/florensis) describes mechanized gapping. The Spriggo feature text was retrieved through its indexed primary page; a subsequent full-page retrieval yielded no text. Cell-by-cell manual input also risks requiring more work than physical consolidation. This idea was rejected; no software-demand or labor-saving claim was established.

**Basic backward seed-pretreatment calendar.** Rejected after GameBob, Seedtime and Homestead Shelf demonstrated substantial existing coverage. Arbitrary phase dates plus ICS would not distinguish another product.

**Variable-duration or resource-constrained scheduling.** Removed. Selecting among minimum/maximum durations, finding feasible task graphs, capacity planning, and actual-start replanning belong to a different product scope. SeedStartGate checks exact supplied offsets and preserves every one.

## Constructed usage scenario

This scenario is invented to explain the supported operation. Names, actions and offsets are arithmetic examples, not species treatment instructions or observed customer behavior.

A nursery coordinator has an internally approved protocol with an attendance action on day 0 and a second attendance action on day 30. Its checked staffing calendar covers **2026-12-01 through 2027-01-31**, staffs Monday through Friday, and explicitly closes **2027-01-01** with the label `Site closure`. The coordinator screens December 1–3:

| Candidate start | Day-30 action | Result |
| --- | --- | --- |
| 2026-12-01, Tuesday | 2026-12-31, Thursday | Allowed under the supplied calendar. |
| 2026-12-02, Wednesday | 2027-01-01, Friday | Blocked: the future action hits the explicit site closure. |
| 2026-12-03, Thursday | 2027-01-02, Saturday | Blocked: the future action hits an unstaffed weekday. |

All three candidate starts are ordinary staffed weekdays. Checking only the day work begins misses the later conflicts. The compiler reports the affected event and date; it does not move the action to Monday or alter the offset.

If the same calendar is checked only through **2026-12-31**, December 2 is **unknown** because its day-30 event falls beyond coverage. A missing future closure entry cannot be interpreted as permission. Unknown candidates remain in the report, are not exported as known blocked starts, and cause a nonzero screening result. A blocked or unknown `check` produces diagnosis without an executable worklist or action ICS. The operator must verify and extend coverage before rerunning.

## Applying Crossing the Chasm selectively

Moore's official [*Crossing the Chasm* overview](https://geoffreyamoore.com/book/crossing-the-chasm/) emphasizes one demanding use case, a compelling reason, complete delivery, and clear alternatives. His [positioning overview](https://geoffreyamoore.com/positioning/) discusses a narrow beachhead, whole product, and differentiation. Applied here, these ideas justify a specific nursery operator and an end-to-end exclusion check, rather than a general farm platform. They do not establish that a market has been won or that reference customers exist.

The [Chasm Group's whole-offer discussion](https://chasmgroup.com/what-we-do/) informs the required supporting pieces: input schema, examples, clear unsupported cases, installation, deterministic reports, optional offline calendar files, and an independent chosen-start check. Its [differentiation discussion](https://chasmgroup.com/how-different-must-different-be/) supports comparison with a good spreadsheet and with doing nothing. No financial, distribution, or growth strategy is inferred for this open-source utility.

### Original two-sentence positioning

For small native-seed preparation teams dissatisfied with manually reconciling approved action offsets against future staffing closures, SeedStartGate is a fixed-offset exclusion-calendar compiler that identifies permitted, blocked, and unknown start dates with every affected action and reason. Compared with managing this check inside a calendar or task-series suite, SeedStartGate provides explicit calendar coverage, validated reusable protocols, deterministic JSON and CSV reports, optional exclusion ICS, and a fingerprint-checked start assessment that emits a dated worklist only when every supplied action is staffed.

This positioning is original project copy. The scenario is constructed, the beachhead is a hypothesis, and release verification demonstrates software behavior within the contract rather than biological suitability or market adoption.
