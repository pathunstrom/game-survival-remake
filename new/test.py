
import ppb
from pytest import mark

import enemies


@mark.parametrize(
    "limits,_input,expected",
    [
        ((-1, 1, -1, 1), ppb.Vector(0, 0), False),
        ((-1, 1, -1, 1), ppb.Vector(-1, 1), True),
        ((-1, 1, -1, 1), ppb.Vector(-2, 2), True)
    ]
)
def test_enemy_check_outside_limit(limits, _input, expected):
    result = enemies.Zombie.check_outside_limit(_input, *limits)
    assert result == expected
