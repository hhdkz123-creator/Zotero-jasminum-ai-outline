#!/usr/bin/env python3
"""Replace scaffold-injected upstream updates; validate the actual installable ZIP."""
import hashlib,json,os,sys,tempfile,zipfile
from pathlib import Path
source=Path(sys.argv[1]);destination=Path(sys.argv[2]);destination.parent.mkdir(parents=True,exist_ok=True)
with tempfile.NamedTemporaryFile(suffix='.xpi',dir=destination.parent,delete=False) as tmp: staging=Path(tmp.name)
try:
    with zipfile.ZipFile(source) as z,zipfile.ZipFile(staging,'w',compression=zipfile.ZIP_DEFLATED) as out:
        assert z.testzip() is None
        assert len(z.namelist())==len(set(z.namelist()))
        for entry in z.infolist():
            data=z.read(entry.filename)
            if entry.filename=='manifest.json':
                manifest=json.loads(data)
                assert manifest['name']=='Zotero-jasminum-ai-outline'
                assert manifest['version']=='1.1.45.5'
                assert manifest['applications']['zotero']['id']=='jasminum@linxzh.com'
                manifest['applications']['zotero']['update_url']='https://raw.githubusercontent.com/hhdkz123-creator/Zotero-jasminum-ai-outline/main/updates-manual.json'
                data=json.dumps(manifest,ensure_ascii=False,indent=2).encode()
            out.writestr(entry,data)
    with zipfile.ZipFile(staging) as z:
        assert z.testzip() is None
        assert json.loads(z.read('manifest.json'))['applications']['zotero']['update_url']=='https://raw.githubusercontent.com/hhdkz123-creator/Zotero-jasminum-ai-outline/main/updates-manual.json'
        script=z.read('chrome/content/scripts/jasminum.js').decode()
        assert 'outlineRecognitionMode' in script and 'jasminum-ai-backups' in script and 'quotaPaused' in script
    os.replace(staging,destination)
    digest=hashlib.sha256(destination.read_bytes()).hexdigest()
    destination.with_suffix('.xpi.sha256').write_text(f'{digest}  {destination.name}\n')
    print(f'Validated {destination.name} ({destination.stat().st_size} bytes), SHA256 {digest}')
finally: staging.unlink(missing_ok=True)
