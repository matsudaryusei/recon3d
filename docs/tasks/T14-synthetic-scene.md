# T14 — `tests/fixtures/synthetic_scene.py` を実装する（画像なしの合成シーン）

[← 次にやること一覧に戻る](../next.md)

| | |
|---|---|
| ジャンル | **G7 テスト・CI** |
| 目安時間 | 3〜4時間（実装が中心） |
| 前提 | [T01](T01-pairpro1-io.md) 完了（`io/coords.py`・`io/cameras.py`）。**Blender も画像も不要**。T11〜T13 とは独立に進められる |
| 作るもの | **`tests/fixtures/synthetic_scene.py`** と、それ自身のテスト **`tests/test_synthetic_scene.py`** |
| 出どころ | [計画書 §9-1（第1層）](../plan.md#s9-1) ／ [D-23](../decisions.md#d-23) ／ [conventions.md](../conventions.md) ／ [cameras.md](../schema/cameras.md) |

---

## 着手前に読むもの

| 初めて出てくること | 資料 |
|---|---|
| pytest の書き方・`pytest.raises`・`np.testing` | [学びの入口 G6+G7](../learning.md) の pytest 入門 |
| **ピンホールカメラで3D点を投影する式** `x ~ K [R \| t] X` | [Hartley & Zisserman](https://www.robots.ox.ac.uk/~vgg/hzbook/) の第6章／[Szeliski 本](https://szeliski.org/Book/) のカメラモデル |
| 乱数を再現可能にする（`np.random.default_rng(seed)`） | [NumPy の乱数](https://numpy.org/doc/stable/reference/random/index.html) |

---

## なぜやるのか

**Phase 2（W06〜）の主力テストは、この生成器です**（[D-23](../decisions.md#d-23)）。DLT・三角測量・バンドル調整を自作したとき、**「正解が分かっている入力」がなければ、合っているか間違っているかが分かりません。**

画像を使わないので、**Blender も OpenCV も要らず、CI（Ubuntu・Windows）で数ミリ秒で回ります。**
そして **ノイズを 0 にすれば解析的に厳密な正解**が出るので、**バグが自作のソルバなのか、生成器なのか**を切り分けられます。

> **この生成器が間違っていると、後で書くソルバのテストが全部無意味になります。** だから生成器自身に先にテストを書きます（下のステップ3）。

---

## ステップ1：ブランチと足場

```bash
git switch main && git pull origin main
uv sync
git switch -c feat/synthetic-scene
```

`tests/fixtures/` には `.gitkeep` があります。**ファイルが入ったら `.gitkeep` は消してかまいません**（[計画書 §6-2](../plan.md#s6-2)）。

---

## ステップ2：関数の形（ここだけ決まっている）

[計画書 §9-1](../plan.md#s9-1) が決めているのはこの形です。**中身と、戻り値の型の細部は自分で設計してください。**

```python
def make_scene(n_points=100, n_cameras=20, noise_px=0.0, seed=0):
    """3D点をランダム生成し、既知のカメラ行列で投影する。
    戻り値: (points_3d, cameras, observations_2d)  — すべて正解が既知
    """
```

**決めておく設計の項目**（自分たちで決める。**決めたら docstring に書く**）：

| 項目 | 考えること |
|---|---|
| 点をどこに置くか | 被写体の大きさ（[T12](T12-prepare-blend.md) で決めた単位）に合わせるか。カメラの前方（`z > 0`）に必ず入るか |
| カメラをどう並べるか | ターンテーブル風に円周上か／ランダムか。**両方あってもよい**（引数で切り替え） |
| 内部パラメータ `K` | 固定か引数か。`cameras.json` の `intrinsics` と同じ形にしておくと後で楽 |
| 戻り値の型 | `recon3d.io.cameras` の `CameraSet` を再利用するか／素の `np.ndarray` か。**G1 の関数が受け取りやすい形**を考える |
| 画像外に出た点 | 除くか、`NaN` か（観測できない点の扱い） |

**制約**（守ること）：

- **`numpy` と標準ライブラリだけで書く。** `cv2` を入れない（[D-23](../decisions.md#d-23) の狙いが崩れる）
- **`seed` が同じなら、まったく同じ結果になる**（`np.random.default_rng(seed)`）
- **座標変換を自分で書かない。** 必要なら `recon3d.io.coords` を呼ぶ（`diag(1,-1,-1)` を書くと `tests/test_conventions.py` が落ちる）

---

## ステップ3：生成器自身のテストを書く

**`tests/test_synthetic_scene.py` に、最低限この4つのテストを書きます。**（期待値の中身は自分で導いてください）

| # | テストの名前の案 | 確かめること |
|---|---|---|
| 1 | `test_zero_noise_reprojection_is_exact` | `noise_px=0` のとき、`points_3d` を `cameras` で投影し直すと `observations_2d` と**ほぼ完全に一致**（許容誤差は自分で決める） |
| 2 | `test_same_seed_same_scene` | 同じ `seed` で2回呼ぶと、3つとも完全に一致 |
| 3 | `test_all_points_in_front_of_cameras` | すべてのカメラで、点のカメラ座標の `z > 0` |
| 4 | `test_noise_has_expected_scale` | `noise_px=1.0` で、観測とのずれの標準偏差が 1 px 前後（統計的な許容幅を自分で決める） |

**加えて1つ、カメラの `R` が正しい回転行列であることを確かめる**（`RᵀR ≈ I`・`det(R) ≈ +1`。[`validate`](../../src/recon3d/io/cameras.py) と同じ検査）。

```bash
uv run pytest tests/test_synthetic_scene.py -v
uv run pytest            # 全部（既存の10件 + 新規）
```

---

## ステップ4：PR

```bash
git add tests/fixtures/synthetic_scene.py tests/test_synthetic_scene.py
git commit -m "feat(G7): 画像なしの合成シーン生成器を追加"
git push -u origin feat/synthetic-scene
```

**PR の説明に書くこと**：上の設計の項目（ステップ2の表）にどう答えたか。**Approve する人は「この生成器のどこを信じてよいか」を自分の言葉で1〜3行**書く（[計画書 §3-2](../plan.md#s3-2)）。

CI（Ubuntu・Windows）が緑になることを確認してからマージ。

---

## 完了判定

- [ ] `uv run pytest` が緑（新規テスト5件以上を含む）
- [ ] **`noise_px=0` で投影し直した誤差がほぼゼロ**（テスト1）
- [ ] 同じ `seed` で結果が完全に同じ（テスト2）
- [ ] `cv2` を import していない（`grep -n "import cv2" tests/fixtures/synthetic_scene.py` が空）
- [ ] 設計の項目の答えが docstring か PR に書いてある
- [ ] CI が Ubuntu・Windows とも緑

---

## つまずいたら

| 症状 | 対処 |
|---|---|
| `tests/fixtures` から import できない | `tests/fixtures/__init__.py` を置く（空でよい）か、`tests/conftest.py` でパスを通す。**どちらにしたかを PR に書く** |
| テスト1が 1e-6 程度で落ちる | 浮動小数点の誤差。**許容誤差の根拠**（float64 の精度・座標の大きさ）を考えて `atol` を決める |
| 点が画像の外に出る | `K` の `cx, cy`・点の範囲・カメラ距離のバランス。**投影した `u, v` の最小最大を print して確かめる** |
| テストが緑にならず、生成器かテストか分からない | **紙に1点・1カメラの手計算を書く。** 手計算と一致すれば生成器が合っている |
| `test_conventions.py` が落ちた | 座標変換のリテラルを書いた。`io/coords.py` の関数を呼ぶ形に直す |

---

## 終わったら

1. [次にやること](../next.md) の T14 の状態を `✅ 完了（日付・PR番号）` にする
2. **[T15](T15-opencv-pipeline.md) の自作版（W06〜）が、この生成器を最初の入力にします。** 使い方を `docs/notes/` に1行残すと、G1 に入る人が楽です
