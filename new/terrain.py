import ppb

COLLIDER_NORMALS = (ppb.directions.Up, ppb.directions.Right, ppb.directions.Left, ppb.directions.Down)

COLLIDER_VERTICAL_IMG = ppb.Image('collider_vertical.png')
COLLIDER_HORIZONTAL_IMG = ppb.Image('collider_horizontal.png')


class Terrain(ppb.RectangleSprite):
    pass


class WallCollider(Terrain):
    width = 0.5
    height = 2
    image = None
    normal = ppb.directions.Up
    layer = 10


class Wall(Terrain):
    width = 2
    height = 2
    image = ppb.Square(85, 46, 12)
    colliders_launched = False
    attribute_map = {
        (0, 1): 'top',
        (0, -1): 'bottom',
        (-1, 0): 'left',
        (1, 0): 'right'
    }

    def on_update(self, event: ppb.events.Update, signal):
        if not self.colliders_launched:
            for direction in COLLIDER_NORMALS:
                is_vertical = direction * ppb.directions.Up
                # This value will be -1, 0, 1 based on direction
                # Up should be 1, down should be -1, and 0 for left and right

                collider = WallCollider(
                    normal=direction,
                    width=2 if is_vertical else 0.5,
                    height=0.5 if is_vertical else 2,
                    position=self.position
                )
                attr = self.attribute_map[tuple(direction)]
                value = getattr(self, attr)
                setattr(collider, attr, value)
                event.scene.add(collider)
            self.colliders_launched = True
