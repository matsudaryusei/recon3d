# T12 — 元モデルを `.blend` にして、長さの単位を決める

[← 次にやること一覧に戻る](../next.md)

| | |
|---|---|
| ジャンル | **G2 3DCG・データ生成** |
| 目安時間 | 1.5時間 |
| 前提 | **Blender 5.0.1（松田の端末）**。[T09](T09-find-3d-model.md) 完了（主データ＝Ceramic Pot）。[T11](T11-decide-mask-method.md) は並行してよい |
| 作るもの | **`data/synthetic_cup/cup.blend`**（コミットしない）／ **長さの単位を決めて [conventions.md](../conventions.md) に1行**／採用結果の追記 |
| 出どころ | [model-candidates.md](../notes/model-candidates.md) ／ [計画書 §2](../plan.md#s2) ／ [§4-1](../plan.md#s4-1) |

---

## なぜやるのか

**[T13 の `blender_render.py`](T13-blender-render.md) は「シーンに被写体が1つ、原点に立っている」ことを前提に書きます。** ダウンロードしたモデルはそのまま使えません。大きさも位置もバラバラだからです。

**もう1つ、まだ誰も決めていないことがあります：長さの単位です。** `cameras.json` の `t` や `gt_mesh.ply` の座標が **m なのか mm なのか**、[cameras.md](../schema/cameras.md) にも [conventions.md](../conventions.md) にも書いてありません。
**後から食い違うと、再投影誤差もHausdorff距離（mm で目標を立てる）も静かにずれます。** 最初の1回で決めて、規約に書きます。

> 座標の**向き**は決まっています（+Z が上・原点は回転台の中心・[計画書 §4-1](../plan.md#s4-1)）。**ここで整えるのはモデルをその規約に合わせる作業です。**

---

## ステップ1：モデルを取る

1. <https://polyhaven.com/a/ceramic_pot> を開く
2. **Download** で形式 **`.blend`**、解像度は **1K** を選ぶ（テクスチャは軽くてよい。20枚のレンダリング時間が変わる）
3. 展開して、リポジトリの **`data/synthetic_cup/`** に置く（`data/` は `.gitignore` 済み。**コミットされません**）

```bash
mkdir -p data/synthetic_cup
# 展開したファイルをここへ移す
```

---

## ステップ2：単位を決める

**推す案は「メートル」です**（Blender の既定単位。[計画書 §5-1](../plan.md#s5-1) の `t: [0, 0, 0.5]` の例もメートルの大きさ）。
**Hausdorff 距離を mm で述べるときは、出力時に ×1000 すれば足ります。**

**2人で1分話して決める。** 決まったら [conventions.md](../conventions.md) に次の1行を足す（`io/` の規約なので**両者がレビュー**する）：

```markdown
| 長さの単位 | **メートル**（`t`・`gt_mesh.ply` の座標。Hausdorff 距離を mm で述べるときは表示時に ×1000） |
```

---

## ステップ3：モデルを規約に合わせる（Blender GUI）

**1. 被写体を1つにする**：床・背景・ライトなどの余計なオブジェクトを消す（ライトは T13 で置き直す）

**2. スケールを実寸にする**：`N` キーの **Item** タブで **Dimensions** を見る。**マグカップなら高さ 0.1 m 前後**が目安。ずれていたら `S` で拡縮し、**`Ctrl+A` → `Scale`** で確定する（**確定しないと `scale` が 1 でないまま残り、`gt_mesh.ply` の座標が狂います**）

**3. 底面を Z=0、中心を XY の原点に置く**：`Object → Set Origin → Origin to Geometry` のあと、`Location` を `X=0, Y=0`、**底面が Z=0 に触れるよう `Z` を調整**（Dimensions の Z の半分）。**`Ctrl+A` → `Location`** で確定

**4. Pass Index を1にする**：Properties → Object → **Relations → Pass Index = 1**（[T11](T11-decide-mask-method.md) で ID Mask 以外に決まったら飛ばす）

**5. 閉じたメッシュか確認**：Edit モード → `Select → Select All by Trait → Non Manifold`。**0件ならOK**（[model-candidates.md](../notes/model-candidates.md) で確認済みだが、加工後にもう一度）

**6. 保存**：`File → Save As` → `data/synthetic_cup/cup.blend`

---

## ステップ4：CLI で中身を読む（確認）

**GUI で直したものを、`-b` でも同じに読めるかを確かめます。** 次の内容を **`tools/inspect_blend.py`**（新規・使い捨てでよいがコミットしてよい）に貼る：

```python
"""シーンのオブジェクトと寸法・位置を出力する。T12 の完了判定用。

使い方:
    blender -b data/synthetic_cup/cup.blend -P tools/inspect_blend.py
"""

import bpy

for o in bpy.data.objects:
    print(o.name, o.type,
          "loc=", tuple(round(v, 4) for v in o.location),
          "scale=", tuple(round(v, 4) for v in o.scale),
          "dim=", tuple(round(v, 4) for v in o.dimensions),
          "pass_index=", o.pass_index)
```

```powershell
& "C:\Program Files\Blender Foundation\Blender 5.0\blender.exe" -b data\synthetic_cup\cup.blend -P tools\inspect_blend.py
```

**期待する出力：被写体が1つ。`scale=(1.0, 1.0, 1.0)`、`loc` の X・Y が 0、`dim` の Z がおよそ 0.1、`pass_index=1`。**

---

## ステップ5：記録して PR

1. [model-candidates.md](../notes/model-candidates.md) の末尾に「**採用結果**」を足す：採用したモデル・ダウンロードした形式と解像度・Dimensions・**単位（m）**・加工した点（例：蓋は一体のまま）
2. PR：

```bash
git switch main && git pull origin main
git switch -c docs/prepare-blend
git add docs/conventions.md docs/notes/model-candidates.md tools/inspect_blend.py
git commit -m "docs(G2): 元モデルの準備結果と長さの単位を記録"
git push -u origin docs/prepare-blend
```

---

## 完了判定

- [ ] `data/synthetic_cup/cup.blend` があり、`inspect_blend.py` の出力が上の期待どおり
- [ ] **単位が [conventions.md](../conventions.md) に書いてあり、2人とも同意した**
- [ ] `git status` に `data/` が出ない（コミットされない）
- [ ] 関口側で `cup.blend` が要る場合の**受け渡し方法を決めた**（対面で USB／ローカル転送でよい。**CC0 でも 20枚＋テクスチャは大きいので、リポジトリには入れない**）

---

## つまずいたら

| 症状 | 対処 |
|---|---|
| `Ctrl+A` の Apply が灰色 | オブジェクトモード（Object Mode）か確認。複数選択していないか確認 |
| Dimensions が 2m など巨大 | 単位設定（Scene → Units）が違う場合がある。**Scene の Unit Scale が 1.0 か**確認 |
| Non Manifold が出る | `Mesh → Clean Up → Fill Holes`。それでも残る場合は Ceramic Pot の別解像度を試す |
| `-b` で開くと GUI で見た形と違う | 保存し忘れ。`Ctrl+S` して再実行 |

---

## 終わったら

1. [次にやること](../next.md) の T12 の状態を `✅ 完了` にする
2. **続けて [T13 `blender_render.py`](T13-blender-render.md)。**
