import json,re,time,concurrent.futures,threading,hashlib
from pathlib import Path
from urllib.parse import urljoin,urlsplit,urlunsplit
import requests
from bs4 import BeautifulSoup
ROOT=Path(__file__).parent
CACHE=ROOT/'.cache-bts';CACHE.mkdir(exist_ok=True)
BASE='https://www.btsgroup.co.th'
thread=threading.local()
def get(url):
 if not hasattr(thread,'s'):thread.s=requests.Session()
 for attempt in range(3):
  try:
   r=thread.s.get(url,timeout=35);r.encoding='utf-8'
   if r.status_code==200:return r.text
  except requests.RequestException:pass
  time.sleep(.4*(attempt+1))
 raise RuntimeError('Could not read original page')
sitemap=BeautifulSoup(get(BASE+'/sitemap.xml'),'xml')
seed=[]
for item in sitemap.find_all('url'):
 seed.append(item.find('loc').text)
 seed.extend(x['href'] for x in item.find_all('link') if x.get('href'))
seed=list(dict.fromkeys(seed))
def canonical(url):
 u=urlsplit(urljoin(BASE,url))
 if u.netloc not in ('www.btsgroup.co.th','btsgroup.co.th'):return None
 if not re.match(r'^/(th|en)/',u.path):return None
 if re.search(r'\.(pdf|xlsx?|zip|docx?|jpe?g|png|webp|svg|mp4)$',u.path,re.I):return None
 return BASE+u.path.rstrip('/')
def collect(url):
 path=urlsplit(url).path
 filename=path.strip('/').replace('/','__')
 file=CACHE/((hashlib.sha256(path.encode()).hexdigest() if len(filename)>120 else filename)+'.html')
 try:
  text=file.read_text(encoding='utf8') if file.exists() else get(url)
  soup=BeautifulSoup(text,'html.parser');main=soup.select_one('main.content,main')
  if not main:raise RuntimeError('Missing original page content')
  file.write_text(text,encoding='utf8')
  title=(main.find('h1') or soup.find('title'))
  title=title.get_text(' ',strip=True).split('|')[0].strip() if title else path.split('/')[-1]
  links=[canonical(a.get('href','')) for a in main.select('a[href]')]
  hero=main.select_one('.banner__bg');banner=''
  if hero:
   match=re.search(r'url\([\'"]?([^\'"\)]+)',hero.get('style',''))
   if match:banner=urljoin(url,match.group(1))
  body=main.select_one('article') or main
  for e in body.select('script,style,link,meta,.content__header,.content__breadcrumb,.banner,noscript'):
   e.decompose()
  for f in body.find_all('form'):
   a=soup.new_tag('a',href=url);a['class']='official-action';a.string='เปิดแบบฟอร์มบนเว็บไซต์ BTS Group' if path.startswith('/th/') else 'Open this form on the BTS Group website';f.replace_with(a)
  for e in body.find_all(True):
   for key in list(e.attrs):
    if key.startswith('on') or key in ['style','srcdoc','data-sitekey','integrity','crossorigin']:del e.attrs[key]
   if e.name in ['input','textarea','select','button'] and e.find_parent('form') is None:
    if e.name=='input' and e.get('type')=='hidden':e.decompose();continue
   for attr in ['src','poster','href']:
    value=e.get(attr)
    if value and not value.startswith('#'):
     if value.startswith(('javascript:','data:text/html')):del e.attrs[attr]
     else:e[attr]=urljoin(url,value)
   if e.name=='img':e['loading']='lazy';e.attrs.pop('width',None);e.attrs.pop('height',None)
   if e.name=='iframe':e['loading']='lazy';e['title']=e.get('title') or title
   if 'nav' in e.get('class',[]):e['class']=['source-tabs' if c=='nav' else c for c in e['class']]
  # Native accordions replace Bootstrap's JavaScript dependency.
  for card in list(body.select('.card')):
   header=card.select_one('.card-header');content=card.select_one('.collapse')
   if header and content:
    details=soup.new_tag('details');details['class']='source-accordion'
    summary=soup.new_tag('summary');summary.string=header.get_text(' ',strip=True);details.append(summary)
    for child in list(content.contents):details.append(child.extract())
    card.replace_with(details)
  html=''.join(str(x) for x in body.contents)
  plain=body.get_text(' ',strip=True)
  return {'path':path,'title':title,'banner':banner,'html':html,'text':plain[:18000],'links':list(dict.fromkeys(x for x in links if x)),'source':url,'status':'ok'}
 except Exception as e:return {'path':path,'source':url,'status':'error','error':str(e),'links':[]}
all_pages={};pending=seed
for depth in range(3):
 pending=[x for x in dict.fromkeys(pending) if urlsplit(x).path not in all_pages]
 if not pending:break
 print('Reading batch',depth+1,'pages',len(pending),flush=True)
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
  for i,page in enumerate(pool.map(collect,pending)):
   all_pages[page['path']]=page
   if (i+1)%20==0:print('Read',i+1,'/',len(pending),flush=True)
 pending=[]
 for page in all_pages.values():
  for link in page['links']:
   path=urlsplit(link).path
   if path not in all_pages and '/document/' not in path and re.search(r'/(\d+)(?:/|$)',path):pending.append(link)
report={'seed_count':len(seed),'page_count':len(all_pages),'pages':list(all_pages.values())}
(CACHE/'pages.json').write_text(json.dumps(report,ensure_ascii=False),encoding='utf8')
print(json.dumps({'seed_count':len(seed),'page_count':len(all_pages),'errors':[p['path'] for p in all_pages.values() if p['status']!='ok']},ensure_ascii=True),flush=True)

index=json.loads((CACHE/'search-en.json').read_text(encoding='utf8'))
records={}
for item in index:
 url=canonical(item.get('url',''))
 if url:records[urlsplit(url).path]=dict(item,url=url)
new=[r['url'] for path,r in records.items() if path not in all_pages and '/document/viewer/' not in path]
print('Reading public search-index pages',len(new),flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
 for i,page in enumerate(pool.map(collect,new)):
  all_pages[page['path']]=page
  if (i+1)%25==0:print('Indexed content',i+1,'/',len(new),flush=True)
for path,record in records.items():
 if path not in all_pages:all_pages[path]={'path':path,'source':record['url'],'status':'document' if '/document/viewer/' in path else 'indexed','links':[]}
 page=all_pages[path];page['index']=record
 page['title']=page.get('title') or record['title']
 if page.get('status')=='error':page['status']='indexed'
 page['image']=record.get('image','')
report={'seed_count':len(seed),'page_count':len(all_pages),'pages':list(all_pages.values())}
(CACHE/'pages-extended.json').write_text(json.dumps(report,ensure_ascii=False),encoding='utf8')
from collections import Counter
print(json.dumps({'pages':len(all_pages),'status':dict(Counter(p['status'] for p in all_pages.values()))}),flush=True)
