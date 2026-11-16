"""Use the official tiger film at home and the rail film on the IR cover."""
from pathlib import Path
from bs4 import BeautifulSoup
R=Path(__file__).parent;D=R/'dist'
BASE='https://www.btsgroup.co.th/storage/'
for route in ['index.html','th/home/index.html','en/home/index.html']:
 f=D/route;s=BeautifulSoup(f.read_text(encoding='utf-8'),'html.parser');v=s.select_one('#hero-video')
 v['poster']=BASE+'bilboard/banner-res.jpg'
 v.attrs.pop('src',None)
 for n in v.select('source'):n.decompose()
 v.append(s.new_tag('source',src=BASE+'bilboard/video-banner.mp4',type='video/mp4'))
 f.write_text(str(s),encoding='utf-8')
for lang in ['th','en']:
 f=D/lang/'investor-relations/home/index.html';s=BeautifulSoup(f.read_text(encoding='utf-8'),'html.parser')
 hero=s.select_one('.inner-hero');hero['class']=list(dict.fromkeys(hero.get('class',[])+['video-cover']))
 s.select_one('link[href^="/bts-covers.css"]')['href']='/bts-covers.css?v=2'
 for n in s.select('.source-body .ir-banner,.cover-video,.cover-video-toggle,script[src^="/cover-video.js"]'):n.decompose()
 video=s.new_tag('video',attrs={'class':'cover-video','autoplay':'','muted':'','loop':'','playsinline':'','preload':'metadata','poster':BASE+'bilboard/banner-masstransit-v2.jpg','aria-hidden':'true'})
 video.append(s.new_tag('source',src=BASE+'investor-relations/home/video-banner.mp4',type='video/mp4'))
 hero.select_one('.inner-cover').append(video)
 button=s.new_tag('button',type='button',attrs={'class':'cover-video-toggle','aria-label':'Pause cover video' if lang=='en' else 'หยุดวิดีโอ cover'});button.string='Ⅱ';hero.append(button)
 s.body.append(s.new_tag('script',src='/cover-video.js?v=1',type='module'))
 f.write_text(str(s),encoding='utf-8')
print('Updated 3 homepage tiger videos and 2 IR video covers; removed duplicate IR players.')
