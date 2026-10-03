const $=s=>document.querySelector(s),m=$('#m');
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
async function api(u,o){const r=await fetch(u,o);const j=await r.json().catch(()=>({}));if(!r.ok)throw new Error(j.detail||r.status);return j}
const J=(method,b)=>({method,headers:{'Content-Type':'application/json'},body:JSON.stringify(b)});
const key=i=>i.media_type+':'+i.tmdb_id;
const cache={};let mine={};
const fail=e=>{m.innerHTML='<div class="err">'+esc(e.message)+'</div>'};
const loadMine=()=>api('/api/watchlist').then(l=>{mine={};l.forEach(i=>mine[key(i)]=i)}).catch(()=>{});

function card(i){
  cache[key(i)]=i;const st=mine[key(i)]?.status;
  const badge=st==='downloaded'?'<span class="badge dl" title="Descargado">⬇</span>':st?'<span class="badge" title="En tu lista">✓</span>':'';
  const img=i.poster?`<img loading="lazy" src="${esc(i.poster)}" alt="">`:`<div class="noimg">${esc(i.title)}</div>`;
  return `<div class="card" data-k="${esc(key(i))}">${img}<span class="chip ${i.media_type}">${i.media_type==='tv'?'SERIE':'PELÍCULA'}</span>${badge}
  <div class="ov"><span class="y">${esc(i.year)} ${i.rating?'<span class="star">★</span> '+i.rating.toFixed(1):''}</span><span class="t">${esc(i.title)}</span><span class="d">${esc(i.overview)}</span></div></div>`}
const slider=(t,l)=>`<h2>${t}</h2><div class="slider">${l.map(card).join('')||'<div class="empty">Sin resultados</div>'}</div>`;
const grid=l=>l.length?`<div class="grid">${l.map(card).join('')}</div>`:'<div class="empty">Nada por aquí todavía</div>';

m.addEventListener('click',e=>{const c=e.target.closest('.card');if(c)openModal(cache[c.dataset.k])});

const views={
 async discover(){const rows=[['🔥 Tendencias · Películas','trending_movie'],['🔥 Tendencias · Series','trending_tv'],['🎬 Películas populares','popular_movie'],['📺 Series populares','popular_tv'],['🗓️ Próximos estrenos','upcoming']];
  m.innerHTML='<div class="empty">Cargando…</div>';const data=await Promise.all(rows.map(r=>api('/api/discover/'+r[1])));
  m.innerHTML=rows.map((r,n)=>slider(r[0],data[n])).join('')},
 async movies(){m.innerHTML='<h2>Películas populares</h2>'+grid(await api('/api/discover/popular_movie'))},
 async series(){m.innerHTML='<h2>Series populares</h2>'+grid(await api('/api/discover/popular_tv'))},
 async list(){m.innerHTML='<h2>Mi lista</h2>'+grid(await api('/api/watchlist'))},
 calendar:calView, downloads:dl, settings:cfg,
};
let current='discover';
async function go(v){current=v;document.querySelectorAll('#side a').forEach(a=>a.classList.toggle('on',a.dataset.v===v));
  try{await loadMine();await views[v]()}catch(e){fail(e)}}
document.querySelectorAll('#side a').forEach(a=>a.onclick=()=>go(a.dataset.v));
let t;$('#q').oninput=e=>{clearTimeout(t);const v=e.target.value.trim();if(!v){go(current);return}
  t=setTimeout(async()=>{try{await loadMine();const r=await api('/api/search?q='+encodeURIComponent(v));m.innerHTML=`<h2>Resultados para “${esc(v)}”</h2>`+grid(r)}catch(e){fail(e)}},350)};

