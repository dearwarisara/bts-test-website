"""Apply one BTS shell and local navigation to every generated page."""
from pathlib import Path
from urllib.parse import urlsplit, unquote
from bs4 import BeautifulSoup
import json, subprocess, sys, html, re
R=Path(__file__).parent; D=R/'dist'
CAT=json.loads((D/'site-catalog.json').read_text(encoding='utf-8'))
def key(s):return unquote(urlsplit(s).path).rstrip('/')
BY={key(p['path']):p for p in CAT['pages']}
ROUTES={key(p['href']):p for p in CAT['pages']}
def local(url,lang='th'):
 if not url or url.startswith(('#','mailto:','tel:','javascript:')):return url
 u=urlsplit(url)
 if u.netloc and u.netloc not in ('www.btsgroup.co.th','btsgroup.co.th'):return url
 k=key(url)
 aliases={'/sustainability/message-from-the-chairman':'/sustainability/sustainability-at-bts-group','/update/other-activities':'/update/news-event','/about/at-a-glance':'/about/our-ambition','/our-business/at-a-glance':'/our-business/business-overview'}
 for old,new in aliases.items():
  if k in ('/th'+old,'/en'+old):k=k[:3]+new;break
 if re.match(r'^/(th|en)/update/news-event/\d+$',k) and k not in BY:
  match=next((p for p in CAT['pages'] if p['path'].startswith(k+'/')),None)
  k=key(match['path']) if match else k[:3]+'/update/news-event'
 if '/document/viewer/flipbook/' in k:
  m=re.search(r'/flipbook/(\d+)/',k)
  match=next((p for p in CAT['pages'] if m and p['lang']==lang and '/document/viewer/'+m[1]+'/' in p['path']),None)
  if match:k=key(match['path'])
 if k in BY:out=BY[k]['href']
 elif k in ROUTES:out=ROUTES[k]['href']
 elif k in ('','/'):out=f'/{lang}/home/'
 else:return url
 return out+('?' + u.query if u.query else '')+('#'+u.fragment if u.fragment else '')
def first(n):return n.get('href') or next((first(c) for c in n.get('children',[]) if first(c)),None)
def esc(s):return html.escape(str(s),quote=True)
def tree_links(nodes):
 return '<ul>'+''.join('<li>'+('<a href="'+esc(n['href'])+'">'+esc(n['label'])+' <span>↗</span></a>' if n.get('href') else '<strong>'+esc(n['label'])+'</strong>')+(tree_links(n['children']) if n.get('children') else '')+'</li>' for n in nodes)+'</ul>'
def header(lang,path):
 nodes=CAT['navigation'][lang]; p=BY.get(key(path)) or ROUTES.get(key(path)); other='en' if lang=='th' else 'th'
 alternate=BY.get(key(re.sub(r'^/(th|en)/','/'+other+'/',p['path'] if p else path)))
 alt=alternate['href'] if alternate else f'/{other}/home/'
 nav=[]; panels=[]
 for n in nodes:
  current=bool(p and (p['group']==n['key'] or p['path']==n.get('path')))
  if n.get('children'):
   nav.append(f'<button data-menu="{n["key"]}" aria-expanded="false" aria-controls="mega-{n["key"]}"'+(' class="current-section"' if current else '')+'>'+esc(n['label'])+'</button>')
   panels.append(f'<section class="mega-panel" id="mega-{n["key"]}" hidden><div><small>BTS GROUP</small><h2>{esc(n["label"])}</h2><a class="outline-button" href="{first(n)}">'+('ดูข้อมูลในหมวดนี้' if lang=='th' else 'Explore this section')+' <span>↗</span></a></div><div class="mega-links official-tree">'+tree_links(n['children'])+'</div></section>')
  else:nav.append(f'<a class="nav-direct'+(' current-section' if current else '')+'" href="'+esc(n['href'])+'">'+esc(n['label'])+'</a>')
 return f'<header class="site-header"><div class="header-top"><a class="logo" href="/{lang}/home/" aria-label="BTS Group"><img src="/assets/bts-logo.svg" alt="BTS Group"/></a><div class="header-tools"><span class="language"><b>{lang.upper()}</b> | <a href="{alt}">{other.upper()}</a></span><button class="search-open" aria-label="'+('ค้นหา' if lang=='th' else 'Search')+'">⌕</button><button class="menu-toggle" aria-label="'+('เปิดเมนู' if lang=='th' else 'Open menu')+'" aria-expanded="false">☰</button></div></div><nav class="main-nav" aria-label="'+('เมนูหลัก' if lang=='th' else 'Main navigation')+'">'+''.join(nav)+'</nav><div class="mega-shell">'+''.join(panels)+'</div></header>'
