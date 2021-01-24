from __future__ import annotations
from dataclasses import dataclass
from random import randint, uniform
from typing import Any, Callable

import misbehave
import ppb

from shared import BASE_SPEED
import players as player_module
import events as game_events
import behaviors


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
    awareness = 4
    image = ppb.Square(40, 200, 35)
    size = 1.2
    points = 10
    tree: Callable[[Zombie, Any], misbehave.State] = behaviors.base_tree

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.state = WanderState()

    @property
    def speed(self):
        return self.speed_modifer * BASE_SPEED * self.state.speed_modifier

    def on_update(self, event, signal):
        context = Context(event, signal)
        self.tree(self, context)

    def on_shot_fired(self, event: game_events.ShotFired, signal):
        if (event.position - self.position).length <= self.awareness * event.noise:
            self.state = AttackState()

    @classmethod
    def spawn(cls, scene):
        left_limit = scene.main_camera.left
        right_limit = scene.main_camera.right
        top_limit = scene.main_camera.top
        bottom_limit = scene.main_camera.bottom
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


class Skeleton(Zombie):
    speed_modifer = 1.2
    awareness = 8
    image = ppb.Circle(240, 240, 255)
    size = 0.8
    points = 15

    @classmethod
    def spawn(cls, scene):
        left_limit = scene.main_camera.left
        right_limit = scene.main_camera.right
        top_limit = scene.main_camera.top
        bottom_limit = scene.main_camera.bottom
        spawn_position = ppb.Vector(
            uniform(left_limit, right_limit),
            uniform(top_limit, bottom_limit)
        )
        player = next(scene.get(kind=player_module.Player))
        if (player.position - spawn_position).length <= cls.awareness:
            return
        scene.add(cls(position=spawn_position))