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
