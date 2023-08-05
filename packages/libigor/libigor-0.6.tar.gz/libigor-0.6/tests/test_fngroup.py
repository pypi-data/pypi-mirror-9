# -*- coding: utf-8 -*-
import unittest
from igor.util.fngroup import FnGroup, IndexedFnGroup


#==============================================================================
class FnGroupTest(unittest.TestCase):
    #------------------------------------------------------------------------//
    def setUp(self):
        self.mygrp = FnGroup()

        @self.mygrp(123, alias = 'first')
        def first_cmd():
            pass

        @self.mygrp
        def second_cmd():
            pass

        self.first_cmd = first_cmd
        self.second_cmd = second_cmd

    #------------------------------------------------------------------------//
    def test_create(self):
        self.assertEqual(len(self.mygrp.all()), 2)

    #------------------------------------------------------------------------//
    def test_get(self):
        fcmd = self.mygrp.get('first_cmd')
        scmd = self.mygrp.get('second_cmd')

        self.assertEqual(fcmd, self.first_cmd)
        self.assertEqual(scmd, self.second_cmd)

    #------------------------------------------------------------------------//
    def test_getmeta(self):
        fmeta = self.mygrp.get_meta('first_cmd')
        smeta = self.mygrp.get_meta('second_cmd')

        self.assertEqual(fmeta.fn, self.first_cmd)
        self.assertEqual(smeta.fn, self.second_cmd)
        self.assertEqual(fmeta.name, 'first_cmd')
        self.assertEqual(smeta.name, 'second_cmd')
        self.assertEqual(fmeta.alias, 'first')
        self.assertEqual(len(fmeta.args), 1)
        self.assertEqual(fmeta.args[0], 123)


#==============================================================================
class IndexedFnGroupTest(unittest.TestCase):
    #------------------------------------------------------------------------//
    def setUp(self):
        self.fngrp = IndexedFnGroup('alias')

        @self.fngrp(123, alias = 'first')
        def first_cmd():
            pass

        @self.fngrp(alias = 'second')
        def second_cmd():
            pass

        self.first_cmd = first_cmd
        self.second_cmd = second_cmd

    #------------------------------------------------------------------------//
    def test_creation(self):
        self.assertEqual(len(self.fngrp.indexes), 1)
        self.assertEqual(self.fngrp.indexes[0], 'alias')
        self.assertEqual(len(self.fngrp.index), len(self.fngrp.indexes))
        self.assertEqual(
            len(self.fngrp.index['alias']),
            2
        )
        self.assertIn('first', self.fngrp.index['alias'])
        self.assertIn('second', self.fngrp.index['alias'])

    #------------------------------------------------------------------------//
    def test_find_fail(self):
        with self.assertRaises(ValueError):
            self.fngrp.find('invalid_index', 123)

    #------------------------------------------------------------------------//
    def test_find(self):
        fcmd = self.fngrp.find('alias', 'first')
        scmd = self.fngrp.find('alias', 'second')

        self.assertEqual(fcmd.fn, self.first_cmd)
        self.assertEqual(scmd.fn, self.second_cmd)
        self.assertEqual(fcmd.name, 'first_cmd')
        self.assertEqual(scmd.name, 'second_cmd')
        self.assertEqual(fcmd.alias, 'first')
        self.assertEqual(scmd.alias, 'second')

