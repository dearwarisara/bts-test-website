"""Extend the BTS investor visual system to every other internal page."""
from pathlib import Path
from urllib.parse import unquote
from bs4 import BeautifulSoup
from collections import Counter
import json,re
R=Path(__file__).parent;D=R/'dist'
catalog=json.loads((D/'site-catalog.json').read_text(encoding='utf-8'))['pages']
by={unquote(p['href']).rstrip('/'):p for p in catalog}
stats=Counter();rows=[]
def add(n,c):n['class']=list(dict.fromkeys(n.get('class',[])+[c]))
for f in sorted(D.rglob('*.html')):
 s=BeautifulSoup(f.read_text(encoding='utf-8-sig'),'html.parser')
 if not s.body or 'inner-page' not in s.body.get('class',[]) or 'ir-home-page' in s.body.get('class',[]):continue
 route='/'+f.parent.relative_to(D).as_posix();p=by[unquote(route)];path=unquote(p['path']);body=s.select_one('.source-body')
 add(s.body,'modern-inner');s.body['data-modern-group']=p['group']
 kind='reading'
 if '/our-history' in path:kind='history'
 elif p.get('document') or '/document/' in path:kind='documents'
 elif '/management-structure/' in path:kind='profile'
 elif '/update/news-event/' in path:kind='news'
 elif body.select_one('table'):kind='data'
 elif p['group'] in ['about','our-business','sustainability','corporate-governance','career','contact']:kind='editorial'
 s.body['data-modern-kind']=kind
 photos=icons=0
 if kind!='history':
  for section in body.find_all('section',recursive=False):add(section,'modern-section')
  # Let source photographs tell their own subject; charts and document covers stay uncropped.
  for img in body.select('img'):
   img['class']=[c for c in img.get('class',[]) if c not in ('modern-photo','modern-icon')]
   src=img.get('src','');classes=img.get('class',[])
   if 'business-related__card-image' in classes:continue
   if 'icon' in src.lower() or any('icon' in c for c in classes):
    add(img,'modern-icon');icons+=1
   elif re.search(r'/storage/(business|sustainability|cg|update/news-event)/',src) and not re.search(r'chart|info-|infographic|logo|table|diagram',src,re.I):
    add(img,'modern-photo');photos+=1
  for row in body.select('.row'):
   cols=[n for n in row.find_all(recursive=False) if any(c.startswith('col-') for c in n.get('class',[]))]
   if len(cols)>=2 and all(n.select_one(':scope > .card-content,:scope > .card-default,:scope > .card-board,:scope > .card--sustainability') for n in cols):
    add(row,'modern-card-grid');row['data-modern-columns']='3' if any(n.select_one('.card-board,.card--sustainability') for n in cols) else '2'
  if '/about/our-ambition' in path:
   first=body.find('section',recursive=False)
   if first:add(first,'modern-emphasis')
  # Flatten obsolete nested half-height wrappers into a responsive photographic grid.
  gallery=body.select_one('.cg-at_a_glance>.container')
  if gallery:
   cards=gallery.select('.card-more:has(img.card-photo)')
   if cards:
    grid=s.new_tag('div',attrs={'class':'modern-photo-grid'})
    for card in cards:add(card,'modern-photo-card');grid.append(card.extract())
    gallery.clear();gallery.append(grid)
 for n in s.select('link[href^="/bts-modern-inner.css"],script[src^="/bts-modern-inner.js"]'):n.decompose()
 s.head.append(s.new_tag('link',rel='stylesheet',href='/bts-modern-inner.css?v=1'))
 s.body.append(s.new_tag('script',src='/bts-modern-inner.js?v=1',type='module'))
 f.write_text(str(s),encoding='utf-8')
 stats[kind]+=1;rows.append({'route':p['href'],'kind':kind,'group':p['group'],'source_photos':photos,'bounded_icons':icons})
(R/'modern-inner-report.json').write_text(json.dumps({'pages':len(rows),'kinds':dict(stats),'source_photos':sum(p['source_photos'] for p in rows),'bounded_icons':sum(p['bounded_icons'] for p in rows),'routes':rows},ensure_ascii=False,indent=2),encoding='utf-8')
print('Modernized '+str(len(rows))+' internal pages: '+str(dict(stats)))
