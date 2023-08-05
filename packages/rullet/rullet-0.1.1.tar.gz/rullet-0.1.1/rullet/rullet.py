# -*- coding: utf-8 -*-

import random, codecs, os, sys

def run():
  if not sys.argv or len(sys.argv) == 1:
    help()
  else:
    args = sys.argv[1:len(sys.argv)]
    print args[(int) (random.random() * len(args))]


def help():
  print ''
  print '[How to use]'
  print ''
  print '$ rullet foo bar baz ...'
  print '> bar'
  print ''


if __name__ == '__main__':
  run()
