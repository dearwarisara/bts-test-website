from pathlib import Path
from bs4 import BeautifulSoup
R=Path(__file__).parent
for f in (R/'dist').rglob('*.html'):
 s=BeautifulSoup(f.read_text(encoding='utf8'),'html.parser')
 if not s.select_one('.site-header'):continue
 for n in s.select('link[href^="/bts-editorial.css"]'):n.decompose()
 s.head.append(s.new_tag('link',rel='stylesheet',href='/bts-editorial.css?v=1'))
 f.write_text(str(s),encoding='utf8')
print('Applied the BTS editorial system to all shared layouts.')
