# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Eric Cheng | http://echeng.com
"""Pumpkin teeth, millimeter geometry. Run in Blender's Text Editor to rebuild.

Edit CROWN_HEIGHTS_MM for size sets; canines are 25% taller than each set size.
The mounting harpoon is 20 mm long, with a 5 mm core and 7.5 mm barbs.
Outputs use the sizes/, project/, and zips/ folder organization.
"""
import bpy
import bmesh
import math
import json
import struct
import hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

editor = getattr(bpy.context, 'space_data', None)
if editor and editor.type == 'TEXT_EDITOR' and editor.text:
    SOURCE_TEXT = editor.text.as_string()
else:
    SOURCE_TEXT = Path(__file__).read_text()

CROWN_HEIGHTS_MM = [20, 25, 30, 35, 40]
CANINE_HEIGHT_FACTOR = 1.25
CANINE_WIDTH_FACTOR = 1.25
CANINE_DEPTH_FACTOR = 1.20
STEM_LENGTH = 20.0
STEM_DIAMETER = 5.0
BARB_DIAMETER = 7.5
VOXEL_SIZE = 0.12
OUTPUT = Path(bpy.path.abspath('//')) if bpy.data.filepath else Path(__file__).resolve().parents[1]
if OUTPUT.name == 'project': OUTPUT = OUTPUT.parent
OUTPUT.mkdir(parents=True, exist_ok=True)
PROJECT = OUTPUT/'project'
PROJECT.mkdir(parents=True, exist_ok=True)

# Ring profiles are z, half-width, half-thickness, and lateral displacement.
DESIGNS = {
    'Canine': [
        (-0.6, 4.4, 4.0, 0), (1.4, 6.3, 5.4, 0),
        (5, 8.3, 6.7, -0.4), (10, 9.3, 7.2, -0.2),
        (16, 8.9, 7.0, 0.7), (22, 7.0, 5.8, 1.8),
        (27, 4.7, 4.0, 3.0), (31, 2.7, 2.3, 4.0),
        (33, 1.3, 1.1, 4.5), (34, 0.20, 0.20, 4.7)],
    'Incisor': [
        (-0.6, 4.4, 4.0, 0), (1.5, 6.2, 4.7, 0),
        (5, 8.4, 5.8, -0.1), (10, 10.3, 6.5, -0.1),
        (16, 10.9, 6.7, 0.2), (21, 10.3, 6.0, 0.4),
        (24.2, 9.4, 4.9, 0.5), (26, 7.9, 3.5, 0.7),
        (26.8, 5.6, 1.9, 0.8), (27, 0.20, 0.20, 0.8)],
    'Premolar': [
        (-0.6, 4.4, 4.0, 0), (1.5, 6.3, 5.0, 0),
        (5, 9.0, 6.8, -0.2), (10, 10.8, 8.0, -0.3),
        (15, 11.2, 8.2, 0), (19, 10.9, 7.9, 0.2),
        (22, 9.7, 6.8, 0.3), (24.3, 7.7, 4.5, 0.4),
        (25.1, 4.5, 2.7, 0.6), (25.5, 0.20, 0.20, 0.6)],
    'Molar': [
        (-0.6, 4.4, 4.0, 0), (1.5, 6.4, 5.4, 0),
        (5, 9.5, 7.6, -0.2), (10, 12.2, 9.1, -0.4),
        (16, 13.0, 9.4, -0.1), (21, 12.8, 9.2, 0.3),
        (24, 11.8, 8.5, 0.5), (25.5, 9.7, 6.9, 0.5),
        (26.0, 6.0, 4.2, 0.5), (26.1, 0.20, 0.20, 0.5)]}

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for c in list(bpy.data.collections): bpy.data.collections.remove(c)
models = bpy.data.collections.new('Teeth | printable masters')
bpy.context.scene.collection.children.link(models)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 0.001
scene.unit_settings.length_unit = 'MILLIMETERS'

def active(obj):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

