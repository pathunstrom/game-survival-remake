from __future__ import annotations
import math
from dataclasses import dataclass
from random import randint, uniform
from time import perf_counter
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


@dataclass
class Cry:
    source: Zombie


class CryDebug(ppb.Sprite):
    layer = -1000
    size = 12
    life_time = 2
    image = ppb.Circle(200, 200, 100)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.start = perf_counter()

    def on_pre_render(self, e: ppb.events.PreRender, signal):
        if perf_counter() > self.start + self.life_time:
            e.scene.remove(self)


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
    chase_target = None
    last_cry = 0

    spawn_multiplier = 3
    min_first_cut = 0.5
    max_first_cut = 0.25
    min_second_cut = 0.25
    max_second_cut = 0.5
    min_third_cut = 0.25
    max_third_cut = 0.25

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

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
        # Minimum  == level,  1/2 round up to fist, then 1/4 and 1/4 round down
        # Maximum == level * 3, 1/4 1/2 1/4
        # Level 1: minimum == 1 randint min 1, randint min 0, randint min 0
        # Level 1: maximum == 4 randint max 1, ranint max 2, randint max 1
        # 1 and 4 randint(1, 2), randint(0, 2), randint(0, 1)
        level = scene.level
        spawn_max = level * cls.spawn_multiplier

        first_min = math.ceil(level * cls.min_first_cut)
        first_max = max(first_min, math.floor(spawn_max * cls.max_first_cut))
        second_min = math.floor(level * cls.min_second_cut)
        second_max = max(second_min, math.ceil(spawn_max * cls.max_second_cut))
        third_min = math.floor(level * cls.min_second_cut)
        third_max = max(third_min, math.floor(spawn_max * cls.max_third_cut))

        for _ in range(randint(first_min, first_max) + randint(second_min, second_max) + randint(third_min, third_max)):
            offset_vector = ppb.Vector(uniform(-2.5, 2.5), uniform(-2.5, 2.5))
            spawn_position = group_origin + offset_vector
            if ((player.position - spawn_position).length <= cls.awareness
                    or cls.check_outside_limit(spawn_position, left_limit, right_limit, bottom_limit, top_limit)):
                continue
            scene.add(cls(position=group_origin + offset_vector))
            scene.spawned += 1

    @utils.debounce(FIRE_DEBOUNCE)
    def on_mobile_in_fire(self, event, signal):
        self.heat += 1

    @utils.debounce(0.2)
    def reduce_heat(self):
        self.heat = max(0, self.heat - 1)

    def on_cry(self, event, signal):
        if not self.chase_target and (self.position - event.source.position).length >= self.awareness:
            self.chase_target = event.source.chase_target

    @staticmethod
    def check_outside_limit(position, left, right, bottom, top) -> bool:
        x_result = left >= position.x or position.x >= right
        y_result = (bottom >= position.y or position.y >= top)
        return x_result or y_result


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
        count = randint(1, scene.level) if scene.level > 1 else 1
        for _ in range(count):
            spawn_position = ppb.Vector(
                uniform(left_limit, right_limit),
                uniform(top_limit, bottom_limit)
            )
            player = next(scene.get(kind=player_module.Player))
            if (player.position - spawn_position).length <= cls.awareness:
                continue
            scene.add(cls(position=spawn_position))
            scene.spawned += 1
