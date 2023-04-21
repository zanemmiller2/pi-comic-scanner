class Comic:

    def __init__(self, comic_dict):
        for key in comic_dict:
            setattr(self, key, comic_dict[key])

    def __repr__(self):
        """"""
        return "<Comic: %s="">" % self.__dict__
