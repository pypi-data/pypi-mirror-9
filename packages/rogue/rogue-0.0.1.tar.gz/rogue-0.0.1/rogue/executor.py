#!/usr/bin/env
''' rogue.executor

Execute rogue code
'''

import sys
import traceback

import rg_parser

def compile_rogue(path):
    with open(path) as f:
        text = f.read()
    parser = rg_parser.Parser(text)
    code = compile(parser.root, path, 'exec')
    return code

def execute(path):
    code = compile_rogue(path)
    try:
        d = {}
        exec(code, d)
        d['main']()
    except:
        exc_lines = traceback.format_exc().splitlines()
        exc = '\n'.join(exc_lines[3:])
        sys.stderr.write(exc_lines[0] + '\n')
        sys.stderr.write(exc + '\n')
        sys.exit(1)


if __name__ == '__main__':
    import sys
    path = sys.argv[1]
    execute(path)
