Pumpkin teeth | 20-40 mm size sets | millimeter geometry

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
