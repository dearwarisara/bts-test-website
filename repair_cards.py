"""Give all generated cards an explicit content box and a readable excerpt."""
from pathlib import Path
from bs4 import BeautifulSoup
from card_content import summarize,card_image
import json
R=Path(__file__).parent;D=R/'dist'
cat=json.loads((D/'site-catalog.json').read_text(encoding='utf-8'))
lookup={p['href'].rstrip('/'):p for p in cat['pages']}
changed=0;cards=0
for f in D.rglob('*.html'):
 raw=f.read_text(encoding='utf-8');s=BeautifulSoup(raw,'html.parser');dirty=False
 for section in s.select('.related-pages'):section['id']='related-information'
 for card in s.select('.page-card'):
  data=lookup.get(card.get('href','').rstrip('/'))
  if data:
   p=card.select_one('p')
   if p:
    p.string=summarize(data.get('description',''));p.attrs.pop('class',None)
   image=card.select_one('.page-card-image img')
   if image:image['src']=card_image(data)
  if not card.select_one(':scope > .page-card-body'):
   body=s.new_tag('div',attrs={'class':'page-card-body'})
   for n in list(card.contents):
    if getattr(n,'get',None) and 'page-card-image' in n.get('class',[]):continue
    body.append(n.extract())
   card.append(body)
  card['data-card-layout']='v2';cards+=1;dirty=True
 if dirty:f.write_text(str(s),encoding='utf-8');changed+=1
print(f'Reviewed card content and layout: {cards} cards across {changed} pages')
