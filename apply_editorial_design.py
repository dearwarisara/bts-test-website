from pathlib import Path
from bs4 import BeautifulSoup

def apply_finance_scene(page, language):
 section = page.select_one('.financial-home')
 if section is None:
  return

 is_thai = language == 'th'
 label = section.select_one('.section-tag').get_text(strip=True)
 period = section.select_one('.financial-period').get_text(strip=True)
 period = period.removeprefix('ข้อมูลสำคัญทางการเงินประจำ' if is_thai else 'Financial Highlights ')
 figures = [figure.extract() for figure in section.select('.metric strong')]
 finance_url = section.select_one('.finance-actions a')['href']

 section.clear()
 section['class'] = ['finance-glass']
 section['aria-labelledby'] = 'finance-glass-title'
 scene = BeautifulSoup("""
 <div class="finance-glass-inner">
  <p class="finance-glass-eyebrow"></p>
  <h2 id="finance-glass-title"></h2>
  <p class="finance-glass-period"></p>
  <dl class="finance-glass-metrics"></dl>
  <a class="finance-glass-action"><span aria-hidden="true">↗</span></a>
 </div>
 """, 'html.parser').div

 scene.p.string = label
 heading = scene.h2
 if is_thai:
  heading.append('ข้อมูลสำคัญ')
  heading.append(page.new_tag('br'))
  heading.append('ทางการเงิน')
 else:
  heading.string = 'Key Financial Data'
 period_text, separator, unit = period.partition(' · ')
 period_node = scene.select_one('.finance-glass-period')
 period_node.append(period_text)
 if separator:
  dot = page.new_tag('span')
  dot.string = '·'
  period_node.append(dot)
  period_node.append(unit)

 labels = ('รายได้รวม', 'EBITDA', 'กำไร (ขาดทุน)') if is_thai else (
  'Total Revenue', 'EBITDA', 'Net Profit (Loss)')
 details = 'สุทธิส่วนที่เป็นของผู้ถือหุ้น' if is_thai else 'Attributable to Equity Holders'
 for index, (name, figure) in enumerate(zip(labels, figures)):
  card = page.new_tag('div', attrs={'class': 'finance-glass-card'})
  term = page.new_tag('dt')
  term.string = name
  if index == 2:
   detail = page.new_tag('span', attrs={'class': 'finance-glass-detail'})
   detail.string = details
   term.append(' ')
   term.append(detail)
  value = page.new_tag('dd')
  value.append(figure)
  card.extend([term, value])
  scene.dl.append(card)

 scene.a['href'] = finance_url
 scene.a.insert(0, 'ดูข้อมูลทางการเงิน' if is_thai else 'View Financial Data')
 section.append(scene)

def apply_investor_hub(page):
 compact_hub = page.select_one('section.investor-night#publications')
 if compact_hub is not None:
  focus_investor_documents(compact_hub)
  return

 section = page.select_one('section.investor#publications')
 if section is None:
  return

 intro = section.select_one('.investor-intro')
 intro.name = 'header'
 intro['class'] = ['investor-night-intro']
 intro.h2['id'] = 'investor-night-title'
 intro.select_one('.investor-eyebrow')['class'] = ['investor-night-eyebrow']

 resources = section.select_one('.investor-links')
 resources['class'] = ['investor-night-resources']
 for resource in resources.find_all('a', recursive=False):
  resource['class'] = ['investor-night-resource']
  icon = page.new_tag('span', attrs={'class': 'investor-night-icon', 'aria-hidden': 'true'})
  resource.svg.attrs.pop('class', None)
  resource.svg.wrap(icon)
  arrow = resource.b
  arrow.name = 'span'
  arrow['class'] = ['investor-night-arrow']

 action = intro.select_one('.investor-contact').extract()
 action['class'] = ['investor-night-action']
 arrow = action.b
 arrow.name = 'span'
 arrow['class'] = ['investor-night-arrow']
 arrow['aria-hidden'] = 'true'

 section.clear()
 section['class'] = ['investor-night']
 section['aria-labelledby'] = 'investor-night-title'
 inner = page.new_tag('div', attrs={'class': 'investor-night-inner'})
 inner.extend([intro.extract(), resources.extract(), action])
 section.append(inner)
 focus_investor_documents(section)

def focus_investor_documents(section):
 for link in section.select('.investor-night-resources a[href]'):
  if link['href'].rstrip('/').endswith('/financial-information/key-financial-data'):
   link.decompose()
 intro_copy = section.select_one('.investor-night-intro > p')
 if intro_copy is not None:
  intro_copy.decompose()

R=Path(__file__).parent
for f in (R/'dist').rglob('*.html'):
 s=BeautifulSoup(f.read_text(encoding='utf8'),'html.parser')
 if not s.select_one('.site-header'):continue
 for n in s.select('link[href^="/bts-editorial.css"]'):n.decompose()
 body_path = s.body.get('data-path', '') if s.body else ''
 stylesheet_version = 31 if body_path in ('/th/home', '/en/home') else 26
 s.head.append(s.new_tag('link',rel='stylesheet',href=f'/bts-editorial.css?v={stylesheet_version}'))
 # Turn the homepage sustainability module into a full-bleed editorial scene.
 if body_path in ('/th/home', '/en/home'):
  apply_finance_scene(s, body_path.split('/')[1])
  apply_investor_hub(s)
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
