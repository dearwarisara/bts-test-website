"""Replace the history model with an expansive, accessible vertical timeline."""
from pathlib import Path
from bs4 import BeautifulSoup
import json
R=Path(__file__).parent;D=R/'dist'
ART=json.loads((R/'history-image-prompts.json').read_text(encoding='utf-8'))['assets']
for lang in ('th','en'):
 f=D/lang/'about/our-history/index.html';s=BeautifulSoup(f.read_text(encoding='utf-8'),'html.parser')
 old=s.select('.history-station,.timeline-entry');records=[]
 for entry in old:
  copy=entry.select_one('.history-event-copy')
  if copy:records.append((entry.get('data-year') or entry.select_one('h2').get_text(strip=True),str(copy)))
 if not records:raise RuntimeError('History source milestones missing: '+lang)
 for n in s.select('.inner-hero,.history-intro,.timeline-years'):n.decompose()
 for n in s.select('script[src],link[href]'):
  u=n.get('src',n.get('href',''))
  if any(x in u for x in ('history-world','history-timeline','chapter-motion.js')):n.decompose()
 s.body['class']=list(dict.fromkeys(s.body.get('class',[])+['history-timeline-page']))
 intro=s.new_tag('section',attrs={'class':'history-intro'})
 title='Our History' if lang=='en' else 'ความเป็นมาของบริษัท'
 home='Home' if lang=='en' else 'หน้าหลัก';about='About BTS Group' if lang=='en' else 'เกี่ยวกับบีทีเอสกรุ๊ป'
 sub='Milestones through the years' if lang=='en' else 'เส้นทางการเติบโตของบีทีเอสกรุ๊ป'
 first,last=records[0][0],records[-1][0]
 intro.append(BeautifulSoup(f'<div class="history-intro-top"><div class="history-breadcrumb"><a href="/{lang}/home/">{home}</a><span>/</span><span>{about}</span></div><span class="history-kicker">BTS GROUP / OUR HISTORY</span></div><div class="history-intro-grid"><div><h1>{title}</h1><p>{sub}</p></div><div class="history-date-range"><span>{first}</span><i aria-hidden="true">—</i><span>{last}</span><small>{len(records)} '+('MILESTONES' if lang=='en' else 'เหตุการณ์สำคัญ')+'</small></div></div>','html.parser'))
 s.main.insert(0,intro)
 source=s.select_one('.source-body');source.clear()
 nav=s.new_tag('nav',attrs={'class':'timeline-years','aria-label':'Choose a year' if lang=='en' else 'เลือกปี'})
 caption=s.new_tag('span',attrs={'class':'timeline-nav-caption'});caption.string='YEAR' if lang=='en' else 'ปี';nav.append(caption)
 scroller=s.new_tag('div',attrs={'class':'timeline-year-links'});nav.append(scroller)
 timeline=s.new_tag('section',attrs={'class':'bts-timeline','aria-label':title})
 rail=s.new_tag('div',attrs={'class':'timeline-rail','aria-hidden':'true'});progress=s.new_tag('i',attrs={'class':'timeline-rail-progress'});rail.append(progress);train=s.new_tag('div',attrs={'class':'timeline-train','aria-hidden':'true'});train.append(s.new_tag('img',src='/assets/bts-timeline-train-top.svg',alt='',attrs={'class':'timeline-train-body'}));rail.append(train);timeline.append(rail)
 listing=s.new_tag('ol',attrs={'class':'timeline-list'});timeline.append(listing)
 for i,(year,copy_html) in enumerate(records):
  link=s.new_tag('a',href=f'#year-{i}',attrs={'data-timeline-year':str(i)});link.string=year;scroller.append(link)
  entry=s.new_tag('li',id=f'year-{i}',attrs={'class':'timeline-entry','data-year':year})
  dot=s.new_tag('span',attrs={'class':'timeline-stop','aria-hidden':'true'});entry.append(dot)
  content=s.new_tag('article',attrs={'class':'timeline-content'})
  heading=s.new_tag('h2',attrs={'class':'timeline-year-label','tabindex':'-1'});heading.string=year;content.append(heading)
  copy=BeautifulSoup(copy_html,'html.parser').select_one('.history-event-copy');copy['class']=['history-event-copy','timeline-copy'];content.append(copy)
  entry.append(content)
  art=ART[i];art_path=R/art.get('web_file',art['file'])
  if not art_path.exists():raise RuntimeError('Missing generated illustration: '+str(art_path))
  figure=s.new_tag('figure',attrs={'class':'timeline-art'})
  image=s.new_tag('img',src='/'+str(art_path.relative_to(D)).replace('\\','/'),alt=('Concept illustration for ' if lang=='en' else 'ภาพประกอบแนวคิดปี ')+year,loading='lazy',decoding='async',width=str(art['width']),height=str(art['height']))
  figure.append(image)
  caption=s.new_tag('figcaption');caption.string='Concept illustration · AI' if lang=='en' else 'ภาพประกอบแนวคิด · AI';figure.append(caption)
  entry.append(figure);listing.append(entry)
 end=s.new_tag('div',attrs={'class':'timeline-end','aria-hidden':'true'});end.string='BTS GROUP';timeline.append(end)
 source.append(timeline);s.select_one('.page-layout').insert_before(nav)
 css=s.new_tag('link',rel='stylesheet',href='/history-timeline.css?v=4');s.head.append(css)
 js=s.new_tag('script',src='/history-timeline.js?v=2',type='module');s.body.append(js)
 f.write_text(str(s),encoding='utf-8')
 print(f'{lang}: redesigned {len(records)} history milestones')
