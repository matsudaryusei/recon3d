"""cameras.json の読み書きと検証（docs/schema/cameras.md）。

追加依存は入れない。dataclass と json だけで書く（D-17）。
"""

from dataclasses import dataclass
from pathlib import Path
import json
import numpy as np


SCHEMA_VERSION = "1.0"


@dataclass
class Convention:
    world_up: str
    handedness: str
    camera: str
    image_origin: str
    extrinsic_form: str


@dataclass
class Intrinsics:
    fx: float
    fy: float
    cx: float
    cy: float
    distortion: dict


@dataclass
class View:
    image: str
    mask: str | None
    R: list[list[float]]
    t: list[float]
    source: str                      # "turntable_gt" | "dlt" | "bundle_adjusted"
    turntable_angle_deg: float | None
    reprojection_error_px: float | None


@dataclass
class CameraSet:
    schema_version: str
    convention: Convention
    image_size: tuple[int, int]
    intrinsics: Intrinsics
    views: list[View]
    meta: dict


def load_cameras(path: Path) -> CameraSet:
    text = path.read_text(encoding="utf-8")
    data = json.loads(text)

    convention = Convention(**data["convention"])

    intrinsics = Intrinsics(
        fx=data["intrinsics"]["fx"],
        fy=data["intrinsics"]["fy"],
        cx=data["intrinsics"]["cx"],
        cy=data["intrinsics"]["cy"],
        distortion=data["intrinsics"]["distortion"]
    )

    image_size = (data["image_size"]["width"], data["image_size"]["height"])

    views = [View(**v) for v in data["views"]]

    cameras = CameraSet(
        schema_version=data["schema_version"],
        convention=convention,
        image_size=image_size,
        intrinsics=intrinsics,
        views=views,
        meta=data["meta"],
    )

    validate(cameras)
    return cameras


def save_cameras(cameras: CameraSet, path: Path) -> None:
    """書き出す前に validate() を通す。壊れたファイルを世に出さない。"""
    validate(cameras)

    data = {
        "schema_version": cameras.schema_version,
        "convention": cameras.convention.__dict__,
        "image_size": {"width": cameras.image_size[0], "height": cameras.image_size[1]},
        "intrinsics": {
            "fx": cameras.intrinsics.fx,
            "fy": cameras.intrinsics.fy,
            "cx": cameras.intrinsics.cx,
            "cy": cameras.intrinsics.cy,
            "distortion": cameras.intrinsics.distortion,
        },
        "views": [v.__dict__ for v in cameras.views],
        "meta": cameras.meta,
    }

    text = json.dumps(data, indent=4, ensure_ascii=False)
    path.write_text(text, encoding="utf-8")


def validate(cameras: CameraSet) -> None:
    """4項目を検査し、違反があれば ValueError を投げる。

    1. schema_version が SCHEMA_VERSION と一致するか
    2. convention が docs/conventions.md の値と一致するか
    3. すべての R について R.T @ R ≈ I
    4. すべての R について det(R) ≈ +1   ← 符号ミス（鏡映）の検出
    """
    if cameras.schema_version != SCHEMA_VERSION:
        raise ValueError(f"schema_version={cameras.schema_version} は想定外")

    if cameras.convention != Convention(
        world_up="+Z",
        handedness="right",
        camera="opencv",
        image_origin="top_left",
        extrinsic_form="world_to_camera",
    ):
        raise ValueError(f"convention={cameras.convention} は想定外")

    for view in cameras.views:
        R = np.array(view.R)

        if not np.allclose(R.T @ R, np.eye(3), atol=1e-6):
            raise ValueError(f"{view.image}: Rが直交行列でない")

        if not np.isclose(np.linalg.det(R), 1.0):
            raise ValueError(f"{view.image}: det(R)={np.linalg.det(R):.3f} は鏡映の可能性")    
    