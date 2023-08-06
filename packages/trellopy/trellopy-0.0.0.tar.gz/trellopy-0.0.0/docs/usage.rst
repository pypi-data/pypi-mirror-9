========
Usage
========

Import module:

    >>> import trellopy

Get a controller:

    >>> controller = trellopy.Controller()
    >>> dir(controller)
    ['__class__', '__delattr__', '__dict__', '__doc__', '__format__', '__getattribute__', '__hash__', '__init__', '__module__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_operator', 'get_board', 'get_member', 'new_board', 'new_member', 'show_boards', 'show_members']


The Controller object allows you to do the following actions:

 * New board

   >>> controller.new_board('Board')

 * Get existing board

   >>> controller.get_board('Board')

 * New member

   >>> controller.new_member('Person')

 * Get exisiting member

   >>> controller.get_member('Person')

 * Show all the boards

   >>> controller.show_boards()

 * Show all the members

   >>> controller.show_members()