def footer(lang):
 nodes=[n for n in CAT['navigation'][lang] if n['key']!='home']; th=lang=='th'
 def links(ns):return ''.join(f'<a class="more" href="{first(n)}">{esc(n["label"])}<span>↗</span></a>' for n in ns)
 return f'<footer class="bts-footer"><div class="container footer-grid"><div class="footer-company"><a href="/{lang}/home/"><img src="/assets/bts-logo.svg" alt="BTS Group"/></a><h3>'+('บริษัท บีทีเอส กรุ๊ป โฮลดิ้งส์<br>จำกัด (มหาชน)' if th else 'BTS Group Holdings<br>Public Company Limited')+'</h3><p>Borderless Transform Solutions</p></div><div><h3>BTS Group</h3>'+links(nodes[:4])+'</div><div><h3>'+('ติดต่อและข้อมูลเพิ่มเติม' if th else 'Connect with BTS Group')+'</h3>'+links(nodes[4:])+f'<a class="more" href="/{lang}/sitemap/">'+('แผนผังเว็บไซต์' if th else 'Sitemap')+' <span>↗</span></a><button class="back-top" aria-label="'+('กลับด้านบน' if th else 'Back to top')+'">↑</button></div></div><div class="footer-bottom container"><span>© 2026 BTS Group Holdings Public Company Limited</span><div>'+f'<a href="/{lang}/privacy-statement/">'+('นโยบายความเป็นส่วนตัว' if th else 'Privacy Statement')+f'</a><a href="/{lang}/cookies-policy/">'+('นโยบายคุกกี้' if th else 'Cookies Policy')+'</a></div></div></footer>'
def dialog(lang):
 th=lang=='th'
 return '<dialog id="search-dialog"><div class="search-dialog-head"><img src="/assets/bts-logo.svg" alt="BTS Group"><button class="search-close" aria-label="'+('ปิดการค้นหา' if th else 'Close search')+'">×</button></div><form class="search-form"><label for="search-input">'+('ค้นพบทุกเรื่องราวของ BTS Group' if th else 'Explore BTS Group')+'</label><div><input id="search-input" type="search" placeholder="'+('ค้นหาข้อมูล ข่าวสาร หรือเอกสาร' if th else 'Search pages, news and documents')+'" autocomplete="off"><button type="submit">'+('ค้นหา' if th else 'Search')+'</button></div></form><div id="search-results" aria-live="polite"><p>'+('พิมพ์อย่างน้อย 2 ตัวอักษรเพื่อค้นหา' if th else 'Enter at least 2 characters to search')+'</p></div></dialog>'
def fragment(s):return BeautifulSoup(s,'html.parser')
def set_text(node,text):
 if node:node.clear();node.append(text)
# Regenerate the homepage source, then retain only BTS source headings and data.
subprocess.run([sys.executable,str(R/'build_metro_home.py')],check=True)
home=BeautifulSoup((D/'index.html').read_text(encoding='utf-8'),'html.parser')
for sel in ('.purpose-strip','.careers'):
 for n in home.select(sel):n.decompose()
about=home.select_one('section.about')
metrics=about.select_one('.metrics').extract()
metrics.select('.metric')[-1].decompose()
financial=fragment('<section class="financial-home container" id="financial"><span class="section-tag">นักลงทุนสัมพันธ์</span><h2 class="section-title">ข้อมูลสำคัญทางการเงิน</h2><p class="financial-period">ข้อมูลสำคัญทางการเงินประจำไตรมาส 1 ปี 2569/70 · หน่วย: ล้านบาท</p></section>').section
financial.append(metrics);financial.append(fragment('<div class="finance-actions"><a class="outline-button" href="/th/investor-relations/financial-information/key-financial-data/">ข้อมูลทางการเงิน <span>↗</span></a><a class="outline-button" href="/th/investor-relations/home/">นักลงทุนสัมพันธ์ <span>↗</span></a></div>'))
about.decompose()
news=home.select_one('section.news');set_text(news.select_one('h2'),'ข่าวล่าสุด');set_text(news.select_one('.news-heading .outline-button'),'ข่าวสารองค์กร ↗')
filters=fragment('<div class="news-filters" role="group" aria-label="หมวดข่าว"><button class="active" data-news-filter="company" aria-pressed="true">ข่าวของบริษัท</button><button data-news-filter="market" aria-pressed="false">ข่าวแจ้งตลาดหลักทรัพย์</button></div>')
news.select_one('.news-heading').insert_after(filters)
for i,card in enumerate(news.select('.news-card')):card['data-news-kind']='company' if i<2 else 'market'
news.select_one('.news-carousel')['data-filtered']='company'
# The two SET announcements link to their own local document pages.
for card,ident in zip(news.select('.news-card')[2:],('204615','204522')):
 p=next(p for p in CAT['pages'] if p['lang']=='th' and '/document/viewer/'+ident+'/' in p['path'])
 card['href']=p['href']
