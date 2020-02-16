'''EquiPy
------

Provides
    1. A set object containing cards from a traditional 52-card deck
'''
import numpy as np 

def _gen_deck():
    '''Generate the set containing a deck of cards'''
    values = {str(n) for n in range(2, 10)}.union({'A', 'T', 'J', 'Q', 'K'})
    suits = {'s', 'h', 'd', 'c'}
    deck = {''.join([value, suit]) for value in values for suit in suits}
    return deck

def _str_to_set(cards_str):
    '''Change a string of cards to a set of cards'''
    deck = _gen_deck()
    if len(cards_str) % 2 != 0:
        raise ValueError('Invalid Cards String')
    cards_set = set()
    for i in range(int(len(cards_str)/2)):
        if not cards_str[2*i:2*i+2] in deck:
            raise ValueError('Invalid Cards String')
        cards_set.add(cards_str[2*i:2*i+2])
    return cards_set

def _valid_set(cards_set):
    '''Check if a set of cars are valid'''
    deck = _gen_deck()
    for card in cards_set:
        if not card in deck:
            raise ValueError('Invalid Cards Set')
    return True

def _gen_values(cards):
    '''Create dictionary with values as keys and frozensets of
suits as values'''
    values = {}
    for card in cards:
        if card[0] in values:
            values[card[0]] = values[card[0]].union(frozenset([card[1]]))
        else:
            values[card[0]] = frozenset([card[1]])
    return values

def _gen_suits(cards):
    '''Create a dictionary with suits as keys and frozensets of
values as values'''
    suits = {}
    for card in cards:
        if card[1] in suits:
            suits[card[1]] = suits[card[1]].union(frozenset([card[0]]))
        else:
            suits[card[1]] = frozenset([card[0]])
    return suits

class Cards:
    '''Cards(cards)

A set object representing a group of cards.

Parameters
----------

cards : set of strings or a string
    Group of cards.

Attributes
----------

cards : set of strings
    All cards represented as 'ValueSuit'.
values : dict of frozen sets
    All existing card values are stored as keys and their associated
    existing suits are stored together as frozenset values.
suits : dict of frozen sets
    All existing card suits are stored as keys and their associated
    existing values are stored together as frozenset values.

Examples
--------
>>> cards = {'2c', '4s'}
>>> C = Cards(cards)
>>> print(C)
2c4s'''
    def __init__(self, cards):
        if isinstance(cards, str):
            cards = _str_to_set(cards)
        _valid_set(cards)
        self.cards = cards
        self.values = _gen_values(cards)
        self.suits = _gen_suits(cards)
    def __str__(self):
        cards_str = ''
        for card in self.cards:
            cards_str = ''.join([cards_str, card])
        return cards_str

class Hand(Cards):
    '''Hand(hand)

A set object representing a Texas Hold'em hand.

Parameters
----------

hand : set of strings or string
    Group of two cards.

Attributes
----------

hand : set of strings
    All cards represented as 'ValueSuit'
values : dict of frozen sets
    All existing card values are stored as keys and their associated
    existing suits are stored together as frozenset values.
suits : dict of frozen sets
    All existing card suits are stored as keys and their associated
    existing values are stored together as frozenset values.
pair : bool
    Are the values of the hand paired.
suited : bool
    Are the suited of the hand the same.
connected : bool
    Are the values of the hand one apart from each other.

Examples
--------
>>> hand = {'Kh', 'Kd'}
>>> H = Hand(hand)
>>> print(H)
Hand: KdKh
Pair: True
Suited: False
Connected: False
'''
    @staticmethod
    def _pair(values):
        '''Check if two cards are a pair'''
        if len(values) == 1:
            return True
        return False
    @staticmethod
    def _suited(suits):
        '''Check if two cards are suited'''
        if len(suits) == 1:
            return True
        return False
    @staticmethod
    def _connected(cards):
        '''Check if two cards are connectors'''
        values = ['A'] + [str(n) for n in range(2, 10)] + ['T', 'J', 'Q', 'K', 'A']
        connectors = set()
        for i in range(13):
            connectors.add(frozenset(values[i:i+2]))
        return {card[0] for card in cards} in connectors
    def __init__(self, hand):
        if isinstance(hand, str):
            hand = _str_to_set(hand)
        _valid_set(hand)
        if len(hand) != 2:
            raise ValueError('Invalid Hand')
        Cards.__init__(self, hand)
        self.hand = self.cards
        self.pair = self._pair(self.values)
        self.suited = self._suited(self.suits)
        self.connected = self._connected(self.cards)
    def __str__(self):
        return ''.join(['Hand: ', Cards.__str__(self), 
                        '\n', 'Pair: ', str(self.pair), 
                        '\n', 'Suited: ', str(self.suited),
                        '\n', 'Connected: ', str(self.connected)])

def _fill_hand(values, dead_cards, n):
    '''Fill a hand with the best remaining cards'''
    all_values = ['A', 'K', 'Q', 'J', 'T'] + [str(n) for n in range(9, 1, -1)]
    for value in all_values:
        if value in values:
            for suit in values[value]:
                card = ''.join([value, suit])
                if not card in dead_cards:
                    dead_cards.add(card)
                    n = n - 1
                    if n == 0:
                        return dead_cards
    return dead_cards

