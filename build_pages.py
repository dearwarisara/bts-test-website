import json,re,hashlib,html
from pathlib import Path
from urllib.parse import urlsplit,unquote,urljoin
from bs4 import BeautifulSoup
from inner_design import split_pages,layout_kind,chapter_art,decorate
ROOT=Path(__file__).parent;DIST=ROOT/'dist';CACHE=ROOT/'.cache-bts'
data=json.loads((CACHE/'pages-extended.json').read_text(encoding='utf8'))
pages={p['path']:p for p in data['pages']}
for p in pages.values():
 if p.get('status')=='error':
  p['status']='source-link'
  for f in CACHE.glob('*__home.html'):
   source=BeautifulSoup(f.read_text(encoding='utf8'),'html.parser')
   a=source.find('a',href=lambda h:bool(h and urljoin('https://www.btsgroup.co.th',h)==p['source']))
   if a:p['title']=a.get_text(' ',strip=True);break
navigation=json.loads((ROOT/'navigation-tree.json').read_text(encoding='utf8'))['navigation']
en_navigation={n['key']:n for n in navigation['en']}
groups=[(n['key'],n['label'],en_navigation[n['key']]['label']) for n in navigation['th'] if n['key']!='home']
aliases={'our-purpose':'about/our-ambition','subsidiaries-associates':'about/subsidiaries-and-associated','investor-relations':'investor-relations/home','financial-information':'investor-relations/financial-information/key-financial-data','newsroom':'corporate-communications/news-event','sustainability':'sustainability/at-a-glance','about-us':'about/our-ambition','contact-us':'contact'}
def group(path):
 if '/management-structure/' in path or re.search('/awards$',path):return 'about'
 if '/update/' in path:return 'corporate-communications'
 if '/download/' in path:return 'sustainability' if 'sustainability' in path else 'corporate-governance'
 if '/document/viewer/' in path:return 'investor-relations'
 return path.split('/')[2] if len(path.split('/'))>2 else 'about'
def route(path):
 lang=path.split('/')[1];ident=re.search(r'/(\d+)(?:/|$)',path)
 if '/document/viewer/' in path:return f'/{lang}/library/{ident.group(1) if ident else "record"}-{hashlib.sha1(path.encode()).hexdigest()[:6]}/'
 if len(path)>140 or '/management-structure/' in path and ident or '/update/' in path and ident:return f'/{lang}/detail/{hashlib.sha1(path.encode()).hexdigest()[:12]}/'
 return path.rstrip('/')+'/'
def title(p):
 labels={'key-financial-data':('ข้อมูลสำคัญทางการเงิน','Key Financial Data'),'key-financial-ratios':('อัตราส่วนทางการเงิน','Key Financial Ratios'),'debt-information':('ข้อมูลหนี้สิน','Debt Information'),'credit-rating':('อันดับความน่าเชื่อถือ','Credit Rating'),'corporate-information':('ข้อมูลบริษัท','Corporate Information'),'shareholder-structure':('โครงสร้างผู้ถือหุ้น','Shareholder Structure'),'dividend-information':('ข้อมูลเงินปันผล','Dividend Information'),'debentures-information':('ข้อมูลหุ้นกู้','Debentures Information'),'contact-our-registrar':('ติดต่อนายทะเบียนหลักทรัพย์','Contact Our Registrar'),'ir-contact':('ติดต่อนักลงทุนสัมพันธ์','IR Contact'),'news-subscription':('สมัครรับข่าวสาร','News Subscription'),'bts-w8':('ใบสำคัญแสดงสิทธิ BTS-W8','BTS-W8 Warrants')}
 leaf=p['path'].split('/')[-1]
 if p['path'] in ['/th/about','/en/about']:return 'เกี่ยวกับบีทีเอสกรุ๊ป' if p['path'].startswith('/th/') else 'About BTS Group'
 if leaf in labels:return labels[leaf][p['path'].startswith('/en/')]
 return html.unescape(p.get('index',{}).get('title') or p.get('title') or unquote(leaf).replace('-',' '))
