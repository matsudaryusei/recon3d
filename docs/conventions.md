# 座標の規約

## OpenCV規約に統一

| 対象 | 規約 |
|---|---|
| 世界座標系 | 右手系、**+Z が上**（ターンテーブルの回転軸）、原点は回転台の中心 |
| カメラ座標系 | **OpenCV規約**：+X 右、+Y 下、**+Z が光軸の前方** |
| 画像座標系 | **OpenCV規約**：原点は左上ピクセルの中心、+u 右、+v 下 |
| 外部パラメータの向き | **world → camera**。すなわち `X_cam = R · X_world + t` |

イメージとしては、カメラから見て +X が右、+Y が下、被写体は +Z 方向にある。

- **R**：3×3の回転行列（rotation matrix）。世界座標系の向きからカメラ座標系の向きへの回転を表す。
- **t**：3次元の並進ベクトル（translation vector）。回転後の座標系での平行移動量を表す。

## Blender との変換

Blenderのカメラは **−Z 方向を見て、+Y が上**。OpenCVは **+Z 方向を見て、+Y が下**。Y軸とZ軸の符号が逆なため、python上ではこのように書く。

```python
C = np.diag([1.0, -1.0, -1.0])

R_cv = C @ R_blender
t_cv = C @ t_blender
```
画像の縦方向もBlenderとOpenCVで異なるため、次のように記述する。

```
v_cv = H - 1 - v_blender
```

ここで```H```は画像の高さである総ピクセル行数を指す。

## 禁止事項（重要）

座標変換を書いてよいのは ``` src/recon3d/io/coords.py ```の中だけにする。

他のファイルに ```diag(1,-1,-1)``` や``` H - 1 - v ```などの座標変換を禁止とする。

## 違反の検出方法

前述した禁止事項の検出方法としてテストプログラムである```tests/test_conventions.py```の配置をする。

```
# tests/test_conventions.py
def test_no_stray_coordinate_conversion():
    """io/coords.py 以外に座標変換のリテラルが現れないことを確認する。
    src/ 全体を走査し、diag(1, -1, -1) 相当のパターンを検出したら失敗。"""
```