class FrontEndEntity:
    """ Generic entity class model """

    def __init__(self, entity_detail_dict):
        self.id = None
        self.title = None
        self.description = None
        self.seriesId = None

        self.ENTITY = None

        for key in entity_detail_dict:
            setattr(self, key, entity_detail_dict[key])

    def update_attributes(self, attributes, qualifier: str = None):
        """
        DOCSTRING
        :param qualifier:
        :param attributes:
        """
        if qualifier is None:
            for key in attributes:
                setattr(self, key, attributes[key])
        else:
            for key in attributes:
                temp_key = qualifier + '.' + str(key)
                setattr(self, temp_key, attributes[key])

    def __repr__(self):
        """"""
        return f"<{self.ENTITY}: %s="">" % self.__dict__
