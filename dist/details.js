export function enrich(T,world,train,scene,renderer){
 const wheels=[],waterWaves=[],trees=[];
 const material=(color,roughness=.6,metalness=0)=>new T.MeshStandardMaterial({color,roughness,metalness});
 const white=material(0xe4e8e7,.3,.5),steel=material(0x727e88,.3,.8),rubber=material(0x17232d,.85),navy=material(0x163e66,.38,.45),red=material(0xd92d3d,.4,.3),glass=material(0x183440,.12,.5);
 function mesh(geo,mat,x,y,z,parent=world){let a=new T.Mesh(geo,mat);a.position.set(x,y,z);a.castShadow=true;a.receiveShadow=true;parent.add(a);return a}
 function box(w,h,d,m,x,y,z,p){return mesh(new T.BoxGeometry(w,h,d),m,x,y,z,p)}
 function rounded(w,h,d,r,m,x,y,z,p){const s=new T.Shape(),a=w/2,b=h/2;s.moveTo(-a+r,-b);s.lineTo(a-r,-b);s.quadraticCurveTo(a,-b,a,-b+r);s.lineTo(a,b-r);s.quadraticCurveTo(a,b,a-r,b);s.lineTo(-a+r,b);s.quadraticCurveTo(-a,b,-a,b-r);s.lineTo(-a,-b+r);s.quadraticCurveTo(-a,-b,-a+r,-b);const g=new T.ExtrudeGeometry(s,{depth:d,bevelEnabled:true,bevelSize:.012,bevelThickness:.012,bevelSegments:2,steps:1,curveSegments:8});g.translate(0,0,-d/2);return mesh(g,m,x,y,z,p)}
 function textMap(text,color='#cce6c7',bg='#0c1b22'){const c=document.createElement('canvas');c.width=512;c.height=128;const ctx=c.getContext('2d');ctx.fillStyle=bg;ctx.fillRect(0,0,512,128);ctx.fillStyle=color;ctx.font='bold 57px sans-serif';ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText(text,256,66);const t=new T.CanvasTexture(c);t.colorSpace=T.SRGBColorSpace;return new T.MeshStandardMaterial({map:t,emissiveMap:t,emissive:0xffffff,emissiveIntensity:.25,roughness:.4})}
 // Soft studio reflections in the glass and brushed metal.
 const ec=document.createElement('canvas');ec.width=512;ec.height=256;const ex=ec.getContext('2d'),grad=ex.createLinearGradient(0,0,0,256);grad.addColorStop(0,'#d6e4ee');grad.addColorStop(.5,'#faf5e6');grad.addColorStop(1,'#555e60');ex.fillStyle=grad;ex.fillRect(0,0,512,256);ex.fillStyle='#ffffff';ex.fillRect(100,35,70,110);ex.fillRect(350,45,30,85);const env=new T.CanvasTexture(ec);env.mapping=T.EquirectangularReflectionMapping;env.colorSpace=T.SRGBColorSpace;const pm=new T.PMREMGenerator(renderer);scene.environment=pm.fromEquirectangular(env).texture;env.dispose();pm.dispose();
 // Surface variation on earth and concrete, generated locally.
 function grainTexture(a,b,scale){const c=document.createElement('canvas');c.width=c.height=128;const cx=c.getContext('2d');cx.fillStyle=a;cx.fillRect(0,0,128,128);for(let i=0;i<1600;i++){cx.globalAlpha=.1+Math.random()*.2;cx.fillStyle=b;cx.fillRect(Math.random()*128,Math.random()*128,1+Math.random()*2,1+Math.random()*2)}const t=new T.CanvasTexture(c);t.wrapS=t.wrapT=T.RepeatWrapping;t.repeat.set(scale,scale);t.colorSpace=T.SRGBColorSpace;return t}
 const stone=grainTexture('#b7bcba','#7f8582',4),earth=grainTexture('#655e4c','#b0a286',3),grass=grainTexture('#8b9b70','#516b42',6);
 for(const child of world.children){if(!child.isMesh)continue;const d=child.geometry.parameters;if(d.width===7.6&&d.height===.85)child.material=new T.MeshStandardMaterial({map:earth,roughness:1});if(d.width===7.6&&d.height===.16&&d.depth===6.1)child.material=new T.MeshStandardMaterial({map:grass,roughness:1});if(child.material.color?.getHex()===0xc8ccca)child.material=new T.MeshStandardMaterial({map:stone,roughness:.92});}
 // Rebuild the cars with rounded roofs, cab profiles, working bogies and interior detail.
 train.clear();
 for(let n=0;n<3;n++){const car=new T.Group();car.position.x=(n-1)*1.66;train.add(car);
 rounded(1.55,.58,.62,.085,white,0,.39,0,car);rounded(1.5,.08,.57,.035,white,0,.71,0,car);
 box(1.55,.045,.68,red,0,.22,0,car);box(1.55,.063,.685,navy,0,.15,0,car);box(1.28,.1,.4,rubber,0,.035,0,car);
 for(const side of [-1,1]){const z=side*.326;for(let j=0;j<4;j++){const x=-.55+j*.36;rounded(.235,.215,.008,.026,steel,x,.47,z,car);rounded(.209,.188,.011,.02,glass,x,.475,z+side*.006,car);box(.006,.17,.008,steel,x,.47,z+side*.014,car);box(.18,.04,.05,navy,x,.32,side*.22,car)}
 for(const x of [-.32,.4]){rounded(.205,.42,.012,.019,material(0xd0d9db,.4,.55),x,.39,z+side*.014,car);for(const dx of [-.047,.047])rounded(.073,.17,.014,.015,glass,x+dx,.48,z+side*.025,car);box(.008,.39,.018,steel,x,.39,z+side*.026,car);box(.018,.035,.025,rubber,x+.018,.31,z+side*.028,car);box(.21,.014,.04,steel,x,.18,z+side*.01,car)}
 box(1.42,.012,.016,steel,0,.61,z,car);box(1.4,.012,.016,steel,0,.09,z,car);
 // A small carriage identifier and the official BTS emblem.
 const id=mesh(new T.PlaneGeometry(.13,.035),textMap(String(880+n),'#30404c','#e6e8e6'),-.6,.25,z+side*.02,car);if(side===-1)id.rotation.y=Math.PI;
 }
 for(const x of [-.48,.48]){const bogie=new T.Group();bogie.position.set(x,.015,0);car.add(bogie);box(.37,.1,.37,rubber,0,.02,0,bogie);for(const dx of [-.105,.105]){const axle=mesh(new T.CylinderGeometry(.023,.023,.54,12),steel,dx,-.025,0,bogie);axle.rotation.x=Math.PI/2;for(const z of [-.255,.255]){const wheel=mesh(new T.CylinderGeometry(.085,.085,.04,24),steel,dx,-.025,z,bogie);wheel.rotation.x=Math.PI/2;wheels.push(wheel);const hub=mesh(new T.CylinderGeometry(.037,.037,.049,16),rubber,dx,-.025,z,bogie);hub.rotation.x=Math.PI/2;const spring=box(.08,.055,.045,steel,dx,.08,z,bogie);}}}
 // Roof air conditioners, radiator slats and conduit.
 for(const x of [-.42,.35]){rounded(.42,.09,.41,.025,material(0xaeb9bc,.55,.45),x,.79,0,car);for(let k=0;k<8;k++)box(.008,.008,.29,steel,x-.15+k*.043,.846,0,car)}box(1.3,.014,.025,steel,0,.75,.2,car);
 if(n<2){for(let k=0;k<6;k++)rounded(.015,.42,.45,.02,k%2?steel:rubber,.79+k*.013,.36,0,car);box(.2,.05,.1,steel,.85,.06,0,car)}
 if(n===2||n===0){const sign=n===2?1:-1;const nose=new T.Group();nose.position.x=sign*.765;if(sign<0)nose.rotation.y=Math.PI;car.add(nose);
 const shape=new T.Shape();shape.moveTo(-.06,.1);shape.lineTo(.1,.12);shape.lineTo(.16,.25);shape.lineTo(.105,.61);shape.quadraticCurveTo(.08,.68,-.06,.68);shape.closePath();const geo=new T.ExtrudeGeometry(shape,{depth:.58,bevelEnabled:true,bevelSize:.012,bevelThickness:.012,bevelSegments:3});geo.translate(0,0,-.29);mesh(geo,white,0,0,0,nose);
 const windshield=box(.015,.235,.48,glass,.128,.49,0,nose);windshield.rotation.z=.14;box(.018,.018,.48,steel,.145,.355,0,nose);box(.018,.22,.012,steel,.14,.49,0,nose);
 const destination=mesh(new T.PlaneGeometry(.4,.065),textMap('SIAM  ·  BTS'),.105,.63,0,nose);destination.rotation.y=Math.PI/2;
 for(const z of [-.195,.195]){rounded(.024,.057,.104,.008,steel,.155,.275,z,nose);const lamp=box(.027,.034,.075,material(0xfff4cf,.2),.17,.277,z,nose);lamp.material.emissive=new T.Color(0xffe8aa);lamp.material.emissiveIntensity=1.4;const wiper=box(.013,.16,.009,rubber,.151,.45,z*.45,nose);wiper.rotation.x=.35}
 box(.025,.07,.55,navy,.153,.18,0,nose);box(.03,.028,.55,red,.148,.225,0,nose);box(.13,.045,.12,steel,.21,.08,0,nose);
 }
 }
 // Official logo decals on the car side and on the driving cab.
 new T.TextureLoader().load('./assets/bts-logo.svg',texture=>{texture.colorSpace=T.SRGBColorSpace;for(const car of train.children){const m=new T.MeshStandardMaterial({map:texture,transparent:true,roughness:.6});mesh(new T.PlaneGeometry(.095,.12),m,.04,.37,.338,car)}});
 // Guideway safety parapets, cable ducts and warm station lighting.
 const cement=new T.MeshStandardMaterial({map:stone,roughness:.9});for(const z of [-.18,.88]){box(7.5,.15,.055,cement,0,1.85,z);box(7.5,.035,.06,steel,0,1.95,z)}
 for(let x=-3.5;x<3.6;x+=.28)for(const z of [.07,.63])box(.055,.018,.11,steel,x,1.81,z);
 for(const x of [-2.7,-.65]){box(.04,.8,.04,steel,x,2.2,1.5);box(.5,.035,.04,steel,x,2.57,1.23)}
 for(let x=-3;x<-.4;x+=.16){box(.025,.028,.7,steel,x,2.64,1.18);box(.016,.18,.018,steel,x,1.92,1.46)}box(2.65,.022,.025,material(0xe6b746),-1.7,1.78,.85);
 const sign=mesh(new T.PlaneGeometry(.78,.18),textMap('BTS  |  SIAM','#ffffff','#183951'),-1.9,2.38,1.34);sign.castShadow=false;
 // Riverside railing, planting beds, benches and layered ground edges.
 for(let x=-3.65;x<=3.7;x+=.22)box(.018,.2,.018,steel,x,.25,1.52);box(7.5,.018,.018,steel,0,.36,1.52);
 for(const x of [-2.7,2.45]){box(.58,.12,.42,cement,x,.2,1.12);for(let k=0;k<8;k++){const leaf=mesh(new T.SphereGeometry(.1,7,5),material(0x4e7751),x+(Math.random()-.5)*.45,.34+Math.random()*.08,1.12+(Math.random()-.5)*.3);trees.push(leaf)}}
 // Instanced grass avoids thousands of separate draw calls.
 const bladeGeo=new T.ConeGeometry(.016,.13,3),bladeMat=material(0x6d8b4c),blades=new T.InstancedMesh(bladeGeo,bladeMat,1100);const dummy=new T.Object3D();for(let i=0;i<1100;i++){let x=(Math.random()-.5)*7.2,z=-1.5-Math.random()*1.3;dummy.position.set(x,.17+Math.random()*.015,z);dummy.rotation.set((Math.random()-.5)*.4,Math.random()*Math.PI,(Math.random()-.5)*.4);dummy.scale.setScalar(.6+Math.random()*.7);dummy.updateMatrix();blades.setMatrixAt(i,dummy.matrix)}blades.castShadow=false;world.add(blades);
 // Fine water ripples with actual vertex displacement.
 const waterGeo=new T.PlaneGeometry(7.5,1.42,72,20);waterGeo.rotateX(-Math.PI/2);const water=new T.Mesh(waterGeo,new T.MeshPhysicalMaterial({color:0x729eae,metalness:.28,roughness:.17,clearcoat:1,clearcoatRoughness:.2}));water.position.set(0,.17,2.25);water.receiveShadow=true;world.add(water);
 // Remove the previous rigid surface stripes from the river.
 for(const child of [...world.children]){const p=child.geometry?.parameters;if(p?.width===.025&&p?.depth===1.25){world.remove(child);child.geometry.dispose()}}
 return {update(t,dt){const phase=(t%24)/24;const eased=.5-.5*Math.cos(phase*Math.PI*2);train.position.x=-.82+eased*1.25;train.position.y=1.92+Math.sin(t*4)*.0015;for(const w of wheels)w.rotation.y=t*.35;const pos=waterGeo.attributes.position;for(let i=0;i<pos.count;i++){const x=pos.getX(i),z=pos.getZ(i);pos.setY(i,Math.sin(x*3+t*.9)*.009+Math.cos(z*10+t*.65+x)*.005)}pos.needsUpdate=true;waterGeo.computeVertexNormals();for(let i=0;i<trees.length;i++)trees[i].rotation.z=Math.sin(t*.9+i)*.025;}};
}
