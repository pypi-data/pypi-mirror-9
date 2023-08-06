import pymongo


class Operator(object):
    """
    This is the database operator. Currently only supports MongoDB.
    """
    def __init__(self):
        """ Make a connection to the database """
        self._client = pymongo.MongoClient('mongodb://localhost:27017')
        self._db = self._client.potatodb
        self.boards = self._db.boards
        self.members = self._db.members
        self.boards.create_index('name', unique=True)
        self.members.create_index('name', unique=True)

    def save_board(self, board_dict):
        """ Save the board to the database """
        self.boards.insert(board_dict)

    def get_board(self, board_name):
        """ Get a board from the database """
        spec = {'name': board_name}
        try:
            return self.boards.find_one(spec)
        except Exception, e:
            print "Could not find board with name", board_name
            return False

    def update_board(self, board_data, board_name=None):
        """ Update the board in the database """
        spec = {}
        if board_name:
            spec['name'] = board_name
        else:
            spec['name'] = board_data['name']
        self.boards.update(spec, board_data)

    def gimme_everything(self):
        """ Fetch every board in the database """
        return self.boards.find()

    def gimme_everybody(self):
        """ Fetch every member in the database """
        return self.members.find()

    def new_member(self, member_dict):
        """ Add a member to the database """
        self.members.insert(member_dict)

    def update_member(self, member_data, member_name=None):
        """ Update a member in database """
        spec = {}
        if member_name:
            spec['name'] = member_name
        else:
            spec['name'] = member_data['name']
        self.members.update(spec, member_data)

    def get_member(self, member_name):
        """ Get a member from the database """
        spec = {'name': member_name}
        try:
            return self.members.find_one(spec)
        except Exception, e:
            print "Could not find member with name", member_name
            return False
