from pathlib import Path

ROOT = Path(__file__).resolve().parent
RESOURCES = ROOT / "resources"
ENV = ROOT / ".env"

MODEL = RESOURCES / "model"
QUOTES = RESOURCES / "oenomaus_quotes.txt"
LAUGHING_GLADIATORS = RESOURCES / "laughing_gladiators.gif"
CURRENT_WHIP = RESOURCES / "current_whip.gif"
WHIP_BASE = RESOURCES / "whip_cropped_small.gif"
