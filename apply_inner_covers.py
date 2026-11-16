"""Apply photographed covers selected by article, route and BTS business topic."""
from pathlib import Path
from urllib.parse import urlsplit, unquote
from urllib.request import Request, urlopen
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
from PIL import Image
import hashlib, io, json, re

R=Path(__file__).parent; D=R/'dist'; A=D/'assets/covers'; A.mkdir(exist_ok=True)
CAT=json.loads((D/'site-catalog.json').read_text(encoding='utf-8'))['pages']
BY={unquote(p['href']).rstrip('/'):p for p in CAT}
BASE='https://www.btsgroup.co.th/storage/'
TOPICS={
 'company':'banner/banner-about.jpg',
 'business':'banner/banner-esg.jpg',
 'move':'business/move/rail-business.jpg',
 'mix':'business/mix/advertising.jpg',
 'match':'business/match/mixed-use.webp',
 'finance':'banner/banner-term.jpg',
 'governance':'banner/banner-cg.jpg',
 'news':'banner/banner-news.jpg',
 'contact':'banner/banner-contact.jpg',
 'careers':'banner/banner-career.jpg',
 'sustainability':'banner/banner-sustain.jpg',
 'environment':'banner/sustainability-guidelines.jpg',
 'social':'sustainability/social-sustainability-materials/banner.jpg',
 'economic':'sustainability/economic-sustainability/banner.jpg',
 'passengers':'banner/banner-inside.jpg',
 'awards':'update/news-event/2026/02/20260220-154640-1.webp',
}
# Designed announcement cards are unsuitable as full-bleed cover photographs.
EXCLUDED_PHOTOS={
 BASE+'update/news-event/2026/05/20260512-170623-1.webp',
 BASE+'update/news-event/2026/08/20260828-164407-3.webp',
 BASE+'update/news-event/2026/08/20260828-164407-5.webp',
}

def select_topic(p):
 path=unquote(p['path']).lower();group=p['group'];title=p['title'].lower()
 if '/our-business/move' in path:return 'move'
 if '/our-business/mix' in path:return 'mix'
 if '/our-business/match' in path:return 'match'
 if group=='our-business':return 'business'
 if 'environmental' in path:return 'environment'
 if 'social-sustainability' in path:return 'social'
 if 'economic-sustainability' in path:return 'economic'
 # Download/viewer routes inherit their document's subject rather than a logo.
 if group=='sustainability' or any(t in path+' '+title for t in ['sustainability','esg','ความยั่งยืน']):return 'sustainability'
 if group=='career':return 'careers'
 if group=='awards' or '/awards/' in path:return 'awards'
 if group=='contact' or '/ir-contact' in path or '/analyst-contact' in path:return 'contact'
 if group=='corporate-communications':return 'news'
 if group=='corporate-governance' or 'risk-management' in path or '/management-structure/' in path:return 'governance'
 if group=='investor-relations' or any(t in path+' '+title for t in ['financial','dividend','shareholder','debenture','warrant','รายงานประจำปี','งบการเงิน','annual report']):return 'finance'
 if group in ['terms-and-conditions','privacy-policy','privacy-statement','cookies-policy']:return 'finance'
 return 'company'

def photo_candidates(s,p):
 # Use a news article's own pictures, not report covers, headshots or diagrams.
 if '/update/news-event/' not in p['path']:return []
 result=[]
 for img in s.select('.source-body img'):
  src=img.get('src','')
  if '/storage/update/' in src and re.search(r'\.(jpg|jpeg|png|webp)(?:\?|$)',src,re.I):
   src=src.replace('/glide/storage/','/storage/').split('?')[0]
   if src not in result and src not in EXCLUDED_PHOTOS and '20260512-170623' not in src:result.append(src)
  if len(result)==3:break
 return result

