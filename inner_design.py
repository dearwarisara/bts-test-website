"""Content-aware page layouts and a scroll-driven railway history."""
import re,html
from bs4 import BeautifulSoup

def split_pages(pages,route):
 added={}
 for path,p in list(pages.items()):
  if '/document/viewer/' in path or path.endswith('/our-history'):continue
  soup=BeautifulSoup(p.get('html',''),'html.parser');lang=path.split('/')[1];th=lang=='th';leaf=path.split('/')[-1]
  selectors=[];labels=[];slugs=[];section='topics'
  if path.endswith('/management-structure/director'):
   selectors=soup.select('.source-accordion');slugs=['board-of-directors','audit','nomination-remuneration','sustainability','executive','risk-management'];section='committees'
  elif path.endswith('/management-structure/management'):
   selectors=soup.select('.source-accordion');slugs=['executives','company-secretary','internal-audit-director'];section='teams'
  elif leaf=='contact':selectors=soup.select('.source-accordion');slugs=['company-secretary','internal-audit','investor-relations','sustainability'];section='departments'
  elif leaf=='awards' and '/about/' not in path:
   selectors=soup.select('.source-accordion');section='years'
  else:
   panes=soup.select('.tab-pane[id]')
   if len(panes)>1:selectors=panes;section='views'
   elif leaf=='key-financial-data' and soup.select_one('.yearly') and soup.select_one('.quarter'):
    selectors=[soup.select_one('.yearly'),soup.select_one('.quarter')];labels=['ข้อมูลรายปี' if th else 'Annual results','ข้อมูลรายไตรมาส' if th else 'Quarterly results'];slugs=['annual','quarterly'];section='results'
  if len(selectors)<2:continue
  links=[]
  for i,node in enumerate(selectors):
   summary=node.select_one('summary');ident=node.get('id') or str(i+1)
   tab=soup.find('a',href='#'+ident)
   label=labels[i] if i<len(labels) else summary.get_text(' ',strip=True) if summary else tab.get_text(' ',strip=True) if tab else ident.upper()
   slug=slugs[i] if i<len(slugs) else re.sub('[^a-zA-Z0-9-]+','-',ident if ident!=str(i+1) else label).strip('-') or str(i+1)
   childpath=path+'/'+section+'/'+slug
   body=BeautifulSoup(str(node),'html.parser');summary=body.select_one('summary')
   if summary:summary.decompose()
   for nav in body.select('.source-tabs'):nav.decompose()
   container=body.find(['details','div']) or body
   child=dict(p);child.update(path=childpath,html=''.join(str(x) for x in container.contents),title=label,index={'title':label,'description':container.get_text(' ',strip=True)[:900]},source=p['source']+'#'+ident,split_child=True,parent_path=path)
   added[childpath]=child
   links.append(f'<a class="chapter-destination" href="{route(childpath)}"><span class="destination-index">{i+1:02d}</span><h2>{html.escape(label)}</h2><span class="destination-arrow">↗</span></a>')
   node.decompose()
  for nav in soup.select('.source-tabs'):nav.decompose()
  p['html']=str(soup)+'<div class="chapter-destinations">'+''.join(links)+'</div>';p['split_index']=True
 pages.update(added)
 # Retain the original menu URLs while using the new separated directory.
 aliases={'about/board-of-directors':'management-structure/director','about/management-team':'management-structure/management','about/awards':'awards'}
 for lang in ('th','en'):
  for a,b in aliases.items():
   if f'/{lang}/{a}' in pages and f'/{lang}/{b}' in pages:
    pages[f'/{lang}/{a}']['html']=pages[f'/{lang}/{b}']['html'];pages[f'/{lang}/{a}']['split_index']=True
 return len(added)

def layout_kind(p):
 path=p['path'];leaf=path.split('/')[-1]
 if path.endswith('/our-history'):return 'journey'
 if '/document/viewer/' in path:return 'document'
 if '/management-structure/' in path and re.search(r'/\d+/',path) or '/ceo-of-' in path:return 'profile'
 if '/management-structure/' in path or '/board-of-directors' in path or '/management-team' in path:return 'people'
 if '/our-business/' in path:return 'business'
 if '/financial-information/' in path or '/stock-quote/' in path or leaf in ['dividend-information','shareholder-structure','debentures-information','investment-calculator']:return 'finance'
 if '/update/news-event/' in path:return 'article'
 if '/corporate-communications/' in path or '/update/' in path or '/newsroom/' in path:return 'news'
 if '/sustainability/' in path:return 'impact'
 if '/career/' in path:return 'career'
 if '/contact' in path:return 'contact'
 if '/corporate-governance/' in path or '/download/' in path or '/document/' in path or '/resource-center' in path:return 'library'
 if any(k in path for k in ['privacy','cookies','terms-and-conditions']):return 'legal'
 if leaf in ['sitemap','advance-search']:return 'directory'
 return 'story'

