
import sys
import json
import socket

class BHAVSyntaxError(Exception):
    pass

class Config:
    def __init__(self, config_file=None):
        self.__dict__.update({
    "language_name": "BHAV",
    "file_extension": ".bhav",
    "command_name": "bhavexec",
    "comment_prefix": "BHAVCOMMENT",
    "command_prefix": "BHAV",
    "case_sensitive": "False",
    "enforce_uppercase_comments": "True",
    "enforce_uppercase_code": "True",
    "type_prefixes": {
        "integer": "BHAVINT",
        "float": "BHAVFLOAT",
        "string": "BHAVSTRING"
    },
    "block_end": "BHAVEND",
    "true_value": "YEYS",
    "false_value": "NAOW"
})

# Lexer
def lexer(code, config):
    tokens = []
    lines = code.split('\n')
    for line_number, line in enumerate(lines, 1):
        if config['comment_prefix'] in line:
            comment_start = line.index(config['comment_prefix'])
            if config['enforce_uppercase_comments'] and any(c.islower() for c in line[comment_start:]):
                raise BHAVSyntaxError(f"Syntax Error on line {line_number}: Comments must be in all caps")
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
            raise ValueError(f"Unknown {config['command_prefix']} command: {token}")

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
        self.variables = {}
        self.config = config

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
        return self.variables.get(node.name, 0)

    def visit_Assignment(self, node):
        value = self.visit(node.value)
        self.variables[node.name] = value
        return value

    def visit_FunctionCall(self, node):
        if node.name == f'{config["command_prefix"]}PRINT':
            args = [self.visit(arg) for arg in node.args]
            print(*args)
        elif node.name == f'{config["command_prefix"]}SHOUT':
            if len(node.args) != 1:
                raise ValueError(f"{config['command_prefix']}SHOUT function expects exactly one argument")
            arg = self.visit(node.args[0])
            return str(arg).upper()
        else:
            raise ValueError(f"Unknown function: {node.name}")

def run(code, config):
    if config.enforce_uppercase_code:
        code = code.upper()
    try:
        tokens = lexer(code, config)
        ast = parse(tokens, config)
        interpreter = Interpreter(config)
        for statement in ast:
            interpreter.visit(statement)
    except BHAVSyntaxError as e:
        print(f"{config['command_prefix']}PY ERROR: {str(e).upper()}")
        sys.exit(1)

def run_file(filename, config):
    if not filename.endswith(config['file_extension']):
        raise ValueError(f"Only {config['file_extension']} files can be run")
    with open(filename, 'r') as file:
        code = file.read()
    return run(code, config)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: python {config['language_name'].lower()}.py <filename{config['file_extension']}>")
        sys.exit(1)
    
    config = Config()
    
    try:
        run_file(sys.argv[1], config)
    except Exception as e:
        print(f"ERROR: {str(e).upper()}")
        sys.exit(1)
