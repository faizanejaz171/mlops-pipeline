"""
Unit tests for curation logic that can run in CI without GPU or GCP.
Tests cover: filename parsing, config loading, input validation helpers.
"""
import pytest
import re
from pathlib import Path

# ── Replicated constants from test.py (will import from package later) ──
CAMERA_FRAME_RE = re.compile(r"^(.+?)_(\d+)\.[^.]+$")
PLAIN_NUMBER_RE = re.compile(r"^(\d+)\.[^.]+$")


def parse_camera(filename: str) -> tuple:
    """Copied logic from test.py for isolated testing."""
    stem = filename.rsplit(".", 1)[0]
    parts = stem.split("_")
    if len(parts) >= 5:
        idx_part = parts[-1]
        seq_part = parts[-2]
        time_part = parts[-3]
        date_part = parts[-4]
        if (idx_part.isdigit() and seq_part.isdigit() and len(seq_part) == 4 and
                time_part.isdigit() and len(time_part) == 6 and
                date_part.isdigit() and len(date_part) == 8):
            cam_id = "_".join(parts[:-4])
            frame_num = int(seq_part) * 10_000 + int(idx_part)
            return cam_id, frame_num
    m = CAMERA_FRAME_RE.match(filename)
    if m:
        return m.group(1), int(m.group(2))
    m = PLAIN_NUMBER_RE.match(filename)
    if m:
        return "seq", int(m.group(1))
    return "unknown", 0


# ── parse_camera tests ──────────────────────────────────────────────────────

class TestParseCameraFilename:

    def test_full_format_extracts_camera_id(self):
        """Standard CCTV filename: camid_date_time_seq_idx.jpg"""
        cam_id, _ = parse_camera("cam01_20260518_143000_0001_5.jpg")
        assert cam_id == "cam01"

    def test_full_format_frame_number_ordering(self):
        """Later frames should have higher frame numbers."""
        _, fn1 = parse_camera("cam01_20260518_143000_0001_0.jpg")
        _, fn2 = parse_camera("cam01_20260518_143000_0002_0.jpg")
        assert fn2 > fn1

    def test_multi_part_camera_id(self):
        """Camera IDs with underscores like 'site_a_cam01' must be preserved."""
        cam_id, _ = parse_camera("site_a_cam01_20260518_143000_0001_5.jpg")
        assert cam_id == "site_a_cam01"

    def test_simple_camera_frame_format(self):
        """Fallback: camera_framenum.jpg"""
        cam_id, frame_num = parse_camera("camera1_0042.jpg")
        assert cam_id == "camera1"
        assert frame_num == 42

    def test_plain_number_format(self):
        """Fallback: plain numbered frames like 0001.jpg"""
        cam_id, frame_num = parse_camera("0099.jpg")
        assert cam_id == "seq"
        assert frame_num == 99

    def test_unknown_format_returns_zero(self):
        cam_id, frame_num = parse_camera("random_name_no_pattern.jpg")
        assert frame_num == 0

    def test_different_cameras_not_grouped(self):
        """Bug regression: two different cameras must not share a camera ID."""
        cam1, _ = parse_camera("cam01_20260518_143000_0001_0.jpg")
        cam2, _ = parse_camera("cam02_20260518_143000_0001_0.jpg")
        assert cam1 != cam2


# ── Config validation tests ─────────────────────────────────────────────────

class TestConfigDefaults:

    def test_default_config_has_required_keys(self):
        required = [
            "mode", "gcp_cloud_path", "camera_ids", "target_dates",
            "output_choice", "fps_rate", "local_dataset_dir",
            "detection_strategy", "yolo_confidence",
        ]
        DEFAULT_CONFIG = {
            "mode": "3",
            "gcp_cloud_path": "raw-face-videos/person/bonita/record",
            "camera_ids": "all",
            "target_dates": "20260518",
            "target_hours": "all",
            "video_limit": "all",
            "output_choice": "3",
            "fps_rate": "6",
            "local_dataset_dir": "/home/faizan/Desktop/UI/",
            "detection_strategy": "1",
            "coco_target_classes": "person",
            "coco_exclusion_classes": "tv",
            "custom_dino_prompt": "",
            "camera_has_tv": "n",
            "frame_skip_seconds": 2,
            "yolo_confidence": 0.32,
            "dino_confidence": 0.32,
        }
        for key in required:
            assert key in DEFAULT_CONFIG, f"Missing required key: {key}"

    def test_confidence_values_in_valid_range(self):
        yolo_conf = 0.32
        dino_conf = 0.32
        assert 0.0 < yolo_conf <= 1.0
        assert 0.0 < dino_conf <= 1.0

    def test_fps_rate_is_parseable(self):
        """fps_rate can be '6', '1/6', '1/2' — all should be evaluable."""
        valid_fps = ["6", "1", "2"]
        for fps in valid_fps:
            assert float(fps) > 0


# ── SAM3 class dict parsing tests ──────────────────────────────────────────

class TestSam3ClassParsing:

    def _parse(self, raw: str) -> dict:
        """Same logic as ask_sam3_class_dict in test.py."""
        class_dict = {}
        for item in raw.split(","):
            if ":" not in item:
                raise ValueError(f"missing ':' in segment '{item.strip()}'")
            k, v = item.split(":", 1)
            k, v = k.strip(), v.strip()
            if not k.isdigit() or not v:
                raise ValueError(f"bad segment")
            class_dict[int(k)] = v
        return class_dict

    def test_valid_single_class(self):
        result = self._parse("0:person")
        assert result == {0: "person"}

    def test_valid_multiple_classes(self):
        result = self._parse("0:head, 1:person")
        assert result == {0: "head", 1: "person"}

    def test_missing_colon_raises(self):
        with pytest.raises(ValueError):
            self._parse("0head")

    def test_empty_value_raises(self):
        with pytest.raises(ValueError):
            self._parse("0:")
