from __future__ import annotations
import itertools
import typing
from random import uniform, shuffle, randint

import ppb
from ppb import keycodes
from ppb import gomlib

from shared import TITLE, FONT
import enemies
import events
import players
import systems
import terrain


def do_collide(first, second):
    left = min(first.left, second.left)
    right = max(first.right, second.right)
    top = max(first.top, second.top)
    bottom = min(first.bottom, second.bottom)
    rv = ((right - left < first.width + second.width)
          and (top - bottom < first.height + second.height))
    return rv


class LifeDisplay(ppb.Sprite):
    health_value = 1
    full_image = ppb.Image('full-heart.png')
    empty_image = ppb.Image('empty-heart.png')
    image = full_image
    layer = 100

    def on_pre_render(self, event, signal):
        player = next(event.scene.get(kind=players.Player))
        if player.life < self.health_value:
            self.image = self.empty_image


class Collider(gomlib.GameObject):
    primed = False

    def on_update(self, event, signal):
        self.primed = True

    def on_idle(self, event: ppb.events.Idle, signal):
        for_removal = set()
        player = next(event.scene.get(kind=players.Player))
        zombies = list(event.scene.get(kind=enemies.Zombie))
        bullets = list(event.scene.get(kind=players.Bullet))
        wall_colliders = list(event.scene.get(kind=terrain.WallCollider))
        hazards = list(event.scene.get(kind=terrain.Hazard))

        if self.primed:
            wall: terrain.WallCollider
            mobile: typing.Union[players.Player, enemies.Zombie, players.Bullet]
            for wall, mobile in itertools.product(wall_colliders, itertools.chain([player], zombies, bullets)):
                if do_collide(wall, mobile):
                    if isinstance(mobile, players.Bullet):
                        for_removal.add(mobile)
                        continue
                    mobile.position += wall.normal.scale_to(0.25)

            for hazard, mobile in itertools.product(hazards, itertools.chain([player], zombies)):
                if do_collide(hazard, mobile):
                    signal(events.MobileInFire(), targets=[mobile])

            for enemy in zombies:
                for bullet in bullets:
                    if bullet in for_removal:
                        continue
                    if do_collide(enemy, bullet):
                        for_removal.add(enemy)
                        for_removal.add(bullet)
                        signal(events.EnemyKilled(enemy))
                        break
                if enemy in for_removal:
                    continue
                if do_collide(player, enemy):
                    for_removal.add(enemy)
                    signal(events.PlayerHurt())
            for obj in for_removal:
                event.scene.remove(obj)
            self.primed = False


class TitleScreen(ppb.BaseScene):
    background_color = (0, 0, 0)
    last_score = 0
    top_score = 0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add(
            ppb.RectangleSprite(
                image=ppb.Text(
                    TITLE,
                    font=FONT,
                    color=(255, 255, 255)
                ),
                height=2,
                position=ppb.Vector(0, 2)
            )
        )
        self.add(
            ppb.RectangleSprite(
                image=ppb.Text(
                    "Press SPACE to Start",
                    font=FONT,
                    color=(255, 255, 255)
                ),
                position=ppb.Vector(0, -2)
            )
        )

    def on_key_released(self, event: ppb.events.KeyReleased, signal):
        if event.key is keycodes.Space:
            signal(ppb.events.StartScene(Game))


class GameOverScene(ppb.BaseScene):
    background_color = (0, 0, 0)
    last_score = 0
    top_score = 0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add(
            ppb.RectangleSprite(
                image=ppb.Text("Game Over", font=FONT, color=(255, 255, 255)),
                position=ppb.Vector(0, 4)
            )
        )

    def on_scene_started(self, event, signal):
        self.add(
            ppb.RectangleSprite(
                image=ppb.Text(f"You scored {self.last_score}", font=FONT, color=(255, 255, 255)),
                position=ppb.Vector(0, -2)
            )
        )
        if self.last_score >= self.top_score:
            self.add(
                ppb.RectangleSprite(
                    image=ppb.Text("New high score!", font=FONT, color=(255, 255, 255)),
                    position=ppb.Vector(0, -4)
                )
            )

    def on_key_released(self, event, signal):
        if event.key is keycodes.Space:
            signal(ppb.events.StopScene())

    def on_button_released(self, event, signal):
        signal(ppb.events.StopScene())


