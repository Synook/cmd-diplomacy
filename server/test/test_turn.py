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
        self.board.set_unit('1', 'A')

    def tearDown(self):
        self.board.reset()

class TurnParserTestCase(TurnTestCase):
    def test_basic_move(self):
        self.assertEqual(self.turn.parse_order('1', 'A A-B'), {
            'type': 'move',
            'unit_type': 'A',
            'unit': 'A',
            'dst': 'B'
        })

    def test_no_unit(self):
        self.assertEqual(self.turn.parse_order('1', 'A B-A'), None)

    def test_wrong_unit_type(self):
        self.assertEqual(self.turn.parse_order('1', 'F A-B'), None)

    def test_wrong_nation(self):
        self.assertEqual(self.turn.parse_order('2', 'A A-B'), None)

class TurnExecuteTestCase(TurnTestCase):
    def test_basic_move(self):
        self.board.add_move('1901-S', '1', 'A A-B')
        self.turn.do_turn('1901-S')
        self.assertEqual(self.board.get_territory('A')['unit'], None)
        self.assertEqual(self.board.get_territory('B')['unit'], '1')

    def test_blocked_move(self):
        pass

    def test_vacating_move(self):
        self.board.set_unit('2', 'B')
        self.board.add_move('1901-S', '1', 'A A-B')
        self.board.add_move('1901-S', '2', 'A B-C')
        self.turn.do_turn('1901-S')
        self.assertEqual(self.board.get_territory('A')['unit'], None)
        self.assertEqual(self.board.get_territory('B')['unit'], '1')
        self.assertEqual(self.board.get_territory('C')['unit'], '2')



    # swap


if __name__ == '__main__':
    unittest.main()
