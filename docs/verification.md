# Public release verification

Verified on **2026-10-15**. [Release v1.0.0](https://github.com/waxwingfactor/seedstartgate/releases/tag/v1.0.0) is public and installable. This record distinguishes published-artifact observations from development tests and market assumptions.

## Source, review and CI

- Source commit: [`0e2b158379db3b646ac69d754170b56dd1856f86`](https://github.com/waxwingfactor/seedstartgate/commit/0e2b158379db3b646ac69d754170b56dd1856f86).
- Git tree: `f3ef61262ee2b5967abc809f8022ebc82384353d`. The release tree matches reviewed PR head `0a16ee942d04f3a2038a7f968ea712e9f838236c` exactly.
- Annotated tag `v1.0.0` resolves through tag object `8764a0def50a48a16f5e4ff1928619f623f27697` to that source commit.
- [Implementation PR #3](https://github.com/waxwingfactor/seedstartgate/pull/3) merged only after [required checks passed](https://github.com/waxwingfactor/seedstartgate/actions/runs/38795212446). [Exact merged-revision CI](https://github.com/waxwingfactor/seedstartgate/actions/runs/38795518600) also passed.
- Six OS/Python combinations: Linux, macOS and Windows × Python 3.10 and 3.14. Each runs 24 independent CLI acceptance tests, wheel/sdist installed workflows and the standalone zipapp flow. Local independent tests additionally use Python 3.12.
- Main requires the `required` aggregate check and a PR; administrator enforcement remains enabled, force pushes/deletions are disabled. Separate AI-agent reviews are recorded in [reviews](reviews.md) and the PR. They are not human or separate-account GitHub approvals.

## Actual published artifacts

All files below were downloaded from public GitHub release URLs without authentication, rather than copied from the build directory. SHA-256 values matched `SHA256SUMS`, publisher `provenance.json` and GitHub release asset digests.

| Artifact | SHA-256 |
| --- | --- |
| `seedstartgate-1.0.0-py3-none-any.whl` | `fe133198dd7166369f91fd685b8121368c59076ba913fa62cf98b76f264c34de` |
| `seedstartgate-1.0.0.tar.gz` | `fd51f6e1b8a60d1fc10d06f4b9bed90be18ab10660b935d2b86090a638836483` |
| `seedstartgate.pyz` | `0ba844476fb9efb30eae4bc84fa77911b5dc90ca1f53d2b605b9145ac5b822fc` |

The seven package files match byte-for-byte across the downloaded wheel, source archive and zipapp; the standalone license matches the source license. Build provenance describes the exact source revision, matching reviewed tree, Python/build-tool versions and commands. It is a publisher-supplied record, not a signed build attestation. Verified software assets were not replaced after publication.

## Fresh environment observations

The lead downloaded the actual public files and independently installed the wheel into a fresh virtual environment outside the development checkout. Isolated execution confirmed the import came from that environment's site-packages. All 24 tests from the downloaded source archive passed; the installed example, allowed worklist, blocked/no-calendar result, no-overwrite, stale fingerprint and relocated operation passed.

A separate AI verification agent independently downloaded the same public assets, verified their hashes and source/tag/tree relationships, and used fresh wheel and source-archive environments outside the checkout. Both installations passed all 24 tests from the actual published source archive and its installed-workflow script. The source archive included the documented examples, tests, license and operating/research documentation.

The verifier relocated the actual published zipapp and ran the complete flow under Python `-I -S`, isolating it from PYTHONPATH and site packages. Allowed actions passed; blocked and unknown starts returned exit 3 with diagnosis only; stale fingerprints and existing outputs returned exit 2. Moving the plan directory still worked. System Python 3.9.6 was rejected cleanly. The observed artifact environment was Darwin arm64 with Python 3.12.14. Offline checks used `--no-index` installations and isolated standard-library execution; they were not an OS-level network-firewall test.

The lead separately generated calendar output with the downloaded zipapp and parsed it using **icalendar 6.3.2** in a separate environment. Three action events and nine known exclusions parsed without reported component errors. All-day dates, UTC stamps, unique UIDs, escaped punctuation/backslashes/long Unicode, 75-octet UTF-8 line folding and absence of alarms/METHOD were checked. This is parser/structure evidence, not calendar-client import certification.

Machine-readable records: [independent artifact verification](https://github.com/waxwingfactor/seedstartgate/releases/download/v1.0.0/verification.json) and [calendar parser checks](https://github.com/waxwingfactor/seedstartgate/releases/download/v1.0.0/calendar-parser-verification.json).

## Reproduce the checks

After downloading and checking the release hashes, create fresh environments; do not use an editable install or add the checkout to PYTHONPATH. For the wheel, use `python -m pip install --no-index --no-deps seedstartgate-1.0.0-py3-none-any.whl`. Run the downloaded source archive's `scripts/installed_smoke.py` with the installed interpreter in isolated mode. Run its tests with `SEEDSTARTGATE_TEST_INSTALLED=1` and `python -I -m unittest discover -s EXTRACTED_SOURCE/tests -v`.

For the source archive, preinstall setuptools 80.9.0 and wheel 0.45.1 in a separate fresh environment, then install the downloaded `.tar.gz` using `--no-index --no-deps --no-build-isolation` and repeat. For the standalone archive use supported Python, optionally `-I -S`, from a directory outside the source checkout. The included example is constructed arithmetic, not seed-treatment guidance.

## Limits of this evidence

These checks establish software behavior within [the supported contract](contract.md). No production nursery deployment, customer adoption, measured labor savings, biological validity or seed-testing certification was tested. Real calendar-client imports were not exercised; ICS compatibility is limited to generated all-day standard data and the structural/parser checks recorded here. Declared calendars may still omit real closures or required actions. No labor/storage capacity or optimal schedule is implied. [Dated opportunity and positioning evidence](research.md) remains bounded and demand is inferred.
