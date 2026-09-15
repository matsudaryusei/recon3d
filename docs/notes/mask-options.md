# マスク生成方式の候補（決定用の判断材料）

**目的**: Blender の合成データから、被写体だけを白・背景を黒にした二値マスクを得る方式を決める。
**決めるとき**: **W02 中**に2人で（→ docs/decisions.md#d-35）。**W03 以降の G3 がここで止まる**
**この文書の位置づけ**: 決定ではなく判断材料。決めた結果は別に1本残す。

## 前提（この環境で動くことが条件）

- Blender 5.0.1 / 内蔵 Python 3.11.13 / numpy 1.26.4（`pip install` はしない。`bpy` と `numpy` のみに依存させる → 計画書 §7-4）
- `blender --background --python <script>` で **CLI から自動実行できること**（20枚を手作業で書き出すのは論外）
- 出力は **PNG。0 と 255 の二値**（グレーの中間値が残ると彫刻が濁る）

## 比較表

| | 1 アルファ | 2 Holdout | 3 Cryptomatte | 4 ID Mask |
|---|---|---|---|---|
| 仕組み（1〜2行） | レンダリング時に背景を透過（`film_transparent`）にして、出力PNGのRGBAのうちAlphaだけを取り出し、しきい値で0/255に二値化する https://docs.blender.org/manual/ja/5.0/render/freestyle/view_layer/line_style/alpha.html | 対象外のオブジェクトのマテリアル/オブジェクト設定を「Holdout」にすると、そのオブジェクトの領域だけAlpha=0として「穴」扱いになり、残った被写体だけが不透明で描画される https://docs.blender.org/manual/ja/5.0/render/shader_nodes/shader/holdout.html | オブジェクトごとにハッシュ化されたIDを持つ専用パス（Cryptomatteパス）をレンダー時に出力し、コンポジタのCryptomatteノードで目的のオブジェクトIDだけを指定して抽出する https://docs.blender.org/manual/ja/5.0/compositing/types/mask/cryptomatte.html | 各オブジェクトに`pass_index`という番号を割り振ってレンダリングし、コンポジタのID Maskノードで「この番号と一致する画素だけ残す」処理をする https://docs.blender.org/manual/ja/5.0/compositing/types/mask/id_mask.html |
| **スクリプトから自動化できるか** | | | | |
| **出力が二値になるか**（中間値が出ないか） | | | | |
| 半透明・毛・髪への強さ | | | | |
| **実装量**（行数の肌感／設定箇所の数） | | | | |
| レンダリングエンジン依存（EEVEE / Cycles） | | | | |
| 落とし穴・既知の罠 | | | | |
| 参考にした URL | | | | |

## 推す案と、その理由

（1〜3段落。「なぜこれが本プロジェクトに合うか」を書く）

## 決めるときの質問（この3つに答えられれば決まる）

1. 20枚を CLI で自動生成できるか
2. しきい値を触らずに 0/255 の二値が出るか
3. 被写体が増えたとき（回転台＋被写体の2物体）に破綻しないか

## 松田側で確認してほしいこと（Blender がある端末）

- [ ] 推した方式で 1 枚だけ出力してみる
- [ ] 出力を開いて、**中間値の画素が無いか**を確認する（例：ヒストグラムが 0 と 255 の2本だけか）
- [ ] 確認した結果を、この文書の下に追記する