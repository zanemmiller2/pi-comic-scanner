from app.models.FrontEndEntity import FrontEndEntity


class FrontEndCharacter(FrontEndEntity):
    """
    DOCSTRING
    """

    def __init__(self, entity_detail_dict):
        super().__init__(entity_detail_dict)
        self.ENTITY = 'Characters'
