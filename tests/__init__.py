import sys

from os.path import abspath, dirname, join

PROJECT_ROOT = abspath(join(dirname(dirname(__file__)), "baden"))
sys.path.insert(0, PROJECT_ROOT)
