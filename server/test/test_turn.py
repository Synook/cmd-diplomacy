import sys
import unittest
from pymongo import MongoClient
sys.path.append('..')
import turn
import board

class TurnTestCase(unittest.TestCase):
    def setUp(self):
        self.db = MongoClient('localhost').test_diplomacy
        self.board = board.Board(self.db)
        self.turn = turn.Turn(self.db, None)

        self.board.add_territory('A')
        self.board.add_territory('B')
        self.board.add_territory('C')
        self.board.link('A', 'B')
        self.board.link('B', 'C')
        self.board.add_nation('1')
        self.board.add_nation('2')

    def tearDown(self):
        self.board.reset()

class TurnParserTestCase(TurnTestCase):
    def test_basic_move(self):
        self.board.set_unit('1', 'A')
        self.assertEqual(self.turn.parse_order('1', 'A A-B'), {
            'type': 'move',
            'unit_type': 'A',
            'unit': 'A',
            'dst': 'B'
        })

    def test_wrong_nation(self):
        self.board.set_unit('1', 'A')
        self.assertEqual(self.turn.parse_order('2', 'A A-B'), None)

if __name__ == '__main__':
    unittest.main()
