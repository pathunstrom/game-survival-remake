from __future__ import annotations
from dataclasses import dataclass
from random import uniform, randint

import ppb
from ppb import keycodes, buttons, gomlib, systemslib

TITLE = "Zombie Apocalypse"
BASE_SPEED = 5

font = ppb.Font("Comfortaa_Bold.ttf", size=72)


def do_collide(first, second):
    left = min(first.left, second.left)
    right = max(first.right, second.right)
    top = max(first.top, second.top)
    bottom = min(first.bottom, second.bottom)
    return (right - left < first.size + second.size
            and top - bottom < first.size + second.size)


class ScoreDisplay(ppb.RectangleSprite):
    score = 0

    @property
    def image(self):
        return ppb.Text(f"Score: {self.score}", font=font, color=(255, 255, 255))


class ScoreSystem(systemslib.System):
    top_score = 0
    last_score = 0
    current_score = 0

    def __enter__(self):
        pass  # load up existing high score if available

    def on_enemy_killed(self, event: EnemyKilled, signal):
        self.current_score += event.enemy.points

    def on_game_over(self, event: GameOver, signal):
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


class TitleScreen(ppb.BaseScene):
    background_color = (0, 0, 0)
    last_score = 0
    top_score = 0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add(
            ppb.RectangleSprite(
                image=ppb.Text(
                    TITLE,
                    font=font,
                    color=(255, 255, 255)
                ),
                height=2,
                position=ppb.Vector(0, 2)
            )
        )
        self.add(
            ppb.RectangleSprite(
                image=ppb.Text(
                    "Press SPACE to Start",
                    font=font,
                    color=(255, 255, 255)
                ),
                position=ppb.Vector(0, -2)
            )
        )

    def on_key_released(self, event: ppb.events.KeyReleased, signal):
        if event.key is keycodes.Space:
            signal(ppb.events.StartScene(Game))


class GameOverScene(ppb.BaseScene):
    background_color = (0, 0, 0)
    last_score = 0
    top_score = 0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add(
            ppb.RectangleSprite(
                image=ppb.Text("Game Over", font=font, color=(255, 255, 255)),
                position=ppb.Vector(0, 4)
            )
        )

    def on_scene_started(self, event, signal):
        self.add(
            ppb.RectangleSprite(
                image=ppb.Text(f"You scored {self.last_score}", font=font, color=(255, 255, 255)),
                position=ppb.Vector(0, -2)
            )
        )
        if self.last_score >= self.top_score:
            self.add(
                ppb.RectangleSprite(
                    image=ppb.Text("New high score!", font=font, color=(255, 255, 255)),
                    position=ppb.Vector(0, -4)
                )
            )

    def on_key_released(self, event, signal):
        if event.key is keycodes.Space:
            signal(ppb.events.StopScene())

    def on_button_released(self, event, signal):
        signal(ppb.events.StopScene())

@dataclass
class EnemyKilled:
    enemy: 'Zombie'
    scene: 'Game' = None


@dataclass
class GameOver:
    scene: 'Game' = None


@dataclass
class PlayerHurt:
    scene: 'Game' = None


@dataclass
class ShotFired:
    position: ppb.Vector
    noise: int
    scene: 'Game' = None


class LifeDisplay(ppb.Sprite):
    health_value = 1
    full_image = ppb.Image('full-heart.png')
    empty_image = ppb.Image('empty-heart.png')
    image = full_image

    def on_pre_render(self, event, signal):
        player = next(event.scene.get(kind=Player))
        if player.life < self.health_value:
            self.image = self.empty_image


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
            signal(ShotFired(self.position, 1))
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
            signal(ShotFired(self.position, 3))

    def on_update(self, event: ppb.events.Update, signal):
        velocity = self.velocity
        if velocity:
            velocity = velocity.normalize()
        self.position += velocity * event.time_delta * self.speed

    def on_player_hurt(self, event: PlayerHurt, signal):
        self.life -= 1
        if self.life <= 0:
            signal(GameOver())


