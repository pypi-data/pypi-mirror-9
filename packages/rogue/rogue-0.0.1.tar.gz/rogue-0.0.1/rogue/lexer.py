#!/usr/bin/env python
''' rogue.lexer

Lexer for rogue lang.

'''

import re

TOKENS = (
    ('assign', r'='),
    ('colon', r':'),
    ('comma', r','),
    ('print', r'prt\b'),
    #('local', r'loc\b'),
    ('true', r'true\b'),
    ('false', r'false\b'),
    ('null', r'null\b'),
    ('id', r'(?P<val>[a-zA-Z_]\w*)'),
    ('dstring', r'"(?P<val>[^"]*)"'),
    ('sstring', r"'(?P<val>[^']*)'"),
    ('float', r'(?P<sign>[-+]?)(?P<val>[0-9]*\.[0-9]+)'),
    ('int', r'(?P<sign>[-+]?)(?P<val>[0-9]+)'),
    ('lparen', r'(?P<val>\()'),
    ('rparen', r'(?P<val>\))'),
    ('lbrack', r'{'),
    ('rbrack', r'}'),
    ('index', r'\[(?P<val>\d+)\]'),
    ('slice', r'\[(?P<val1>\d*):(?P<val2>\d*)\]'),
)
RE_TOKENS = {key: re.compile(val) for key,val in TOKENS}
RE_INDENT = re.compile(r'^(?P<val>\s+)')

class LexerError(ValueError):
    pass

def gen_tokens(text):
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if not line.strip():
            continue
        indent_m = RE_INDENT.match(line)
        indent = 0
        if indent_m:
            val = indent_m.group('val')
            if len(val) % 4 != 0:
                raise IndentationError('line {}: {}'.format(i, line))
            indent = len(val) / 4
        yield (i, 'indent', indent)
        rest = line.strip()
        while rest:
            for token, _ in TOKENS:
                regex = RE_TOKENS[token]
                match = regex.match(rest)
                if match:
                    yield (i, token, match.group())
                    rest = rest[match.end():].strip()
                    break
            else:
                raise LexerError('line {}: ...{}'.format(i, rest))

if __name__ == '__main__':
    import sys
    filename = sys.argv[1]
    with open(filename) as f:
        text = f.read()
    for i, token, val in gen_tokens(text):
        print('Line {}: {} = {}'.format(i, token, val))
