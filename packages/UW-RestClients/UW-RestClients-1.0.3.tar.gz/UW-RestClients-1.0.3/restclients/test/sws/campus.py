from django.test import TestCase
from django.conf import settings
from restclients.sws.campus import get_all_campuses
from restclients.exceptions import DataFailureException

class SWSTestCampus(TestCase):

    def test_all_campuses(self):
        with self.settings(
                RESTCLIENTS_SWS_DAO_CLASS='restclients.dao_implementation.sws.File',
                RESTCLIENTS_PWS_DAO_CLASS='restclients.dao_implementation.pws.File'):

            campuses = get_all_campuses()

            self.assertEquals(len(campuses), 3)
