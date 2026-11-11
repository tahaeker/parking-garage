package garage;

import java.time.LocalDateTime;

public class Car extends Vehicle {

    public Car(String licensePlate, LocalDateTime enteredAt) {
        super(licensePlate, enteredAt);
    }

    @Override
    public double getSpotRequirement() {
        return 1.0;
    }

    @Override
    public boolean fitsInSpot(Spot spot) {
        return spot != null && spot.getCapacity() >= 1.0;
    }
}