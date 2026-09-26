import json
from pathlib import Path

from ..core.rules import RuleEngineConfig
from .class_storage import CLASSES_DIR

PRESETS_FILE = CLASSES_DIR / "rule_presets.json"


class RulePresetError(Exception):
    """Raised when a preset operation fails."""


def load_presets():
    """
    Returns {name: RuleEngineConfig}. A missing or corrupt file is
    treated as "no presets saved yet" rather than an error -- same
    tolerance class_storage.load_all_classes() has for a bad class
    folder.
    """

    if not PRESETS_FILE.exists():
        return {}

    try:
        with open(PRESETS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        return {
            name: RuleEngineConfig.from_dict(config_data)
            for name, config_data in data.items()
        }

    except (json.JSONDecodeError, OSError, KeyError):
        return {}


def save_preset(name, config):
    """
    Save/overwrite one named preset (`config` is a RuleEngineConfig)
    and persist the full preset file back to disk immediately, so
    the Rule Engine screen's preset list is accurate the moment it's
    reloaded.
    """

    presets = load_presets()
    presets[name] = config

    try:
        CLASSES_DIR.mkdir(parents=True, exist_ok=True)

        data = {
            preset_name: preset_config.to_dict()
            for preset_name, preset_config in presets.items()
        }

        with open(PRESETS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    except OSError as error:
        raise RulePresetError(f"Could not save preset: {error}")