// ---- modal de detalle ----
const modal=$('#modal'),dlg=$('#dlg');
modal.onclick=e=>{if(e.target===modal)modal.classList.remove('open')};
document.addEventListener('keydown',e=>{if(e.key==='Escape')modal.classList.remove('open')});
let cur,results=[];
async function openModal(i){
  cur=i;modal.classList.add('open');render(i,null);
  try{const d=await api(`/api/details/${i.media_type}/${i.tmdb_id}`);cur={...i,...d};cache[key(i)]=cur;render(cur,d)}catch(e){}
}
function render(i,d){
  const inList=!!mine[key(i)];
  dlg.innerHTML=`<div class="hero" style="background-image:url('${esc(i.backdrop||'')}')"><button class="close" onclick="modal.classList.remove('open')">✕</button>
  <div class="row">${i.poster?`<img class="p" src="${esc(i.poster)}" alt="">`:''}<div><h1>${esc(i.title)} <small style="color:#9ca3af;font-weight:400">${i.year?'('+esc(i.year)+')':''}</small></h1>
  <div class="meta"><span class="chip tv" style="position:static;${i.media_type==='movie'?'background:var(--mov)':''}">${i.media_type==='tv'?'SERIE':'PELÍCULA'}</span>
  ${i.rating?`<span><span class="star">★</span> ${i.rating.toFixed(1)}</span>`:''}${d?.runtime?`<span>${d.runtime} min</span>`:''}</div>
  <div class="tags">${(d?.genres||[]).map(g=>`<span>${esc(g)}</span>`).join('')}</div>
  <button class="btn ${inList?'ok':''}" id="bList" ${inList?'disabled':''}>${inList?'✓ En tu lista':'＋ Añadir a mi lista'}</button>
  <button class="btn sec" id="bTor">🔎 Buscar torrents</button></div></div></div>
  <div class="body">${d?.tagline?`<p><i>${esc(d.tagline)}</i></p>`:''}<p>${esc(i.overview||'Sin sinopsis en castellano.')}</p><div id="tor"></div></div>`;
  $('#bList').onclick=async()=>{try{await api('/api/watchlist',J('POST',i));mine[key(i)]=i;render(i,d);refresh()}catch(e){alert(e.message)}};
  $('#bTor').onclick=()=>torrents(i);
}
const refresh=()=>{if(['discover','movies','series','list'].includes(current)&&!$('#q').value)views[current]().catch(fail)};
async function torrents(i){
  const box=$('#tor');box.innerHTML='<div class="empty">Buscando en fuentes en castellano…</div>';
  try{const r=await api('/api/torrents?q='+encodeURIComponent(i.title)+'&media_type='+i.media_type);results=r.results;
   box.innerHTML=r.errors.map(e=>`<div class="err">${esc(e)}</div>`).join('')+(r.results.length?`<div class="panel"><table><tr><th>Título</th><th>Fuente</th><th>Seeds</th><th></th></tr>${r.results.map((t,k)=>
   `<tr><td>${esc(t.title)} ${t.spanish?'<span class="pill es">ES</span>':''}</td><td>${esc(t.source)}</td><td>${t.seeders}</td><td><button class="btn sm" data-k="${k}">Descargar</button></td></tr>`).join('')}</table></div>`:'<div class="empty">No hay torrents en castellano</div>');
   box.querySelectorAll('button[data-k]').forEach(b=>b.onclick=async()=>{b.disabled=true;b.textContent='Enviando…';
    try{await api('/api/grab',J('POST',results[b.dataset.k]));b.textContent='✓ Enviado'}catch(e){b.disabled=false;b.textContent='Descargar';alert(e.message)}})
  }catch(e){box.innerHTML=`<div class="err">${esc(e.message)}</div>`}
}

