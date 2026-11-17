#!/usr/bin/env python3
"""Run upstream CJS regression suites and the added smart-outline tests."""
import subprocess
import sys
from pathlib import Path
root=Path(sys.argv[1]).resolve()
for test in sorted((root/'test').glob('*.cjs')):
    subprocess.run(['node',str(test.relative_to(root))],cwd=root,check=True)
subprocess.run(['node','--test',*[str(p.relative_to(root)) for p in sorted((root/'test/smart').glob('*.test.cjs'))]],cwd=root,check=True)
