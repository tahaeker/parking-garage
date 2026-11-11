package garage;

import java.time.Duration;
import java.time.LocalDateTime;

/**
 * Abstract base for all vehicles entering the garage.
 */
public abstract class Vehicle {

    protected String licensePlate;
    protected LocalDateTime enteredAt;

    public Vehicle(String licensePlate, LocalDateTime enteredAt) {
        this.licensePlate = licensePlate;
        this.enteredAt = enteredAt;
    }

    /**
     * Return how many capacity units this vehicle needs.
     */
    public abstract double getSpotRequirement();

    /**
     * Default: any vehicle fits if the spot exists.
     */
    public boolean fitsInSpot(Spot spot) {
        return spot != null;
    }

    /**
     * Default fee calculation based on time parked.
     */
    public double calculateFee(double ratePerHour) {
        if (enteredAt == null) {
            throw new IllegalStateException("enteredAt was never set");
        }
        double hours = Duration.between(enteredAt, LocalDateTime.now()).toMinutes() / 60.0;
        return Math.max(1.0, hours) * ratePerHour;
    }

    public String getLicensePlate() {
        return licensePlate;
    }

    public LocalDateTime getEnteredAt() {
        return enteredAt;
    }

    @Override
    public String toString() {
        return getClass().getSimpleName() + "(" + licensePlate + ")";
    }
}