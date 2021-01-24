from __future__ import annotations
from typing import Any, Callable

import misbehave
import ppb

import enemies


def move_in_direction(direction: ppb.Vector) -> Callable[[enemies.Zombie, Any], misbehave.State]:

    def move_in_direction_inner(actor: enemies.Zombie, context: Any) -> misbehave.State:  # Context event, signal ???
        actor.position += direction * actor.speed * context.event.time_delta
        return misbehave.State.SUCCESS
    return move_in_direction_inner


base_tree = misbehave.selector.Sequence(
    move_in_direction(ppb.directions.Up)
)