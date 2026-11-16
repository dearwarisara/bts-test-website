const video=document.querySelector('.cover-video');
const toggle=document.querySelector('.cover-video-toggle');
if(video&&toggle){
 const en=document.documentElement.lang==='en';
 const reduced=matchMedia('(prefers-reduced-motion: reduce)');
 function sync(){toggle.textContent=video.paused?'▶':'Ⅱ';toggle.setAttribute('aria-label',en?(video.paused?'Play cover video':'Pause cover video'):(video.paused?'เล่นวิดีโอ cover':'หยุดวิดีโอ cover'));}
 video.addEventListener('play',sync);video.addEventListener('pause',sync);
 toggle.addEventListener('click',()=>{if(video.paused)video.play().catch(sync);else video.pause()});
 if(reduced.matches){video.autoplay=false;video.pause()}
 reduced.addEventListener('change',()=>{if(reduced.matches)video.pause()});
 sync();
}
