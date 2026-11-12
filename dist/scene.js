import * as T from './assets/three.module.js';
import { enrich } from './details.js';
import { animateCity } from './life.js';
const canvas=document.querySelector('#bts-world');
const scene=new T.Scene();
const renderer=new T.WebGLRenderer({canvas,antialias:true,alpha:true});renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.shadowMap.enabled=true;renderer.shadowMap.type=T.PCFSoftShadowMap;renderer.setClearColor(0x000000,0);renderer.outputColorSpace=T.SRGBColorSpace;renderer.toneMapping=T.ACESFilmicToneMapping;renderer.toneMappingExposure=1.05;
const camera=new T.PerspectiveCamera(31,1,.1,100);camera.position.set(11,9.5,12.5);camera.lookAt(0,1,0);
scene.add(new T.HemisphereLight(0xf7f8ef,0x7a8791,2.1));const light=new T.DirectionalLight(0xfff4df,4.2);light.position.set(-5,12,7);light.castShadow=true;light.shadow.mapSize.set(2048,2048);light.shadow.camera.left=-10;light.shadow.camera.right=10;light.shadow.camera.top=10;light.shadow.camera.bottom=-10;light.shadow.normalBias=.035;scene.add(light);
const world=new T.Group();scene.add(world);
const mat=(c,rough=.7,metal=0)=>new T.MeshStandardMaterial({color:c,roughness:rough,metalness:metal});
const silver=mat(0xe9eeec,.25,.45),blue=mat(0x154776,.35,.2),red=mat(0xe12735,.4,.2),glass=mat(0x152d3d,.17,.4),concrete=mat(0xc8ccca),dark=mat(0x25323b),green=mat(0x84906b),wood=mat(0x7a664a);
function box(w,h,d,m,x,y,z,p=world){const a=new T.Mesh(new T.BoxGeometry(w,h,d),m);a.position.set(x,y,z);a.castShadow=true;a.receiveShadow=true;p.add(a);return a}
function sphere(r,m,x,y,z,p=world){const a=new T.Mesh(new T.IcosahedronGeometry(r,1),m);a.position.set(x,y,z);a.castShadow=true;p.add(a);return a}
// Floating city block, layered earth, riverside and a miniature Bangkok neighbourhood.
box(7.6,.85,6.1,mat(0x635e54),0,-.5,0);box(7.6,.16,6.1,mat(0xa5ac93),0,.005,0);box(7.6,.16,1.5,mat(0x759fae,.2,.15),0,.06,2.25);
for(let i=0;i<20;i++){box(.025,.025,1.25,mat(0xb2c6cc,.3),-3.5+i*.37,.16,2.25)}
box(7.45,.04,.67,mat(0x78818a),0,.12,-.9);for(let i=0;i<19;i++)box(.17,.008,.025,mat(0xece9d7),-3.5+i*.39,.147,-.9);
function tree(x,z,s=1){box(.09,.65*s,.09,wood,x,.4*s,z);const crown=sphere(.37*s,mat(0x557856),x,.95*s,z);crown.scale.y=1.35;sphere(.24*s,mat(0x718b62),x+.15*s,.8*s,z+.1)}
for(const v of [[-3,-2.2,.9],[-2.3,-2.4,1.1],[-1.4,-2.3,.75],[2.9,-1.8,.85],[3.1,.8,.65],[-2.8,1.3,.65]])tree(...v);
const buildings=[[1.2,-2,.6,2.6,.65],[2,-2.2,.55,3.4,.6],[.2,-2.3,.7,1.9,.7],[-.7,-2.2,.5,1.4,.6]];
for(const [x,z,w,h,d] of buildings){box(w,h,d,mat(0xc3cbd0),x,h/2+.1,z);box(w+.06,.07,d+.06,mat(0x899ba5),x,h+.14,z);for(let y=.4;y<h;y+=.32)for(let xx=-w/2+.12;xx<w/2;xx+=.19)box(.09,.15,.012,mat(0x6b8899),x+xx,y,z+d/2+.01)}
// Elevated guideway and its supports.
for(const x of [-2.8,-.9,1,2.9]){box(.26,1.4,.35,concrete,x,.76,.35);box(.85,.2,.75,concrete,x,1.43,.35)}
box(7.5,.27,1.05,concrete,0,1.62,.35);box(7.6,.07,.055,mat(0x727c83,.2,.6),0,1.8,.07);box(7.6,.07,.055,mat(0x727c83,.2,.6),0,1.8,.63);
for(let x=-3.65;x<3.7;x+=.22)box(.08,.045,.74,dark,x,1.77,.35);
const train=new T.Group();world.add(train);train.position.set(-.3,1.92,.35);
for(let car=0;car<3;car++){const g=new T.Group();train.add(g);g.position.x=(car-1)*1.64;box(1.54,.58,.61,silver,0,.38,0,g);box(1.48,.085,.58,mat(0xd4dcdb,.3,.4),0,.71,0,g);box(1.54,.055,.625,red,0,.22,0,g);box(1.54,.065,.63,blue,0,.14,0,g);box(1.25,.1,.45,dark,0,.035,0,g);
for(const z of [-.313,.313]){for(let i=0;i<5;i++){box(.19,.23,.012,glass,-.57+i*.28,.47,z,g)}for(const x of [-.63,.33]){box(.19,.46,.014,mat(0xb7c4c8,.3,.3),x,.4,z*1.01,g);box(.12,.19,.017,glass,x,.5,z*1.025,g);box(.009,.41,.019,dark,x,.4,z*1.04,g)}}
for(const x of [-.48,.48])for(const z of [-.22,.22]){const wheel=new T.Mesh(new T.CylinderGeometry(.1,.1,.075,16),dark);wheel.rotation.x=Math.PI/2;wheel.position.set(x,-.01,z);g.add(wheel)}
if(car===2){box(.035,.29,.51,glass,.783,.48,0,g);box(.04,.16,.55,blue,.79,.2,0,g);for(const z of [-.2,.2]){const lamp=box(.035,.06,.095,mat(0xfff0bf),.815,.29,z,g);lamp.material.emissive=new T.Color(0xffe8ad);lamp.material.emissiveIntensity=.5}}else box(.13,.4,.43,dark,.82,.36,0,g);
}
// Station canopy, plants, steps, tiny passengers and red wayfinding elements.
box(2.7,.18,.62,mat(0xe0dcd0),-1.7,1.67,1.15);for(const x of [-2.7,-.65])box(.055,.9,.055,mat(0x62717a),x,2.2,1.22);const roof=box(2.8,.09,.82,mat(0xf0f0e4),-1.7,2.68,1.18);roof.rotation.x=-.07;
for(let i=0;i<3;i++){sphere(.065,mat(0xd4b198),-2.15+i*.43,2.1,1.2);box(.09,.22,.08,i===1?red:blue,-2.15+i*.43,1.94,1.2)}
box(.12,.9,.1,red,2.8,.55,1.28);box(.5,.29,.09,red,2.8,.94,1.28);
for(let i=0;i<6;i++)box(.7,.12,.2,concrete,-3.1,.15+i*.12,.55+i*.17);
const shadow=new T.Mesh(new T.PlaneGeometry(40,40),new T.ShadowMaterial({opacity:.13}));shadow.rotation.x=-Math.PI/2;shadow.position.y=-1.2;shadow.receiveShadow=true;scene.add(shadow);
let pointer={x:0,y:0},running=!matchMedia('(prefers-reduced-motion: reduce)').matches;canvas.addEventListener('pointermove',e=>{const r=canvas.getBoundingClientRect();pointer.x=(e.clientX-r.left)/r.width-.5;pointer.y=(e.clientY-r.top)/r.height-.5});canvas.addEventListener('pointerleave',()=>pointer={x:0,y:0});document.querySelector('#scene-toggle').onclick=e=>{running=!running;e.currentTarget.textContent=running?'Ⅱ':'▶';e.currentTarget.setAttribute('aria-label',running?'หยุดการเคลื่อนไหว':'เล่นการเคลื่อนไหว')};
const detail=enrich(T,world,train,scene,renderer); const city=animateCity(T,world,train,renderer,camera); city.update(8);
function resize(){const r=canvas.parentElement.getBoundingClientRect();renderer.setSize(r.width,r.height,false);camera.aspect=r.width/r.height;camera.updateProjectionMatrix()}new ResizeObserver(resize).observe(canvas.parentElement);resize();let t=0,last=performance.now();function frame(now){requestAnimationFrame(frame);const dt=Math.min((now-last)/1000,.04);last=now;if(running){t+=dt;detail.update(t,dt);city.update(t)}world.rotation.y+=(pointer.x*.15+Math.sin(t*.12)*.025-world.rotation.y)*.025;world.position.y=Math.sin(t*.45)*.025;camera.position.y=9.5+pointer.y*.22;camera.lookAt(0,1,0);renderer.render(scene,camera)}requestAnimationFrame(frame);
function time(){document.querySelector('#bangkok-time').textContent=new Intl.DateTimeFormat('en-GB',{hour:'2-digit',minute:'2-digit',timeZone:'Asia/Bangkok'}).format(new Date())}time();setInterval(time,60000);