def text(value):return BeautifulSoup(html.unescape(value or ''),'html.parser').get_text(' ',strip=True)
def href(url,lang='th'):
 if url.startswith('#'):return url
 u=urlsplit(urljoin('https://www.btsgroup.co.th',url));path=u.path.rstrip('/')
 if u.netloc not in ('www.btsgroup.co.th','btsgroup.co.th'):return url
 if path in pages:return route(path)+('?' + u.query if u.query else '')+('#'+u.fragment if u.fragment else '')
 tail=path[4:] if re.match('^/(th|en)/',path) else path.strip('/')
 if tail in aliases:return f'/{lang}/{aliases[tail]}/'
 return url
def resolve_navigation(nodes):
 for node in nodes:
  if node.get('path'):node['href']=route(node['path'])
  resolve_navigation(node.get('children',[]))
for nodes in navigation.values():resolve_navigation(nodes)

def first_link(node):
 return node.get('href') or next((first_link(child) for child in node.get('children',[]) if first_link(child)),None)

def navigation_links(nodes,current=''):
 rows=[]
 for node in nodes:
  label=html.escape(node['label']);children=node.get('children',[])
  if node.get('href'):
   head='<a '+('aria-current="page" ' if node.get('path')==current else '')+'href="'+html.escape(node['href'],quote=True)+'"><span>'+label+'</span><span aria-hidden="true">↗</span></a>'
  else:head='<span class="nav-branch-label">'+label+'</span>'
  rows.append('<li>'+head+(navigation_links(children,current) if children else '')+'</li>')
 return '<ul class="nav-tree">'+''.join(rows)+'</ul>'

def sitemap_content(lang):
 return '<nav class="sitemap-tree" aria-label="'+('แผนผังเว็บไซต์' if lang=='th' else 'Sitemap')+'">'+''.join('<section><h2>'+('<a href="'+n['href']+'">'+html.escape(n['label'])+' ↗</a>' if n.get('href') else html.escape(n['label']))+'</h2>'+navigation_links(n.get('children',[]))+'</section>' for n in navigation[lang])+'</nav>'

def header(lang):
 th=lang=='th';search='ค้นหา' if th else 'Search';menu='เมนู' if th else 'Menu'
 links=''.join(f'<button class="site-nav-link" data-menu-group="{key}">{thai if th else en}<span>⌄</span></button>' for key,thai,en in groups[:5])
 return f'''<header class="site-header"><a class="site-brand" href="/{lang}/home/" aria-label="BTS Group"><img src="/assets/bts-logo.svg" alt="BTS Group" width="63" height="76" /></a><nav class="site-nav" aria-label="{'เมนูหลัก' if th else 'Main navigation'}">{links}</nav><div class="site-utilities"><a class="site-lang" id="language-switch" href="/{'en' if th else 'th'}/home/">{'EN' if th else 'TH'}</a><button class="site-search-button" data-search-open aria-label="{search}">⌕</button><button class="site-menu-toggle" aria-controls="site-menu" aria-expanded="false">{menu}<span>☰</span></button></div></header><div class="site-menu" id="site-menu" hidden><div class="menu-top"><span>BTS GROUP · EXPLORE</span><button data-menu-close aria-label="{'ปิดเมนู' if th else 'Close menu'}">×</button></div><div class="menu-groups"></div></div><div class="search-overlay" id="site-search" hidden><div class="search-shell"><button data-search-close aria-label="Close">×</button><label for="global-search">{'ค้นพบทุกเรื่องราวของ BTS Group' if th else 'Explore BTS Group'}</label><input id="global-search" type="search" placeholder="{'ค้นหาหน้า ข่าว หรือเอกสาร' if th else 'Search pages, news and documents'}" autocomplete="off"/><div id="global-results" aria-live="polite"></div></div></div>'''
