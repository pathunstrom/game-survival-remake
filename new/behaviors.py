from __future__ import annotations
from random import uniform
from time import perf_counter
from typing import Any, Callable, Union

import misbehave
import ppb

import enemies
import players


class GlobalDebounce(misbehave.decorator.Decorator):
    """
    Debounces for all objects using the same tree.

    Replaces need for global blackboard.
    """
    last_call = 0

    def __init__(self, child, cooldown=.5):
        super().__init__(child, cooldown=cooldown)
        self.cooldown = cooldown

    def __call__(self, actor: enemies.Zombie, context: enemies.Context):
        now = perf_counter()
        if now >= self.last_call + self.cooldown:
            result = super().__call__(actor, context)
            if result == misbehave.State.SUCCESS:
                self.last_call = now
            return result
        return misbehave.State.FAILED


def signal_cry(actor: enemies.Zombie, context: enemies.Context) -> misbehave.State:
    context.signal(enemies.Cry(actor))
    return misbehave.State.SUCCESS


def add_debug_object(actor: ppb.Sprite, context: enemies.Context) -> misbehave.State:
    context.event.scene.add(enemies.CryDebug(position=actor.position))
    return misbehave.State.SUCCESS


def compare_heat(child):

    def compare_heat_inner(actor: enemies.Zombie, context: Any) -> misbehave.State:
        if actor.heat >= actor.max_heat:
            return child(actor, context)
        return misbehave.State.FAILED
    return compare_heat_inner


def move_in_fixed_direction(direction: ppb.Vector, time: Union[int, float] = 1) -> Callable[[enemies.Zombie, Any], misbehave.State]:

    def move_in_fixed_direction_inner(actor: enemies.Zombie, context: Any) -> misbehave.State:  # Context event, signal ???
        attribute = f"{move_in_fixed_direction_inner.__name__}_{id(move_in_fixed_direction_inner)}"
        if not getattr(actor, attribute, None):
            setattr(actor, attribute, perf_counter())
        actor.position += direction * actor.speed * context.event.time_delta
        if perf_counter() - getattr(actor, attribute) >= time:
            setattr(actor, attribute, None)
            return misbehave.State.SUCCESS
        return misbehave.State.RUNNING
    return move_in_fixed_direction_inner


def move_to_target(target_attribute: str):

    def move_to_target_inner(actor, context):
        target_position = getattr(actor, target_attribute)
        actor.position += (target_position - actor.position).normalize() * actor.speed * context.event.time_delta
        if (target_position - actor.position).length <= actor.size * 1.5:
            return misbehave.State.SUCCESS
        return misbehave.State.RUNNING
    return move_to_target_inner


def pick_random_direction(storage_attribute):

    def pick_random_direction_inner(actor, context):
        direction_vector = ppb.Vector(uniform(-1, 1), uniform(-1, 1))
        if direction_vector:
            direction_vector.normalize()
        setattr(actor, storage_attribute, direction_vector)
        return misbehave.State.SUCCESS
    return pick_random_direction_inner


def pick_random_value(storage_attribute, min, max):

    def pick_random_value_inner(actor, context):
        setattr(actor, storage_attribute, uniform(min, max))
        return misbehave.State.SUCCESS
    return pick_random_value_inner


def pick_random_speed(storage_attribute, min, max):

    def pick_random_speed_inner(actor, context):
        result = uniform(min, max) * actor.speed
        if result > actor.speed:
            raise ValueError("Way too fast.")
        setattr(actor, storage_attribute, result)
        return misbehave.State.SUCCESS
    return pick_random_speed_inner


def wander(direction_attr, speed_attr, time_attr, start_attr):

    def wander_inner(actor, context):
        start_time = getattr(actor, start_attr)
        direction = getattr(actor, direction_attr)
        speed = getattr(actor, speed_attr)
        time = getattr(actor, time_attr)
        movement_vector = direction * speed * context.event.time_delta
        actor.position += movement_vector
        if perf_counter() - start_time >= time:
            return misbehave.State.SUCCESS
        return misbehave.State.RUNNING
    return wander_inner


