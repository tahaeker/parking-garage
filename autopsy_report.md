# Inheritance Autopsy — Taha Yasin Eker

**Student ID:** 230201042  
**Course:** Object-Oriented Programming  
**Date:** 11 November 2026

## 1. Summary

This analysis uses the local source files, compiler output, supplied JUnit suite, and recorded debugger sessions. The original and corrected source versions are kept separately.

| Check | Observed result |
|---|---|
| Compile the original Git sources | 1 compilation error in the Truck constructor |
| Reproduce the old Motorcycle failure after removing the compilation blocker | NullPointerException in fitsInSpot(null) |
| Supplied JUnit suite against the current source | 7 tests: 6 pass, 1 fails, 0 errors |
| Separate behaviour checks | 8 scenarios: all pass |
| Supplied GarageTest.java | Preserved; SHA-256 checked |

The classes involved are Vehicle, Truck, Motorcycle, Garage, and GarageTest. The missing superclass constructor call prevents compilation. The Motorcycle override also fails to preserve the base class's safe handling of a null spot. Space selection and check-out state were checked separately.

**Unresolved result:** `truckCheckoutFailsDueToMissingEnteredAt` expects an exception caused by a missing entry time. The current Truck constructor sets that time, so the expected exception is not thrown. The supplied assertion is unchanged. This report does not claim that every supplied test passes.

## 2. Source versions and evidence

The captured Git commit begins with `a59f0c1`; its full ID is in [capture_manifest.json](trace_evidence/capture_manifest.json).

The original Git sources were in the repository root, and the Vehicle file was named `vehicle.java`. For the compiler check, their contents were copied into the documented Maven layout and the filename was normalized to `Vehicle.java`. This did not remove the constructor error. The original contents are preserved in [repository-original](trace_evidence/snapshots/repository-original/).

To reproduce the Motorcycle failure, only `super(licensePlate, LocalDateTime.now());` was added to the copied Truck constructor. This removed the compilation blocker while preserving the original Motorcycle and GarageTest contents. The resulting record is a new execution of the stated reproduction, not a capture from a past session. See the [reproduction note](trace_evidence/snapshots/reproduce-motorcycle-failure/REPRODUCTION.md).

Line references identify the source version being discussed. Current files are under `src/`; earlier versions are under `trace_evidence/snapshots/`.

## 3. Original Truck constructor failure

### Symptom

The original `Truck.java:9` does not compile. No JUnit assertion has run at this point; the failure occurs before testing.

```text
constructor Vehicle in class Vehicle cannot be applied to given types;
required: String,LocalDateTime
found:    no arguments
reason: actual and formal argument lists differ in length
```

Full output: [01-original-compile.txt](trace_evidence/logs/01-original-compile.txt).

### Trace and root cause

In the original source snapshot:

```text
Truck.java:5 — Truck extends Vehicle
→ Truck.java:9 — Truck(String licensePlate, double height)
→ no explicit super(...) call
→ the compiler looks for a no-argument Vehicle constructor
→ Vehicle.java:14 — only Vehicle(String, LocalDateTime) exists
→ COMPILATION FAILURE: Truck.java:9
```

Declaring the parameterized Vehicle constructor means a default no-argument constructor is not generated. Truck does not call the constructor that actually exists. The comment saying that enteredAt is left unset describes an intended runtime defect, but the provided sources stop earlier at compilation.

### Minimal fix

Current `Truck.java:10`:

```java
super(licensePlate, LocalDateTime.now());
```

This initializes the plate and entry time through `Vehicle.java:14–16`. The redundant assignment of the same plate in Truck was removed. The public constructor signature is unchanged.

**Design rule:** Check which superclass constructor establishes the required fields whenever a subclass is created. A usable object should have that state initialized before its methods depend on it.

## 4. Motorcycle null-spot failure

### Symptom

**Test:** `motorcycleHandlesNullSpotGracefully`  
**First assertion:** `src/test/java/garage/GarageTest.java:65`  
**Expected:** `moto.fitsInSpot(null)` returns false.  
**Actual:** The old implementation throws while calling `spot.getWidth()`, before the assertion can evaluate the result.