def footer(lang):
 th=lang=='th';nodes=[n for n in navigation[lang] if n['key']!='home']
 def links(items):return ''.join('<a href="'+first_link(n)+'">'+html.escape(n['label'])+' ↗</a>' for n in items)
 return f'''<footer class="footer full-site-footer"><div class="footer-outro"><div><span class="footer-kicker">BTS GROUP · BORDERLESS TRANSFORM SOLUTIONS</span><h2>{'เชื่อมเมือง<br/><em>เชื่อมทุกโอกาส</em>' if th else 'Connected cities.<br/><em>Endless opportunities.</em>'}</h2></div><a class="footer-contact" href="/{lang}/contact/">{'ติดต่อบีทีเอสกรุ๊ป' if th else 'Contact BTS Group'} <span aria-hidden="true">↗</span></a></div><div class="footer-main"><a class="brand brand-foot" href="/{lang}/home/" aria-label="BTS Group home"><img class="bts-logo" src="/assets/bts-logo.svg" alt="BTS Group"/></a><div class="footer-tag">BORDERLESS<br/>TRANSFORM<br/><em>SOLUTIONS.</em><span>{'เชื่อมเมือง. เชื่อมชีวิต.' if th else 'Connect cities. Connect lives.'}</span></div><div class="footer-links"><span>{'สำรวจ BTS Group' if th else 'Explore BTS Group'}</span>{links(nodes[:4])}</div><div class="footer-links"><span>{'เชื่อมต่อกับเรา' if th else 'Stay Connected'}</span>{links(nodes[4:])}<a href="/{lang}/sitemap/">{'แผนผังเว็บไซต์' if th else 'Sitemap'} ↗</a></div></div><div class="footer-bottom"><span>© 2026 BTS Group Holdings PCL · {'แนวคิดการออกแบบเว็บไซต์' if th else 'Website design concept'}</span><a href="/{lang}/privacy-statement/">{'นโยบายความเป็นส่วนตัว' if th else 'Privacy Statement'}</a><a href="/{lang}/cookies-policy/">{'นโยบายคุกกี้' if th else 'Cookies Policy'}</a><a href="/{lang}/terms-and-conditions/">{'ข้อตกลงและเงื่อนไข' if th else 'Terms & Conditions'}</a></div></footer>'''

split_count=split_pages(pages,route)
catalog=[]
for path,p in pages.items():
 if p.get('status')=='error':continue
 description=text(p.get('index',{}).get('description',''))
 catalog.append({'path':path,'href':route(path),'lang':path.split('/')[1],'title':title(p),'group':group(path),'description':description[:700],'image':p.get('image') or p.get('banner',''),'document':'/document/viewer/' in path,'primary':path in {x['path'] for x in data['pages'][:data['seed_count']]}})
by_path={p['path']:p for p in catalog}
for p in catalog:
 p['navigable']=p['primary'] or (not p['document'] and not re.search(r'/\d+(?:/|$)',p['path']) and p['group'] in {g[0] for g in groups})
def cards(items,kind=''):
 return '<div class="page-card-grid '+kind+'">'+''.join(f'''<a class="page-card" href="{html.escape(p['href'],quote=True)}">{('<div class="page-card-image"><img loading="lazy" src="'+html.escape(p['image'],quote=True)+'" alt=""/></div>') if p.get('image') and 'opengraph' not in p['image'] else ''}<span class="page-card-kicker">{'DOCUMENT' if p['document'] else p['group'].replace('-',' ').upper()}</span><h3>{html.escape(p['title'])}</h3><p>{html.escape(p['description'][:180])}</p><span class="page-card-arrow">↗</span></a>''' for p in items)+'</div>'
