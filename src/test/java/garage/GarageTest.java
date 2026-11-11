package garage;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.time.LocalDateTime;

import static org.junit.jupiter.api.Assertions.*;

class GarageTest {

    private Garage garage;

    @BeforeEach
    void setUp() {
        garage = new Garage("Downtown");
        garage.addSpot(new Spot("A1", 1.0, 2.0, 2.0));
        garage.addSpot(new Spot("A2", 2.0, 3.0, 3.0));
        garage.addSpot(new Spot("M1", 0.5, 1.0, 1.0));
    }

    @Test
    void carChecksInSuccessfully() {
        Car car = new Car("CAR-001", LocalDateTime.now());
        assertTrue(garage.checkIn(car));
        assertTrue(garage.getActiveSessions().containsKey("CAR-001"));
    }

    @Test
    void carCheckoutCalculatesFee() {
        Car car = new Car("CAR-002", LocalDateTime.now().minusHours(2));
        garage.checkIn(car);
        Double fee = garage.checkOut("CAR-002", 5.0);
        assertNotNull(fee);
        assertEquals(10.0, fee, 0.5);
    }

    @Test
    void truckChecksIn() {
        // Truck should fit in A2 (capacity 2.0, clearance 3.0)
        Truck truck = new Truck("TRK-001", 2.5);
        assertTrue(garage.checkIn(truck), "Truck should fit in A2");
    }

    @Test
    void truckCheckoutFailsDueToMissingEnteredAt() {
        // This test exposes the constructor chaining bug
        Truck truck = new Truck("TRK-002", 2.0);
        garage.checkIn(truck);
        assertThrows(IllegalStateException.class,
                () -> garage.checkOut("TRK-002", 5.0),
                "Fee calculation should fail because enteredAt was never set");
    }

    @Test
    void motorcycleFitsInMotorcycleSpot() {
        Motorcycle moto = new Motorcycle("MOTO-001", LocalDateTime.now());
        assertTrue(garage.checkIn(moto));
    }

    @Test
    void motorcycleHandlesNullSpotGracefully() {
        // A Motorcycle must return false for a null spot, not throw NPE
        Motorcycle moto = new Motorcycle("MOTO-002", LocalDateTime.now());
        assertFalse(moto.fitsInSpot(null),
                "fitsInSpot(null) should return false, not throw");
    }

    @Test
    void twoMotorcyclesShareSpotWithoutTracking() {
        // Exposes that spot sharing isn't actually tracked
        Motorcycle m1 = new Motorcycle("MOTO-003", LocalDateTime.now());
        Motorcycle m2 = new Motorcycle("MOTO-004", LocalDateTime.now());
        garage.checkIn(m1);
        garage.checkIn(m2);
        long occupiedCount = garage.getSpots().stream().filter(Spot::isOccupied).count();
        assertEquals(2, occupiedCount,
                "Two motorcycles should require two spots (no sharing logic)");
    }
}