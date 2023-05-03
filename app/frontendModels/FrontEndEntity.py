class FrontEndEntity:
    """ Generic entity class model """

    def __init__(self, entity_detail_dict):
        self.id = None
        self.title = None
        self.description = None
        self.seriesId = None
        self.variantDescription = None
        self.purchaseDate = None
        self.purchaseType = None
        self.purchasePrice = None
        self.isPurchased = None
        self.textObjects = {}

        self.ENTITY = None

        for key in entity_detail_dict:
            setattr(self, key, entity_detail_dict[key])

        if self.description:
            self.description = self.description.decode()
        if self.variantDescription:
            self.variantDescription = self.variantDescription.decode()

        if self.purchaseDate and self.purchaseType and self.purchasePrice:
            self.isPurchased = True

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
