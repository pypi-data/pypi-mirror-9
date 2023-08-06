#!/usr/bin/env python
import unittest
from igor.fieldspec import Fieldspec


#==============================================================================
class FieldspecTest(unittest.TestCase):
    #------------------------------------------------------------------------//
    def test_fs1(self):
        fs = Fieldspec('field1,field2(sub1,sub2),field3(*)')
        self.assertEqual(repr(fs), '<Fieldspec: field1,field2,field3>')

        self.assertEqual(fs['field1'], True)
        self.assertIn('field1', fs)
        self.assertNotIn('field7', fs)

        self.assertEqual(repr(fs['field2']), '<Fieldspec: sub1,sub2>')
        self.assertEqual(fs['field2']['sub1'], True)
        self.assertIn('sub1', fs['field2'])

