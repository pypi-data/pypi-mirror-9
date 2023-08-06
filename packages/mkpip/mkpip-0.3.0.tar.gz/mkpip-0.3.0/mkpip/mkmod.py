#!/usr/bin/env python
import sys
import os

def build_path():
    curdir = os.path.abspath(os.getcwd())
    paths = []
    while os.path.exists(os.path.join(curdir, '__init__.py')):
        paths += [os.path.basename(curdir).replace('-', '_')]
        curdir = os.path.dirname(curdir)
    return paths[::-1]

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('name')
    parser.add_argument('description')
    args = parser.parse_args()
    name = args.name
    desc = args.description

    mod_temp = '''#!/usr/bin/env python
\'\'\' {path}
{desc}
\'\'\'
'''
    path = '.'.join(build_path() + [name])
    mod_text = mod_temp.format(path=path, desc=desc)
    ipath = os.path.join(name, '__init__.py')
    if os.path.exists(ipath):
        print('Module already exists... exitting.')
        sys.exit(1)
    if not os.path.exists(name):
        os.mkdir(name)
    with open(os.path.join(name, '__init__.py'), 'w') as f:
        f.write(mod_text)
