package garage;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class Garage {

    private final String name;
    private final List<Spot> spots = new ArrayList<>();
    private final Map<String, Vehicle> activeSessions = new HashMap<>();

    public Garage(String name) {
        this.name = name;
    }

    public void addSpot(Spot spot) {
        spots.add(spot);
    }

    /**
     * Find a spot that can accommodate the vehicle.
     */
    public Spot findSpot(Vehicle vehicle) {
        double requirement = vehicle.getSpotRequirement();
        for (Spot spot : spots) {
            if (spot.isOccupied()) {
                continue;
            }
            if (vehicle.fitsInSpot(spot)) {
                // BUG: uses capacity comparison but ignores fitsInSpot()
                return spot;
            }
        }
        return null;
    }

    /**
     * Attempt to park a vehicle. Returns true if successful.
     */
    public boolean checkIn(Vehicle vehicle) {
        if (activeSessions.containsKey(vehicle.getLicensePlate())) {
            return false;
        }

        // BUG: this call assumes fitsInSpot handles null safely
        for (Spot spot : spots) {
            if (!spot.isOccupied() && vehicle.fitsInSpot(spot)) {
                spot.setOccupied(true);
                activeSessions.put(vehicle.getLicensePlate(), vehicle);
                return true;
            }
        }

        return false;
    }

    /**
     * Remove vehicle and return fee owed, or null if not present.
     */
    public Double checkOut(String licensePlate, double rate) {
        Vehicle vehicle = activeSessions.remove(licensePlate);
        if (vehicle == null) {
            return null;
        }

        double fee = vehicle.calculateFee(rate);

        for (Spot spot : spots) {
            if (spot.isOccupied()) {
                // BUG: naively frees the first occupied spot, not the vehicle's actual spot
                spot.setOccupied(false);
                break;
            }
        }

        return fee;
    }

    public List<Spot> getSpots() {
        return spots;
    }

    public Map<String, Vehicle> getActiveSessions() {
        return activeSessions;
    }
}