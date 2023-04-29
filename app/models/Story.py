from app.models.FrontEndEntity import FrontEndEntity


class FrontEndStory(FrontEndEntity):
    """
    Story Entity Class model
    """

    def __init__(self, entity_detail_dict):
        super().__init__(entity_detail_dict)
        self.ENTITY = "Stories"
