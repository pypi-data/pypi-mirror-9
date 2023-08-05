#!/usr/bin/env python

import rg_parser

with open('test_exec.rg') as f:
    text = f.read()
parser = rg_parser.Parser(text)
root = parser.root
