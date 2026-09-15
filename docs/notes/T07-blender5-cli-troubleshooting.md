# T07：Blender 5.0 でのマスク生成CLI自動化、詰まった点 2026/09/16

[docs/notes/mask-options.md](mask-options.md)（T07本体の判断材料）を作る過程で、GUIでの手動確認は問題なく通ったが、**同じ内容をCLI（`blender --background --python`）から自動実行しようとすると6段階でエラーが出た。** 内容自体は mask-options.md の比較表・実機確認結果にも反映済みだが、他の人が同じ壁にぶつからないよう経緯として残す。

## 前提として分かったこと

**ネット上のBlender Python API解説記事は、ほとんどが Blender 4.5 以前（コンポジター刷新前）の書き方。** そのままコピペすると動かない。Blender 5.0 の変更点は公式の [Compositor Migration](https://developer.blender.org/docs/release_notes/5.0/migration/compositor_migration/) が一次情報として一番信頼できる。

## つまずいた順番

1. **`scene.node_tree` が無い** → コンポジットノードツリーが `scene.compositing_node_group` という独立したデータブロックに変わった。`Composite` ノードも廃止されて `Group Output` ノードに置き換わっている
2. **`id_mask.index` が無い** → 「多くのノードのオプションが入力ソケット化された」という5.0の方針変更で、`id_mask.inputs["Index"].default_value` のようにソケット経由で設定する形になった
3. **`IndexOB` ソケットが無い**（`KeyError`） → Render Layers ノードの出力ソケット一覧は、スクリプトでパスを有効化しても**即座には更新されない既知の不具合**（[T48760](https://developer.blender.org/T48760)）。`render_layers.scene = scene` と自分自身に再代入すると更新される、という回避策が知られている
4. **ソケット名が違う** → `IndexOB` ではなく `Object Index` という人間可読な名前に変わっていた（③のエラーメッセージで利用可能なソケット名一覧を出力させたことで発見できた）
5. **二値のはずが中間値**（`[0. 0.004 0.804 0.808 0.812]`） → デフォルトの **View Transform（AgX）** が写真的なトーンマッピングをかけていて、0/1のマスク値を歪めて保存していた。`scene.view_settings.view_transform = "Standard"` で解消
6. **上記対処後も僅かなズレ**（`[0. 0.004 0.996 1.]`） → デフォルトで有効な**ディザリング**（8bit変換時のバンディング防止ノイズ）が原因。`scene.render.dither_intensity = 0.0` で解消

## 学んだこと・次に活かせること

- **エラーメッセージに「利用可能な選択肢一覧」を出させるとデバッグが速い。** ③・④はどちらも `KeyError` だったが、例外メッセージに `[o.name for o in render_layers.outputs]` を含めるようにしたことで、正しいソケット名 `Object Index` がすぐ分かった。以後もこのパターン（存在チェック→失敗したら候補一覧を出す）を使う
- **「二値になっているはず」を過信しない。** コンポジタのノード計算自体は正しく0/1を出していても、**保存パイプライン（色管理・ディザリング）側で値が変わる**ことがある。マスクのように「データ」として使う画像は、必ずレンダリング後に実際のPNGを読み込んで画素値を検証するところまでやる（今回は `numpy` でユニークな画素値を出力するようにした）
- **GUIで動いた手順を、そのままCLIスクリプトに翻訳しても動くとは限らない。** GUI操作は裏で「再描画のたびに内部状態を同期する」処理が挟まるが、スクリプト一発実行ではその同期が起きないケースがある（③がまさにこれ）

## 関連ファイル

- 判断材料本体：[docs/notes/mask-options.md](mask-options.md)
- 単体オブジェクトの自動検証スクリプト：[tools/blender_id_mask_check.py](../../tools/blender_id_mask_check.py)
- 2オブジェクト分離の自動検証スクリプト：[tools/blender_id_mask_check_multiobj.py](../../tools/blender_id_mask_check_multiobj.py)
