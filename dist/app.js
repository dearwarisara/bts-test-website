const menuButton=document.querySelector('.menu-toggle');
const nav=document.querySelector('.nav');
menuButton?.addEventListener('click',()=>{const open=menuButton.getAttribute('aria-expanded')!=='true';menuButton.setAttribute('aria-expanded',String(open));menuButton.setAttribute('aria-label',open?'ปิดเมนู':'เปิดเมนู');nav?.classList.toggle('open',open)});
nav?.querySelectorAll('a').forEach(link=>link.addEventListener('click',()=>{nav.classList.remove('open');menuButton?.setAttribute('aria-expanded','false')}));
document.querySelectorAll('.news-tabs [data-news]').forEach(button=>button.addEventListener('click',()=>{const target=button.dataset.news;document.querySelectorAll('.news-tabs [data-news]').forEach(tab=>{const active=tab===button;tab.classList.toggle('active',active);tab.setAttribute('aria-selected',String(active))});document.querySelectorAll('.news-list[data-panel]').forEach(panel=>panel.classList.toggle('hidden',panel.dataset.panel!==target))}));
