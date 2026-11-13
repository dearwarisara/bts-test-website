"""Extract the official sitemap hierarchy, including its adjacent-list markup."""
import json
from pathlib import Path
from urllib.parse import urlsplit
from bs4 import BeautifulSoup

root=Path(__file__).parent
keys=['home','about','our-business','investor-relations','corporate-governance','sustainability','corporate-communications','career','contact']
def parse_list(ul):
 nodes=[]
 for tag in ul.find_all(['li','ul'],recursive=False):
  if tag.name=='ul':
   if not nodes:raise ValueError('A sitemap list has no parent')
   nodes[-1].setdefault('children',[]).extend(parse_list(tag))
   continue
  heading=tag.find(['a','div'],recursive=False)
  if not heading:raise ValueError('A sitemap item has no label')
  node={'label':heading.get_text(' ',strip=True)}
  if heading.name=='a':
   url=urlsplit(heading['href']);assert url.netloc in ('www.btsgroup.co.th','btsgroup.co.th')
   node['path']=url.path.rstrip('/')
  for child in tag.find_all('ul',recursive=False):node.setdefault('children',[]).extend(parse_list(child))
  nodes.append(node)
 return nodes

navigation={}
for lang in ('th','en'):
 soup=BeautifulSoup((root/f'.cache-bts/{lang}__sitemap.html').read_text(encoding='utf8'),'html.parser')
 nodes=parse_list(soup.select_one('nav.sitemap > ul'))
 assert len(nodes)==len(keys),(lang,len(nodes))
 for key,node in zip(keys,nodes):node['key']=key
 navigation[lang]=nodes
 def count(nodes):return sum(bool(n.get('path'))+count(n.get('children',[])) for n in nodes)
 assert count(nodes)==len(soup.select('nav.sitemap a'))
 print(f'{lang}: {len(nodes)} top-level entries, {count(nodes)} links')
(root/'navigation-tree.json').write_text(json.dumps({'source':'https://www.btsgroup.co.th/th/sitemap','navigation':navigation},ensure_ascii=False,indent=2),encoding='utf8')
