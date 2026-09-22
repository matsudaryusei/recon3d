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
