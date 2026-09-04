import re
from pathlib import Path
import pytest
import numpy as np
from recon3d.io.coords import blender_to_opencv_rt, blender_v_to_opencv_v
import json
from recon3d.io.cameras import load_cameras

FORBIDDEN_PATTERNS = [
    # diag(1, -1, -1) や diag([1.0, -1.0, -1.0]) など、±1を3つ並べる対角行列の書き方
    re.compile(r"diag\(\s*\[?\s*-?1(\.0)?\s*,\s*-?1(\.0)?\s*,\s*-?1(\.0)?"),

    # H - 1 - v のような画像縦方向の反転（変数名がH/v以外でも拾えるよう緩めにしている）
    re.compile(r"\b\w*[Hh]\w*\s*-\s*1\s*-\s*\w*[vV]\w*\b"),

    # [[1,0,0],[0,-1,0],[0,0,-1]] のような3x3対角行列の直書き
    re.compile(
        r"\[\s*\[\s*-?1\s*,\s*0\s*,\s*0\s*\]\s*,\s*"
        r"\[\s*0\s*,\s*-?1\s*,\s*0\s*\]\s*,\s*"
        r"\[\s*0\s*,\s*0\s*,\s*-?1\s*\]\s*\]"
    ),
]

# テスト対象のコードに座標変換の処理が散在していないかをチェックするテスト
def test_no_stray_coordinate_conversion():
    src_dir = Path(__file__).resolve().parents[1] / "src"
    coords_file = src_dir / "recon3d" / "io" / "coords.py"

    py_files = list(src_dir.rglob("*.py"))
    assert len(py_files) > 0, "走査対象が0件（パスが間違っている可能性）"  # ← 空振り防止の1行

    for path in py_files:
        if path == coords_file:
            continue
        text = path.read_text(encoding="utf-8")
        for pattern in FORBIDDEN_PATTERNS:
            if pattern.search(text):
                pytest.fail(f"{path}: 座標変換は io/coords.py に書くこと")

# Blender→OpenCVの回転・並進の変換が仕様通りかを確認するテスト（単位行列のケース）
def test_identity_rotation():
    R_blender = np.eye(3)
    t_blender = np.array([0.0, 0.0, 5.0])

    R_cv, t_cv = blender_to_opencv_rt(R_blender, t_blender)

    expected_R_cv = np.array([[1.0, 0.0, 0.0],
                              [0.0, -1.0, 0.0],
                              [0.0, 0.0, -1.0]])
    expected_t_cv = np.array([0.0, 0.0, -5.0])

    np.testing.assert_allclose(R_cv, expected_R_cv)
    np.testing.assert_allclose(t_cv, expected_t_cv)

# 変換後のR_cvが壊れていない回転行列か（直交行列かつdet=+1）を確認するテスト
def test_rotation_is_orthogonal():
    R_blender = np.eye(3)
    t_blender = np.array([0.0, 0.0, 5.0])
    R_cv, _ = blender_to_opencv_rt(R_blender, t_blender)

    np.testing.assert_allclose(R_cv.T @ R_cv, np.eye(3), atol=1e-10)
    assert np.isclose(np.linalg.det(R_cv), 1.0)

# 画像縦方向の反転が両端（v=0とv=H-1）で正しく対応するかを確認するテスト
def test_v_edges():
    H = 1080 # サンプル値
    assert blender_v_to_opencv_v(0, H) == H - 1
    assert blender_v_to_opencv_v(H - 1, H) == 0

def valid_camera_dict():
    return {
        "schema_version": "1.0",
        "convention": {
            "world_up": "+Z",
            "handedness": "right",
            "camera": "opencv",
            "image_origin": "top_left",
            "extrinsic_form": "world_to_camera",
        },
        "image_size": {"width": 1920, "height": 1080},
        "intrinsics": {
            "fx": 1600.0, "fy": 1600.0,
            "cx": 960.0,  "cy": 540.0,
            "distortion": {
                "model": "opencv_radtan",
                "k1": 0.0, "k2": 0.0, "p1": 0.0, "p2": 0.0, "k3": 0.0,
            },
        },
        "views": [
            {
                "image": "images/img_000.png",
                "mask": "masks/img_000.png",
                "R": [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
                "t": [0.0, 0.0, 0.5],
                "source": "turntable_gt",
                "turntable_angle_deg": 0.0,
                "reprojection_error_px": None,
            }
        ],
        "meta": {
            "generated_by": "tools/blender_render.py",
            "generated_at": "2026-08-20T10:00:00+09:00",
            "dataset": "synthetic_cup_20views",
        },
    }

def test_load_valid_cameras(tmp_path):
    path = tmp_path / "cameras.json"
    path.write_text(json.dumps(valid_camera_dict()))
    cameras = load_cameras(path)
    assert cameras.schema_version == "1.0"

def test_wrong_schema_version_raises(tmp_path):
    data = valid_camera_dict()
    data["schema_version"] = "invalid"           # ここで意図的に1か所だけ壊す

    path = tmp_path / "cameras.json"
    path.write_text(json.dumps(data))

    with pytest.raises(ValueError):     # load_cameras()が投げる例外の型
        load_cameras(path)

def test_wrong_convention_raises(tmp_path):
    data = valid_camera_dict()
    data["convention"]["world_up"] = "invalid"   # convention内のどれか1キーを規約と違う値に

    path = tmp_path / "cameras.json"
    path.write_text(json.dumps(data))
    
    with pytest.raises(ValueError):     # load_cameras()が投げる例外の型
        load_cameras(path)

def test_non_orthogonal_R_raises(tmp_path):
    data = valid_camera_dict()
    data["views"][0]["R"] = [[1, 0, 0],
                             [0, 1, 0],
                             [0, 0, 0]]   # R^T R ≈ I が崩れる行列に

    path = tmp_path / "cameras.json"
    path.write_text(json.dumps(data))
    
    with pytest.raises(ValueError):     # load_cameras()が投げる例外の型
        load_cameras(path)

def test_mirrored_R_raises(tmp_path):
    data = valid_camera_dict()
    data["views"][0]["R"] = [[1, 0, 0],
                             [0, 1, 0],
                             [0, 0, -1]]  # 直交はしているがdet = -1の行列に
    path = tmp_path / "cameras.json"
    path.write_text(json.dumps(data))

    with pytest.raises(ValueError):     # load_cameras()が投げる例外の型
        load_cameras(path)