def train_svg():
 return '''<svg viewBox="0 0 46 130" aria-hidden="true"><defs><linearGradient id="train-metal" x2="1"><stop stop-color="#b4c3cb"/><stop offset=".5" stop-color="#fff"/><stop offset="1" stop-color="#b4c3cb"/></linearGradient></defs><g fill="#24394a"><rect x="4" y="13" width="38" height="15" rx="3"/><rect x="4" y="54" width="38" height="15" rx="3"/><rect x="4" y="96" width="38" height="15" rx="3"/></g><g fill="url(#train-metal)" stroke="#8195a1"><rect x="8" y="3" width="30" height="38" rx="7"/><rect x="8" y="45" width="30" height="38" rx="7"/><path d="M15 87h16q7 0 7 7v23q0 10-15 11Q8 127 8 117V94q0-7 7-7z"/></g><g fill="#17384e"><rect x="13" y="10" width="20" height="11" rx="3"/><rect x="13" y="52" width="20" height="11" rx="3"/><path d="M13 106h20v9q-10 9-20 0z"/></g><g fill="#df2735"><rect x="10" y="26" width="26" height="3"/><rect x="10" y="68" width="26" height="3"/><rect x="10" y="99" width="26" height="3"/></g><g fill="#225989"><rect x="10" y="30" width="26" height="3"/><rect x="10" y="72" width="26" height="3"/><rect x="10" y="94" width="26" height="3"/></g><g fill="#fff3bc"><circle cx="14" cy="119" r="2"/><circle cx="32" cy="119" r="2"/></g></svg>'''

def history(p):
 th=p['path'].startswith('/th/');soup=BeautifulSoup(p.get('html',''),'html.parser');events=[]
 for heading in soup.find_all('h2'):
  year=heading.get_text(' ',strip=True)
  if not re.match(r'^\d{4}',year):continue
  block=heading.find_next_sibling()
  if not block:continue
  for e in block.select('.history__block--icon'):e.decompose()
  events.append((year,''.join(str(x) for x in block.contents)))
 buttons=''.join(f'<button data-year-target="year-{i}" aria-label="{("ไปยังปี" if th else "Go to")} {html.escape(year)}">{html.escape(year)}</button>' for i,(year,_) in enumerate(events))
 stations=''.join(f'''<article class="history-station" id="year-{i}" data-year="{html.escape(year,quote=True)}"><div class="history-event"><span class="station-index">STATION {i+1:02d} / {len(events):02d}</span><h2 tabindex="-1">{html.escape(year)}</h2><div class="history-event-copy">{body}</div></div></article>''' for i,(year,body) in enumerate(events))
 return f'''<section class="history-cinema" aria-label="{'การเดินทางผ่านประวัติบีทีเอสกรุ๊ป' if th else 'A journey through BTS Group history'}"><div class="history-run"><div class="history-stage"><div class="history-atmosphere"></div><div class="history-world-wrap"><canvas id="history-world" role="img" aria-label="{'ฉากรถไฟฟ้า 3 มิติ เคลื่อนตามการเลื่อนหน้า' if th else 'A 3D BTS train travelling as you scroll'}"></canvas><div class="history-loading">{'กำลังเตรียมขบวนรถไฟ…' if th else 'Preparing your journey…'}</div></div><div class="history-scene-heading"><h1 class="history-overline">{'ความเป็นมาของบริษัท' if th else 'OUR HISTORY'} / A JOURNEY IN MOTION</h1><div id="history-current">{events[0][0] if events else ''}</div><h3 id="history-scene-title">{'จุดเริ่มต้นของการเดินทาง' if th else 'Where our journey begins'}</h3><span id="history-scene-subtitle">{'จากรากฐาน สู่การเชื่อมต่อเมือง' if th else 'From foundations to a connected city'}</span></div><div class="history-scene-bottom"><span class="history-signal"><i></i><span id="history-train-state">{'เดินทางผ่านประวัติศาสตร์' if th else 'A journey in motion'}</span></span><button id="history-pause" type="button" aria-pressed="false">{'Ⅱ พักการเคลื่อนไหว' if th else 'Ⅱ Pause motion'}</button><span class="history-scroll-cue">{'เลื่อนเพื่อเดินทางต่อ' if th else 'SCROLL TO CONTINUE'} ↓</span></div><div class="history-route-progress"><i></i></div><nav class="history-years" aria-label="{'เลือกปี' if th else 'Choose a year'}">{buttons}</nav></div><div class="history-journey">{stations}</div></div><div class="journey-terminus"><span>THE NEXT CHAPTER</span><p>{'ทุกเส้นทาง พาเราไปข้างหน้า' if th else 'Every journey takes us forward.'}</p><a href="/{'th' if th else 'en'}/our-business/business-overview/">{'สำรวจธุรกิจของเรา' if th else 'Explore our businesses'} ↗</a></div></section><script type="module" src="/history-world.js?v=spacing-1"></script>'''


