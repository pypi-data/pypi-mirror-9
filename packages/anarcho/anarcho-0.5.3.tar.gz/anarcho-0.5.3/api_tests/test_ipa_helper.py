from unittest import TestCase
from anarcho import ipa_helper

__author__ = 'NikolayRudenko'

class IpaHelperTest(TestCase):

    def setUp(self):
        pass

    def test_ipa_parsing(self):
        ipa_helper.parse_ipa("/Users/NikolayRudenko/Documents/ios.ipa")
        ipa_helper.parse_ipa("/Users/NikolayRudenko/Documents/ios2.ipa")
        ipa_helper.parse_ipa("/Users/NikolayRudenko/Documents/ios3.ipa")