def check_if_player_is_close(child, *, storage_attr):

    def check_if_player_is_close_inner(actor, context):
        player = next(context.event.scene.get(kind=players.Player))
        distance_to_player = (player.position - actor.position).length
        critical_distance = getattr(actor, storage_attr)
        if distance_to_player <= critical_distance:
            return child(actor, context)
        return misbehave.State.FAILED

    return check_if_player_is_close_inner


def set_player_position_on_actor(storage_attr):

    def set_player_position_inner(actor, context):
        player = next(context.event.scene.get(kind=players.Player))
        setattr(actor, storage_attr, player.position)
        return misbehave.State.SUCCESS
    return set_player_position_inner


def set_attack_direction(target_attr, storage_attr):

    def set_attack_direction_inner(actor, context):
        target = getattr(actor, target_attr)
        direction_vector = (target - actor.position).normalize()
        setattr(actor, storage_attr, direction_vector)
        return misbehave.State.SUCCESS
    return set_attack_direction_inner


def kill_actor(actor, context):
    context.event.scene.remove(actor)
    return misbehave.State.SUCCESS


def octogon(magnitude=0.5):
    return misbehave.selector.Sequence(
        move_in_fixed_direction(ppb.directions.Up, magnitude),
        move_in_fixed_direction(ppb.directions.UpAndLeft, magnitude),
        move_in_fixed_direction(ppb.directions.Left, magnitude),
        move_in_fixed_direction(ppb.directions.DownAndLeft, magnitude),
        move_in_fixed_direction(ppb.directions.Down, magnitude),
        move_in_fixed_direction(ppb.directions.DownAndRight, magnitude),
        move_in_fixed_direction(ppb.directions.Right, magnitude),
        move_in_fixed_direction(ppb.directions.UpAndRight, magnitude)
    )


chase_tree = misbehave.selector.Concurrent(
    misbehave.selector.Sequence(
        misbehave.action.CheckValue("chase_target"),
        move_to_target("chase_target"),
        misbehave.action.SetValue("chase_target", None),
    ),
    GlobalDebounce(
        misbehave.selector.Sequence(
            misbehave.action.CheckValue("chase_target"),
            signal_cry
        ),
        cooldown=1.5  # TODO: Magic Number
    ),
    num_fail=2
)

wander_tree = misbehave.selector.Sequence(
    pick_random_direction("wander_direction"),
    pick_random_speed("wander_speed", .25, .75),
    pick_random_value("wander_time", .25, 1.5),
    misbehave.action.SetCurrentTime("wander_start"),
    wander("wander_direction", "wander_speed", "wander_time", "wander_start")
)

lunge_tree = misbehave.selector.Sequence(
    check_if_player_is_close(
        set_player_position_on_actor("attack_target"),
        storage_attr="attack_range"
    ),
    set_attack_direction("attack_target", "attack_direction"),
    misbehave.action.SetCurrentTime("wind_up"),
    misbehave.action.Wait("wind_up", 0.1),
    misbehave.action.SetCurrentTime("attack_start"),
    wander(
        "attack_direction",
        "attack_speed",
        "attack_time",
        "attack_start"
    )
)

on_fire_tree = compare_heat(
    misbehave.selector.Sequence(
        pick_random_direction("flee_direction"),
        misbehave.action.SetCurrentTime("flee_start"),
        wander(
            "flee_direction",
            "flee_speed",
            "flee_time",
            "flee_start"
        ),
        misbehave.action.SetCurrentTime('death_wait'),
        misbehave.action.Wait('death_wait', 0.25),
        kill_actor
    )
)

zombie_base_tree = misbehave.selector.Priority(
    on_fire_tree,
    lunge_tree,
    misbehave.selector.Concurrent(
        chase_tree,
        check_if_player_is_close(
            set_player_position_on_actor("chase_target"),
            storage_attr="awareness"
        ),
        num_fail=2
    ),
    wander_tree
)
