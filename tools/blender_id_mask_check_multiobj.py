"""複数オブジェクトがあるシーンで、ID Mask方式が正しく描き分けられるかを確認するスクリプト。

T07（docs/notes/mask-options.md）の「決めるときの質問」3番目
（被写体が増えたとき＝回転台＋被写体の2物体で破綻しないか）の代替検証として、
同じシーン内にある2つのオブジェクト（円・円.001）それぞれにパスインデックスを振り、
それぞれを正しく単独でマスクできるかを確認する。

使い方:
    blender --background data/synthetic_cup/cup.blend --python tools/blender_id_mask_check_multiobj.py
"""

import bpy
import numpy as np

# オブジェクト名 → 割り当てるパスインデックス
OBJECT_INDEXES = {
    "円": 1,
    "円.001": 2,
}
OUTPUT_DIR = "//output/"


def setup_scene():
    scene = bpy.context.scene
    view_layer = scene.view_layers[0]

    for name in OBJECT_INDEXES:
        if name not in bpy.data.objects:
            available = [o.name for o in bpy.data.objects]
            raise KeyError(f"オブジェクト '{name}' が見つかりません。シーン内: {available}")

    scene.render.engine = "CYCLES"
    # マスクを歪める色管理・ディザリングを無効化（T07で確認済みの罠）
    scene.view_settings.view_transform = "Standard"
    scene.render.dither_intensity = 0.0

    for name, idx in OBJECT_INDEXES.items():
        bpy.data.objects[name].pass_index = idx

    view_layer.use_pass_object_index = True

    tree = bpy.data.node_groups.new("MultiObjMaskCheck", "CompositorNodeTree")
    scene.compositing_node_group = tree
    scene.render.use_compositing = True
    tree.interface.new_socket(name="Image", in_out="OUTPUT", socket_type="NodeSocketColor")

    render_layers = tree.nodes.new(type="CompositorNodeRLayers")
    render_layers.scene = scene
    render_layers.layer = view_layer.name
    if "Object Index" not in render_layers.outputs:
        available = [o.name for o in render_layers.outputs]
        raise KeyError(f"'Object Index' 出力ソケットが見つかりません。利用可能な出力: {available}")

    id_mask = tree.nodes.new(type="CompositorNodeIDMask")
    id_mask.inputs["Anti-Alias"].default_value = False
    group_output = tree.nodes.new(type="NodeGroupOutput")
    tree.links.new(render_layers.outputs["Object Index"], id_mask.inputs["ID value"])
    tree.links.new(id_mask.outputs["Alpha"], group_output.inputs["Image"])

    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"

    return scene, id_mask


def render_mask_for(scene, id_mask, name, index):
    id_mask.inputs["Index"].default_value = index
    output_path = f"{OUTPUT_DIR}mask_{name.replace('.', '_')}.png"
    scene.render.filepath = output_path
    bpy.ops.render.render(write_still=True)
    print(f"[{name}] index={index} -> {output_path}")

    img = bpy.data.images.load(bpy.path.abspath(output_path))
    w, h = img.size
    pixels = np.array(img.pixels[:]).reshape(h, w, 4)
    channel = pixels[..., 0]
    unique_vals = np.unique(np.round(channel, 3))
    white_ratio = float(np.mean(channel > 0.5))
    print(
        f"  ユニークな画素値: {unique_vals} ／ 種類数: {len(unique_vals)} "
        f"／ 白の割合: {white_ratio:.3%}"
    )
    return channel, unique_vals


def main():
    scene, id_mask = setup_scene()

    masks = {}
    for name, idx in OBJECT_INDEXES.items():
        channel, unique_vals = render_mask_for(scene, id_mask, name, idx)
        masks[name] = channel
        assert len(unique_vals) <= 2, f"{name} のマスクが二値になっていません: {unique_vals}"

    names = list(masks.keys())
    a, b = masks[names[0]], masks[names[1]]
    overlap = int(np.logical_and(a > 0.5, b > 0.5).sum())
    print(
        f"\n{names[0]} と {names[1]} のマスクの重なり画素数: {overlap}"
        "（0であれば正しく分離できている）"
    )
    if np.array_equal(a, b):
        print("警告: 2つのマスクが完全に同一です。オブジェクトが分離できていません。")
    else:
        print("結果: 2つのマスクは異なっています（オブジェクトごとに正しく描き分けられました）。")


if __name__ == "__main__":
    main()
