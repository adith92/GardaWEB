from pathlib import Path
import pytest
from garda_vision.core import plate_candidates, load_cameras


def test_plates():
    assert "B 1234 XYZ" in plate_candidates("B 1234 XYZ")
    assert "D 888 AB" in plate_candidates("D888AB")
    assert plate_candidates("no plate") == []


def test_reject_embedded_credentials(tmp_path: Path):
    path = tmp_path / "cameras.json"
    path.write_text('[{"id":"CAM01","site_id":"LAB","rtsp_env":"rtsp://foo:bar@host"}]')
    with pytest.raises(ValueError):
        load_cameras(path)
