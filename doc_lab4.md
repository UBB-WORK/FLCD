# Lab 4 Documentation: Finite Automata (FA) to Regular Grammars (RG)

## 1. Formal Definition of Finite Automata (FA)

A Finite Automaton is formally defined as a 5-tuple $M = (Q, \Sigma, \delta, q_0, F)$ where:

-   **$Q$**: Finite set of states.
-   **$\Sigma$**: Finite input alphabet.
-   **$\delta$**: Transition function $\delta: Q \times \Sigma \rightarrow \mathcal{P}(Q)$.
-   **$q_0$**: Initial state ($q_0 \in Q$).
-   **$F$**: Set of final (accepting) states ($F \subseteq Q$).

---

### 1.1 FA for SensorScript Identifiers

Identifiers must start with a letter and can be followed by zero or more letters, digits, or underscores (`[a-zA-Z][a-zA-Z0-9_]*`).

-   **$Q$** = $\{S, A\}$
-   **$\Sigma$** = $\{\text{letter}, \text{digit}, \_ \}$
-   **$q_0$** = $S$
-   **$F$** = $\{A\}$ (Representing the accepting "double circle" state)
-   **Transitions ($\delta$)**:
    -   $\delta(S, \text{letter}) = A$
    -   $\delta(A, \text{letter}) = A$
    -   $\delta(A, \text{digit}) = A$
    -   $\delta(A, \_) = A$

---

### 1.2 FA for SensorScript Integer Constants

Integer constants are either a single zero or a sequence of digits starting with a non-zero digit (`0|[1-9][0-9]*`).

-   **$Q$** = $\{S, Z, N\}$
-   **$\Sigma$** = $\{0, \text{nonzero\_digit}\}$
-   **$q_0$** = $S$
-   **$F$** = $\{Z, N\}$ (Representing the accepting "double circle" states)
-   **Transitions ($\delta$)**:
    -   $\delta(S, 0) = Z$ _(State $Z$ has no outgoing transitions, preventing leading zeros like `05`)_
    -   $\delta(S, \text{nonzero\_digit}) = N$
    -   $\delta(N, 0) = N$
    -   $\delta(N, \text{nonzero\_digit}) = N$

---

## 2. Transformation Algorithm: FA to Regular Grammar (RG)

Based on Theorem 2 (Equivalence of Finite Automata and Right-Linear Grammars), for any FA $M = (Q, \Sigma, \delta, q_0, F)$, an equivalent right-linear grammar $G = (N, \Sigma, P, S)$ is constructed such that $L(G) = L(M)$:

1. **Non-terminals ($N$):** Set equal to the states of the automaton ($N = Q$).
2. **Terminals ($\Sigma$):** Set equal to the automaton's alphabet.
3. **Start Symbol ($S$):** Set equal to the initial state ($S = q_0$).
4. **Production Rules ($P$):** Constructed by iterating over all transitions in $\delta$:
    - **Rule 1 ("Keep Going"):** For every transition $\delta(q, a) = p$, add the production $q \rightarrow a p$ to $P$.
    - **Rule 2 ("Stop Here"):** If the destination state $p \in F$ (a final double-circle state), also add the terminating production $q \rightarrow a$ to $P$. This gives the grammar mathematical permission to successfully complete the derivation.
    - **Rule 3 (Epsilon rule):** If the initial state is also a final state ($q_0 \in F$), add the production $S \rightarrow \epsilon$ to $P$.

---

## 3. Resulting Regular Grammars

### 3.1 Generated RG for Identifiers

Applying the transformation algorithm to the Identifiers FA yields:

-   **$N$** = $\{S, A\}$
-   **$\Sigma$** = $\{\text{letter}, \text{digit}, \_ \}$
-   **$S$** = $S$
-   **$P$**:
    -   $S \rightarrow \text{letter } A \mid \text{letter}$
    -   $A \rightarrow \text{letter } A \mid \text{letter} \mid \text{digit } A \mid \text{digit} \mid \_ A \mid \_$

### 3.2 Generated RG for Integer Constants

Applying the transformation algorithm to the Integer Constants FA yields:

-   **$N$** = $\{S, Z, N\}$ _(Note: $Z$ has no outgoing transitions, so it produces no left-hand side rules; it is only reached terminally via $S \rightarrow 0$)_
-   **$\Sigma$** = $\{0, \text{nonzero\_digit}\}$
-   **$S$** = $S$
-   **$P$**:
    -   $S \rightarrow 0 Z \mid 0 \mid \text{nonzero\_digit } N \mid \text{nonzero\_digit}$
    -   $N \rightarrow 0 N \mid 0 \mid \text{nonzero\_digit } N \mid \text{nonzero\_digit}$

## 4. Implementation Details

The transformation is automated in Python (`fa_to_rg.py`) utilizing two primary classes:

-   **`FiniteAutomaton`**: Parses the `.in` configuration files, mapping transitions into a dictionary (`self.delta`). It identifies final states via `self.F` and executes the `to_regular_grammar()` mechanical transformation.
-   **`RegularGrammar`**: Encapsulates the resulting 4-tuple $(N, \Sigma, P, S)$. It dynamically cleans up empty non-terminals (like `Z`) and formats the output into strict BNF notation using the logical OR pipe (`|`) to group productions originating from the same non-terminal.
