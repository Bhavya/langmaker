import json
import os
import stat
import sys

def generate_language(config_file):
    print(f"Loading configuration from {config_file}")
    # Load configuration
    with open(config_file, 'r') as f:
        config = json.load(f)

    lang_name = config['language_name']
    file_extension = config['file_extension']
    command_name = config['command_name']

    print(f"Generating {lang_name} language")

    # Create main languages directory if it doesn't exist
    langs_dir = 'langs'
    os.makedirs(langs_dir, exist_ok=True)
    print(f"Created/confirmed 'langs' directory")

    # Create language-specific directory
    lang_dir = os.path.join(langs_dir, lang_name.lower())
    os.makedirs(lang_dir, exist_ok=True)
    print(f"Created/confirmed '{lang_name}' directory")

    # Create lib directory
    lib_dir = os.path.join(lang_dir, 'lib')
    os.makedirs(lib_dir, exist_ok=True)
    print(f"Created/confirmed 'lib' directory")

    # Generate interpreter
    print("Generating interpreter...")
    generate_interpreter(lib_dir, config)
    print("Interpreter generated successfully")

    # Generate README
    print("Generating README...")
    generate_readme(lang_dir, config)
    print("README generated successfully")

    # Generate example programs
    print("Generating example programs...")
    generate_examples(lang_dir, config)
    print("Example programs generated successfully")

    # Generate shell script
    print("Generating shell script...")
    generate_shell_script(lang_dir, command_name, lang_name)
    print("Shell script generated successfully")

    print(f"\n{lang_name} language has been successfully generated!")
    print(f"You can find it in the '{langs_dir}/{lang_name}' directory.")
    print(f"To run a {lang_name} program, use: ./{command_name} <filename>{file_extension}")
    # Load configuration
    with open(config_file, 'r') as f:
        config = json.load(f)

    lang_name = config['language_name']
    file_extension = config['file_extension']
    command_name = config['command_name']

    # Create main languages directory if it doesn't exist
    langs_dir = 'langs'
    os.makedirs(langs_dir, exist_ok=True)

    # Create language-specific directory
    lang_dir = os.path.join(langs_dir, lang_name)
    os.makedirs(lang_dir, exist_ok=True)

    # Create lib directory
    lib_dir = os.path.join(lang_dir, 'lib')
    os.makedirs(lib_dir, exist_ok=True)

    # Generate interpreter
    generate_interpreter(lib_dir, config)

    # Generate README
    generate_readme(lang_dir, config)

    # Generate example programs
    generate_examples(lang_dir, config)

    # Generate shell script
    generate_shell_script(lang_dir, command_name, lang_name)

