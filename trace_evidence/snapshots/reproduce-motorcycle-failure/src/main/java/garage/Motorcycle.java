package garage;

import java.time.LocalDateTime;

public class Motorcycle extends Vehicle {

    public Motorcycle(String licensePlate, LocalDateTime enteredAt) {
        super(licensePlate, enteredAt);
    }

    @Override
    public double getSpotRequirement() {
        return 0.5;
    }

    @Override
    public boolean fitsInSpot(Spot spot) {
        // BUG: assumes spot is never null
        return spot.getWidth() >= 1.0 && spot.getCapacity() >= 0.5;
    }
}