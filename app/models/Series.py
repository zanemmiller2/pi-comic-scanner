from app.models.Entity import Entity


class Series(Entity):
    """
    Series Entity class model
    """

    def __init__(self, entity_detail_dict):
        super().__init__(entity_detail_dict)
        self.ENTITY = 'Series'
