from backend import Operator


class Member(object):
    """ Represents a member in the trellopy system. """
    def __init__(self, member_name):
        """ Initialize a member class """
        self._operator = Operator()
        if not self.in_database(member_name):
            self.person = {}
            self.person['name'] = member_name
            self._operator.new_member(self.person)
        else:
            self.person = self._operator.get_member(member_name)

    def rename(self, new_name):
        """ Rename the member """
        old_name = self.person['name']
        self.person['name'] = new_name
        self._operator.update_member(self.person, old_name)

    def archive(self):
        """ archive the member """
        self.person['archived'] = True
        self._operator.update_member(self.person)

    def in_database(self, member_name):
        """ Check if member already exists """
        return self._operator.get_member(member_name)
