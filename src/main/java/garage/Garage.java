package garage;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class Garage {

    private final String name;
    private final List<Spot> spots = new ArrayList<>();
    private final Map<String, Vehicle> activeSessions = new HashMap<>();
    private final Map<String, Spot> assignedSpots = new HashMap<>();

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
        for (Spot spot : spots) {
            if (spot.isOccupied()) {
                continue;
            }
            if (vehicle.fitsInSpot(spot)) {
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

        for (Spot spot : spots) {
            if (!spot.isOccupied() && vehicle.fitsInSpot(spot)) {
                spot.setOccupied(true);
                activeSessions.put(vehicle.getLicensePlate(), vehicle);
                assignedSpots.put(vehicle.getLicensePlate(), spot);
                return true;
            }
        }

        return false;
    }

    /**
     * Remove vehicle and return fee owed, or null if not present.
     */
    public Double checkOut(String licensePlate, double rate) {
        Vehicle vehicle = activeSessions.get(licensePlate);
        if (vehicle == null) {
            return null;
        }

        double fee = vehicle.calculateFee(rate);
        activeSessions.remove(licensePlate);
        Spot spot = assignedSpots.remove(licensePlate);
        if (spot != null) {
            spot.setOccupied(false);
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
