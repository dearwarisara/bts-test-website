from pathlib import Path
from bs4 import BeautifulSoup
R=Path(__file__).parent;D=R/'dist'
for lang in ['th','en']:
 f=D/lang/'investor-relations/home/index.html';s=BeautifulSoup(f.read_text(encoding='utf-8'),'html.parser');root=s.select_one('.ir_home')
 s.body['class']=list(dict.fromkeys(s.body.get('class',[])+['ir-home-page']))
 sections=[n for n in root.children if getattr(n,'name',None)]
 for n in root.select('.billboard--ir-home'):n.decompose()
 sections=[n for n in root.children if getattr(n,'name',None)]
 for n,cls in zip(sections,['ir-results','ir-publications','ir-news-events','ir-contact-section']):
  n['class']=list(dict.fromkeys(n.get('class',[])+[cls]))
  if cls=='ir-contact-section':n['class']=[c for c in n['class'] if c!='container']
 # Replace the nonfunctional Bootstrap modal with a native, keyboard-accessible disclosure.
 for card in root.select('.ir_home__download'):
  modal=card.select_one('.modal')
  if not modal:continue
  trigger=card.select_one('a[data-toggle]');label=card.find('div',recursive=False)
  content=modal.select_one('.modal-body');items=list(content.contents)
  card.name='details';card['data-ir-documents']='';summary=s.new_tag('summary')
  summary.append(label.extract());trigger.name='span'
  for a in ['data-toggle','data-target','href']:trigger.attrs.pop(a,None)
  summary.append(trigger.extract());card.clear();card.append(summary)
  body=s.new_tag('div',attrs={'class':'ir-document-options'})
  for n in items:body.append(n.extract())
  card.append(body)
 for a in root.select('a[href]'):
  href=a['href']
  if href.startswith('/en/investor-relations/events-calendar/') and lang=='th':a['href']='/th/investor-relations/events-calendar/'
 for card in s.select('.related-pages .page-card'):
  image=card.select_one('.page-card-image')
  if image:image.decompose()
  desc=card.select_one('p');heading=card.select_one('h3')
  if desc and heading and desc.get_text(strip=True)==heading.get_text(strip=True):desc.decompose()
 for n in s.select('link[href^="/ir-home.css"]'):n.decompose()
 s.head.append(s.new_tag('link',rel='stylesheet',href='/ir-home.css?v=1'))
 f.write_text(str(s),encoding='utf-8')
 print(lang+': redesigned IR overview and replaced broken download modal')