def _straight_flush(HB):
    '''Detect a straight flush in a HBoard data structure'''
    if HB.pflush and HB.pstraight:
        psuit = HB.pflush[0].lower()
        pvalues = ['A', 'K', 'Q', 'J', 'T'] + [str(n) for n in range(9, 1, -1)] + ['A']
        pcards = [''.join([value, psuit]) for value in pvalues]
        pstraights = [pcards[i:i+5] for i in range(10)]
        for straight in pstraights:
            if set(straight).issubset(HB.cards):
                made_straight_flush = set(straight)
                return made_straight_flush
    return False

def _quads(HB):
    '''Detect a straight flush in a HBoard data structure'''
    all_suits = {'s', 'h', 'd', 'c'}
    for value in HB.values:
        if len(HB.values.get(value, set())) == 4:
            made_quads = {''.join([value, suit]) for suit in all_suits}
            best_hand = _fill_hand(HB.values, made_quads, 1)
            return best_hand
    return False

def _full_house(HB):
    '''Detect a full house in a HBoard data structure'''
    all_values = ['A', 'K', 'Q', 'J', 'T'] + [str(n) for n in range(9, 1, -1)]
    for v1 in all_values:
        if len(HB.values.get(v1, set())) == 3:
            for v2 in all_values:
                if len(HB.values.get(v2, set())) >= 2 and v2 != v1:
                    trips = {''.join([v1, suit]) for suit in HB.values[v1]}
                    pair = {''.join([v2, suit]) for suit in np.random.choice(np.array(list(HB.values[v2])), 2, replace=False)}
                    made_full_house = trips.union(pair)
                    return made_full_house
    return False

def _flush(HB):
    '''Detect a flush in a HBoard data structure'''
    all_values = ['A', 'K', 'Q', 'J', 'T'] + [str(n) for n in range(9, 1, -1)]
    for suit in HB.suits:
        if len(HB.suits[suit]) >= 5:
            best_flush = set()
            for value in all_values:
                if value in HB.suits[suit]:
                    best_flush.add(''.join([value, suit]))
                if len(best_flush) == 5:
                    break
            return best_flush
    return False

def _straight(HB):
    '''Detect a straight in a HBoard data structure'''
    for straight_str in HB.pstraight:
        straight_list = [value for value in straight_str]
        if set(straight_list).issubset(set(HB.values.keys())):
            best_straight = {''.join([value, np.random.choice(np.array(list(HB.values[value])), 1)[0]]) for value in straight_list}
            return best_straight
    return False

def _trips(HB):
    '''Detect a three of a kind in a HBoard data structure'''
    all_values = ['A', 'K', 'Q', 'J', 'T'] + [str(n) for n in range(9, 1, -1)]
    for value in all_values:
        if len(HB.values.get(value, set())) == 3:
            trips = {''.join([value, suit]) for suit in HB.values[value]}
            best_hand = _fill_hand(HB.values, trips, 2)
            return best_hand
    return False

def _two_pair(HB):
    '''Detect a two pair in a HBoard data structure'''
    all_values = ['A', 'K', 'Q', 'J', 'T'] + [str(n) for n in range(9, 1, -1)]
    for v1 in all_values:
        if len(HB.values.get(v1, set())) == 2:
            for v2 in all_values:
                if len(HB.values.get(v2, set())) == 2 and v2 != v1:
                    two_pair = set()
                    for suit in HB.values[v1]:
                        two_pair.add(''.join([v1, suit]))
                    for suit in HB.values[v2]:
                        two_pair.add(''.join([v2, suit]))
                    best_hand = _fill_hand(HB.values, two_pair, 1)
                    return best_hand
    return False

def _one_pair(HB):
    '''Detect a pair in a HBoard data strucuture'''
    all_values = ['A', 'K', 'Q', 'J', 'T'] + [str(n) for n in range(9, 1, -1)]
    for value in all_values:
        if len(HB.values.get(value, set())) == 2:
            pair = {''.join([value, suit]) for suit in HB.values[value]}
            best_hand = _fill_hand(HB.values, pair, 3)
            return best_hand
    return False

def _best_hand(HB):
    phands = {_straight_flush:'Straight Flush',
              _quads:'Four of a Kind',
              _full_house:'Full House', 
              _flush:'Flush', 
              _straight:'Straight', 
              _trips:'Three of a Kind', 
              _two_pair:'Two Pair', 
              _one_pair:'Pair'}
    for func in phands:
        if func(HB):
            return func(HB), phands[func] 
    best_hand = _fill_hand(HB.values, set(), 5)
    return best_hand, 'none'

def _formatter(prefix, cards):
    '''__str__ method formatter'''
    string = prefix
    for cards in cards:
        string = ''.join([string, cards])
    return string