class Game(ppb.BaseScene):
    background_color = (0, 0, 0)

    level = 1
    level_spawned = False
    current_generator = None
    spawn_limit = 25
    spawned = 0

    def __init__(self, player_life=10, **props):
        super().__init__(**props)
        self.add(players.Player(player_life=10))
        self.add(Collider())
        self.add(systems.ScoreDisplay(position=ppb.Vector(8, 16)))
        for value in range(1, 11):
            self.add(LifeDisplay(health_value=value, position=(ppb.Vector(-8 + (-1.5 * value), 16))))
        self.spawn_timers = {
            enemies.Zombie: [3.0, 0.0],
            enemies.Skeleton: [12.0, 6.0]
        }
        # Build Level
        self.generators = [self.generate_walls, self.generate_hazards]
        limits_value = 10 + (3 * self.level)
        self.play_space_limits = (limits_value, limits_value, -limits_value, -limits_value)

        # Spawn setup
        self.spawn_limit = 20 + (5 * self.level)

    def on_scene_started(self, event, signal):
        self.main_camera.width = 48

    def on_update(self, event: ppb.events.Update, signal):
        if not self.level_spawned:
            return

        if self.spawned >= self.spawn_limit:
            if not list(self.get(kind=enemies.Zombie)):
                signal(ppb.events.ReplaceScene(Game, kwargs={"level": self.level + 1}))
            return

        for kind, timer in self.spawn_timers.items():
            timer[1] -= event.time_delta
            if timer[1] <= 0:
                kind.spawn(self)
                default = timer[0]
                timer[1] = (default * 0.5) + (default * uniform(0, 1))

    def on_pre_render(self, event, signal):
        if not self.level_spawned:
            if self.current_generator is None:
                try:
                    next_generator, *self.generators = self.generators
                except ValueError:
                    self.level_spawned = True
                    return
                else:
                    self.current_generator = next_generator(0)
            try:
                items = next(self.current_generator)
            except StopIteration:
                self.current_generator = None
            else:
                for item in items:
                    self.add(item)
        self.main_camera.position = next(self.get(kind=players.Player)).position

    def on_game_over(self, event: events.GameOver, signal):
        signal(ppb.events.ReplaceScene(GameOverScene))

    def generate_walls(self, level):
        """
        x x x x x x x
        x . . . . . x
        x . . . . . x
        x . . . . . x
        x . . . . . x
        x . . . . . x
        x x x x x x x
        :param level:
        :return:
        """

        all_walls = []
        top = self.play_space_limits[0] + 1
        left = self.play_space_limits[3] - 1
        right = self.play_space_limits[1] + 1
        bottom = self.play_space_limits[2] - 1
        print(top, right, left, bottom)
        all_walls.extend([ppb.Vector(x, top) for x in range(left, right + 1, 2)])  # Top walls
        all_walls.extend([ppb.Vector(x, bottom) for x in range(left, right + 1, 2)])  # Bottom walls
        all_walls.extend([ppb.Vector(left, x) for x in range(bottom, top, 2)])  # Left walls
        all_walls.extend([ppb.Vector(right, x) for x in range(bottom, top, 2)])  # right walls
        all_walls.extend([ppb.Vector(randint(left, right), randint(bottom, top)) for _ in range(self.level * 3)])

        shuffle(all_walls)

        while all_walls:
            walls = all_walls[:3]
            all_walls = all_walls[3:]
            yield [terrain.Wall(position=wall) for wall in walls]

    def generate_hazards(self, level):
        number_of_hazards = self.level - 5
        top, right, bottom, left = self.play_space_limits
        if number_of_hazards > 0:
            hazards = [terrain.Hazard(position=ppb.Vector(randint(left, right), randint(bottom, top))) for _ in range(number_of_hazards)]
            while hazards:
                yield [hazards.pop()]


class Sandbox(ppb.BaseScene):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add(Collider())
        self.add(players.Player(position=ppb.Vector(10, 10)))
        self.add(terrain.Hazard(position=ppb.Vector(0, 0)))
        self.add(enemies.Zombie(position=ppb.Vector(0, 0)))
        for value in range(1, 11):
            self.add(LifeDisplay(health_value=value, position=(ppb.Vector(-8 + (-1.5 * value), 16))))

    def on_scene_started(self, event, signal):
        self.main_camera.width = 48
