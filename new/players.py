from __future__ import annotations
from random import randint, uniform
from time import perf_counter

import ppb
from ppb import buttons

import events
import utils
from shared import BASE_SPEED


class Bullet(ppb.Sprite):
    image = ppb.Triangle(200, 200, 75)
    basis = ppb.directions.Up
    size = 0.5
    speed_modifer = 3
    direction = ppb.directions.Up
    max_distance = 5

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.starting_position = self.position

    def on_update(self, event: ppb.events.Update, signal):
        self.position += self.direction * self.speed_modifer * BASE_SPEED * event.time_delta
        if (self.position - self.starting_position).length >= self.max_distance:
            event.scene.remove(self)


class Player(ppb.Sprite):
    image = ppb.Square(200, 25, 25)
    speed = BASE_SPEED
    life = 10
    heat = 0
    max_heat = 10
    primary_cooldown = .4
    last_fire_weapon_primary = 0
    secondary_cooldown = 1
    last_fire_weapon_secondary = 0

    def on_button_released(self, event: ppb.events.ButtonReleased, signal):
        now = perf_counter()
        if event.button is ppb.buttons.Primary and now > self.last_fire_weapon_primary + self.primary_cooldown:
            direction = (event.position - self.position).normalize()
            event.scene.add(Bullet(position=self.position + direction, direction=direction, facing=direction,
                                   max_distance=15))
            signal(events.ShotFired(self.position, 1))
            self.last_fire_weapon_primary = now
        elif event.button is ppb.buttons.Secondary and now > self.last_fire_weapon_secondary + self.secondary_cooldown:
            direction = (event.position - self.position).normalize()
            for _ in range(randint(1, 2) + randint(1, 2) + randint(0, 1)):
                new_facing = direction.rotate(uniform(-40, 40))
                event.scene.add(
                    Bullet(
                        position=self.position + direction,
                        direction=new_facing,
                        facing=new_facing
                    )
                )
            signal(events.ShotFired(self.position, 5))
            self.last_fire_weapon_secondary = now

    def on_update(self, event: ppb.events.Update, signal):
        velocity = event.movement
        if velocity:
            velocity = velocity.normalize()
        self.position += velocity * event.time_delta * self.speed
        if self.heat >= self.max_heat:
            self.handle_heat(signal)
        self.reduce_heat()

    def on_player_hurt(self, event: events.PlayerHurt, signal):
        self.take_damage(signal)

    @utils.debounce(0.1)
    def on_mobile_in_fire(self, event, signal):
        self.heat += 1

    def take_damage(self, signal):
        self.life -= 1
        if self.life <= 0:
            signal(events.GameOver())

    @utils.debounce(0.5)
    def handle_heat(self, signal):
        self.take_damage(signal)

    @utils.debounce(0.40)
    def reduce_heat(self):
        self.heat = max(0, self.heat - 1)
