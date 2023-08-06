.. image:: https://travis-ci.org/mund/Trellopy.svg?branch=master
    :target: https://travis-ci.org/mund/Trellopy
.. image:: https://readthedocs.org/projects/trellopy/badge/?version=latest
    :target: https://readthedocs.org/projects/trellopy/?badge=latest
    :alt: Documentation Status


===============================
Trellopy
===============================

A Python mockup of Trello with CLI. Trello is a very popular (and powerful) todo-list / task board. 

* Free software: BSD license
* Documentation: https://trellopy.readthedocs.org.

Requirements
============
* PyMongo (and of course, MongoDB)
* Nose (for testing)

Example
========
>>> import trellopy
>>> controller = trellopy.Controller()
>>> board = controller.add_board('Board')
>>> list1 = board.add_list('List One')
>>> list2 = board.add_list('List Two')
>>> list3 = board.add_list('List Three')
>>> list4 = board.add_list('List Four')
>>> carda = list1.add_card('Card A')
>>> cardb = list1.add_card('Card B')
>>> cardc = list1.add_card('Card C')
>>> list2.add_card(carda)
>>> list3.rename('List 3')
>>> list4.archive()
>>> board.get_order()
>>> board.reorder([2,0,3,1])
>>> list1.get_order()
>>> list2.reorder([2,0,1])
>>> person = controller.new_member('Person')
