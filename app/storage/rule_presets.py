"""
Persistence for reusable Rule Engine presets (new feature: Rule
Engine Presets).

A preset is a *reusable* RuleEngineConfig a professor can save once
(e.g. "Portrait") and load again for any future class's Rule Engine
screen. This is a different concept from ClassRecord.rule_config
(core.class_model), which is the actual configuration a specific
class was graded with -- a preset can be edited or deleted later
without changing what an already-graded class remembers using.

Mirrors storage/class_storage.py: plain JSON on disk, no database.
Everything lives in a single flat file since presets are small and
there's no per-preset data beyond the config itself:

    rule_presets.json  ->  {"Portrait": {...RuleEngineConfig...}, ...}

GUI code never touches this module directly -- only App (the
controller) calls load_presets()/save_preset() and hands the result
to RuleEngineScreen to render, the same pattern used for classes.
"""

import json
from pathlib import Path

from ..core.rules import RuleEngineConfig

PRESETS_FILE = Path(__file__).resolve().parents[2] / "rule_presets.json"


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
        data = {
            preset_name: preset_config.to_dict()
            for preset_name, preset_config in presets.items()
        }

        with open(PRESETS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    except OSError as error:
        raise RulePresetError(f"Could not save preset: {error}")
