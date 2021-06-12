# -*- coding: utf-8 -*-
# Copyright (c) 2013, 2014 Erik Hetzner
#
# This file is part of ledger-autosync
#
# ledger-autosync is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# ledger-autosync is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ledger-autosync. If not, see
# <http://www.gnu.org/licenses/>.


import os.path
from unittest import TestCase

from nose.plugins.attrib import attr
from nose.tools import raises
from ofxclient.config import OfxConfig

from ledgerautosync import EmptyInstitutionException
from ledgerautosync.cli import run
from ledgerautosync.converter import OfxConverter
from ledgerautosync.ledgerwrap import HLedger, Ledger, LedgerPython
from ledgerautosync.sync import OfxSynchronizer


class WeirdOfxTest(object):
    @raises(EmptyInstitutionException)
    def test_no_institution_no_fid(self):
        config = OfxConfig(os.path.join("fixtures", "ofxclient.ini"))
        run(
            [
                os.path.join("fixtures", "no-institution.ofx"),
                "-l",
                os.path.join("fixtures", "empty.lgr"),
                "-a",
                "Assets:Savings:Foo",
            ],
            config,
        )

    def test_no_institution(self):
        ofxpath = os.path.join("fixtures", "no-institution.ofx")
        sync = OfxSynchronizer(self.lgr)
        ofx = OfxSynchronizer.parse_file(ofxpath)
        txns = sync.filter(ofx.account.statement.transactions, ofx.account.account_id)
        self.assertEqual(len(txns), 3)

    @raises(EmptyInstitutionException)
    def test_no_institution_no_accountname(self):
        ofxpath = os.path.join("fixtures", "no-institution.ofx")
        ofx = OfxSynchronizer.parse_file(ofxpath)
        OfxConverter(account=ofx.account, name=None)

    def test_apostrophe(self):
        ofxpath = os.path.join("fixtures", "apostrophe.ofx")
        ofx = OfxSynchronizer.parse_file(ofxpath)
        sync = OfxSynchronizer(self.lgr)
        txns = sync.filter(ofx.account.statement.transactions, ofx.account.account_id)
        self.assertEqual(len(txns), 1)

    def test_one_settleDate(self):
        ofxpath = os.path.join("fixtures", "fidelity-one-dtsettle.ofx")
        ofx = OfxSynchronizer.parse_file(ofxpath)
        sync = OfxSynchronizer(self.lgr)
        txns = sync.filter(ofx.account.statement.transactions, ofx.account.account_id)
        self.assertEqual(len(txns), 17)

    def test_accented_characters_latin1(self):
        ofxpath = os.path.join("fixtures", "accented_characters_latin1.ofx")
        ofx = OfxSynchronizer.parse_file(ofxpath)
        sync = OfxSynchronizer(self.lgr)
        txns = sync.filter(ofx.account.statement.transactions, ofx.account.account_id)
        converter = OfxConverter(account=ofx.account, name="Foo")
        self.assertEqual(converter.format_payee(txns[0]), "Virement Interac à: Jean")
        self.assertEqual(len(txns), 1)


@attr("hledger")
class TestWeirdOfxHledger(TestCase, WeirdOfxTest):
    def setUp(self):
        self.lgr = HLedger(os.path.join("fixtures", "empty.lgr"))


@attr("ledger")
class TestWeirdOfxLedger(TestCase, WeirdOfxTest):
    def setUp(self):
        self.lgr = Ledger(os.path.join("fixtures", "empty.lgr"), no_pipe=True)


@attr("ledger-python")
class TestWeirdOfxLedgerPython(TestCase, WeirdOfxTest):
    def setUp(self):
        self.lgr = LedgerPython(os.path.join("fixtures", "empty.lgr"))
