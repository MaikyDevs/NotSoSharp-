#!/usr/bin/env python3
import re, sys

def error(msg, line=None):
    if line is not None:
        print(f"Fehler in Zeile {line}: {msg}")
    else:
        print(f"Fehler: {msg}")
    sys.exit(1)

if len(sys.argv) < 2:
    error("Usage: nscharp <file.ns>")

if sys.argv[1] in ('-h', '--help'):
    print("Nscharp Interpreter\nUsage: nscharp <filename.ns>\nRuns Nscharp code files.")
    sys.exit(0)

TOKEN_SPEC = [
    ('NUMBER', r'\d+'),
    ('STRING', r'"[^"]*"'),
    ('LET', r'let'),
    ('FUN', r'fun'),
    ('PRINT', r'print'),
    ('IF', r'if'),
    ('ELSE', r'else'),
    ('WHILE', r'while'),
    ('LBRACE', r'\{'),
    ('RBRACE', r'\}'),
    ('LPAREN', r'\('),
    ('RPAREN', r'\)'),
    ('EQEQ', r'=='),
    ('EQ', r'='),
    ('OP', r'[+\-*/><]+'),
    ('IDENT', r'[a-zA-Z_]\w*'),
    ('NEWLINE', r'\n'),
    ('SKIP', r'[ \t]+'),
]

class Token:
    def __init__(self, kind, value, line):
        self.kind = kind
        self.value = value
        self.line = line
    def __repr__(self):
        return f"Token({self.kind}, {self.value}, line={self.line})"

def lexer(code):
    tokens = []
    regex = '|'.join('(?P<%s>%s)' % pair for pair in TOKEN_SPEC)
    line_num = 1
    pos = 0
    while pos < len(code):
        m = re.match(regex, code[pos:])
        if not m:
            error(f"Unbekanntes Zeichen: {code[pos]!r}", line_num)
        kind = m.lastgroup
        value = m.group()
        if kind == 'NEWLINE':
            line_num += 1
            pos += len(value)
            continue
        if kind == 'SKIP':
            pos += len(value)
            continue
        if kind == 'NUMBER':
            value = int(value)
        if kind == 'STRING':
            value = value.strip('"')
        tokens.append(Token(kind, value, line_num))
        pos += len(m.group())
    tokens.append(Token('EOF', None, line_num))
    return tokens

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        if self.pos >= len(self.tokens):
            return Token('EOF', None, self.tokens[-1].line)
        return self.tokens[self.pos]

    def eat(self, kind):
        tok = self.peek()
        if tok.kind == kind:
            self.pos += 1
            return tok
        error(f"Erwartet {kind}, aber bekommen {tok.kind}", tok.line)

    def parse(self):
        stmts = []
        while self.peek().kind != 'EOF':
            stmts.append(self.statement())
        return stmts

    def statement(self):
        kind = self.peek().kind
        if kind == 'LET': return self.parse_let()
        if kind == 'PRINT': return self.parse_print()
        if kind == 'FUN': return self.parse_fun()
        if kind == 'IF': return self.parse_if()
        if kind == 'ELSE': return self.parse_else()
        if kind == 'WHILE': return self.parse_while()
        return self.parse_expression_statement()

    def parse_let(self):
        self.eat('LET')
        name_tok = self.eat('IDENT')
        self.eat('EQ')
        expr = self.expression()
        return ('LET', name_tok.value, expr, name_tok.line)

    def parse_print(self):
        self.eat('PRINT')
        self.eat('LPAREN')
        expr = self.expression()
        self.eat('RPAREN')
        return ('PRINT', expr, self.peek().line)

    def parse_fun(self):
        self.eat('FUN')
        name_tok = self.eat('IDENT')
        self.eat('LPAREN')
        self.eat('RPAREN')
        self.eat('LBRACE')
        body = []
        while self.peek().kind != 'RBRACE':
            body.append(self.statement())
        self.eat('RBRACE')
        return ('FUN', name_tok.value, body, name_tok.line)

    def parse_if(self):
        if_tok = self.eat('IF')
        cond_tokens = []
        while self.peek().kind not in ('LBRACE',):
            cond_tokens.append(self.peek())
            self.pos += 1
        self.eat('LBRACE')
        body = []
        while self.peek().kind != 'RBRACE':
            body.append(self.statement())
        self.eat('RBRACE')
        # Check if next token is else
        if self.peek().kind == 'ELSE':
            else_stmt = self.parse_else()
            return ('IFELSE', ('EXPR', cond_tokens), body, else_stmt[1], if_tok.line)
        return ('IF', ('EXPR', cond_tokens), body, if_tok.line)

    def parse_else(self):
        self.eat('ELSE')
        self.eat('LBRACE')
        body = []
        while self.peek().kind != 'RBRACE':
            body.append(self.statement())
        self.eat('RBRACE')
        return ('ELSE', body)

    def parse_while(self):
        while_tok = self.eat('WHILE')
        cond_tokens = []
        while self.peek().kind != 'LBRACE':
            cond_tokens.append(self.peek())
            self.pos += 1
        self.eat('LBRACE')
        body = []
        while self.peek().kind != 'RBRACE':
            body.append(self.statement())
        self.eat('RBRACE')
        return ('WHILE', ('EXPR', cond_tokens), body, while_tok.line)

    def parse_expression_statement(self):
        expr = self.expression()
        return ('EXPR_STMT', expr, self.peek().line)

    def expression(self):
        parts = []
        # Erlaubt auch EQEQ (==)
        while self.peek().kind in ['OP','IDENT','NUMBER','STRING','EQEQ']:
            parts.append(self.peek())
            self.pos += 1
        if not parts:
            error("Erwarteter Ausdruck, aber nichts gefunden", self.peek().line)
        return ('EXPR', parts)

