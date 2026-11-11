package garage;

/** Runs the supplied test methods individually so a debugger can inspect them. */
public final class DebugRunner {
    public static void main(String[] args) {
        GarageTest test = new GarageTest();
        test.setUp();
        if (args.length != 1) {
            throw new IllegalArgumentException("Use motorcycle or truck");
        }
        if ("motorcycle".equals(args[0])) {
            test.motorcycleHandlesNullSpotGracefully();
        } else if ("truck".equals(args[0])) {
            test.truckCheckoutFailsDueToMissingEnteredAt();
        } else {
            throw new IllegalArgumentException(args[0]);
        }
    }
}