def generate_interpreter(lib_dir, config):
    interpreter_code = f"""
import re
import sys
import json
import socket

class {config['language_name']}SyntaxError(Exception):
    pass

# Hardcoded configuration
LANGUAGE_NAME = "{config['language_name']}"
FILE_EXTENSION = "{config['file_extension']}"
COMMAND_PREFIX = "{config['command_prefix']}"
COMMENT_PREFIX = "{config['comment_prefix']}"
ENFORCE_UPPERCASE_COMMENTS = {config['enforce_uppercase_comments']}
ENFORCE_UPPERCASE_CODE = {config['enforce_uppercase_code']}
TYPE_PREFIX_INTEGER = "{config['type_prefixes']['integer']}"
TYPE_PREFIX_FLOAT = "{config['type_prefixes']['float']}"
TYPE_PREFIX_STRING = "{config['type_prefixes']['string']}"
TRUE_VALUE = "{config['true_value']}"
FALSE_VALUE = "{config['false_value']}"
BLOCK_END = "{config['block_end']}"

# Lexer
def lexer(code):
    tokens = []
    lines = code.split('\\n')
    for line_number, line in enumerate(lines, 1):
        if COMMENT_PREFIX in line:
            comment_start = line.index(COMMENT_PREFIX)
            if ENFORCE_UPPERCASE_COMMENTS and any(c.islower() for c in line[comment_start:]):
                raise {config['language_name']}SyntaxError(f"Syntax Error on line {{line_number}}: Comments must be in all caps")
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
            raise {config['language_name']}SyntaxError("Unexpected end of input")
        if tokens[0] == '(':
            tokens.pop(0)  # Remove '('
            result = parse_expression()
            if not tokens or tokens.pop(0) != ')':
                raise {config['language_name']}SyntaxError("Expected closing parenthesis")
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
                raise {config['language_name']}SyntaxError(f"Unexpected token: {{token}}")

    def parse_function_call(name):
        args = []
        if tokens and tokens[0] == '(':
            tokens.pop(0)  # Remove '('
            while tokens and tokens[0] != ')':
                args.append(parse_expression())
                if tokens and tokens[0] == ',':
                    tokens.pop(0)
            if not tokens or tokens.pop(0) != ')':
                raise {config['language_name']}SyntaxError(f"Expected closing parenthesis in function call to {{name}}")
        return FunctionCall(name, args)

    def parse_command():
        token = tokens.pop(0)
        if token in [TYPE_PREFIX_INTEGER, TYPE_PREFIX_FLOAT, TYPE_PREFIX_STRING]:
            if not tokens:
                raise {config['language_name']}SyntaxError(f"Expected value after {{token}}")
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
            raise {config['language_name']}SyntaxError(f"Unknown command: {{token}}")

    def parse_variable_or_function():
        name = tokens.pop(0)
        if tokens and tokens[0] == '(':
            return parse_function_call(name)
        return Variable(name)

    def parse_if_statement():
        tokens.pop(0)  # Remove IF
        condition = parse_expression()
        if not tokens or tokens.pop(0) != ':':
            raise {config['language_name']}SyntaxError("Expected ':' after if condition")
        if_body = []
        while tokens and tokens[0] != f"{{COMMAND_PREFIX}}ELSE" and tokens[0] != BLOCK_END:
            if_body.append(parse_statement())
        else_body = None
        if tokens and tokens[0] == f"{{COMMAND_PREFIX}}ELSE":
            tokens.pop(0)  # Remove ELSE
            if not tokens or tokens.pop(0) != ':':
                raise {config['language_name']}SyntaxError("Expected ':' after else")
            else_body = []
            while tokens and tokens[0] != BLOCK_END:
                else_body.append(parse_statement())
        if not tokens or tokens.pop(0) != BLOCK_END:
            raise {config['language_name']}SyntaxError(f"Expected '{{BLOCK_END}}' at the end of if statement")
        return IfStatement(condition, if_body, else_body)

    def parse_while_loop():
        tokens.pop(0)  # Remove WHILE
        condition = parse_expression()
        if not tokens or tokens.pop(0) != ':':
            raise {config['language_name']}SyntaxError("Expected ':' after while condition")
        body = []
        while tokens and tokens[0] != BLOCK_END:
            body.append(parse_statement())
        if not tokens or tokens.pop(0) != BLOCK_END:
            raise {config['language_name']}SyntaxError(f"Expected '{{BLOCK_END}}' at the end of while loop")
        return WhileLoop(condition, body)

    def parse_statement():
        if not tokens:
            raise {config['language_name']}SyntaxError("Unexpected end of input")
        if len(tokens) >= 3 and tokens[1] == '=':
            name = tokens.pop(0)
            tokens.pop(0)  # Remove '='
            value = parse_expression()
            return Assignment(name, value)
        elif tokens[0].startswith(COMMAND_PREFIX):
            if tokens[0] == f"{{COMMAND_PREFIX}}IF":
                return parse_if_statement()
            elif tokens[0] == f"{{COMMAND_PREFIX}}WHILE":
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
        self.variables = {{}}
        self.sockets = {{}}

    def visit(self, node):
        method_name = f'visit_{{type(node).__name__}}'
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
            raise NameError(f"Variable '{{node.name}}' is not defined")
        return self.variables[node.name]

    def visit_Assignment(self, node):
        value = self.visit(node.value)
        self.variables[node.name] = value
        return value

    def visit_FunctionCall(self, node):
        if node.name == f'{{COMMAND_PREFIX}}PRINT':
            args = [str(self.visit(arg)) for arg in node.args]
            print(*args)
        elif node.name == f'{{COMMAND_PREFIX}}SHOUT':
            if len(node.args) != 1:
                raise ValueError(f"{{COMMAND_PREFIX}}SHOUT function expects exactly one argument")
            arg = self.visit(node.args[0])
            return str(arg).upper()
        elif node.name == f'{{COMMAND_PREFIX}}SOCKET':
            socket_name = self.visit(node.args[0])
            self.sockets[socket_name] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            return socket_name
        elif node.name == f'{{COMMAND_PREFIX}}BIND':
            socket_name = self.visit(node.args[0])
            port = self.visit(node.args[1])
            self.sockets[socket_name].bind(('', port))
        elif node.name == f'{{COMMAND_PREFIX}}LISTEN':
            socket_name = self.visit(node.args[0])
            backlog = self.visit(node.args[1])
            self.sockets[socket_name].listen(backlog)
        elif node.name == f'{{COMMAND_PREFIX}}ACCEPT':
            socket_name = self.visit(node.args[0])
            conn, _ = self.sockets[socket_name].accept()
            return conn
        elif node.name == f'{{COMMAND_PREFIX}}SEND':
            conn = self.visit(node.args[0])
            data = str(self.visit(node.args[1])).encode()
            conn.send(data)
        else:
            raise ValueError(f"Unknown function: {{node.name}}")

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
    except {config['language_name']}SyntaxError as e:
        print(f"{{COMMAND_PREFIX}}PY ERROR: {{str(e).upper()}}")
        sys.exit(1)

def run_file(filename):
    if not filename.endswith(FILE_EXTENSION):
        raise ValueError(f"Only {{FILE_EXTENSION}} files can be run")
    with open(filename, 'r') as file:
        code = file.read()
    return run(code)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: python {{LANGUAGE_NAME.lower()}}.py <filename{{FILE_EXTENSION}}>")
        sys.exit(1)
    
    try:
        run_file(sys.argv[1])
    except Exception as e:
        print(f"ERROR: {{str(e).upper()}}")
        sys.exit(1)
"""
    with open(os.path.join(lib_dir, f"{config['language_name'].lower()}.py"), 'w') as f:
        f.write(interpreter_code)

