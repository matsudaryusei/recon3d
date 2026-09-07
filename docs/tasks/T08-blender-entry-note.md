# T08 — Blender スクリプトの入口メモを1本書く

[← 次にやること一覧に戻る](../next.md)

| | |
|---|---|
| ジャンル | **G2 3DCG**（[計画書 §7-7](../plan.md#s7-7) の入口整備 3） |
| 目安時間 | 1.5時間 |
| 前提 | **Blender 5.0.1 が入っている端末**（現状 松田の端末のみ） |
| 作るもの | **`docs/notes/blender-entry.md`** と、動作確認用の **`tools/hello_bpy.py`** |
| 出どころ | [計画書 §7-7](../plan.md#s7-7) ／ [§7-4](../plan.md#s7-4) ／ [§3-7](../plan.md#s3-7) |

---

## 着手前に読むもの

| 初めて出てくること | 資料 |
|---|---|
| **`bpy` の考え方**（オブジェクトの取り方・設定の仕方） | [学びの入口 G2](../learning.md) の Blender API クイックスタート |
| **Scripting タブ** | [学びの入口 G2](../learning.md) の Blender マニュアル |

**分からない言葉が出たら** → [用語集](../glossary.md)。

## なぜやるのか

**W02 から Blender で合成データを作ります**（[計画書 §10 Phase 0](../plan.md#s10)）。そこで必要なのは、GUI の操作ではなく **「スクリプトで自動的に20枚レンダリングする」** ことです。

いま止まっているのはこの2点：

1. **Scripting タブを使ったことがない**
2. **`blender --background`（CLI レンダリング）を使ったことがない**

**この2つが通れば、あとは中身を書くだけになります。** 詰まるのは毎回「入口」なので、**入口だけ先に1本メモにして、次に見るときと、他の人が見るときに再現できるようにします。**

> **重要な制約**：[計画書 §7-4](../plan.md#s7-4) は **「`tools/blender_*.py` は `bpy` と `numpy` のみに依存させる」**と決めています。
> **これは「他に何も入っていない」という意味ではありません。** Blender には `mathutils`・`bmesh`・`bpy_extras`・`gpu` などが同梱されています。
> **『同梱されているものを使ってよいか』は決まっていません。** 使いたくなったら、勝手に決めずに [Notice.md](../../Notice.md) に出して2人で決め、[決定記録](../decisions.md) に1行残してください（**`mathutils` はカメラ行列を扱うときに真っ先に欲しくなるので、実際に起きます**）。
> **確実に駄目なのは、`uv` 側で入れたもの**（`scipy` など）と **`pip install` が要るもの**です。**メモにもこれを書いてください。**

---

## ステップ1：ブランチとファイル

```bash
git switch main && git pull origin main
git switch -c docs/blender-entry
mkdir -p docs/notes
```

---

## ステップ2：動作確認用のスクリプトを作る

`tools/hello_bpy.py` を作って、**下をそのまま貼ります。**

```python
"""Blender の内蔵 Python が動くことだけを確認するスクリプト。

使い方:
    blender --background --python tools/hello_bpy.py
"""

import sys

import bpy
import numpy as np

print("=" * 50)
print("Blender version :", bpy.app.version_string)
print("Python version  :", sys.version)
print("numpy version   :", np.__version__)
print("シーン内のオブジェクト:", [o.name for o in bpy.data.objects])
print("=" * 50)
```

**このスクリプトの役割**：計画書が前提にしている「Blender 5.0.1 / Python 3.11.13 / numpy 1.26.4」が本当にその通りかを、**1コマンドで再確認できるようにする**ことです。

---

## ステップ3：3つのやり方を実際に試す

**メモに書く前に、自分で1回ずつ通してください。** 通らなかった箇所こそがメモに書く価値のある部分です。

### やり方A：Python Console で1行打つ

1. Blender を開く
2. 上部のワークスペースタブから **`Scripting`** を選ぶ
3. 左下の **Python Console** に打つ：

```python
import bpy
bpy.app.version_string
```

**バージョン文字列が返れば成功。**

### やり方B：Text Editor から実行する

1. `Scripting` タブの中央が **Text Editor**
2. **`New`** を押す → 上のコードを貼る
3. **`Run Script` ▶** を押す
4. **出力は画面には出ません。** ターミナルから Blender を起動しているか、`Window → Toggle System Console`（Windows）で見ます

> **「Run Script を押したのに何も起きない」は、ほぼ全員が1回やります。** print の出力先が別なだけです。**この落とし穴をメモに書いてください。**

### やり方C：CLI（これが本命）

**ターミナルから**：

```bash
# macOS
/Applications/Blender.app/Contents/MacOS/Blender --background --python tools/hello_bpy.py

# Windows (PowerShell)
& "C:\Program Files\Blender Foundation\Blender 5.0\blender.exe" --background --python tools\hello_bpy.py

# Ubuntu
blender --background --python tools/hello_bpy.py
```

**`--background`（略して `-b`）は「GUI を開かずに実行する」。** これができると、**20枚のレンダリングを1コマンドで回せます。**

> **毎回フルパスを打つのは面倒なので、エイリアスを作っておくと楽です**（メモに書く）:
> ```bash
> # ~/.zshrc に足す（macOS）
> alias blender="/Applications/Blender.app/Contents/MacOS/Blender"
> ```

---

## ステップ4：メモを書く

`docs/notes/blender-entry.md` に、**下の骨組みで書きます。**

```markdown
# Blender スクリプトの入口

**対象**: Blender 5.0.1 / 内蔵 Python 3.11.13 / numpy 1.26.4
**前提**: `pip install` はしない。`tools/blender_*.py` は `bpy` と `numpy` のみに依存させる（計画書 §7-4）。同梱の `mathutils` 等を使ってよいかは未決定

## 0. まず動くことを確かめる

（`tools/hello_bpy.py` を CLI で実行するコマンドを、自分の環境のフルパスで書く）

期待する出力:
（実際に出た出力を貼る）

## 1. Scripting タブの使い方

- タブの場所
- Python Console と Text Editor の違い
- **`Run Script` の出力がどこに出るか** ← 詰まりやすい

## 2. CLI から実行する

- `--background` の意味
- `--python <file>` の意味
- 自分の環境での blender 実行ファイルのパス
- エイリアスの張り方

## 3. よく使う bpy の入口（分かった範囲でよい）

| やりたいこと | 書き方 |
|---|---|
| シーンのオブジェクト一覧 | `bpy.data.objects` |
| カメラを取る | `bpy.data.objects["Camera"]` |
| 出力先を決める | `bpy.context.scene.render.filepath = "..."` |
| レンダリングする | `bpy.ops.render.render(write_still=True)` |
| 背景を透明にする | `bpy.context.scene.render.film_transparent = True` |

（実際に試して動いたものだけ残す。動かなかったものは「動かなかった」と書く）

## 4. 詰まった点

（ここが一番価値がある。素直に書く）
```

> **4 が本体です。** 「詰まった点」を書き残すのは [Notice.md 8/17 の関口の依頼](../../Notice.md)そのものです。**冗長でかまいません。**

---

## 完了判定

- [ ] **`blender --background --python tools/hello_bpy.py` が実際に動き、バージョンが3つとも表示された**
- [ ] 表示された値が **Blender 5.0.1 / Python 3.11.13 / numpy 1.26.4** と一致する（違ったら [Notice.md](../../Notice.md) に書く。**計画の前提が崩れます**）
- [ ] `docs/notes/blender-entry.md` の 0〜4 が埋まっている
- [ ] **「Run Script の出力がどこに出るか」が書いてある**
- [ ] **自分の環境の blender 実行ファイルのフルパスが書いてある**（次に見たとき探さずに済む）

PR：

```bash
git add tools/hello_bpy.py docs/notes/blender-entry.md
git commit -m "docs(G2): Blender スクリプトの入口メモと動作確認スクリプトを追加"
git push -u origin docs/blender-entry
```

---

## つまずいたら

| 症状 | 対処 |
|---|---|
| `blender: command not found` | フルパスで打つ。パスは Blender の `About` か、アプリの場所から確認 |
| `ModuleNotFoundError: No module named 'numpy'` | **前提が崩れています。** 8/16 に numpy 1.26.4 を確認しているので、環境が変わった可能性。[Notice.md](../../Notice.md) に書いて相談 |
| Windows で print が見えない | `Window → Toggle System Console` |
| `--python` に相対パスを渡して見つからない | **リポジトリのルートで実行しているか確認。** 迷ったら絶対パスで渡す |

---

## 終わったら

1. **詰まった点・学んだことを `docs/notes/` に1本残す**
2. [次にやること](../next.md) の T08 の状態を `✅ 完了` に書き換える
3. **続けて [T09 3Dモデル探し](T09-find-3d-model.md) をやると、W02 の合成データ作りにそのまま入れます**
