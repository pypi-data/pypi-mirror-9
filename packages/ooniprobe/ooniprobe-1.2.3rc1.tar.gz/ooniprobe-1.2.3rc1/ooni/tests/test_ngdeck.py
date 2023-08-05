from twisted.trial import unittest
from ooni.ngdeck import NgDeck


class TestNgDeck(unittest.TestCase):
    deck_path = ""

    def test_run_deck(self):
        deck = NgDeck(self.deck_path)
        deck.run()