def mesh_object(name, vertices, faces, collection=models):
    mesh = bpy.data.meshes.new(name + ' geometry')
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(mesh)
    bm.free()
    return obj

def loft(name, rings, count=96, deform=None):
    verts, faces = [], []
    for z, rx, ry, shift in rings:
        for i in range(count):
            theta = 2 * math.pi * i / count
            x, y = rx * math.cos(theta), ry * math.sin(theta)
            zz = z
            if deform:
                x, y, zz = deform(x, y, z, rx, ry, theta)
            verts.append((x + shift, y, zz))
    for j in range(len(rings)-1):
        for i in range(count):
            a, b = j*count+i, j*count+(i+1)%count
            faces.append((a, b, b+count, a+count))
    faces.append(tuple(reversed(range(count))))
    faces.append(tuple((len(rings)-1)*count+i for i in range(count)))
    return mesh_object(name, verts, faces)

def crown_deform(kind):
    height = DESIGNS[kind][-1][0]
    def deform(x, y, z, rx, ry, theta):
        t = max(0.0, z / height)
        envelope = math.sin(math.pi * min(1.0, t)) ** 1.2
        # Broad asymmetry on opposite faces is real printable surface geometry.
        swell = 1 + envelope * (0.045*math.sin(3*theta+0.5) + 0.035*math.cos(2*theta-0.4))
        x *= swell
        y *= swell
        front = max(0.0, -math.sin(theta)) ** 4
        back = max(0.0, math.sin(theta)) ** 4
        # One crooked longitudinal groove in front; two shallower ridges behind.
        groove_x = -1.8 + 2.8*t
        y += 0.75 * math.exp(-((x-groove_x)/0.9)**2) * envelope * front
        y += 0.42 * math.cos(x*0.8+0.4) * envelope * back
        if kind == 'Canine':
            y += 0.85 * math.sin(t*math.pi) * math.sin(theta+0.7)
            # Abraded shoulder rather than a needle-like fang.
            z -= 0.65 * math.exp(-((x-3.8)/1.2)**2) * front * t**4
        elif kind == 'Incisor':
            z += (0.65*math.sin(theta+0.9) + 0.6*x/11) * t**5
            z -= 1.75*math.exp(-((x+2.7)/1.05)**2) * t**7
            y += 0.35 * math.exp(-((x-5)/1.4)**2) * front * envelope
        elif kind == 'Premolar':
            # Broad rounded cusps separated by a physical saddle.
            z -= 4.7 * math.exp(-((x+0.6)/2.4)**2) * t**6
            z += 0.8 * (x/11) * t**5
            y -= 0.7 * math.exp(-((x-4)/2.0)**2) * front * envelope
        else:
            # Three worn lobes on a broad crown, with different chipped shoulders.
            z -= 2.0 * (math.exp(-((x+4.4)/1.5)**2)
                        + math.exp(-((x-4.0)/1.4)**2)) * t**6
            z += 0.8 * (x/13) * t**5
            z -= 2.0 * math.exp(-((x-8.2)/2.0)**2) * front * t**5
            z -= 1.2 * math.exp(-((x+7.0)/2.4)**2) * back * t**5
            y += 0.8 * math.exp(-((x+5.0)/1.2)**2) * front * envelope
            y -= 0.6 * math.exp(-((x-5.5)/1.8)**2) * back * envelope
        return x, y, z
    return deform

def make_mount(name):
    r = STEM_DIAMETER/2
    b = BARB_DIAMETER/2
    profile = [
        (-24, 0.12), (-23.85, 0.38), (-23.2, 0.75),
        (-21.6, 1.65), (-19.5, r), (-19.1, r),
        (-15.6, b-0.20), (-15.4, b), (-15.2, b-0.06),
        (-15.0, r+0.25), (-14.8, r), (-11.1, r),
        (-7.6, b-0.20), (-7.4, b), (-7.2, b-0.06),
        (-7.0, r+0.25), (-6.8, r), (-4.2, r),
        (-3.6, r+0.18), (-2.2, 3.2), (-0.8, 3.5), (0, 3.5), (2.5, 3.5)]
    rings = [(z*STEM_LENGTH/24 if z < 0 else z,r,r,0) for z,r in profile]
    obj = loft(name, rings)
    bm = bmesh.new(); bm.from_mesh(obj.data)
    bmesh.ops.triangulate(bm, faces=list(bm.faces))
    bm.to_mesh(obj.data); bm.free()
    return obj

