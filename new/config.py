class Root:
    base_speed = 5


class Bullet:
    size = 0.5
    speed_modifier = 3


class Collider:
    wall_push = 0.25


class Game:
    hazard_min_level = 5

    main_camera_width = 50
    main_camera_position_blend = 0.05

    spawn_limit_base = 20
    spawn_limit_scalar = 5

    zombie_spawn_base = 3.0
    zombie_spawn_initial = 0.0

    skeleton_spawn_base = 12.0
    skeleton_spawn_initial = 6.0

    wall_spawn_step_count = 3


class Fire:
    debounce = 0.1
    heat = 1


class Player:
    life = 10
    max_heat = 10
    primary_cooldown = 0.4
    primary_max_distance = 15
    primary_noise_scalar = 1
    secondary_cooldown = 1
    secondary_max_distance = 5
    secondary_noise_scalar = 5
    secondary_spread = 40
    handle_fire_debounce = 0.5
    reduce_heat_debounce = 0.4


class Skeleton:
    attack_range = 3
    awareness = 8
    point_value = 15
    size = 0.8
    speed_modifer = 1.2


class Zombie:
    attack_speed_modifier = 2
    attack_time = .35
    attack_range = 2.5
    awareness = 6
    flee_speed = 3
    flee_time = 1
    max_heat = 1
    point_value = 10
    reduce_heat_debounce = 0.2
    size = 1.2
    spawn_multiplier = 3
    spawn_first_min = 0.5
    spawn_first_max = 0.25
    spawn_second_min = 0.25
    spawn_second_max = 0.5
    spawn_third_min = 0.25
    spawn_third_max = 0.25
    spawn_offset_base = 2.5
    speed_modifier = 0.7
