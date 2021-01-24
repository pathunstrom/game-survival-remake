from __future__ import annotations
from random import uniform

import ppb
from ppb import keycodes
from ppb import gomlib

from shared import TITLE, FONT
import enemies
import events
import players
import systems


def do_collide(first, second):
    left = min(first.left, second.left)
    right = max(first.right, second.right)
    top = max(first.top, second.top)
    bottom = min(first.bottom, second.bottom)
    return (right - left < first.size + second.size
            and top - bottom < first.size + second.size)


class LifeDisplay(ppb.Sprite):
    health_value = 1
    full_image = ppb.Image('full-heart.png')
    empty_image = ppb.Image('empty-heart.png')
    image = full_image

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
        if self.primed:
            for enemy in event.scene.get(kind=enemies.Zombie):
                for bullet in event.scene.get(kind=players.Bullet):
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
    spawn_timers = {
        enemies.Zombie: [3.0, 0.0],
        enemies.Skeleton: [12.0, 6.0]
    }

    def __init__(self, **props):
        super().__init__(**props)
        self.add(players.Player(position=ppb.Vector(5, -5)))
        self.add(Collider())
        self.add(systems.ScoreDisplay(position=ppb.Vector(8, 16)))
        for value in range(1, 11):
            self.add(LifeDisplay(health_value=value, position=(ppb.Vector(-8 + (-1.5 * value), 16))))

    def on_scene_started(self, event, signal):
        self.main_camera.width = 48

    def on_update(self, event: ppb.events.Update, signal):
        for kind, timer in self.spawn_timers.items():
            timer[1] -= event.time_delta
            if timer[1] <= 0:
                kind.spawn(self)
                default = timer[0]
                timer[1] = (default * 0.5) + (default * uniform(0, 1))

    def on_game_over(self, event: events.GameOver, signal):
        signal(ppb.events.ReplaceScene(GameOverScene))


class Sandbox(ppb.BaseScene):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add(players.Player(position=ppb.Vector(20, 20)))
        self.add(enemies.Zombie(position=ppb.Vector(0, 0)))

    def on_scene_started(self, event, signal):
        self.main_camera.width = 48
