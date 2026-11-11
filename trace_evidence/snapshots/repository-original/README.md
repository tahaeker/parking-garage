# Parking Garage System

A small library for managing vehicle entry/exit and fee calculation.

## Public API

- `Garage.addSpot(spot)` — register a parking spot
- `Garage.checkIn(vehicle)` — attempt to park a vehicle, returns `boolean`
- `Garage.checkOut(licensePlate, rate)` — remove vehicle, return fee (`Double`, or `null`)
- `Vehicle.calculateFee(rate)` — compute fee based on time parked
- `Vehicle.fitsInSpot(spot)` — whether this vehicle can use the given spot

## Build & test

```bash
mvn test