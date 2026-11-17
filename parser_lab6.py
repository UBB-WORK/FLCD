import string
import re
import ply.lex as lex
import ply.yacc as yacc

# ==========================================
# 1. SYMBOL TABLE & FINITE AUTOMATA
# ==========================================


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
        if not word:
            return False
        current_state = self.q0
        for char in word:
            if (current_state, char) in self.delta:
                current_state = self.delta[(current_state, char)][0]
            else:
                return False
        return current_state in self.F


# ==========================================
# 2. TOKEN DEFINITIONS FOR LEX & YACC
# ==========================================

RESERVED_MAP = {
    'sensor_node': 'SENSOR_NODE',
    'signal': 'SIGNAL',
    'buffer': 'BUFFER',
    'detect': 'DETECT',
    'otherwise': 'OTHERWISE',
    'monitor': 'MONITOR',
    'sample': 'SAMPLE',
    'emit': 'EMIT',
}

SYMBOL_TOKEN_MAP = {
    '+': 'PLUS',
    '-': 'MINUS',
    '*': 'TIMES',
    '/': 'DIVIDE',
    '%': 'MOD',
    '=': 'ASSIGN',
    '==': 'EQ',
    '!=': 'NEQ',
    '<': 'LT',
    '<=': 'LE',
    '>': 'GT',
    '>=': 'GE',
    ';': 'SEMI',
    ',': 'COMMA',
    '(': 'LPAREN',
    ')': 'RPAREN',
    '{': 'LBRACE',
    '}': 'RBRACE',
    '[': 'LBRACKET',
    ']': 'RBRACKET',
    'id': 'ID',
    'int_const': 'INT_CONST',
    'str_const': 'STR_CONST',
    'const': 'INT_CONST'
}

tokens = list(RESERVED_MAP.values()) + [
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MOD',
    'ASSIGN', 'EQ', 'NEQ', 'LT', 'LE', 'GT', 'GE',
    'SEMI', 'COMMA', 'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE', 'LBRACKET', 'RBRACKET',
    'ID', 'INT_CONST', 'STR_CONST'
]


# ==========================================
# 3. PIF LEXER (Reads PIF.out)
# ==========================================

class PIFToken:
    def __init__(self, type_, value, lineno):
        self.type = type_
        self.value = value
        self.lineno = lineno
        self.lexpos = 0


class PIFLexer:
    """Feeds tokens directly from Lab 5's PIF.out into Yacc."""

    def __init__(self, pif_filename="PIF.out"):
        self.token_stream = []
        self.index = 0
        self._load_pif(pif_filename)

    def _load_pif(self, filename):
        with open(filename, 'r') as f:
            lines = f.readlines()

        line_num = 1
        for line in lines:
            line = line.strip()
            if not line or line.startswith("===") or line.startswith("Token") or line.startswith("---"):
                continue
            if "|" in line:
                raw_token = line.split("|")[0].strip()
                if raw_token in RESERVED_MAP:
                    tok_type = RESERVED_MAP[raw_token]
                elif raw_token in SYMBOL_TOKEN_MAP:
                    tok_type = SYMBOL_TOKEN_MAP[raw_token]
                else:
                    raise ValueError(f"Unknown token in PIF: '{raw_token}'")
                self.token_stream.append(PIFToken(tok_type, raw_token, line_num))
                line_num += 1

    def token(self):
        if self.index < len(self.token_stream):
            tok = self.token_stream[self.index]
            self.index += 1
            return tok
        return None


# ==========================================
# 4. INTEGRATED LEX + FA SCANNER
# ==========================================

class IntegratedFALexer:
    """Integrates PLY Lex with Finite Automata, Symbol Table, and PIF generation."""
    tokens = tokens

    t_EQ = r'=='
    t_NEQ = r'!='
    t_LE = r'<='
    t_GE = r'>='
    t_ASSIGN = r'='
    t_LT = r'<'
    t_GT = r'>'
    t_PLUS = r'\+'
    t_MINUS = r'-'
    t_TIMES = r'\*'
    t_DIVIDE = r'/'
    t_MOD = r'%'
    t_SEMI = r';'
    t_COMMA = r','
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_LBRACE = r'\{'
    t_RBRACE = r'\}'
    t_LBRACKET = r'\['
    t_RBRACKET = r'\]'

    t_ignore = ' \t\r'

    def __init__(self, fa_id_file="fa_identifier.in", fa_const_file="fa_constant.in", fa_string_file="fa_string_constant.in"):
        self.st = SymbolTable()
        self.pif = []
        self.lexical_errors = []

        self.fa_id = FiniteAutomata()
        self.fa_id.load_from_file(fa_id_file)

        self.fa_const = FiniteAutomata()
        self.fa_const.load_from_file(fa_const_file)

        self.fa_string = FiniteAutomata()
        self.fa_string.load_from_file(fa_string_file)

        self.lexer = lex.lex(module=self)

    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    def t_STRING_CANDIDATE(self, t):
        r'"[^"\n]*"'
        if self.fa_string.accepts(t.value):
            t.type = 'STR_CONST'
            pos = self.st.add(t.value)
            self.pif.append(("str_const", pos))
            return t
        else:
            self.lexical_errors.append(f"Lexical error at line {t.lexer.lineno}: invalid string '{t.value}'")
            t.lexer.skip(1)

    def t_WORD_CANDIDATE(self, t):
        r'[a-zA-Z0-9_]+'
        if t.value in RESERVED_MAP:
            t.type = RESERVED_MAP[t.value]
            self.pif.append((t.value, (-1, -1)))
            return t
        elif self.fa_id.accepts(t.value):
            t.type = 'ID'
            pos = self.st.add(t.value)
            self.pif.append(("id", pos))
            return t
        elif self.fa_const.accepts(t.value):
            t.type = 'INT_CONST'
            pos = self.st.add(t.value)
            self.pif.append(("int_const", pos))
            return t
        else:
            self.lexical_errors.append(
                f"Lexical error at line {t.lexer.lineno}: FA rejected token '{t.value}'"
            )

    def t_error(self, t):
        self.lexical_errors.append(
            f"Lexical error at line {t.lexer.lineno}: illegal character '{t.value[0]}'"
        )
        t.lexer.skip(1)

    def input(self, data):
        self.pif.clear()
        self.lexical_errors.clear()
        self.lexer.lineno = 1
        self.lexer.input(data)

    def token(self):
        tok = self.lexer.token()
        if tok and tok.type not in ('ID', 'INT_CONST', 'STR_CONST') and tok.value not in RESERVED_MAP:
            self.pif.append((tok.value, (-1, -1)))
        return tok


