# T15 — OpenCV の既存関数で一直線にパイプラインを通す（ライブラリ版）

[← 次にやること一覧に戻る](../next.md)

| | |
|---|---|
| ジャンル | **G1・G3** |
| 目安時間 | 6〜8時間（実装が中心。**環境・データの受け取り・確認の仕方は下にすべて書いてある**） |
| 前提 | [T13](T13-blender-render.md) 完了（`data/synthetic_cup/` を松田から受け取っている）。**Blender は不要** |
| 作るもの | **`tools/lib_pipeline.py`**（使い捨てのスクリプト）。出力は画面表示と数値のログ |
| 出どころ | [計画書 §10 W02](../plan.md#s10) ／ [D-23](../decisions.md#d-23)（ライブラリ版を先に作る理由）／ [cameras.md](../schema/cameras.md) |

---

## 着手前に読むもの

| 初めて出てくること | 資料 |
|---|---|
| **SIFT・特徴点マッチング** | [学びの入口 G3](../learning.md) の OpenCV 公式チュートリアル（特徴点検出・マッチングの節） |
| **三角測量・PnP・カメラモデル** | [学びの入口 G1](../learning.md) の Szeliski 本と Hartley & Zisserman（**該当節だけ**） |
| Open3D で点群を表示する | [Open3D の点群チュートリアル](https://www.open3d.org/docs/release/tutorial/geometry/pointcloud.html) |

**分からない言葉が出たら** → [用語集](../glossary.md)。**`再投影誤差`・`PnP`・`三角測量`・`点群`**あたりが出ます。

---

## なぜやるのか

**ここで作るのは使い捨てです。W06 以降に自作する DLT・三角測量・バンドル調整の「答え合わせの相手」になります**（[計画書 §9-1 第2層](../plan.md#s9-1)・[D-23](../decisions.md#d-23)）。

もう1つの目的は、**「パイプライン全体のどこで何が起きるか」を先に一周して体で知ること**です。
**特徴点が何点取れるか・どこで壊れやすいかは、自作を始める前に知っておくと、自作の優先順位が決まります**（W03 で実測する値の予行演習）。

> **本体は「どの関数をどの順で、何を渡してつなぐか」を自分で組むことです。** 手順書には、つなぎ方は書いていません。
> **1つだけ、最初に紙に書いてください：`solvePnP` に渡す 3D 点はどこから来るのか。**

---

## ステップ1：ブランチと依存の追加

```bash
git switch main && git pull origin main
uv sync
git switch -c feat/lib-pipeline
```

**OpenCV と Open3D を入れます。** ただし **CI（Ubuntu・Windows で `uv sync`）を重くしたくない**ので、**開発用とは別のグループに分けます**：

```bash
uv add --group pipeline opencv-python open3d
uv sync --group pipeline
```

- **`uv.lock` と `pyproject.toml` が変わります。** 差分はコミットしてよい（[T03](T03-ci-workflow.md) の CI は既定グループだけ同期するので、`cv2` を import するテストは `pytest.importorskip("cv2")` で飛ばす）
- 入れたあとの確認：

```bash
uv run --group pipeline python -c "import cv2, open3d; print(cv2.__version__, open3d.__version__)"
```

> **numpy のバージョン衝突が出たら**（`pyproject.toml` は `numpy>=2.4.6`）：エラーを消さずに残して Issue に貼る。**依存の選択は勝手に決めず、2人で決めて [決定記録](../decisions.md) に1行残す**（[T08](T08-blender-entry-note.md) の `mathutils` と同じ扱い）。

---

## ステップ2：データを受け取って中身を確認する

**`data/` は Git に入りません。** [T13](T13-blender-render.md) の出力を、**松田から対面（USB・ローカル転送）で受け取って**、自分のリポジトリの `data/synthetic_cup/` に置きます。

```bash
ls data/synthetic_cup/            # images/ masks/ cameras.json gt_mesh.ply
ls data/synthetic_cup/images | wc -l   # 20
```

**読めるかを確認**（`io/cameras.py` はここで初めて実データに使われます）：

```bash
uv run python -c "from pathlib import Path; from recon3d.io.cameras import load_cameras, validate; c = load_cameras(Path('data/synthetic_cup/cameras.json')); validate(c); print(len(c.views), c.views[0].source, c.image_size)"
```

**期待する出力：`20 turntable_gt (640, 480)`**（解像度は松田の設定による）。**ここで落ちたら T13 の出力の問題**なので、Issue に貼って松田に戻す。

---

## ステップ3：パイプラインを組む

**`tools/lib_pipeline.py` を作ります。** 次の骨組みだけ決まっています。**中の組み立ては自分で。**

```python
"""OpenCV の既存関数で 画像 → 点群 を一直線に通す（ライブラリ版）。

使い方:
    uv run --group pipeline python tools/lib_pipeline.py data/synthetic_cup
"""

from pathlib import Path
import sys
import time

import cv2
import numpy as np
import open3d as o3d

from recon3d.io.cameras import load_cameras


def main(dataset_dir: Path) -> None:
    cameras = load_cameras(dataset_dir / "cameras.json")
    t0 = time.perf_counter()

    # TODO: 1. 画像を読む
    # TODO: 2. SIFT で特徴点を検出し、隣の視点とマッチング（ratio test で外れ値を減らす）
    # TODO: 3. 姿勢の推定（solvePnP）と三角測量（triangulatePoints）をつなぐ
    #          ← 何から始めるか（最初の2視点はどうするか）は自分で決める
    # TODO: 4. 推定した R, t を真値（cameras.views[i].R, .t）と比べる
    # TODO: 5. 再投影誤差を測る
    # TODO: 6. 点群を Open3D で表示し、.ply にも保存する

    print(f"処理時間: {time.perf_counter() - t0:.1f} s")


if __name__ == "__main__":
    main(Path(sys.argv[1]))
```

**書きながら守ること**：

- **座標変換は `io/coords.py` の外に書かない**（[規約 D-11](../decisions.md#d-11)）。OpenCV の規約は本プロジェクトの規約と同じなので、変換は不要のはずです（**要らないはずのところで変換したくなったら、どこかが間違っています**）
- **`K`（内部パラメータ）は `cameras.json` の `intrinsics` から組む。** 真値を使ってよい（ここは検証用の一周）
- **推定値を `cameras.json` に書き戻すなら `source: "dlt"` にする**（真値の `turntable_gt` を上書きしない。[cameras.md](../schema/cameras.md)）

---

## ステップ4：数値を3つ出す

**W03 の実測（G8）の予行演習です。** 次の3つを **`docs/notes/` に貼ってください**（値の良し悪しは今は問わない）：

| 測るもの | 見方 |
|---|---|
| **再投影誤差（px）** | 推定した点を画像へ投影し直したときの、観測とのずれの平均 |
| **カメラ角度誤差（°）** | 推定した回転と、`cameras.json`（真値）の回転との差 |
| **点群の点数と処理時間** | 点群の点数、`処理時間: ○ s` |

**何点取れたか・どの視点で壊れたかも1行ずつ書く**（特に**無地の面で点が空いていないか**：[計画書 §2](../plan.md#s2) の想定が実物で確かめられます）。

---

## ステップ5：PR

```bash
git add tools/lib_pipeline.py pyproject.toml uv.lock docs/notes/
git commit -m "feat(G1,G3): OpenCV版の一直線パイプラインを追加"
git push -u origin feat/lib-pipeline
```

**PR の説明に書くこと**：`solvePnP` の 3D 点をどこから得たか・使った関数の順・ステップ4の3つの数値・**うまくいかなかった点**。Approve する人は「このPRが何をしているか」を自分の言葉で1〜3行書く。

---

## 完了判定

- [ ] **`uv run --group pipeline python tools/lib_pipeline.py data/synthetic_cup` が最後まで動く**
- [ ] **Open3D のウィンドウに点群が出る**（形がカップらしい。**点群と真値メッシュ `gt_mesh.ply` を同時に表示して重なりを見る**とよい）
- [ ] ステップ4の**3つの数値**が `docs/notes/` にある
- [ ] `uv run pytest`（既定グループ）が **既存どおり緑**（`opencv`・`open3d` が無くても落ちない）
- [ ] `solvePnP` の 3D 点の出どころを、**自分の言葉で説明できる**

---

## つまずいたら

| 症状 | 対処 |
|---|---|
| Open3D のウィンドウが出ない（SSH・リモート環境） | 表示は諦めて `.ply` に保存し、手元で開く。**ウィンドウが要るのは確認だけ** |
| `ImportError: libGL` など（Ubuntu） | Open3D の依存ライブラリ。エラー文の名前で `apt` 検索。解決した手順を `docs/notes/` に残す |
| 特徴点がほとんど取れない | **マスク領域だけに絞っていないか、画像が暗すぎないか。** 合成画像は無地の面が多く、**取れないのが想定どおりのことがあります**。取れた点数を記録して、それ自体を成果にする |
| 三角測量の点が原点から遠く離れる | **スケールが不定**です（2視点だけからは大きさが決まらない）。Hartley & Zisserman の該当節へ。真値のカメラ間距離で合わせる手が使えるが、**どう合わせるかは自分で決める** |
| 姿勢が鏡映になる | `det(R)` を確認。座標変換を余計に掛けていないか。**規約は本プロジェクトと OpenCV で同じ**なので、変換は要らないはず |
| `numpy` の衝突 | ステップ1の注意。Issue に貼って2人で決める |
| 再投影誤差が大きい | 外れ値マッチが混ざっている可能性。ratio test の閾値・RANSAC の有無を変えて**数値の変化を記録**する |

---

## 終わったら

1. [次にやること](../next.md) の T15 の状態を `✅ 完了（日付・PR番号）` にする
2. **詰まった点・学んだことを `docs/notes/` に残す**
3. **W03 へ**：この結果に**実写1セット（[計画書 §10](../plan.md#s10) W03）**を通して比べます。手順書は W03 に入る前に足します