def fetch(url):
 stem=hashlib.sha256(url.encode()).hexdigest()[:16]
 optimized=A/(stem+'-cover.webp');existing=([optimized] if optimized.exists() else list(A.glob(stem+'.*')))
 try:
  data=existing[0].read_bytes() if existing else urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=25).read()
  im=Image.open(io.BytesIO(data));im.verify();im=Image.open(io.BytesIO(data))
  w,h=im.size
  if w<580 or h<220 or w/h<1.3:raise ValueError(f'Unsuitable landscape photo: {w}x{h}')
  if im.format not in ['JPEG','PNG','WEBP']:raise ValueError('Not a static photographic format')
  # Delivery compression keeps local covers fast without relying on the source site.
  if not optimized.exists():
   im=im.convert('RGB')
   if w>1800:im.resize((1800,round(h*1800/w)),Image.Resampling.LANCZOS).save(optimized,quality=82,method=6)
   else:im.save(optimized,quality=82,method=6)
  with Image.open(optimized) as output:w,h=output.size
  return url,{'src':'/'+optimized.relative_to(D).as_posix(),'width':w,'height':h,'bytes':optimized.stat().st_size}
 except Exception as e:return url,{'error':str(e)}

pages=[];urls=set(BASE+v for v in TOPICS.values())
for f in sorted(D.rglob('*.html')):
 s=BeautifulSoup(f.read_text(encoding='utf-8-sig'),'html.parser')
 hero=s.select_one('.inner-hero,.history-intro')
 if not hero:continue
 route='/'+f.parent.relative_to(D).as_posix();p=BY[unquote(route)]
 topic=select_topic(p);candidates=photo_candidates(s,p)
 urls.update(candidates);pages.append((f,s,hero,p,topic,candidates))
photos=dict(ThreadPoolExecutor(8).map(fetch,sorted(urls)))
for topic,path in TOPICS.items():
 if 'error' in photos[BASE+path]:raise RuntimeError(topic+': '+str(photos[BASE+path]))
report=[]
for f,s,hero,p,topic,candidates in pages:
 article=next((u for u in candidates if 'src' in photos[u]),None)
 url=article or BASE+TOPICS[topic];photo=photos[url]
 holder=hero.select_one('.inner-cover')
 img=hero.select_one('.history-cover-image')
 if not img:
  if holder is None:
   holder=s.new_tag('div',attrs={'class':'inner-cover'});hero.insert(0,holder)
  holder.clear();img=s.new_tag('img',alt='');holder.append(img)
 img['src']=photo['src'];img['width']=str(photo['width']);img['height']=str(photo['height'])
 img['fetchpriority']='high';img['decoding']='async';img.attrs.pop('loading',None)
 hero['data-cover-topic']=topic
 title_length=len(hero.select_one('h1').get_text(' ',strip=True))
 hero['data-cover-title-length']='extended' if title_length>150 else 'long' if title_length>75 else 'short'
 if article:hero['data-cover-article']='true'
 else:hero.attrs.pop('data-cover-article',None)
 for n in s.select('link[href^="/bts-covers.css"]'):n.decompose()
 s.head.append(s.new_tag('link',rel='stylesheet',href='/bts-covers.css?v=1'))
 f.write_text(str(s),encoding='utf-8')
 report.append({'route':p['href'],'title':p['title'],'topic':topic,'selection':'article photograph' if article else 'BTS subject photograph','source':url,**photo})
out={'pages':len(report),'unique_photos':len({p['src'] for p in report}),'article_photos':sum(p['selection']=='article photograph' for p in report),'covers':report,'unusable_article_images':{u:v for u,v in photos.items() if 'error' in v}}
# Remove only generated, unused cover files in this dedicated asset directory.
used={p['src'].rsplit('/',1)[-1] for p in report}
for f in A.iterdir():
 if f.is_file() and f.parent.resolve()==A.resolve() and re.fullmatch(r'[a-f0-9]{16}(?:-cover)?\.(jpg|png|webp)',f.name) and f.name not in used:f.unlink()
(R/'inner-cover-report.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(f"Photographic covers: {out['pages']} pages, {out['unique_photos']} photographs, {out['article_photos']} article-specific covers")
