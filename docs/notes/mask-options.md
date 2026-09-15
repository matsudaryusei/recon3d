# マスク生成方式の候補（決定用の判断材料）

**目的**: Blender の合成データから、被写体だけを白・背景を黒にした二値マスクを得る方式を決める。
**決めるとき**: **W02 中**に2人で（→ docs/decisions.md#d-35）。**W03 以降の G3 がここで止まる**
**この文書の位置づけ**: 決定ではなく判断材料。決めた結果は別に1本残す。

## 前提（この環境で動くことが条件）

- Blender 5.0.1 / 内蔵 Python 3.11.13 / numpy 1.26.4（`pip install` はしない。`bpy` と `numpy` のみに依存させる → 計画書 §7-4）
- `blender --background --python <script>` で **CLI から自動実行できること**（20枚を手作業で書き出すのは論外）
- 出力は **PNG。0 と 255 の二値**（グレーの中間値が残ると彫刻が濁る）

> **【実機確認済み・全方式共通の罠】** Blender 5.0 はデフォルトで **色管理（View Transform: AgX）** と **ディザリング** が有効になっている。これらは写真的な最終レンダリング向けの機能で、**マスクのような「データ」を保存する用途では値を歪める**（0/1のはずの画素が0.8や0.996のような中間値になる）。どの方式を選んでも、レンダリング前に以下の設定が必要：
> ```python
> scene.view_settings.view_transform = "Standard"  # または "Raw"
> scene.render.dither_intensity = 0.0
> ```

## 比較表