business=home.select_one('#business');set_text(business.select_one('.section-tag'),'BTS Group');set_text(business.select_one('h2'),'ธุรกิจของเรา');set_text(business.select_one('.business-intro>p'),'กลุ่มบริษัทบีทีเอสดำเนินธุรกิจระบบขนส่งมวลชน สื่อโฆษณา อสังหาริมทรัพย์ และบริการ')
resources=home.select_one('#investor');resources['id']='publications';set_text(resources.select_one('.section-tag'),'เอกสารเผยแพร่');set_text(resources.select_one('h2'),'เอกสารเผยแพร่');resources.select_one('.section-heading .section-tag').decompose()
quick=[('MD&A','คำอธิบายและวิเคราะห์ของฝ่ายจัดการ','/th/investor-relations/document/mdna/'),('งบการเงิน','งบการเงิน','/th/investor-relations/document/financial-statements/'),('เอกสารนำเสนอบริษัท','เอกสารนำเสนอบริษัท','/th/investor-relations/document/investor-presentation/'),('เว็บแคสต์และเอกสารนำเสนอ','เว็บแคสต์และเอกสารนำเสนอ','/th/investor-relations/document/webcasts/')]
for card,(title,desc,url) in zip(resources.select('.quick-card'),quick):
 set_text(card.h3,title);set_text(card.select_one(':scope > span:not(.glass-icon)'),desc);card['href']=url
