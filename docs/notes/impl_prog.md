# Pythonでの実装プログラムについて 2026/9/5

`src/`配下の実装コードに関するメモ。

## ステップ5：coords.py の実装

`src/recon3d/io/coords.py`に3つの関数を実装した。

```python
C = np.diag([1.0, -1.0, -1.0])

def blender_to_opencv_rt(R_blender, t_blender):
    return C @ R_blender, C @ t_blender

def blender_v_to_opencv_v(v_blender, height):
    return height - 1 - v_blender

def world_to_camera(R, t, x_world):
    if x_world.ndim == 1:
        return R @ x_world + t
    elif x_world.ndim == 2:
        return x_world @ R.T + t
    else:
        raise ValueError(f"x_world.ndim={x_world.ndim} は想定外")
```

**`world_to_camera`の`ndim==2`側は、当初`(R @ x_world.T).T + t`だったが`x_world @ R.T + t`に変更した。** 転置の性質`(A @ B).T = B.T @ A.T`より、`(R @ x_world.T).T = x_world @ R.T`は数学的に完全に同じ結果になる。転置が2回から1回に減り、読みやすくもなるため採用。

### 各関数の目的

- `blender_to_opencv_rt`：Blender規約の`(R, t)`をOpenCV規約に変換する。テスト2で確認済みの変換式（`C @ R`, `C @ t`）をそのまま実装
- `blender_v_to_opencv_v`：画像の縦座標をBlender/OpenGL（左下原点）からOpenCV（左上原点）に変換する。`v_edges`テストで確認済みの`H - 1 - v`を実装
- `world_to_camera`：`X_cam = R @ X_world + t`の実装。**1点`(3,)`でも複数点`(N,3)`でもまとめて計算できるようにする**必要があり、`ndim`（後述）で分岐している

### world_to_camera の役割

「世界のどこかにある点」を「そのカメラから見た座標」に変換する関数。3D再構成の流れの中では

```
世界座標の点 → [world_to_camera] → カメラ座標の点 → 内部パラメータで投影 → 画像上のピクセル座標
```

の最初のステップにあたる。複数点をまとめて扱えるようにしているのは、G5（ボクセル）で大量の格子点を一度に変換する必要があるため。

### ndim とは

`np.ndarray`が持つ属性で、**配列の軸（次元）の本数**を表す整数。`shape`が「各軸の長さ」を教えるのに対し、`ndim`は「軸が何本あるか」だけを教える（`ndim == len(shape)`）。

```python
np.array([1, 2, 3]).ndim              # 1（形は(3,)、1点のベクトル）
np.array([[1,2,3],[4,5,6]]).ndim      # 2（形は(2,3)、複数点をまとめた行列）
```

`world_to_camera`では、`x_world.ndim`を見て「1点だけ渡されたか、複数点まとめて渡されたか」を判定し、計算方法を分岐させている。

### np.ndarray とは

NumPyが提供する配列専用のクラス（型）。`np.array(...)`や`np.eye(3)`などはすべてこの`ndarray`のオブジェクトを返す。普通の`list`と違い、**全要素が同じ型でメモリ上に並んでおり、`@`（行列積）や要素ごとの`+`など、まとめて高速に計算できる演算が使える**のが特徴。関数の引数に`R: np.ndarray`のように書くのは、「NumPy配列を渡してほしい」という意図を示す型ヒント。

## cameras.py の実装

`src/recon3d/io/cameras.py`に、dataclass（`Convention`・`Intrinsics`・`View`・`CameraSet`）と3つの関数（`load_cameras`・`save_cameras`・`validate`）を実装した。全体の目的は「`cameras.json`を安全に読み書きし、壊れたデータが紛れ込まないよう入口と出口の両方で検証する」こと。

### 各dataclassの目的

