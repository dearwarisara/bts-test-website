export function orbitScene(canvas,world,camera){
 let yaw=0,pitch=0,drag=false,previous=null,pinch=0;const points=new Map();canvas.tabIndex=0;canvas.setAttribute('role','application');canvas.setAttribute('aria-label','โมเดลรถไฟ 360 องศา ลากเพื่อหมุน ใช้สองนิ้วหรือปุ่มบวกลบเพื่อซูม');
 const zoom=delta=>{camera.userData.zoomOverride=Math.max(.65,Math.min(1.9,(camera.userData.zoomOverride??camera.zoom)+delta))};
 function reset(){yaw=0;pitch=0;camera.userData.zoomOverride=1.15}
 document.querySelector('#scene-reset')?.addEventListener('click',reset);
 canvas.addEventListener('pointerdown',e=>{points.set(e.pointerId,{x:e.clientX,y:e.clientY});canvas.setPointerCapture(e.pointerId);drag=true;previous={x:e.clientX,y:e.clientY};canvas.classList.add('is-dragging');if(points.size===2){const p=[...points.values()];pinch=Math.hypot(p[0].x-p[1].x,p[0].y-p[1].y)}});
 canvas.addEventListener('pointermove',e=>{if(!points.has(e.pointerId))return;points.set(e.pointerId,{x:e.clientX,y:e.clientY});if(points.size===2){const p=[...points.values()],distance=Math.hypot(p[0].x-p[1].x,p[0].y-p[1].y);zoom((distance-pinch)*.004);pinch=distance;return}if(previous){yaw+=(e.clientX-previous.x)*.008;pitch=Math.max(-.28,Math.min(.35,pitch+(e.clientY-previous.y)*.003));previous={x:e.clientX,y:e.clientY}}});
 function end(e){points.delete(e.pointerId);if(!points.size){drag=false;previous=null;canvas.classList.remove('is-dragging')}else{previous=[...points.values()][0]}}
 canvas.addEventListener('pointerup',end);canvas.addEventListener('pointercancel',end);canvas.addEventListener('lostpointercapture',end);canvas.addEventListener('wheel',e=>{if(e.ctrlKey||e.metaKey){e.preventDefault();zoom(-e.deltaY*.003)}},{passive:false});
 canvas.addEventListener('keydown',e=>{if(['ArrowLeft','ArrowRight','ArrowUp','ArrowDown','+','-','=','Home'].includes(e.key))e.preventDefault();if(e.key==='ArrowLeft')yaw-=.15;if(e.key==='ArrowRight')yaw+=.15;if(e.key==='ArrowUp')pitch=Math.max(-.28,pitch-.06);if(e.key==='ArrowDown')pitch=Math.min(.35,pitch+.06);if(e.key==='+'||e.key==='=')zoom(.1);if(e.key==='-')zoom(-.1);if(e.key==='Home')reset()});
 return {update(){world.rotation.y+=(yaw-world.rotation.y)*(drag?.3:.09);world.rotation.x+=(pitch-world.rotation.x)*.12}};
}
