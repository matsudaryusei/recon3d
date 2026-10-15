# ID Mask 検証スクリプト2本の備忘録（読み方・直し方）2026/10/15

`tools/` にある ID Mask 検証スクリプト2本について、**「どの行が何のためにあるか」「触ると何が静かに壊れるか」**をまとめる。
[T07](T07-blender5-cli-troubleshooting.md) は「詰まった順番」の記録、[T11 の EEVEE ノート](T11-eevee-object-index.md) は「EEVEE で何が起きたか」の記録で、**どちらもスクリプト全体の地図にはなっていない**。次に [T13 `blender_render.py`](../tasks/T13-blender-render.md) を書くとき、この2本から持っていく行が多いので、先に1枚にしておく。

> **このスクリプトは検証用であって、本番のレンダラではない。** [T13](../tasks/T13-blender-render.md) は20方向レンダリングの本番実装で、別ファイルになる。ただし**色管理・ディザリング・PNG 読み戻し検証の3つは、そのまま T13 に持っていく必要がある**（理由は下記）。

## 2本の役割

| ファイル | 答えようとしている問い | 出力 |
|---|---|---|
| `tools/blender_id_mask_check.py` | [mask-options.md の質問2](mask-options.md)：**しきい値を触らずに 0/255 の二値が出るか** | `//output/mask_cli.png` 1枚＋ユニークな画素値 |
| `tools/blender_id_mask_check_multiobj.py` | 同じく**質問3：被写体が増えたときに破綻しないか** | `//output/mask_<名前>.png` をオブジェクトの数だけ＋重なり画素数 |

**中身の8割は同じ**で、違うのは「1回焼くか、`pass_index` を切り替えて複数回焼くか」だけである。

| | 単体版 | 複数版 |
|---|---|---|
| 対象の指定 | `TARGET_OBJECT_NAME` / `TARGET_INDEX`（定数2つ） | `OBJECT_INDEXES`（名前 → index の辞書） |
| 構成の組み立て | `main()` に全部 | `setup_scene()` に分離（**ノードツリーは1回だけ組んで使い回す**） |
| 焼く回数 | 1回 | オブジェクトの数だけ（`render_mask_for()`） |
| 判定 | ユニークな画素値の種類数 | 種類数の `assert` ＋**2枚の重なり画素数**と同一性チェック |

## 共通の骨格（7ステップ）

番号はスクリプト中のコメントと対応している。**「消すと静かに壊れる」列が、このメモの本題**である。

| # | やっていること | 消すとどうなるか |
|---|---|---|
| 0 | 対象オブジェクトの存在チェック | `.blend` を差し替えたとき、意味不明な箇所で落ちる |
| 1 | `scene.render.engine = "CYCLES"` | **EEVEE では ID Mask が成立しない**（[T11 ノート](T11-eevee-object-index.md)）。ここは今のところ Cycles 固定 |
| 1.5 | `view_transform = "Standard"` / `dither_intensity = 0.0` | **静かに壊れる。** 0/1 のはずの画素が `[0. 0.004 0.804 ...]` になる。計算は正しいのに**保存側で歪む**（T07 の罠5・6） |
| 2 | `obj.pass_index = N` | ID Mask が何も拾わず真っ黒 |
| 3 | `view_layer.use_pass_object_index = True` | 同上。**ただし EEVEE ではこれを書いても効かない**（後述） |
| 4 | コンポジタのノードツリー構築 | 本体 |
| 5 | `file_format = "PNG"` / `color_mode = "RGBA"` | RGB にすると Alpha ごと失われる |
| 6 | `bpy.ops.render.render(write_still=True)` | 本体 |
| 7 | **保存した PNG を読み戻して画素値を検証** | **検証スクリプトの意味が無くなる。** 1.5 の歪みはここでしか気づけない |

### ステップ4（ノードツリー）だけ補足

