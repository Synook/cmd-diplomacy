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

        for a in ['La', 'Lb', 'Lc', 'Ld', 'Le']:
            self.board.add_territory(a)
        for a in ['Sa', 'Sb', 'Sc', 'Sd']:
            self.board.add_territory(a, land=False)

        for a in (
            ('La', 'Lb'), ('La', 'Ld'),
            ('Lb', 'Lc'), ('Lb', 'Ld')
        ):
            self.board.link(*a)

        self.board.link('Sb', 'Sc')
        self.board.link('Sb', 'Sd')

        self.board.linkcoast('Lb', 'Sa', 'N')
        self.board.linkcoast('Lc', 'Sa')
        self.board.linkcoast('Lb', 'Sb', 'S')
        self.board.linkcoast('Ld', 'Sb')
        self.board.linkcoast('Lc', 'Sb')
        self.board.linkcoast('Le', 'Sc')
        self.board.linkcoast('Ld', 'Sd')

        self.board.add_nation('1')
        self.board.add_nation('2')
        self.board.set_unit('1', 'La')

    def tearDown(self):
        self.board.reset()

class TurnParserTestCase(TurnTestCase):
    def test_basic_move(self):
        self.assertEqual(self.turn.parse_order('1', 'A La-Lb'), {
            'type': 'move',
            'unit_type': 'A',
            'unit': 'La',
            'dst': 'Lb'
        })

    def test_no_unit(self):
        self.assertEqual(self.turn.parse_order('1', 'A Lb-La'), None)

    def test_wrong_unit_type(self):
        self.assertEqual(self.turn.parse_order('1', 'F La-Lb'), None)

    def test_wrong_nation(self):
        self.assertEqual(self.turn.parse_order('2', 'A La-Lb'), None)

class TurnExecuteTestCase(TurnTestCase):
    def test_basic_move(self):
        self.board.add_move('1901-S', '1', 'A La-Lb')
        self.turn.do_turn('1901-S')
        self.assertEqual(self.board.get_territory('La')['unit'], None)
        self.assertEqual(self.board.get_territory('Lb')['unit'], '1')

    def test_blocked_move(self):
        pass

    def test_vacating_move(self):
        self.board.set_unit('2', 'Lb')
        self.board.add_move('1901-S', '1', 'A La-Lb')
        self.board.add_move('1901-S', '2', 'A Lb-Lc')
        self.turn.do_turn('1901-S')
        self.assertEqual(self.board.get_territory('La')['unit'], None)
        self.assertEqual(self.board.get_territory('Lb')['unit'], '1')
        self.assertEqual(self.board.get_territory('Lc')['unit'], '2')



    # swap


if __name__ == '__main__':
    unittest.main()
