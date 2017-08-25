from __future__ import print_function
from __future__ import unicode_literals

import collections
import re
import sys

from rtmbot.core import Plugin

import Set
import BoardGenerator


BOT_NAME = 'set-bot'
CHANNEL = '#set-bot-debug'


Model = collections.namedtuple(
    'SetBotModel',
    [
        'bot_user_id',
        'is_playing',
        'board',
        'deck',
        'can_call_sets',
    ]
)


def chat_message(s):
    return (
        'chat.postMessage',
        {'text': s}
    )

def set_board_image_upload(board):
    board_names = Set.board_to_names(board)
    board_image = BoardGenerator.generate_board(board_names)
    return (
        'files.upload',
        {
            'title': 'Current board',
            'name': 'board.png',
            'file': board_image,
            'channels': CHANNEL,
        }
    )


def is_start_game_message(user_id, message):
    return (
        message['type'] == 'message' and
        (
            'set-bot' in message['text'].lower() or
            user_id in message['text']
        ) and
        'start' in message['text'].lower()
    )

def is_set_call_message(message):
    return (
        message['type'] == 'message' and
        bool(re.match('[a-z]{3}', message['text'].lower().strip())) and
        len(set(message['text'].lower().strip())) == 3
    )

def is_no_sets_call_message(message):
    return (
        message['type'] == 'message' and
        (
            'no set' in message['text'].lower() or
            message['text'].strip().lower() == 'v'
        )
    )

def is_self_message(message, model):
    return message['type'] == 'message' and message['user'] == model.bot_user_id


def update_by_self_message(message, model):
    # Ignore messages that come from the bot itself, so that we don't get in
    # infinite loops with "no set" triggering itself.
    #
    # However, do listen for own file uploads, because we want to open the
    # floor for calling sets only after the next board image appears in the
    # chat.
    if message['subtype'] == 'file_share':
        return (
            Model._replace(model, can_call_sets=True), []
        )
    else:
        return (model, [])


def update_while_playing(message, model):
    if is_start_game_message(model.bot_user_id, message):
        return (
            model,
            [chat_message("We're already in the middle of a game!")]
        )

    elif is_set_call_message(message) and model.can_call_sets:
        message_text = message['text']
        cards_called_in = Set.letter_codes_to_cards(model.board, message_text)

        if Set.is_set(*cards_called_in):
            board = Set.remove_cards_from_board(model.board, cards_called_in)

            if Set.is_game_over(board, model.deck):
                return (
                    Model._replace(
                        model,
                        board=board, deck=[],
                        is_playing=False, can_call_sets=False,
                    ),
                    [
                        chat_message("SET called by <@{}>!".format(
                            message['user']
                        )), chat_message(
                            "Game over! Type `set-bot start` to start a new game."
                        )
                    ]
                )

            else:
                # Game not over: there are still cards in the deck or sets
                # remaining on the board.
                if len(board) > 12:
                    board = Set.coalesce_empty_spaces(board)
                    deck = model.deck
                elif len(model.deck) > 0:
                    board, deck = Set.deal_cards_into_empty_spaces(
                        board, model.deck)
                else:
                    board = Set.coalesce_empty_spaces(board)
                    deck = []

                if Set.is_game_over(board, deck):
                    return (
                        Model._replace(
                            model,
                            board=board, deck=[],
                            is_playing=False, can_call_sets=False,
                        ),
                        [
                            chat_message("SET called by <@{}>!".format(
                                message['user']
                            )), chat_message(
                                "Game over! Type `set-bot start` to start a new game."
                            )
                        ]
                    )
                else:
                    return (
                        Model._replace(
                            model,
                            board=board, deck=deck, can_call_sets=False,
                        ),
                        [
                            chat_message(
                                'SET called by <@{}>!'.format(message['user'])),
                            set_board_image_upload(board),
                        ]
                    )

        else:
            return (
                model,
                [chat_message(
                    "`{}` is not a set.".format(message_text)
                )]
            )

    elif is_no_sets_call_message(message) and model.can_call_sets:
        a_set = Set.find_set(model.board)

        if a_set:
            return (
                model,
                [chat_message("Nope, there's at least one set here.")]
            )
        else:
            board, deck = Set.deal_more_cards(model.board, model.deck)
            if Set.is_game_over(board, deck):
                return (
                    Model._replace(
                        model,
                        board=board, deck=[],
                        is_playing=False, can_call_sets=False,
                    ),
                    [
                        chat_message(
                            "Game over! Type `set-bot start` to start a new game."
                        )
                    ]
                )
            else:
                return (
                    Model._replace(model, board=board, deck=deck),
                    [
                        chat_message("Dealing more cards..."),
                        set_board_image_upload(board),
                    ]
                )

    return (model, [])


def start_game_update(message, model):
    board, deck = Set.make_initial_deal()
    new_model = Model._replace(
        model,
        is_playing=True,
        board=board,
        deck=deck,
    )
    return (
        new_model,
        [
            chat_message(
                'Starting a game of SET! Type a three letter code like "abc" ' +
                'to call in a set with those corresponding cards. If you ' +
                'think there are no sets, type "no sets".'
            ),
            set_board_image_upload(board),
        ]
    )


def update(message, model):
    """
    Update function, part of a model-update pattern

    Parameters:
      - incoming message: slack data dict
      - model: previous state, type Model

    Returns:
      tuple of (
        <new state> ,
        list of tuples ( <slack method, string> , <arguments as dict> )
      )
    """

    if is_self_message(message, model):
        # Generally, ignore messages that come from the bot itself
        return update_by_self_message(message, model)

    elif model.is_playing:
        return update_while_playing(message, model)

    else:
        # Not in the middle of a game
        if is_start_game_message(model.bot_user_id, message):
            return start_game_update(message, model)

    return (model, [])


class SetBotPlugin(Plugin):
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(self, *args, **kwargs)

        my_user_id = None
        users_list_call_result = self.slack_client.api_call('users.list')
        if users_list_call_result.get('ok'):
            users = users_list_call_result.get('members')
            for user in users:
                if user.get('name') == BOT_NAME:
                    my_user_id = user.get('id')

        if not my_user_id:
            print('Could not fetch own user id')
            sys.exit(1)

        print('Set bot starting up. User ID is', my_user_id)
        self.slack_client.api_call("chat.postMessage", text='Hello, {}! Type `set-bot start` to begin a game.'.format(CHANNEL), channel=CHANNEL, username='set-bot')

        self.model = Model(
            bot_user_id=my_user_id,
            is_playing=False,
            board=[],
            deck=[],
            can_call_sets=False,
        )


    def process_message(self, data):
        current_state = self.model
        new_state, commands = update(data, current_state)
        print('transitioning to', new_state)
        print('executing commands', commands)
        for command in commands:
            if command[0] == 'chat.postMessage':
                command[1]['channel'] = CHANNEL
                command[1]['username'] = BOT_NAME
            self.slack_client.api_call(command[0], **command[1])
        self.model = new_state
