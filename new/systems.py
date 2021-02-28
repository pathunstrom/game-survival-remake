from __future__ import annotations
from dataclasses import dataclass

import ppb
from ppb import keycodes, systemslib

import events
from shared import FONT


class ScoreDisplay(ppb.RectangleSprite):
    score = 0
    layer = 100
    offset = ppb.Vector(0, 0)
    height = 1.5

    @property
    def image(self):
        return ppb.Text(f"Score: {self.score}", font=FONT, color=(255, 255, 255))

    def on_pre_render(self, event: ppb.events.PreRender, signal):
        self.position = event.scene.main_camera.position + self.offset


class ScoreSystem(systemslib.System):
    top_score = 0
    last_score = 0
    current_score = 0

    def __enter__(self):
        pass  # load up existing high score if available

    def on_enemy_killed(self, event: events.EnemyKilled, signal):
        self.current_score += event.enemy.points

    def on_game_over(self, event: events.GameOver, signal):
        if self.current_score >= self.top_score:
            self.top_score = self.current_score
        self.last_score = self.current_score
        self.current_score = 0

    def on_scene_started(self, event: ppb.events.SceneStarted, signal):
        event.scene.top_score = self.top_score
        event.scene.last_score = self.last_score

    def on_pre_render(self, event, signal):
        for score_display in event.scene.get(kind=ScoreDisplay):
            score_display.score = self.current_score


class Controller(systemslib.System):

    move_vector = ppb.Vector(0, 0)

    def __init__(self, engine: ppb.engine.GameEngine, **kwargs):
        super().__init__(engine=engine, **kwargs)
        engine.register(ppb.events.Update, self.add_controls)

    def add_controls(self, event):
        event.movement = self.move_vector

    def on_key_pressed(self, event: ppb.events.KeyPressed, signal):
        if event.key is keycodes.W:
            self.move_vector += ppb.directions.Up
        elif event.key is keycodes.A:
            self.move_vector += ppb.directions.Left
        elif event.key is keycodes.S:
            self.move_vector += ppb.directions.Down
        elif event.key is keycodes.D:
            self.move_vector += ppb.directions.Right

    def on_key_released(self, event: ppb.events.KeyReleased, signal):
        if event.key is keycodes.W:
            self.move_vector -= ppb.directions.Up
        elif event.key is keycodes.A:
            self.move_vector -= ppb.directions.Left
        elif event.key is keycodes.S:
            self.move_vector -= ppb.directions.Down
        elif event.key is keycodes.D:
            self.move_vector -= ppb.directions.Right
