#!/usr/bin/env python
''' rogue.parser

Parser for rogue lang.

'''
import lexer
import ast as stdast

class PrintVisitor(object):
    
    def __init__(self, root):
        self.root = root

    def param_str(self, params):
        return ', '.join([p.id for p in params])

    def output(self, num_indent=0):
        indent = num_indent*' '
        lhs, rhs = [], []
        cls = self.root.__class__.__name__
        children = []
        if isinstance(self.root, stdast.Module):
            me = '{}Module'.format(indent)
            children = self.root.body
        elif isinstance(self.root, stdast.FunctionDef):
            params = self.param_str(self.root.args.args)
            children = self.root.body
            me = '{}Func {}({})'.format(indent, self.root.name, params)
        elif isinstance(self.root, stdast.Num):
            me = '{}Const {}'.format(indent, self.root.n)
        elif isinstance(self.root, stdast.Str):
            me = '{}Const {}'.format(indent, self.root.s)
        elif isinstance(self.root, stdast.Name):
            me = '{}id: {}'.format(indent, self.root.id)
        elif isinstance(self.root, stdast.Assign):
            me = '{}Assign'.format(indent)
            children = self.root.targets + [self.root.value]
        elif isinstance(self.root, stdast.Expr):
            me = '{}Expr'.format(indent)
            children = [self.root.value]
        elif isinstance(self.root, stdast.Call):
            me = '{}Call {}'.format(indent, self.root.func.id)
            children = self.root.args
        elif isinstance(self.root, stdast.Print):
            me = '{}Print'.format(indent)
            children = self.root.values
        print(me)
        for child in children:
            pv = PrintVisitor(child)
            pv.output(num_indent=num_indent + 4)

class Parser(object):
    
    def __init__(self, text):
        self.indent = 0
        self.tokgen = lexer.gen_tokens(text)
        self.accepted = False
        self.functions = {}
        self.done = False
        self.root = None
        self.next_token()
        self.parse()
        stdast.fix_missing_locations(self.root)

    def parse(self):
        self.root = stdast.Module()
        self.root.body = []
        while self.accept('indent', 0):
            func = self.new_function(0)
            self.root.body += [func]
            self.functions[func.name] = func

    def new_function(self, indent):
        self.expect('indent', indent)
        val = self.expect('id')
        func_ast = stdast.FunctionDef()
        func_ast.lineno = self.i + 1
        func_ast.decorator_list = []
        func_ast.name = val
        func_ast.args = self.new_arguments()
        self.expect('colon')
        func_ast.body = self.new_body(indent + 1)
        return func_ast

    def new_arguments(self):
        args = stdast.arguments()
        args.lineno = self.i + 1
        args.args = []
        args.defaults = []
        args.varargs = None
        args.kwargs = None
        args.lambda_keyword = None
        if self.accept('lparen'):
            self.expect('lparen')
            while True:
                if self.accept('rparen'):
                    self.expect('rparen')
                    break
                args.args += [self.new_param()]
                if self.accept('comma'):
                    self.expect('comma')
        return args

    def new_param(self):
        id = self.expect('id')
        name = stdast.Name()
        name.lineno = self.i + 1
        name.id = id
        name.ctx = stdast.Param()
        name.ctx.lineno = self.i + 1
        return name

    def new_load(self):
        id = self.expect('id')
        name = stdast.Name()
        name.lineno = self.i + 1
        name.id = id
        name.ctx = stdast.Load()
        name.ctx.lineno = self.i + 1
        return name

    def new_store(self):
        id = self.expect('id')
        name = stdast.Name()
        name.lineno = self.i + 1
        name.id = id
        name.ctx = stdast.Store()
        name.lineno = self.i + 1
        return name

    def new_body(self, indent):
        body = []
        while True:
            stmt = self.statement(indent)
            if stmt is None:
                break
            body += [stmt]
        if not body:
            raise SyntaxError('Line {}: Expected statement.'.format(self.i))
        return body

    def statement(self, indent):
        if not self.accept('indent', indent):
            return None
        self.expect('indent', indent)
        if self.accept('id'):
            if self.val in self.functions:
                newast = self.new_call()
            else:
                newast = self.new_assignment()
        elif self.accept('print'):
            newast = self.new_print()
        else:
            return None
        return newast

    def new_assignment(self):
        assignment = stdast.Assign()
        assignment.lineno = self.i + 1
        assignment.targets = [self.new_store()]
        self.expect('assign')
        assignment.value = self.expression()
        if assignment.value is None:
            raise SyntaxError('Line {}: Expected expression.'.format(self.i))
        return assignment

    def new_func_name(self, id):
        return callast

    def new_call(self):
        exprast = stdast.Expr()
        exprast.lineno = self.i + 1
        callast = stdast.Call()
        callast.lineno = self.i + 1
        callast.keywords = []
        callast.func = self.new_load()
        callast.args = []
        while True:
            expr = self.expression()
            if expr is None:
                break
            callast.args += [expr]
        exprast.value = callast
        return exprast

    def main_call(self):
        name = stdast.Name()
        name.lineno = self.i + 1
        name.id = 'main'
        name.ctx = stdast.Load()
        name.ctx.lineno = self.i + 1
        exprast = stdast.Expr()
        exprast.lineno = self.i + 1
        callast = stdast.Call()
        callast.lineno = self.i + 1
        callast.keywords = []
        callast.func = name
        callast.args = []
        exprast.value = callast
        return exprast

    def new_print(self):
        self.expect('print')
        prt = stdast.Print()
        prt.lineno = self.i + 1
        prt.nl = True
        expr = self.expression()
        if expr:
            prt.values = [expr]
        else:
            prt.values = [self.new_load()]
        return prt

    def new_str(self, value):
        s = stdast.Str()
        s.lineno = self.i + 1
        s.s = value
        return s

    def new_num(self, value):
        n = stdast.Num()
        n.lineno = self.i + 1
        n.n = value
        return n

    def expression(self):
        # return expr ast
        if self.accept('id'):
            return self.new_load()
        elif self.accept('dstring'):
            string = self.expect('dstring')
            return self.new_str(string)
        elif self.accept('sstring'):
            string = self.expect('sstring')
            return self.new_str(string)
        elif self.accept('int'):
            integer = self.expect('int')
            return self.new_num(integer)
        else:
            return None

    def expect(self, sym, val=None):
        #print('Line {}: Expecting {} of {}'.format(self.i, sym, val))
        #print('Have {} of {}'.format(self.tok, self.val))
        if not self.accept(sym, val=val):
            if val is None:
                raise SyntaxError('Line {}: Expected {}'.format(self.i, sym))
            else:
                raise SyntaxError('Line {}: Expected {} of {}'.format(
                    self.i, sym, val
                ))
        old_val = self.val
        self.next_token()
        return old_val

    def next_token(self):
        try:
            self.i, self.tok, self.val = self.tokgen.next()
        except StopIteration:
            self.done = True

    def accept(self, sym, val=None):
        if self.done:
            return False
        if val is None:
            self.accepted = (self.tok == sym)
        else:
            self.accepted = (self.tok == sym and self.val == val)
        return self.accepted

def main():
    with open('test_parser.rg') as f:
        text = f.read()
    parser = Parser(text)
    pv = PrintVisitor(parser.root)
    pv.output()

if __name__ == '__main__':
    main()
