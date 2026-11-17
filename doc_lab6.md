# Lab 6 Documentation: Syntactical Analysis

## 1. Formal Definition of the SensorScript

A Context-Free Grammar (CFG) is formally defined as a 4-tuple $G = (N, \Sigma, P, S)$ where:

-   **$N$ (Non-terminals):** $$N = \{ \text{program}, \text{stmt\_list}, \text{stmt}, \text{declaration}, \text{id\_list}, \text{assign\_stmt}, \text{io\_stmt}, \text{if\_stmt}, \text{while\_stmt}, \text{condition}, \text{rel\_op}, \text{expression}, \text{term}, \text{factor} \}$$

-   **$\Sigma$ (Terminals):**

    -   **Keywords:** `sensor_node`, `signal`, `buffer`, `detect`, `otherwise`, `monitor`, `sample`, `emit`
    -   **Operators:** `+`, `-`, `*`, `/`, `%`, `=`, `==`, `!=`, `<`, `<=`, `>`, `>=`
    -   **Separators:** `;`, `,`, `(`, `)`, `{`, `}`, `[`, `]`
    -   **Lexical Categories (validated via FA):** `id`, `int_const`, `str_const`

-   **$S$ (Start Symbol):** $\text{program}$

---

## 2. Numbered BNF Production Rules ($P$)

To output the required **string of productions** during bottom-up parsing, every BNF rule is assigned a unique production index $(1) \dots (43)$:

### Program Structure & Statements

1. $\text{program} \rightarrow \text{sensor\_node } \text{id } \{ \text{ stmt\_list } \}$
2. $\text{program} \rightarrow \text{stmt\_list}$
3. $\text{stmt\_list} \rightarrow \text{stmt}$
4. $\text{stmt\_list} \rightarrow \text{stmt\_list } \text{stmt}$
5. $\text{stmt} \rightarrow \text{declaration}$
6. $\text{stmt} \rightarrow \text{assign\_stmt}$
7. $\text{stmt} \rightarrow \text{io\_stmt}$
8. $\text{stmt} \rightarrow \text{if\_stmt}$
9. $\text{stmt} \rightarrow \text{while\_stmt}$

### Declarations (`signal`, `buffer`, `sensor_node`)

10. $\text{declaration} \rightarrow \text{signal } \text{id\_list } ;$
11. $\text{declaration} \rightarrow \text{signal } \text{id } = \text{expression } ;$
12. $\text{declaration} \rightarrow \text{sensor\_node } \text{id } ;$
13. $\text{declaration} \rightarrow \text{buffer } \text{id } [ \text{ int\_const } ] \text{ } ;$
14. $\text{declaration} \rightarrow \text{buffer } \text{id } = \text{str\_const } ;$
15. $\text{id\_list} \rightarrow \text{id}$
16. $\text{id\_list} \rightarrow \text{id\_list } , \text{ id}$

### Assignment & I/O Statements (`sample`, `emit`)

17. $\text{assign\_stmt} \rightarrow \text{id } = \text{expression } ;$
18. $\text{assign\_stmt} \rightarrow \text{id } [ \text{ expression } ] = \text{expression } ;$
19. $\text{io\_stmt} \rightarrow \text{sample } ( \text{ id } ) \text{ } ;$
20. $\text{io\_stmt} \rightarrow \text{sample } \text{id } ;$
21. $\text{io\_stmt} \rightarrow \text{emit } \text{expression } ;$

### Control Flow (`detect` / `otherwise` & `monitor`)

22. $\text{if\_stmt} \rightarrow \text{detect } ( \text{ condition } ) \text{ } \{ \text{ stmt\_list } \}$
23. $\text{if\_stmt} \rightarrow \text{detect } ( \text{ condition } ) \text{ } \{ \text{ stmt\_list } \} \text{ otherwise } \{ \text{ stmt\_list } \}$
24. $\text{while\_stmt} \rightarrow \text{monitor } ( \text{ condition } ) \text{ } \{ \text{ stmt\_list } \}$

### Conditions & Relational Operators

25. $\text{condition} \rightarrow \text{expression } \text{rel\_op } \text{expression}$
26. $\text{rel\_op} \rightarrow ==$
27. $\text{rel\_op} \rightarrow !=$
28. $\text{rel\_op} \rightarrow <$
29. $\text{rel\_op} \rightarrow <=$
30. $\text{rel\_op} \rightarrow >$
31. $\text{rel\_op} \rightarrow >=$

### Arithmetic & String Expressions

32. $\text{expression} \rightarrow \text{term}$
33. $\text{expression} \rightarrow \text{expression } + \text{ term}$
34. $\text{expression} \rightarrow \text{expression } - \text{ term}$
35. $\text{term} \rightarrow \text{factor}$
36. $\text{term} \rightarrow \text{term } * \text{ factor}$
37. $\text{term} \rightarrow \text{term } / \text{ factor}$
38. $\text{term} \rightarrow \text{term } \% \text{ factor}$
39. $\text{factor} \rightarrow \text{id}$
40. $\text{factor} \rightarrow \text{id } [ \text{ expression } ]$
41. $\text{factor} \rightarrow \text{int\_const}$
42. $\text{factor} \rightarrow \text{str\_const}$
43. $\text{factor} \rightarrow ( \text{ expression } )$

---

## 3. Parsing Architecture & Implementation

-   **Requirement 2 (Parsing from PIF):** `PIFLexer` reads the pre-generated `PIF.out` file from Lab 5, translates each token string into its terminal symbol, and passes the token stream into `ply.yacc`.
-   **Requirement 3 (Integrated Lex + FA + Yacc):** `IntegratedFALexer` combines `ply.lex` with the Lab 4/5 `FiniteAutomaton` state machines (`fa_identifier.in`, `fa_constant.in`, `fa_string.in`), validating identifiers, integer constants, and string literals via explicit state transitions while driving the LALR(1) parser.
