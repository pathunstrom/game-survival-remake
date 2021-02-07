from __future__ import annotations
from dataclasses import dataclass

import ppb

import enemies
import scenes


@dataclass
class EnemyKilled:
    enemy: enemies.Zombie
    scene: scenes.Game = None


@dataclass
class GameOver:
    scene: scenes.Game = None


@dataclass
class PlayerHurt:
    scene: scenes.Game = None


@dataclass
class ShotFired:
    position: ppb.Vector
    noise: int
    scene: scenes.Game = None


@dataclass
class MobileInFire:
    scene: scenes.Game = None
