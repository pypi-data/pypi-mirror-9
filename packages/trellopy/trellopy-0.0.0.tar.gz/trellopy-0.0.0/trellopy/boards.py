from backend import Operator
from members import Member


class Board(object):
    def __init__(self, name, data=None):
        """
            Initializes an Operator instance. The entire board is represented
            as a dict with the following attributes and defaults: ::

                self.board = {}
                self.board['name']        : Name of the board
                self.board['lists']       : initialized as "None"
                self.board['archived']    : initialized as "False"
                self.board['labels']      : initialized as "None"

            :param name: Name of the board
            :type name: str.
            :param data: Populate the board with data
            :type data: dict.

        """
        self._operator = Operator()
        if not self.in_database(name):
            self.board = {}
            self.board['name'] = name
            self.board['lists'] = None
            self.board['archived'] = False
            self.board['labels'] = None
            self._operator.save_board(self.board)
        elif not data:
            self.board = self._operator.get_board(name)
        elif data:
            self.board = data

    def archive(self):
        """ Sets the archived flag to True. This method updates the board.

            :param None: Call it like it is.
        """
        self.board['archived'] = True
        self._operator.update_board(self.board)

    def rename(self, new_name):
        """ Renames the board. This method updates the board.

            :param new_name: The new name of board.
            :type new_name: str.
        """
        old_name = self.board['name']
        self.board['name'] = new_name
        self._operator.update_board(self.board, old_name)

    def add_list(self, list_name):
        """ Add a list to the board. This method updates the board.

            :param list_name: Name of the list
            :type list_name: str.
            :returns: List as an instance of `BoardList`
        """
        if not self.board['lists']:
            self.board['lists'] = []
        parent_board = self.board['name']
        new_list_item = BoardList(board=parent_board, name=list_name)
        self.board['lists'].append(new_list_item.lizt)
        self._operator.update_board(self.board)
        return new_list_item

    def get_list(self, list_name):
        """ Get a list from the board

            :param list_name: Name of the list
            :type list_name: str.
            :returns: List as an instance of `BoardList`
        """
        for lizt in self.board['lists']:
            if lizt['name'] == list_name:
                list_from_dict = BoardList(from_dict=lizt)
                return list_from_dict

    def get_order(self):
        """ Get the order of the lists in board

            :param None: Call it like it is.
        """
        all_lists = self.board['lists']
        for each in all_lists:
            index = all_lists.index(each)
            print index, each['name']

    def reorder(self, new_order):
        """ Reorder the lists in the board.

            >>> board.reorder([2,4,5,1])

        :param new_order: A list of indices
        :type new_order: list.
        """
        if isinstance(new_order, list):
            all_lists = self.board['lists']
            if len(all_lists) == len(new_order):
                all_lists = [all_lists[idx] for idx in new_order]
                for each in all_lists:
                    index = all_lists.index(each)
                    print index, each['name']
                self.board['lists'] = all_lists
                self._operator.update_board(self.board)

    def add_label(self, label_name):
        """ Add a label to the board

        :param label_name: The name of label
        :type label_name: str.
        """
        if not self.board['labels']:
            self.board['labels'] = []
        if not len(self.board['labels']) >= 6:
            self.board['labels'].append(label_name)

    def rename_label(self, label, new_name):
        """ Rename the label on the board

        :param label: The original name of label
        :type label: str.
        :param new_name: The new name of label
        :type new_name: str.
        """
        if label in self.board['labels']:
            idx = self.board['labels'].index(label)
            self.board['labels'][idx] = new_name

    def in_database(self, name):
        """ Check if baord is already in the database

        :param name: Name of the board
        :type name: str.
        :returns: True if board exists, False if it does not.
        """
        return self._operator.get_board(name)

    def save(self):
        """ Update the board in dictionary. Call this function to update lists.
        """
        self._operator.update_board(self.board)