| | 1 アルファ | 2 Holdout | 3 Cryptomatte | 4 ID Mask |
|---|---|---|---|---|
| 仕組み（1〜2行） | レンダリング時に背景を透過（`film_transparent`）にして、出力PNGのRGBAのうちAlphaだけを取り出し、しきい値で0/255に二値化する https://docs.blender.org/manual/ja/5.0/render/freestyle/view_layer/line_style/alpha.html | 対象外のオブジェクトのマテリアル/オブジェクト設定を「Holdout」にすると、そのオブジェクトの領域だけAlpha=0として「穴」扱いになり、残った被写体だけが不透明で描画される https://docs.blender.org/manual/ja/5.0/render/shader_nodes/shader/holdout.html | オブジェクトごとにハッシュ化されたIDを持つ専用パス（Cryptomatteパス）をレンダー時に出力し、コンポジタのCryptomatteノードで目的のオブジェクトIDだけを指定して抽出する https://docs.blender.org/manual/ja/5.0/compositing/types/mask/cryptomatte.html | 各オブジェクトに`pass_index`という番号を割り振ってレンダリングし、コンポジタのID Maskノードで「この番号と一致する画素だけ残す」処理をする https://docs.blender.org/manual/ja/5.0/compositing/types/mask/id_mask.html |
| **スクリプトから自動化できるか** | できる。`scene.render.film_transparent = True` を設定し、出力を PNG / RGBA にするだけ。数行で完結 | できる。対象オブジェクトに `object.is_holdout = True`（Cycles）を設定＋`film_transparent = True`。オブジェクト数だけループすればよい | できるが手数が多い。`view_layer.use_pass_cryptomatte_object = True` でパスを有効化した上で、コンポジタのノードツリー（Cryptomatteノード追加・`matte_id`設定・File Output接続）をスクリプトで組む必要がある | **【実機確認済み・できる】** `tools/blender_id_mask_check.py` で実際にCLIから成功。ただしBlender 5.0のAPI変更に合わせた書き方が必要（下の「落とし穴」参照） |
| **出力が二値になるか**（中間値が出ないか） | **ならない。** アンチエイリアス（サンプリング）で輪郭に中間値が出るため、保存後にしきい値で二値化する後処理が必須 | **ならない。** 仕組みはアルファと同じ（alpha=0の穴）なので輪郭に同様の中間値が出る。後処理が必要 | **ならない。** マニュアル（Legacy版）に「マットはアンチエイリアス処理され、モーションブラーや透過度などの効果が考慮される」と明記されている。出力は「白黒（grayscale）アルファマスク」と書かれているが、これは**「2色（0/255）」の意味ではなく「モノクロ＝グレースケール」の意味**（非レガシー版ページでは同じ出力を明示的に "A grayscale mask" と説明）。輪郭はアンチエイリアスされる＝中間値を持つので、後処理が必要 | **【実機確認済み・なる】** Anti-Alias入力をオフにし、**かつ**View Transform/ディザリングを切ると、`ユニークな画素値: [0. 1.] ／ 種類数: 2` を確認（下の「実機確認結果」参照）。4方式で唯一、しきい値処理なしで二値が出せた |
| 半透明・毛・髪への強さ | 強い。レンダリングの実カバレッジをそのまま Alpha に反映するので毛先の半透明も自然に出る（二値化すると失われる） | アルファと同等（Holdout も alpha=0/1 として同じ仕組みで出る） | 強い。カバレッジベースでマットを生成し、毛・被写界深度・モーションブラーも考慮される（Cycles の「Accurate」モードで精度が高い。EEVEE はモーションブラー非対応という既知の制限あり） | 弱い。1ピクセル1インデックスの生値で部分カバレッジの概念が無く、毛先はジャギー（ギザギザ）になりやすい |
| **実装量**（行数の肌感／設定箇所の数） | 最小。2〜3行（`film_transparent` ＋出力フォーマット設定）＋保存後の numpy しきい値処理 | 小。対象オブジェクトごとに `is_holdout = True` を設定するループ＋数行 | 大きい。パス有効化＋コンポジタのノードツリー構築（ノード追加・接続・`matte_id`設定・File Output）を丸ごとスクリプト化する必要があり、数十行規模になりやすい | 中。`pass_index` 設定＋パス有効化＋ ID Mask ノードと File Output ノードの追加・接続 |
| レンダリングエンジン依存（EEVEE / Cycles） | 依存なし。EEVEE / Cycles / Workbench すべてで動作 | Cycles で確立された機能。EEVEE でも使えるが、過去に「Holdout と Transparent の併用が EEVEE で正しく動作しない」不具合報告あり（[T77069](https://developer.blender.org/T77069)、後に修正）。Blender 5.0 での挙動は要実機確認 | 元は Cycles 専用だったが、EEVEE Next（4.x 以降・5.0 含む）でも Cryptomatte パス出力に対応済み。ただし EEVEE はモーションブラーがマットに反映されないなど、Cycles との機能差が残る | **【実機確認済み】Cyclesでは動作を確認**（`tools/blender_id_mask_check.py`・`_multiobj.py` とも `scene.render.engine = "CYCLES"` で成功）。**EEVEEは未検証のまま。** 情報源によって「長らく非対応」「対応済み」の記述が割れているため、EEVEEでの採用は別途確認が必要 |
| 落とし穴・既知の罠 | 出力フォーマットを「RGB」のままにすると Alpha ごと失われ背景が黒く焼き付く。必ず「RGBA」を指定する | 過去に EEVEE で Transparent 併用時の不具合報告あり。オブジェクトが増減するたびに `is_holdout` の設定漏れが起きやすい（オブジェクトごとにループし直す必要がある） | EEVEE はモーションブラーがマットに反映されない（既知の制限）。「Accurate」モードは CPU 専用で GPU レンダリング時は使えない。**【実機確認済み】③④はコンポジタのノードツリーをスクリプトで組むが、Blender 5.0でこのAPIが破壊的変更されている**（後述） | 同じ `pass_index` を複数オブジェクトに割り当てると区別できなくなる（Cryptomatte はハッシュ方式だが、こちらは整数値なので手動管理が必要）。マニュアル上は「Cryptomatte に置き換えられつつある機能」という位置づけ。**【実機確認済み】Blender 5.0でコンポジターのPython APIが変更されており**、`scene.node_tree`（4.5以前の書き方）が`AttributeError`になる。正しくは `scene.compositing_node_group` に独立したノードツリー（`bpy.data.node_groups.new(name, "CompositorNodeTree")`）を割り当てる必要があり、`Composite`ノードも廃止されて`Group Output`ノードに置き換わっている。ネットの解説記事は旧APIのままのものが多く**そのままでは動かないので要注意**（[Compositor Migration](https://developer.blender.org/docs/release_notes/5.0/migration/compositor_migration/)） |
| 参考にした URL | [Film - Blender Manual](https://docs.blender.org/manual/en/5.0/render/cycles/render_settings/film.html) ／ [背景を透明にしてレンダリングする - dskjal](https://dskjal.com/blender/background-transparent.html) | [Holdout - Blender Manual](https://docs.blender.org/manual/ja/5.0/render/shader_nodes/shader/holdout.html) ／ [T77069（EEVEE Holdout+Transparent 不具合）](https://developer.blender.org/T77069) | [Cryptomatte Node - Blender Manual](https://docs.blender.org/manual/ja/5.0/compositing/types/mask/cryptomatte.html) ／ [Cryptomatte (Legacy) Node - Blender Manual](https://docs.blender.org/manual/ja/5.0/compositing/types/mask/cryptomatte_legacy.html)（「マットはアンチエイリアス処理される」の記載元） ／ [CompositorNodeCryptomatteV2 API](https://docs.blender.org/api/current/bpy.types.CompositorNodeCryptomatteV2.html) ／ [T93095（EEVEE motion blur in cryptomatte）](https://developer.blender.org/T93095) | [ID Mask Node - Blender Manual](https://docs.blender.org/manual/ja/5.0/compositing/types/mask/id_mask.html) ／ [Object API（pass_index）](https://docs.blender.org/api/current/bpy.types.Object.html) ／ [EEVEE Object Index pass 議論](https://devtalk.blender.org/t/eevee-index-pass-or-cryptomatte/6401) |

## 推す案と、その理由

**④ ID Mask（Object Index）を推す。** 「決めるときの質問」の2番目・3番目に最も素直に答えられる方式だからである。ID Maskは4方式の中で唯一、後処理のしきい値調整なしに0/255の二値がほぼそのまま出る（Anti-Aliasingチェックをオフにするだけ）。さらに、被写体と回転台のように複数オブジェクトが写り込む場合でも、オブジェクトごとに異なる`pass_index`を振るだけで「被写体だけ255・それ以外は0」を明確に分離でき、しきい値の匙加減に頼らずに済む。これは「回転台＋被写体の2物体で破綻しないか」という質問に対して、他の3方式（すべて輪郭のアンチエイリアスにしきい値で対処する必要がある）より構造的に強い。

一方で懸念点は2つある。1つは毛や半透明表現に弱いことだが、今回の被写体はBlenderの合成データ（硬い形状が主）であり、髪・毛のような繊細な半透明表現を優先する要件は無いと考えられるため許容範囲と判断した。もう1つはEEVEEでの対応状況が情報源によって割れている点で、これは**松田側での実機確認が必須**（下のチェックリスト参照）。もしEEVEEで動かない場合でも、このプロジェクトはCLIでの再現可能なバッチレンダリングが前提（計画書§7-4）であり、品質重視のオフラインレンダリングにはCyclesを使うのが自然なので、致命的な制約にはならないと考える。

次点は①アルファチャンネルである。実装が最小で全エンジンに依存しないという圧倒的な単純さがあり、ID Maskの実機確認でエンジン非対応が判明した場合の代替として温存する価値がある。ただし二値化のためのしきい値処理が別途必要になる分、「質問2」への答えがID Maskより弱い。

## 決めるときの質問（この3つに答えられれば決まる）

1. 20枚を CLI で自動生成できるか
2. しきい値を触らずに 0/255 の二値が出るか
3. 被写体が増えたとき（回転台＋被写体の2物体）に破綻しないか

## 松田側で確認してほしいこと（Blender がある端末）

- [x] 推した方式で 1 枚だけ出力してみる
- [x] 出力を開いて、**中間値の画素が無いか**を確認する（例：ヒストグラムが 0 と 255 の2本だけか）
- [x] 確認した結果を、この文書の下に追記する

## 実機確認結果（2026-09-16、松田・Blender 5.0.1）

**① GUIで手動確認 → 成功。** `data/synthetic_cup/cup.blend` の被写体（`円.001`）に `Pass Index = 1` を設定し、コンポジタで ID Mask ノード（Anti-Aliasing オフ）を手動で組んでレンダリング。出力（`data/synthetic_cup/output/mask_manual.png`）は二値化されており、同じ形状のオブジェクトでも Pass Index で描き分けられることを確認した。

**② CLIで自動確認 → 成功（`tools/blender_id_mask_check.py`）。** ただし手動でGUIをなぞっただけでは動かず、以下の想定外の壁が連続して見つかった。**いずれもBlender 5.0特有の変更・挙動であり、ネット上の解説記事の多くは古いバージョン（4.5以前）の書き方のままなので要注意。**

| # | 症状 | 原因 | 対処 |
|---|---|---|---|
| 1 | `AttributeError: 'Scene' object has no attribute 'node_tree'` | Blender 5.0 でコンポジットノードツリーが独立したデータブロックに変更された（[Compositor Migration](https://developer.blender.org/docs/release_notes/5.0/migration/compositor_migration/)） | `bpy.data.node_groups.new(name, "CompositorNodeTree")` を作成し `scene.compositing_node_group` に割り当てる。`Composite`ノードは廃止され `Group Output`ノードに置き換わっている |
| 2 | `AttributeError: 'CompositorNodeIDMask' object has no attribute 'index'` | Blender 5.0 で「多くのノードのオプションが入力ソケット化された」（公式リリースノート） | `id_mask.index = ...` ではなく `id_mask.inputs["Index"].default_value = ...`。同様に `use_antialiasing` も `id_mask.inputs["Anti-Alias"].default_value` |
| 3 | `KeyError: 'IndexOB' not found` | Render Layers ノードの出力ソケットは、スクリプトでパスを有効化しても即座には更新されない既知の問題（[Blender公式バグ #48760](https://developer.blender.org/T48760)） | ノード作成後に `render_layers.scene = scene` を再代入すると更新される |
| 4 | ソケット名の不一致 | Blender 5.0 でパス名が人間可読な表記に統一された | `IndexOB` ではなく `Object Index` という名前になっている |
| 5 | 二値のはずが `[0. 0.004 0.804 0.808 0.812]` のような中間値に | デフォルトの**View Transform（AgX）**がトーンマッピングし、0/1の値を歪めて保存していた | `scene.view_settings.view_transform = "Standard"` を明示的に設定 |
| 6 | 上記対処後も `[0. 0.004 0.996 1.]` と微小なズレが残る | デフォルトで**ディザリング**（8bit変換時のバンディング防止ノイズ）が有効 | `scene.render.dither_intensity = 0.0` |

**最終結果**：上記すべてに対処した [tools/blender_id_mask_check.py](../../tools/blender_id_mask_check.py) を `blender --background <blend> --python <script>` で実行し、`ユニークな画素値: [0. 1.] ／ 種類数: 2` を確認。**CLIからの完全自動・完全二値のマスク生成に成功。**

**③ 2物体での分離確認 → 成功（`tools/blender_id_mask_check_multiobj.py`）。** シーン内に既にある `円`・`円.001` の2オブジェクトにそれぞれ異なる Pass Index（1・2）を割り当て、CLIから1回の実行で2枚のマスクを自動生成して検証した。

```
[円] index=1 -> //output/mask_円.png
  ユニークな画素値: [0. 1.] ／ 種類数: 2 ／ 白の割合: 6.380%
[円.001] index=2 -> //output/mask_円_001.png
  ユニークな画素値: [0. 1.] ／ 種類数: 2 ／ 白の割合: 20.413%

円 と 円.001 のマスクの重なり画素数: 0（0であれば正しく分離できている）
結果: 2つのマスクは異なっています（オブジェクトごとに正しく描き分けられました）。
```

両方のマスクとも二値（0/1のみ）で、かつ**重なり画素数0**（お互いのオブジェクトを誤って拾っていない）、白の割合も別々（6.4% と 20.4%）で実際に異なる形状を描き分けられていることを確認した。（※今回のシーンは「回転台＋被写体」ではなく「カップを構成する2オブジェクト」だが、複数オブジェクトが同一シーンにある状況での分離能力という点では同じ検証になっている）

**この結果を踏まえた「決めるときの質問」への回答**：

1. 20枚をCLIで自動生成できるか → **できる**（確認済み）
2. しきい値を触らずに0/255の二値が出るか → **出る**（ただしView Transform・ディザリングのオフが必須。これは他方式でも共通して必要になるはずの設定）
3. 被写体が増えたとき（回転台＋被写体の2物体）に破綻しないか → **破綻しない**（確認済み。2物体それぞれを重なりなく正しく分離してマスク化できた）

**→ 3つの質問すべてに「できる／出る／破綻しない」と答えられたため、④ ID Mask（Object Index）で決定してよいと判断する。**