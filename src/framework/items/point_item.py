from src.framework.items.base_item import *


class PointItem(BaseItem):
    def __init__(self, scene, pos: list[float, float]):
        super().__init__(scene)
        
        self.setPos(pos)
        
    def render(self):
        super().render()