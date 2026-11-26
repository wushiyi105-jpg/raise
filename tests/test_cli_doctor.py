from __future__ import annotations

from typer.testing import CliRunner

from raiseup.doctor import run_doctor
from raiseup.iface.cli import app


def test_cli_readiness_empty_ok(tmp_path):
    runner = CliRunner()
    res = runner.invoke(app, ["readiness", "--db", str(tmp_path / "c.db")])
    assert res.exit_code == 0


def test_cli_check_flags_number(tmp_path):
    runner = CliRunner()
    res = runner.invoke(app, ["check", "--db", str(tmp_path / "n.db"), "--text", "我提升了 37%"])
    assert res.exit_code == 0
    assert "37" in res.stdout


def test_cli_bad_level_option(tmp_path):
    runner = CliRunner()
    assert runner.invoke(app, ["readiness", "--db", str(tmp_path / "x.db"), "--level", "P9"]).exit_code == 0


def test_doctor_green(settings):
    checks, ok = run_doctor(settings)
    assert ok is True
