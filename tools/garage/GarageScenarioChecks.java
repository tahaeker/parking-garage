package garage;

import java.time.LocalDateTime;

/** Additional checks kept outside the instructor's unchanged JUnit test suite. */
public final class GarageScenarioChecks {
    private static int passed;
    private static int failed;

    public static void main(String[] args) {
        run("truck height is respected by findSpot", () -> {
            Garage garage = new Garage("Low ceiling");
            garage.addSpot(new Spot("LOW", 2.0, 3.0, 2.0));
            check(garage.findSpot(new Truck("TALL", 2.5)) == null,
                    "A 2.5m truck must not be assigned a 2.0m spot");
        });
        run("motorcycle width is respected by findSpot", () -> {
            Garage garage = new Garage("Narrow spot");
            garage.addSpot(new Spot("NARROW", 0.5, 0.5, 2.0));
            check(garage.findSpot(new Motorcycle("MOTO", LocalDateTime.now())) == null,
                    "A motorcycle must not be assigned a spot narrower than 1.0m");
        });
        run("checkout frees the departing vehicle's spot", () -> {
            Garage garage = new Garage("Checkout order");
            Spot a1 = new Spot("A1", 1.0, 2.0, 2.0);
            Spot a2 = new Spot("A2", 2.0, 3.0, 3.0);
            garage.addSpot(a1);
            garage.addSpot(a2);
            check(garage.checkIn(new Car("CAR", LocalDateTime.now())), "Car check-in failed");
            check(garage.checkIn(new Truck("TRUCK", 2.5)), "Truck check-in failed");
            garage.checkOut("TRUCK", 5.0);
            check(a1.isOccupied(), "The car's A1 spot was incorrectly freed");
            check(!a2.isOccupied(), "The truck's A2 spot remained occupied");
            check(garage.getActiveSessions().containsKey("CAR"), "The car's session was removed");
            check(!garage.getActiveSessions().containsKey("TRUCK"), "The truck's session remained");
        });
        run("failed fee calculation preserves the session", () -> {
            Garage garage = new Garage("Missing entry time");
            Spot spot = new Spot("B1", 1.0, 2.0, 2.0);
            garage.addSpot(spot);
            check(garage.checkIn(new Car("BAD-TIME", null)), "Initial check-in failed");
            boolean threw = false;
            try {
                garage.checkOut("BAD-TIME", 5.0);
            } catch (IllegalStateException expected) {
                threw = true;
            }
            check(threw, "Missing entry time must cause an explicit error");
            check(garage.getActiveSessions().containsKey("BAD-TIME"), "Session was lost on failure");
            check(spot.isOccupied(), "Spot was freed even though checkout failed");
        });
        run("truck entry time is initialized", () -> {
            Truck truck = new Truck("TRUCK-TIME", 2.0);
            check(truck.getEnteredAt() != null, "Truck entry time is missing");
            check(truck.calculateFee(5.0) == 5.0, "The minimum one-hour fee should be 5.0");
        });
        run("motorcycle rejects a null spot", () ->
                check(!new Motorcycle("NULL-SPOT", LocalDateTime.now()).fitsInSpot(null),
                        "A null spot must return false"));
        run("duplicate check-in is rejected", () -> {
            Garage garage = new Garage("Duplicate");
            garage.addSpot(new Spot("A1", 1.0, 2.0, 2.0));
            Car car = new Car("SAME", LocalDateTime.now());
            check(garage.checkIn(car), "First check-in failed");
            check(!garage.checkIn(car), "Duplicate check-in was accepted");
        });
        run("unknown checkout returns null", () ->
                check(new Garage("Empty").checkOut("ABSENT", 5.0) == null,
                        "An unknown license plate must return null"));
        System.out.println("SCENARIOS: " + passed + " passed, " + failed + " failed");
        if (failed != 0) {
            System.exit(1);
        }
    }

    private static void run(String name, Runnable scenario) {
        try {
            scenario.run();
            passed++;
            System.out.println("PASS: " + name);
        } catch (RuntimeException | AssertionError error) {
            failed++;
            System.out.println("FAIL: " + name + " -- " + error.getMessage());
        }
    }

    private static void check(boolean condition, String message) {
        if (!condition) {
            throw new AssertionError(message);
        }
    }
}