# ==========================================
# 5. YACC PARSER & BNF PRODUCTION RULES
# ==========================================

productions_used = []
syntax_errors = []


def record_prod(num, rule_str):
    productions_used.append((num, rule_str))


def p_program(p):
    '''program : SENSOR_NODE ID LBRACE stmt_list RBRACE
               | stmt_list'''
    if len(p) == 6:
        record_prod(1, "program -> sensor_node id { stmt_list }")
    else:
        record_prod(2, "program -> stmt_list")


def p_stmt_list(p):
    '''stmt_list : stmt
                 | stmt_list stmt'''
    if len(p) == 2:
        record_prod(3, "stmt_list -> stmt")
    else:
        record_prod(4, "stmt_list -> stmt_list stmt")


# Clean explicit dispatcher for unambiguous production recording:


def p_stmt_declaration(p):
    'stmt : declaration'
    record_prod(5, "stmt -> declaration")


def p_stmt_assign(p):
    'stmt : assign_stmt'
    record_prod(6, "stmt -> assign_stmt")


def p_stmt_io(p):
    'stmt : io_stmt'
    record_prod(7, "stmt -> io_stmt")


def p_stmt_if(p):
    'stmt : if_stmt'
    record_prod(8, "stmt -> if_stmt")


def p_stmt_while(p):
    'stmt : while_stmt'
    record_prod(9, "stmt -> while_stmt")

# Declarations


def p_declaration(p):
    '''declaration : SIGNAL id_list SEMI
                   | SIGNAL ID ASSIGN expression SEMI
                   | SENSOR_NODE ID SEMI
                   | BUFFER ID LBRACKET INT_CONST RBRACKET SEMI
                   | BUFFER ID ASSIGN STR_CONST SEMI'''
    if len(p) == 4 and p[1] == 'signal':
        record_prod(10, "declaration -> signal id_list ;")
    elif len(p) == 6 and p[1] == 'signal':
        record_prod(11, "declaration -> signal id = expression ;")
    elif len(p) == 4:
        record_prod(12, "declaration -> sensor_node id ;")
    elif len(p) == 7:
        record_prod(13, "declaration -> buffer id [ int_const ] ;")
    elif len(p) == 6:
        record_prod(14, "declaration -> buffer id = str_const ;")


def p_id_list(p):
    '''id_list : ID
               | id_list COMMA ID'''
    if len(p) == 2:
        record_prod(15, "id_list -> id")
    else:
        record_prod(16, "id_list -> id_list , id")

# Assignments & I/O


def p_assign_stmt(p):
    '''assign_stmt : ID ASSIGN expression SEMI
                   | ID LBRACKET expression RBRACKET ASSIGN expression SEMI'''
    if len(p) == 5:
        record_prod(17, "assign_stmt -> id = expression ;")
    else:
        record_prod(18, "assign_stmt -> id [ expression ] = expression ;")


def p_io_stmt(p):
    '''io_stmt : SAMPLE LPAREN ID RPAREN SEMI
               | SAMPLE ID SEMI
               | EMIT expression SEMI'''
    if len(p) == 6:
        record_prod(19, "io_stmt -> sample ( id ) ;")
    elif len(p) == 4 and p[1] == 'sample':
        record_prod(20, "io_stmt -> sample id ;")
    else:
        record_prod(21, "io_stmt -> emit expression ;")

# Control Flow


def p_if_stmt(p):
    '''if_stmt : DETECT LPAREN condition RPAREN LBRACE stmt_list RBRACE
               | DETECT LPAREN condition RPAREN LBRACE stmt_list RBRACE OTHERWISE LBRACE stmt_list RBRACE'''
    if len(p) == 8:
        record_prod(22, "if_stmt -> detect ( condition ) { stmt_list }")
    else:
        record_prod(23, "if_stmt -> detect ( condition ) { stmt_list } otherwise { stmt_list }")


