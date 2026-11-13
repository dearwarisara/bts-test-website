import * as T from './assets/three.module.js';
import { enrich } from './details.js';
import { createJourneyMap, advanceMotion } from './history-motion.js';
import { batchStatic } from './history-batch.js';
import { createLivingScene } from './history-life.js';

const canvas=document.querySelector('#history-world');
if(canvas) {
 const host=canvas.closest('.history-cinema'),stage=host.querySelector('.history-stage'),journey=host.querySelector('.history-journey');
 const cards=[...journey.querySelectorAll('.history-station')],buttons=[...host.querySelectorAll('[data-year-target]')];
 const en=document.documentElement.lang==='en',reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
 const themes=[
  ['FOUNDATIONS','จุดเริ่มต้นของการเดินทาง','Where our journey begins','วางรากฐานธุรกิจอสังหาริมทรัพย์','Laying our property foundations',0xe8dec7,0xb9c9c3],
  ['BUILDING CONNECTIONS','สร้างเส้นทางใหม่ให้เมือง','Building a new way forward','จากวิสัยทัศน์ สู่โครงสร้างระบบราง','From a vision to urban rail',0xe4e7df,0xabc4ca],
  ['A CITY IN MOTION','เมืองที่เริ่มเคลื่อนไหว','A city in motion','การเดินทางที่เชื่อมชีวิตผู้คน','Connecting people and places',0xdde9e8,0x91b4c5],
  ['BEYOND THE JOURNEY','เชื่อมโอกาสที่มากกว่าการเดินทาง','Beyond the journey','ระบบราง สื่อ และโอกาสใหม่','Rail, media and new opportunities',0xe5e5ef,0x9daec5],
  ['A GROWING NETWORK','ขยายเครือข่าย เชื่อมต่ออนาคต','A growing network','เส้นทางใหม่ เชื่อมต่อกันมากขึ้น','New lines. More connections.',0xe3ece4,0x98bcb2],
  ['THE NEXT CHAPTER','ก้าวต่อไปอย่างไร้ขีดจำกัด','The next chapter','การเดินทาง ที่อยู่อาศัย และโครงสร้างพื้นฐาน','Mobility, homes and infrastructure',0xe6ecdf,0x9fbec2]
 ];
 // The scenery follows the actual chapter represented by each original milestone.
 const themeFor=i=>i<2?0:i<4?1:i<6?2:i<12?3:i<18?4:5;
 const chapterNames=[
  ['จุดเริ่มต้นของการเดินทาง','Where our journey begins','วางรากฐานธุรกิจอสังหาริมทรัพย์','Laying our property foundations'],
  ['ก้าวสู่ตลาดหลักทรัพย์','A new public chapter','อีกก้าวของธนายงในตลาดทุนไทย','Tanayong enters the Thai stock market'],
  ['สร้างเส้นทางใหม่ให้เมือง','Building a new way forward','จุดเริ่มต้นของรถไฟฟ้าบีทีเอสสายหลัก','The foundations of Bangkok’s BTS SkyTrain'],
  ['ผ่านความท้าทายไปด้วยกัน','Through a challenging chapter','วิกฤติเศรษฐกิจในภูมิภาคเอเชีย','The Asian financial crisis'],
  ['กรุงเทพฯ เริ่มเคลื่อนไหว','Bangkok in motion','เปิดให้บริการรถไฟฟ้าบีทีเอสสายหลัก','The BTS SkyTrain begins service'],
  ['พร้อมเดินหน้าต่อ','Ready to move forward','ธนายงและบีทีเอสซีออกจากกระบวนการฟื้นฟู','Emerging from rehabilitation'],
  ['เชื่อมต่อมากกว่าการเดินทาง','Beyond the journey','ส่วนต่อขยายสายสีลม และก้าวสู่ธุรกิจสื่อ','The Silom extension and a move into media'],
  ['ก้าวใหม่ในชื่อบีทีเอส กรุ๊ป','A new chapter as BTS Group','เชื่อมธุรกิจและระบบขนส่งเข้าด้วยกัน','Bringing businesses and transport together'],
  ['เชื่อมเมืองออกไปอีก','Connecting more of the city','เปิดให้บริการส่วนต่อขยายสายสุขุมวิท','The Sukhumvit extension opens'],
  ['ต่อยอดเส้นทางและโอกาส','New routes. New opportunities.','สัญญาเดินรถและซ่อมบำรุง และการเติบโตของ VGI','Rail operations and VGI’s growth'],
  ['เปิดมิติใหม่ของการลงทุน','A new investment milestone','กองทุนโครงสร้างพื้นฐาน BTSGIF','The BTSGIF infrastructure fund'],
  ['เสริมรากฐานให้แข็งแรง','Strengthening our foundations','ขยายการลงทุนในธุรกิจอสังหาริมทรัพย์','Expanding our property investments'],
  ['เครือข่ายใหม่ อนาคตใหม่','A growing network','ส่วนต่อขยายสีเขียว สายสีชมพู และสายสีเหลือง','Green extensions, Pink and Yellow lines'],
  ['เชื่อมต่อเมืองและธุรกิจ','Connecting cities and businesses','สายสีเขียว สายสีทอง และโอกาสแบบ O2O','Green and Gold lines. O2O opportunities.'],
  ['จากเมือง สู่ภูมิภาค','From the city to the region','สนามบินอู่ตะเภา มอเตอร์เวย์ และเส้นทางใหม่','U-Tapao, motorways and new rail connections'],
  ['MOVE. MIX. MATCH.','MOVE. MIX. MATCH.','กลยุทธ์ใหม่ ภายใต้ Borderless, Transform, Solutions','A new strategy. Borderless, Transform, Solutions.'],
  ['ต่อยอดทุกการเชื่อมต่อ','Creating new connections','ขยายเครือข่ายและแพลตฟอร์มการลงทุน','Growing our network and investment platforms'],
  ['สีใหม่ของการเดินทาง','New colours of mobility','เปิดให้บริการสายสีเหลืองและสายสีชมพู','The Yellow and Pink lines begin service'],
  ['ปรับโครงสร้าง พร้อมเติบโต','Reshaping for growth','การปรับโครงสร้างกลุ่มบริษัท และรถโดยสารไฟฟ้า BRT','Group restructuring and electric BRT service'],
  ['เชื่อมต่อทุกช่วงการเดินทาง','Connecting every journey','ระบบ APM สนามบินสุวรรณภูมิ และสายสีชมพูส่วนต่อขยาย','Suvarnabhumi APM and the Pink Line extension'],
  ['ก้าวต่อไปอย่างไร้ขีดจำกัด','The next chapter','มอเตอร์เวย์ บ้านชาวไทย และสนามบินอู่ตะเภา','Motorways, Baan Chao Thai and U-Tapao']
 ];
 const years=cards.map(c=>c.dataset.year),scene=new T.Scene();
 let renderer;
 try{renderer=new T.WebGLRenderer({canvas,alpha:true,antialias:true,powerPreference:'high-performance'});}catch(e){stage.classList.add('history-no-webgl');host.querySelector('.history-loading').textContent=en?'3D is unavailable on this device. Explore the full timeline below.':'อุปกรณ์นี้ไม่รองรับฉาก 3D อ่านเหตุการณ์ตามปีได้ด้านล่าง';}
 if(renderer)start();
 function start(){
 renderer.setPixelRatio(Math.min(devicePixelRatio,innerWidth<700?1.5:1.75));renderer.outputColorSpace=T.SRGBColorSpace;renderer.toneMapping=T.ACESFilmicToneMapping;renderer.toneMappingExposure=1.04;
 renderer.shadowMap.enabled=true;renderer.shadowMap.type=T.PCFSoftShadowMap;renderer.shadowMap.autoUpdate=true;
 const camera=new T.PerspectiveCamera(35,1,.1,72);scene.fog=new T.Fog(0xe8dec7,21,54);
 const hemi=new T.HemisphereLight(0xeef7ff,0x85836c,1.8);scene.add(hemi);
 const sun=new T.DirectionalLight(0xffedd1,3.2);sun.position.set(-9,16,8);sun.castShadow=true;sun.shadow.mapSize.set(1024,1024);Object.assign(sun.shadow.camera,{left:-10,right:10,top:10,bottom:-10,near:.5,far:55});sun.shadow.normalBias=.04;scene.add(sun,sun.target);
 const world=new T.Group();scene.add(world);const train=new T.Group();world.add(train);
 const detail=enrich(T,world,train,scene,renderer,{trainOnly:true});
 const cache=new Map(),geos=new Map();
 function mat(c,metal=0,rough=.65){const key=[c,metal,rough].join();if(!cache.has(key))cache.set(key,new T.MeshStandardMaterial({color:c,metalness:metal,roughness:rough}));return cache.get(key)}
 const concrete=mat(0xc4cbc7),steel=mat(0x5b707b,.7,.3),navy=mat(0x173e62),red=mat(0xe33242),glass=mat(0x355c6c,.4,.22),white=mat(0xeeeade),green=mat(0x527964),leafLight=mat(0x849b72),roadMat=mat(0x76838a);
 function box(w,h,d,m,x,y,z,p=world){const key=[w,h,d].join();if(!geos.has(key))geos.set(key,new T.BoxGeometry(w,h,d));const mesh=new T.Mesh(geos.get(key),m);mesh.position.set(x,y,z);mesh.castShadow=true;mesh.receiveShadow=true;p.add(mesh);return mesh}
 function sphere(r,m,x,y,z,p=world){const key='s'+r;if(!geos.has(key))geos.set(key,new T.SphereGeometry(r,10,8));const mesh=new T.Mesh(geos.get(key),m);mesh.position.set(x,y,z);mesh.castShadow=true;p.add(mesh);return mesh}
 function sign(text,w,h,x,y,z,p,bg='#17394b',fg='#ffffff'){
  const c=document.createElement('canvas');c.width=1024;c.height=256;const cx=c.getContext('2d');cx.fillStyle=bg;cx.fillRect(0,0,1024,256);cx.fillStyle=fg;cx.textAlign='center';cx.textBaseline='middle';cx.font='bold 105px Arial';cx.fillText(text,512,134,950);const t=new T.CanvasTexture(c);t.colorSpace=T.SRGBColorSpace;
  const m=new T.MeshStandardMaterial({map:t,emissiveMap:t,emissive:0xffffff,emissiveIntensity:.15,roughness:.45});const q=new T.Mesh(new T.PlaneGeometry(w,h),m);q.position.set(x,y,z);p.add(q);return q;
 }
 const stopGap=21,end=(cards.length-1)*stopGap;
 const curvePoint=z=>new T.Vector3(Math.sin(z*.042)*2.8,1.65,z);
 const tangent=z=>new T.Vector3(Math.cos(z*.042)*.1176,0,1).normalize();
 const railPoints=[];for(let z=-36;z<=end+45;z+=2)railPoints.push(curvePoint(z));

 function rail(offset,radius,m,y=0){const pts=railPoints.map(p=>new T.Vector3(p.x+offset,p.y+y,p.z));const mesh=new T.Mesh(new T.TubeGeometry(new T.CatmullRomCurve3(pts),660,radius,5,false),m);mesh.receiveShadow=true;world.add(mesh);return mesh}
 rail(-.27,.035,steel,.12);rail(.27,.035,steel,.12);
 rail(-.72,.075,concrete,-.05);rail(.72,.075,concrete,-.05);
 const dummy=new T.Object3D();
 function instances(geo,m,n,place){const mesh=new T.InstancedMesh(geo,m,n);for(let i=0;i<n;i++){dummy.position.set(0,0,0);dummy.rotation.set(0,0,0);dummy.scale.set(1,1,1);place(dummy,i);dummy.updateMatrix();mesh.setMatrixAt(i,dummy.matrix)}mesh.receiveShadow=true;world.add(mesh);return mesh}
 const trackN=Math.ceil((end+80)/.32);
 instances(new T.BoxGeometry(.82,.07,.12),mat(0x7d898b),trackN,(o,i)=>{const z=-36+i*.32,p=curvePoint(z);o.position.set(p.x,p.y+.05,z);o.rotation.y=Math.atan2(tangent(z).x,1)});
 instances(new T.BoxGeometry(1.62,.25,2.2),concrete,Math.ceil((end+80)/2.1),(o,i)=>{const z=-36+i*2.1,p=curvePoint(z);o.position.set(p.x,p.y-.2,z);o.rotation.y=Math.atan2(tangent(z).x,1)});
 instances(new T.BoxGeometry(.4,1.65,.5),concrete,Math.ceil((end+80)/5),(o,i)=>{const z=-36+i*5,p=curvePoint(z);o.position.set(p.x,.6,z)});
 const terrain=box(90,.3,end+120,mat(0x9aa38b),0,-.48,end/2);
 box(4,.04,end+115,roadMat,7,-.29,end/2);box(.1,.01,end+115,white,7,-.265,end/2);
 instances(new T.BoxGeometry(.07,.01,.85),white,Math.ceil((end+110)/2),(o,i)=>o.position.set(7,-.26,-45+i*2));
 // A continuous waterway catches the changing sky as the camera follows the train.
 const water=box(5,.03,end+120,new T.MeshPhysicalMaterial({color:0x7babb7,roughness:.22,metalness:.25,clearcoat:1}),-11,-.25,end/2);
 const chapters=[],commuters=[],movingCars=[],cranes=[],windmills=[],planes=[],billboards=[];
 function tree(x,z,p,s=1){box(.09,.7*s,.09,mat(0x7f6b53),x,.12+s*.25,z,p);const a=sphere(.42*s,green,x,.85*s,z,p);a.scale.y=1.4;const b=sphere(.3*s,leafLight,x+.2*s,.65*s,z+.1,p);return a}
 function building(x,z,w,h,d,c,p,windows=true){box(w,h,d,mat(c,.12),x,h/2-.25,z,p);box(w+.1,.12,d+.1,white,x,h-.19,z,p);if(windows){for(let y=.35;y<h-.2;y+=.48)box(w*.76,.21,.025,glass,x,y,z+d/2+.018,p);for(let y=.35;y<h-.2;y+=.48)box(.025,.21,d*.78,glass,x+w/2+.018,y,z,p)}return h}
 function person(x,z,p,i){const g=new T.Group();g.userData.animated=true;p.add(g);g.position.set(x,1.93,z);sphere(.06,mat(0xc6a183),0,.37,0,g);box(.105,.2,.085,i%3===0?red:navy,0,.22,0,g);const legs=[box(.035,.15,.04,navy,-.03,.05,0,g),box(.035,.15,.04,navy,.03,.05,0,g)];commuters.push({g,legs,phase:i,base:x,baseZ:z})}
 function platform(z,p,index){
  box(1.75,.23,7,white,-1.76,1.65,0,p);box(.06,.02,7,mat(0xe2c35e),-.94,1.78,0,p);
  for(const dz of [-2.7,0,2.7]){box(.08,1.45,.08,steel,-2.26,2.48,dz,p);box(1.6,.07,.08,steel,-1.7,3.17,dz,p)}
  const roof=box(1.9,.11,7.3,mat(0x567589,.35),-1.8,3.22,0,p);roof.rotation.z=-.06;
  for(let k=0;k<11;k++)box(1.92,.025,.025,steel,-1.8,3.29,-3.3+k*.66,p);
  sign('BTS  /  '+years[index],2.15,.47,-1.85,2.77,1.3,p);
  for(let k=0;k<4;k++)person(-1.48-k%2*.38,-2+k*1.1,p,k+index);
  for(let k=0;k<8;k++)box(.65,.13,.32,concrete,-3.0,.1+k*.2,-1.2+k*.3,p);
 }
 const seed=i=>{const a=Math.sin(i*127.1+47)*43758.5453;return a-Math.floor(a)};
 for(let i=0;i<cards.length;i++){
  const z=i*stopGap,pos=curvePoint(z),g=new T.Group();g.position.set(pos.x,0,z);g.rotation.y=Math.atan2(tangent(z).x,1);world.add(g);const theme=themeFor(i);chapters.push({g,z,theme});platform(z,g,i);
  const district=new T.Group();g.add(district);
  for(let j=0;j<6;j++){const x=j<3?-5.1-(j%3)*1.35:9.5+(j%3)*1.2,zz=(seed(i*11+j)-.5)*15,w=.8+seed(j*5+i)*.9,h=(theme<2?1.1:2.4)+seed(i*17+j)* (theme<2?2:5);building(x,zz,w,h,1.2,theme===0?0xc4b395:theme===3?0xb8c6cf:0xc8d2cf,district)}
  for(let j=0;j<7;j++)tree(-3.9-(j%2)*.9,-7+j*2.1,g,.65+seed(i+j)*.4);
  if(theme===0){for(let j=0;j<3;j++)building(3.2+j*.95,-4+j*1.8,.72,1.1,.95,0xddc7a5,g);}
  if(theme===1){
   box(.22,5,.22,mat(0xd7b25e),3.6,2.2,-3,g);const crane=new T.Group();crane.userData.animated=true;crane.position.set(3.6,4.8,-3);g.add(crane);box(7,.12,.14,mat(0xd7b25e),.5,0,0,crane);box(.03,2,.03,steel,2.7,-1,0,crane);box(.45,.18,.4,navy,2.7,-2,0,crane);cranes.push(crane);
   for(let k=0;k<4;k++){box(2.5,.12,2.3,concrete,4.1,.6+k*.8,2,g);for(const x of [3.1,5.1])box(.1,3.3,.1,steel,x,1.6,2,g)}
  }
  if(theme===3||i===1||i===15||i===18){const label=({1:'SET / 1991',6:'VGI',7:'BTS GROUP',8:'SUKHUMVIT',9:'VGI / BTS',10:'BTSGIF',11:'U CITY',15:'MOVE MIX MATCH',18:'BTS GROUP'})[i]||'BTS GROUP';const b=sign(label,3,1.55,3.5,3.1,-1.7,g,'#e32c40');box(.14,2.5,.14,steel,3.5,1.4,-1.8,g);billboards.push(b);}
  if(theme>=4){
   for(let k=0;k<2;k++){const color=k?mat(0xe6bc48):mat(0xdba3bc),q=box(7,.12,.17,color,-4,3.9+k*.35,5+k,g);q.rotation.y=-.5;for(const x of [-6,-2])box(.15,4,.15,white,x,1.7,5+k,g)}
   for(let j=0;j<2;j++){const pole=box(.09,2,.09,white,-7.8,1,-4+j*4,g),blades=new T.Group();blades.userData.animated=true;blades.position.set(-7.8,2,-4+j*4);g.add(blades);for(let k=0;k<3;k++){const blade=box(.12,1.1,.05,white,0,.5,0,blades);blade.geometry=blade.geometry.clone();blade.geometry.translate(0,.5,0);blade.position.y=0;blade.rotation.z=k*Math.PI*2/3}windmills.push(blades);}
  }
  if(i===20){for(let j=0;j<4;j++){building(3.1+(j%2)*1.35,3+Math.floor(j/2)*1.8,1.05,.95,1.15,0xdedac4,g,false);const panel=box(.9,.045,.65,navy,3.1+(j%2)*1.35,.8,3+Math.floor(j/2)*1.8,g);panel.rotation.x=.25;}}
  if([14,19,20].includes(i)){building(4.3,-3,3.2,.75,1.6,0xd3dfdd,g);box(.15,2.3,.15,white,5.8,1,-4,g);box(.6,.35,.6,glass,5.8,2.25,-4,g);const plane=new T.Group();plane.userData.animated=true;g.add(plane);box(2.3,.15,.22,white,0,0,0,plane);const wing=box(.65,.06,2.1,white,-.1,0,0,plane);wing.rotation.y=.2;box(.6,.3,.05,red,-.8,.15,0,plane);planes.push({g:plane,base:new T.Vector3(2.5,6,-6),phase:i});}
  if(i===18){const bus=new T.Group();bus.userData.animated=true;g.add(bus);bus.position.set(6.2,0,2);box(.65,.55,2,mat(0x489d74),0,.38,0,bus);box(.67,.24,1.8,glass,0,.52,0,bus);sign('BRT',.5,.15,0,.62,1.02,bus);for(const z of [-.65,.65])for(const x of [-.34,.34])sphere(.12,navy,x,.08,z,bus);movingCars.push({g:bus,phase:15,speed:.7,local:true})}
 }
 const life=createLivingScene(T,world,{chapters,end,curvePoint,box,sphere,mat,sign});
 // Batching keeps the richer scenery inexpensive and the close-up train sharp.
 for(const chapter of chapters)batchStatic(T,chapter.g);
 const wheelSet=new Set(detail.wheels);for(const car of train.children)batchStatic(T,car,wheelSet);
 // Road traffic continues independently of scroll input.
 for(let i=0;i<9;i++){const g=new T.Group();world.add(g);box(.4,.17,.85,mat([0xd53346,0xe1c45f,0xe6ece7,0x2b759b][i%4]),0,.15,0,g);box(.35,.17,.4,glass,0,.3,-.02,g);for(const x of [-.2,.2])for(const z of [-.25,.25])sphere(.07,navy,x,.04,z,g);movingCars.push({g,phase:i*9,speed:.6+i*.08})}
 const birds=[];for(let i=0;i<5;i++){const g=new T.Group();scene.add(g);const a=box(.22,.025,.08,navy,-.1,0,0,g),b=box(.22,.025,.08,navy,.1,0,0,g);birds.push({g,a,b,phase:i});}
 let centers=[],mapJourney=()=>0,scrollDistance=0,distance=-8,active=-1,paused=reduced,clock=0,last=performance.now(),visible=true,pointerX=0,softPointer=0,statsTime=0,statsFrames=0,frameSum=0,lastSky='';
 const motion={position:-8,velocity:0};const look=new T.Vector3(),cameraOffset=new T.Vector3();
 const current=host.querySelector('#history-current'),title=host.querySelector('#history-scene-title'),subtitle=host.querySelector('#history-scene-subtitle'),status=host.querySelector('#history-train-state'),pause=host.querySelector('#history-pause');
 const clamp=(v,a=0,b=1)=>Math.max(a,Math.min(b,v));
 function cardCenter(c){const event=c.querySelector('.history-event');return event.getBoundingClientRect().top+scrollY+Math.min(event.offsetHeight,innerHeight*.55)*.5;}
 function measure(){centers=cards.map(cardCenter);mapJourney=createJourneyMap(centers,stopGap,innerHeight*.8);syncScroll()}
 function syncScroll(){
  const read=scrollY+innerHeight*(innerWidth<700?.82:.5);let i=0;while(i<centers.length-1&&read>=centers[i+1])i++;
  const u=i===centers.length-1?0:clamp((read-centers[i])/(centers[i+1]-centers[i]));
  scrollDistance=mapJourney(read);
  const selection=Math.min(cards.length-1,i+(u>.53?1:0));
  if(active!==selection){active=selection;const chapter=chapterNames[active];current.textContent=years[active];title.textContent=chapter[en?1:0];subtitle.textContent=chapter[en?3:2];stage.dataset.era=String(themeFor(active));cards.forEach((c,j)=>c.classList.toggle('is-active',j===active));buttons.forEach((b,j)=>{b.classList.toggle('is-current',j===active);b.setAttribute('aria-current',j===active?'step':'false')});const bar=host.querySelector('.history-years'),b=buttons[active];bar.scrollTo({left:b.offsetLeft-bar.clientWidth/2+b.clientWidth/2,behavior:reduced?'instant':'smooth'});}
  host.querySelector('.history-route-progress i').style.transform=`scaleX(${clamp((scrollDistance+9)/(end+9))})`;
 }
 const resize=()=>{const r=canvas.parentElement.getBoundingClientRect();renderer.setSize(r.width,r.height,false);camera.aspect=r.width/r.height;camera.fov=innerWidth<700?34:35;camera.updateProjectionMatrix();measure()};
 new ResizeObserver(resize).observe(canvas.parentElement);document.fonts.ready.then(measure);
 addEventListener('scroll',syncScroll,{passive:true});addEventListener('resize',measure,{passive:true});
 buttons.forEach((b,i)=>b.addEventListener('click',()=>{const target=cardCenter(cards[i])-innerHeight*(innerWidth<700?.82:.5);window.scrollTo({top:target,behavior:reduced?'instant':'smooth'});cards[i].querySelector('h2').focus({preventScroll:true})}));
 pause.addEventListener('click',()=>{paused=!paused;updatePause()});function updatePause(){pause.setAttribute('aria-pressed',String(paused));pause.textContent=paused?(en?'▶ Play motion':'▶ เล่นการเคลื่อนไหว'):(en?'Ⅱ Pause motion':'Ⅱ พักการเคลื่อนไหว')};updatePause();
 host.addEventListener('pointermove',e=>{pointerX=(e.clientX/innerWidth-.5)*.5});host.addEventListener('pointerleave',()=>pointerX=0);
 new IntersectionObserver(es=>visible=es[0].isIntersecting,{rootMargin:'150px'}).observe(host);
 const sky=new T.Color(),targetColor=new T.Color();
 function frame(now){requestAnimationFrame(frame);const elapsed=(now-last)/1000,dt=Math.min(elapsed,.1);last=now;if(!visible||document.hidden)return;
  if(!paused)clock+=dt;
  if(reduced){motion.position=scrollDistance;motion.velocity=0;}else if(!paused)advanceMotion(motion,scrollDistance,dt);
  distance=motion.position;const velocity=paused?0:motion.velocity;
  const p=curvePoint(distance),v=tangent(distance);train.position.copy(p);train.position.y+=.26+(paused?0:Math.sin(clock*6)*.0015);train.rotation.y=Math.atan2(v.x,v.z)-Math.PI/2;detail.update(clock,dt,velocity,0);
  const mobile=innerWidth<700;softPointer+=(pointerX-softPointer)*(1-Math.exp(-dt*3));
  cameraOffset.set((mobile?6.0:6.15)+softPointer, mobile?6.0:6.35, mobile?7.5:7.3);
  camera.position.copy(p).add(cameraOffset);look.set(p.x-(mobile?.95:.6),mobile?2.65:2.5,p.z-.8);camera.lookAt(look);
  sun.position.set(p.x-9,16,p.z+8);sun.target.position.set(p.x,0,p.z);
  const theme=themes[themeFor(Math.max(active,0))];targetColor.setHex(theme[5]);sky.lerp(targetColor,1-Math.exp(-dt*1.4));scene.fog.color.copy(sky);const skyHex=sky.getHexString();if(skyHex!==lastSky){host.style.setProperty('--sky','#'+skyHex);lastSky=skyHex;}terrain.material.color.lerp(targetColor.setHex(theme[6]),1-Math.exp(-dt*1.4));
  const state=paused?(en?'MOTION PAUSED':'พักการเคลื่อนไหว'):(en?'A JOURNEY IN MOTION · ':'เดินทางผ่านปี · ')+years[Math.max(active,0)];if(status.textContent!==state)status.textContent=state;
  for(const c of chapters)c.g.visible=Math.abs(c.z-distance)<32;
  if(!paused){life.update(clock);for(let i=0;i<billboards.length;i++)billboards[i].material.emissiveIntensity=.24+Math.sin(clock*.6+i)*.08;for(const c of commuters){if(c.g.parent.visible){c.g.position.x=c.base+Math.sin(clock*.4+c.phase)*.07;c.g.position.z=c.baseZ+Math.sin(clock*.28+c.phase)*.48;for(let k=0;k<2;k++)c.legs[k].rotation.x=Math.sin(clock*5+c.phase+k*Math.PI)*.23;}}
   for(const c of movingCars){if(c.local)c.g.position.z=Math.sin(clock*.12)*5;else{c.g.position.set(6.2+c.phase%2*1.6,.0,distance+((clock*c.speed+c.phase)%62)-29);c.g.rotation.y=c.phase%2?Math.PI:0;}}
   for(let i=0;i<cranes.length;i++)cranes[i].rotation.y=Math.sin(clock*.13+i)*.17;
   for(const w of windmills)w.rotation.z=clock*.55;
   for(const a of planes){a.g.position.copy(a.base);a.g.position.x+=Math.sin(clock*.13+a.phase)*4;a.g.position.z+=Math.cos(clock*.13+a.phase)*2;a.g.rotation.y=Math.cos(clock*.13+a.phase)*.2;}
   for(const b of birds){b.g.position.set(p.x+Math.sin(clock*.2+b.phase)*8,6.5+Math.sin(clock*.5+b.phase),distance-8+Math.cos(clock*.2+b.phase)*5);b.a.rotation.z=Math.sin(clock*5+b.phase)*.5;b.b.rotation.z=-b.a.rotation.z;}
   water.material.color.setRGB(.40+Math.sin(clock*.3)*.015,.61,.67);
  }
  renderer.render(scene,camera);
  statsTime+=elapsed;frameSum+=elapsed;statsFrames++;if(statsTime>=1){canvas.dataset.drawCalls=String(renderer.info.render.calls);canvas.dataset.frameMs=(frameSum/statsFrames*1000).toFixed(1);statsTime=0;frameSum=0;statsFrames=0;}

 }
 resize();distance=scrollDistance;motion.position=distance;renderer.compile(scene,camera);requestAnimationFrame(frame);stage.classList.add('history-ready');
 }
}
