# -*- coding: utf-8 -*-
"""
  ..  .module:: trellopy
      :synopsis: The "main" module. Has a Controller class that serves as
      the first layer of interaction.

    Actions which can be performed on each item include:
    Boards can be:
        ✓created,
        ✓renamed,
        ✓archived
    Lists can be:
        ✓created,
        ✓archived,
        ✓renamed,
        ✓reordered
    Cards can be:
        ✓created,
        ✓archived,
        ✓renamed,
        ✓reordered within a list,
        ✓moved to another list
    Members can be:
        ✓created,
        ✓renamed,
        ✓archived,
        ✓assigned to cards
    Labels can be:
        ✓renamed,
        ✓assigned to cards,
        ✓One label per card
"""

from boards import Board
from members import Member
from backend import Operator


class Controller(object):
    def __init__(self):
        """
        Initializes a Controller class. It consists of a single *_operator*
        instance: ::

          self._operator = Operator()
        """
        self._operator = Operator()

    def new_board(self, board_name):
        """
        Create a new board with name *board_name*.

        :param board_name: The name you want the board to have.
        :returns: A Board class, with name attribute *board_name*.
        """
        return Board(board_name)

    def get_board(self, board_name):
        """
        Get the board that has the name *board_name*.

        :param board_name: The name of the board you want to get.
        :returns: A Board class, with Board.board populated with board data.
        """
        board_data = self._operator.get_board(board_name)
        return Board(board_name, board_data)

    def show_boards(self):
        """
        Show all the boards in the database.

        :param: Takes no arguments, call it like it is.
        :returns: A somewhat human-friendly listing of all boards.
        """
        everything = self._operator.gimme_everything()
        for each in everything:
            print "Board Name:", each['name']
            print "Archived:  ", each['archived']
            all_lists = each['lists']
            if all_lists:
                for single in all_lists:
                    print "  List Name:", single['name']
            # print "Lists:     ", each['lists']

    def new_member(self, member_name):
        """
        Add a new member with name *member_name*

        :param member_name: The name of the member.
        :returns: A Member class, with Members.person populated with name.
        """
        return Member(member_name)

    def get_member(self, member_name):
        """
        Get existing member with name *member_name*

        :param member_name: The name of the member.
        :returns: A Member class, with Members.person populated with name.
        """
        return Member(member_name)

    def show_members(self):
        """
        Show all members in the database.

        :param: Takes no arguments, call it like it is.
        :returns: A somewhat human-friendly listing of all members.
        """
        everybody = self._operator.gimme_everybody()
        for body in everybody:
            print body
