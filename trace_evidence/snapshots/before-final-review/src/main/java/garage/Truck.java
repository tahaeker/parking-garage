package garage;

import java.time.LocalDateTime;

public class Truck extends Vehicle {

    private final double height;

    public Truck(String licensePlate, double height) {
        // BUG: never calls super(...), so enteredAt is never set

        super(licensePlate,LocalDateTime.now());
        this.licensePlate = licensePlate;
        this.height = height;
    }

    public double getHeight() {
        return height;
    }

    @Override
    public double getSpotRequirement() {
        return 2.0;
    }

    @Override
    public boolean fitsInSpot(Spot spot) {
        if (spot == null) {
            return false;
        }
        return spot.getCapacity() >= 2.0 && spot.getClearance() >= height;
    }
}