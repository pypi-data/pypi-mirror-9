# -*- coding: utf-8 -*-

import random, codecs, os, sys

def show():
  if not sys.argv or len(sys.argv) == 1:
    help()
  else:
    print run(sys.argv[1:len(sys.argv)])


def run(params=[]):
  if len(params) == 0:
    return
  else:
    return params[(int) (random.random() * len(params))]


def help():
  print ''
  print '[How to use]'
  print ''
  print '$ rullet foo bar baz ...'
  print '> bar'
  print ''


if __name__ == '__main__':
  show()
