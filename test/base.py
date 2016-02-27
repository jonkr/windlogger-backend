import unittest

import db
import datetime


class TestBase(unittest.TestCase):

    def setUp(self):
        db.init(db_uri='sqlite://')
        #db.init(db_uri='sqlite:///data.db')

    def tearDown(self):
        db.clear()
        db.remove_session()

    @property
    def utc_now(self):
        return datetime.datetime.utcnow()

    @property
    def now(self):
        return datetime.datetime.now()
