# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Eric Cheng | http://echeng.com
import bpy
import bmesh
import hashlib
import json
from pathlib import Path

root=Path(__file__).resolve().parents[1]
expected=json.loads((root/'project/sized-mesh-validation.json').read_text())
assert len(expected)==21
for size in [20,25,30,35,40]:
    entries=[v for v in expected.values() if v.get('size_set_mm')==size]
    assert len(entries)==4
    assert {Path(v['stl_file']).name for v in entries}=={
        f'{kind}-{size}mm.stl' for kind in ['canine','incisor','premolar','molar']}
report={}
reference_hash=None
for name,info in expected.items():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    bpy.ops.wm.stl_import(filepath=str(root/info['stl_file']),global_scale=1.0,use_scene_unit=False)
    obj=bpy.context.object
    mesh=obj.data
    bm=bmesh.new(); bm.from_mesh(mesh)
    visited=set(); components=0
    for v in bm.verts:
        if v in visited: continue
        components+=1; visited.add(v); queue=[v]
        while queue:
            a=queue.pop()
            for e in a.link_edges:
                b=e.other_vert(a)
                if b not in visited: visited.add(b); queue.append(b)
    bad_edges=sum(not e.is_manifold for e in bm.edges)
    bad_normals=sum(not e.is_contiguous for e in bm.edges if e.is_manifold)
    volume=bm.calc_volume(signed=True)
    degenerate=sum(f.calc_area()<1e-10 for f in bm.faces)
    dims=[round(float(d),2) for d in obj.dimensions]
    minimum=min(v.co.z for v in bm.verts)
    maximum=max(v.co.z for v in bm.verts)
    assert components==1 and bad_edges==0 and bad_normals==0 and degenerate==0
    assert dims==info['dimensions_mm'],(name,dims)
    assert abs(volume-info['positive_volume_mm3'])<0.02
    assert abs(minimum+20)<1e-4
    if 'crown_height_mm' in info: assert abs(maximum-info['crown_height_mm'])<1e-4
    mesh.calc_loop_triangles()
    lower=[]; crossings=0
    for tri in mesh.loop_triangles:
        coords=[mesh.vertices[i].co for i in tri.vertices]
        if min(v.z for v in coords)<-1e-5 and max(v.z for v in coords)>1e-5:
            crossings+=1
        if all(v.z<=1e-6 for v in coords):
            lower.append(sorted(tuple(round(float(c),5) for c in v) for v in coords))
    assert crossings==0,(name,crossings)
    digest=hashlib.sha256(json.dumps(sorted(lower)).encode()).hexdigest()
    reference_hash=reference_hash or digest
    assert digest==reference_hash==info['mount_surface_sha256']
    # Measure the actual lathed shaft and barb rings in the exported mesh.
    shaft_z=-11.1*20/24
    barb_z=-7.4*20/24
    shaft=[v for v in bm.verts if abs(v.co.z-shaft_z)<1e-4]
    barb=[v for v in bm.verts if abs(v.co.z-barb_z)<1e-4]
    shaft_diameter=max(v.co.x for v in shaft)-min(v.co.x for v in shaft)
    barb_diameter=max(v.co.x for v in barb)-min(v.co.x for v in barb)
    assert abs(shaft_diameter-5)<1e-4 and abs(barb_diameter-7.5)<1e-4
    report[info['stl_file']]=dict(dimensions_mm=dims,connected_components=components,
        non_manifold_edges=bad_edges,inconsistent_normal_edges=bad_normals,
        degenerate_triangles=degenerate,positive_volume_mm3=round(volume,2),
        crown_height_mm=info.get('crown_height_mm'),size_set_mm=info.get('size_set_mm'),mount_length_mm=20,
        measured_shaft_diameter_mm=round(shaft_diameter,5),
        measured_barb_diameter_mm=round(barb_diameter,5),
        mount_surface_sha256=digest,triangles_crossing_root_plane=crossings,
        reimport_verified=True)
    bm.free()
    print('STL VERIFIED',info['stl_file'],dims,flush=True)

bpy.ops.wm.open_mainfile(filepath=str(root/'project/pumpkin-teeth-sized.blend'))
masters=bpy.data.collections['Teeth | printable masters'].objects
assert len(masters)==len(expected)
assert all(bpy.data.objects.get(info['object_name']) for info in expected.values() if 'object_name' in info)
assert 'CROWN_HEIGHTS_MM = [20, 25, 30, 35, 40]' in bpy.data.texts['Rebuild teeth.py'].as_string()
assert abs(bpy.context.scene.unit_settings.scale_length-.001)<1e-8
(root/'project/sized-stl-verification.json').write_text(json.dumps(report,indent=2))
print(f'ALL {len(expected)} EXPORTS AND BLENDER PROJECT VERIFIED',flush=True)
