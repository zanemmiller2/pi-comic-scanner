from app.models.FrontEndEntity import FrontEndEntity


class FrontEndCreator(FrontEndEntity):
    """
    Creator Entity CLass Model for front end Creator
    """

    def __init__(self, entity_detail_dict):
        super().__init__(entity_detail_dict)
        self.ENTITY = 'Creators'
