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
    # Convert JSON booleans to Python booleans in a new dictionary
    python_config = {}
    for key, value in config.items():
        if isinstance(value, bool):
            python_config[key] = str(value)
        elif isinstance(value, dict):
            python_config[key] = {k: str(v) if isinstance(v, bool) else v for k, v in value.items()}
        else:
            python_config[key] = value
    
    # Convert the Python dictionary to a string representation
    config_str = json.dumps(python_config, indent=4)
    
    interpreter_code = f"""
import sys
import json
import socket

class {config['language_name']}SyntaxError(Exception):
    pass

class Config:
    def __init__(self):
        self.__dict__.update({config_str})

config = Config()

# Lexer
def lexer(code):
    tokens = []
    lines = code.split('\\n')
    for line_number, line in enumerate(lines, 1):
        if config.comment_prefix in line:
            comment_start = line.index(config.comment_prefix)
            if config.enforce_uppercase_comments and any(c.islower() for c in line[comment_start:]):
                raise {config['language_name']}SyntaxError(f"Syntax Error on line {{line_number}}: Comments must be in all caps")
            line = line[:comment_start].strip()
        if not line:
            continue
        line_tokens = []
        current = ''
        for char in line:
            if char.isspace():
                if current:
                    line_tokens.append(current)
                    current = ''
            elif char in '+-*/()=:':
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

def parse(tokens):
    def parse_expression():
        result = parse_term()
        while len(tokens) > 0 and tokens[0] in '+-':
            op = tokens.pop(0)
            right = parse_term()
            result = BinOp(result, op, right)
        return result

    def parse_term():
        result = parse_factor()
        while len(tokens) > 0 and tokens[0] in '*/':
            op = tokens.pop(0)
            right = parse_factor()
            result = BinOp(result, op, right)
        return result

    def parse_factor():
        if tokens[0] == '(':
            tokens.pop(0)  # Remove '('
            result = parse_expression()
            tokens.pop(0)  # Remove ')'
            return result
        elif tokens[0].startswith(config.command_prefix):
            return parse_command()
        elif tokens[0] in [config.true_value, config.false_value]:
            return BooleanLiteral(tokens.pop(0) == config.true_value)
        elif tokens[0].isalpha():
            return parse_variable_or_function()
        else:
            return Number(float(tokens.pop(0)))

    def parse_command():
        token = tokens.pop(0)
        if token == config.type_prefixes.integer:
            return Number(int(tokens.pop(0)))
        elif token == config.type_prefixes.float:
            return Number(float(tokens.pop(0)))
        elif token == config.type_prefixes.string:
            return String(tokens.pop(0).strip('"'))
        else:
            raise ValueError(f"Unknown {{config.command_prefix}} command: {{token}}")

    def parse_variable_or_function():
        name = tokens.pop(0)
        if len(tokens) > 0 and tokens[0] == '(':
            tokens.pop(0)  # Remove '('
            args = []
            while len(tokens) > 0 and tokens[0] != ')':
                args.append(parse_expression())
                if tokens[0] == ',':
                    tokens.pop(0)
            tokens.pop(0)  # Remove ')'
            return FunctionCall(name, args)
        return Variable(name)

    def parse_statement():
        if len(tokens) >= 3 and tokens[1] == '=':
            name = tokens.pop(0)
            tokens.pop(0)  # Remove '='
            value = parse_expression()
            return Assignment(name, value)
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
        return self.variables.get(node.name, 0)

    def visit_Assignment(self, node):
        value = self.visit(node.value)
        self.variables[node.name] = value
        return value

    def visit_FunctionCall(self, node):
        if node.name == f'{{config.command_prefix}}PRINT':
            args = [self.visit(arg) for arg in node.args]
            print(*args)
        elif node.name == f'{{config.command_prefix}}SHOUT':
            if len(node.args) != 1:
                raise ValueError(f"{{config.command_prefix}}SHOUT function expects exactly one argument")
            arg = self.visit(node.args[0])
            return str(arg).upper()
        else:
            raise ValueError(f"Unknown function: {{node.name}}")

def run(code):
    if config.enforce_uppercase_code:
        code = code.upper()
    try:
        tokens = lexer(code)
        ast = parse(tokens)
        interpreter = Interpreter()
        for statement in ast:
            interpreter.visit(statement)
    except {config['language_name']}SyntaxError as e:
        print(f"{{config.command_prefix}}PY ERROR: {{str(e).upper()}}")
        sys.exit(1)

def run_file(filename):
    if not filename.endswith(config.file_extension):
        raise ValueError(f"Only {{config.file_extension}} files can be run")
    with open(filename, 'r') as file:
        code = file.read()
    return run(code)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: python {{config.language_name.lower()}}.py <filename{{config.file_extension}}>")
        sys.exit(1)
    
    try:
        run_file(sys.argv[1])
    except Exception as e:
        print(f"ERROR: {{str(e).upper()}}")
        sys.exit(1)
"""
    with open(os.path.join(lib_dir, f"{config['language_name'].lower()}.py"), 'w') as f:
        f.write(interpreter_code)
    # Convert JSON booleans to Python booleans in a new dictionary
    python_config = {}
    for key, value in config.items():
        if isinstance(value, bool):
            python_config[key] = str(value)
        elif isinstance(value, dict):
            python_config[key] = {k: str(v) if isinstance(v, bool) else v for k, v in value.items()}
        else:
            python_config[key] = value
    
    # Convert the Python dictionary to a string representation
    config_str = json.dumps(python_config, indent=4)
    
    interpreter_code = f"""
import sys
import json
import socket

class {config['language_name']}SyntaxError(Exception):
    pass

class Config:
    def __init__(self):
        self.__dict__.update({config_str})

config = Config()

# Lexer
def lexer(code):
    tokens = []
    lines = code.split('\\n')
    for line_number, line in enumerate(lines, 1):
        if config.comment_prefix in line:
            comment_start = line.index(config.comment_prefix)
            if config.enforce_uppercase_comments and any(c.islower() for c in line[comment_start:]):
                raise {config['language_name']}SyntaxError(f"Syntax Error on line {{line_number}}: Comments must be in all caps")
            line = line[:comment_start].strip()
        if not line:
            continue
        line_tokens = []
        current = ''
        for char in line:
            if char.isspace():
                if current:
                    line_tokens.append(current)
                    current = ''
            elif char in '+-*/()=:':
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

def parse(tokens):
    def parse_expression():
        result = parse_term()
        while len(tokens) > 0 and tokens[0] in '+-':
            op = tokens.pop(0)
            right = parse_term()
            result = BinOp(result, op, right)
        return result

    def parse_term():
        result = parse_factor()
        while len(tokens) > 0 and tokens[0] in '*/':
            op = tokens.pop(0)
            right = parse_factor()
            result = BinOp(result, op, right)
        return result

    def parse_factor():
        if tokens[0] == '(':
            tokens.pop(0)  # Remove '('
            result = parse_expression()
            tokens.pop(0)  # Remove ')'
            return result
        elif tokens[0].startswith(config.command_prefix):
            return parse_command()
        elif tokens[0] in [config.true_value, config.false_value]:
            return BooleanLiteral(tokens.pop(0) == config.true_value)
        elif tokens[0].isalpha():
            return parse_variable_or_function()
        else:
            return Number(float(tokens.pop(0)))

    def parse_command():
        token = tokens.pop(0)
        if token in config.type_prefixes.values():
            return parse_type(token)
        else:
            raise ValueError(f"Unknown {{config.command_prefix}} command: {{token}}")

    def parse_type(type_token):
        if type_token == config.type_prefixes['integer']:
            return Number(int(tokens.pop(0)))
        elif type_token == config.type_prefixes['float']:
            return Number(float(tokens.pop(0)))
        elif type_token == config.type_prefixes['string']:
            return String(tokens.pop(0).strip('"'))

    def parse_variable_or_function():
        name = tokens.pop(0)
        if len(tokens) > 0 and tokens[0] == '(':
            tokens.pop(0)  # Remove '('
            args = []
            while len(tokens) > 0 and tokens[0] != ')':
                args.append(parse_expression())
                if tokens[0] == ',':
                    tokens.pop(0)
            tokens.pop(0)  # Remove ')'
            return FunctionCall(name, args)
        return Variable(name)

    def parse_statement():
        if len(tokens) >= 3 and tokens[1] == '=':
            name = tokens.pop(0)
            tokens.pop(0)  # Remove '='
            value = parse_expression()
            return Assignment(name, value)
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
        return self.variables.get(node.name, 0)

    def visit_Assignment(self, node):
        value = self.visit(node.value)
        self.variables[node.name] = value
        return value

    def visit_FunctionCall(self, node):
        if node.name == f'{{config.command_prefix}}PRINT':
            args = [self.visit(arg) for arg in node.args]
            print(*args)
        elif node.name == f'{{config.command_prefix}}SHOUT':
            if len(node.args) != 1:
                raise ValueError(f"{{config.command_prefix}}SHOUT function expects exactly one argument")
            arg = self.visit(node.args[0])
            return str(arg).upper()
        else:
            raise ValueError(f"Unknown function: {{node.name}}")

def run(code):
    if config.enforce_uppercase_code:
        code = code.upper()
    try:
        tokens = lexer(code)
        ast = parse(tokens)
        interpreter = Interpreter()
        for statement in ast:
            interpreter.visit(statement)
    except {config['language_name']}SyntaxError as e:
        print(f"{{config.command_prefix}}PY ERROR: {{str(e).upper()}}")
        sys.exit(1)

def run_file(filename):
    if not filename.endswith(config.file_extension):
        raise ValueError(f"Only {{config.file_extension}} files can be run")
    with open(filename, 'r') as file:
        code = file.read()
    return run(code)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: python {{config.language_name.lower()}}.py <filename{{config.file_extension}}>")
        sys.exit(1)
    
    try:
        run_file(sys.argv[1])
    except Exception as e:
        print(f"ERROR: {{str(e).upper()}}")
        sys.exit(1)
"""
    with open(os.path.join(lib_dir, f"{config['language_name'].lower()}.py"), 'w') as f:
        f.write(interpreter_code)
    # Convert JSON booleans to Python booleans in a new dictionary
    python_config = {}
    for key, value in config.items():
        if isinstance(value, bool):
            python_config[key] = str(value)
        elif isinstance(value, dict):
            python_config[key] = {k: str(v) if isinstance(v, bool) else v for k, v in value.items()}
        else:
            python_config[key] = value
    
    # Convert the Python dictionary to a string representation
    config_str = json.dumps(python_config, indent=4)
    
    interpreter_code = f"""
import sys
import json
import socket

class {config['language_name']}SyntaxError(Exception):
    pass

class Config:
    def __init__(self, config_file=None):
        self.__dict__.update({config_str})

# Lexer
def lexer(code, config):
    tokens = []
    lines = code.split('\\n')
    for line_number, line in enumerate(lines, 1):
        if config['comment_prefix'] in line:
            comment_start = line.index(config['comment_prefix'])
            if config['enforce_uppercase_comments'] and any(c.islower() for c in line[comment_start:]):
                raise {config['language_name']}SyntaxError(f"Syntax Error on line {{line_number}}: Comments must be in all caps")
            line = line[:comment_start].strip()
        if not line:
            continue
        line_tokens = []
        current = ''
        for char in line:
            if char.isspace():
                if current:
                    line_tokens.append(current)
                    current = ''
            elif char in '+-*/()=:':
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

def parse(tokens, config):
    def parse_expression():
        result = parse_term()
        while len(tokens) > 0 and tokens[0] in '+-':
            op = tokens.pop(0)
            right = parse_term()
            result = BinOp(result, op, right)
        return result

    def parse_term():
        result = parse_factor()
        while len(tokens) > 0 and tokens[0] in '*/':
            op = tokens.pop(0)
            right = parse_factor()
            result = BinOp(result, op, right)
        return result

    def parse_factor():
        if tokens[0] == '(':
            tokens.pop(0)  # Remove '('
            result = parse_expression()
            tokens.pop(0)  # Remove ')'
            return result
        elif tokens[0].startswith(config['command_prefix']):
            return parse_command()
        elif tokens[0] in [config['true_value'], config['false_value']]:
            return BooleanLiteral(tokens.pop(0) == config['true_value'])
        elif tokens[0].isalpha():
            return parse_variable_or_function()
        else:
            return Number(float(tokens.pop(0)))

    def parse_command():
        token = tokens.pop(0)
        if token in config['type_prefixes'].values():
            return parse_type(token)
        else:
            raise ValueError(f"Unknown {{config['command_prefix']}} command: {{token}}")

    def parse_type(type_token):
        if type_token == config['type_prefixes']['integer']:
            return Number(int(tokens.pop(0)))
        elif type_token == config['type_prefixes']['float']:
            return Number(float(tokens.pop(0)))
        elif type_token == config['type_prefixes']['string']:
            return String(tokens.pop(0).strip('"'))

    def parse_variable_or_function():
        name = tokens.pop(0)
        if len(tokens) > 0 and tokens[0] == '(':
            tokens.pop(0)  # Remove '('
            args = []
            while len(tokens) > 0 and tokens[0] != ')':
                args.append(parse_expression())
                if tokens[0] == ',':
                    tokens.pop(0)
            tokens.pop(0)  # Remove ')'
            return FunctionCall(name, args)
        return Variable(name)

    def parse_statement():
        if len(tokens) >= 3 and tokens[1] == '=':
            name = tokens.pop(0)
            tokens.pop(0)  # Remove '='
            value = parse_expression()
            return Assignment(name, value)
        else:
            return parse_expression()

    statements = []
    while tokens:
        statements.append(parse_statement())
    return statements

# Interpreter
class Interpreter:
    def __init__(self, config):
        self.variables = {{}}
        self.config = config

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
        return self.variables.get(node.name, 0)

    def visit_Assignment(self, node):
        value = self.visit(node.value)
        self.variables[node.name] = value
        return value

    def visit_FunctionCall(self, node):
        if node.name == f'{{config["command_prefix"]}}PRINT':
            args = [self.visit(arg) for arg in node.args]
            print(*args)
        elif node.name == f'{{config["command_prefix"]}}SHOUT':
            if len(node.args) != 1:
                raise ValueError(f"{{config['command_prefix']}}SHOUT function expects exactly one argument")
            arg = self.visit(node.args[0])
            return str(arg).upper()
        else:
            raise ValueError(f"Unknown function: {{node.name}}")

def run(code, config):
    if config.enforce_uppercase_code:
        code = code.upper()
    try:
        tokens = lexer(code, config)
        ast = parse(tokens, config)
        interpreter = Interpreter(config)
        for statement in ast:
            interpreter.visit(statement)
    except {config['language_name']}SyntaxError as e:
        print(f"{{config['command_prefix']}}PY ERROR: {{str(e).upper()}}")
        sys.exit(1)

def run_file(filename, config):
    if not filename.endswith(config['file_extension']):
        raise ValueError(f"Only {{config['file_extension']}} files can be run")
    with open(filename, 'r') as file:
        code = file.read()
    return run(code, config)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: python {{config['language_name'].lower()}}.py <filename{{config['file_extension']}}>")
        sys.exit(1)
    
    config = Config()
    
    try:
        run_file(sys.argv[1], config)
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
    CONNECTION, ADDRESS = {config['command_prefix']}ACCEPT(SERVERSOCKET)
    {config['command_prefix']}PRINT({config['command_prefix']}SHOUT({config['type_prefixes']['string']} "CONNECTED TO:"), ADDRESS)
    
    RESPONSE = {config['command_prefix']}SHOUT({config['type_prefixes']['string']} "HELLO")
    {config['command_prefix']}SEND(CONNECTION, RESPONSE)
    
    CONNECTION.CLOSE()
{config['block_end']}
"""
    with open(os.path.join(lang_dir, f"server{config['file_extension']}"), 'w') as f:
        f.write(server_example)

    # Boolean logic example
    boolean_example = f"""
{config['comment_prefix']} Boolean logic example

A = {config['true_value']}
B = {config['false_value']}

{config['command_prefix']}PRINT({config['type_prefixes']['string']} "A IS TRUE:", A)
{config['command_prefix']}PRINT({config['type_prefixes']['string']} "B IS FALSE:", B)

{config['command_prefix']}IF A:
    {config['command_prefix']}PRINT({config['type_prefixes']['string']} "A IS TRUE")
{config['block_end']}

{config['command_prefix']}IF B:
    {config['command_prefix']}PRINT({config['type_prefixes']['string']} "THIS WILL NOT BE PRINTED")
{config['command_prefix']}ELSE:
    {config['command_prefix']}PRINT({config['type_prefixes']['string']} "B IS FALSE")
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