class Interpreter:
    def __init__(self, stmts):
        self.stmts = stmts
        self.env = {}
        self.funcs = {}

    def eval_expr(self, expr):
        # Direkte input()-Verarbeitung wenn alleinstehend
        if len(expr[1]) == 1 and expr[1][0].kind == 'IDENT' and expr[1][0].value == 'input':
            return input()

        text = ""
        for t in expr[1]:
            if t.kind == 'NUMBER':
                text += str(t.value)
            elif t.kind == 'STRING':
                text += repr(t.value)  # Strings mit Anführungszeichen
            elif t.kind == 'IDENT':
                if t.value not in self.env:
                    error(f"Variable '{t.value}' ist nicht definiert", t.line)
                text += str(self.env[t.value])
            elif t.kind == 'EQEQ':
                text += "=="
            elif t.kind == 'OP':
                text += t.value
            else:
                error(f"Nicht unterstütztes Token im Ausdruck: {t.kind}", t.line)
        try:
            return eval(text)
        except Exception as e:
            error(f"Fehler bei Auswertung: {e}", expr[1][0].line)

    def run(self):
        for stmt in self.stmts:
            self.exec(stmt)

    def exec(self, stmt):
        t = stmt[0]
        line = stmt[-1] if len(stmt) > 2 else None
        try:
            if t == 'LET':
                self.env[stmt[1]] = self.eval_expr(stmt[2])
            elif t == 'PRINT':
                print(self.eval_expr(stmt[1]))
            elif t == 'FUN':
                self.funcs[stmt[1]] = stmt[2]
            elif t == 'IF':
                if self.eval_expr(stmt[1]):
                    for s in stmt[2]:
                        self.exec(s)
            elif t == 'IFELSE':
                if self.eval_expr(stmt[1]):
                    for s in stmt[2]:
                        self.exec(s)
                else:
                    for s in stmt[3]:
                        self.exec(s)
            elif t == 'ELSE':
                for s in stmt[1]:
                    self.exec(s)
            elif t == 'WHILE':
                while self.eval_expr(stmt[1]):
                    for s in stmt[2]:
                        self.exec(s)
            elif t == 'EXPR_STMT':
                self.eval_expr(stmt[1])
            else:
                error(f"Unbekannter Statement-Typ: {t}", line)
        except Exception as e:
            error(f"Laufzeitfehler: {e}", line)

try:
    with open(sys.argv[1]) as f:
        code = f.read()
except FileNotFoundError:
    error(f"Datei {sys.argv[1]} nicht gefunden.")

tokens = lexer(code)
parser = Parser(tokens)

try:
    statements = parser.parse()
except SyntaxError as e:
    error(str(e), parser.peek().line)

interpreter = Interpreter(statements)

try:
    interpreter.run()
except Exception as e:
    error(str(e))
