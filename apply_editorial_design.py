from pathlib import Path
from bs4 import BeautifulSoup
R=Path(__file__).parent
for f in (R/'dist').rglob('*.html'):
 s=BeautifulSoup(f.read_text(encoding='utf8'),'html.parser')
 if not s.select_one('.site-header'):continue
 for n in s.select('link[href^="/bts-editorial.css"]'):n.decompose()
 s.head.append(s.new_tag('link',rel='stylesheet',href='/bts-editorial.css?v=6'))
 # Keep archive artwork restrained: show one representative story image per
 # news archive, and leave the remaining cards as clean editorial text cards.
 news_archive = s.body and s.body.get('data-path', '').endswith(('/news-event', '/update/news-event'))
 boxes = s.select('.source-body .card-bg')
 if news_archive:
  for box in boxes:
   for image in box.select('img'): image.decompose()
  boxes = boxes[:1]
 for box in boxes:
  if box.select_one('img'): continue
  a=box.find_parent('a',href=True)
  if not a:continue
  target=R/'dist'/a['href'].strip('/')/'index.html'
  if not target.is_file():continue
  source=BeautifulSoup(target.read_text(encoding='utf8'),'html.parser')
  photo=source.select_one('.source-body img[src]')
  if photo:
   img=s.new_tag('img',src=photo['src'],alt='',loading='eager')
   box.append(img)
 f.write_text(str(s),encoding='utf8')
print('Applied the BTS editorial system to all shared layouts.')