```text
java.lang.NullPointerException: Cannot invoke "garage.Spot.getWidth()" because "spot" is null
    at garage.Motorcycle.fitsInSpot(Motorcycle.java:19)
    at garage.GarageTest.motorcycleHandlesNullSpotGracefully(GarageTest.java:65)
    at garage.DebugRunner.main(DebugRunner.java:12)
```

### Trace

The debugger recorded this path in the reproduction source:

```text
tools/garage/DebugRunner.java:12
→ src/test/java/garage/GarageTest.java:65
→ src/main/java/garage/Motorcycle.java:19
→ FAILURE: NullPointerException at spot.getWidth()
```

The test creates a Motorcycle. Because that class overrides fitsInSpot, runtime dispatch selects the Motorcycle implementation. The null check in the base method is not automatically executed before an override.

Recorded values:

| Variable | Actual value |
|---|---|
| `spot` | `null` |
| `this.licensePlate` | `"MOTO-002"` |
| `this.enteredAt.toString()` | `"2026-11-11T13:48:28.114111200"` |

Full transcript: [motorcycle-reproduction.txt](trace_evidence/debugger/motorcycle-reproduction.txt).

### Root cause

`Vehicle.fitsInSpot(null)` returns false without throwing. The Motorcycle override assumes a spot always exists. Crashing for the same argument breaks the safe behaviour established by the base class. The override effectively accepts a narrower set of inputs.

### Minimal fix and result

Current `Motorcycle.java:18–20`:

```java
if (spot == null) {
    return false;
}
```

The width and capacity rules and the public method signature are preserved. In the second debugger run, the same null argument reaches line 18 and then returns false at line 19. The assertion completes without an exception.

Evidence: [motorcycle-current.txt](trace_evidence/debugger/motorcycle-current.txt).

**Design rule:** An override should safely handle the inputs supported by the base method. Deal with null before accessing the object's fields or methods.

## 5. The current Truck test expectation

### Symptom

**Test:** `truckCheckoutFailsDueToMissingEnteredAt`  
**First failing assertion:** `src/test/java/garage/GarageTest.java:50`  
**Expected:** An IllegalStateException is thrown.  
**Actual:** The fee is calculated. Since the expected exception does not occur, JUnit raises an AssertionFailedError.

```text
Fee calculation should fail because enteredAt was never set
==> Expected java.lang.IllegalStateException to be thrown, but nothing was thrown.
```

### Trace

Recorded path through the current sources:

```text
tools/garage/DebugRunner.java:14
→ src/test/java/garage/GarageTest.java:50 — assertThrows
→ GarageTest.java:51 — checkOut inside the lambda
→ src/main/java/garage/Garage.java:67 — vehicle.calculateFee(rate)
→ src/main/java/garage/Vehicle.java:35 — enteredAt null check
→ Vehicle.java:38–39 — elapsed-time and fee calculation
→ assertThrows does not observe the expected exception
→ FAILURE: GarageTest.java:50
```

Truck does not override calculateFee. The inherited Vehicle implementation therefore calculates the truck's fee.

Recorded values:

| Variable | Actual value |
|---|---|
| `this.licensePlate` | `"TRK-002"` |
| `ratePerHour` | `5.0` |
| `this.enteredAt.toString()` | `"2026-11-11T13:48:33.307268100"` |
| `this.enteredAt != null` | `true` |

Evidence: [truck-current.txt](trace_evidence/debugger/truck-current.txt).

### Assessment

It is reasonable to test that fee calculation rejects an object with a missing entry time. However, the Truck created by this test now has an entry time. The test name and assertion message no longer describe its actual state.

The test's “constructor chaining bug” comment suggests that it may have been written to demonstrate the earlier defect. This is an interpretation, not confirmation of the author's intent. The original compilation failure also shows a mismatch between the distributed source and the expected runtime scenario.

The supplied test was preserved. The entry time was not reset to null and an artificial exception was not added just to satisfy this assertion. The instructor needs to clarify whether this test should demonstrate the old defect or verify the corrected behaviour. That question remains open.

**Design rule:** Compare the assertion's expectation with the actual state of its test object. “Expected an exception” does not mean the application itself threw one.

## 6. Additional behaviour checks

