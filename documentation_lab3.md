# Lexical Analysis & Symbol Table

## 1. Use of Tools

This lexical analyzer was developed using **Flex** (Fast Lexical Analyzer Generator) and **C**.

-   **Flex** was chosen because it provides a highly efficient, declarative way to define token patterns using Regular Expressions. It automatically compiles these rules into a deterministic finite automaton (DFA) generated as C code (`lex.yy.c`).
-   **C** was used to manually implement the Symbol Table (ST) data structure from scratch, satisfying the requirement for manual memory management and data structure implementation. The Flex scanner natively integrates with the C codebase, calling the ST functions whenever an identifier or constant is detected.

## 2. Lexical Token Detection

Tokens are detected using regex rules defined in `scanner.l`. The order of rules is critical to avoid matching conflicts:

1.  **Keywords & Operators:** Matched first via explicit string literals (e.g., `"sensor_node"`, `"monitor"`, `"=="`). When detected, they are printed to the Program Internal Form (PIF) with an ST position of `-1`.
2.  **Constants:** Matched using the regex `0|[1-9][0-9]*`. This ensures constants are either a singular zero or a sequence of digits starting with a non-zero digit.
3.  **Identifiers:** Matched using `[a-zA-Z][a-zA-Z0-9_]*`. Because keywords are placed higher in the Flex file, Flex correctly prioritizes them over generic identifiers.
4.  **Error Handling:** A specific fallback regex `[0-9]+[a-zA-Z_]+[a-zA-Z0-9_]*` is used to catch invalidly constructed tokens (e.g., `123invalid`) before they can be erroneously split into a valid constant and a valid identifier. Unrecognized solitary characters are caught by the `.` catch-all rule.

## 3. Data Structures and Operations for ST Management

The Symbol Table is implemented in `symtable.c` as a **Hash Table** utilizing separate chaining to resolve collisions.

### 3.1 Data Structure

-   **Hash Table Array:** An array of 100 pointers to a `Node` struct (`Node* hashTable[100]`).
-   **Linked List Nodes:** Each `Node` contains a `char array` for the token string and a `next` pointer to handle collisions within the same bucket.

### 3.2 Core Operations

-   **`hashFunction(char* key)`:** Computes the index by summing the ASCII values of all characters in the token string and applying a modulo of the table size (`100`).
-   **`addToST(char* key)`:**
    1. Hashes the incoming token to find its bucket index.
    2. Traverses the linked list at that index. If the token already exists (checked via `strcmp`), it immediately returns the bucket index to prevent duplicates.
    3. If the token is not found, a new `Node` is allocated in memory (`malloc`).
    4. The new node is appended to the **tail** of the linked list. Appending to the tail ensures that the relative list order remains stable when collisions occur.
    5. Returns the hash bucket index, which the Flex scanner then records in the PIF.
