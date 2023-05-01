from app.frontendModels.FrontEndEntity import FrontEndEntity


class FrontEndEvent(FrontEndEntity):
    """
    DOCSTRING
    """

    def __init__(self, entity_detail_dict):
        super().__init__(entity_detail_dict)
        self.ENTITY = 'Event'
