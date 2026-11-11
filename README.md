# Parking Garage System

A small Java library for vehicle check-in, check-out, parking-space selection, and fee calculation.

**Student:** Taha Yasin Eker · **Student ID:** 230201042

**Course:** Object-Oriented Programming, Fall 2026

Start with the [submission guide](SUBMISSION.md). The [autopsy report](autopsy_report.md) contains the failure traces, recorded values, changes, and verification results.

## Public API

- `Garage.addSpot(spot)` registers a parking space.
- `Garage.findSpot(vehicle)` finds a free space that satisfies the vehicle's fitting rules.
- `Garage.checkIn(vehicle)` attempts to park a vehicle and returns a boolean.
- `Garage.checkOut(licensePlate, rate)` returns the fee, or null for an unknown plate.
- `Vehicle.calculateFee(rate)` calculates the fee from the recorded entry time.
- `Vehicle.fitsInSpot(spot)` checks whether the vehicle fits in a given space.

## Build and test

Java 17 or later and Maven are required.

```powershell
mvn --batch-mode --no-transfer-progress test
```

| Verification | Recorded result |
|---|---|
| Supplied JUnit suite | 6 of 7 tests pass; 1 failure, 0 errors |
| Additional behaviour checks | 8 of 8 pass |
| Supplied test source | Unchanged |
| Source patch | Applies to the documented baseline and reproduces the final sources |

The remaining Truck test expects the missing-entry-time defect that the constructor change removes. Its assertion is preserved, and the discrepancy is documented in [report section 5](autopsy_report.md#5-the-current-truck-test-expectation).

## Repository layout

```text
src/main/java/garage/       Library source
src/test/java/garage/       Supplied JUnit tests
autopsy_report.md          Failure analysis and verification
fix.patch                  Source changes
reflection.md              Personal reflection
ai_log.md                  Assistance log
trace_evidence/            Source snapshots, debugger records, screenshots, and logs
docs/viva_notes.md         Oral-defence preparation
tools/                     Reproduction and verification helpers
```

The evidence guide explains [how to repeat the debugger sessions](trace_evidence/README.md). Build outputs and IDE configuration are excluded from version control.
