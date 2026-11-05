import string
import re


class SymbolTable:
    def __init__(self, size=101):
        self.size = size
        self.table = [[] for _ in range(size)]

    def _hash(self, key):
        return sum(ord(c) for c in str(key)) % self.size

    def add(self, key):
        bucket_idx = self._hash(key)
        bucket = self.table[bucket_idx]
        for idx, existing_key in enumerate(bucket):
            if existing_key == key:
                return (bucket_idx, idx)
        bucket.append(key)
        return (bucket_idx, len(bucket) - 1)

    def __str__(self):
        lines = ["=== Symbol Table (Hash Table) ==="]
        for i, bucket in enumerate(self.table):
            if bucket:
                lines.append(f"Bucket {i:3d}: {bucket}")
        return "\n".join(lines)


class FiniteAutomata:
    def __init__(self):
        self.Q = []
        self.sigma = []
        self.q0 = ""
        self.F = []
        self.delta = {}

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
            if sym == "[STR_CHARS]":
                return [c for c in string.printable if c not in ('"', '\n', '\r')]

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

                for actual_char in expand_symbol(symbol_macro):
                    if (state, actual_char) not in self.delta:
                        self.delta[(state, actual_char)] = []
                    if next_state not in self.delta[(state, actual_char)]:
                        self.delta[(state, actual_char)].append(next_state)

    def accepts(self, word):
        """Simulates the deterministic FA over the input word."""
        if not word:
            return False
        current_state = self.q0
        for char in word:
            if (current_state, char) in self.delta:
                current_state = self.delta[(current_state, char)][0]
            else:
                return False
        return current_state in self.F


class Scanner:
    def __init__(self, token_file, fa_id_file, fa_const_file, fa_string_file):
        self.st = SymbolTable()
        self.pif = []
        self.errors = []

        # Load the Finite Automata
        self.fa_id = FiniteAutomata()
        self.fa_id.load_from_file(fa_id_file)

        self.fa_const = FiniteAutomata()
        self.fa_const.load_from_file(fa_const_file)

        self.fa_string = FiniteAutomata()
        self.fa_string.load_from_file(fa_string_file)

        self.reserved_tokens = set()
        self.multi_char_ops = ["==", "!=", "<=", ">="]

        self.single_char_delims = set("=+-*/%<>(){}[];,")
        self._load_tokens(token_file)

    def _load_tokens(self, token_file):
        with open(token_file, 'r') as f:
            for line in f:
                t = line.strip()
                if t:
                    self.reserved_tokens.add(t)

    def tokenize_line(self, line):
        """Splits a line into raw candidate tokens using operators/separators as boundaries."""

        ops_pattern = "|".join(re.escape(op) for op in self.multi_char_ops)
        delims_pattern = "|".join(re.escape(d) for d in self.single_char_delims)

        pattern = f'("[^"]*")|({ops_pattern}|{delims_pattern}|\\s+)'
        raw_parts = re.split(pattern, line)
        return [part for part in raw_parts if part and not part.isspace()]

    def scan(self, source_file):
        with open(source_file, 'r') as f:
            lines = f.readlines()

        for line_num, line in enumerate(lines, start=1):
            line_clean = line.split("//")[0]
            tokens = self.tokenize_line(line_clean)

            for token in tokens:
                if token in self.reserved_tokens or token in self.multi_char_ops or token in self.single_char_delims:
                    self.pif.append((token, (-1, -1)))

                elif self.fa_id.accepts(token):
                    pos = self.st.add(token)
                    self.pif.append(("id", pos))

                elif self.fa_const.accepts(token):
                    pos = self.st.add(token)
                    self.pif.append(("const", pos))

                elif self.fa_string.accepts(token):
                    pos = self.st.add(token)
                    self.pif.append(("str_const", pos))

                else:
                    self.errors.append(f"Lexical error at line {line_num}: unrecognized token '{token}'")

    def write_outputs(self, pif_file="PIF.out", st_file="ST.out"):
        with open(pif_file, 'w') as f:
            f.write("=== Program Internal Form (PIF) ===\n")
            f.write(f"{'Token':<15} | {'ST_Pos (Bucket, Index)'}\n")
            f.write("-" * 40 + "\n")
            for token_type, pos in self.pif:
                f.write(f"{token_type:<15} | {pos}\n")

        with open(st_file, 'w') as f:
            f.write(str(self.st) + "\n")

        print(str(self.st))
        print("\n=== Program Internal Form (PIF) ===")
        for token_type, pos in self.pif:
            print(f"{token_type:<12} | {pos}")

        print("\n=== Scan Report ===")
        if not self.errors:
            print("Lexically correct!")
        else:
            for err in self.errors:
                print(err)


if __name__ == "__main__":
    scanner = Scanner(
        token_file="tokens.in",
        fa_id_file="fa_identifier.in",
        fa_const_file="fa_constant.in",
        fa_string_file="fa_string_constant.in"
    )
    scanner.scan("program2.ss")
    scanner.write_outputs()
