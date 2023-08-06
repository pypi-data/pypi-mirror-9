#!/usr/bin/env python
import os
import re

RE_VERSION = re.compile(r'\s*version\s*=\s*["\']([^"\']+)["\'],\s*')
RE_GROUPS = re.compile(r'(?P<major>\w+)\.(?P<minor>\w+)\.(?P<patch>\w+)')

def line_version(path):
    with open(path) as f:
        for i, line in enumerate(f):
            match = RE_VERSION.match(line)
            if match:
                version = match.group(1)
                break
        else:
            raise ValueError('No version at {}'.format(path))
    gmatch = RE_GROUPS.match(version)
    major, minor, patch = gmatch.group('major'), gmatch.group('minor'), gmatch.group('patch')
    return i, version, int(major), int(minor), int(patch)

def check(path):
    line_no, version, major, minor, patch = line_version(path)
    print(version)

def bump_patch(path, push=False):
    line_no, version, major, minor, patch = line_version(path)
    new_version = '{}.{}.{}'.format(major, minor, patch+1)
    bump_set(path, new_version, push=push)
    
def bump_minor(path, push=False):
    line_no, version, major, minor, patch = line_version(path)
    new_version = '{}.{}.{}'.format(major, minor+1, 0)
    bump_set(path, new_version, push=push)

def bump_major(path, push=False):
    line_no, version, major, minor, patch = line_version(path)
    new_version = '{}.{}.{}'.format(major+1, 0, 0)
    bump_set(path, new_version, push=push)

def bump_set(path, new_version, push=False):
    line_no, version, major, minor, patch = line_version(path)
    with open(path) as f:
        setup_lines = f.readlines()
    setup_lines[line_no] = setup_lines[line_no].replace(version, new_version)
    new_text = ''.join(setup_lines)
    with open(path, 'w') as f:
        f.write(new_text)
    if push:
        pushout(path, new_version)

def pushout(path, new_version):
    dirname = os.path.dirname(path)
    os.chdir(dirname)
    os.system('git add -u')
    os.system('git commit -am "{}"'.format(new_version))
    os.system('git tag {}'.format(new_version))
    os.system('git push --all -u')
    os.system('git push --tags')

def main():
    import sys
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', '-c', action='store_true', help='print current version')
    parser.add_argument('--major', '-M', action='store_true', help='bump major')
    parser.add_argument('--minor', '-m', action='store_true', help='bump minor')
    parser.add_argument('--patch', '-p', action='store_true', help='bump patch level')
    parser.add_argument('--set', '-s', help='set version number')
    parser.add_argument('--setup-path', '-S', default='./setup.py', help='path to setup file')
    parser.add_argument('--push', '-P', action='store_true', help='tag and push using git')
    args = parser.parse_args()
    if args.check:
        check(args.setup_path)
    elif args.set:
        bump_set(args.setup_path, args.set, push=args.push)
    elif args.minor:
        bump_minor(args.setup_path, push=args.push)
    elif args.patch:
        bump_patch(args.setup_path, push=args.push)
    elif args.major:
        bump_major(args.setup_path, push=args.push)
