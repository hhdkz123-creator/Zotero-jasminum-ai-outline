var Zotero;
function install(){}function uninstall(){}function shutdown(){}function startup(){void run();}
async function run(){
 const root=TASK_ROOT, file=root+'/verification/native.json';let original;
 const report=await IOUtils.readJSON(file).catch(()=>({stage:'starting',checks:[],errors:[]}));
 const save=()=>IOUtils.writeJSON(file,report);
 const check=(name,pass,detail)=>{report.checks.push({name,pass:!!pass,detail});if(!pass)throw Error(name);};
 const wait=async(name,fn,ms=180000)=>{const start=Date.now();while(Date.now()-start<ms){if(await fn())return;await Zotero.Promise.delay(150);}throw Error('Timed out: '+name);};
 try{
  Zotero=ChromeUtils.importESModule('chrome://zotero/content/zotero.mjs').Zotero;
  await Zotero.uiReadyPromise;await Zotero.Libraries.get(Zotero.Libraries.userLibraryID).waitForDataLoad('item');
  await wait('plugin',()=>Zotero.Jasminum?.data.alive&&Zotero.Reader._registeredListeners.some(l=>l.pluginID==='jasminum@linxzh.com'&&l.type==='renderToolbar'));
  const {AddonManager}=ChromeUtils.importESModule('resource://gre/modules/AddonManager.sys.mjs');
  check('v1.1.45.2 active',(await AddonManager.getAddonByID('jasminum@linxzh.com'))?.version==='1.1.45.2');
  Zotero.Prefs.set('extensions.jasminum.autoRecognizeOutline',false,true);
  const rows=[['第一章 理论基础',1,1],['第一节 研究方法',2,2],['一、核心概念',3,3],['第二章 历史分析',1,130],['第一节 材料分析',2,131],['一、史料说明',3,132],['第三章 结论',1,280]];
  let calls=0,images=0;
  original=Zotero.HTTP.request;
  Zotero.HTTP.request=function(method,url,options){
   if(method!=='POST'||url!=='http://127.0.0.1:61236/v1/chat/completions')return original.call(this,method,url,options);
   const body=JSON.parse(options.body);const user=body.messages.find(m=>m.role==='user').content;const prompt=user.find(p=>p.type==='text').text;
   const pages=prompt.match(/physical PDF pages ([0-9, ]+)\./)[1].split(',').map(Number);calls++;images+=pages.length;
   const enhanced=body.messages[0].content.includes('pageLabel: the Arabic');
   const response={pages:pages.map(p=>({page:p,headings:p===3?[]:rows.filter(r=>r[2]+14===p).map(r=>({title:r[0],level:r[1],left:.075,top:.125})),...(enhanced?{pageLabel:p>=15?String(p-14):null,contents:p===3?{starts:true,continues:false,entries:rows.map(r=>({title:r[0],level:r[1],pageLabel:String(r[2])}))}:null}:{})}))};
   return Promise.resolve({responseText:JSON.stringify({choices:[{message:{content:JSON.stringify(response)}}],usage:{prompt_tokens:100,completion_tokens:10,total_tokens:110}})});
  };
  const open=async item=>{let reader=await Zotero.Reader.open(item.id);if(!reader){await wait('restored reader',()=>Zotero.Reader._readers.some(r=>r.itemID===item.id));reader=Zotero.Reader._readers.find(r=>r.itemID===item.id);}await reader._initPromise;await wait('toolbar',()=>reader._iframeWindow.document.getElementById('j-outline-ai'));reader._iframeWindow.alert=message=>{report.uiError=message;void save();};return {reader,doc:reader._iframeWindow.document,button:reader._iframeWindow.document.getElementById('j-outline-ai')};};
  const task=item=>Zotero.Jasminum.taskRunner.getTaskById('outline-'+item.id);
  const click=async ui=>{ui.button.click();await wait('click complete',()=>!ui.button.disabled);};
  const native=async ui=>{await wait('reloadPDF',()=>ui.reader._internalReader?._primaryView?._iframeWindow?.PDFViewerApplication?.pdfDocument);return ui.reader._internalReader._primaryView._iframeWindow.PDFViewerApplication.pdfDocument;};
  if(report.stage==='complete'&&!report.finalQA){
   const ui=await open(Zotero.Items.get(report.scannedID));
   const title=Array.from(ui.doc.querySelectorAll('#root-list .node-title')).find(n=>n.textContent.replace(/\s/g,'')==='第二章历史分析');title.click();
   await wait('real title navigation',()=>ui.reader._internalReader._primaryView._iframeWindow.PDFViewerApplication.pdfViewer.currentPageNumber===144);
   check('clicking real sidebar title navigates to physical page 144',true);
   const pane=Zotero.PreferencePanes.pluginPanes.find(p=>p.pluginID==='jasminum@linxzh.com');const prefwin=Zotero.Utilities.Internal.openPreferences(pane.id);await wait('preference controls',()=>prefwin.document.getElementById('jasminum-outline-mode'));
   const mode=prefwin.document.getElementById('jasminum-outline-mode');mode.value='smart';mode.dispatchEvent(new prefwin.Event('command',{bubbles:true}));
   await wait('mode write',()=>Zotero.Prefs.get('extensions.jasminum.outlineRecognitionMode',true)==='smart',10000);
   const limit=prefwin.document.getElementById('jasminum-outline-limit');limit.value='7';limit.dispatchEvent(new prefwin.Event('change',{bubbles:true}));
   await wait('limit write',()=>Zotero.Prefs.get('extensions.jasminum.outlineRequestLimit',true)===7,10000);
   check('settings controls really persist mode and numeric quota',true);prefwin.close();report.finalQA=true;report.pendingPrefsRestart=true;await save();Zotero.HTTP.request=original;Zotero.Utilities.Internal.quit();return;
  }
  if(report.pendingPrefsRestart){
   check('recognition settings survive restart',Zotero.Prefs.get('extensions.jasminum.outlineRecognitionMode',true)==='smart'&&Zotero.Prefs.get('extensions.jasminum.outlineRequestLimit',true)===7);
   report.pendingPrefsRestart=false;report.restartVerified=true;await save();Zotero.HTTP.request=original;Zotero.Utilities.Internal.quit();return;
  }
  if(!report.phase1){
   report.stage='local-297';await save();Zotero.Prefs.set('extensions.jasminum.outlineRecognitionMode','smart',true);
   const local=await Zotero.Attachments.importFromFile({file:root+'/native/book-297.pdf'});const ui=await open(local);await click(ui);
   report.local={calls,images,status:ui.doc.querySelector('.j-outline-ai-progress').textContent};await save();
   check('local 297 real toolbar saves without AI',calls===0&&report.local.status.startsWith('已保存'),report.local);
   const pdf=await native(ui);const outline=await pdf.getOutline();check('real PDF three hierarchy levels',outline.length===3&&outline[0].items[0].items[0].title.replace(/\s/g,'')==='一、核心概念');
   const dest=outline[1].dest;check('second chapter physical destination 144',(await pdf.getPageIndex(dest[0]))===143);
   const json=await IOUtils.readJSON(PathUtils.join(Zotero.DataDirectory.dir,'storage',local.key,'jasminum-outline.json'));check('sidecar and PDF both saved',json.outline[1].page===144);
   check('backup retained', (await IOUtils.getChildren(PathUtils.join(PathUtils.parent(await local.getFilePathAsync()),'jasminum-ai-backups'))).some(p=>p.endsWith('.pdf')));
   const prior=await Zotero.Utilities.Internal.md5Async(await local.getFilePathAsync());await click(ui);check('repeat protects existing outline',calls===0&&prior===await Zotero.Utilities.Internal.md5Async(await local.getFilePathAsync())&&ui.doc.querySelector('.j-outline-ai-progress').textContent==='已保留现有大纲');
   report.stage='scanned-quota';await save();Zotero.Prefs.set('extensions.jasminum.outlineRequestLimit',2,true);
   const scanned=await Zotero.Attachments.importFromFile({file:root+'/native/scanned-297.pdf'});report.scannedID=scanned.id;const scanUI=await open(scanned);await click(scanUI);
   check('real scan pauses at 2 requests',calls===2&&task(scanned).status==='paused'&&task(scanned).quotaPaused,{calls,images});
   report.scannedKey=scanned.key;report.phase1=true;report.stage='restart-required';await save();Zotero.HTTP.request=original;Zotero.Utilities.Internal.quit();return;
  }
  report.stage='restart-cache';await save();Zotero.Prefs.set('extensions.jasminum.outlineRecognitionMode','smart',true);Zotero.Prefs.set('extensions.jasminum.outlineRequestLimit',2,true);
  const scanned=Zotero.Items.get(report.scannedID), ui=await open(scanned);await click(ui);
  check('restart restores cache and cumulative limit without request',calls===0&&task(scanned).quotaPaused&&task(scanned).usage.requests===2);
  for(let i=0;i<4&&task(scanned)?.canResume;i++)await click(ui);
  check('explicit quota continue reaches automatic save',ui.doc.querySelector('.j-outline-ai-progress').textContent.startsWith('已保存'),{calls,images,status:ui.doc.querySelector('.j-outline-ai-progress').textContent});
  const pdf=await native(ui);const outline=await pdf.getOutline();check('scan hierarchy and links saved',outline.length===3&&(await pdf.getPageIndex(outline[2].dest[0]))===293);
  const usage=await IOUtils.readJSON(PathUtils.join(Zotero.DataDirectory.dir,'storage',scanned.key,'jasminum-ai-usage.json'));check('real counters persisted including actual tokens',usage.requests===calls+2&&usage.imagePages===images+8&&usage.tokens.total_tokens===usage.requests*110,usage);report.scannedUsage=usage;
  report.stage='full-mode';await save();Zotero.Prefs.set('extensions.jasminum.outlineRecognitionMode','full',true);Zotero.Prefs.set('extensions.jasminum.outlineRequestLimit',100,true);const before=calls;
  const full=await Zotero.Attachments.importFromFile({file:root+'/native/full-17.pdf'});const fullUI=await open(full);await click(fullUI);
  check('full mode real UI processes 17 pages in 4 requests and saves',calls-before===4&&fullUI.doc.querySelector('.j-outline-ai-progress').textContent.startsWith('已保存'));
  const fullPDF=await native(fullUI);const fullOutline=await fullPDF.getOutline();check('full mode PDF actually has nested destinations',fullOutline?.[0]?.items?.[0]?.items?.[0]?.title.replace(/\s/g,'')==='一、核心概念');
  const pause=fullUI.doc.getElementById('j-outline-ai-pause');check('buttons restored and pause hidden',!fullUI.button.disabled&&!fullUI.button.classList.contains('j-outline-ai-busy')&&pause.hidden);
  const pane=Zotero.PreferencePanes.pluginPanes.find(p=>p.pluginID==='jasminum@linxzh.com');const prefwin=Zotero.Utilities.Internal.openPreferences(pane.id);await wait('mode preference',()=>prefwin.document.getElementById('jasminum-outline-mode'));
  check('settings UI reflects current mode',prefwin.document.getElementById('jasminum-outline-mode').value==='full');prefwin.close();
  report.stage='complete';await save();Zotero.HTTP.request=original;Zotero.Utilities.Internal.quit();
 }catch(error){if(original)Zotero.HTTP.request=original;report.stage='failed';report.errors.push({message:String(error),stack:error.stack});await save();Zotero.Utilities.Internal.quit();}
}