These checks were kept outside GarageTest.java, in the separately executable [GarageScenarioChecks.java](tools/garage/GarageScenarioChecks.java).

| Problem | Earlier behaviour | Change |
|---|---|---|
| findSpot compared capacity only | A 2.5 m truck could be assigned a space with 2.0 m clearance; a motorcycle could be assigned a 0.5 m-wide space | Current Garage.java:31 calls vehicle.fitsInSpot(spot) |
| Check-out released the first occupied space | With a car in A1 and a truck in A2, checking out the truck released A1 | assignedSpots maps each plate to its actual space, which is released on departure |
| The session was removed before fee calculation | If a null entry time caused calculation to fail, the session disappeared but its space remained occupied | Garage.java:67 calculates the fee before removing either record |

Against the snapshot taken before the final review, 6 checks passed and 2 failed. The failures were releasing the wrong space and losing the session after a calculation exception. The findSpot correction was already present in that snapshot.

All 8 checks pass against the final sources. They cover truck clearance, motorcycle width, releasing the correct space, preserving records on a failed fee calculation, Truck entry time, Motorcycle null handling, duplicate check-in rejection, and an unknown plate at check-out.

Records: [scenarios-before.txt](trace_evidence/logs/scenarios-before.txt) and [scenarios-after.txt](trace_evidence/logs/scenarios-after.txt).

The same checks were also run against the old source copy with only the Truck compilation blocker removed. That reproduction passes 3 checks and fails 5, including the old findSpot clearance and width cases. These are separate behaviour checks, not the supplied JUnit test count. See [scenarios-reproduction.txt](trace_evidence/logs/scenarios-reproduction.txt).

## 7. Patch and scope

The source changes are in [fix.patch](fix.patch). Apply it to the original sources already arranged in the Maven layout under repository-original. Moving the Java files from the repository root into src and correcting the Vehicle filename are layout preparation steps before this patch.

The patch changes three production files:

- Truck.java calls the superclass constructor and removes the redundant plate assignment.
- Motorcycle.java returns false early for a null spot.
- Garage.java delegates fitting to the vehicle, records the assigned space, and delays session removal until fee calculation succeeds.

The unused requirement variable and outdated BUG comments were removed. Car, Spot, Vehicle, and the public method signatures are preserved. The hourly tariff, one-hour minimum, and motorcycle space-sharing behaviour are unchanged.

The patch was checked with git apply --check on a temporary original copy, applied, and compared with the final sources. The supplied test file's SHA-256 is identical before and after preparation. Results are in [verification.json](trace_evidence/verification.json).

## 8. Trace evidence

- [Failure transcript](trace_evidence/debugger/motorcycle-reproduction.txt): stack frames and actual spot, licensePlate, and enteredAt values.
- [Corrected-method transcript](trace_evidence/debugger/motorcycle-current.txt): stepping from the null check to returning false.
- [Truck transcript](trace_evidence/debugger/truck-current.txt): initialized entry time and the failing assertThrows path.
- IDE captures and their source versions are described in the [evidence guide](trace_evidence/README.md).

## 9. Final test output

The following output was captured by running Maven against the final sources. The supplied suite passes **6/7** because of the Truck assertion discussed above. The failure is preserved.

