# processes a turn, producing a list of changes to the board
# uses recursive descent to resolve conflicts

class Turn(object):
    def __init__(db, log):
        self.db = db
        self.log = log

    def do_turn(turn):
        moves = self.db.move.find({'turn': turn})
        for move in moves:
            move['parsed'] = self.__parse_order(move['nation'], move['order'])

        while len(moves):


    # (A|F) Abc(-Def| (S|C) (A|F) Abc-Def)
    # nationality markings not supported
    def __parse_order(self, nation, order):
        try:
            split = re.split('\s+', move_str)
            result = {}

            result['unit_type'] = split[0]
            if result['unit_type'] not in ['A', 'F']:
                # not a unit type
                return None

            if split[1].indexOf('-') > -1:
                result['type'] = 'move'
                (result['unit'], result['dst']) = split[1].split('-')

            else:
                result['unit'] = split[1]
                result['target'] = {}
                result['target']['unit_type'] = split[3]
                if result['target']['unit_type'] not in ['A', 'F']:
                    # not a unit type
                    return None
                (result['target']['unit'], result['target']['dst']) = split[4].split('-')
                if not self.db.territory.find({
                    'shortname': result['target']['unit'],
                    'land': result['target']['unit_type'] == 'A'
                }).count():
                    # no unit to support/convoy
                    return None

                if split[2] == 'S':
                    if not self.__can_move_to(result['target']['unit_type'], result['target']['unit'], result['target']['dst']):
                        # supported unit cannot make move
                        return None
                    if not self.__can_move_to(result['unit_type'], result['unit'], result['target']['dst']):
                        # unit would not be able to make move
                        return None
                    result['type'] = 'support'
                elif split[2] == 'C':
                    if result['unit_type'] != 'F':
                        # only fleets can convoy
                        return None
                    if not db.territory.find({'shortname': result['target']['dst'], land: True}):
                        # destination is not land
                    result['type'] = 'convoy'

                else:
                    # invalid order type
                    return None

            if not self.db.territory.find({
                'unit': nation, 'shortname': result['unit'],
                'land': result['unit_type'] == 'A'
            }).count():
                # no such unit
                return None

            return result
        except:
            # malformed order
            return None

    def __are_adjacent(self, a, b):
        return self.db.territory.find({'shortname': a, 'neighbors': b}) and

    def __can_move_to(self, type, a, b):
        return (
            # adjacent
            self.__are_adjacent(a, b) and (
                # army - b is land
                type == 'A' and self.db.territory.find({'shortname': b, 'land': True}) or
                # fleet - b is sea or coastal
                type == 'F' and self.db.territory.find({'shortname': b, {
                    '$or': {'coastal': True, 'land': False}
                )
            )
        )
