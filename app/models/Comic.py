class Comic:

    def __init__(self, comic_dict):
        self.description = None

        for key in comic_dict:
            setattr(self, key, comic_dict[key])

    def update_attributes(self, attributes):
        for key in attributes:
            setattr(self, key, attributes[key])

    def __repr__(self):
        """"""
        return "<Comic: %s="">" % self.__dict__