// ---- calendario ----
let calMonth=new Date();calMonth.setDate(1);let calEvents=[];
const iso=d=>d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');
async function calView(shift){
  if(typeof shift==='number')calMonth.setMonth(calMonth.getMonth()+shift);
  const y=calMonth.getFullYear(),mo=calMonth.getMonth(),last=new Date(y,mo+1,0).getDate(),today=iso(new Date());
  m.innerHTML='<div class="empty">Cargando…</div>';
  const ev=await api('/api/calendar?start='+iso(calMonth)+'&end='+iso(new Date(y,mo,last)));calEvents=ev;
  const lead=(calMonth.getDay()+6)%7;
  let h=`<h2><button class="btn sec sm" id="cp">◀</button> ${esc(calMonth.toLocaleDateString('es-ES',{month:'long',year:'numeric'}))} <button class="btn sec sm" id="cn">▶</button></h2><div class="cal">`;
  ['L','M','X','J','V','S','D'].forEach(d=>h+=`<div class="h">${d}</div>`);for(let i=0;i<lead;i++)h+='<div></div>';
  for(let d=1;d<=last;d++){const k=iso(new Date(y,mo,d));
   h+=`<div class="day ${k===today?'today':''}"><h6>${d}</h6>${ev.map((e,n)=>e.date===k?`<span class="ev ${e.media_type} ${e.in_list?'mine':''}" data-n="${n}" title="${esc(e.title)}">${esc(e.title)}${e.season?` S${e.season}E${e.episode}`:''}</span>`:'').join('')}</div>`}
  m.innerHTML=h+'</div><p style="color:var(--mut)">Verde = en tu lista · borde azul = película · borde morado = serie</p>';
  $('#cp').onclick=()=>calView(-1).catch(fail);$('#cn').onclick=()=>calView(1).catch(fail);
  m.querySelectorAll('.ev').forEach(el=>el.onclick=()=>{const e=calEvents[el.dataset.n];cache[key(e)]=e;openModal(e)});
}

// ---- descargas ----
async function dl(){
  const l=await api('/api/downloads');
  m.innerHTML='<h2>Download Station</h2>'+(l.length?`<div class="panel"><table><tr><th>Título</th><th>Estado</th><th>Progreso</th><th></th></tr>${l.map(t=>
   `<tr><td>${esc(t.title)}</td><td><span class="pill">${esc(t.status)}</span></td><td><div class="bar"><i style="width:${t.progress}%"></i></div>${t.progress}%</td>
   <td><button class="btn sec sm" data-a="pause" data-id="${esc(t.id)}">⏸</button> <button class="btn sec sm" data-a="resume" data-id="${esc(t.id)}">▶</button> <button class="btn bad sm" data-a="delete" data-id="${esc(t.id)}">🗑</button></td></tr>`).join('')}</table></div>`:'<div class="empty">Sin descargas</div>');
  m.querySelectorAll('button[data-a]').forEach(b=>b.onclick=()=>api('/api/downloads/'+encodeURIComponent(b.dataset.id)+'/'+b.dataset.a,{method:'POST'}).then(dl).catch(fail));
}

// ---- ajustes ----
async function cfg(){
  const s=await api('/api/settings');
  m.innerHTML=`<h2>Ajustes</h2><div class="form panel" style="padding:10px 18px 18px">${Object.keys(s).map(k=>`<label>${esc(k)}</label><input name="${esc(k)}" value="${esc(s[k])}">`).join('')}
  <p><button class="btn" id="sv">Guardar</button> <button class="btn sec" id="vp">Probar proxy VPN</button> <button class="btn sec" id="au">Ejecutar descarga automática</button></p></div>`;
  $('#sv').onclick=()=>{const b={};m.querySelectorAll('input[name]').forEach(i=>b[i.name]=i.value);api('/api/settings',J('PUT',b)).then(()=>alert('Guardado')).catch(e=>alert(e.message))};
  $('#vp').onclick=()=>api('/api/vpn').then(r=>alert('IP vía VPN: '+r.ip+' ('+r.country+')')).catch(e=>alert(e.message));
  $('#au').onclick=()=>api('/api/auto/run',{method:'POST'}).then(r=>alert(JSON.stringify(r))).catch(e=>alert(e.message));
}
go('discover');
