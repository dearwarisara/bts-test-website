import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createJourneyMap,advanceMotion } from '../dist/history-motion.js';

test('unequal chapter heights map continuously, without a stop at each year',()=>{
 const centers=[200,1100,2450,4100,6100],map=createJourneyMap(centers,21,700);
 for(let i=0;i<centers.length;i++){
  assert.ok(Math.abs(map(centers[i])-i*21)<1e-10);
  const epsilon=.01,left=(map(centers[i])-map(centers[i]-epsilon))/epsilon,right=(map(centers[i]+epsilon)-map(centers[i]))/epsilon;
  assert.ok(left>0&&right>0,'train must pass the year without a dwell plateau');
  assert.ok(Math.abs(left-right)<1e-6,'velocity must be continuous at a year boundary');
 }
 for(let p=-499;p<6800;p+=3)assert.ok(map(p+3)>map(p),'the train must not reverse during forward scrolling');
});

test('smoothing has the same result at 30, 60 and 120 fps',()=>{
 const run=fps=>{const state={position:0,velocity:0};for(let i=0;i<fps;i++)advanceMotion(state,120,1/fps);return state;};
 const reference=run(120);
 for(const fps of [30,60]){const state=run(fps);assert.ok(Math.abs(state.position-reference.position)<1e-9);assert.ok(Math.abs(state.velocity-reference.velocity)<1e-9);}
});

test('a jump to another year settles smoothly without overshooting',()=>{
 const state={position:0,velocity:0};let previous=0;
 for(let i=0;i<240;i++){advanceMotion(state,420,1/60);assert.ok(state.position>=previous);assert.ok(state.position<=420);previous=state.position;}
 assert.ok(Math.abs(420-state.position)<1e-7);
});
