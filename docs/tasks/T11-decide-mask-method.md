# T11 — マスク生成方式を決める

[← 次にやること一覧に戻る](../next.md)

| | |
|---|---|
| ジャンル | **G2・G3**（全員で決める） |
| 目安時間 | 30分（松田の EEVEE 確認 15分 ＋ 対面で決める 15分） |
| 前提 | [T07](T07-mask-options.md) 完了（`docs/notes/mask-options.md` がある）。**Blender が入っている端末（松田）** |
| 作るもの | **決定記録 D-43（1件）**。計画書 §16 の該当行の削除 |
| 出どころ | [D-35](../decisions.md#d-35)（「W02 中に2人で決める」）／ [D-20](../decisions.md#d-20) ／ [mask-options.md](../notes/mask-options.md) ／ [計画書 §7-6](../plan.md#s7-6) |

---

## なぜやるのか

**[T13（`blender_render.py`）](T13-blender-render.md) が最初に書く行は、マスクの出し方です。** ここが決まっていないと G2 が着手できません。
[D-35](../decisions.md#d-35) の期日は **W02 中**で、**これを越えると W03 以降の G3 が止まります。**

**判断材料は [T07](T07-mask-options.md) で揃っています。** 残っているのは次の2つだけです。

1. **EEVEE で ID Mask が動くか**（mask-options.md は「Cyclesでは確認済み・**EEVEE は未検証**」。合成データの既定レンダラは EEVEE です → [D-19](../decisions.md#d-19)）
2. **2人で「これにする」と言うこと**

> **決めること自体が作業です。** 「推す案があるからそれでいい」ではなく、[mask-options.md](../notes/mask-options.md) の**3つの質問**に自分の言葉で答えてから決めてください。

---

## ステップ1：読む（関口・松田とも／10分）

[mask-options.md](../notes/mask-options.md) の次の3か所だけ。

- 「**推す案と、その理由**」
- 「**決めるときの質問**」（3つ）
- 「**実機確認結果**」の落とし穴の表（Blender 5.0 で `scene.node_tree` が使えない等）

---

## ステップ2：EEVEE で ID Mask を試す（松田・Blender 端末）

**既存の検証スクリプトのレンダラを1行変えるだけです。** 新しくスクリプトは書きません。

```bash
git switch main && git pull origin main
git switch -c docs/decide-mask
```

1. `tools/blender_id_mask_check.py` の `scene.render.engine = "CYCLES"` を **`"BLENDER_EEVEE"`** に書き換える（**コミットしない。試すだけ**）
2. 実行（リポジトリのルートで。パスは [blender-entry.md](../notes/blender-entry.md) の自分の環境の書き方で）

```powershell
& "C:\Program Files\Blender Foundation\Blender 5.0\blender.exe" --background data\synthetic_cup\cup.blend --python tools\blender_id_mask_check.py
```

3. 出力の最後にある **`ユニークな画素値`** を見る。**`[0. 1.]`（2種類）なら EEVEE でも二値**
4. 試し終わったら `git restore tools/blender_id_mask_check.py` で元に戻す

**結果を1行メモしておく**（次のステップで使う）：`EEVEE: 二値 OK / 中間値あり（値: ...）/ 動かない（エラー: ...）`

---

## ステップ3：3つの質問に答えて決める（2人・対面）

[mask-options.md](../notes/mask-options.md) の質問に、**それぞれ自分の言葉で1行ずつ**答えます。

| 質問 | 答え |
|---|---|
| 1. 20枚を CLI で自動生成できるか | |
| 2. しきい値を触らずに 0/255 の二値が出るか | |
| 3. 被写体が増えたとき（回転台＋被写体）に破綻しないか | |

**決める分岐は次のとおり**（結論は2人で出してください）：

| EEVEE の結果 | 選択肢 |
|---|---|
| 二値 OK | ID Mask を EEVEE で使う案 |
| 中間値あり・動かない | ①マスクだけ Cycles で出す ②アルファ方式（次点）に切り替える ③全部 Cycles にする（速度は要実測） |

---

## ステップ4：記録する

**決めた内容は3か所に残します**（[D-28](../decisions.md#d-28)）。

**(a) [決定記録](../decisions.md) に D-43 を追記**（D-42 の下。書式は D-35 と同じ）

```markdown
<a id="d-43"></a>
## D-43. マスク生成方式は ○○ に決定する

**決定**: （方式・使うレンダラ・View Transform=Standard・ディザ=0 を書く）
**日付**: 2026-xx-xx ／ **計画書**: §7-6・§16 ／ **根拠**: [D-35](#d-35)・mask-options.md

### 根拠
（3つの質問への答えと、EEVEE の確認結果）
```

**(b) [計画書 §16](../plan.md#s16) の「マスク画像の生成方法」の行を削除**（冒頭の決着済みメモにも1行足す）

**(c) [決定記録の「計画を変えた記録」](../decisions.md#changes) に1行足す**

```bash
git add docs/decisions.md docs/plan.md
git commit -m "docs(G2): マスク生成方式を決定 (D-43)"
git push -u origin docs/decide-mask
```

**PR を出して、もう1人が Approve**（要約を1〜3行書く。[計画書 §3-2](../plan.md#s3-2)）。

---

## 完了判定

- [ ] EEVEE での ID Mask の結果を、**画素値の種類数**で確認した
- [ ] 3つの質問に、それぞれ自分の言葉で答えた
- [ ] **D-43 が `main` に入っている**（採用しなかった方式の理由も1行ある）
- [ ] 計画書 §16 の該当行が消えている

---

## つまずいたら

| 症状 | 対処 |
|---|---|
| `TypeError: ... enum "BLENDER_EEVEE" not found` | **エラー文に有効な値の一覧が出ます。** その中の EEVEE を選ぶ（Blender のバージョンで名前が変わっています）。何が有効だったかを D-43 に書く |
| `data\synthetic_cup\cup.blend` が無い | [T12](T12-prepare-blend.md) の前に試す場合は、mask-options.md の実機確認で使った `.blend` のパスに読み替える |
| EEVEE で出力が真っ黒 | 対象に `pass_index` が入っているか、レンダー対象のカメラがあるか。`blender_id_mask_check.py` のログを見る |
| 2人の意見が割れた | **どちらも許容範囲なら、実装量が小さいほうを選ぶ。** 理由を D-43 に残せば後から変えられる |

---

## 終わったら

1. [次にやること](../next.md) の T11 の状態を `✅ 完了` にする
2. **続けて [T12 元モデルの `.blend` 準備](T12-prepare-blend.md)。**
