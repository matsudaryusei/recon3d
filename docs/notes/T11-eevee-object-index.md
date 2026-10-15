# T11：EEVEE は Object Index パス非対応／①アルファ方式の実測 2026/10/08

[T11（マスク生成方式を決める）](../tasks/T11-decide-mask-method.md) のステップ2「EEVEE で ID Mask が動くか」を実機で確認した。
**結論：EEVEE では ID Mask 方式は成立しない。** [mask-options.md](mask-options.md) が「情報源によって『長らく非対応』『対応済み』で記述が割れている」として残していた宿題に、この環境での答えが出た。

> **これは判断材料であって決定ではない。** 採用方式の決定（D-43）は2人で行う。下の「[T11 の決定に与える影響](#t11への影響)」に分岐だけ整理してある。

## 症状

[tools/blender_id_mask_check.py](../../tools/blender_id_mask_check.py) の `scene.render.engine` を `"CYCLES"` → `"BLENDER_EEVEE"` に1行変えて実行したところ、ステップ4のソケット存在チェックで落ちた。

```
KeyError: "'Object Index' 出力ソケットが見つかりません。
利用可能な出力: ['Image', 'Alpha', 'Depth', ..., 'Object Index', 'Material Index', ...]
```

**メッセージが矛盾している。** 「見つかりません」と言いながら、同じ文の「利用可能な出力」に `Object Index` が載っている。
ここで「スクリプトのバグでは？」と疑ったが、**ガードは本物の非対応を正しく捕まえていた。**

## 切り分け（エンジンだけを変えた A/B）

同じ `.blend`・同じコード経路で、`scene.render.engine` だけを変えて比較した。

| | `use_pass_object_index` の読み戻し | `"Object Index" in rl.outputs` | ソケットの `enabled` | enabled なソケット |
|---|---|---|---|---|
| **Cycles** | `True` | `True` | **`True`** | Image, Alpha, **Object Index**, Noisy Image |
| **EEVEE** | `True` | `False` | **`False`** | Image, Alpha |

**EEVEE では Object Index パスが出ない。** 紛らわしかったのは次の2点である。

| # | 紛らわしかった点 | 実際の挙動 |
|---|---|---|
| 1 | `view_layer.use_pass_object_index = True` が EEVEE でも**エラーにならず、読み戻すと `True` になる** | 代入は黙って受け取られるだけで、パスは出力されない。**この属性は対応状況の判定に使えない** |
| 2 | 出力ソケット `Object Index` は**一覧には存在する**のに、キー照合では見つからない | ソケットは `enabled=False` で存在している。`[o.name for o in outputs]` の**反復は無効ソケットも拾う**が、`in` / `.get()` / `[...]` の**キー照合は無効ソケットに一致しない**（3つとも失敗することを確認） |

2 がそのまま、あの「あるのに無い」メッセージの正体である。
**対応状況を判定したいときに見るべきは、属性の読み戻しでもソケット名の一覧でもなく、ソケットの `enabled` である。**

## 副産物：EEVEE で使える代替パス

同じ probe で、代替案（[mask-options.md の比較表](mask-options.md#比較表) の ①③）の足場も確認できた。

- **①アルファ方式**：`Alpha` ソケットは EEVEE でも `enabled=True`。`scene.render.film_transparent = True` も問題なく通る
- **③Cryptomatte**：`view_layer.use_pass_cryptomatte_object = True` にすると `CryptoObject00`〜`CryptoObject02` が `enabled=True` になる

**つまり EEVEE 単独で進めたい場合の代替は2つとも実在する。** ①については下の「[①アルファ方式の実測](#アルファ実測)」でマスクを実際に出力して測った（③Cryptomatte はパスが出ることの確認のみで、出力の実測は未実施）。

<a id="t11への影響"></a>
## T11 の決定に与える影響

「ID Mask を採用」のままでは済まなくなった。[mask-options.md の「推す案と、その理由」](mask-options.md#推す案とその理由) が想定していたとおりの分岐に入る。

| 案 | 中身 | 効く点 | 痛い点 |
|---|---|---|---|
| **A: ID Mask ＋ マスクだけ Cycles** | 推す案を維持し、カラー画像は EEVEE・マスクは Cycles で出す | **厳密に二値**（`[0. 1.]`）＝質問2 に最強。**1回のレンダーで、遮蔽を解いた物体別マスク**が出る＝質問3 も満たす | [D-19](../decisions.md#d-19) と衝突（決定文書の整合として改訂が必要）。パイプラインが2エンジン立てになり、**[T07 で6通りに壊れた Blender 5.0 コンポジタ API](T07-blender5-cli-troubleshooting.md) を踏み続ける** |
| **B: ①アルファ方式** | `film_transparent` ＋ numpy でしきい値 | EEVEE 単独で完結し [D-19](../decisions.md#d-19) を動かさずに済む。実装2〜3行で**コンポジタを一切使わない**。しきい値は実測で**極めて鈍感**（下記） | 厳密な二値ではない（輪郭1px に中間値、全体の 0.317%）。**全オブジェクトの和集合しか出せず**、物体別が要るなら1視点あたり `1 + N` 回レンダーが必要 |
| **C: ③Cryptomatte** | EEVEE でもパスは出る | エンジンを跨いでも同じ書き方が通る | 実装が数十行。かつ輪郭がアンチエイリアスされるので**結局しきい値が必要**＝A の長所も B の手軽さも取れない |

**レンダー時間は決め手にならない**（実測は下記）。案A を「CPU Cycles だから遅い」で落とすのは誤りで、マスクだけを `samples=1` で焼けば**40枚で追加4分**に収まる。[D-19](../decisions.md#d-19) の「現実的な時間に収まらない」は大域照明つきの本番カラーレンダーと反復試行についての判断であり、マスクパスには当てはまらない。**衝突するのは決定文書の整合であって、スループットではない。**

**実測後、論点は質問2 から質問3 に移った。** 質問2（しきい値なしで二値）は、A が厳密に満たす一方、B も「中間値は輪郭1pxだけ・しきい値は鈍感」と分かったので**実害がほぼない**。残る本当の差は**質問3（物体を分離できるか）**である。

- **合成シーンに被写体が1つだけなら**（[T12](../tasks/T12-prepare-blend.md) は「シーンに被写体が1つ、原点に立っている」前提で `.blend` を整える）、B の「和集合しか出せない」は**コストゼロ**。回転台は合成データでは**モデリングしなければ写らない**ので、質問3 の「回転台＋被写体の2物体」は合成データでは回避できる
- **逆に、回転台を含めて写す／被写体を複数置く設計にするなら**、A が明確に優位（1回のレンダーで遮蔽込みの物体別マスク）

**したがって T11 の決定は、[T12](../tasks/T12-prepare-blend.md) の「合成シーンに何を置くか」と連動する。** 単体被写体で進めるなら B、シーンに回転台や複数物体を入れるなら A、という対応になる。

<a id="アルファ実測"></a>
## ①アルファ方式の実測（2026-10-08・EEVEE・1920x1080・samples=64）

`film_transparent = True` で RGBA PNG を出し、Alpha チャンネルを numpy で検証した（[T07 の学び](T07-blender5-cli-troubleshooting.md)「保存後のPNGを読んで画素値を確かめる」に従う。View Transform=Standard・ディザリング0 も ID Mask の検証と同条件に揃えた）。

### 質問2：しきい値を触らずに二値が出るか → **出ない。ただし実害は小さい**

| 指標 | 実測 |
|---|---|
| Alpha のユニーク値 | **255 種類**（0.0〜1.0 が連続） |
| 中間値（0.001 < a < 0.999）の画素 | **6,579 / 2,073,600 = 0.3173%** |

**中間値はアンチエイリアスされた輪郭1px分しかない。** そして**しきい値はほとんど効かない**：

| threshold | 0.1 | 0.3 | 0.5 | 0.7 | 0.9 |
|---|---|---|---|---|---|
| 白の割合 | 28.812% | 28.765% | 28.734% | 28.701% | 28.653% |

しきい値を 0.1 から 0.9 まで9倍動かしても、白の割合の変化は **0.159 ポイント**しかない。
**つまり「しきい値処理が必須」という弱点は、実際には『値を決める必要がほぼない処理が1行増える』程度の重さである。** ID Mask を推した最大の理由（質問2）は、実測すると A と B の差をほとんど生まない。

### 質問3：物体を分離できるか → **できない（和集合になる）**

同一条件で、オブジェクトを1つずつ `hide_render` して分解した。

| レンダー内容 | 白の割合（threshold=0.5） |
|---|---|
| 全部（`円` ＋ `円.001`） | **28.734%** |
| `円` のみ | 14.317% |
| `円.001` のみ | 20.590% |
| （単体の和） | 34.907% |

**単体の和（34.907%）が全部（28.734%）を上回るのは、2物体が重なっている（遮蔽がある）ため。**
そして**単体マスクの和集合と「全部」の画素単位の一致率は 100.0000%** だった。**アルファ出力はシーン内の全オブジェクトのシルエットの和集合そのもので、物体の区別という概念を持たない。**

物体別マスクが必要なら、他の物体を `hide_render` して焼き直すしかなく、**1視点あたり 本番1回 + 物体数N回**のレンダーになる。

> **ここが T07 の実測値との食い違いの正体でもある。** T07 の ID Mask は `円=6.380%` だが、アルファで `円` 単体を測ると **14.317%**。**ID Mask は「見えている部分」だけを返す（遮蔽が解かれている）**ので、`円` は `円.001` の陰に半分以上隠れていたことになる。**これは A の長所である**（1回のレンダーで遮蔽込みの物体別マスクが取れる）。
> なお T07 の可視分の合計 26.793% と、アルファの和集合 28.734% には約1.9ポイントの差が残る。Cycles と EEVEE のカバレッジ差と、ID Mask の `Anti-Alias` オフによる中心サンプル判定（面積を小さめに見積もる）が原因と考えられるが、**ここは詰めていない**。方式選定には影響しない。

### レンダー時間（同一マシン・1920x1080・40枚＝20方向×2データセットに外挿）

| 条件 | 1枚 | 40枚 |
|---|---|---|
| 案B EEVEE alpha（samples=64） | 2.34 秒 | **1.6 分** |
| 案B EEVEE alpha（samples=16） | 0.64 秒 | 0.4 分 |
| 案A Cycles ID Mask（samples=1） | 6.00 秒 | **4.0 分** |
| 案A Cycles ID Mask（samples=16） | 8.02 秒 | 5.3 分 |

`scene.cycles.device` は **`CPU`**（[D-19](../decisions.md#d-19) の前提どおり GPU は使えない）。
それでも**マスクパスなら CPU Cycles で 1枚6秒**で、案A の追加コストは全データセットで4分程度。**「Cycles は遅いから案A は無い」という理由づけは、実測では成立しない。**

## 検証に使ったコード

**新しいツールは追加していない。** `tools/` のスクリプトは変更せず（EEVEE への1行書き換えは試すだけで、`git restore` で戻す）、下の probe を一時ファイルとして流した。再確認したいときはこれを貼り直せば足りる。

```python
import bpy
scene = bpy.context.scene
view_layer = scene.view_layers[0]

for eng in ("CYCLES", "BLENDER_EEVEE"):
    scene.render.engine = eng                      # 代入してみるのが確実（下記「学んだこと」参照）
    view_layer.use_pass_object_index = True
    tree = bpy.data.node_groups.new(f"probe_{eng}", "CompositorNodeTree")
    scene.compositing_node_group = tree
    rl = tree.nodes.new(type="CompositorNodeRLayers")
    rl.scene = scene                               # ソケット一覧を更新させる（T07 の #3 と同じ回避策）
    rl.layer = view_layer.name
    sock = next((s for s in rl.outputs if s.name == "Object Index"), None)
    print(eng, "enabled =", sock.enabled if sock else "ソケット自体が無い")
    print("  enabled なソケット =", [s.name for s in rl.outputs if s.enabled])
```

**アルファ方式の実測**も同じく一時ファイルで流した。要点は3行だけで、**コンポジタを使わない**のが案A との最大の違いである。

```python
scene.render.engine = "BLENDER_EEVEE"
scene.render.film_transparent = True              # これがアルファ方式の本体
scene.render.image_settings.color_mode = "RGBA"   # RGB にすると Alpha ごと失われる
scene.render.use_compositing = False              # コンポジタを一切通さない
scene.view_settings.view_transform = "Standard"   # T07 の罠5
scene.render.dither_intensity = 0.0               # T07 の罠6
bpy.ops.render.render(write_still=True)

# 検証（保存後のPNGを読む）
a = np.array(img.pixels[:]).reshape(h, w, 4)[..., 3]
print("中間値の画素:", np.count_nonzero((a > 0.001) & (a < 0.999)))
mask = a >= 0.5                                   # しきい値は鈍感なので 0.5 固定で十分
```

物体分離の確認は、`o.hide_render = o.name not in visible` で1つずつ隠して焼き直し、
単体マスクの和集合と全部入りマスクを画素単位で比較した（一致率 100.0000%）。

出力は `data/synthetic_cup/output/mask_alpha.png`（`data/` は `.gitignore` 済み）。

## 学んだこと・次に活かせること

- **「対応していない機能」は、エラーではなく黙った無効化として現れることがある。** `use_pass_object_index = True` は EEVEE でも通り、読み戻しても `True` が返る。**書けたこと・読み戻せたことは、効いていることの証明にならない。** 効いたかどうかは別の観測点（ここではソケットの `enabled`）で確かめる
- **`bpy_prop_collection` のキー照合は無効な要素に一致しない。** `in` が `False` なのに `[o.name for o in ...]` には載る、という食い違いが起きる。存在チェックが矛盾した結果を返したら、まず**「無効な状態で存在している」**を疑う
- **[T07 の学び](T07-blender5-cli-troubleshooting.md)「エラーメッセージに候補一覧を出させる」は、今回**半分だけ**効いた。** 一覧は出たが、`enabled` を出していなかったため「あるのに無い」で手が止まった。**一覧を出すときは、名前だけでなく「使えるかどうか」も併記する**と、次の人が1分で分かる。**【2026-10-15 修正済み】** [blender_id_mask_check.py](../../tools/blender_id_mask_check.py) と [blender_id_mask_check_multiobj.py](../../tools/blender_id_mask_check_multiobj.py) の両方を下の形に差し替え、Cycles で従来どおり通ること・EEVEE で `存在=True / enabled=False` が出ることを実機で確認した。[T07 の学び](T07-blender5-cli-troubleshooting.md)の側もあわせて改訂してある：

  ```python
  sock = next((s for s in render_layers.outputs if s.name == "Object Index"), None)
  if sock is None or not sock.enabled:
      enabled = [s.name for s in render_layers.outputs if s.enabled]
      raise KeyError(
          f"'Object Index' が使えません（存在={sock is not None} / "
          f"enabled={getattr(sock, 'enabled', None)}）。"
          f"エンジン {scene.render.engine} はこのパスに非対応の可能性があります。"
          f"このエンジンで使える出力: {enabled}"
      )
  ```

- **「弱点」は、大きさを測るまで弱点と決まらない。** 今回 A/B の比較は、測る前と後で結論が引っくり返りかけた。**B の「しきい値処理が必須」**は実測すると 0.1〜0.9 で結果が 0.159 ポイントしか動かない＝ほぼ無害だったし、**A の「CPU Cycles は遅い」**も マスクパスなら40枚で4分＝無害だった。**代わりに、測る前は誰も挙げていなかった「アルファは物体を分離できない」が最大の争点として残った。** 比較表の定性的な○×は、採用の直前に必ず数字にする
- **レンダーエンジンの一覧を `bl_rna.properties['engine'].enum_items` で取ろうとしたのは誤りだった。** このenumは動的で、**Cycles のような登録エンジンが列挙されない**（最初の probe は `['BLENDER_EEVEE']` だけを返し、Cycles が無いビルドだと誤認しかけた）。**エンジンの有無は `scene.render.engine` に代入して例外を見るか、`addon_utils.check("cycles")` で確かめる**

## 関連ファイル

- 判断材料本体（4方式の比較表・T07 の実機確認結果）：[docs/notes/mask-options.md](mask-options.md)
- Blender 5.0 の API 変更で踏んだ罠6件：[docs/notes/T07-blender5-cli-troubleshooting.md](T07-blender5-cli-troubleshooting.md)
- **スクリプト2本の読み方・直し方（備忘録）**：[docs/notes/mask-check-scripts.md](mask-check-scripts.md)
- 検証対象のスクリプト：[tools/blender_id_mask_check.py](../../tools/blender_id_mask_check.py)
- タスク手順書：[docs/tasks/T11-decide-mask-method.md](../tasks/T11-decide-mask-method.md)
