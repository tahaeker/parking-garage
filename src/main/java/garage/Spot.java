package garage;

public class Spot {

    private final String spotId;
    private final double capacity;
    private final double width;
    private final double clearance;
    private boolean occupied;

    public Spot(String spotId, double capacity, double width, double clearance) {
        this.spotId = spotId;
        this.capacity = capacity;
        this.width = width;
        this.clearance = clearance;
        this.occupied = false;
    }

    public String getSpotId()   { return spotId; }
    public double getCapacity()  { return capacity; }
    public double getWidth()     { return width; }
    public double getClearance() { return clearance; }

    public boolean isOccupied()          { return occupied; }
    public void setOccupied(boolean o)   { this.occupied = o; }

    @Override
    public String toString() {
        return "Spot(" + spotId + ", cap=" + capacity + ")";
    }
}