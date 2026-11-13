// Monotone Hermite interpolation preserves velocity across year boundaries.
export function createJourneyMap(centers, spacing, lead) {
 const x=[centers[0]-lead,...centers,centers.at(-1)+lead];
 const y=[-8,...centers.map((_,i)=>i*spacing),(centers.length-1)*spacing+8];
 const sec=x.slice(1).map((v,i)=>(y[i+1]-y[i])/(v-x[i]));
 const slopes=x.map((_,i)=>{
  if(i===0)return sec[0];if(i===x.length-1)return sec.at(-1);
  const a=x[i]-x[i-1],b=x[i+1]-x[i],w1=2*b+a,w2=b+2*a;
  return (w1+w2)/(w1/sec[i-1]+w2/sec[i]);
 });
 return value=>{
  if(value<=x[0])return y[0];if(value>=x.at(-1))return y.at(-1);
  let i=0;while(value>x[i+1])i++;
  const h=x[i+1]-x[i],t=(value-x[i])/h,t2=t*t,t3=t2*t;
  return (2*t3-3*t2+1)*y[i]+(t3-2*t2+t)*h*slopes[i]+(-2*t3+3*t2)*y[i+1]+(t3-t2)*h*slopes[i+1];
 };
}

// Exact critically damped integration, independent of refresh rate.
export function advanceMotion(state,target,dt,omega=12) {
 const offset=state.position-target,decay=Math.exp(-omega*dt),term=(state.velocity+omega*offset)*dt;
 state.position=target+(offset+term)*decay;
 state.velocity=(state.velocity-omega*term)*decay;
 return state;
}
