import re

# processes a turn, producing a list of changes to the board
# uses recursive descent to resolve conflicts

class Turn(object):
    def __init__(self, db, log):
        self.db = db
        self.log = log

    def do_turn(self, turn):
        moves = self.db.move.find({'turn': turn})
        orders = []
        for move in moves:
            parsed = self.parse_order(move['nation'], move['order'])
            if parsed:
                orders.append(parsed)

        last_len = len(orders) + 1
        while len(orders) < last_len:
            last_len = len(orders)
            self.__successful_order(orders)

    def __successful_order(self, orders):
        # select move order
        i = 0
        while i < len(orders):
            order = orders[i]
            if order['type'] == 'move':
                break
        if i == len(orders):
            return

        self.__try_do_order(order, orders)

    def __try_do_order(self, order, orders):

        # loop until order is done or nothing is possible
        # actually more like loop by region
        checked = set()
        while True:
            # TODO: check if convoy

            # check for unit at dst
            unit_at_dst = False
            if self.db.territory.find({'shortname': order['dst'], 'unit': {'$ne': None}}):
                # check if target unit is moving away
                # if so, do that first (easier)
                for other in orders:
                    if other['unit'] == order['dst'] and other['dst'] not in checked:
                        checked.add(order['unit'])
                        order = other
                        continue
                unit_at_dst = True

            # check for winner at dst by support
            dst = order['dst']
            candidates = []
            best_candidate = None
            best_candidate_support = 1
            for other in orders:
                if other['dst'] == dst: # candidate
                    candidates.append(other)
                    support_score = self.__calc_support(other, orders)
                    if support_score > best_candidate_support:
                        best_candidate_support = support_score
                        best_candidate = other
                    elif support_score == best_candidate_support:
                        best_candidate = None

            # don't forget to check person at dst
            if unit_at_dst:
                support_score = self.__calc_support(dst, orders)
                if support_score >= best_candidate_support:
                    # unit as dst holds, no-one is moving
                    best_candidate = None

            # delete all candidates: no one else is moving
            for candidate in candidates:
                orders.remove(candidate)

            # execute winning order
            if best_candidate:
                self.__do_order(best_candidate)

            break

    def __calc_support(self, order, orders):
        support_score = 1
        for support in orders:
            add = 1
            if support['type'] == 'support' and (
                type(order) == dict and # support move
                support['target']['dst'] == order['dst'] and
                support['target']['unit'] == order['unit']
            ) or (
                type(order) == str and # support hold
                support['target']['dst'] == order and
                support['target']['unit'] == None
            ):
                # check for cutting
                for cutter in orders:
                    if cutter['type'] == 'move' and cutter['dst'] == support['unit']:
                        add = 0
                        break
            support_score += add
        return support_score

    # TODO: implement
    # MUST include call to try_do_order if about to displace to give a chance
    # for displaced unit to move, if there is an appropriate order. BUT check
    # for position swaps first.
    # BUT lift unit off board before calling try_do_order to allow for triangles
    # then place after the call returns. Maybe some way of moving it to the dest?
    # or it doesn't matter since existence check is done when parsing order.
    # Can just move, update DB then call.
    def __do_order(self, order):
        pass

    def debug(self, msg):
        print msg

    # (A|F) Abc(-Def| (S|C) (A|F) Abc-Def)
    # nationality markings not supported
    # TODO: coastal movement and two-coast support
    # maybe just entirely special support
    def parse_order(self, nation, order):
        try:
            split = re.split('\s+', order)
            result = {}

            result['unit_type'] = split[0]
            if result['unit_type'] not in ['A', 'F']:
                self.debug('not a unit type')
                return None

            if split[1].find('-') > -1:
                result['type'] = 'move'
                (result['unit'], result['dst']) = split[1].split('-')

            else:
                result['unit'] = split[1]
                result['target'] = {}
                result['target']['unit_type'] = split[3]
                if result['target']['unit_type'] not in ['A', 'F']:
                    self.debug('target not a unit type')
                    return None
                (result['target']['unit'], result['target']['dst']) = (
                    split[4].split('-') if split[4].find('-') > -1
                    else (None, split[4])
                )
                if not self.db.territory.find({
                    'shortname': result['target']['unit'],
                    'land': result['target']['unit_type'] == 'A'
                }).count():
                    # no unit to support/convoy
                    return None

                if split[2] == 'S':
                    if result['target']['unit'] and not self.__can_move_to(result['target']['unit_type'], result['target']['unit'], result['target']['dst']):
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
                    if not self.db.territory.find({'shortname': result['target']['dst'], land: True}):
                        # destination is not land
                        return None
                    if not self.db.territory.find({'shortname': result['unit'], land: False}):
                        # fleets on land cannot convoy
                        return None
                    result['type'] = 'convoy'

                else:
                    # invalid order type
                    return None

            if not self.db.territory.find({
                'unit': nation, 'shortname': result['unit'],
                'land': result['unit_type'] == 'A'
            }).count():
                self.debug('no such unit')
                return None

            return result
        except Exception as e:
            self.debug('malformed order '+ e.message)
            return None

    def __are_adjacent(self, a, b):
        return self.db.territory.find({'shortname': a, 'neighbors': b})

    def __can_move_to(self, type, a, b):
        return (
            # adjacent
            self.__are_adjacent(a, b) and (
                # army - b is land
                type == 'A' and self.db.territory.find({'shortname': b, 'land': True}) or
                # fleet - b is sea or coastal
                type == 'F' and self.db.territory.find({
                    'shortname': b,
                    '$or': {'coastal': True, 'land': False}
                })
            )
        )
