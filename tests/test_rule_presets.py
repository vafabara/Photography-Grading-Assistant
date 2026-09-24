import pytest

from app.core.rules import Rule, RuleEngineConfig
from app.storage import rule_presets


@pytest.fixture(autouse=True)
def isolated_presets_file(tmp_path, monkeypatch):
    """
    Redirect rule_presets.PRESETS_FILE to a temporary file for every
    test in this file, so nothing here ever reads or writes the
    project's real rule_presets.json.
    """

    monkeypatch.setattr(rule_presets, "PRESETS_FILE", tmp_path / "rule_presets.json")
    return tmp_path


def make_config():

    return RuleEngineConfig(
        system_score=40,
        human_score=60,
        rules=[
            Rule(factor="iso", minimum=100.0, maximum=400.0),
            Rule(factor="aperture", minimum=2.0, maximum=8.0),
        ],
    )


class TestSaveAndLoadPresets:

    def test_round_trip_preserves_score_split_and_rules(self):

        rule_presets.save_preset("Portrait", make_config())

        loaded = rule_presets.load_presets()

        assert "Portrait" in loaded
        preset = loaded["Portrait"]

        assert preset.system_score == 40
        assert preset.human_score == 60
        assert [r.factor for r in preset.rules] == ["iso", "aperture"]
        assert preset.rules[0].minimum == 100.0
        assert preset.rules[0].maximum == 400.0

    def test_load_presets_returns_empty_dict_when_file_missing_or_corrupt(self, isolated_presets_file):

        # No file at all yet -- treated as "no presets saved".
        assert rule_presets.load_presets() == {}

        # A corrupt file must fail safe the same way class_storage
        # tolerates a corrupt class.json, rather than raising.
        isolated_presets_file.joinpath("rule_presets.json").write_text(
            "{not valid json", encoding="utf-8"
        )

        assert rule_presets.load_presets() == {}

    def test_save_preset_overwrites_same_name_without_duplicating_others(self):

        rule_presets.save_preset("Portrait", make_config())
        rule_presets.save_preset("Landscape", RuleEngineConfig(system_score=70, human_score=30, rules=[]))

        # Saving "Portrait" again with a different config must
        # replace it in place, not create a second entry, and must
        # leave the unrelated "Landscape" preset untouched.
        updated = RuleEngineConfig(system_score=20, human_score=80, rules=[])
        rule_presets.save_preset("Portrait", updated)

        loaded = rule_presets.load_presets()

        assert len(loaded) == 2
        assert loaded["Portrait"].system_score == 20
        assert loaded["Portrait"].rules == []
        assert loaded["Landscape"].system_score == 70
