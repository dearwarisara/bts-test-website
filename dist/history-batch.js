// Consolidate static geometry while leaving animated actors in their own hierarchy.
export function batchStatic(T,root,keep=new Set()) {
 root.updateWorldMatrix(true,true);
 const inverse=root.matrixWorld.clone().invert(),groups=new Map(),remove=[];
 root.traverse(mesh=>{
  if(!mesh.isMesh||mesh.isInstancedMesh||Array.isArray(mesh.material)||keep.has(mesh))return;
  for(let node=mesh;node&&node!==root;node=node.parent)if(node.userData.animated)return;
  const m=mesh.material;
  const key=[m.type,m.color?.getHex(),m.roughness,m.metalness,m.map?.uuid,m.emissive?.getHex(),m.emissiveIntensity,m.transparent,m.opacity,m.side,mesh.castShadow,mesh.receiveShadow].join(':');
  if(!groups.has(key))groups.set(key,{material:m,parts:[],cast:mesh.castShadow,receive:mesh.receiveShadow});
  const geometry=mesh.geometry.index?mesh.geometry.toNonIndexed():mesh.geometry.clone();
  geometry.applyMatrix4(new T.Matrix4().multiplyMatrices(inverse,mesh.matrixWorld));
  groups.get(key).parts.push(geometry);remove.push(mesh);
 });
 for(const group of groups.values()){
  const count=group.parts.reduce((n,g)=>n+g.attributes.position.count,0),geometry=new T.BufferGeometry();
  for(const [key,size] of [['position',3],['normal',3],['uv',2]]){
   const values=new Float32Array(count*size);let offset=0;
   for(const part of group.parts){const attr=part.attributes[key];if(attr)values.set(attr.array,offset);offset+=part.attributes.position.count*size;}
   geometry.setAttribute(key,new T.BufferAttribute(values,size));
  }
  geometry.computeBoundingSphere();const mesh=new T.Mesh(geometry,group.material);mesh.castShadow=group.cast;mesh.receiveShadow=group.receive;root.add(mesh);
  for(const part of group.parts)part.dispose();
 }
 for(const mesh of remove)mesh.removeFromParent();
}