def resources(p):
 path=p['path'];lang=path.split('/')[1];suffix=path.split('/')[-1];g=group(path)
 candidates=[x for x in catalog if x['lang']==lang and x['path']!=path]
 if suffix=='board-of-directors' or path.endswith('/management-structure/director'):
  candidates=[x for x in candidates if '/management-structure/director/board-of-directors/' in x['path']]
 elif suffix=='management-team' or path.endswith('/management-structure/management'):
  candidates=[x for x in candidates if '/management-structure/management/' in x['path']]
 elif 'news' in suffix or 'projects-activities' in path:
  candidates=[x for x in candidates if '/update/news-event/' in x['path'] or '/newsroom/' in x['path']]
 elif any(s in suffix for s in ['publication','report','documents','charters','policy','conduct','anti-corruption','webcast','fact-sheet']):
  candidates=[x for x in candidates if x['document']]
  keys={'annual-report':['annual-report','yearly-report'],'sustainability-report':['sustainability-report'],'webcasts':['webcast','opportunity-day','presentation'],'fact-sheet':['fact-sheet'],'charters-and-definition-of-independent-directors':['charter'],'corporate-governance-policy-and-code-of-business-conduct':['cg-policy','governance','conduct'],'anti-corruption':['corruption']}
  if suffix in keys:
   matched=[x for x in candidates if any(k in x['path'].lower() for k in keys[suffix])]
   if matched:candidates=matched
 elif path.endswith('/about'):candidates=[x for x in candidates if x['group']=='about' and x['primary']]
 else:candidates=[x for x in candidates if x['group']==g and (x['primary'] or x['document'])]
 return candidates
def content(p):
 path=p['path'];lang=path.split('/')[1];th=lang=='th';raw=p.get('html','');plain=text(raw)
 if '/document/viewer/' in path:
  d=text(p.get('index',{}).get('description',''))
  return f'<div class="document-view"><span class="document-symbol">↗</span><h2>{html.escape(title(p))}</h2><p>{html.escape(d)}</p><a class="official-action" href="{html.escape(p["source"],quote=True)}" target="_blank" rel="noreferrer">{("เปิดเอกสารต้นฉบับ" if th else "Open original document")} ↗</a><p class="source-note">{("เอกสารเผยแพร่โดย BTS Group" if th else "Published by BTS Group")}</p></div>'
 if path.endswith('/sitemap'):return sitemap_content(lang)
 if path.endswith('/corporate-vdo'):
  return '<div class="corporate-video"><video src="https://www.btsgroup.co.th/storage/bilboard/video-banner.mp4" controls playsinline preload="none" aria-label="BTS Group Corporate Video"></video><a class="official-action" href="https://www.youtube.com/watch?v=R4d-wIxII7I" target="_blank" rel="noreferrer">'+('ชมวิดีโอฉบับเต็ม' if th else 'Watch the full corporate video')+' ↗</a></div>'
 if path.endswith('/advance-search'):return '<div class="page-search"><label for="page-query">'+('ค้นหาภายในเว็บไซต์' if th else 'Search the website')+'</label><input type="search" id="page-query" placeholder="'+('ค้นหาหน้า ข่าว หรือเอกสาร' if th else 'Search pages, news or documents')+'"/><div class="archive-results" aria-live="polite"></div></div>'
 # Resolve obsolete empty routes to the corresponding current public pages.
 alt={'board-of-directors':'management-structure/director','management-team':'management-structure/management','awards':'awards','news-event':'update/news-event','corporate-documents':'download/corporate-documents','charters-and-definition-of-independent-directors':'download/charters','corporate-governance-policy-and-code-of-business-conduct':'download/corporate-governance-policy-and-code-of-business-conduct','sustainability-report':'download/sustainability-report','company-secretary':'download/company-secretary','internal-audit-office':'download/internal-audit-office','anti-corruption':'download/anti-corruption','risk-management':'download/risk-management','corporate-social-responsibilities':'download/corporate-social-responsibilities','investor-relations-code-of-conduct':'download/investor-relations-code-of-conduct'}
 if len(plain)<15:
  key=path.split('/')[-1];other=pages.get(f'/{lang}/'+alt.get(key,'---'))
  if other and len(text(other.get('html','')))>30:raw=other['html'];plain=text(raw)
 if len(plain)<15:
  description=text(p.get('index',{}).get('description',''))
  if description and description!=title(p):
   paragraphs=[x.strip() for x in re.split(r'\s{2,}',description) if x.strip()]
   raw='<div class="indexed-content">'+''.join('<p>'+html.escape(x)+'</p>' for x in paragraphs)+'</div>'
   plain=text(raw)
   return raw
  items=resources(p)
  if items:return (raw if len(plain)>15 else '')+'<div class="resource-archive" data-archive-path="'+html.escape(path,quote=True)+'"><div class="archive-controls"><input type="search" placeholder="'+('ค้นหาในหมวดนี้' if th else 'Search this section')+'" aria-label="Search this section"/><span class="archive-count"></span></div><div class="archive-results">'+cards(items[:12])+'</div><button class="archive-more">'+('ดูเพิ่มเติม' if th else 'Show more')+' ↓</button></div>'
  return '<div class="section-intro"><h2>'+html.escape(title(p))+'</h2><a class="official-action" href="'+html.escape(p['source'],quote=True)+'" target="_blank" rel="noreferrer">'+('ดูรายละเอียดจาก BTS Group' if th else 'View details from BTS Group')+' ↗</a></div>'
 body=BeautifulSoup(raw,'html.parser')
 for a in body.select('a[href]'):
  original=a['href'];a['href']=href(original,lang)
  if a['href'].startswith('http'):a['target']='_blank';a['rel']='noreferrer'
 for e in body.select('[data-toggle="tab"]'):e['role']='tab'
 for video in body.select('video'):video['controls']='';video.attrs.pop('autoplay',None)
 # Tables get their own horizontal scroller rather than breaking the layout.
 for table in list(body.select('table')):
  wrap=body.new_tag('div');wrap['class']='table-scroll';table.wrap(wrap)
 return str(body)