def chapter_art(kind,p,image):
 if kind in ('profile','article','news','career') and image and 'opengraph' not in image:
  return f'<div class="chapter-visual visual-{kind}"><img src="{html.escape(image,quote=True)}" alt=""/><span class="visual-caption">BTS GROUP / {kind.upper()}</span><i class="visual-frame"></i></div>'
 if kind=='journey':return f'<div class="chapter-visual visual-journey"><div class="hero-rail"></div><div class="hero-mini-train">{train_svg()}</div><span class="visual-word">ON<br/>TRACK.</span><span class="visual-caption">OUR STORY IN MOTION</span></div>'
 if kind in ('library','document','legal'):
  return '<div class="chapter-visual visual-library"><div class="paper paper-back"></div><div class="paper paper-middle"></div><div class="paper paper-front"><img src="/assets/bts-logo.svg" alt=""/><span>BORDERLESS<br/>TRANSFORM<br/><b>SOLUTIONS.</b></span><i></i><i></i><i></i></div><span class="visual-caption">KNOWLEDGE · TRUST · TRANSPARENCY</span></div>'
 if kind=='finance':return '<div class="chapter-visual visual-finance"><div class="finance-grid"></div><div class="finance-bars"><i></i><i></i><i></i><i></i><i></i></div><span class="visual-word">LOOK<br/>FORWARD.</span><span class="visual-caption">PERFORMANCE / LONG-TERM VALUE</span></div>'
 if kind=='impact':return '<div class="chapter-visual visual-impact"><div class="impact-orbit orbit-one"></div><div class="impact-orbit orbit-two"></div><div class="impact-leaf leaf-one"></div><div class="impact-leaf leaf-two"></div><span class="visual-word">GROW<br/>WITH<br/>CARE.</span><span class="visual-caption">PEOPLE · PLANET · PROGRESS</span></div>'
 if kind=='business':
  word=p['path'].split('/')[-1].upper();word=word if word in ['MOVE','MIX','MATCH'] else 'CONNECT.'
  return f'<div class="chapter-visual visual-business"><div class="business-orbit"></div><span class="business-word">{word}</span><div class="business-routes"><i></i><i></i><i></i></div><span class="visual-caption">ONE ECOSYSTEM. MANY POSSIBILITIES.</span></div>'
 if kind in ('people','contact'):return '<div class="chapter-visual visual-connect"><div class="connect-node node-a"></div><div class="connect-node node-b"></div><div class="connect-node node-c"></div><div class="connect-lines"></div><span class="visual-word">BETTER<br/>TOGETHER.</span><span class="visual-caption">PEOPLE & CONNECTIONS</span></div>'
 if image and 'opengraph' not in image:return f'<div class="chapter-visual visual-story"><img src="{html.escape(image,quote=True)}" alt=""/><div class="visual-shade"></div><span class="visual-word">BEYOND<br/>BORDERS.</span></div>'
 return '<div class="chapter-visual visual-business"><div class="business-orbit"></div><span class="business-word">BTS.</span><div class="business-routes"><i></i><i></i><i></i></div><span class="visual-caption">BORDERLESS TRANSFORM SOLUTIONS</span></div>'

def decorate(p,body):
 kind=layout_kind(p)
 if kind=='journey':return kind,history(p)
 soup=BeautifulSoup(body,'html.parser')
 # Give every topic its own visual hierarchy while retaining original text/data.
 if kind in ('article','story','career','impact'):
  first=next((x for x in soup.find_all('p') if len(x.get_text(strip=True))>85 and not x.find_parent('table')),None)
  if first:first['class']=first.get('class',[])+['chapter-lead']
 if kind=='finance':
  for table in soup.select('table'):
   if table.find('tr') and not table.find('thead'):
    row=table.find('tr');head=soup.new_tag('thead');row.extract();head.append(row);table.insert(0,head)
 if kind=='people':
  for card in soup.select('a.card-board'):
   for paragraph in card.select('.card-text')[1:]:paragraph.decompose()
 if kind=='article':
  for image in soup.select('img'):image['class']=image.get('class',[])+['article-photo']
 return kind,str(soup)
