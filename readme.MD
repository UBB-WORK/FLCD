# SensorScript: Language Specification & Use Case Documentation

## 1. Choice of Statements & Justifications

### 1.1 Input / Output (I/O) Statements

-   **Syntax**:
    ```text
    read(<variable_access>);
    write(<expression>);
    ```
-   **Semantic Description**:
    -   `read`: Ingests an integer value from standard input
    -   `write`: Evaluates an expression and dispatches the resulting integer to standard output
-   **Domain Justification**: An IoT system must interface with physical hardware. Without dedicated I/O, the program cannot sample its environment or transmit safety signals.

#### Explanatory Example:

```c
// Polls the sensor located in the room then writes to standard output
read(roomTemperature);
write(roomTemperature);
```

---

### 1.2 Assignment Statement

-   **Syntax**:
    ```text
    <variable_access> = <expression>;
    ```
-   **Semantic Description**: Evaluates an arithmetic expression and binds the calculated value to a variable or array cell.
-   **Domain Justification**: Sensor processing requires continuous state maintenance accumulating totals for moving averages, tracking iteration indices, and computing differential metrics.

#### Explanatory Example:

```c
// Accumulate raw readings into a cumulative sum and record to buffer
sum = sum + currentReading;
buffer[sampleIndex] = currentReading;
```

---

### 1.3 Conditional Statements (`if` / `if-else`)

-   **Syntax**:
    ```text
    if (<condition>) {
        <statement_list>
    }
    ```
    or
    ```text
    if (<condition>) {
        <statement_list>
    } else {
        <statement_list>
    }
    ```
-   **Semantic Description**: Evaluates a relational condition. If the condition holds true, the primary compound statement executes; otherwise, the optional alternative executes.
-   **Domain Justification**: The primary role of an IoT monitor is anomaly detection. When measurements exceed safe physical thresholds, immediate branching logic is needed to raise alerts or shutdown machinery.

#### Explanatory Example:

```c
// Safety interlock: Trigger emergency alarm if temperature exceeds threshold
if (currentTemp > 40) {
    write(999); // Emits hazard alert code 999
} else {
    write(0);   // Emits "All Normal" code
}
```

---

### 1.4 Loop Statement (`while`)

-   **Syntax**:
    ```text
    while (<condition>) {
        <statement_list>
    }
    ```
-   **Semantic Description**: Re-evaluates a condition before each iteration and repeatedly executes the inner block while the condition evaluates to true.
-   **Domain Justification**: Arrays holding data / measurements must be traversed to calculate statistical aggregates. The `while` loop offers general-purpose iteration without complex syntax.

#### Explanatory Example:

```c
// Traverses a 5-element array to calculate total sum
i = 0;
sum = 0;
while (i < 5) {
    sum = sum + samples[i];
    i = i + 1;
}
average = sum / 5;
```

---
