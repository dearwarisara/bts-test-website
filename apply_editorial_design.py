from pathlib import Path
from bs4 import BeautifulSoup
R=Path(__file__).parent
for f in (R/'dist').rglob('*.html'):
 s=BeautifulSoup(f.read_text(encoding='utf8'),'html.parser')
 if not s.select_one('.site-header'):continue
 for n in s.select('link[href^="/bts-editorial.css"]'):n.decompose()
 s.head.append(s.new_tag('link',rel='stylesheet',href='/bts-editorial.css?v=20'))
 # Turn the homepage sustainability module into a full-bleed editorial scene.
 body_path = s.body.get('data-path', '') if s.body else ''
 if body_path in ('/th/home', '/en/home'):
  # The newsletter/IR contact tiles are redundant after the homepage story flow.
  for section in s.select('main > .planb-contact'):
   section.decompose()
  scene = s.select_one('.sustainability')
  if scene:
   is_th = s.html.get('lang', 'th') == 'th'
   heading = 'การพัฒนาอย่างยั่งยืน' if is_th else 'Sustainable Development'
   eyebrow = 'BTS GROUP  /  ความยั่งยืน' if is_th else 'BTS GROUP  /  SUSTAINABILITY'
   description = ('เรามุ่งสร้างคุณค่าระยะยาว ด้วยการดำเนินธุรกิจที่รับผิดชอบต่อสิ่งแวดล้อม สังคม และการกำกับดูแลกิจการที่ดี'
                  if is_th else 'We create long-term value through responsible business practices for the environment, society and good corporate governance.')
   link_text = 'สำรวจความยั่งยืน' if is_th else 'Explore sustainability'
   link_href = '/th/sustainability/sustainability-at-bts-group/' if is_th else '/en/sustainability/sustainability-at-bts-group/'
   scene.clear()
   scene['class'] = ['sustainability', 'sustainability-cover']
   scene['aria-labelledby'] = 'sustainability-cover-title'
   content = s.new_tag('div', attrs={'class': 'sustainability-cover-content'})
   label = s.new_tag('span', attrs={'class': 'sustainability-cover-eyebrow'})
   label.string = eyebrow
   title = s.new_tag('h2', id='sustainability-cover-title')
   title.string = heading
   copy = s.new_tag('p')
   copy.string = description
   cta = s.new_tag('a', href=link_href, attrs={'class': 'sustainability-cover-arrow', 'aria-label': link_text})
   arrow = s.new_tag('span', attrs={'aria-hidden': 'true'})
   arrow.string = '→'
   cta.append(arrow)
   links = s.new_tag('nav', attrs={'class': 'sustainability-cover-more', 'aria-label': 'Sustainability topics' if not is_th else 'หัวข้อความยั่งยืน'})
   destinations = [('sustainability/environmental-sustainability', 'ความยั่งยืนด้านสิ่งแวดล้อม' if is_th else 'Environmental Sustainability'),
                   ('sustainability/social-sustainability', 'ความยั่งยืนด้านสังคม' if is_th else 'Social Sustainability'),
                   ('corporate-governance/at-a-glance', 'การกำกับดูแลกิจการ' if is_th else 'Corporate Governance')]
   for index, (path, text) in enumerate(destinations):
    item = s.new_tag('a', href=f'/{s.html.get("lang", "th")}/{path}/', attrs={'data-esg': str(index)})
    item.string = text
    links.append(item)
   content.extend([label, title, copy, cta, links])
   scene.append(content)
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