```text
Captured: 2026-11-11T14:17:17.916911+03:00
Working directory: C:\Users\Tahae\OOP-home-quiz\parking-garage
Command: C:\Users\Tahae\AppData\Local\Programs\ApacheMaven\apache-maven-3.9.16\bin\mvn.cmd --batch-mode --no-transfer-progress test
Exit code: 1

[INFO] Scanning for projects...
[INFO] 
[INFO] -----------------------< edu.oop:parking-garage >-----------------------
[INFO] Building parking-garage 1.0-SNAPSHOT
[INFO]   from pom.xml
[INFO] --------------------------------[ jar ]---------------------------------
[INFO] 
[INFO] --- resources:3.4.0:resources (default-resources) @ parking-garage ---
[INFO] skip non existing resourceDirectory C:\Users\Tahae\OOP-home-quiz\parking-garage\src\main\resources
[INFO] 
[INFO] --- compiler:3.15.0:compile (default-compile) @ parking-garage ---
[INFO] Nothing to compile - all classes are up to date.
[INFO] 
[INFO] --- resources:3.4.0:testResources (default-testResources) @ parking-garage ---
[INFO] skip non existing resourceDirectory C:\Users\Tahae\OOP-home-quiz\parking-garage\src\test\resources
[INFO] 
[INFO] --- compiler:3.15.0:testCompile (default-testCompile) @ parking-garage ---
[INFO] Nothing to compile - all classes are up to date.
[INFO] 
[INFO] --- surefire:3.2.5:test (default-test) @ parking-garage ---
[INFO] Using auto detected provider org.apache.maven.surefire.junitplatform.JUnitPlatformProvider
[INFO] 
[INFO] -------------------------------------------------------
[INFO]  T E S T S
[INFO] -------------------------------------------------------
[INFO] Running garage.GarageTest
[ERROR] Tests run: 7, Failures: 1, Errors: 0, Skipped: 0, Time elapsed: 0.090 s <<< FAILURE! -- in garage.GarageTest
[ERROR] garage.GarageTest.truckCheckoutFailsDueToMissingEnteredAt -- Time elapsed: 0.008 s <<< FAILURE!
org.opentest4j.AssertionFailedError: Fee calculation should fail because enteredAt was never set ==> Expected java.lang.IllegalStateException to be thrown, but nothing was thrown.
	at org.junit.jupiter.api.AssertionFailureBuilder.build(AssertionFailureBuilder.java:152)
	at org.junit.jupiter.api.AssertThrows.assertThrows(AssertThrows.java:73)
	at org.junit.jupiter.api.AssertThrows.assertThrows(AssertThrows.java:39)
	at org.junit.jupiter.api.Assertions.assertThrows(Assertions.java:3131)
	at garage.GarageTest.truckCheckoutFailsDueToMissingEnteredAt(GarageTest.java:50)
	at java.base/java.lang.reflect.Method.invoke(Method.java:569)
	at java.base/java.util.ArrayList.forEach(ArrayList.java:1511)
	at java.base/java.util.ArrayList.forEach(ArrayList.java:1511)

[INFO] 
[INFO] Results:
[INFO] 
[ERROR] Failures: 
[ERROR]   GarageTest.truckCheckoutFailsDueToMissingEnteredAt:50 Fee calculation should fail because enteredAt was never set ==> Expected java.lang.IllegalStateException to be thrown, but nothing was thrown.
[INFO] 
[ERROR] Tests run: 7, Failures: 1, Errors: 0, Skipped: 0
[INFO] 
[INFO] ------------------------------------------------------------------------
[INFO] BUILD FAILURE
[INFO] ------------------------------------------------------------------------
[INFO] Total time:  2.659 s
[INFO] Finished at: 2026-11-11T14:17:17+03:00
[INFO] ------------------------------------------------------------------------
[ERROR] Failed to execute goal org.apache.maven.plugins:maven-surefire-plugin:3.2.5:test (default-test) on project parking-garage: There are test failures.
[ERROR] 
[ERROR] Please refer to C:\Users\Tahae\OOP-home-quiz\parking-garage\target\surefire-reports for the individual test results.
[ERROR] Please refer to dump files (if any exist) [date].dump, [date]-jvmRun[N].dump and [date].dumpstream.
[ERROR] -> [Help 1]
[ERROR] 
[ERROR] To see the full stack trace of the errors, re-run Maven with the -e switch.
[ERROR] Re-run Maven using the -X switch to enable full debug logging.
[ERROR] 
[ERROR] For more information about the errors and possible solutions, please read the following articles:
[ERROR] [Help 1] http://cwiki.apache.org/confluence/display/MAVEN/MojoFailureException
```

## 10. Limits and submission status

The supplied test file is unchanged. The 7/7 JUnit requirement is not yet met because the remaining assertion's expectation needs clarification. Passing all 8 additional checks does not replace that result.

getSpots() and getActiveSessions() still expose mutable collections. This work does not redesign the public API to prevent callers from manually corrupting those collections. The checks exercise normal addSpot, checkIn, and checkOut calls.

The submission repository is [tahaeker/parking-garage](https://github.com/tahaeker/parking-garage). The source, report, and evidence are prepared for that repository. The instructor's clarification and the oral defence are separate from file preparation.
