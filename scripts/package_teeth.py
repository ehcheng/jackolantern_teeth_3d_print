# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Eric Cheng | http://echeng.com
from pathlib import Path
import json
import zipfile

root=Path(__file__).resolve().parents[1]
zips=root/'zips'
zips.mkdir(exist_ok=True)
readme=(root/'README.txt').read_bytes()
report=json.loads((root/'project/sized-stl-verification.json').read_text())
assert len(report)==21 and all(v['reimport_verified'] for v in report.values())
expected_stls={root/name for name in report if name.startswith('sizes/')}
assert len(expected_stls)==20
assert set((root/'sizes').rglob('*.stl'))==expected_stls
for size in [20,25,30,35,40]:
    assert {p.name for p in expected_stls if p.parent.name==f'{size}mm'}=={
        f'{kind}-{size}mm.stl' for kind in ['canine','incisor','premolar','molar']}
assets=['project/pumpkin-teeth-sized.blend','project/mount-fit-test-20mm.stl',
    'project/sized-mesh-validation.json','project/sized-stl-verification.json',
    'README.txt','README.md','LICENSE','README-FOR-CHATGPT.md','teeth-sizes-preview.png']
if (root/'canine-20mm-set-comparison.png').is_file():
    assets.append('canine-20mm-set-comparison.png')
files=[root/name for name in assets]+sorted(expected_stls)
package=zips/'pumpkin-teeth-20-40mm.zip'
partial=package.with_suffix('.partial.zip')
with zipfile.ZipFile(partial,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
    for path in files:
        archive.write(path,'pumpkin-teeth-20-40mm/'+str(path.relative_to(root)))
with zipfile.ZipFile(partial) as archive:
    assert archive.testzip() is None
    assert archive.read('pumpkin-teeth-20-40mm/README.txt')==readme
    for path in files:
        assert archive.read('pumpkin-teeth-20-40mm/'+str(path.relative_to(root)))==path.read_bytes()
partial.replace(package)
for size in [20,25,30,35,40]:
    package=zips/f'pumpkin-teeth-{size}mm-STLs.zip'
    partial=package.with_suffix('.partial.zip')
    with zipfile.ZipFile(partial,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
        for path in sorted((root/'sizes'/f'{size}mm').glob('*.stl')): archive.write(path,path.name)
        archive.write(root/'project/mount-fit-test-20mm.stl','mount-fit-test-20mm.stl')
        archive.write(root/'README.txt','README.txt')
        archive.write(root/'LICENSE','LICENSE')
    with zipfile.ZipFile(partial) as archive:
        assert archive.testzip() is None
        assert archive.read('README.txt')==readme
        assert archive.read('LICENSE')==(root/'LICENSE').read_bytes()
        for path in sorted((root/'sizes'/f'{size}mm').glob('*.stl')):
            assert archive.read(path.name)==path.read_bytes()
        assert archive.read('mount-fit-test-20mm.stl')==(root/'project/mount-fit-test-20mm.stl').read_bytes()
    partial.replace(package)
backup=root/'project/pumpkin-teeth-sized.blend1'
if backup.exists(): backup.unlink()
print('All six current packages rebuilt and verified',flush=True)
