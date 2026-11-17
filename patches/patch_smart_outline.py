#!/usr/bin/env python3
"""Apply the reviewed v1.1.45 customization without replacing the upstream tree."""
import subprocess,sys
from pathlib import Path
root=Path(sys.argv[1]).resolve()
pinned='d3b1b3227b0e46aaf56585c5c09ff9e343152ce4'
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
if head!=pinned:raise SystemExit(f'Expected upstream v1.1.45 commit {pinned}; got {head}. Use a clean pinned checkout.')
patch=Path(__file__).with_name('smart-outline-v1.1.45.patch').resolve()
subprocess.run(['git','apply','--check',str(patch)],cwd=root,check=True)
subprocess.run(['git','apply',str(patch)],cwd=root,check=True)
print('Applied v1.1.45 custom UI + smart outline incremental patch')
