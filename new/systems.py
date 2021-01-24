from __future__ import annotations

import ppb
from ppb import systemslib

import events
from shared import FONT

class ScoreDisplay(ppb.RectangleSprite):
    score = 0

    @property
    def image(self):
        return ppb.Text(f"Score: {self.score}", font=FONT, color=(255, 255, 255))


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
