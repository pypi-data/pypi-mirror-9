#!/usr/bin/env python
''' rogue.bin

Program entry points.

'''

import executor

def rogue():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('path')
    args = parser.parse_args()
    executor.execute(args.path)
