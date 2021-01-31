from __future__ import annotations
from dataclasses import dataclass
from random import randint, uniform
from typing import Any, Callable

import misbehave
import ppb

from shared import BASE_SPEED, FIRE_DEBOUNCE
import players as player_module
import events as game_events
import behaviors
import utils

@dataclass
class Context:
    event: Any
    signal: Any


class AttackState:
    speed_modifier = 1

    def update(self, parent, event: ppb.events.Update, signal):
        player = next(event.scene.get(kind=player_module.Player))
        direction = (player.position - parent.position).normalize()
        delta = direction * event.time_delta * parent.speed
        parent.position += delta


class WanderState:
    wander_intensity = 16
    speed_modifier = 0.5

    def __init__(self):
        self.wander_vector = ppb.Vector(uniform(-1, 1), uniform(-1, 1)).normalize()
        self.velocity = ppb.Vector(0, 0)

    def update(self, parent, event, signal):
        # Check for state change
        player = next(event.scene.get(kind=player_module.Player))
        distance_to_player = (player.position - parent.position).length
        if distance_to_player <= parent.awareness:
            parent.state = AttackState()

        # Wander Code
        self.wander_vector = self.wander_vector.rotate(uniform(-self.wander_intensity, self.wander_intensity))
        velocity = self.velocity.scale_to(2) if self.velocity else self.velocity
        self.velocity += velocity + self.wander_vector.scale_to(1)
        self.velocity = self.velocity.truncate(parent.speed)
        parent.position += self.velocity * event.time_delta


class Zombie(ppb.Sprite):
    speed_modifer = 0.7
    attack_speed_modifier = 2
    attack_time = .35
    attack_range = 2.5
    awareness = 6
    image = ppb.Square(40, 200, 35)
    size = 1.2
    points = 10
    tree: Callable[[Zombie, Any], misbehave.State] = behaviors.zombie_base_tree
    heat: int = 0
    max_heat: int = 1
    flee_speed_modifier = 3
    flee_time = 1

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.state = WanderState()

    @property
    def speed(self):
        return self.speed_modifer * BASE_SPEED

    @property
    def attack_speed(self):
        return self.speed_modifer * BASE_SPEED * self.attack_speed_modifier

    @property
    def flee_speed(self):
        return self.speed * self.flee_speed_modifier

    def on_update(self, event, signal):
        context = Context(event, signal)
        self.tree(self, context)
        self.reduce_heat()

    def on_shot_fired(self, event: game_events.ShotFired, signal):
        if (event.position - self.position).length <= self.awareness * event.noise:
            self.chase_target = event.position

    @classmethod
    def spawn(cls, scene):
        top_limit, right_limit, bottom_limit, left_limit = scene.play_space_limits
        group_origin = ppb.Vector(
            uniform(left_limit, right_limit),
            uniform(top_limit, bottom_limit)
        )
        player = next(scene.get(kind=player_module.Player))
        if (player.position - group_origin).length <= cls.awareness + 2.5:
            return
        for _ in range(randint(1, 2) + randint(0, 2) + randint(0, 1)):
            offset_vector = ppb.Vector(uniform(-2.5, 2.5), uniform(-2.5, 2.5))
            if (player.position - group_origin + offset_vector).length <= cls.awareness:
                continue
            scene.add(cls(position=group_origin + offset_vector))

    @utils.debounce(FIRE_DEBOUNCE)
    def on_mobile_in_fire(self, event, signal):
        self.heat += 1

    @utils.debounce(0.2)
    def reduce_heat(self):
        self.heat = max(0, self.heat - 1)


class Skeleton(Zombie):
    speed_modifer = 1.2
    awareness = 8
    image = ppb.Circle(240, 240, 255)
    size = 0.8
    points = 15
    attack_range = 3

    @classmethod
    def spawn(cls, scene):
        top_limit, right_limit, bottom_limit, left_limit = scene.play_space_limits
        spawn_position = ppb.Vector(
            uniform(left_limit, right_limit),
            uniform(top_limit, bottom_limit)
        )
        player = next(scene.get(kind=player_module.Player))
        if (player.position - spawn_position).length <= cls.awareness:
            return
        scene.add(cls(position=spawn_position))