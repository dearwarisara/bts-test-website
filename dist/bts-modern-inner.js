// Native dialogs keep original document links usable without the old Bootstrap runtime.
document.querySelectorAll('.modern-inner .source-body [data-toggle="modal"]').forEach(trigger=>{
 const selector=trigger.getAttribute('data-target')||trigger.getAttribute('href');
 if(!selector?.startsWith('#'))return;
 const original=document.getElementById(selector.slice(1));
 if(!original)return;
 if(!trigger.hasAttribute('href')){trigger.setAttribute('role','button');trigger.tabIndex=0;}
 trigger.setAttribute('aria-haspopup','dialog');
 function open(event){
  event.preventDefault();const dialog=document.createElement('dialog');dialog.className='modern-dialog';
  const close=document.createElement('button');close.type='button';close.className='modern-dialog-close';close.textContent='×';close.setAttribute('aria-label',document.documentElement.lang==='th'?'ปิด':'Close');
  const content=original.querySelector('.modal-content')||original;const copy=content.cloneNode(true);
  copy.removeAttribute('id');copy.querySelectorAll('[id]').forEach(n=>n.removeAttribute('id'));dialog.append(close,copy);
  const title=copy.querySelector('.modal-title');dialog.setAttribute('aria-label',title?.textContent?.trim()||'Documents');
  close.addEventListener('click',()=>dialog.close());copy.querySelectorAll('[data-dismiss="modal"]').forEach(b=>b.addEventListener('click',()=>dialog.close()));
  dialog.addEventListener('click',e=>{if(e.target===dialog){const r=dialog.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)dialog.close();}});
  dialog.addEventListener('close',()=>{dialog.remove();trigger.focus();},{once:true});document.body.append(dialog);dialog.showModal();
 }
 trigger.addEventListener('click',open);trigger.addEventListener('keydown',e=>{if(e.key===' '||e.key==='Enter'&&!trigger.hasAttribute('href'))open(e)});
});
// Visual review mode eagerly loads photographs before full-page capture.
if(new URLSearchParams(location.search).has('visual_review')){document.documentElement.classList.add('visual-review');document.documentElement.style.setProperty('--review-height',innerHeight+'px');document.querySelectorAll('img').forEach(img=>{img.loading='eager';img.decoding='sync'});}
// Restore the annual / quarterly views without the original select plugin.
document.querySelectorAll('.modern-inner .block-select__content').forEach(group=>{
 const panels=[...group.children].filter(n=>n.classList.contains('select-content'));
 if(panels.length<2||!panels.every(n=>['yearly','quarter'].includes(n.id)))return;
 const th=document.documentElement.lang!=='en',tabs=document.createElement('div');tabs.className='financial-view-tabs';tabs.setAttribute('role','group');tabs.setAttribute('aria-label',th?'ช่วงเวลาข้อมูลการเงิน':'Financial reporting period');
 panels.forEach((panel,index)=>{const button=document.createElement('button');button.type='button';button.textContent=panel.id==='yearly'?(th?'ข้อมูลประจำปี':'Full Year Highlights'):(th?'ข้อมูลรายไตรมาส':'Quarterly Highlights');button.setAttribute('aria-controls',panel.id);button.setAttribute('aria-pressed',String(index===0));panel.hidden=index!==0;button.addEventListener('click',()=>{panels.forEach(p=>p.hidden=p!==panel);tabs.querySelectorAll('button').forEach(b=>b.setAttribute('aria-pressed',String(b===button)));window.dispatchEvent(new Event('resize'))});tabs.append(button)});group.before(tabs);
});
