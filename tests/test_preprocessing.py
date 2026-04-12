import pytest

from src.data.preprocessing import apply_export_rule


def _row(zone, raw_mw):
    return {"timestamp": "2024-06-15T17:00:00Z", "zone": zone, "raw_net_load_mw": raw_mw}


class TestExportRuleA:
    def test_positive_load_passes_through(self):
        rows = apply_export_rule([_row("NORTH", 100.0)], rule="A")
        assert rows[0]["load_mw"] == 100.0

    def test_negative_load_clamped_to_zero(self):
        rows = apply_export_rule([_row("WEST", -50.0)], rule="A")
        assert rows[0]["load_mw"] == 0.0


class TestExportRuleB:
    def test_positive_load_passes_through(self):
        rows = apply_export_rule([_row("NORTH", 100.0)], rule="B")
        assert rows[0]["load_mw"] == 100.0

    def test_negative_load_preserved(self):
        rows = apply_export_rule([_row("WEST", -50.0)], rule="B")
        assert rows[0]["load_mw"] == -50.0


class TestExportRuleC:
    def test_positive_load_no_export(self):
        rows = apply_export_rule([_row("NORTH", 100.0)], rule="C")
        assert rows[0]["load_mw"] == 100.0
        assert rows[0]["export_mw"] == 0.0
        assert rows[0]["export_interval_flag"] == 0

    def test_negative_load_flagged_as_export(self):
        rows = apply_export_rule([_row("WEST", -50.0)], rule="C")
        assert rows[0]["load_mw"] == 0.0
        assert rows[0]["export_mw"] == 50.0
        assert rows[0]["export_interval_flag"] == 1


class TestExportRuleInvalid:
    def test_unknown_rule_raises(self):
        with pytest.raises(ValueError, match="Unknown export rule"):
            apply_export_rule([_row("NORTH", 100.0)], rule="Z")

    def test_empty_input(self):
        assert apply_export_rule([], rule="A") == []
