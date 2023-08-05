#!/usr/bin/env python

"""
"""

import sys
import time
import unittest

from concrete import AnnotationMetadata, Communication
from concrete.util import generate_UUID
from concrete.validate import validate_communication

#

class TestConcreteDump(unittest.TestCase):
    def test_generate_uuid(self):
        print "HELLO WORLD"
        comm = Communication()
        comm.uuid = generate_UUID()



if __name__ == '__main__':
    unittest.main(buffer=True)
