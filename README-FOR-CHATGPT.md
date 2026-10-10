# Pumpkin teeth: handoff for ChatGPT and contributors

Updated October 10, 2026. Designs by [Eric Cheng](http://echeng.com), under the
[MIT license](LICENSE). Read the current user request and applicable `AGENTS.md`
instructions before editing. Inspect the actual files, since users may move them.

## Source and file layout

- `README.txt`: printing instructions, dimensions and Bambu Studio settings.
- `scripts/build_teeth.py`: authoritative procedural source for all designs,
  validation, STL export, preview layout and the printing README.
- `project/pumpkin-teeth-sized.blend`: editable masters, the preview scene and
  embedded text blocks `Rebuild teeth.py` and `READ ME`.
- `sizes/{20,25,30,35,40}mm/`: four individual STL designs per size set.
- `project/mount-fit-test-20mm.stl`: sample of the fixed mounting system.
- `project/sized-mesh-validation.json`: original mesh checks.
- `project/sized-stl-verification.json`: independent STL import checks.
- `teeth-sizes-preview.png`: large-text overview, 1600 × 1800 pixels.
- `scripts/verify_sized_exports.py`: import and verify actual exported meshes.
- `scripts/rebuild_sizes_preview.py`: update preview labels and camera without
  rebuilding or exporting the teeth.
- `scripts/package_teeth.py`: build one complete and five per-size ZIP packages.
  Output goes to the ignored `zips/` folder.

Keep the script and embedded generator synchronized. Direct mesh edits in the
saved scene are overwritten by a procedural rebuild. Save deliberate sculpting
separately and document the new source and export workflow. Maintenance scripts
are included in this repository; the generated complete pack embeds the generator
in its `.blend`, but does not include the `scripts/` folder.

## Design intent and current parameters

These are exaggerated, bulbous, creepy teeth for a jack-o'-lantern. Preserve
rounded mass, worn edges and distinct silhouettes. The four designs are canine,
incisor, two-cusp premolar and broad, blunt molar with uneven worn lobes.
Four copies of each design give four canines and twelve assorted teeth.

```python
CROWN_HEIGHTS_MM = [20, 25, 30, 35, 40]
CANINE_HEIGHT_FACTOR = 1.25
CANINE_WIDTH_FACTOR = 1.25
CANINE_DEPTH_FACTOR = 1.20
STEM_LENGTH = 20.0
STEM_DIAMETER = 5.0
BARB_DIAMETER = 7.5
VOXEL_SIZE = 0.12
```

Folder and STL filename sizes identify the size set. Incisor, premolar and molar
crowns equal that size; canine crowns are 25% taller: 25, 31.25, 37.5, 43.75 and
50 mm. Crown height is measured from local `z=0` to the highest crown point.
The crown points along `+Z` and the mount along `-Z`. Total length is crown height
plus 20 mm.

Eric reduced the smallest canine from 27 mm to 25 mm. Keep that decision unless
asked to change it. The current smallest canine crown is approximately 25 mm tall,
17.28 mm wide and 13.13 mm thick. Width and depth multipliers are additional to
the proportional enlargement from the height factor. Changing only the height
factor therefore scales all three crown dimensions.

Opposite faces have different surface details. Rotate a tooth 180 degrees about
local Z, the insertion axis, for variety. This does not describe teeth at both
ends of the mount.

## Fixed mount constraints

Every size and design has the same 20 mm insertion length, 5 mm shaft, two circular
barbs with 7.5 mm maximum diameter, and 7 mm root collar. The mount extends 2.5 mm
inside the crown to establish a positive overlap for the Boolean union.

Scale the crown independently and then join the fixed mount. Uniform scaling of
the finished STL changes the harpoon fit. Remesh and smooth only the crown;
voxel-remeshing the completed tooth can shrink or round the barbs.

The current lower mount surface has 4,126 triangles. Its signature is:

```text
64bd3cc0e46a48366e67bf31ba4aa14dffb558bf7e873ba149a2b066632a4015
```

`mount_signature()` computes this SHA-256 from sorted, rounded triangle
coordinates at or below `z=0`; it is not a hash of the STL file bytes. Preserve it
across teeth and the fit-test sample unless asked to modify the mounting system.
If changing the mount, update the fit-test sample, measurements, validation
requirements and dimension notes together.

## Where to edit

| Change | Code in `scripts/build_teeth.py` |
| --- | --- |
| Overall crown shape | `DESIGNS` ring profiles: Z, half-width, half-thickness, lateral displacement |
| Grooves, wear, asymmetry and cusps | `crown_deform(kind)` |
| Crown size and canine proportions | Size constants and `make_tooth()` |
| Mount geometry | Mount constants and `make_mount()` |
| Crown processing | `make_crown()` |
| Preview spacing and readable labels | Master display locations, `label()` calls and camera settings |
| Printing README | The `readme` string, which exports `README.txt` |

The generator lofts rings, subdivides, voxel-remeshes the crown, smooths and
simplifies it, normalizes exact crown height and performs an exact Boolean union
with the triangulated mount. Cleanup must preserve the lower mount surface.

Add an explicit deformation branch for a new design; the final `else` currently
implements the molar. Also update expected names and counts in the verifier and
packager, documentation, and preview layout if the inventory changes.

## Rebuild and verification

1. Inspect the current files and user changes. Record hashes of geometry that
   should remain unchanged. Save backups in an ignored `work/` folder, or a Git
   branch. Preserve all user-created `.3mf` files.
2. Edit the source and check its Python syntax. Make only the requested design
   changes. Rebuild into a temporary copy when trying an uncertain change.
3. Run the generator and verify its assertions. Inspect the actual preview.
4. Run the independent STL importer; do not treat source-level checks alone as
   proof of exported artifact integrity.
5. Update the embedded source, README, preview, reports and packages. Review the
   diff and verify that unrelated teeth and the fixed mount were preserved.

In Blender, open the saved project, select `Rebuild teeth.py` in the Scripting
workspace and run it. The script replaces the scene and overwrites generated
files, so save any manual work first. A `.blend` in `project/` uses that folder's
parent as the output root. A background run of the standalone script uses the
repository root derived from `scripts/build_teeth.py`. Copy the repository for a
separate variant, or inspect and deliberately change `OUTPUT`.

From the repository root, on macOS:

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --python scripts/build_teeth.py
/Applications/Blender.app/Contents/MacOS/Blender --background --python scripts/verify_sized_exports.py
python3 scripts/package_teeth.py
```

On another platform, replace the Blender executable path. Run these sequentially
and check each result. Blender 5.2.2 LTS was used for the current models. In the
original Codex environment, background Blender crashed in the restricted sandbox
and worked through the approved execution tool. Use the tool's permission flow
if that happens again. Blender MCP is optional; recheck available tools before
assuming a local MCP endpoint exists.

Require one closed connected component per tooth, consistent normals, positive
volume, no degenerate triangles and no intersections of nonadjacent triangles.
Verify exact crown height, minimum Z of -20 mm, 5 mm shaft and 7.5 mm barbs, matching
lower mount signatures, and no STL triangle crossing the root plane. Reimported
dimensions and volume must match the source manifest.

There are 20 teeth plus one fit-test sample, so the current verifier expects 21
exports and 21 objects in `Teeth | printable masters`. Lights, labels and cameras
belong in `Preview | labels and lights`. STL export uses local geometry;
scene display positions must not enter the exported coordinates. Blender uses
metric units and `scale_length=0.001`; STL coordinates are explicitly millimeters.

The generator checks triangle intersections on the source meshes. The independent
import helper checks connectivity, manifoldness, normals, degeneracy, dimensions,
volume and mount geometry, but does not repeat intersection detection. Repeat
that check after independent mesh edits. Refresh reports after geometry changes.
Geometry checks do not establish insertion force or retention in real pumpkins.

For preview-only changes, use `scripts/rebuild_sizes_preview.py` and verify that
STL and `.3mf` hashes stay unchanged. It currently assumes the four designs and
five sizes. Keep labels readable at normal screen sizes; increasing resolution
alone does not enlarge text on screen.

## Printing projects and packaging

`README.txt` explains lightly filled crowns and solid harpoons in Bambu Studio.
The exported meshes are closed solids; slicer modifiers control their interior
infill. Give separately imported teeth their own modifiers; configure a tooth
before duplicating it so copies inherit its modifier settings.

Included `.3mf` files are Eric's Bambu Studio projects. Preserve their layouts and
settings. Rebuilding STLs does not update meshes already imported into those
projects. Verify their model contents before describing them as the latest
designs. Do not overwrite them during a procedural rebuild.

The packager creates one complete pack and five size packs. It verifies archive
integrity and included file bytes. The complete pack includes the editable
master, reports, STLs, documentation, license and preview. Generated packs exclude
`.3mf` projects and maintenance scripts. The optional old canine close-up PNG is
included only if present. ZIPs are ignored by Git to avoid duplicating the models;
GitHub's Code → Download ZIP provides a repository download with the scripts and
tracked `.3mf` files.

The original unsized builds and early canine backup were removed at Eric's request.
Do not recreate them or select an earlier 27 mm canine as the current source.

Retain Eric Cheng's attribution, http://echeng.com and the MIT license notice.
Report the actual change, refreshed outputs, validation performed and any physical
print limitations relevant to the revision. Show a preview for shape changes.
