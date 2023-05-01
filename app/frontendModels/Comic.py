from app.frontendModels.FrontEndEntity import FrontEndEntity


class FrontEndComic(FrontEndEntity):
    """ Comic Entity class model for front end Comic """

    def __init__(self, entity_detail_dict):
        super().__init__(entity_detail_dict)
        self.ENTITY = "Comics"
