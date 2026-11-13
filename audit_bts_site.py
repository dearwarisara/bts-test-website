"""Audit shared styling, local routes, original navigation and preserved content."""
from pathlib import Path
from urllib.parse import urlsplit,unquote
from collections import Counter
from bs4 import BeautifulSoup
import json,subprocess,sys
R=Path(__file__).parent;D=R/'dist';cat=json.loads((D/'site-catalog.json').read_text(encoding='utf-8'))
files=sorted(D.rglob('*.html'));issues=[];missing=Counter();external=Counter();content_mismatch=[];inner=[]
def text(article):
 if article is None:return None
 for n in article.select('.source-attribution'):n.decompose()
 return ' '.join(' '.join(article.stripped_strings).split())
for f in files:
 s=BeautifulSoup(f.read_text(encoding='utf-8'),'html.parser');lang='en' if s.html.get('lang')=='en' else 'th'
 if len(s.select('body>header.site-header'))!=1 or len(s.select('body>footer.bts-footer'))!=1 or not s.select_one('link[href^="/bts-brand.css"]') or not s.select_one('link[href^="/bts-inner.css"]'):issues.append(str(f.relative_to(R)))
 labels=[n.get_text(' ',strip=True) for n in s.select('.main-nav > button,.main-nav > a.nav-direct')]
 if labels!=[n['label'] for n in cat['navigation'][lang]]:issues.append('Navigation: '+str(f.relative_to(R)))
 for a in s.select('header a[href],footer a[href]'):
  if urlsplit(a['href']).netloc:external[a['href']]+=1
 for a in s.select('a[href]'):
  h=a['href'];u=urlsplit(h)
  if h.startswith('/') and not h.startswith('//') and not Path(u.path).suffix:
   p=D/u.path.lstrip('/')/'index.html';q=D/unquote(u.path.lstrip('/'))/'index.html'
   if not p.exists() and not q.exists():missing[h]+=1
 if s.select_one('.inner-hero'):inner.append((f,text(s.select_one('.source-body'))))
specs=[('HEAD:'+f.relative_to(R).as_posix()) for f,_ in inner]
batch=subprocess.run(['git','cat-file','--batch'],cwd=R,input=('\n'.join(specs)+'\n').encode(),stdout=subprocess.PIPE,check=True).stdout
pos=0;checked=0
for (f,current),spec in zip(inner,specs):
 end=batch.index(b'\n',pos);header=batch[pos:end].decode();pos=end+1
 if header.endswith(' missing'):content_mismatch.append(spec);continue
 size=int(header.rsplit(' ',1)[1]);blob=batch[pos:pos+size];pos+=size+1
 old=BeautifulSoup(blob.decode('utf-8-sig'),'html.parser')
 if text(old.select_one('.source-body'))!=current:content_mismatch.append(str(f.relative_to(R)))
 checked+=1
report={'baseline_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),'pages':len(files),'inner_content_checked':checked,'content_changes':content_mismatch,'shell_or_navigation_errors':issues,'external_menu_links':dict(external),'missing_local_links':dict(missing)}
(R/'site-unification-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
if issues or missing or external or content_mismatch:sys.exit(1)
