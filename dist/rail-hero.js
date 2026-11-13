import * as T from './assets/three.module.js';
import { enrich } from './details.js';
const canvas=document.querySelector('#rail-scene');
const hero=document.querySelector('.hero');
const reduced=matchMedia('(prefers-reduced-motion: reduce)');
try {
 const renderer=new T.WebGLRenderer({canvas,antialias:true,alpha:true,powerPreference:'low-power'});
 renderer.setPixelRatio(Math.min(devicePixelRatio,1.8));renderer.setClearColor(0,0);renderer.shadowMap.enabled=true;renderer.shadowMap.type=T.PCFSoftShadowMap;renderer.outputColorSpace=T.SRGBColorSpace;renderer.toneMapping=T.ACESFilmicToneMapping;renderer.toneMappingExposure=1.0;
 const scene=new T.Scene(),world=new T.Group();scene.add(world);
 const camera=new T.OrthographicCamera(-8,8,6,-6,.1,100);camera.position.set(9,7.5,11);camera.lookAt(0,1.2,0);
 scene.add(new T.HemisphereLight(0xffffff,0x8794a8,2.0));const sun=new T.DirectionalLight(0xffffff,3.0);sun.position.set(-4,12,8);sun.castShadow=true;sun.shadow.mapSize.set(2048,2048);sun.shadow.camera.left=-16;sun.shadow.camera.right=16;sun.shadow.camera.top=10;sun.shadow.camera.bottom=-10;sun.shadow.normalBias=.035;sun.shadow.bias=-.0001;scene.add(sun);
 const mat=(color,roughness=.6,metalness=0)=>new T.MeshStandardMaterial({color,roughness,metalness});
 const concrete=mat(0xe2e6e8,.88),steel=mat(0x8d9ba8,.28,.7),dark=mat(0x34495c),white=mat(0xf3f5f4),blue=mat(0x163f91),red=mat(0xdf3347);
 function box(w,h,d,m,x,y,z,p=world){const a=new T.Mesh(new T.BoxGeometry(w,h,d),m);a.position.set(x,y,z);a.castShadow=true;a.receiveShadow=true;p.add(a);return a}
 // Continuous elevated guideway. Geometry stays fixed while the train traverses it.
 box(32,.28,1.22,concrete,0,1.46,0);box(32,.08,1.24,white,0,1.63,0);
 for(const z of [-.27,.27])box(32,.045,.05,steel,0,1.73,z);
 for(let x=-16;x<16;x+=.24)box(.09,.045,.82,dark,x,1.68,0);
 for(const z of [-.66,.66]){box(32,.15,.07,concrete,0,1.71,z);box(32,.023,.075,steel,0,1.8,z)}
 for(let x=-14;x<=14;x+=3.2){box(.32,1.3,.42,concrete,x,.68,0);box(1.05,.16,.92,concrete,x,1.25,0);box(.9,.12,.75,white,x,.06,0)}
 // A second guideway and a restrained station establish parallax and scale.
 box(26,.18,.83,concrete,0,1.3,-2.05);for(const z of [-2.28,-1.82])box(26,.035,.04,steel,0,1.42,z);
 box(5.3,.22,.88,white,1.2,1.47,-1.15);box(5.3,.025,.06,red,1.2,1.6,-.73);
 for(const x of [-1,1.1,3.3]){box(.065,1.25,.065,steel,x,2.17,-1.48);box(.08,.06,1.23,steel,x,2.76,-1.45)}
 const roof=box(5.7,.095,1.42,white,1.2,2.82,-1.45);roof.rotation.x=.06;
 for(let x=-1.35;x<3.8;x+=.36){box(.018,.07,1.38,steel,x,2.87,-1.45)}
 // Glass platform screen and simplified architectural volumes, kept behind the train.
 const glass= new T.MeshPhysicalMaterial({color:0xc8e0ec,transparent:true,opacity:.25,roughness:.16,metalness:.15,depthWrite:false});
 box(5.1,.55,.025,glass,1.2,1.93,-1.65);for(let x=-1.3;x<3.8;x+=.5)box(.018,.58,.025,steel,x,1.93,-1.65);
 for(const [x,z,h] of [[-4.2,-3.8,1.2],[4.5,-3.8,1.7]]){box(.85,h,.7,white,x,h/2,z);box(.9,.055,.75,steel,x,h,z)}
 function tree(x,z){box(.06,.8,.06,steel,x,.4,z);const crown=new T.Mesh(new T.SphereGeometry(.35,16,12),mat(0x19375a));crown.scale.set(.8,1.5,.8);crown.position.set(x,1.08,z);crown.castShadow=true;world.add(crown)}tree(-2.6,-3);tree(5.2,-2.8);
 const train=new T.Group();train.position.set(-2.4,1.86,0);train.scale.setScalar(1.1);world.add(train);const details=enrich(T,world,train,scene,renderer,{trainOnly:true});
 const floor=new T.Mesh(new T.PlaneGeometry(100,100),new T.ShadowMaterial({opacity:.11}));floor.rotation.x=-Math.PI/2;floor.position.y=-.02;floor.receiveShadow=true;scene.add(floor);
 let target=0,progress=0,last=performance.now(),visible=true,dirty=true;
 function onScroll(){const r=hero.getBoundingClientRect();target=reduced.matches?0:T.MathUtils.clamp(-r.top/Math.max(1,r.height-innerHeight),0,1);canvas.style.setProperty('--rail-progress',target);hero.style.setProperty('--rail-progress',target);dirty=true}
 function resize(){const r=canvas.parentElement.getBoundingClientRect();renderer.setSize(r.width,r.height,false);const aspect=r.width/r.height;const width=innerWidth<681?10.5:12.5;camera.left=-width/2;camera.right=width/2;camera.top=width/aspect/2;camera.bottom=-width/aspect/2;camera.updateProjectionMatrix();dirty=true;onScroll()}
 new ResizeObserver(resize).observe(canvas.parentElement);new IntersectionObserver(([e])=>{visible=e.isIntersecting;dirty=true},{rootMargin:'100px'}).observe(hero);addEventListener('scroll',onScroll,{passive:true});reduced.addEventListener('change',onScroll);resize();
 function frame(now){requestAnimationFrame(frame);const dt=Math.min((now-last)/1000,.05);last=now;if(!visible)return;const previous=progress;progress+= (target-progress)*(1-Math.exp(-dt*7));if(Math.abs(target-progress)<.00005)progress=target;if(!dirty&&progress===previous)return;const x=-2.4+progress*10.8;const speed=(progress-previous)*10.8/Math.max(dt,.001);train.position.x=x;details.update(now/1000,dt,speed,0);camera.position.set(9-progress*1.3,7.5-progress*.55,11+progress*.7);camera.zoom=1+Math.sin(progress*Math.PI)*.08;camera.lookAt(progress*1.2,1.2,0);camera.updateProjectionMatrix();renderer.render(scene,camera);canvas.dataset.progress=progress.toFixed(3);canvas.dataset.trainX=x.toFixed(3);dirty=false}
 requestAnimationFrame(frame);
 canvas.addEventListener('webglcontextlost',e=>{e.preventDefault();document.querySelector('.rail-error').hidden=false});
} catch(error){document.querySelector('.rail-error').hidden=false;console.error('Railway scene could not initialize:',error)}

