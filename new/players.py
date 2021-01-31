from __future__ import annotations
from random import randint, uniform

import ppb
from ppb import buttons, keycodes

import events
import utils
from shared import BASE_SPEED


class Bullet(ppb.Sprite):
    image = ppb.Triangle(200, 200, 75)
    basis = ppb.directions.Up
    size = 0.5
    speed_modifer = 3
    direction = ppb.directions.Up

    def on_update(self, event: ppb.events.Update, signal):
        self.position += self.direction * self.speed_modifer * BASE_SPEED * event.time_delta


class Player(ppb.Sprite):
    image = ppb.Square(200, 25, 25)
    velocity = ppb.Vector(0, 0)  # Badly named
    speed = BASE_SPEED
    life = 10
    heat = 0
    max_heat = 10

    def on_key_pressed(self, event: ppb.events.KeyPressed, signal):
        if event.key is keycodes.W:
            self.velocity += ppb.directions.Up
        elif event.key is keycodes.A:
            self.velocity += ppb.directions.Left
        elif event.key is keycodes.S:
            self.velocity += ppb.directions.Down
        elif event.key is keycodes.D:
            self.velocity += ppb.directions.Right

    def on_key_released(self, event: ppb.events.KeyReleased, signal):
        if event.key is keycodes.W:
            self.velocity -= ppb.directions.Up
        elif event.key is keycodes.A:
            self.velocity -= ppb.directions.Left
        elif event.key is keycodes.S:
            self.velocity -= ppb.directions.Down
        elif event.key is keycodes.D:
            self.velocity -= ppb.directions.Right

    def on_button_released(self, event: ppb.events.ButtonReleased, signal):
        if event.button is ppb.buttons.Primary:
            direction = (event.position - self.position).normalize()
            event.scene.add(Bullet(position=self.position + direction, direction=direction, facing=direction))
            signal(events.ShotFired(self.position, 1))
        elif event.button is ppb.buttons.Secondary:
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

    def on_update(self, event: ppb.events.Update, signal):
        velocity = self.velocity
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