def apply_modifier(obj, mod):
    active(obj)
    bpy.ops.object.modifier_apply(modifier=mod.name)

def make_crown(kind):
    crown = loft(kind, DESIGNS[kind], deform=crown_deform(kind))
    sub = crown.modifiers.new('Rounded crown', 'SUBSURF')
    sub.levels = 2
    apply_modifier(crown, sub)
    # Remesh the crown alone; the shared mount never passes through a voxel grid.
    remesh = crown.modifiers.new('Closed printable surface', 'REMESH')
    remesh.mode = 'VOXEL'
    remesh.voxel_size = VOXEL_SIZE
    remesh.use_smooth_shade = True
    apply_modifier(crown, remesh)
    smooth = crown.modifiers.new('Round tiny corners', 'SMOOTH')
    smooth.factor = 0.35
    smooth.iterations = 3
    apply_modifier(crown, smooth)
    simplify = crown.modifiers.new('Efficient printable mesh', 'DECIMATE')
    simplify.ratio = 0.25
    apply_modifier(crown, simplify)
    bm = bmesh.new()
    bm.from_mesh(crown.data)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bmesh.ops.triangulate(bm, faces=list(bm.faces))
    bm.to_mesh(crown.data)
    bm.free()
    for p in crown.data.polygons: p.use_smooth = True
    return crown

def make_tooth(kind, height, base):
    size_set = height
    if kind == 'Canine': height *= CANINE_HEIGHT_FACTOR
    name = f'{kind} {size_set} mm set | {height:g} mm crown'
    crown = bpy.data.objects.new(name, base.data.copy())
    models.objects.link(crown)
    lo = min(v.co.z for v in crown.data.vertices)
    hi = max(v.co.z for v in crown.data.vertices)
    factor = height / (hi-lo)
    for v in crown.data.vertices:
        v.co.x *= factor
        v.co.y *= factor
        v.co.z = (v.co.z-lo)*factor
        if kind == 'Canine':
            v.co.x *= CANINE_WIDTH_FACTOR
            v.co.y *= CANINE_DEPTH_FACTOR
    stem = make_mount('Shared mount')
    union = crown.modifiers.new('Integrated harpoon', 'BOOLEAN')
    union.operation = 'UNION'
    union.solver = 'EXACT'
    union.object = stem
    apply_modifier(crown, union)
    bpy.data.objects.remove(stem, do_unlink=True)
    bm = bmesh.new(); bm.from_mesh(crown.data)
    bmesh.ops.remove_doubles(bm, verts=[v for v in bm.verts if v.co.z > 1e-6], dist=1e-5)
    bmesh.ops.dissolve_degenerate(bm, edges=[e for e in bm.edges if all(v.co.z >= 0 for v in e.verts)], dist=1e-5)
    bmesh.ops.triangulate(bm, faces=list(bm.faces))
    for _ in range(2):
        bmesh.ops.dissolve_degenerate(bm, edges=[e for e in bm.edges if all(v.co.z >= 0 for v in e.verts)], dist=1e-4)
        bmesh.ops.triangulate(bm, faces=list(bm.faces))
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(crown.data); bm.free()
    for p in crown.data.polygons: p.use_smooth = True
    crown['crown_height_mm'] = height
    crown['size_set_mm'] = size_set
    crown['mount_length_mm'] = STEM_LENGTH
    crown['stem_diameter_mm'] = STEM_DIAMETER
    crown['barb_diameter_mm'] = BARB_DIAMETER
    crown['rotation_note'] = 'Rotate 180 degrees about local Z to expose the opposite face.'
    return crown