- `Convention`：座標系の規約（`world_up`など5項目）を表す。`cameras.json`自身に規約を埋め込み、想定と違えば読み込み時に弾けるようにするため（[docs/plan.md:558](../plan.md#s5-2)）
- `Intrinsics`：カメラの内部パラメータ（焦点距離・主点）を表す
- `View`：1台のカメラ（1枚の画像）の情報（画像パス・外部パラメータ・由来など）を表す
- `CameraSet`：`cameras.json`1ファイル全体に対応するトップレベルのまとまり

### Intrinsics に distortion フィールドを追加した理由

`docs/plan.md`§5-1のJSONには`intrinsics.distortion`（`k1,k2,p1,p2,k3`などの歪み係数）があるが、[タスク手順書](../tasks/T01-pairpro1-io.md)の骨組みには`Intrinsics`にこのフィールドが無かった（コメントで「distortionはdictのままでよい」とあるのみ）。

現状すべて`0.0`固定で実際には使っていない値だが、**フィールドが無いと読み込み時に情報が失われる**ため、専用のdataclassは作らず`distortion: dict`という素の辞書型フィールドとして追加することにした。

```python
@dataclass
class Intrinsics:
    fx: float
    fy: float
    cx: float
    cy: float
    distortion: dict
```

### load_cameras の目的と設計

**目的**：`cameras.json`を読み込み、壊れていないことを確認した上で`CameraSet`として返す（壊れたデータを後続の処理に渡さないための入口の防波堤）。

```python
def load_cameras(path: Path) -> CameraSet:
    text = path.read_text(encoding="utf-8")
    data = json.loads(text)

    convention = Convention(**data["convention"])
    intrinsics = Intrinsics(
        fx=data["intrinsics"]["fx"], fy=data["intrinsics"]["fy"],
        cx=data["intrinsics"]["cx"], cy=data["intrinsics"]["cy"],
        distortion=data["intrinsics"]["distortion"],
    )
    image_size = (data["image_size"]["width"], data["image_size"]["height"])
    views = [View(**v) for v in data["views"]]

    cameras = CameraSet(
        schema_version=data["schema_version"], convention=convention,
        image_size=image_size, intrinsics=intrinsics, views=views, meta=data["meta"],
    )
    validate(cameras)
    return cameras
```

- JSON文字列→`dict`（`json.loads`）→ 各dataclassを`**`展開で組み立て（`Convention(**data["convention"])`など、キー名がdataclassのフィールド名と一致しているため使える）
- `image_size`（タプル）は`{"width":..,"height":..}`という辞書と相互変換が必要なので、`**`展開が使えず個別に組み立てている
- 最後に`validate()`を通してから返す（ここで壊れていれば`ValueError`が飛び、呼び出し元に伝わる）

### save_cameras の目的と設計

**目的**：`CameraSet`を`cameras.json`として書き出す（壊れた状態のデータを誤って世に出さないための出口の防波堤）。`load_cameras`のちょうど逆方向の変換を行う。

- 先に`validate()`を通す（書き出す前に壊れていないか確認）
- 各dataclassを`.__dict__`で素の辞書に戻し、`image_size`はタプルから`{"width":..,"height":..}`に戻す
- `json.dumps(indent=4, ensure_ascii=False)`で読みやすい形に整形して書き出す

### validate の目的と設計（完成）

**目的**：`CameraSet`が規約通りの壊れていないデータかを検証し、[docs/plan.md§5-3](../plan.md#s5-3)の4項目のいずれかが崩れていれば`ValueError`を投げる。`load_cameras`・`save_cameras`の両方から呼ばれる、検証ロジックの本体。

```python
def validate(cameras: CameraSet) -> None:
    if cameras.schema_version != SCHEMA_VERSION:
        raise ValueError(f"schema_version={cameras.schema_version} は想定外")

    if cameras.convention != Convention(
        world_up="+Z", handedness="right", camera="opencv",
        image_origin="top_left", extrinsic_form="world_to_camera",
    ):
        raise ValueError(f"convention={cameras.convention} は想定外")

    for view in cameras.views:
        R = np.array(view.R)
        if not np.allclose(R.T @ R, np.eye(3), atol=1e-6):
            raise ValueError(f"{view.image}: Rが直交行列でない")
        if not np.isclose(np.linalg.det(R), 1.0):
            raise ValueError(f"{view.image}: det(R)={np.linalg.det(R):.3f} は鏡映の可能性")
```

- **項目1（schema_version）**：単純な文字列比較
- **項目2（convention）**：あるべき正しい`Convention`をその場で1個作り、`!=`で比較。`@dataclass`は`__eq__`を自動生成するので、`!=`だけで5フィールド全部の一致判定ができる
- **項目3・4（R）**：`cameras.views`は複数ありうるので`for`でループし、1つずつチェック。`view.R`は`list[list[float]]`のままなので`np.array(view.R)`で`ndarray`に変換してから`.T`・`@`・`np.linalg.det`を使う。`np.allclose`/`np.isclose`は`assert`せず`True`/`False`を返すので、`if not ...:`と組み合わせて使う
- エラーメッセージに`view.image`を含めることで、複数視点のうちどれが壊れているか特定できるようにしている

`uv run pytest tests/test_conventions.py -v`で9件全てpass済み。