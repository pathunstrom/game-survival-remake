from __future__ import annotations

import ppb

from shared import TITLE
from scenes import Sandbox
from systems import ScoreSystem

ppb.run(starting_scene=Sandbox, title=TITLE, systems=[ScoreSystem])
