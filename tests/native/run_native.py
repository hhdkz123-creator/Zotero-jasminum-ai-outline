#!/usr/bin/env python3
"""macOS-only native smoke tests. Uses an isolated profile and synthetic PDFs."""
import argparse,json,subprocess,sys,zipfile
from pathlib import Path
parser=argparse.ArgumentParser()
parser.add_argument('--xpi',type=Path,required=True)
parser.add_argument('--zotero',type=Path,default=Path('/Applications/Zotero.app/Contents/MacOS/zotero'))
args=parser.parse_args()
root=Path(__file__).resolve().parents[2]
profile=root/'native/profile';data=root/'native/data';reports=root/'verification'
for d in [profile/'extensions',data,reports]:d.mkdir(parents=True,exist_ok=True)
if (reports/'native.json').exists():raise SystemExit('Existing native report found: preserve/archive native/ and verification/ before starting a new isolated run.')
for script,out in [('create_fixture.py','book-297.pdf'),('create_scanned.py',None)]:
    cmd=[sys.executable,str(Path(__file__).with_name(script))]
    if out:cmd.append(str(root/'native'/out))
    subprocess.run(cmd,cwd=root,check=True)
(profile/'extensions/jasminum@linxzh.com.xpi').write_bytes(args.xpi.resolve().read_bytes())
prefs={'extensions.autoDisableScopes':0,'extensions.startupScanScopes':15,'extensions.zotero.firstRun.skipFirefoxProfileAccessCheck':True,'extensions.zotero.firstRunGuidance':False,'extensions.zotero.firstRun2':False,'extensions.zotero.sync.autoSync':False,'extensions.zotero.dataDir':str(data),'extensions.zotero.useDataDir':True,'extensions.zotero.httpServer.enabled':False,'extensions.zoteroMacWordIntegration.skipInstallation':True,'extensions.zoteroWinWordIntegration.skipInstallation':True,'extensions.zoteroOpenOfficeIntegration.skipInstallation':True,'intl.locale.requested':'zh-CN','extensions.update.enabled':False,'extensions.jasminum.firstRun':False,'extensions.jasminum.autoRecognizeOutline':False,'extensions.jasminum.llmBaseURL':'http://127.0.0.1:61236/v1','extensions.jasminum.llmApiKey':'fixture-only','extensions.jasminum.llmModel':'fixture-only'}
(profile/'user.js').write_text('\n'.join(f'user_pref({json.dumps(k)}, {json.dumps(v)});' for k,v in prefs.items())+'\n')
manifest={'manifest_version':2,'name':'Isolated smart outline verification','version':'1.0.0','applications':{'zotero':{'id':'smart-outline-test@local','strict_min_version':'9.0','strict_max_version':'11.*','update_url':'https://example.invalid/smart-outline-test.json'}}}
with zipfile.ZipFile(profile/'extensions/smart-outline-test@local.xpi','w') as z:
    z.writestr('manifest.json',json.dumps(manifest))
    z.writestr('bootstrap.js',Path(__file__).with_name('bootstrap.js').read_text().replace('TASK_ROOT',json.dumps(str(root))))
for phase in range(4):
    with (reports/f'native-run-{phase+1}.log').open('w') as log:
        subprocess.run([str(args.zotero),'-no-remote','-profile',str(profile)],stdout=log,stderr=subprocess.STDOUT,cwd=root,timeout=600,check=True)
    report=json.loads((reports/'native.json').read_text())
    if report.get('stage')=='failed':raise SystemExit(str(report.get('errors')))
    if report.get('restartVerified'):break
else:raise SystemExit('Native checks did not reach restartVerified')
print('Native PDF/toolbar/save/cache/settings checks passed; report:',reports/'native.json')