def generate_readme(lang_dir, config):
    readme_content = f"""
# {config['language_name']} Programming Language

{config['language_name']} is a custom programming language created to honor friendship.

## Features

- File extension: {config['file_extension']}
- Comment prefix: {config['comment_prefix']}
- Command prefix: {config['command_prefix']}
- {'Case-insensitive' if not config['case_sensitive'] else 'Case-sensitive'}
- {'Enforces uppercase comments' if config['enforce_uppercase_comments'] else 'Allows any case for comments'}
- {'Enforces uppercase code' if config['enforce_uppercase_code'] else 'Allows any case for code'}
- True value: {config['true_value']}
- False value: {config['false_value']}

## Running {config['language_name']} Programs

Use the `{config['command_name']}` command followed by your {config['language_name']} file:

```
./{config['command_name']} your_program{config['file_extension']}
```

## Examples

Check out the example programs in this directory:
- `string_manipulation{config['file_extension']}`
- `arithmetic{config['file_extension']}`
- `server{config['file_extension']}`
- `boolean_logic{config['file_extension']}`

Enjoy coding in {config['language_name']}!
"""
    with open(os.path.join(lang_dir, 'README.md'), 'w') as f:
        f.write(readme_content)

def generate_examples(lang_dir, config):
    # String manipulation example
    string_example = f"""
{config['comment_prefix']} String manipulation example

NAME = {config['type_prefixes']['string']} "FRIEND"
GREETING = {config['command_prefix']}SHOUT({config['type_prefixes']['string']} "Hello, ")
FULL_GREETING = GREETING + NAME
{config['command_prefix']}PRINT(FULL_GREETING)
"""
    with open(os.path.join(lang_dir, f"string_manipulation{config['file_extension']}"), 'w') as f:
        f.write(string_example)

    # Arithmetic example
    arithmetic_example = f"""
{config['comment_prefix']} Arithmetic example

A = {config['type_prefixes']['integer']} 10
B = {config['type_prefixes']['integer']} 5

SUM = A + B
DIFFERENCE = A - B
PRODUCT = A * B
QUOTIENT = A / B

{config['command_prefix']}PRINT({config['type_prefixes']['string']} "SUM:", SUM)
{config['command_prefix']}PRINT({config['type_prefixes']['string']} "DIFFERENCE:", DIFFERENCE)
{config['command_prefix']}PRINT({config['type_prefixes']['string']} "PRODUCT:", PRODUCT)
{config['command_prefix']}PRINT({config['type_prefixes']['string']} "QUOTIENT:", QUOTIENT)
"""
    with open(os.path.join(lang_dir, f"arithmetic{config['file_extension']}"), 'w') as f:
        f.write(arithmetic_example)

    # Server example
    server_example = f"""
{config['comment_prefix']} Server example

SERVERSOCKET = {config['command_prefix']}SOCKET({config['type_prefixes']['string']} "SERVER")
{config['command_prefix']}BIND(SERVERSOCKET, {config['type_prefixes']['integer']} 1001)
{config['command_prefix']}LISTEN(SERVERSOCKET, {config['type_prefixes']['integer']} 1)

{config['command_prefix']}PRINT({config['type_prefixes']['string']} "SERVER LISTENING ON PORT 1001")

{config['command_prefix']}WHILE {config['true_value']}:
    {config['command_prefix']}PRINT({config['type_prefixes']['string']} "WAITING FOR CONNECTION...")
    CONNECTION = {config['command_prefix']}ACCEPT(SERVERSOCKET)
    {config['command_prefix']}PRINT({config['command_prefix']}SHOUT({config['type_prefixes']['string']} "CONNECTED"))
    
    RESPONSE = {config['command_prefix']}SHOUT({config['type_prefixes']['string']} "HELLO")
    {config['command_prefix']}SEND(CONNECTION, RESPONSE)
    
    {config['command_prefix']}PRINT({config['type_prefixes']['string']} "CLOSING CONNECTION")
{config['block_end']}

{config['command_prefix']}PRINT({config['type_prefixes']['string']} "SERVER CLOSED")
"""
    with open(os.path.join(lang_dir, f"server{config['file_extension']}"), 'w') as f:
        f.write(server_example)

    # Boolean logic example
    boolean_example = f"""
{config['comment_prefix']} Boolean logic example

A = {config['true_value']}
B = {config['false_value']}

{config['command_prefix']}PRINT({config['type_prefixes']['string']} "A IS {config['true_value']}:", A)
{config['command_prefix']}PRINT({config['type_prefixes']['string']} "B IS {config['false_value']}:", B)

{config['command_prefix']}IF A:
    {config['command_prefix']}PRINT({config['type_prefixes']['string']} "A IS {config['true_value']}")
{config['block_end']}

{config['command_prefix']}IF B:
    {config['command_prefix']}PRINT({config['type_prefixes']['string']} "THIS WILL NOT BE PRINTED")
{config['command_prefix']}ELSE:
    {config['command_prefix']}PRINT({config['type_prefixes']['string']} "B IS {config['false_value']}")
{config['block_end']}
"""
    with open(os.path.join(lang_dir, f"boolean_logic{config['file_extension']}"), 'w') as f:
        f.write(boolean_example)

def generate_shell_script(lang_dir, command_name, lang_name):
    script_content = f"""#!/bin/sh
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
python "$SCRIPT_DIR/lib/{lang_name.lower()}.py" "$@"
"""
    script_path = os.path.join(lang_dir, command_name)
    with open(script_path, 'w', newline='\n') as f:  # Use Unix line endings
        f.write(script_content)
    
    # Make the script executable
    current_permissions = os.stat(script_path).st_mode
    os.chmod(script_path, current_permissions | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

def main():
    if len(sys.argv) != 2:
        print("Usage: python langmaker.py <config_file.json>")
        sys.exit(1)
    
    config_file = sys.argv[1]
    generate_language(config_file)

if __name__ == "__main__":
    main()