from app.models.Entity import Entity


class Story(Entity):
    """
    Story Entity Class model
    """

    def __init__(self, entity_detail_dict):
        super().__init__(entity_detail_dict)
        self.ENTITY = "Stories"
