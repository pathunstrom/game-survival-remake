from __future__ import annotations

import ppb

from shared import TITLE
from scenes import TitleScreen, Sandbox
from systems import ScoreSystem

ppb.run(starting_scene=TitleScreen, title=TITLE, systems=[ScoreSystem])
