"""座標変換。プロジェクト内で座標変換を書いてよいのはこのファイルだけ（docs/conventions.md）。"""

import numpy as np

# Blender ↔ OpenCV のカメラ座標変換行列（+Y と +Z の符号を反転する）
C = np.diag([1.0, -1.0, -1.0])


def blender_to_opencv_rt(R_blender: np.ndarray, t_blender: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    return C @ R_blender, C @ t_blender


def blender_v_to_opencv_v(v_blender: np.ndarray | float, height: int) -> np.ndarray | float:
    return height - 1 - v_blender


def world_to_camera(R, t, x_world):
    if x_world.ndim == 1:
        return R @ x_world + t
    elif x_world.ndim == 2:
        return x_world @ R.T + t
    else:
        raise ValueError(f"x_world.ndim={x_world.ndim} は想定外") # raiseはエラーを発生させる