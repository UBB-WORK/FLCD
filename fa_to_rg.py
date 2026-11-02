import string


class RegularGrammar:
    def __init__(self, N, sigma, P, S):
        self.N = N          # Set of non-terminals
        self.sigma = sigma  # Set of terminals
        self.P = P          # Dictionary: lhs -> list of rhs strings
        self.S = S          # Start symbol

    def display(self):
        print("\n=== Regular Grammar (RG) ===")
        print(f"Non-terminals (N) : {{ {', '.join(self.N)} }}")
        print(f"Terminals (Sigma) : {{ {', '.join(self.sigma)} }}")
        print(f"Start Symbol (S)  : {self.S}")
        print("Productions (P)   :")
        for lhs, rhs_list in self.P.items():
            formatted_rhs = " | ".join(rhs_list)
            print(f"  {lhs} -> {formatted_rhs}")
        print("============================\n")


class FiniteAutomaton:
    def __init__(self):
        self.Q = []          # States
        self.sigma = []      # Alphabet
        self.q0 = ""         # Initial state
        self.F = []          # Final states
        self.delta = {}      # Transitions: (state, symbol) -> list of next_states

    def load_from_file(self, filename):
        self.Q, self.sigma, self.F, self.delta = [], [], [], {}
        self.q0 = ""

        def expand_symbol(sym):
            if sym == "[LETTERS]":
                return list(string.ascii_letters)
            if sym == "[DIGITS]":
                return list(string.digits)
            if sym == "[NONZERO_DIGITS]":
                return list(string.digits[1:])
            return [sym]

        with open(filename, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]

        mode = None
        for line in lines:
            if line.startswith("STATES:"):
                self.Q = [x.strip() for x in line.split(":", 1)[1].split(",")]
            elif line.startswith("ALPHABET:"):
                raw_sigma = [x.strip() for x in line.split(":", 1)[1].split(",")]
                for rs in raw_sigma:
                    self.sigma.extend(expand_symbol(rs))
            elif line.startswith("INITIAL:"):
                self.q0 = line.split(":", 1)[1].strip()
            elif line.startswith("FINAL:"):
                self.F = [x.strip() for x in line.split(":", 1)[1].split(",")]
            elif line.startswith("TRANSITIONS:"):
                mode = "TRANSITIONS"
            elif mode == "TRANSITIONS":
                left, right = line.split("->")
                state, symbol_macro = [x.strip() for x in left.split(",")]
                next_state = right.strip()

                # Automatically generate a transition for every actual letter/digit
                for actual_char in expand_symbol(symbol_macro):
                    if (state, actual_char) not in self.delta:
                        self.delta[(state, actual_char)] = []
                    if next_state not in self.delta[(state, actual_char)]:
                        self.delta[(state, actual_char)].append(next_state)

    def display(self):
        print("\n=== Finite Automaton (FA) ===")
        print(f"States (Q)         : {{ {', '.join(self.Q)} }}")
        print(f"Alphabet (Sigma)   : {{ {', '.join(self.sigma)} }}")
        print(f"Initial State (q0) : {self.q0}")
        print(f"Final States (F)   : {{ {', '.join(self.F)} }}")
        print("Transitions (delta):")
        for (state, symbol), next_states in self.delta.items():
            for ns in next_states:
                print(f"  delta({state}, '{symbol}') = {ns}")
        print("=============================\n")

    def to_regular_grammar(self):
        """
        Theorem 2 Implementation: Construct Right-Linear Grammar G based on FA M
        N = Q
        S = q0
        P: if delta(q, a) = p then q -> a p
           if p in F then q -> a
           if q0 in F then S -> epsilon
        """
        N = list(self.Q)
        sigma = list(self.sigma)
        S = self.q0
        P = {state: [] for state in N}

        if self.q0 in self.F:
            P[S].append("ε")

        # process transitions
        for (q, a), next_states in self.delta.items():
            for p in next_states:
                # q -> a p
                prod_non_term = f"{a} {p}"
                if prod_non_term not in P[q]:
                    P[q].append(prod_non_term)

                # if p in F then q -> a
                if p in self.F:
                    prod_term = f"{a}"
                    if prod_term not in P[q]:
                        P[q].append(prod_term)

        # Clean up states with no outgoing productions
        P = {k: v for k, v in P.items() if v}

        return RegularGrammar(N, sigma, P, S)

    def _map_char_to_symbol(self, char):
        # map real characters to symbolic alphabet classes for verification.
        if char in self.sigma:
            return char
        if char.isalpha() and "letter" in self.sigma:
            return "letter"
        if char.isdigit():
            if "digit" in self.sigma:
                return "digit"
            if char != '0' and "nonzero_digit" in self.sigma:
                return "nonzero_digit"
        return char

    def accepts(self, word):
        # simulates the FA to check if a concrete token string is accepted.
        current_state = self.q0
        print(f"\nTracing '{word}':")
        for char in word:
            symbol = self._map_char_to_symbol(char)
            if (current_state, symbol) in self.delta:
                next_state = self.delta[(current_state, symbol)][0]
                print(f"  ({current_state}, '{char}' [{symbol}]) |- {next_state}")
                current_state = next_state
            else:
                print(f"  ({current_state}, '{char}' [{symbol}]) |- BLOCKED (No transition)")
                return False

        is_accepted = current_state in self.F
        print(f"Final state reached: {current_state} (In F? {is_accepted})")
        return is_accepted


def main():
    fa = FiniteAutomaton()
    rg = None

    while True:
        print("1. Load FA for Identifiers (fa_identifier.in)")
        print("2. Load FA for Integer Constants (fa_constant.in)")
        print("3. Display current Finite Automaton (FA)")
        print("4. Transform FA -> Regular Grammar (RG) & Display")
        print("5. Verify a token string against current FA")
        print("0. Exit")
        choice = input("Select an option: ").strip()

        if choice == '1':
            fa.load_from_file("fa_identifier.in")
            print("-> Loaded Identifier FA successfully.\n")
        elif choice == '2':
            fa.load_from_file("fa_constant.in")
            print("-> Loaded Constant FA successfully.\n")
        elif choice == '3':
            if not fa.Q:
                print("-> Please load an FA first (Option 1 or 2).\n")
            else:
                fa.display()
        elif choice == '4':
            if not fa.Q:
                print("-> Please load an FA first (Option 1 or 2).\n")
            else:
                rg = fa.to_regular_grammar()
                rg.display()
        elif choice == '5':
            if not fa.Q:
                print("-> Please load an FA first (Option 1 or 2).\n")
            else:
                word = input("Enter a token to test (e.g., current_val, 85, 05, 123abc): ").strip()
                if fa.accepts(word):
                    print(f"=> RESULT: '{word}' is VALID.\n")
                else:
                    print(f"=> RESULT: '{word}' is INVALID.\n")
        elif choice == '0':
            break
        else:
            print("-> Invalid option.\n")


if __name__ == "__main__":
    main()
