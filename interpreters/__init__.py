from os import path

# pylint: disable=import-error
from lisp.core.loading import load_classes


def find_interpreters():
    return load_classes(__package__, path.dirname(__file__))
