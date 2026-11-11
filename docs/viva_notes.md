# Oral Defence Notes

## Explaining the motorcycle trace

1. `GarageTest.java:65` calls `fitsInSpot(null)`.
2. The method selected at runtime is `Motorcycle.fitsInSpot`, because the object is a Motorcycle.
3. In the old source, `Motorcycle.java:19` calls `spot.getWidth()`.
4. The debugger shows `spot = null` and `licensePlate = "MOTO-002"`.
5. Calling an instance method on null produces a `NullPointerException`.
6. The current version checks null at line 18 and returns false at line 19.

The old and current line numbers refer to different source versions. The old source is under `trace_evidence/snapshots/reproduce-motorcycle-failure`; the current source is under `src/main/java`.

## Questions to practise

**Why does an abstract method have no body?** It requires subclasses to provide an implementation. For `getSpotRequirement`, Car returns 1.0, Motorcycle returns 0.5, and Truck returns 2.0.

**Why does the Truck method run when the variable type is Vehicle?** An overridden instance method is selected using the object's runtime class. A Truck object uses `Truck.fitsInSpot`.

**Why is a capacity check insufficient?** Truck also checks clearance, and Motorcycle also checks width. `findSpot` calls the vehicle's fitting method rather than duplicating these rules.

**Why check null first?** The object must exist before `getWidth()` or another instance method can be called. Returning false early prevents that invalid access.

**How does the Liskov Substitution Principle apply here?** The base method returns false for a null spot without throwing. A subclass that crashes for the same argument breaks that behaviour contract.

**Why is the Truck test still failing?** It expects an `IllegalStateException`. The current constructor sets the entry time, so that exception is not thrown. The debugger confirms the field is non-null. The intended purpose of the test has not been confirmed.

**Why record the assigned space?** Without a plate-to-space mapping, check-out releases the first occupied space. `assignedSpots` records which space belongs to the departing vehicle.

**Why calculate the fee before removing the session?** If calculation throws, check-out has not completed. The session and occupied space should remain consistent.

## Live demonstration

Repeat the commands in `trace_evidence/README.md`. Explain `where`, `locals`, and `print spot` while following the trace. Practise setting the breakpoint and inspecting the actual variables rather than memorizing the output.