class HBoard(Hand):
    '''HBoard(hand, flop, turn=set(), river=set())

A set object representing a Texas Hold'em board and hand.

Parameters
----------

hand : set of strings or string
    Group of two cards.
flop : set of strings or string
    Group of three cards.
turn : set of strings or string, optional
    Group of one card.
river : set of strings or string, optional
    Group of one card.

Attributes
----------

cards : set of strings
    All cards represented as 'ValueSuit'
values : dict of frozen sets
    All existing card values are stored as keys and their associated
    existing suits are stored together as frozenset values.
suits : dict of frozen sets
    All existing card suits are stored as keys and their associated
    existing values are stored together as frozenset values.
hand : set of strings
    All cards in the hand.
pair : bool
    Are the values of the hand paired.
suited : bool
    Are the suited of the hand the same.
connected : bool
    Are the values of the hand one apart from each other.
flop : set of strings
    All cards in the flop.
turn : set of strings
    All cards in the turn.
river : set of strings
    All cards in the river.
board : set of strings
    All cards from the flop, turn, and river.
pstraight : list of strings
    All sequences of possible straights based on the board cards only.
pflush : string
    The suit for a possible flush based on the board cards only.
best_hand : set of strings
    The best 5 card hand out of all existing cards.
best_hand_type : string
    The hand category of the best 5 card hand.

Examples
--------
>>> hand = {'Td', 'Kh'}
>>> flop = {'5h', '9c', '7d'}
>>> turn = {'Js'}
>>> river = {'Qh'}
>>> HB = HBoard(hand, flop, turn, river)
>>> print(H)
Hand: TdKh
Pair: False
Suited: False
Connected: False
Flop: 5h9c7d
Turn: Js
River: Qh
Potential Straights: KQJT9 QJT98 JT987 98765
Potential Flush Suit: none
Best Hand: KhJsTdQh9c (Straight)
'''
    @staticmethod
    def _pstraight(board):
        '''Check if a board has enough for a potential straight'''
        all_values = ['A', 'K', 'Q', 'J', 'T'] + [str(n) for n in range(9, 1, -1)] + ['A']
        all_straights = [all_values[i:i+5] for i in range(10)]
        possible_straights = []
        values = _gen_values(board)
        values_set = {value for value in values}
        for straight in all_straights:
            if len(values_set.intersection(set(straight))) >= 3:
                possible_straights.append(straight)
        possible_straights = [''.join(values) for values in possible_straights]
        return possible_straights
    @staticmethod
    def _pflush(board):
        '''Check if a board has enough of one suit to make a potential flush'''
        suits = _gen_suits(board)
        suit_names = {'s':'Spades', 'h':'Hearts', 'd':'Diamonds', 'c':'Clubs'}
        for suit in suits:
            if len(suits[suit]) >= 3:
                return suit_names[suit]
        return False
    def __init__(self, hand, flop, turn=set(), river=set()):
        if isinstance(hand, str):
            hand = _str_to_set(hand)
        if isinstance(flop, str):
            flop = _str_to_set(flop)
        _valid_set(hand.union(flop))
        Hand.__init__(self, hand)
        cards = hand.union(flop)
        board = flop
        if turn:
            if isinstance(turn, str):
                turn = _str_to_set(turn)
            _valid_set(turn)
            cards = cards.union(turn)
            board = board.union(turn)
            if river:
                if isinstance(river, str):
                    river = _str_to_set(river)
                _valid_set(river)
                cards = cards.union(river)
                board = board.union(river)
        Cards.__init__(self, cards)
        self.flop = flop
        self.turn = turn
        self.river = river
        self.board = board
        self.pstraight = self._pstraight(board)
        self.pflush = self._pflush(board)
        self.best_hand, self.best_hand_type = _best_hand(self)
    def __str__(self):
        hand = _formatter('Hand: ', self.hand)
        flop = _formatter('Flop: ', self.flop)
        turn = _formatter('Turn: ', self.turn)
        river = _formatter('River: ', self.river)
        pstraights = 'Potential Straights: '
        if self.pstraight:
            for straight in self.pstraight:
                pstraights = ''.join([pstraights, straight, ' '])
        else:
            pstraights = ''.join([pstraights, 'none'])
        pflush = 'Potential Flush Suit: '
        if self.pflush:
            pflush = ''.join([pflush, self.pflush])
        else:
            pflush = ''.join([pflush, 'none'])
        best_hand = 'Best Hand: '
        for card in self.best_hand:
            best_hand = ''.join([best_hand, card])
        best_hand = ''.join([best_hand, ' (', self.best_hand_type, ')'])
        return ''.join([hand,
                        '\n', 'Pair: ', str(self.pair), 
                        '\n', 'Suited: ', str(self.suited),
                        '\n', 'Connected: ', str(self.connected),
                        '\n', flop,
                        '\n', turn,
                        '\n', river,
                        '\n', pstraights,
                        '\n', pflush,
                        '\n', best_hand])

if __name__ == '__main__':
    hand = hand = {'Kh', 'Td'}
    C = Cards(hand)
    print(C)
    print()

    H = Hand(hand)
    print(H)
    print()

    flop = {'5h', '7d', '9c'}
    turn = {'Js'}
    river = {'Qh'}
    B = HBoard(hand, flop, turn, river)
    print(B)