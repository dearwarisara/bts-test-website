"""Check every internal cover and verify each delivery image can be decoded."""
from pathlib import Path
from bs4 import BeautifulSoup
from PIL import Image
import json,sys
R=Path(__file__).parent;D=R/'dist'
manifest=json.loads((R/'inner-cover-report.json').read_text(encoding='utf-8'))
expected={p['route'].rstrip('/'):p for p in manifest['covers']}
errors=[];checked=[];images=set()
for f in D.rglob('*.html'):
 s=BeautifulSoup(f.read_text(encoding='utf-8-sig'),'html.parser')
 if not s.body or 'inner-page' not in s.body.get('class',[]):continue
 route='/'+f.parent.relative_to(D).as_posix();hero=s.select_one('.inner-hero,.history-intro')
 if not hero:errors.append([route,'Missing cover']);continue
 img=hero.select_one('.inner-cover img,.history-cover-image');h=hero.select_one('h1')
 if not h or not h.get_text(strip=True):errors.append([route,'Missing page title'])
 if not s.select_one('link[href^="/bts-covers.css"]'):errors.append([route,'Missing shared cover stylesheet'])
 if not img or not img.get('src','').startswith('/assets/covers/'):
  errors.append([route,'Cover must use a local photograph']);continue
 src=img['src'];images.add(src)
 if route not in expected or expected[route]['src']!=src:errors.append([route,'Cover differs from approved selection'])
 if img.get('loading')=='lazy':errors.append([route,'Above-fold image must load immediately'])
 checked.append(route)
for src in images:
 f=D/src.lstrip('/')
 try:
  with Image.open(f) as im:
   w,h=im.size;im.verify()
  if w<580 or h<220 or w>1800 or w/h<1.3:errors.append([src,'Inappropriate cover dimensions'])
 except Exception as e:errors.append([src,str(e)])
if set(checked)!=set(expected):errors.append(['coverage','Manifest and internal pages differ'])
report={'internal_pages_checked':len(checked),'decoded_local_photos':len(images),'delivery_bytes':sum((D/src.lstrip('/')).stat().st_size for src in images),'errors':errors}
(R/'inner-cover-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
if errors:sys.exit(1)
