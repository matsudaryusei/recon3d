# T01 — ペアプロ#1：座標系と `cameras.json` を決めて実装する

[← 次にやること一覧に戻る](../next.md)

| | |
|---|---|
| ジャンル | **G6 基盤・I/O**（[計画書 §3-3](../plan.md#s3-3)） |
| 目安時間 | **2時間・2人そろってやる**（[計画書 §13⑤](../plan.md#s13)） |
| 前提 | `git pull` 済み・`uv sync` 済み・`uv run pytest` が `1 passed` になること |
| 作るもの | `docs/conventions.md` / `docs/schema/cameras.md` / `src/recon3d/io/coords.py` / `src/recon3d/io/cameras.py` / `tests/test_conventions.py` |
| 仕様の出どころ | [計画書 §4（座標系）](../plan.md#s4)・[§5（`cameras.json`）](../plan.md#s5) ／ [D-10](../decisions.md#d-10)・[D-11](../decisions.md#d-11)・[D-12](../decisions.md#d-12)・[D-17](../decisions.md#d-17) |

---

## 着手前に読むもの

> ⏰ **この手順書は、当日ではなく前もって各自1回読んでおいてください。**
> 通読に**25〜30分**かかります。2時間の枠の中で読むと、実際に手を動かす時間が2割減ります。

**このタスクは、[計画書 §7-7](../plan.md#s7-7) で「未経験」に挙がっている項目を4つ同時に使います。**
**知らないまま2時間の枠に入ると、2時間が全部そこで溶けます。** 先に目を通しておいてください（合計3〜4時間）。

| 初めて出てくること | どこで使うか | 資料 |
|---|---|---|
| **`dataclass`** | `cameras.py` のデータ構造 | [学びの入口 G6](../learning.md) |
| **`pytest`**（`assert`・`pytest.raises`・`tmp_path`） | ステップ4 のテスト3本 | [学びの入口 G6](../learning.md) |
| **NumPy**（`@` と `*` の違い・`shape`） | `coords.py` の行列計算 | [学びの入口 G6](../learning.md) |
| **型ヒント** | シグネチャの読み書き | [学びの入口 共通](../learning.md) |

**分からない言葉が出たら** → [用語集](../glossary.md)（`editable install`・`smoke test`・`再投影誤差` など）。

## なぜ最優先なのか

**ここが決まらないと、他のジャンルが1行も書けません。**

- G1（数理コア）は「カメラ行列がどっち向きか」が決まらないと式が書けない
- G2（Blender）は「どの形式で書き出すか」が決まらないと出力できない
- G5（ボクセル）は画像座標の上下が決まらないと投影できない

**しかも座標系のミスは、動くけれど答えが鏡像になる**という形で出るので、後から気づきにくい。だから**最初に決めて、破れない構造にします**（[D-11](../decisions.md#d-11)）。

---

## 進め方（2時間の割り振り）

| 時間 | やること | 成果物 |
|---|---|---|
| 0:00–0:20 | ステップ1：規約を読み合わせる | （口頭） |
| 0:20–0:40 | ステップ2：`docs/conventions.md` を書く | 文書 |
| 0:40–1:00 | ステップ3：`docs/schema/cameras.md` を書く | 文書 |
| 1:00–1:20 | ステップ4：`tests/` を先に書く | テスト |
| 1:20–1:50 | ステップ5：`io/coords.py`・`io/cameras.py` を実装する | コード |
| 1:50–2:00 | ステップ6：PR を出す | PR |

> **テストを先に書きます。** 「何ができたら正しいか」を先に固めてから実装すると、2人で分担しても答え合わせができます。

---

## ステップ0：ブランチを切る

```bash
git switch main
git pull origin main
uv sync
git switch -c feat/io-coords-and-cameras
```

**numpy を入れます。** まだ入っていないので、**ここで1回だけ**：

```bash
uv add numpy
uv run python -c "import numpy; print(numpy.__version__)"   # 数字が出れば OK
```

> ⚠️ **ステップ4（テストを書く）で numpy を使うので、必ず先に入れてください。**
> `pyproject.toml` と `uv.lock` が変わります。**両方コミットしてください。** 他の端末は `git pull` 後に `uv sync` が要ります。

---

## ステップ1：規約を声に出して読み合わせる（20分）

[計画書 §4-1 の表](../plan.md#s4-1)を2人で開いて、**1行ずつ声に出して確認します。** ここで「あ、逆だと思ってた」を潰すのが目的です。

確認する4点：

1. **世界座標**：右手系・**+Z が上**（ターンテーブルの回転軸）・原点は回転台の中心
2. **カメラ座標**：OpenCV規約。**+X 右・+Y 下・+Z が光軸の前方**（Blender と Y・Z の符号が逆）
3. **画像座標**：OpenCV規約。**原点は左上ピクセルの中心・+u 右・+v 下**
4. **外部パラメータの向き**：**world → camera**。つまり `X_cam = R @ X_world + t`

**世界座標の「+Z 上」だけ Blender に合わせてある**理由も確認してください（世界座標の変換が不要になる。→ [D-10](../decisions.md#d-10)）。

---

## ステップ2：`docs/conventions.md` を書く（20分）

**計画書 §4 を丸写しするのではなく、「これを見れば実装できる」1枚にします。**

```bash
touch docs/conventions.md
```

**必ず入れる項目（この5つが揃っていれば合格）**

| # | 項目 | 中身 |
|---|---|---|
| 1 | 4つの規約の表 | [計画書 §4-1](../plan.md#s4-1) の表をそのまま |
| 2 | **図または文章での向きの説明** | 「カメラから見て +X が右、+Y が**下**、被写体は +Z 方向にある」 |
| 3 | Blender ↔ OpenCV の変換式 | `C = np.diag([1.0, -1.0, -1.0])` / `R_cv = C @ R_blender` / `t_cv = C @ t_blender` / `v_cv = H - 1 - v_blender` |
| 4 | **禁止事項** | **「座標変換を書いてよいのは `src/recon3d/io/coords.py` の中だけ。他のファイルに `diag(1,-1,-1)` や `H - 1 - v` が現れたら規約違反」** |
| 5 | 違反の検出方法 | `tests/test_conventions.py` が機械的に検出すること（ステップ4） |

> **4 が本体です。** 規約は「守ろうね」では守られないので、**書ける場所を1ファイルに閉じ込めます**（[D-11](../decisions.md#d-11)）。

---

## ステップ3：`docs/schema/cameras.md` を書く（20分）

```bash
touch docs/schema/cameras.md
```

**必ず入れる項目**

| # | 項目 | 中身 |
|---|---|---|
| 1 | JSON の実例まるごと1つ | [計画書 §5-1](../plan.md#s5-1) の JSON をそのまま貼る |
| 2 | フィールドの表 | 名前 / 型 / 必須か / 意味。[§5-2](../plan.md#s5-2) を土台にする |
| 3 | **`source` の3つの値の意味** | `"turntable_gt"`（Blender の真値）/ `"dlt"`（自作 DLT の推定値）/ `"bundle_adjusted"`（バンドル調整後）。**撤退ライン L2 への切り替えがこの1フィールドで済む**（[§12](../plan.md#s12)・[D-12](../decisions.md#d-12)） |
| 4 | 検証項目の表 | [§5-3](../plan.md#s5-3) の4つ（`schema_version` / `convention` 一致 / `RᵀR ≈ I` / **`det(R) ≈ +1`**） |
| 5 | 追加依存を入れない方針 | **pydantic は使わず `dataclass` + 手書き検証**（[D-17](../decisions.md#d-17)） |

**決めておくこと（ここで決めないと実装が止まります）**

- 相対パス（`"images/img_000.png"`）は**何を基準にするか** → **`cameras.json` 自身の置き場所からの相対**にするのが素直です。決めたら文書に1行書く
- `reprojection_error_px` が `null` のときの扱い → **「まだ測っていない」の意味**と書く

---

## ステップ4：テストを先に書く（20分）

```bash
touch tests/test_conventions.py
```

**この3本を書きます。** テストが「何が正しいか」の定義になるので、**実装より先に書いてください。**

### テスト1：座標変換が `io/coords.py` の外に漏れていないこと

`src/` 全体を走査して、`io/coords.py` **以外**に変換のリテラルが現れたら失敗させます。検出するパターンの例：

- `diag(1, -1, -1)` / `diag([1.0, -1.0, -1.0])`（空白の有無を許す）
- `H - 1 - v` のような画像縦方向の反転
- `[[1,0,0],[0,-1,0],[0,0,-1]]` の直書き

**やり方**：`src/` 配下の `*.py` を全部開き、`io/coords.py` はスキップ、残りの本文に正規表現をかけて、当たったら `pytest.fail(f"{path}: 座標変換は io/coords.py に書くこと")`。

> ⚠️ **`Path("src")` と書かないでください。** これは**コマンドを打った場所からの相対パス**なので、リポジトリ直下以外から `pytest` を起動すると、
> **エラーも出さずに0件走査して必ず pass します。** 規約違反を永久に見逃す、一番たちの悪い壊れ方です。
> **テストファイルの位置を基準にしてください**（`Path(__file__).resolve().parents[1] / "src"` のような形）。
> **あわせて「走査したファイルが0件なら fail させる」1行を必ず入れてください。** これが空振りへの唯一の歯止めです。

> **いま `src/` にはまだ実装がほとんど無いので、このテストは最初から通ります。** それでよいです。**後から誰かが規約を破った瞬間に落ちる**のが目的です。

### テスト2：Blender → OpenCV の変換が仕様どおりであること

**変換式は [計画書 §4-2](../plan.md#s4-2) に決めてあります。テストに書く「期待値」は、先に紙で出してください。**

> **ここは手順書に答えを書きません。** 期待値を自分で出す作業が、そのまま**規約を体に入れる作業**だからです。
> **2人で別々に紙に書いて、突き合わせてから**テストに落とすと、片方の勘違いがその場で出ます。

出す期待値は3つです:

| # | 入力 | 出すもの |
|---|---|---|
| 1 | `R_blender = I`（単位行列）、`t_blender = [0, 0, 5]` | `R_cv` と `t_cv` は何になるか（**手計算で1行で出ます**） |
| 2 | 1 で出した `R_cv` | `R_cv.T @ R_cv` と `det(R_cv)` は何になるべきか |
| 3 | `H = 1080` のとき `v_blender = 0` と `v_blender = H - 1` | それぞれ `v_cv` は何になるか（**端が端に写るか**を見る） |

**2 は「回転行列であること」の確認です。** ここが崩れていたら変換式の書き方が間違っています。

> 💡 **2人の答えが割れたら、それは規約の理解が割れているということです。** [計画書 §4-1](../plan.md#s4-1) に戻ってください。**このズレを本番の実装中に見つけるより、いま見つけるほうが圧倒的に安いです。**

### テスト3：壊れた `cameras.json` を読んだら例外が出ること

**正常系1本と、異常系を [計画書 §5-3 の検証4項目](../plan.md#s5-3) ぶん**書きます。
異常系は「**1か所だけ壊した** JSON」を作り、`load_cameras()` が例外を投げることを `pytest.raises` で確認します。

**§5-3 の4項目は、それぞれ「どう壊せば引っかかるか」を考えて JSON を作ってください。**

| §5-3 の検証項目 | 壊し方は自分で決める |
|---|---|
| `schema_version` が既知か | |
| `convention` が想定と一致するか | |
| `RᵀR ≈ I`（回転行列が壊れていないか） | |
| **`det(R) ≈ +1`**（鏡映になっていないか） | ← **座標変換の符号ミスを捕まえる本命。ここは必ず書く** |

> **「どう壊すか」を考えることが、そのまま「何を守っているか」の理解になります。** だからここは空けてあります。
> 思いつかない項目があったら、[計画書 §5-3](../plan.md#s5-3) の右列「検出できる事故」を読んでください。

テスト用の JSON は `tests/fixtures/` に置くか、テスト内で `tmp_path` に書き出してください。

---

## ステップ5：実装する（30分）

> ⚠️ **実装本体はこの手順書には載せていません。** 「生成AIを使わずに書きたい」という方針（[D-33](../decisions.md#d-33)）を尊重するためです。
> **下に置くのは「関数の形（シグネチャ）と、その関数が何をするか」だけ**です。中身は2人で書いてください。**ステップ4のテストが通れば正解です。**
>
> **さらに、下の `dataclass` の分け方は一案にすぎません。** [計画書 §5-1](../plan.md#s5-1) の JSON と往復できるなら、**まとめても分けても構いません。**
> 「どこで区切ると読みやすいか」は設計そのものなので、**そこは決め直してよい**ところです（変えたら [decisions.md](../decisions.md) に1行）。

### `src/recon3d/io/coords.py`

```python
"""座標変換。プロジェクト内で座標変換を書いてよいのはこのファイルだけ（docs/conventions.md）。"""

import numpy as np

# Blender ↔ OpenCV のカメラ座標変換行列（+Y と +Z の符号を反転する）
C = np.diag([1.0, -1.0, -1.0])


def blender_to_opencv_rt(R_blender: np.ndarray, t_blender: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Blender 規約の (R, t) を OpenCV 規約に変換する。

    引数:
        R_blender: (3, 3) 回転行列
        t_blender: (3,)  並進ベクトル
    戻り値:
        (R_cv, t_cv)
    """


def blender_v_to_opencv_v(v_blender: np.ndarray | float, height: int) -> np.ndarray | float:
    """画像の縦座標を Blender/OpenGL（左下原点）から OpenCV（左上原点）に変換する。"""


def world_to_camera(R: np.ndarray, t: np.ndarray, x_world: np.ndarray) -> np.ndarray:
    """世界座標の点をカメラ座標へ移す。X_cam = R @ X_world + t

    1点なら (3,) を、まとめて渡すなら (N, 3) を受けられるようにする。

    ⚠️ (N, 3) をそのまま `R @ x_world` に渡してはいけない。形が合わない。
       しかも N == 3 のときだけ例外が出ず、黙って違う答えを返す。
       まとめて扱う書き方は自分で確かめること（テストは N != 3 の点でも通ること）。
    """
```

### `src/recon3d/io/cameras.py`

```python
"""cameras.json の読み書きと検証（docs/schema/cameras.md）。

追加依存は入れない。dataclass と json だけで書く（D-17）。
"""

from dataclasses import dataclass
from pathlib import Path

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
    # distortion は dict のままでよい（当面ゼロ固定のため）


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
    """読み込んで validate() を必ず通す。不正なら例外を投げる。"""


def save_cameras(cameras: CameraSet, path: Path) -> None:
    """書き出す前に validate() を通す。壊れたファイルを世に出さない。"""


def validate(cameras: CameraSet) -> None:
    """4項目を検査し、違反があれば ValueError を投げる。

    1. schema_version が SCHEMA_VERSION と一致するか
    2. convention が docs/conventions.md の値と一致するか
    3. すべての R について R.T @ R ≈ I
    4. すべての R について det(R) ≈ +1   ← 符号ミス（鏡映）の検出
    """
```

---

## ステップ6：完了判定（10分）

**下が全部通ったら終わりです。**

```bash
uv run pytest -v
```

- [ ] `tests/test_import.py` に加えて、**`tests/test_conventions.py` の3本以上が pass**
- [ ] `uv run python -c "from recon3d.io import coords, cameras; print('ok')"` が `ok` を返す
- [ ] `docs/conventions.md` に**「座標変換は `io/coords.py` にだけ書く」**が明記されている
- [ ] `docs/schema/cameras.md` に**JSON の実例まるごと1つ**と**検証4項目**が載っている
- [ ] `git status` に**消し忘れの一時ファイルが無い**

PR を出す：

```bash
git add -A
git commit -m "feat(io): 座標系規約と cameras.json の読み書き・検証を追加（ペアプロ#1）"
git push -u origin feat/io-coords-and-cameras
```

GitHub で PR を作成。説明文には**「何を」「なぜ」を1〜3段落**（[計画書 §8-2](../plan.md#s8-2)）。`io/` は共有境界なので**必ず2人でレビュー**します（[計画書 §6-1](../plan.md#s6-1)）。

---

## テストが落ちたときの読み方

**落ちるのが普通です。** pytest の出力は最初とっつきにくいので、**どこを見ればいいか**だけ先に書いておきます。

例として、画像の縦反転で `- 1` を書き忘れた実装を通すと、こう出ます:

```
=================================== FAILURES ===================================
_______________________________ test_bottom_edge _______________________________

    def test_bottom_edge():
>       assert blender_v_to_opencv_v(0, 1080) == 1079
E       assert 1080 == 1079
E        +  where 1080 = blender_v_to_opencv_v(0, 1080)

test_demo.py:5: AssertionError
=========================== short test summary info ============================
FAILED test_demo.py::test_bottom_edge - assert 1080 == 1079
============================== 1 failed in 0.01s ===============================
```

**見る順番は下から上です。**

| 見る場所 | 読み方 |
|---|---|
| 一番下 `1 failed` | **いくつ落ちたか。** `1 passed, 1 failed` のように混在します |
| `FAILED ... :: 関数名` | **どのテストが落ちたか。** `::` の右が関数名 |
| `test_demo.py:5` | **落ちた行。** ここをエディタで開く |
| `E assert 1080 == 1079` | **`E` の行が失敗の中身。** 左が実際の値、右が期待した値 |
| `+ where 1080 = ...(0, 1080)` | **どの呼び出しがその値を返したか。** pytest が自動で展開してくれます |
| `>` が付いた行 | 落ちた文そのもの |

**この例なら**：期待は 1079、実際は 1080。**1 だけ多い**ので、`height - v` を `height - 1 - v` にすればよい、と読めます。

**よく使うオプション**

```bash
uv run pytest -v                          # どのテストが通ったかを一覧で出す
uv run pytest tests/test_conventions.py   # このファイルだけ動かす
uv run pytest -k identity                 # 名前に identity を含むテストだけ動かす
uv run pytest -x                          # 最初の1件が落ちたらそこで止める
```

> ⚠️ **`E   ModuleNotFoundError: No module named 'numpy'` が出たら**、`uv add numpy` がまだです（ステップ0）。
> **`No module named 'recon3d'` なら** `uv sync` を1回（下の表）。

## つまずいたら

| 症状 | 対処 |
|---|---|
| `ModuleNotFoundError: No module named 'recon3d'` | `uv sync` を1回。それでも直らなければ `uv sync --reinstall-package recon3d`（[計画書 §6-3](../plan.md#s6-3)） |
| 同じ症状が数分後に再発する | **リポジトリが iCloud / OneDrive の同期フォルダの下にある**可能性。[計画書 §7-8](../plan.md#s7-8) を読んで移動してください |
| **`det(R) = -1` になる** | **`C` の符号の付け方が違います。** `C` で**符号を反転させる軸が奇数本**だと `det = -1`（鏡映）になります。規約の `diag(1, -1, -1)` は2本なので `+1`。`diag(1, 1, -1)` や `diag(-1, -1, -1)` にしていないか見てください |
| **`det` は合っているが、値が規約と合わない** | **掛ける順序の可能性。** `C @ R` と `R @ C` は**別の行列**ですが、**`det` はどちらも同じ**なので `det` では気づけません。規約は `C @ R` です（[計画書 §4-2](../plan.md#s4-2)） |
| 変換後の `t` の符号で悩む | `t` はベクトルなので `C @ t`。`R` と同じ `C` を左から掛けるだけです |

---

## 終わったら

1. **詰まった点・学んだことを `docs/notes/` に1本残す**
2. [次にやること](../next.md) の T01 の状態を `✅ 完了（日付・PR番号）` に書き換える
3. **決めたこと（相対パスの基準など）を PR コメントに残す。** 口頭で済ませると GitHub に何も残りません（[計画書 §8-3](../plan.md#s8-3)）