ribbon=resources.select_one('.quarter-ribbon');set_text(ribbon.select_one(':scope>span'),'ข้อมูลทางการเงิน')
annual=resources.select_one('.annual-card');annual.select_one('a')['href']='/th/investor-relations/document/yearly-reports/';reports=fragment('<div class="bts-reports"></div>').div
reports.append(annual.extract())
sr=fragment('<article class="annual-card sustainability-report"><img loading="lazy" src="https://www.btsgroup.co.th/storage/download/sustainability/sr/sd-report202526-th.jpg" alt="รายงานความยั่งยืน 2568/69"><h3>รายงานความยั่งยืน ประจำปี 2568/69</h3><div><a href="/th/download/sustainability-report/" aria-label="รายงานความยั่งยืน">↗</a><a href="https://www.btsgroup.co.th/storage/download/sustainability/sr/sd-report202526-th.pdf" aria-label="ดาวน์โหลดรายงานความยั่งยืน" data-official-download="true">↓</a></div></article>').article
reports.append(sr);resources.select_one('.ir-layout').insert_after(reports)
resources.select_one('.ir-layout')['class']=['ir-layout','bts-resource-layout']
sustain=home.select_one('#sustainability');set_text(sustain.select_one('.center-heading>span'),'กลุ่มบริษัทบีทีเอสกับความยั่งยืน');set_text(sustain.select_one('h2'),'ความยั่งยืน')
for b,t in zip(sustain.select('[data-esg]'),('ความยั่งยืนด้านสิ่งแวดล้อม','ความยั่งยืนด้านสังคม','การกำกับดูแลกิจการ')):set_text(b.select_one(':scope>span'),t)
main=home.main
for n in (news,resources,business,sustain):n.extract()
hero=main.select_one('.hero').extract();main.clear();main.append(hero)
main.append(fragment('<nav class="home-shortcuts container" aria-label="ข้อมูล BTS Group"><a href="#news"><b>01</b>ข่าวล่าสุด <span>↓</span></a><a href="#financial"><b>02</b>นักลงทุนสัมพันธ์ <span>↓</span></a><a href="#publications"><b>03</b>เอกสารเผยแพร่ <span>↓</span></a></nav>'))
for n in (news,financial,resources,business,sustain):main.append(n)
(D/'index.html').write_text(str(home),encoding='utf-8');(D/'th/home/index.html').write_text(str(home),encoding='utf-8')
# English home uses the same structure and data; section terminology follows BTS.
en=BeautifulSoup(str(home),'html.parser');en.html['lang']='en'
translations={'ข่าวล่าสุด':'Latest News','ข่าวสารองค์กร ↗':'Corporate News ↗','ข่าวของบริษัท':'Company News','ข่าวแจ้งตลาดหลักทรัพย์':'SET Announcements','นักลงทุนสัมพันธ์':'Investor Relations','ข้อมูลสำคัญทางการเงิน':'Key Financial Data','ข้อมูลสำคัญทางการเงินประจำไตรมาส 1 ปี 2569/70 · หน่วย: ล้านบาท':'Financial Highlights 1Q 2026/27 · Unit: THB million','รายได้รวม (ล้านบาท)':'Total Revenue (THB million)','EBITDA (ล้านบาท)':'EBITDA (THB million)','กำไร (ขาดทุน) สุทธิส่วนที่เป็นของผู้ถือหุ้น (ล้านบาท)':'Net Profit (Loss) Attributable to Equity Holders (THB million)','ข้อมูลทางการเงิน':'Financial Information','เอกสารเผยแพร่':'Publications','งบการเงิน':'Financial Statements','คำอธิบายและวิเคราะห์ของฝ่ายจัดการ':'Management Discussion and Analysis','เอกสารนำเสนอบริษัท':'Company Presentations','เว็บแคสต์และเอกสารนำเสนอ':'Webcasts and Presentations','ธุรกิจของเรา':'Our Business','กลุ่มธุรกิจบีทีเอส':'BTS Group Businesses','กลุ่มบริษัทบีทีเอสดำเนินธุรกิจระบบขนส่งมวลชน สื่อโฆษณา อสังหาริมทรัพย์ และบริการ':'BTS Group operates businesses in Mass Transit, Media, Property and Services.','ความยั่งยืน':'Sustainability','กลุ่มบริษัทบีทีเอสกับความยั่งยืน':'Sustainability at BTS Group','ความยั่งยืนด้านสิ่งแวดล้อม':'Environmental Sustainability','ความยั่งยืนด้านสังคม':'Social Sustainability','การกำกับดูแลกิจการ':'Corporate Governance','ระบบขนส่งมวลชน':'Mass Transit','สื่อโฆษณา':'Media','อสังหาริมทรัพย์':'Property','บริการ':'Services','อ่านเพิ่มเติม ':'Read More ','อ่านเพิ่มเติม':'Read More','รายงานประจำปี 2568/69':'Annual Report 2025/26','รายงานความยั่งยืน ประจำปี 2568/69':'Sustainability Report 2025/26','ดูผลการดำเนินงาน →':'View Financial Results →','ติดต่อนักลงทุนสัมพันธ์':'IR Contact','ทุกการเชื่อมต่อ คือจุดเริ่มต้นของความเป็นไปได้':'Every connection opens new possibilities.','BTS GROUP · เชื่อมเมือง เชื่อมทุกโอกาส':'BTS GROUP · CONNECTING CITIES AND OPPORTUNITIES','ชมวิดีโอเต็ม ↗':'View Full Video ↗','เลื่อนเพื่อออกเดินทาง':'Scroll to Explore','11 พฤศจิกายน 2569':'11 November 2026','09 พฤศจิกายน 2569':'9 November 2026','22 ตุลาคม 2569':'22 October 2026','19 ตุลาคม 2569':'19 October 2026','ติดตามผลการดำเนินงาน เอกสารเผยแพร่ และข้อมูลสำหรับนักลงทุนจาก BTS Group':'Financial performance, publications and investor information from BTS Group.','เรามุ่งสร้างคุณค่าระยะยาว ด้วยการดำเนินธุรกิจที่รับผิดชอบต่อสิ่งแวดล้อม':'Creating long-term value through environmental responsibility,','สังคม และการกำกับดูแลกิจการที่ดี':'social responsibility and good corporate governance.'}
for txt in list(en.main.find_all(string=True)):
 if str(txt) in translations:txt.replace_with(translations[str(txt)])
for card,ident in zip(en.select('.news-card'),('1205','1204','204615','204522')):
 candidates=[p for p in CAT['pages'] if p['lang']=='en' and ('/news-event/'+ident+'/' in p['path'] or '/document/viewer/'+ident+'/' in p['path'])]
 if candidates:card.h3.string=candidates[0]['title'];card['href']=candidates[0]['href']
for a in en.main.select('a[href]'):
 h=a['href']
 if h.startswith('/th/') and BY.get(key(h)):h=BY[key(h)]['path']
 if h.startswith('/th/'):h=re.sub(r'^/th/','/en/',h)
 elif h.startswith('https://www.btsgroup.co.th/th/'):h=h.replace('/th/','/en/',1)
 if h.startswith('/en/library/') and key(h) not in ROUTES:h='/en/investor-relations/newsroom/set-announcements/'
 a['href']=local(h,'en')