def p_while_stmt(p):
    'while_stmt : MONITOR LPAREN condition RPAREN LBRACE stmt_list RBRACE'
    record_prod(24, "while_stmt -> monitor ( condition ) { stmt_list }")

# Conditions


def p_condition(p):
    'condition : expression rel_op expression'
    record_prod(25, "condition -> expression rel_op expression")


def p_rel_op(p):
    '''rel_op : EQ
              | NEQ
              | LT
              | LE
              | GT
              | GE'''
    op_map = {'==': 26, '!=': 27, '<': 28, '<=': 29, '>': 30, '>=': 31}
    str_map = {'==': "==", '!=': "!=", '<': "<", '<=': "<=", '>': ">", '>=': ">="}
    val = p[1]
    record_prod(op_map[val], f"rel_op -> {str_map[val]}")

# Expressions


def p_expression(p):
    '''expression : term
                  | expression PLUS term
                  | expression MINUS term'''
    if len(p) == 2:
        record_prod(32, "expression -> term")
    elif p[2] == '+':
        record_prod(33, "expression -> expression + term")
    else:
        record_prod(34, "expression -> expression - term")


def p_term(p):
    '''term : factor
            | term TIMES factor
            | term DIVIDE factor
            | term MOD factor'''
    if len(p) == 2:
        record_prod(35, "term -> factor")
    elif p[2] == '*':
        record_prod(36, "term -> term * factor")
    elif p[2] == '/':
        record_prod(37, "term -> term / factor")
    else:
        record_prod(38, "term -> term % factor")


def p_factor(p):
    '''factor : ID
              | ID LBRACKET expression RBRACKET
              | INT_CONST
              | STR_CONST
              | LPAREN expression RPAREN'''
    if len(p) == 2:
        if str(p[1]).startswith('"'):
            record_prod(42, "factor -> str_const")
        elif p.slice[1].type == 'INT_CONST':
            record_prod(41, "factor -> int_const")
        else:
            record_prod(39, "factor -> id")
    elif len(p) == 5:
        record_prod(40, "factor -> id [ expression ]")
    else:
        record_prod(43, "factor -> ( expression )")


def p_error(p):
    if p:
        syntax_errors.append(f"Syntax error at token '{p.value}' (type {p.type}) on line {p.lineno}")
    else:
        syntax_errors.append("Syntax error at EOF (unexpected end of input)")


parser = yacc.yacc(write_tables=False, debug=False)


# ==========================================
# 6. OUTPUT FORMATTING & EXECUTION DRIVER
# ==========================================

def display_parse_results(mode_title):
    print(f"\n==================== {mode_title} ====================")
    if syntax_errors:
        print("STATUS: SYNTAX ERRORS DETECTED")
        for err in syntax_errors:
            print("  ->", err)
        return

    print("STATUS: Syntactically Correct!\n")

    prod_numbers = " ".join(f"({num})" for num, _ in productions_used)
    print(f"String of Productions (Reduction Order):\n  {prod_numbers}\n")

    print("Detailed Production Steps:")
    for step, (num, rule) in enumerate(productions_used, start=1):
        print(f"  {step:2d}. ({num:2d}) {rule}")
    print("=" * (42 + len(mode_title)) + "\n")


def run_requirement_2(pif_file="PIF.out"):
    productions_used.clear()
    syntax_errors.clear()
    try:
        pif_lexer = PIFLexer(pif_file)
        parser.parse(lexer=pif_lexer)
        display_parse_results("REQUIREMENT 2: PARSING FROM PIF.out")
    except FileNotFoundError:
        print(f"Error: '{pif_file}' not found. Run Lab 5 scanner first to generate PIF.out.")


def run_requirement_3(source_file="program.ss"):
    productions_used.clear()
    syntax_errors.clear()
    integrated_lexer = IntegratedFALexer()

    try:
        with open(source_file, 'r') as f:
            source_code = f.read()
    except FileNotFoundError:
        print(f"Error: '{source_file}' not found.")
        return

    integrated_lexer.input(source_code)
    parser.parse(lexer=integrated_lexer)

    if integrated_lexer.lexical_errors:
        print("\n=== LEXICAL ERRORS DETECTED BY FA ===")
        for err in integrated_lexer.lexical_errors:
            print("  ->", err)
    else:
        display_parse_results(f"REQUIREMENT 3: INTEGRATED LEX (FA) + YACC ({source_file})")


if __name__ == "__main__":
    while True:
        print("\n--- Lab 6: Syntactical Analysis Menu ---")
        print("1. Parse from existing PIF.out")
        print("2. Integrated Scan (FA + Lex) & Parse (Yacc) on program.ss")
        print("0. Exit")
        choice = input("Select option: ").strip()

        if choice == '1':
            run_requirement_2("PIF.out")
        elif choice == '2':
            run_requirement_3("program1.ss")
        elif choice == '0':
            break
        else:
            print("Invalid option.\n")