Blender 5.0 でコンポジタの API が変わっているため、**ネットの解説記事はほぼそのままでは動かない**（[Compositor Migration](https://developer.blender.org/docs/release_notes/5.0/migration/compositor_migration/)）。この4行が 5.0 の作法である。

```python
tree = bpy.data.node_groups.new("MaskCheck", "CompositorNodeTree")  # scene.node_tree は廃止
scene.compositing_node_group = tree                                  # 独立データブロックを scene に挿す
scene.render.use_compositing = True
tree.interface.new_socket(name="Image", in_out="OUTPUT", socket_type="NodeSocketColor")
```

出口も `Composite` ノードではなく `NodeGroupOutput` で、上の `new_socket` で作った "Image" に繋ぐ。

そして**この1行を消してはいけない**：

```python
render_layers.scene = scene   # 自分自身への再代入
```

ステップ3でパスを有効化しても、Render Layers ノードの**出力ソケット一覧は即座に更新されない**（[T48760](https://developer.blender.org/T48760)）。自分自身を再代入すると更新される、という回避策である。**無いと次のソケット探索が必ず失敗する。**

### ソケットの存在チェック（2026-10-15 修正）

```python
sock = next((s for s in render_layers.outputs if s.name == "Object Index"), None)
if sock is None or not sock.enabled:
    enabled = [s.name for s in render_layers.outputs if s.enabled]
    raise KeyError(...)
```

**`"Object Index" in render_layers.outputs` と書いてはいけない。** 理由は2つある。

1. **無効なソケットは `enabled=False` のまま「存在」する。** 非対応のエンジンでも消えてなくならない
2. **`bpy_prop_collection` のキー照合（`in` / `.get()` / `[...]`）は、無効なソケットに一致しない。** 一方で `for s in outputs` の**反復は無効なソケットも拾う**

この2つが組み合わさると、**「`in` が False なのに、一覧には載っている」**という矛盾したエラーメッセージが出る。実際に EEVEE で手が止まった（[T11 ノート](T11-eevee-object-index.md)）。
**見るべきは名前の一覧ではなく `sock.enabled`。** エラー文にも `enabled` な出力だけを並べ、エンジン名を添える。

## 動かし方

```powershell
& "C:\Program Files\Blender Foundation\Blender 5.0\blender.exe" --background data\synthetic_cup\cup.blend --python tools\blender_id_mask_check.py
```

```powershell
& "C:\Program Files\Blender Foundation\Blender 5.0\blender.exe" --background data\synthetic_cup\cup.blend --python tools\blender_id_mask_check_multiobj.py
```

**期待する出力**（Cycles・`data/synthetic_cup/cup.blend`・2026-10-15 時点）：

| スクリプト | 出力 |
|---|---|
| 単体版 | `ユニークな画素値: [0. 1.] ／ 種類数: 2` |
| 複数版 | 両方とも種類数 2、`重なり画素数: 0`、`2つのマスクは異なっています` |

**種類数が 2 より多ければ、まずステップ1.5 を疑う。**

> **1枚あたり1分前後かかる**（Cycles・CPU）。複数版はオブジェクトの数だけ焼くので、2物体で2分強。急ぐときは `scene.cycles.samples` を下げる（マスクは `samples=1` でも二値性は変わらない。[T11 ノートのレンダー時間](T11-eevee-object-index.md#アルファ実測)参照）。

## 別の `.blend` で使うとき

**書き換えるのは先頭の定数だけ**で済むように作ってある。

| スクリプト | 書き換える場所 |
|---|---|
| 単体版 | `TARGET_OBJECT_NAME`（18〜20行目付近）。既定は `"円.001"` |
| 複数版 | `OBJECT_INDEXES` の辞書（15〜19行目付近）。既定は `{"円": 1, "円.001": 2}` |

オブジェクト名が分からなければ、**わざと存在しない名前にして実行する**とステップ0のエラーがシーン内の一覧を出してくれる。

> ⚠️ **既定値は `data/synthetic_cup/cup.blend` の中身に合わせてある。** この `.blend` は T07・T11 の検証に使った2物体（`円`・`円.001`）のファイルで、[T12](../tasks/T12-prepare-blend.md) で作る Ceramic Pot の `cup.blend` とは**別物**。T12 は同じパスに Save As すると書いてあるので、**上書きする前に退避すること**（`data/` は `.gitignore` 済みで、消すと Git からは戻せない）。

## 編集するときの注意：PowerShell で一括置換しない ⚠️

**Windows PowerShell 5.1 の `Get-Content` は、BOM なし UTF-8 を ANSI（cp932）として読む。** この2本は日本語のコメントと文字列を含むので、次のような置換をすると**ファイルが壊れる**。

```powershell
# やってはいけない
(Get-Content tools\blender_id_mask_check.py) -replace '= "CYCLES"', '= "BLENDER_EEVEE"' | Set-Content -Encoding utf8 tools\blender_id_mask_check.py
```

実際にこれで壊した（2026-10-15）。症状は次のとおりで、**置換した行とは無関係な場所で落ちる**ので原因が分かりにくい。

```
File "...\blender_id_mask_check.py", line 24
    f"繧ｪ繝悶ず繧ｧ繧ｯ繝・'{TARGET_OBJECT_NAME}' 縺瑚ｦ九▽縺九ｊ縺ｾ縺帙ｓ縲・
SyntaxError: unterminated string literal
```

`Set-Content -Encoding utf8` を付けても防げない。**指定できているのは書き出し側だけで、読み込み側が ANSI のまま**だからである。

**Git Bash の `sed` を使う。** バイト列をそのまま扱うので、ASCII のパターン置換は日本語部分に触らない。

```bash
sed -i 's/= "CYCLES"/= "BLENDER_EEVEE"/' tools/blender_id_mask_check.py tools/blender_id_mask_check_multiobj.py
```

> **壊してしまったら `git restore`。** ただし**ステージしていない修正も一緒に消える**ので、置換の前に `git add` しておくと「置換だけ捨てて修正は残す」ができる。

## エンジンを EEVEE に変えて試すとき

**非対応であることの再確認**や、将来 Blender 側が対応したかの確認に使える手順。

1. `git add tools/`（**先にステージする。** これを忘れると次の `git restore` で修正ごと消える）
2. 上の `sed` で `"CYCLES"` → `"BLENDER_EEVEE"` に置換（2ファイルとも）
3. 実行する。**レンダリングまで行かず数秒で落ちるのが正解**（ガードはレンダリングの手前にある）

```
KeyError: "'Object Index' が使えません（存在=True / enabled=False）。
エンジン BLENDER_EEVEE はこのパスに非対応の可能性があります。
このエンジンで使える出力: ['Image', 'Alpha']"
```

4. `git restore tools/` で戻す。`git diff --stat`（空）と `git diff --cached --stat`（修正あり）で確認

**`存在=True / enabled=False` が、EEVEE 非対応の証拠**である。`use_pass_object_index = True` は EEVEE でもエラーにならず、読み戻すと `True` が返るので、**属性の読み戻しは対応状況の判定に使えない。**

## 未解決・気になっている点

- **`円` の白の割合が T07 当時と食い違う。** T07 の記録は `6.380%`、2026-10-15 の実行は `8.144%`。`.blend` かカメラが当時から変わった可能性がある。**方式の選定には影響しない**が、[T13](../tasks/T13-blender-render.md) でレンダリング条件を固定するときに一度合わせておきたい
- **複数版は2オブジェクト前提。** `main()` の最後が `masks` の先頭2つしか比較していない（`a, b = masks[names[0]], masks[names[1]]`）。3つ以上に増やすならここを総当たりにする必要がある

## 関連ファイル

- 4方式の比較表（判断材料本体）：[docs/notes/mask-options.md](mask-options.md)
- Blender 5.0 の API 変更で踏んだ罠6件：[docs/notes/T07-blender5-cli-troubleshooting.md](T07-blender5-cli-troubleshooting.md)
- EEVEE 非対応の切り分けと代替案の実測：[docs/notes/T11-eevee-object-index.md](T11-eevee-object-index.md)
- スクリプト本体：[tools/blender_id_mask_check.py](../../tools/blender_id_mask_check.py) ／ [tools/blender_id_mask_check_multiobj.py](../../tools/blender_id_mask_check_multiobj.py)
