# SensorScript Documentation

## 1. Statements & Use Cases

### 1.1 I/O Statements: `sample` and `emit`

-   **Role:** `sample` reads from a hardware pin and `emit` writes to an output pin or telemetry bus.
-   **Justification:** Without these, the microchip cannot communicate with physical hardware. They enforce a direct link between the software and the physical environment.

```c
sample(currentTemp); // Ingest from hardware register
emit(currentTemp);   // Echo to output serial bus
```

### 1.2 Loop Statement: `monitor`

-   **Role:** Iterates over conditions or iterates through data buffers.
-   **Justification:** Replaces a traditional `while` loop.

```c
monitor (index < 5) {
    // Collect sensor data
}
```

### 1.3 Conditional Statement: `detect` / `otherwise`

-   **Role:** Alters execution flow depending on whether physical readings meet defined hazard limits.
-   **Justification:** Replaces `if / else`. Safety mechanisms in hardware depend on immediate threshold validation to avert damage.

```c
detect (currentTemp >= 75) {
    emit(999); // Emergency signal sent
} otherwise {
    emit(0);   // "All fine" signal sent
}
```

### 1.4 Assignment Statement (`=`)

-   **Role:** Stores calculated intermediate states into variables or buffer elements.
-   **Justification:** Necessary for calculating rolling sums, advancing indices, or updating internal state machines.

---
