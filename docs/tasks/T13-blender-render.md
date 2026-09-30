# T13 — `tools/blender_render.py` を実装する（20方向レンダリング）

[← 次にやること一覧に戻る](../next.md)

| | |
|---|---|
| ジャンル | **G2 3DCG・データ生成** |
| 目安時間 | 10時間前後（実装が中心。**環境と出力の確認は下にすべて書いてある**） |
| 前提 | [T11](T11-decide-mask-method.md)（マスク方式）・[T12](T12-prepare-blend.md)（`cup.blend`・長さの単位）が完了。**Blender 5.0.1（松田の端末）** |
| 作るもの | **`tools/blender_render.py`**。出力は `data/synthetic_cup/` の `images/`・`masks/`・`cameras.json`・`gt_mesh.ply` |
| 出どころ | [計画書 §2](../plan.md#s2)・[§4-2](../plan.md#s4-2)・[§5](../plan.md#s5)・[§7-4](../plan.md#s7-4)・[§7-6](../plan.md#s7-6)・[cameras.md](../schema/cameras.md)・[D-43（T11）](../decisions.md) |

---

## 着手前に読むもの

| 初めて出てくること | 資料 |
|---|---|
| `bpy` でカメラ・レンダリングを動かす | [学びの入口 G2](../learning.md) の Blender API クイックスタート |
| **ピンホールカメラの内部パラメータ（`fx`・`cx`）** | [Szeliski 本](https://szeliski.org/Book/) のカメラモデルの節／[cameras.md](../schema/cameras.md) の `intrinsics` |
| Blender のカメラ向き（−Z を見る・+Y が上）と OpenCV の違い | [計画書 §4-2](../plan.md#s4-2) と [conventions.md](../conventions.md) |
| Blender 5.0 のコンポジタ API の変更（`node_tree` が使えない） | [mask-options.md の落とし穴の表](../notes/mask-options.md)・[T07 トラブルシュート](../notes/T07-blender5-cli-troubleshooting.md) |

---

## なぜやるのか

**このスクリプトが、プロジェクト全体の「正解」を作ります。** 画像・マスク・カメラ行列・真値メッシュのすべてがここから出るので、
**ここで座標を間違えると、下流（G1・G3・G5）の出力が全部静かに壊れます**（[計画書 §4](../plan.md#s4)）。

**そして接続点は `cameras.json` だけです**（[計画書 §3-5](../plan.md#s3-5)）。G1 は Blender を持っていないので、**関口は出力ファイルだけを頼りに動きます。** 出力の形が仕様どおりであることが、いちばん大事な成果物です。

> **本体は「カメラの置き方」と「Blender の姿勢から `R`・`t` を導くこと」です。** ここには答えを書いていません。書いてあるのは**環境・出力の場所・確認の仕方**だけです。

---

## ステップ1：ブランチと足場

```bash
git switch main && git pull origin main
git switch -c feat/blender-render
```

---

## ステップ2：スクリプトの骨組み（手順どおりに置く）

**次の骨組みを `tools/blender_render.py` に貼ります。`TODO` の中が実装です。**

```python
"""synthetic データセットを Blender で生成する（G2）。

使い方（リポジトリのルートで）:
    blender -b data/synthetic_cup/cup.blend -P tools/blender_render.py -- \
        --out data/synthetic_cup --views 20 --width 640 --height 480

Blender 内蔵 Python で動く。依存は bpy と numpy のみ（計画書 §7-4）。
"""

import argparse
import sys
from pathlib import Path

import bpy
import numpy as np

# recon3d は Blender の Python には入っていないので、src/ を検索パスに足す。
# io/cameras.py・io/coords.py は標準ライブラリと numpy だけで書いてあるので読める。
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from recon3d.io.cameras import CameraSet, View, save_cameras, validate  # noqa: E402
from recon3d.io.coords import blender_to_opencv_rt  # noqa: E402


def parse_args() -> argparse.Namespace:
    # Blender 自身の引数と混ざらないよう、"--" より後ろだけを読む。
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--views", type=int, default=20)
    p.add_argument("--width", type=int, default=640)
    p.add_argument("--height", type=int, default=480)
    return p.parse_args(argv)


def setup_render(scene, width: int, height: int) -> None:
    """レンダリング設定。T11 の決定（D-43）と計画書 §7-6 に従う。"""
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.resolution_percentage = 100
    scene.view_settings.view_transform = "Standard"   # 色管理の影響を消す（D-20）
    scene.render.dither_intensity = 0.0               # ディザを切る
    # TODO: レンダラ（D-43 で決めたもの）／サンプル数／背景色


def camera_pose(angle_deg: float) -> ...:
    """回転角から、Blender のカメラの位置・向きを決める。

    TODO: ここが本体。世界座標は「+Z が上・原点は回転台の中心」（計画書 §4-1）。
    カメラは何を見て、どの高さから、原点を中心にどう回るか。
    """
    raise NotImplementedError


def intrinsics_from_blender(cam_data, width: int, height: int) -> dict:
    """Blender のカメラ設定（焦点距離 mm・センサー幅）から fx, fy, cx, cy を出す。

    TODO: ここも導出。ピクセル単位の焦点距離は何と何の比で決まるか。
    センサーフィット（sensor_fit）が AUTO のときの扱いに注意。
    """
    raise NotImplementedError


def render_view(scene, image_path: Path, mask_path: Path) -> None:
    """1視点ぶんの画像とマスクを出す。マスクの出し方は D-43 に従う。"""
    raise NotImplementedError


def export_gt_mesh(obj, path: Path) -> None:
    """被写体の真値メッシュを .ply で出す（世界座標・単位は T12 で決めたもの）。"""
    raise NotImplementedError


def main() -> None:
    args = parse_args()
    (args.out / "images").mkdir(parents=True, exist_ok=True)
    (args.out / "masks").mkdir(parents=True, exist_ok=True)
    scene = bpy.context.scene
    setup_render(scene, args.width, args.height)

    # TODO: 視点ごとに camera_pose → レンダリング → R, t を記録
    #   R, t は blender_to_opencv_rt(...) を通す（座標変換を他の場所に書かない: 規約 D-11）
    # TODO: CameraSet を組み、source="turntable_gt" で save_cameras()、その前に validate()


if __name__ == "__main__":
    main()
```

> **`io/coords.py` の外で `diag(1, -1, -1)` や `H - 1 - v` を書かないでください。** [`tests/test_conventions.py`](../../tests/test_conventions.py) が落ちます（[計画書 §4-3](../plan.md#s4-3)）。座標変換は **`blender_to_opencv_rt` を呼ぶ**だけです。

---

## ステップ3：1枚だけ通す → 20枚にする（この順で）

**いきなり20枚にしない。** 1枚で出力の形を確認してから増やします。

```powershell
# まず1視点（--views 1）
& "C:\Program Files\Blender Foundation\Blender 5.0\blender.exe" -b data\synthetic_cup\cup.blend -P tools\blender_render.py -- --out data\synthetic_cup --views 1

# 出力を見る
dir data\synthetic_cup\images
dir data\synthetic_cup\masks
```

1枚が正しく出たら `--views 20`。**時間を測って `docs/notes/` に残す**（W03 の実測値に使う。EEVEE・640×480 で何秒か）。

---

## ステップ4：出力を検証する（**これが完了判定の中身**）

**「動いた」ではなく、次の4つを観察して確かめます。**

| # | 見るもの | どうやって | 合格 |
|---|---|---|---|
| 1 | `cameras.json` が仕様どおり | 関口の端末でも `uv run python -c "from pathlib import Path; from recon3d.io.cameras import load_cameras, validate; c = load_cameras(Path('data/synthetic_cup/cameras.json')); validate(c); print(len(c.views), c.views[0].source)"` | エラーなし。`20 turntable_gt` |
| 2 | マスクが二値 | `python -c "import numpy as np, cv2; m = cv2.imread('data/synthetic_cup/masks/img_000.png', 0); print(np.unique(m))"`（opencv が要る場合は [T15](T15-opencv-pipeline.md) のあと） | `[  0 255]` の2つだけ |
| 3 | **`R`・`t` が画像と一致している** | `gt_mesh.ply` の頂点を `cameras.json` の `K`・`R`・`t` で自分で投影し、マスク上に点を打つ | **ほぼ全部の点が白（255）の領域に入る。** ずれるなら座標変換の符号か `cx, cy` を疑う |
| 4 | 画像の並びが回転順 | `img_000`〜`img_019` を並べて見る | 被写体が一方向に回っていく |

> **3 が本題です。** 1・2 は形式の確認で、**3 が通って初めて「正解データ」と呼べます。** 3 の確認スクリプトは、自分で書いて `tools/` か `docs/notes/` に置いてください（**そのまま T15 の答え合わせに使えます**）。

---

## ステップ5：PR

```bash
git add tools/blender_render.py
git commit -m "feat(G2): blender_render.py で synthetic_cup を20方向レンダリング"
git push -u origin feat/blender-render
```

**PR の説明に書くこと**：使ったレンダラ・解像度・1枚あたりの時間・ステップ4の結果（3 の確認画像を貼る）・**Blender を持たない関口が「読む」ときの見どころ**（[計画書 §7 実測済み環境情報](../plan.md#s-env)：Blender 固有部分は設計と入出力の妥当性をレビューし、挙動の検証は松田が担う）。

---

## 完了判定

- [ ] `data/synthetic_cup/` に `images/` 20枚・`masks/` 20枚・`cameras.json`・`gt_mesh.ply` がある
- [ ] `cameras.json` が `validate()` を通り、`source` が `turntable_gt`
- [ ] マスクの画素値が `[0, 255]` の2種類だけ
- [ ] **真値メッシュの頂点を投影するとマスクに重なる**（ステップ4の 3）
- [ ] 関口の端末に `data/synthetic_cup/` を渡し、**関口側で 1 の確認コマンドが通った**
- [ ] 1枚あたりの時間を `docs/notes/` に記録した

---

## つまずいたら

| 症状 | 対処 |
|---|---|
| `ModuleNotFoundError: recon3d` | `sys.path.insert` の行があるか。`Path(__file__)` が `-P` で相対指定されていないか（迷ったら絶対パスで渡す） |
| `ValueError: sys.argv.index("--")` | `--` を付け忘れ（Blender の引数と自作の引数の区切り） |
| `scene.node_tree` の `AttributeError` | Blender 5.0 の仕様変更。[mask-options.md](../notes/mask-options.md) の表 #1 を参照。`compositing_node_group` を使う |
| マスクに中間値（灰色）が出る | `view_transform="Standard"`・`dither_intensity=0`・（ID Mask なら）Anti-Alias オフを確認 |
| 投影した点が全部ずれる | **符号か原点の疑い。** Blender と OpenCV は Y と Z の向きが逆・画像の縦も逆（[計画書 §4-2](../plan.md#s4-2)）。**その変換は `io/coords.py` の中だけで直す**（別の場所に足さない） |
| 20枚で時間がかかりすぎる | 解像度を下げる／サンプル数を減らす。**何秒かかったかを記録して**から決める |
| `det(R)` の検証で落ちる | 鏡映になっている。変換を二重に掛けていないか確認 |

---

## 終わったら

1. [次にやること](../next.md) の T13 の状態を `✅ 完了（日付・PR番号）` にする
2. **詰まった点・学んだことを `docs/notes/` に残す**（[T08](T08-blender-entry-note.md) と同様。ここが一番価値がある）
3. **関口に `data/synthetic_cup/` を渡し、[T15](T15-opencv-pipeline.md) が動かせる状態にする**
4. **`--views 8` で低解像度の小セットを作り、`tests/data/` に置く**のは W02 の後（G7 の第3層。数MB以内）。別 Issue にしてください
