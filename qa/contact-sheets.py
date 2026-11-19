from pathlib import Path
from PIL import Image,ImageDraw
p=Path(__file__).resolve().parent.parent/'.visual-qa-inner';(p/'sheets').mkdir(exist_ok=True)
for viewport in ['desktop','mobile']:
 files={int(f.stem):f for f in (p/viewport).glob('*.jpg')}
 for start in range(0,max(files,default=-1)+1,12):
  target=p/'sheets'/f'{viewport}-{start}.jpg'
  if target.exists() and target.stat().st_mtime >= max(f.stat().st_mtime for i,f in files.items() if start<=i<start+12):continue
  if not all(i in files for i in range(start,min(start+12,999))):continue
  canvas=Image.new('RGB',(1600,2100),'#dfe7ee');d=ImageDraw.Draw(canvas)
  for j in range(12):
   if start+j not in files:continue
   im=Image.open(files[start+j]).convert('RGB');im.thumbnail((390,660))
   x=(j%4)*400;y=(j//4)*700;d.text((x+5,y+4),str(start+j),fill='black');canvas.paste(im,(x+(400-im.width)//2,y+25))
  canvas.save(target,quality=88)
