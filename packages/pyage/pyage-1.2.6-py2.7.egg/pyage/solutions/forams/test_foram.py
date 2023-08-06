from unittest import TestCase
from pyage.solutions.forams.foram import Foram

__author__ = 'makz'


class TestForam(TestCase):
    def test_step(self):
        foram = Foram()
        foram.step()