from app.models.Entity import Entity


class Image(Entity):
    """
    Image Entity CLass model
    """

    def __init__(self, entity_detail_dict):
        super().__init__(entity_detail_dict)
        self.ENTITY = 'Images'
