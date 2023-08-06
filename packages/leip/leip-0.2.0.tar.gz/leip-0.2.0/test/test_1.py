#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test 1
"""

import leip


@leip.arg('name', help='Name to say hello to', default='world')
@leip.command
def hello(app, args):
    """
    Run the proverbial hello world test

    Help for the command is provided in the docstring. The first line
    is used for the command overview (test_1.py -h), the rest is used
    for a more extensive help per command (test_1.py hello -h).
    """
    print("Hello %s" % args.name)

if __name__ == '__main__':
    app = leip.app()
    app.discover(locals())
    app.run()
