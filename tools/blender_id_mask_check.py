"""ID Mask方式でオブジェクトの二値マスクをCLIから自動生成できるか確認するスクリプト。

T07（docs/notes/mask-options.md）の「スクリプトから自動化できるか」
「出力が二値になるか」を、GUIを開かずに確認するための検証用スクリプト。

Blender 5.0 でコンポジターのPython APIが変更されている点に注意
（https://developer.blender.org/docs/release_notes/5.0/migration/compositor_migration/）。
- `scene.node_tree` は廃止 → `scene.compositing_node_group`（独立したデータブロック）
- `Composite` ノードは廃止 → `Group Output` ノード

使い方:
    blender --background data/synthetic_cup/cup.blend --python tools/blender_id_mask_check.py
"""

import bpy
import numpy as np

# ここを対象の .blend ファイルに合わせて書き換える
TARGET_OBJECT_NAME = "円.001"
TARGET_INDEX = 1
OUTPUT_PATH = "//output/mask_cli.png"  # .blend ファイルからの相対パス


def main():
    scene = bpy.context.scene
    view_layer = scene.view_layers[0]

    if TARGET_OBJECT_NAME not in bpy.data.objects:
        available = [o.name for o in bpy.data.objects]
        raise KeyError(
            f"オブジェクト '{TARGET_OBJECT_NAME}' が見つかりません。"
            f"シーン内のオブジェクト: {available}"
        )

    # 1. レンダーエンジンをCyclesに
    scene.render.engine = "CYCLES"

    # 1.5. 色管理をオフにする（重要）
    # デフォルトのView Transform（AgX等）はトーンマッピングのため、
    # 0/1のマスク値がPNG保存時に中間値に歪められる。マスクは「データ」なので
    # Standardにして0→0・1→1がそのまま保存されるようにする。
    scene.view_settings.view_transform = "Standard"
    print("View Transform:", scene.view_settings.view_transform)

    # ディザリング（8bit変換時にバンディング防止でノイズを加える機能）も
    # マスク用途では不要なので無効化する
    scene.render.dither_intensity = 0.0

    # 2. 対象オブジェクトにパスインデックスを設定
    obj = bpy.data.objects[TARGET_OBJECT_NAME]
    obj.pass_index = TARGET_INDEX

    # 3. View Layerでオブジェクトインデックスパスを有効化
    view_layer.use_pass_object_index = True

    # 4. コンポジタのノードツリーを構築（Blender 5.0 の新API）
    tree = bpy.data.node_groups.new("MaskCheck", "CompositorNodeTree")
    scene.compositing_node_group = tree
    scene.render.use_compositing = True  # 出力プロパティの「Post Processing > Compositing」に相当

    tree.interface.new_socket(name="Image", in_out="OUTPUT", socket_type="NodeSocketColor")

    render_layers = tree.nodes.new(type="CompositorNodeRLayers")
    # 既知の問題：スクリプトでパスを有効化しても、Render Layersノードの
    # 出力ソケット一覧はすぐには更新されない。scene を再代入すると更新される。
    render_layers.scene = scene
    render_layers.layer = view_layer.name
    if "Object Index" not in render_layers.outputs:
        available = [o.name for o in render_layers.outputs]
        raise KeyError(
            f"'Object Index' 出力ソケットが見つかりません。利用可能な出力: {available}"
        )

    id_mask = tree.nodes.new(type="CompositorNodeIDMask")
    # Blender 5.0 では Index / Anti-Alias もノードの属性ではなく入力ソケットになった
    id_mask.inputs["Index"].default_value = TARGET_INDEX
    id_mask.inputs["Anti-Alias"].default_value = False  # 二値化のポイント
    group_output = tree.nodes.new(type="NodeGroupOutput")

    tree.links.new(render_layers.outputs["Object Index"], id_mask.inputs["ID value"])
    tree.links.new(id_mask.outputs["Alpha"], group_output.inputs["Image"])

    # 5. 出力設定
    scene.render.filepath = OUTPUT_PATH
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"

    # 6. レンダリング実行
    bpy.ops.render.render(write_still=True)
    print("レンダリング完了:", OUTPUT_PATH)

    # 7. 二値になっているかをこのスクリプト内でチェック
    img = bpy.data.images.load(bpy.path.abspath(OUTPUT_PATH))
    w, h = img.size
    pixels = np.array(img.pixels[:]).reshape(h, w, 4)
    unique_vals = np.unique(np.round(pixels[..., 0], 3))
    print("ユニークな画素値:", unique_vals, "／ 種類数:", len(unique_vals))


if __name__ == "__main__":
    main()
