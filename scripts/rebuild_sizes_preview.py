# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Eric Cheng | http://echeng.com
import bpy
import math
from pathlib import Path
from mathutils import Vector

root=Path(__file__).resolve().parents[1]
source=(root/'scripts/build_teeth.py').read_text()
bpy.ops.wm.open_mainfile(filepath=str(root/'project/pumpkin-teeth-sized.blend'))
scene=bpy.context.scene
preview=bpy.data.collections['Preview | labels and lights']
ink=bpy.data.materials['Label ivory']
DESIGNS={kind:None for kind in ['Canine','Incisor','Premolar','Molar']}
CROWN_HEIGHTS_MM=[20,25,30,35,40]
for obj in list(preview.objects):
    if obj.type in {'FONT','CAMERA'}:
        bpy.data.objects.remove(obj,do_unlink=True)
for obj in bpy.data.collections['Teeth | printable masters'].objects:
    if 'size_set_mm' in obj:
        col=list(DESIGNS).index(obj.name.split()[0])
        row=CROWN_HEIGHTS_MM.index(obj['size_set_mm'])
        obj.location=((col-1.5)*90,0,-row*82)
block=source[source.index('def label('):source.index('for name,loc,energy,size,color in [')]
exec(compile(block,'preview-layout','exec'))
scene.render.resolution_x=1600
scene.render.resolution_y=1800
scene.render.resolution_percentage=100
scene.render.filepath=str(root/'teeth-sizes-preview.png')
text=bpy.data.texts['Rebuild teeth.py']
text.clear();text.write(source)
bpy.ops.wm.save_as_mainfile(filepath=str(root/'project/pumpkin-teeth-sized.blend'))
bpy.ops.render.render(write_still=True)
print('Large-text size preview rebuilt.',flush=True)