def mount_signature(obj):
    mesh = obj.data
    mesh.calc_loop_triangles()
    faces = []
    for tri in mesh.loop_triangles:
        coords = [mesh.vertices[i].co for i in tri.vertices]
        if all(v.z <= 1e-6 for v in coords):
            faces.append(sorted(tuple(round(float(c),5) for c in v) for v in coords))
    return hashlib.sha256(json.dumps(sorted(faces)).encode()).hexdigest(), len(faces)

def validate(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    components, visited = 0, set()
    for v in bm.verts:
        if v in visited: continue
        components += 1
        queue = [v]
        visited.add(v)
        while queue:
            current = queue.pop()
            for e in current.link_edges:
                other = e.other_vert(current)
                if other not in visited:
                    visited.add(other)
                    queue.append(other)
    bad_edges = sum(not e.is_manifold for e in bm.edges)
    bad_normals = sum(not e.is_contiguous for e in bm.edges if e.is_manifold)
    degenerate = sum(f.calc_area() < 1e-10 for f in bm.faces)
    if degenerate:
        print('TINY TRIANGLES',obj.name,[[tuple(v.co) for v in f.verts] for f in bm.faces if f.calc_area()<1e-10],flush=True)
    volume = bm.calc_volume(signed=True)
    vertices = [v.co.copy() for v in bm.verts]
    bm.verts.index_update()
    triangles = [tuple(v.index for v in f.verts) for f in bm.faces]
    tree = BVHTree.FromPolygons(vertices, triangles, all_triangles=True, epsilon=0.0)
    intersections = 0
    for a,b in tree.overlap(tree):
        if a >= b: continue
        if set(triangles[a]).isdisjoint(triangles[b]): intersections += 1
    mins = [min(v[i] for v in vertices) for i in range(3)]
    maxs = [max(v[i] for v in vertices) for i in range(3)]
    result = dict(vertices=len(vertices), triangles=len(triangles),
        connected_components=components, non_manifold_edges=bad_edges,
        inconsistent_normal_edges=bad_normals, degenerate_triangles=degenerate,
        non_adjacent_triangle_intersections=intersections,
        positive_volume_mm3=round(volume,2),
        dimensions_mm=[round(maxs[i]-mins[i],2) for i in range(3)],
        bounds_mm=[mins,maxs])
    bm.free()
    assert components == 1 and bad_edges == 0 and bad_normals == 0
    assert volume > 0 and degenerate == 0 and intersections == 0, result
    return result

def export_stl(obj, filepath):
    # STL is unitless. Vertex coordinates here are explicitly millimeters.
    mesh = obj.data
    mesh.calc_loop_triangles()
    with open(filepath, 'wb') as f:
        f.write(b'Pumpkin teeth | coordinates in millimeters'.ljust(80, b'\0'))
        f.write(struct.pack('<I', len(mesh.loop_triangles)))
        for tri in mesh.loop_triangles:
            coords = [mesh.vertices[i].co for i in tri.vertices]
            normal = (coords[1]-coords[0]).cross(coords[2]-coords[0]).normalized()
            values = list(normal)
            for v in coords: values.extend(v)
            f.write(struct.pack('<12fH', *values, 0))

def material(name, color, roughness):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color,1)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*color,1)
    bsdf.inputs['Roughness'].default_value = roughness
    return mat

