from __future__ import annotations
from random import randint, uniform
from time import perf_counter

import ppb
from ppb import buttons

import config
import events
import utils


class Bullet(ppb.Sprite):
    image = ppb.Triangle(200, 200, 75)
    basis = ppb.directions.Up
    size = config.Bullet.size

    speed_modifer = config.Bullet.speed_modifier
    direction = ppb.directions.Up
    max_distance = 5

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.starting_position = self.position

    def on_update(self, event: ppb.events.Update, signal):
        self.position += self.direction * self.speed_modifer * config.Root.base_speed * event.time_delta
        if (self.position - self.starting_position).length >= self.max_distance:
            event.scene.remove(self)


class Player(ppb.Sprite):
    image = ppb.Square(200, 25, 25)
    speed = config.Root.base_speed
    life = config.Player.life
    heat = 0
    max_heat = config.Player.max_heat
    primary_cooldown = config.Player.primary_cooldown
    last_fire_weapon_primary = 0
    secondary_cooldown = config.Player.secondary_cooldown
    last_fire_weapon_secondary = 0

    def on_button_released(self, event: ppb.events.ButtonReleased, signal):
        now = perf_counter()
        if event.button is ppb.buttons.Primary and now > self.last_fire_weapon_primary + self.primary_cooldown:
            direction = (event.position - self.position).normalize()

            event.scene.add(
                Bullet(
                    position=self.position + direction,
                    direction=direction,
                    facing=direction,
                    max_distance=config.Player.primary_max_distance
                )
            )

            signal(events.ShotFired(self.position, config.Player.primary_noise_scalar))
            self.last_fire_weapon_primary = now
        elif event.button is ppb.buttons.Secondary and now > self.last_fire_weapon_secondary + self.secondary_cooldown:
            direction = (event.position - self.position).normalize()
            spread = config.Player.secondary_spread
            for _ in range(randint(1, 2) + randint(1, 2) + randint(0, 1)):
                new_facing = direction.rotate(uniform(-spread, spread))
                event.scene.add(
                    Bullet(
                        position=self.position + direction,
                        direction=new_facing,
                        facing=new_facing,
                        max_distance=config.Player.secondary_max_distance
                    )
                )
            signal(events.ShotFired(self.position, config.Player.secondary_noise_scalar))
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

    @utils.debounce(config.Fire.debounce)
    def on_mobile_in_fire(self, event, signal):
        self.heat += config.Fire.heat

    def take_damage(self, signal):
        self.life -= 1
        if self.life <= 0:
            signal(events.GameOver())

    @utils.debounce(config.Player.handle_fire_debounce)
    def handle_heat(self, signal):
        self.take_damage(signal)

    @utils.debounce(config.Player.handle_fire_debounce)
    def reduce_heat(self):
        self.heat = max(0, self.heat - 1)
