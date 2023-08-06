#!/usr/bin/env python3

import subprocess


def get_tags():
    output = subprocess.Popen(('git', 'tag'), stdout=subprocess.PIPE).stdout
    tags = map(lambda tag: tag.decode('utf-8').strip(), output.readlines())
    return list(tags)


def checkout(tag):
    if subprocess.call(('git', 'checkout', tag)) is not 0:
        raise Exception("Failed to checkout '{}'".format(tag))


def build_universal():
    command = 'python setup.py sdist bdist_wheel --universal'.split()
    if subprocess.call(command) is not 0:
        raise Exception('setup.py failed')


def build_source_dist():
    command = 'python setup.py sdist'.split()
    if subprocess.call(command) is not 0:
        raise Exception('setup.py failed')


if __name__ == '__main__':
    for tag in get_tags():
        checkout(tag)

        with open('setup.py') as fp:
            contents = fp.readlines()
            setuptools = filter(lambda line: 'setuptools' in line, contents)
            has_setuptools = len(list(setuptools)) > 0
            if has_setuptools:
                build_universal()
            else:
                build_source_dist()

