
import re
import sys
import json
import socket

class SOARESSyntaxError(Exception):
    pass

# Hardcoded configuration
LANGUAGE_NAME = "SOARES"
FILE_EXTENSION = ".soares"
COMMAND_PREFIX = "SOARES"
COMMENT_PREFIX = "SOARESAY"
ENFORCE_UPPERCASE_COMMENTS = True
ENFORCE_UPPERCASE_CODE = True
TYPE_PREFIX_INTEGER = "SOARESNUM"
TYPE_PREFIX_FLOAT = "SOARESFLOAT"
TYPE_PREFIX_STRING = "SOARESSTRING"
TRUE_VALUE = "YEEE"
FALSE_VALUE = "NAWWW"
BLOCK_END = "SOARESDONE"

# Lexer
def lexer(code):
    tokens = []
    lines = code.split('\n')
    for line_number, line in enumerate(lines, 1):
        if COMMENT_PREFIX in line:
            comment_start = line.index(COMMENT_PREFIX)
            if ENFORCE_UPPERCASE_COMMENTS and any(c.islower() for c in line[comment_start:]):
                raise SOARESSyntaxError(f"Syntax Error on line {line_number}: Comments must be in all caps")
            line = line[:comment_start].strip()
        if not line:
            continue
        line_tokens = []
        current = ''
        in_string = False
        for char in line:
            if char == '"' and not in_string:
                if current:
                    line_tokens.append(current)
                    current = ''
                in_string = True
                current += char
            elif char == '"' and in_string:
                current += char
                line_tokens.append(current)
                current = ''
                in_string = False
            elif in_string:
                current += char
            elif char.isspace():
                if current:
                    line_tokens.append(current)
                    current = ''
            elif char in '+-*/()=:,':
                if current:
                    line_tokens.append(current)
                    current = ''
                line_tokens.append(char)
            else:
                current += char
        if current:
            line_tokens.append(current)
        tokens.extend(line_tokens)
    return tokens

# Parser
class AST:
    pass

class Number(AST):
    def __init__(self, value):
        self.value = value

class String(AST):
    def __init__(self, value):
        self.value = value

class BooleanLiteral(AST):
    def __init__(self, value):
        self.value = value