def section_name(path,lang):
 for key,thai,en in groups:
  if key==group(path):return thai if lang=='th' else en
 return 'BTS GROUP'
def make_page(p):
 path=p['path'];lang=path.split('/')[1];th=lang=='th';name=title(p);g=group(path)
 siblings=[x for x in catalog if x['lang']==lang and x['group']==g and x['navigable'] and x['path'] not in ('/th/home','/en/home')]
 siblings=list({x['title']:x for x in siblings}.values())
 section=next((n for n in navigation[lang] if n['key']==g),None)
 side=navigation_links(section.get('children') or [section],path) if section else ''
 image=p.get('banner') or p.get('image','');use_image=image and 'opengraph' not in image
 hero_image=chapter_art(layout_kind(p),p,image)
 related=[x for x in siblings if x['path']!=path][:3]
 kind,body=decorate(p,content(p))
 if p.get('parent_path'):
  body='<a class="chapter-back" href="'+route(p['parent_path'])+'">← '+('กลับไปหน้ารวม' if th else 'Back to overview')+'</a>'+body
 return f'''<!doctype html><html lang="{lang}"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/><title>{html.escape(name)} | BTS Group</title><meta name="description" content="{html.escape(text(p.get('index',{}).get('description',''))[:150] or name,quote=True)}"/><link rel="stylesheet" href="/styles.css"/><link rel="stylesheet" href="/redesign.css"/><link rel="stylesheet" href="/pages.css"/><link rel="stylesheet" href="/chapters.css"/><link rel="stylesheet" href="/navigation.css?v=sitemap-1"/><link rel="stylesheet" href="/footer.css?v=2"/><link rel="stylesheet" href="/craft.css?v=1"/>{'<link rel="stylesheet" href="/history-world.css?v=spacing-1"/>' if kind=='journey' else ''}</head><body class="inner-page layout-{kind}" data-path="{html.escape(path,quote=True)}">{header(lang)}<main><section class="page-hero"><div class="page-hero-copy"><a class="page-breadcrumb" href="/{lang}/home/">{'หน้าหลัก' if th else 'Home'} / {section_name(path,lang)}</a><span class="page-eyebrow">{g.replace('-',' ').upper()}</span><h1>{html.escape(name)}</h1><a class="page-scroll" href="#page-content">{'สำรวจเนื้อหา' if th else 'Explore this page'} <span>↓</span></a></div>{hero_image}</section><div class="chapter-navigation"><span>{section_name(path,lang)}</span><details class="chapter-picker"><summary>{'เลือกหน้าในหมวดนี้' if th else 'Explore this chapter'} <span>⌄</span></summary><nav>{side}</nav></details></div><div class="page-layout" id="page-content"><article class="source-body" data-category="{g}">{body}<div class="source-attribution"><a href="{html.escape(p['source'],quote=True)}" target="_blank" rel="noreferrer">{'ข้อมูลต้นฉบับจาก BTS Group' if th else 'Original information from BTS Group'} ↗</a></div></article></div>{('<section class="related-pages"><span class="section-kicker">EXPLORE MORE</span>'+cards(related)+'</section>') if related else ''}</main>{footer(lang)}<script src="/navigation.js?v=sitemap-1" type="module"></script><script src="/chapter-motion.js" type="module"></script></body></html>'''
