# OOP Take-Home Quiz — Submission Guide

**Taha Yasin Eker · 230201042 · 11 November 2026**

**Repository:** [tahaeker/parking-garage](https://github.com/tahaeker/parking-garage)

## Deliverables

| File | Purpose |
|---|---|
| [autopsy_report.md](autopsy_report.md) | Expected and actual behaviour, call paths, root causes, fixes, and results |
| [fix.patch](fix.patch) | Changes to the three production classes |
| [trace_evidence/](trace_evidence/README.md) | Compiler, test, debugger, and screenshot evidence |
| [reflection.md](reflection.md) | Personal reflection based on the student's account |
| [ai_log.md](ai_log.md) | Assistance used and a suggestion that was not applied |
| [docs/viva_notes.md](docs/viva_notes.md) | Short explanations for the oral defence |
| [tools/](tools/) | Helpers for repeating the checks and collecting evidence |

## Verification checklist

- [x] Student details included.
- [x] Report and source patch prepared.
- [x] Supplied `GarageTest.java` preserved and checked for integrity.
- [x] Three debugger transcripts recorded.
- [x] Two IDE screenshots saved; two forms of trace evidence are available.
- [x] Additional behaviour checks pass: 8/8.
- [x] Reflection kept below 250 words.
- [x] Assistance log included.
- [ ] Supplied JUnit suite passes 7/7: **not yet; the recorded result is 6/7.**
- [ ] The Truck test's expectation has been clarified with the instructor.
- [ ] Five-minute oral defence completed.

The unresolved test expectation is explained in report section 5. The additional checks do not replace the supplied JUnit suite.

## Before the oral defence

Review the report and reflection. Be ready to explain `assertThrows`, null arguments, `super(...)`, method overriding, and the mapping between a vehicle and its parking space. Use the commands in the [evidence guide](trace_evidence/README.md) to repeat the trace.

The Java files were moved from the original repository root into Maven's `src/` layout. The report distinguishes this layout preparation from the source changes in the patch.
