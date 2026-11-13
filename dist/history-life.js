export function createLivingScene(T,world,{chapters,end,curvePoint,box,sphere,mat,sign}) {
 const navy=mat(0x203f51),steel=mat(0x667d85,.55,.36),cream=mat(0xe5dfce),red=mat(0xdd3042),glass=mat(0x456a79,.35,.25);
 const lampMaterial=new T.MeshStandardMaterial({color:0xffe8b0,emissive:0xffdfa1,emissiveIntensity:.7,roughness:.5});
 const waterMaterial=new T.MeshPhysicalMaterial({color:0x438d9f,metalness:.24,roughness:.24,clearcoat:.85});
 const boats=[],connections=[],flags=[];
 for(let i=0;i<chapters.length;i++){
  const {g,theme}=chapters[i];
  box(1.1,.12,18,mat(0xc0c8bc),3.0,-.22,0,g);
  for(const z of [-6,1,7]){
   box(.055,2.4,.055,steel,3.1,.95,z,g);box(.58,.045,.06,steel,2.86,2.14,z,g);box(.33,.025,.13,lampMaterial,2.75,2.1,z,g);
  }
  for(const z of [-2,2]){
   box(.25,.055,.6,cream,-2.0,2.0,z,g);for(const dz of [-.22,.22])box(.035,.23,.035,steel,-2.0,1.89,z+dz,g);
   box(.04,.31,.59,navy,-2.12,2.13,z,g);
  }
  // Platform safety screens and balustrades, curb seams and crosswalk paint.
  for(let k=0;k<13;k++){box(.025,.45,.025,steel,-2.59,2.0,-3+k*.5,g);box(.027,.025,.5,steel,-2.59,2.22,-2.75+k*.5,g);}
  for(let k=0;k<7;k++)box(2.9,.012,.12,cream,6.7,-.25,7.1+k*.24,g);
  box(.75,.65,.55,mat(theme<2?0xb89a76:0x668b84),2.5,.1,-4,g);box(.85,.075,.66,red,2.5,.46,-4,g);box(.52,.28,.015,glass,2.5,.24,-3.715,g);
  for(let k=0;k<4;k++)box(.2,.04,.2,cream,2.12+k*.25,-.12,-3.55,g);
  if(i%3===0){
   box(1.55,.035,21,waterMaterial,4.6,-.24,0,g);
   for(const x of [3.8,5.4])box(.09,.18,21,cream,x,-.17,0,g);
   const boat=new T.Group();boat.userData.animated=true;g.add(boat);boat.position.set(4.6,-.15,-3);
   box(.39,.12,.95,cream,0,0,0,boat);box(.31,.2,.58,navy,0,.14,0,boat);box(.43,.035,.65,red,0,.26,0,boat);
   const wake=box(.32,.003,.9,new T.MeshBasicMaterial({color:0xe1f3e8,transparent:true,opacity:.5}),0,-.06,-.9,boat);boats.push({boat,wake,phase:i});
  }
  if(theme>=2){
   const flag=new T.Group();flag.userData.animated=true;flag.position.set(2.9,1.7,3.8);g.add(flag);box(.025,2.2,.025,steel,0,-.6,0,flag);
   const cloth=box(.55,.35,.012,i%2?navy:red,.26,.3,0,flag);flags.push({cloth,phase:i});
  }
  if(theme>=4){
   const rail=new T.Group();rail.position.set(-4,4.04,5);rail.rotation.y=-.5;g.add(rail);
   box(9,.18,.56,cream,0,-.12,0,rail);for(const z of [-.16,.16])box(9,.03,.025,steel,0,.005,z,rail);
   const shuttle=new T.Group();shuttle.userData.animated=true;rail.add(shuttle);
   for(let k=0;k<3;k++){box(.66,.25,.27,cream,(k-1)*.73,.18,0,shuttle);box(.61,.09,.285,glass,(k-1)*.73,.22,0,shuttle);box(.67,.025,.29,i%2?mat(0xd88bab):mat(0xe1bc41),(k-1)*.73,.07,0,shuttle);}
   connections.push({shuttle,phase:i});
  }
  if(theme===1){for(let k=0;k<8;k++){const bar=box(.055,3.4,.055,steel,3.05+k*.3,1.3,2.8,g);bar.rotation.z=k%2?.12:-.12;}for(let k=0;k<6;k++)box(.16,.035,.35,k%2?red:cream,2.7+k*.3,-.1,3.1,g);}
  if(theme===3){box(.85,.09,1.3,navy,2.7,2.65,1,g);sign('BTS  /  CITY',1.25,.31,2.6,2.32,1.67,g);}
 }
 // Instanced vegetation: hundreds of trees sway in one GPU pass per material.
 const count=180,dummy=new T.Object3D(),time={value:0};
 const foliage=new T.MeshStandardMaterial({color:0x587c60,roughness:.86});
 foliage.onBeforeCompile=shader=>{shader.uniforms.historyTime=time;shader.vertexShader='uniform float historyTime;\n'+shader.vertexShader;shader.vertexShader=shader.vertexShader.replace('#include <begin_vertex>','#include <begin_vertex>\n#ifdef USE_INSTANCING\ntransformed.x += sin(historyTime*.85 + instanceMatrix[3].z*.18)*.065*max(position.y+.35,0.0);\n#endif');};
 foliage.customProgramCacheKey=()=> 'history-foliage-v1';
 const crowns=new T.InstancedMesh(new T.IcosahedronGeometry(.48,2),foliage,count),trunks=new T.InstancedMesh(new T.CylinderGeometry(.045,.065,.85,6),mat(0x80684e),count);
 for(let i=0;i<count;i++){
  const z=-18+(end+42)*i/count,p=curvePoint(z),side=i%2?1:-1,s=.75+Math.sin(i*7.3)*.22;
  dummy.position.set(p.x+side*(3.6+(i%3)*.7),.16,z);dummy.scale.set(s,s,s);dummy.rotation.set(0,0,0);dummy.updateMatrix();trunks.setMatrixAt(i,dummy.matrix);
  dummy.position.y=.97*s;dummy.scale.set(s,1.4*s,s);dummy.rotation.y=i;dummy.updateMatrix();crowns.setMatrixAt(i,dummy.matrix);
 }
 crowns.castShadow=true;trunks.castShadow=true;world.add(crowns,trunks);
 return {update(t){time.value=t;for(const {boat,wake,phase} of boats){boat.position.z=Math.sin(t*.1+phase)*7;boat.position.y=-.14+Math.sin(t*1.2+phase)*.012;boat.rotation.y=Math.cos(t*.1+phase)<0?Math.PI:0;wake.scale.z=1+Math.sin(t*2.5)*.12;}for(const {shuttle,phase} of connections)shuttle.position.x=Math.sin(t*.2+phase)*3.1;for(const {cloth,phase} of flags)cloth.rotation.y=Math.sin(t*1.8+phase)*.15;}};
}
