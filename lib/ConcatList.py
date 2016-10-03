class ConcatList(list):
    """
    concatenatable list extension to hold measures in InstManager
    """
    def __add__(self, value):
        return type(self)(super(ConcatList, self).__add__([value]))

    def __iadd__(self, value):
        self.append(value)
        return self

