"""Create a self-contained, offline 3D history preview without external assets."""
import base64,mimetypes,re,sys
from pathlib import Path
from bs4 import BeautifulSoup

root=Path(__file__).parent
dist=root/'dist'
target=Path(sys.argv[1])
def data(raw,mime):
 return 'data:'+mime+';base64,'+base64.b64encode(raw).decode()
def asset(name):
 p=dist/name.lstrip('./')
 return data(p.read_bytes(),mimetypes.guess_type(str(p))[0] or 'application/octet-stream')

soup=BeautifulSoup((dist/'th/about/our-history/index.html').read_text(encoding='utf8'),'html.parser')
for script in soup.select('script'):script.decompose()
for block in soup.select('.page-hero,.chapter-navigation,.related-pages'):block.decompose()
for link in soup.select('link[rel="stylesheet"]'):
 css=(dist/link['href'].lstrip('/')).read_text(encoding='utf8')
 css=re.sub(r'''url\(['"]?(\.?/assets/[^'"\)]+)['"]?\)''',lambda m:'url('+asset(m[1])+')',css)
 style=soup.new_tag('style');style.string=css;link.replace_with(style)
logo=asset('assets/bts-logo.svg')
header=soup.select_one('.site-header')
header.clear()
new=BeautifulSoup(f'<a class="brand" href="https://bts-group-home-refresh-2026.optiwise-3224.chatgpt.site/th/home/"><img src="{logo}" alt="BTS Group" style="width:52px;height:77px"/></a><span style="font:400 23px OzoneX;color:#274f64">ความเป็นมาของบริษัท · 3D Preview</span>','html.parser')
for node in list(new.contents):header.append(node)
for img in soup.select('img[src]'):
 if img['src'].startswith('/assets/'):img['src']=asset(img['src'])
 elif not img['src'].startswith('data:'):img.decompose()
for a in soup.select('a[href]'):
 if a['href'].startswith('/'):a['href']='https://bts-group-home-refresh-2026.optiwise-3224.chatgpt.site'+a['href']
three=data((dist/'assets/three.module.js').read_bytes(),'text/javascript')
details=(dist/'details.js').read_text(encoding='utf8').replace("'/assets/bts-logo.svg'",repr(logo))
details=data(details.encode(),'text/javascript')
code=(dist/'history-world.js').read_text(encoding='utf8').replace("'./assets/three.module.js'",repr(three)).replace("'./details.js'",repr(details))
for name in ('history-motion.js','history-batch.js','history-life.js'):
 code=code.replace(repr('./'+name),repr(data((dist/name).read_bytes(),'text/javascript')))
script=soup.new_tag('script',type='module');script.string=code;soup.body.append(script)
target.write_text(str(soup),encoding='utf8')
print(f'Created standalone preview: {target.name} ({target.stat().st_size:,} bytes)')
