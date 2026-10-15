# Independent review record

Research and review were performed by separate AI agents in this commission. No customer interviews, human reviewer approvals or separate GitHub identities are implied. The repository uses a pull-request gate and required CI, with zero approving-review requirement for its single maintainer. Administrator bypass is disabled; force pushes and main deletion are disabled.

## Opportunity challenge, 2026-10-15

Two agents independently examined primary practitioner material and commercial/open-source alternatives. Their challenges rejected generic tray patching, cell-input-heavy consolidation and basic stratification calendar arithmetic. The final fixed-offset exclusion compiler credits BC's working spreadsheet and keeps demand unvalidated. Details and limitations are in [research](research.md).

## Independent acceptance tests

An agent wrote black-box CLI tests from the contract without implementing source. Its hostile large-integer test found an unhandled Python JSON `ValueError`. The parser now returns clean exit 2 and publishes no output. A mistaken test assumption about the example README extension was corrected to match the generated README.txt; that was a test correction, not a product fix.

## Independent implementation review

An additional agent examined source and reproduced the large-integer defect independently. It identified report amplification from many overlapping closure labels: the first version bounded event evaluations but not the number/size of emitted reasons. The implementation now bounds candidate rows, reason count and total detail characters, fails before publication, and never truncates reasons into a passing report. Regression coverage exercises this case.

The reviewer also found that iCalendar `METHOD:PUBLISH` would require iTIP organizer fields. Standalone snapshot files now omit METHOD, retaining standard all-day VEVENT data, escaped text, octet-correct UTF-8 folding and no alarms. The lead found and corrected a zipapp entrypoint issue so nonzero command returns propagate through SystemExit; the zipapp is exercised with blocked/stale/no-overwrite commands, not only --version.

After the fixes, the independent reviewer reported no remaining correctness blockers. It repeated parser/resource probes, built a copied-source distribution, and installed the wheel in a fresh environment outside the checkout. It recommended permanent regression coverage of all output caps; these cases were added. Exact reviewed revisions and CI evidence are linked from the implementation PR and [verification record](verification.md). Public-artifact and real-calendar-client verification are separate steps.