class WanderState:
    wander_intensity = 16
    speed_modifier = 0.5

    def __init__(self):
        self.wander_vector = ppb.Vector(uniform(-1, 1), uniform(-1, 1)).normalize()
        self.velocity = ppb.Vector(0, 0)

    def update(self, parent, event, signal):
        # Check for state change
        player = next(event.scene.get(kind=Player))
        distance_to_player = (player.position - parent.position).length
        if distance_to_player <= parent.awareness:
            parent.state = AttackState()

        # Wander Code
        self.wander_vector = self.wander_vector.rotate(uniform(-self.wander_intensity, self.wander_intensity))
        velocity = self.velocity.scale_to(2) if self.velocity else self.velocity
        self.velocity += velocity + self.wander_vector.scale_to(1)
        self.velocity = self.velocity.truncate(parent.speed)
        parent.position += self.velocity * event.time_delta


class AttackState:
    speed_modifier = 1

    def update(self, parent, event: ppb.events.Update, signal):
        player = next(event.scene.get(kind=Player))
        direction = (player.position - parent.position).normalize()
        delta = direction * event.time_delta * parent.speed
        parent.position += delta


class Zombie(ppb.Sprite):
    speed_modifer = 0.7
    awareness = 4
    image = ppb.Square(40, 200, 35)
    size = 1.2
    points = 10

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.state = WanderState()

    @property
    def speed(self):
        return self.speed_modifer * BASE_SPEED * self.state.speed_modifier

    def on_update(self, event, signal):
        self.state.update(self, event, signal)

    def on_shot_fired(self, event: ShotFired, signal):
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
        player = next(scene.get(kind=Player))
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
        player = next(scene.get(kind=Player))
        if (player.position - spawn_position).length <= cls.awareness:
            return
        scene.add(cls(position=spawn_position))


class Collider(gomlib.GameObject):
    primed = False

    def on_update(self, event, signal):
        self.primed = True

    def on_idle(self, event: ppb.events.Idle, signal):
        for_removal = set()
        player = next(event.scene.get(kind=Player))
        if self.primed:
            for enemy in event.scene.get(kind=Zombie):
                for bullet in event.scene.get(kind=Bullet):
                    if bullet in for_removal:
                        continue
                    if do_collide(enemy, bullet):
                        for_removal.add(enemy)
                        for_removal.add(bullet)
                        signal(EnemyKilled(enemy))
                        break
                if enemy in for_removal:
                    continue
                if do_collide(player, enemy):
                    for_removal.add(enemy)
                    signal(PlayerHurt())
            for obj in for_removal:
                event.scene.remove(obj)
            self.primed = False


class Game(ppb.BaseScene):
    background_color = (0, 0, 0)
    spawn_timers = {
        Zombie: [3.0, 0.0],
        Skeleton: [12.0, 6.0]
    }

    def __init__(self, **props):
        super().__init__(**props)
        self.add(Player(position=ppb.Vector(5, -5)))
        self.add(Collider())
        self.add(ScoreDisplay(position=ppb.Vector(8, 16)))
        for value in range(1, 11):
            self.add(LifeDisplay(health_value=value, position=(ppb.Vector(-8 + (-1.5 * value), 16))))

    def on_scene_started(self, event, signal):
        self.main_camera.width = 48

    def on_update(self, event: ppb.events.Update, signal):
        for kind, timer in self.spawn_timers.items():
            timer[1] -= event.time_delta
            if timer[1] <= 0:
                kind.spawn(self)
                default = timer[0]
                timer[1] = (default * 0.5) + (default * uniform(0, 1))

    def on_game_over(self, event: GameOver, signal):
        signal(ppb.events.ReplaceScene(GameOverScene))


ppb.run(starting_scene=TitleScreen, title=TITLE, systems=[ScoreSystem])
