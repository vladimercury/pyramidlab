from ..models import Group


class GroupDTO:
    def __init__(self, group: Group):
        self.__name__ = group.name
        self.name = group.name
        self.id = group.id
