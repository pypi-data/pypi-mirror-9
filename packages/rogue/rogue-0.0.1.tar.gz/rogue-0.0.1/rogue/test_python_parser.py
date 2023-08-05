#!/usr/bin/env python
path = './test_python.py'
with open(path) as f:
    source = f.read()

import ast
a = ast.parse(source)
body = a.body
c = compile(a, '', 'exec')
exec(c)
