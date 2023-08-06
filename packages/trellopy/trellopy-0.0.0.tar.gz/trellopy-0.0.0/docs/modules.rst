========
Modules
========
The main modules in this python package are:
  * trellopy.py - consisting of one Controller class
  * boards.py - consisting of one Board, BoardList and BoardListCard classs
  * members.py - consisting of one Member class
  * backend.py - consisting of one Operator class

trellopy.py
-----------
The controller object is the main interface to the entire package. Use this
to make new boards, get boards, add new members, show all boards, and to
show all members.

Start by importing the python package:

>>> import trellopy

Get an instance of the controller like so:

>>> controller = trellopy.Controller()

.. autoclass:: trellopy.trellopy.Controller
  :members:
  :special-members: __init__

boards.py
---------
Once we have an instance of Controller as described above, operations of boards can be done. When a new board is initialized, a simple dict is saved to the database. The names of the boards must be unique.

>>> import trellopy
>>> controller = trellopy.Controller()
>>> board_1 = controller.new_board('Board')
>>> board_2 = controller.get_board('Bored')

.. autoclass:: trellopy.boards.Board
  :members:
  :special-members: __init__


A List class is represented as follows in the database.

>>> import trellopy
>>> controller = trellopy.Controller()
>>> board_1 = controller.new_board('Board')
>>> list_1 = board_1.get_list('List')

.. autoclass:: trellopy.boards.BoardList
  :members:
  :special-members: __init__


This is implemented as a simple dict. The property "name" must exist, as all cards must have a name.

>>> import trellopy
>>> controller = trellopy.Controller()
>>> board_1 = controller.new_board('Board')
>>> list_1 = board_1.get_list('List')
>>> card_1 = list_1.get_card('Card')

.. autoclass:: trellopy.boards.BoardListCard
  :members:
  :special-members: __init__

members.py
----------
.. autoclass:: trellopy.members.Member
  :members: 
  :special-members: __init__

backend.py
----------
.. autoclass:: trellopy.backend.Operator
  :members:
  :special-members: __init__