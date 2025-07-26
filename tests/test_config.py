import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]/"src"))
from crypto.config.loader import load_config


def test_load_config(tmp_path):
    cfg_text = """
exchange:
  api_key: key
"""
    cfg_file = tmp_path / "cfg.yml"
    cfg_file.write_text(cfg_text)
    cfg = load_config(cfg_file)
    assert cfg["exchange"]["api_key"] == "key"
