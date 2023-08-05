# -*- coding: utf-8 -*-

import random, codecs, os, sys

def run():
  args = sys.argv[1:len(sys.argv)]
  print args[(int) (random.random() * len(args))]


if __name__ == '__main__':
  run()