class BinOp(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class Variable(AST):
    def __init__(self, name):
        self.name = name

class Assignment(AST):
    def __init__(self, name, value):
        self.name = name
        self.value = value

class FunctionCall(AST):
    def __init__(self, name, args):
        self.name = name
        self.args = args

class IfStatement(AST):
    def __init__(self, condition, if_body, else_body=None):
        self.condition = condition
        self.if_body = if_body
        self.else_body = else_body

class WhileLoop(AST):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

def parse(tokens):
    def parse_expression():
        result = parse_term()
        while tokens and tokens[0] in '+-':
            op = tokens.pop(0)
            right = parse_term()
            result = BinOp(result, op, right)
        return result

    def parse_term():
        result = parse_factor()
        while tokens and tokens[0] in '*/':
            op = tokens.pop(0)
            right = parse_factor()
            result = BinOp(result, op, right)
        return result

    def parse_factor():
        if not tokens:
            raise SOARESSyntaxError("Unexpected end of input")
        if tokens[0] == '(':
            tokens.pop(0)  # Remove '('
            result = parse_expression()
            if not tokens or tokens.pop(0) != ')':
                raise SOARESSyntaxError("Expected closing parenthesis")
            return result
        elif tokens[0].startswith(COMMAND_PREFIX) or tokens[0] in [TYPE_PREFIX_INTEGER, TYPE_PREFIX_FLOAT, TYPE_PREFIX_STRING]:
            return parse_command()
        elif tokens[0] in [TRUE_VALUE, FALSE_VALUE]:
            return BooleanLiteral(tokens.pop(0) == TRUE_VALUE)
        elif tokens[0].startswith('"') and tokens[0].endswith('"'):
            return String(tokens.pop(0)[1:-1])  # Remove quotes
        elif re.match(r'^[A-Za-z0-9_]+$', tokens[0]):
            return parse_variable_or_function()
        else:
            try:
                token = tokens.pop(0)
                return Number(float(token))
            except ValueError:
                raise SOARESSyntaxError(f"Unexpected token: {token}")

    def parse_function_call(name):
        args = []
        if tokens and tokens[0] == '(':
            tokens.pop(0)  # Remove '('
            while tokens and tokens[0] != ')':
                args.append(parse_expression())
                if tokens and tokens[0] == ',':
                    tokens.pop(0)
            if not tokens or tokens.pop(0) != ')':
                raise SOARESSyntaxError(f"Expected closing parenthesis in function call to {name}")
        return FunctionCall(name, args)

    def parse_command():
        token = tokens.pop(0)
        if token in [TYPE_PREFIX_INTEGER, TYPE_PREFIX_FLOAT, TYPE_PREFIX_STRING]:
            if not tokens:
                raise SOARESSyntaxError(f"Expected value after {token}")
            value = tokens.pop(0)
            if token == TYPE_PREFIX_INTEGER:
                return Number(int(value))
            elif token == TYPE_PREFIX_FLOAT:
                return Number(float(value))
            else:  # TYPE_PREFIX_STRING
                return String(value.strip('"'))
        elif token.startswith(COMMAND_PREFIX):
            return parse_function_call(token)
        else:
            raise SOARESSyntaxError(f"Unknown command: {token}")

    def parse_variable_or_function():
        name = tokens.pop(0)
        if tokens and tokens[0] == '(':
            return parse_function_call(name)
        return Variable(name)

    def parse_if_statement():
        tokens.pop(0)  # Remove IF
        condition = parse_expression()
        if not tokens or tokens.pop(0) != ':':
            raise SOARESSyntaxError("Expected ':' after if condition")
        if_body = []
        while tokens and tokens[0] != f"{COMMAND_PREFIX}ELSE" and tokens[0] != BLOCK_END:
            if_body.append(parse_statement())
        else_body = None
        if tokens and tokens[0] == f"{COMMAND_PREFIX}ELSE":
            tokens.pop(0)  # Remove ELSE
            if not tokens or tokens.pop(0) != ':':
                raise SOARESSyntaxError("Expected ':' after else")
            else_body = []
            while tokens and tokens[0] != BLOCK_END:
                else_body.append(parse_statement())
        if not tokens or tokens.pop(0) != BLOCK_END:
            raise SOARESSyntaxError(f"Expected '{BLOCK_END}' at the end of if statement")
        return IfStatement(condition, if_body, else_body)

    def parse_while_loop():
        tokens.pop(0)  # Remove WHILE
        condition = parse_expression()
        if not tokens or tokens.pop(0) != ':':
            raise SOARESSyntaxError("Expected ':' after while condition")
        body = []
        while tokens and tokens[0] != BLOCK_END:
            body.append(parse_statement())
        if not tokens or tokens.pop(0) != BLOCK_END:
            raise SOARESSyntaxError(f"Expected '{BLOCK_END}' at the end of while loop")
        return WhileLoop(condition, body)

    def parse_statement():
        if not tokens:
            raise SOARESSyntaxError("Unexpected end of input")
        if len(tokens) >= 3 and tokens[1] == '=':
            name = tokens.pop(0)
            tokens.pop(0)  # Remove '='
            value = parse_expression()
            return Assignment(name, value)
        elif tokens[0].startswith(COMMAND_PREFIX):
            if tokens[0] == f"{COMMAND_PREFIX}IF":
                return parse_if_statement()
            elif tokens[0] == f"{COMMAND_PREFIX}WHILE":
                return parse_while_loop()
            else:
                return parse_command()
        else:
            return parse_expression()

    statements = []
    while tokens:
        statements.append(parse_statement())
    return statements

# Interpreter
class Interpreter:
    def __init__(self):
        self.variables = {}
        self.sockets = {}

    def visit(self, node):
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name)
        return method(node)

    def visit_Number(self, node):
        return node.value

    def visit_String(self, node):
        return node.value

    def visit_BooleanLiteral(self, node):
        return node.value

    def visit_BinOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        if node.op == '+':
            return left + right
        elif node.op == '-':
            return left - right
        elif node.op == '*':
            return left * right
        elif node.op == '/':
            return left / right

    def visit_Variable(self, node):
        if node.name not in self.variables:
            raise NameError(f"Variable '{node.name}' is not defined")
        return self.variables[node.name]

    def visit_Assignment(self, node):
        value = self.visit(node.value)
        self.variables[node.name] = value
        return value

    def visit_FunctionCall(self, node):
        if node.name == f'{COMMAND_PREFIX}PRINT':
            args = [str(self.visit(arg)) for arg in node.args]
            print(*args)
        elif node.name == f'{COMMAND_PREFIX}SHOUT':
            if len(node.args) != 1:
                raise ValueError(f"{COMMAND_PREFIX}SHOUT function expects exactly one argument")
            arg = self.visit(node.args[0])
            return str(arg).upper()
        elif node.name == f'{COMMAND_PREFIX}SOCKET':
            socket_name = self.visit(node.args[0])
            self.sockets[socket_name] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            return socket_name
        elif node.name == f'{COMMAND_PREFIX}BIND':
            socket_name = self.visit(node.args[0])
            port = self.visit(node.args[1])
            self.sockets[socket_name].bind(('', port))
        elif node.name == f'{COMMAND_PREFIX}LISTEN':
            socket_name = self.visit(node.args[0])
            backlog = self.visit(node.args[1])
            self.sockets[socket_name].listen(backlog)
        elif node.name == f'{COMMAND_PREFIX}ACCEPT':
            socket_name = self.visit(node.args[0])
            conn, _ = self.sockets[socket_name].accept()
            return conn
        elif node.name == f'{COMMAND_PREFIX}SEND':
            conn = self.visit(node.args[0])
            data = str(self.visit(node.args[1])).encode()
            conn.send(data)
        else:
            raise ValueError(f"Unknown function: {node.name}")

    def visit_IfStatement(self, node):
        if self.visit(node.condition):
            for statement in node.if_body:
                self.visit(statement)
        elif node.else_body:
            for statement in node.else_body:
                self.visit(statement)

    def visit_WhileLoop(self, node):
        while self.visit(node.condition):
            for statement in node.body:
                self.visit(statement)

def run(code):
    if ENFORCE_UPPERCASE_CODE:
        code = code.upper()
    try:
        tokens = lexer(code)
        ast = parse(tokens)
        interpreter = Interpreter()
        for statement in ast:
            interpreter.visit(statement)
    except SOARESSyntaxError as e:
        print(f"{COMMAND_PREFIX}PY ERROR: {str(e).upper()}")
        sys.exit(1)

def run_file(filename):
    if not filename.endswith(FILE_EXTENSION):
        raise ValueError(f"Only {FILE_EXTENSION} files can be run")
    with open(filename, 'r') as file:
        code = file.read()
    return run(code)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: python {LANGUAGE_NAME.lower()}.py <filename{FILE_EXTENSION}>")
        sys.exit(1)
    
    try:
        run_file(sys.argv[1])
    except Exception as e:
        print(f"ERROR: {str(e).upper()}")
        sys.exit(1)