out=[]
for path,p in pages.items():
 if path not in by_path or path in ('/th/home','/en/home'):continue
 target=DIST/route(path).strip('/')/'index.html';target.parent.mkdir(parents=True,exist_ok=True);target.write_text(make_page(p),encoding='utf8');out.append({'source':path,'route':route(path),'status':p.get('status'),'characters':len(text(p.get('html',''))),'document':'/document/viewer/' in path})
# Shared catalogue powers every menu, search and archive view.
for p in pages.values():
 if p['path'] in by_path and '/document/viewer/' not in p['path'] and len(text(p.get('html','')))<15 and not re.search(r'/\d+/',p['path']):by_path[p['path']]['resources']=[x['path'] for x in resources(p)]
(DIST/'site-catalog.json').write_text(json.dumps({'groups':[{'key':a,'th':b,'en':c} for a,b,c in groups],'pages':catalog,'navigation':navigation},ensure_ascii=False),encoding='utf8')
# Keep the authored home experience; apply the complete shared navigation.
home=(DIST/'index.html').read_text(encoding='utf8')
home=re.sub(r'<header class="header">.*?</header>',lambda m:header('th'),home,flags=re.S)
home=re.sub(r'<header class="site-header">.*?(?=<main)',lambda m:header('th')+'\n\n',home,flags=re.S) if '<header class="site-header">' in home and '<header class="header">' not in home else home
home=re.sub(r'<footer class="footer[^>]*>.*?</footer>',lambda m:footer('th'),home,flags=re.S)
home=home.replace('href="./styles.css"','href="/styles.css"').replace('href="./redesign.css"','href="/redesign.css"').replace('src="./assets/','src="/assets/').replace('src="./app.js"','src="/app.js"').replace('src="./scene.js"','src="/scene.js"').replace('src="./motion.js"','src="/motion.js"')
if '/pages.css' not in home:home=home.replace('</head>','<link rel="stylesheet" href="/pages.css"/></head>')
if '/ecosystem.css' not in home:home=home.replace('</head>','<link rel="stylesheet" href="/ecosystem.css?v=1"/></head>')
if '/footer.css' not in home:home=home.replace('</head>','<link rel="stylesheet" href="/footer.css?v=2"/></head>')
if '/craft.css' not in home:home=home.replace('</head>','<link rel="stylesheet" href="/craft.css?v=1"/></head>')
if '/navigation.js' not in home:home=home.replace('</body>','<script type="module" src="/navigation.js"></script></body>')
bs=BeautifulSoup(home,'html.parser')
for card,src,alt in zip(bs.select('.business-card'),['https://www.btsgroup.co.th/storage/banner/banner-move.jpg','https://www.btsgroup.co.th/storage/banner/banner-mix.jpg','https://www.btsgroup.co.th/storage/banner/banner-match.jpg'],['BTS rail line across Bangkok','BTS MIX media screens across the city','Bangkok business district connected by BTS Group']):
 graphic=card.select_one('.card-graphic')
 if graphic:
  graphic.clear();image=bs.new_tag('img',src=src,alt=alt,loading='lazy',decoding='async');graphic.append(image);graphic['data-art-direction']='official-photo'
for script in bs.select('script[src]'):
 if urlsplit(script['src']).path=='/navigation.js':script['src']='/navigation.js?v=sitemap-1'
nav_style=next((n for n in bs.select('link[href]') if urlsplit(n['href']).path=='/navigation.css'),None)
if not nav_style:
 nav_style=bs.new_tag('link',rel='stylesheet');bs.head.append(nav_style)