bone = material('Warm ivory | preview only', (0.66,0.55,0.36), 0.32)
ink = material('Label ivory', (0.65,0.68,0.70), 1.0)
report = {}
teeth = []
base_crowns = {kind: make_crown(kind) for kind in DESIGNS}
signature = None
for row,height in enumerate(CROWN_HEIGHTS_MM):
    folder = OUTPUT/'sizes'/f'{height}mm'
    folder.mkdir(parents=True, exist_ok=True)
    for col,kind in enumerate(DESIGNS):
        obj = make_tooth(kind,height,base_crowns[kind])
        key = f'{kind} {height} mm'
        result = validate(obj)
        sig, count = mount_signature(obj)
        signature = signature or sig
        assert sig == signature, ('Mount changed',key)
        actual_height = obj['crown_height_mm']
        assert abs(result['bounds_mm'][1][2] - actual_height) < 0.001
        assert abs(result['bounds_mm'][0][2] + STEM_LENGTH) < 0.001
        result.update(crown_height_mm=actual_height, size_set_mm=height,
            object_name=obj.name, mount_length_mm=STEM_LENGTH,
            shaft_diameter_mm=STEM_DIAMETER, barb_diameter_mm=BARB_DIAMETER,
            mount_surface_sha256=sig, mount_triangles=count,
            stl_file=f'sizes/{height}mm/{kind.lower()}-{height}mm.stl')
        report[key] = result
        export_stl(obj, OUTPUT/result['stl_file'])
        obj.data.materials.append(bone)
        obj.location = ((col-(len(DESIGNS)-1)/2)*90, 0, -row*82)
        teeth.append(obj)
        print('VALIDATED',key,json.dumps(result),flush=True)
for base in base_crowns.values(): bpy.data.objects.remove(base,do_unlink=True)

test = make_mount('Mount fit test | 20 mm')
report['Mount fit test'] = validate(test)
sig,count = mount_signature(test)
assert sig == signature, 'Test mount differs from teeth'
report['Mount fit test'].update(mount_surface_sha256=sig, mount_triangles=count,
    stl_file='project/mount-fit-test-20mm.stl', mount_length_mm=STEM_LENGTH,
    shaft_diameter_mm=STEM_DIAMETER, barb_diameter_mm=BARB_DIAMETER)
export_stl(test,PROJECT/'mount-fit-test-20mm.stl')
test.hide_render=True
test.hide_set(True)

preview=bpy.data.collections.new('Preview | labels and lights')
scene.collection.children.link(preview)

def label(text,x,z,size,centered=True):
    curve=bpy.data.curves.new(text,'FONT')
    curve.body=text
    curve.align_x='CENTER' if centered else 'LEFT'
    curve.size=size
    obj=bpy.data.objects.new(text,curve)
    preview.objects.link(obj)
    obj.location=(x,-8,z)
    obj.rotation_euler=(math.pi/2,0,0)
    obj.data.materials.append(ink)

label('PUMPKIN TEETH',-20,106,24)
label('Crown sizes in mm / canines are 25% taller',-20,84,12)
for col,kind in enumerate(DESIGNS): label(kind.upper(),(col-(len(DESIGNS)-1)/2)*90,59,16)
label('25% taller',-135,41,11)
label('SET SIZE',-220,59,13)
for row,height in enumerate(CROWN_HEIGHTS_MM):
    label(f'{height} mm',-220,-row*82+9,18)
label('Shared harpoon: 20 mm long\n5 mm shaft / 7.5 mm barbs',-20,-380,12)

def aim(obj,target):
    obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()

camdata=bpy.data.cameras.new('Size comparison camera')
cam=bpy.data.objects.new('Size comparison camera',camdata)
preview.objects.link(cam)
cam.location=(-20,-600,-150)
aim(cam,(-20,0,-150))
camdata.type='ORTHO'
camdata.ortho_scale=560
camdata.clip_end=2000
scene.camera=cam

for name,loc,energy,size,color in [
    ('Large warm key',(-150,-180,120),900000,240,(1,.88,.72)),
    ('Cool fill',(140,-150,-120),500000,260,(.73,.84,1)),
    ('Lower key',(-80,-100,-370),320000,180,(1,.88,.72)),
    ('Rim',(70,100,-80),600000,190,(1,.73,.45))]:
    data=bpy.data.lights.new(name,'AREA'); data.energy=energy
    data.shape='DISK'; data.size=size; data.color=color
    obj=bpy.data.objects.new(name,data); preview.objects.link(obj)
    obj.location=loc; aim(obj,(0,0,-150))
scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.025,.033,.045,1)
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.40
scene.render.engine='CYCLES'
scene.cycles.samples=48
scene.cycles.use_denoising=True
scene.render.resolution_x=1600
scene.render.resolution_y=1800
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.render.filepath=str(OUTPUT/'teeth-sizes-preview.png')
scene.view_settings.view_transform='AgX'

readme='''Pumpkin teeth | 20-40 mm size sets | millimeter geometry

Designs by Eric Cheng | http://echeng.com
MIT license. Copyright (c) 2026 Eric Cheng. See LICENSE.

20 individual teeth: canine, incisor, premolar and molar, in size sets
20, 25, 30, 35, and 40 mm. Sizes are organized in sizes/20mm through sizes/40mm.
Folder and STL filename sizes identify the set. Incisor, premolar and molar crown
heights equal the set size. Canines are 25% taller and have thicker crowns.
Crown height is measured from the root plane z=0 to the highest tooth tip.
The complete object is its actual crown height + 20 mm for the harpoon.

Set size   Other tooth crowns      Canine crown   Canine total length
20 mm      20 mm                   25 mm          45 mm
25 mm      25 mm                   31.25 mm       51.25 mm
30 mm      30 mm                   37.5 mm        57.5 mm
35 mm      35 mm                   43.75 mm       63.75 mm
40 mm      40 mm                   50 mm          70 mm

Canines have an additional 25% increase in width and 20% in front-to-back
thickness beyond the enlargement from the taller crown. Other crown designs
keep their existing proportions. All mounting geometry remains fixed.
Current assets are in sizes/ and project/. Download the repository with
GitHub Code > Download ZIP, or generate size packs using scripts/package_teeth.py.
Generated packs are written to zips/ and are excluded from Git.
See README-FOR-CHATGPT.md for design changes and verification.
The original unsized builds have been removed.

Each size set contains four designs: a curved canine, a worn incisor, a
two-cusp premolar and a broad, blunt molar with uneven worn lobes and chipped
shoulders. Print four copies of each design for four canines and twelve
assorted teeth (four incisors, four premolars and four molars), sixteen total.

Mount: 20 mm below the root plane, 5 mm shaft, 7.5 mm maximum barb diameter,
two circular barbs and a 7 mm root collar. All 20 teeth and the mount test share
identical triangulated surfaces at and below z=0. Hashes are in the validation
report. The upper end of the mount extends 2.5 mm inside the crown for the union.

Opposite crown faces differ. Rotate 180 degrees about the insertion axis for
variety. All teeth are one connected, closed mesh with positive volume.
The crown points along +Z. The insertion point points along -Z.

PRINTING
STL files contain coordinates in millimeters. Import at 100% scale as mm.
Uniform slicer scaling changes the mount dimensions, so select a supplied size.
Check total length against the table above; it includes the harpoon.
Print project/mount-fit-test-20mm.stl first, then the 50 mm canine crown to test leverage in actual
pumpkin flesh. Geometry checks do not establish insertion force or retention.

FDM starting point: 0.2 mm layers, four walls. Lay a tooth on a broad crown face,
with its long axis approximately parallel to the bed, and use underside supports
as required for the crown and barbs. Inspect the sliced junction and barb layers.
Printer, filament and support settings may require adjustment.

BAMBU STUDIO: LIGHT CROWN, SOLID HARPOON
These are starting settings for a 0.4 mm nozzle. The existing STL can be printed
with a lightly filled crown; the slicer creates the shell and interior infill.

1. Import a supplied STL in millimeters at 100% scale. Select your printer,
   filament and a 0.20 mm process preset. Enable Advanced settings if needed.

2. In Process > Global > Strength, set:
   Wall loops: 4
   Sparse infill density: 10%
   Sparse infill pattern: Gyroid
   Top shell layers: 5
   Bottom shell layers: 5
   At 0.20 mm layer height, five solid layers give approximately 1 mm thickness.
   Check any top/bottom shell thickness settings: larger minimum thicknesses
   can cause the slicer to add more solid layers (Bambu Lab, n.d.-b).

3. Orient the tooth with its long axis approximately parallel to the bed.
   Enable supports for the underside of the crown and barbs.

4. Right-click the tooth > Add modifier > Cube. Resize and move the transparent
   cube to cover the entire harpoon, neck and approximately 5 mm into the crown.
   The cube can extend outside the tooth; only its overlap changes the print.

5. Switch Process > Objects. Expand the tooth in the object list and select
   the Cube underneath it. In this modifier's Strength settings, set:
   Sparse infill density: 100%
   Sparse infill pattern: Rectilinear
   Keep the Cube selected while editing these settings. Modifier settings use
   per-object mode (Bambu Lab, n.d.-a). Keep the inherited four wall loops.
   Give each separately imported tooth its own modifier. Configure the modifier
   before cloning a tooth so copies inherit it. A modifier is scoped to its
   parent object, including its parts; separate objects keep their own settings.

6. Click Slice plate. In Preview, use the layer slider to inspect the crown,
   neck and harpoon. The crown should contain sparse infill; the harpoon and
   neck should be filled solid. Check supports beneath the suspended barbs.
   Review estimated filament use and print time before printing.

7. Save the project as a .3mf to retain the modifier, orientation and settings.

Keep some crown infill to support the closing shell. A completely empty crown
requires those layers to bridge across the cavity. The proposed 10% crown infill
is a starting point; verify the layer preview for your orientation and printer.
10% infill does not mean 10% total material: walls, the solid mounting region,
solid surface layers and supports also consume filament.

References
Bambu Lab. n.d.-a. Bambu Studio: Modifier Menus and Object Settings. Source code.
Accessed October 9, 2026.
https://github.com/bambulab/BambuStudio/tree/master/src/slic3r/GUI

Bambu Lab. n.d.-b. H2D 3D Printing User Manual, 55-58. Accessed October 9, 2026.
https://csm.bblcdn.com/hub/4668d0ca43994ff3bff4b37f1a65c2e7.pdf

EDITING
The Blender project contains all 20 labeled master objects. Labels, lights and
camera are in a separate preview collection. Export one selected master if
working from Blender. The standalone STL files already contain just that tooth.

To generate other size sets: open the Scripting workspace, select Rebuild teeth.py
in the Text Editor, edit CROWN_HEIGHTS_MM, and run the script. Canine height,
width and thickness are controlled by CANINE_HEIGHT_FACTOR, CANINE_WIDTH_FACTOR
and CANINE_DEPTH_FACTOR. Edit STEM_LENGTH,
STEM_DIAMETER or BARB_DIAMETER to deliberately change the shared mounting system.
The script replaces the scene and writes the same folder layout; when opened
from project/, it uses that folder's parent as the output root. Copy the entire
output folder before making a separate variant. Source is embedded in the .blend.

The ivory material is a preview color. Grooves, worn edges and cusps are actual
geometry. Closed-surface checks, triangle-intersection checks, positive volume,
exact crown height and matching mount hashes are recorded in project/sized-mesh-validation.json.
Independent STL reimport results are in project/sized-stl-verification.json.
'''
text=bpy.data.texts.get('READ ME') or bpy.data.texts.new('READ ME')
text.clear(); text.write(readme)
text=bpy.data.texts.get('Rebuild teeth.py') or bpy.data.texts.new('Rebuild teeth.py')
text.clear(); text.write(SOURCE_TEXT)
(OUTPUT/'README.txt').write_text(readme)
(PROJECT/'sized-mesh-validation.json').write_text(json.dumps(report,indent=2))
active(teeth[6])
for area in bpy.context.screen.areas:
    if area.type=='VIEW_3D':
        area.spaces.active.region_3d.view_perspective='CAMERA'
        area.spaces.active.shading.type='MATERIAL'
bpy.ops.wm.save_as_mainfile(filepath=str(PROJECT/'pumpkin-teeth-sized.blend'))
bpy.ops.render.render(write_still=True)
print('FINISHED',str(OUTPUT),flush=True)
