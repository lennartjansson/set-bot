import itertools
import random

def get_full_deck():
    """
    Returns a deck of 81 set cards, where each card is a 4-tuple of integers
    0, 1, or 2
    """
    return [
        (a,b,c,d)
        for a in range(3)
        for b in range(3)
        for c in range(3)
        for d in range(3)
    ]

def get_shuffled_deck():
    deck = get_full_deck()
    random.shuffle(deck)
    return deck

def is_set(c1, c2, c3):
    return (
        (c1[0] + c2[0] + c3[0]) % 3 == 0 and
        (c1[1] + c2[1] + c3[1]) % 3 == 0 and
        (c1[2] + c2[2] + c3[2]) % 3 == 0 and
        (c1[3] + c2[3] + c3[3]) % 3 == 0
    )

def third_card_to_make_set(c1, c2):
    def f(a, b):
        s = (a + b) % 3
        return [0, 2, 1][s]
    return (
        f(c1[0], c2[0]),
        f(c1[1], c2[1]),
        f(c1[2], c2[2]),
        f(c1[3], c2[3]),
    )

def find_set(cards):
    set_of_cards = set(cards)
    pairs = list(itertools.combinations(cards, 2))
    third_cards = [third_card_to_make_set(*pair) for pair in pairs]
    for pair, third_card in zip(pairs, third_cards):
        if third_card in set_of_cards:
            return [pair[0], pair[1], third_card]
    return None

def make_initial_deal():
    deck = get_shuffled_deck()
    board = deck[:12]
    remaining_deck = deck[12:]
    return (board, remaining_deck)

def deal_more_cards(board, deck):
    if len(deck) == 0:
        return (board, [])
    else:
        return (board + deck[:3], deck[3:])

def letter_codes_to_cards(board, letter_codes):
    if type(letter_codes) != unicode and type(letter_codes) != str:
        return 'not a string'
    if len(letter_codes) != 3:
        return 'not three letters'
    letter_codes = list(letter_codes.upper())
    try:
        selected_cards = [
            board[ord(code) - ord('A')]
            for code in letter_codes
        ]
        return selected_cards
    except IndexError:
        return 'index out of range'

def remove_cards_from_board(board, cards):
    return [None if card in cards else card for card in board]

def coalesce_empty_spaces(board):
    return [c for c in board if c != None]

def deal_cards_into_empty_spaces(board, deck):
    if len(deck) == 0:
        return [card for card in board if card != None]
    j = 0
    for i in xrange(len(board)):
        if board[i] == None:
            board[i] = deck[j]
            j += 1
    deck = deck[j:]
    return (board, deck)

def is_game_over(board, deck):
    a_set = find_set(card for card in board if card != None)
    if a_set:
        return False
    if len(deck) > 0:
        return False
    return True

def card_to_card_name(c):
    numbers = ['One', 'Two', 'Three']
    colors = ['Red', 'Green', 'Purple']
    shadings = ['Solid', 'Shaded', 'Hollow']
    shapes = ['Squiggle', 'Oval', 'Diamond']
    return '{}{}{}{}'.format(
        numbers[c[0]],
        colors[c[1]],
        shadings[c[2]],
        shapes[c[3]],
    )

def board_to_names(board):
    return [
        card_to_card_name(c) for c in board if c is not None
    ]

# deck = get_shuffled_deck()
# board = deck[:12]
# deck = deck[12:]
# print board
# print len(deck)
# a_set = find_set(board)
# if a_set:
#     print a_set
#     board = remove_cards_from_board(board, a_set)
#     print board
#     (board, deck) = deal_cards_into_empty_spaces(board, deck)
#     print board
#     print len(deck)
# print deck[:12]
# print find_set(deck[:12])
# print letter_codes_to_cards(deck[:12], 'ace')
# print is_set(*letter_codes_to_cards(deck[:12], 'ace'))
# print is_set(*find_set(deck[:12]))