nav_style['href']='/navigation.css?v=sitemap-1' 
for a in bs.select('a[href]'):a['href']=href(a['href'])
home=str(bs);(DIST/'index.html').write_text(home,encoding='utf8')
for lang in ['th','en']:
 h=home
 if lang=='en':
  h=h.replace('lang="th"','lang="en"');h=re.sub(r'<header class="site-header">.*?(?=<main)',lambda m:header('en'),h,flags=re.S);h=re.sub(r'<footer class="footer[^>]*>.*?</footer>',lambda m:footer('en'),h,flags=re.S)
  translations={'เชื่อมเมือง.':'Connect cities.','เชื่อมชีวิต.':'Connect lives.','เปิดทุก':'Open every','ความเป็นไปได้.':'possibility.','ทุกเส้นทางเชื่อมผู้คนเข้าหากัน':'Every journey brings people together','และทุกการเดินทางพาเราไปสู่โอกาสใหม่':'and connects us with new possibilities.','รู้จัก BTS Group':'Discover BTS Group','สำรวจธุรกิจของเรา':'Explore our businesses','มากกว่าเส้นทาง':'Beyond the journey','คือทุกโอกาสของชีวิต.':'A world of possibilities.','จากการเดินทางในแต่ละวัน สู่เมืองที่เชื่อมถึงกัน':'From everyday journeys to a more connected city.','เราเชื่อว่า':'We believe','เมืองที่ดีเริ่มต้นจาก':'better cities begin with','การเชื่อมต่อที่ดี':'better connections','เชื่อมโยง':'Connect','เปลี่ยนผ่าน':'Transform','เติบโตไปด้วยกัน':'Grow together','หนึ่งระบบนิเวศ':'One ecosystem.','หลายโอกาสเติบโต':'Endless possibilities.','การเดินทาง':'Mobility','ประสบการณ์และสื่อ':'Media & experiences','โอกาสและการเติบโต':'Growth & opportunities','ข้อมูลสำคัญ':'Key information','สำหรับนักลงทุน':'for investors','เรื่องราวที่กำลัง':'Stories that','ขับเคลื่อนเรา':'move us forward','ข่าวบริษัท':'Corporate news','ข่าวตลาดหลักทรัพย์':'SET announcements','ดูข่าวทั้งหมด':'All updates','เติบโตอย่างรับผิดชอบ':'Growing responsibly','ไปพร้อมกับสังคม':'Moving forward together','สำรวจความยั่งยืน':'Explore sustainability','ไตรมาส 1 ปี 2569/70 · หน่วย: ล้านบาท':'1Q 2026/27 · THB million','รายได้รวม':'Reported revenue','ล้านบาท':'THB million','กำไร (ขาดทุน) สุทธิส่วนที่เป็นของผู้ถือหุ้น':'Net profit (loss) attributable to shareholders','อ่านจุดมุ่งหมายของเรา':'Explore our ambition'}
  for a,b in translations.items():h=h.replace(a,b)
  extra={'BTS Group | เชื่อมต่อทุกโอกาส':'BTS Group | Connecting Possibilities','บริษัท บีทีเอส กรุ๊ป โฮลดิ้งส์ จำกัด (มหาชน)':'BTS Group Holdings Public Company Limited','นักลงทุนสัมพันธ์':'Investor Relations','กำลังเข้าสถานี':'Arriving at the station','↙ ภาพรวม':'↙ Overview','ลากหมุนได้ 360° · ใช้สองนิ้วเพื่อซูม':'Drag to rotate 360° · Pinch to zoom','▶ เล่นวิดีโอ':'▶ Play video','เปิดเสียง ↗':'Sound on ↗','ชมวิดีโอเต็ม ↗':'Watch full film ↗','ชมวิดีโอจาก':'Watch on','BTS Group บน YouTube ↗':'BTS Group YouTube ↗','BTS Group Holdings มุ่งพัฒนาโซลูชันที่เชื่อมต่อMobility ธุรกิจ และผู้คนเข้าด้วยกัน ด้วยแนวคิด':'BTS Group Holdings develops solutions that connect mobility, businesses and people through','สร้างการเข้าถึงที่ทำให้เมืองเดินหน้า':'Building access that keeps cities moving.','มองหาแนวทางใหม่ที่ตอบโจทย์อนาคต':'Exploring new solutions for tomorrow.','ส่งต่อคุณค่าร่วมให้ผู้คนและสังคม':'Creating shared value for people and society.','สำรวจบริษัทในกลุ่มและโซลูชันที่ร่วมเชื่อมต่อเมือง':'Explore the companies and solutions connecting our city','ในมิติต่าง ๆ ของชีวิตประจำวัน':'across everyday life.','เชื่อมต่อผู้คนกับจุดหมายทั่วเมือง':'Connecting people with destinations across the city.','สร้างการสื่อสารที่เชื่อมแบรนด์กับผู้คน':'Bringing brands and people closer together.','ต่อยอดความร่วมมือสู่คุณค่าระยะยาว':'Building partnerships for long-term value.','ภาพรวมธุรกิจในหน้านี้เป็นแนวทางนำเสนอเบื้องต้น ดูรายชื่อบริษัทย่อยและบริษัทร่วมฉบับทางการ':'Explore the official list of subsidiaries and associated companies','ที่นี่ ↗':'here ↗','ติดตามผลการดำเนินงานและข้อมูลล่าสุดของ BTS Group':'Explore BTS Group performance and investor information.','ไปยังInvestor Relations':'Explore Investor Relations','Key informationทางการเงิน':'Financial highlights','ดูข้อมูลการเงิน':'Financial information','และเอกสารเผยแพร่':'and publications','ข้อมูลตามหน้าเว็บไซต์ BTS Group ที่ตรวจสอบ ณ วันที่ 12 พฤศจิกายน 2569 · โปรดดูเอกสารทางการสำหรับข้อมูลล่าสุด':'Snapshot from the BTS Group website on 12 November 2026. See official publications for the latest information.','ความยั่งยืนคือส่วนหนึ่งของการสร้างคุณค่าระยะยาว':'Sustainability is part of creating long-term value','ให้กับธุรกิจ ผู้คน และสิ่งแวดล้อม':'for business, people and the environment.','บีทีเอส กรุ๊ปฯ ร่วมงานคอนเสิร์ตการกุศลรอบพิเศษ “มูลนิธิพลังน้ำใจไทย Power of Thai Foundation รวมน้ำใจปีที่ 16”':'BTS Group joins the Power of Thai Foundation charity concert.','กลุ่มบริษัทบีทีเอสลงพื้นที่ชุมชนเขตหนองจอก ส่งมอบกำลังใจและถุงยังชีพแก่ผู้ประสบอุทกภัย':'BTS Group delivers relief supplies to flood-affected communities in Nong Chok.','กำหนดวันซื้อขายวันสุดท้ายของ BTS-W8':'Last trading day of BTS-W8','แจ้งการห้ามซื้อขายและการพ้นสภาพจากการเป็นหลักทรัพย์จดทะเบียนของ BTS-W8':'Trading suspension and termination of listing status of BTS-W8'}
  for a,b in extra.items():h=h.replace(a,b)
  h=h.replace('/th/','/en/');h=h.replace('<head>','<head><style>.hero h1{font:400 clamp(55px,6.3vw,94px)/1 Mulish;letter-spacing:-.065em}.hero h1 span:nth-child(4){font-size:.9em}.hero h1 span:nth-child(2){padding-left:5%}@media(max-width:650px){.hero h1{font-size:clamp(44px,11vw,70px)}}</style>')
 target=DIST/lang/'home'/'index.html';target.parent.mkdir(parents=True,exist_ok=True);target.write_text(h,encoding='utf8')
# The reports expose source availability without presenting guessed content as fact.
report={'main_pages':data['seed_count'],'designed_routes':len(out)+2,'separated_topics':split_count,'documents':sum(x['document'] for x in out),'source_empty':[x['source'] for x in out if not x['document'] and x['characters']<15],'routes':out}
(ROOT/'site-build-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in report.items() if k!='routes' and k!='source_empty'},ensure_ascii=True))
