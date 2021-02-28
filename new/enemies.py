from __future__ import annotations
import math
from dataclasses import dataclass
from random import randint, uniform
from time import perf_counter
from typing import Any, Callable

import misbehave
import ppb

import config
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
    speed_modifer = config.Zombie.speed_modifier
    attack_speed_modifier = config.Zombie.attack_speed_modifier
    attack_time = config.Zombie.attack_time
    attack_range = config.Zombie.attack_range
    awareness = config.Zombie.awareness
    image = ppb.Square(40, 200, 35)
    size = config.Zombie.size
    points = config.Zombie.point_value
    tree: Callable[[Zombie, Any], misbehave.State] = behaviors.zombie_base_tree
    heat: int = 0
    max_heat: int = config.Zombie.max_heat
    flee_speed_modifier = config.Zombie.flee_speed
    flee_time = config.Zombie.flee_time
    chase_target = None

    spawn_multiplier = config.Zombie.spawn_multiplier
    min_first_cut = config.Zombie.spawn_first_min
    max_first_cut = config.Zombie.spawn_first_max
    min_second_cut = config.Zombie.spawn_second_min
    max_second_cut = config.Zombie.spawn_second_max
    min_third_cut = config.Zombie.spawn_third_min
    max_third_cut = config.Zombie.spawn_third_max

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def speed(self):
        return self.speed_modifer * config.Root.base_speed

    @property
    def attack_speed(self):
        return self.speed * self.attack_speed_modifier

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

        offset_limit = config.Zombie.spawn_offset_base
        for _ in range(randint(first_min, first_max) + randint(second_min, second_max) + randint(third_min, third_max)):
            offset_vector = ppb.Vector(uniform(-offset_limit, offset_limit), uniform(-offset_limit, offset_limit))
            spawn_position = group_origin + offset_vector
            if ((player.position - spawn_position).length <= cls.awareness
                    or cls.check_outside_limit(spawn_position, left_limit, right_limit, bottom_limit, top_limit)):
                continue
            scene.add(cls(position=group_origin + offset_vector))
            scene.spawned += 1

    @utils.debounce(config.Fire.debounce)
    def on_mobile_in_fire(self, event, signal):
        self.heat += 1

    @utils.debounce(config.Zombie.reduce_heat_debounce)
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
    speed_modifer = config.Skeleton.speed_modifer
    awareness = config.Skeleton.awareness
    image = ppb.Circle(240, 240, 255)
    size = config.Skeleton.size
    points = config.Skeleton.point_value
    attack_range = config.Skeleton.attack_range

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
