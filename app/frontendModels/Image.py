from app.frontendModels.FrontEndEntity import FrontEndEntity


class FrontEndImage(FrontEndEntity):
    """
    Image Entity CLass model
    """

    def __init__(self, entity_detail_dict):
        super().__init__(entity_detail_dict)
        self.ENTITY = 'Images'