(D/'en/home/index.html').write_text(str(en),encoding='utf-8')
# Existing navigation code also owns archive filters, page search, and source tabs.
original=(D/'navigation.js').read_text(encoding='utf-8')
prefix=original[:original.index('const menu=')].replace("fetch('/site-catalog.json?v=sitemap-1')","fetch(new URL('./site-catalog.json',import.meta.url))")
(D/'content.js').write_text(prefix+original[original.index('function resultCards'):],encoding='utf-8')
changed=0;rewritten=0
for file in D.rglob('*.html'):
 soup=BeautifulSoup(file.read_text(encoding='utf-8'),'html.parser')
 if not soup.body:continue
 lang='en' if soup.html.get('lang')=='en' else 'th'; route='/'+file.parent.relative_to(D).as_posix().strip('./')+'/'
 if file==D/'index.html':route='/th/home/'
 p=ROUTES.get(key(route));path=p['path'] if p else route
 is_home=route in ('/th/home/','/en/home/')
 for n in soup.select('body > header,body > footer,#site-menu,#site-search,#search-dialog'):n.decompose()
 for script in soup.select('script[src]'):
  if urlsplit(script['src']).path in ('/navigation.js','/metro.js','/content.js','/home.js','/scene.js','/motion.js','/app.js','/rail-hero.js'):script.decompose()
 for stylesheet in soup.select('link[rel=stylesheet]'):
  url=stylesheet.get('href','')
  if 'fonts.googleapis' in url or urlsplit(url).path in ('/metro.css','/bts-brand.css','/bts-inner.css','/navigation.css','/footer.css'):stylesheet.decompose()
 classes=[c for c in soup.body.get('class',[]) if c not in ('js-motion','ready')]
 soup.body['class']=list(dict.fromkeys(classes+['bts-unified']+([] if is_home else ['inner-page'])))
 soup.body['data-path']=path
 if not is_home:
  oldhero=soup.select_one('.page-hero,.inner-hero')
  title=oldhero.select_one('h1').get_text(' ',strip=True) if oldhero and oldhero.select_one('h1') else (p['title'] if p else soup.title.get_text())
  image=oldhero.select_one('img') if oldhero else None
  group=next((g[lang] for g in CAT['groups'] if p and g['key']==p['group']), 'BTS Group')
  image_html='<div class="inner-cover"><img src="'+esc(image['src'])+'" alt=""/></div>' if image else ''
  hero_html=f'<section class="inner-hero">{image_html}<div class="container"><div class="inner-breadcrumb"><a href="/{lang}/home/">'+('หน้าหลัก' if lang=='th' else 'Home')+'</a><span>/</span><span>'+esc(group)+'</span></div><span class="inner-station">'+esc(group)+'</span><h1>'+esc(title)+'</h1><a class="inner-content-link" href="#page-content">'+('สำรวจเนื้อหา' if lang=='th' else 'Explore this page')+' <span>↓</span></a></div></section>'
  if oldhero:oldhero.replace_with(fragment(hero_html))
  else:soup.main.insert(0,fragment(hero_html))
  for n in soup.select('.source-attribution'):n.decompose()
  for n in soup.select('.related-pages>.section-kicker'):set_text(n,'ข้อมูลที่เกี่ยวข้อง' if lang=='th' else 'Related Information')
 soup.body.insert(0,fragment(header(lang,path)))
 soup.body.append(fragment(footer(lang)));soup.body.append(fragment(dialog(lang)))
 for href in ('/metro.css?v=3','/bts-brand.css?v=2','/bts-inner.css?v=1'):
  n=soup.new_tag('link',rel='stylesheet',href=href);soup.head.append(n)
 for src in ('/metro.js?v=3',)+(() if is_home else ('/content.js?v=1',)):
  n=soup.new_tag('script',src=src,type='module');soup.body.append(n)
 for asset in soup.select('[src],[poster]'):
  for attr in ('src','poster'):
   if asset.get(attr,'').startswith(('/storage/','/themes/')):asset[attr]='https://www.btsgroup.co.th'+asset[attr]
 for a in soup.select('a[href]'):
  h=a['href']
  if h.startswith(('/storage/','/themes/')):h='https://www.btsgroup.co.th'+h;a['href']=h
  is_download=bool(a.has_attr('data-official-download') or '/storage/' in h or '/viewer/stream/' in h or (a.get('class') and 'official-action' in a['class'] and '/document/viewer/' in h))
  new=h if is_download else local(h,lang)
  if new!=h:rewritten+=1;a['href']=new
  if new.startswith('/'):
   a.attrs.pop('target',None);a.attrs.pop('rel',None)
 file.write_text(str(soup),encoding='utf-8');changed+=1
print(f'Applied BTS shell to {changed} pages; localized {rewritten} links')