class BoardList(object):
    def __init__(self, from_dict=None, *tuples, **dicts):
        """
        Represents each list in a board. Cards tied to this list is
        implemented as a list of dicts. The list object itself is represented
        as a dict too. ::

            self.lizt = {}
            self.lizt['board']      : Board the list belongs to
            self.lizt['name']       : Name of the list
            self.lizt['cards']      : List of cards associated. Default is None
            self.lizt['archived']   : The archive flag. Default is False.

        :param from_dict: If the list is to be pre-populated from a dict.
        :type from_dict: dict.
        """
        self._operator = Operator()
        if not from_dict:
            self.lizt = {}
            self.lizt['board'] = dicts.get('board')
            self.lizt['name'] = dicts.get('name')
            self.lizt['cards'] = None
            self.lizt['archived'] = False
        if from_dict:
            self.lizt = from_dict

    def archive(self):
        """ Sets the value of key `archive` to True

        :param None: Call it like it is.
        """
        self.lizt['archived'] = True
        return self

    def rename(self, new_name):
        """ Sets the value of key name to `new_name` """
        old_name = self.lizt['name']
        self.lizt['name'] = new_name
        return self

    def add_card(self, card):
        """ Add a card to the list. If the card is of type string, a new
        card is created. If it is an instance of `BoardListCard` then a copy
        of it appended to the current list of cards.

        >>> list_one = board_one.get_list('Simplist')
        >>> list_two = board_two.get_list('Unlisted')
        >>> card_one = list_one.get_card('Simple Card')
        >>> list_two.add_card(card_one)
        >>> list_two.add_card('Another Card')

        :param card: A card instance or name of card
        :type card: str. or `BoardListCard`
        """
        if not self.lizt['cards']:
            self.lizt['cards'] = []
        new_card = None
        if isinstance(card, BoardListCard):
            new_card = card
        elif isinstance(card, str):
            new_card = BoardListCard(card)
        self.lizt['cards'].append(new_card.card)
        return new_card

    def get_card(self, card_name):
        """ Get a card from the list

            :param card_name: The name of card
            :type card_name: str.
            :returns: Instance of BoardListCard
        """
        if self.lizt['cards']:
            for card in self.lizt['cards']:
                if card['name'] == card_name:
                    return BoardListCard(card_name, data=card)

    def get_order(self):
        """ Get order of cards in list

            >>> sample_list.get_order()
            0 Card A
            1 Another Card
            2 Cardigan
            3 Red Card

        :param None: Call it like it is.
        :returns: An output of lists
        """
        all_cards = self.lizt['cards']
        for each in all_cards:
            index = all_cards.index(each)
            print index, each['name']

    def reorder(self, new_order):
        """ Reorder the cards in list

            :param new_order: New order of cards, as a list of indices.
            :type new_order: list.
        """
        if isinstance(new_order, list):
            all_cards = self.lizt['cards']
            if len(all_cards) == len(new_order):
                all_cards = [all_cards[idx] for idx in new_order]
                for each in all_cards:
                    index = all_cards.index(each)
                    print index, each['name']
                self.lizt['cards'] = all_cards

    def save(self):
        """ Save the list to the board """
        board = self._operator.get_board(self.lizt['board'])
        for each in board['lists']:
            if each['name'] == self.lizt['name']:
                each = self.lizt
        self._operator.update_board(board)


class BoardListCard(object):
    def __init__(self, name, data=None):
        """ Initializes the card as a dict. ::

            self.card  = {}
            self.card['name']       : Name of card
            self.card['archived']   : Archive flag.
                                      Default is False
            self.card['labeled']    : Label attached to card.
                                      Default is None
            self.card['assigned']   : List of members the card is assigned to.
                                      Default is None.

        :param name: Name of card
        :type name: str
        :param data: Data to be pre-populated
        :type data: dict
        """
        self.card = {}
        self.card['name'] = name
        self.card['archived'] = False
        self.card['assigned'] = None
        self.card['labeled'] = None
        if data:
            self.card = data

    def archive(self):
        """ Sets the value of key archived to True """
        self.card['archived'] = True

    def rename(self, new_name):
        """ Sets the value of key name to `new_name` """
        self.card['name'] = new_name
        return self

    def assign(self, member):
        """ Assign card to a member """
        if not self.card['assigned']:
            self.card['assigned'] = []
        if isinstance(member, Member):
            member_name = member.person['name']
            self.card.assigned.append(member_name)

    def label(self, label_name):
        """ Attach label to card """
        self.card['labeled'] = label_name
