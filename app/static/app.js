const $=s=>document.querySelector(s),m=$('#m');
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const P={
 logo:'<polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/>',
 compass:'<circle cx="12" cy="12" r="10"/><polygon points="16.2 7.8 14.1 14.1 7.8 16.2 9.9 9.9 16.2 7.8"/>',
 film:'<rect x="2" y="2" width="20" height="20" rx="2.2"/><path d="M7 2v20M17 2v20M2 12h20M2 7h5M2 17h5M17 17h5M17 7h5"/>',
 tv:'<rect x="2" y="7" width="20" height="15" rx="2"/><polyline points="17 2 12 7 7 2"/>',
 calendar:'<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/>',
 bookmark:'<path d="m19 21-7-4-7 4V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v16z"/>',
 download:'<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>',
 settings:'<line x1="4" y1="21" x2="4" y2="14"/><line x1="4" y1="10" x2="4" y2="3"/><line x1="12" y1="21" x2="12" y2="12"/><line x1="12" y1="8" x2="12" y2="3"/><line x1="20" y1="21" x2="20" y2="16"/><line x1="20" y1="12" x2="20" y2="3"/><line x1="1" y1="14" x2="7" y2="14"/><line x1="9" y1="8" x2="15" y2="8"/><line x1="17" y1="16" x2="23" y2="16"/>',
 search:'<circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>',
 check:'<polyline points="20 6 9 17 4 12"/>',plus:'<line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>',
 x:'<line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>',
 pause:'<rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/>',play:'<polygon points="6 3 20 12 6 21 6 3"/>',
 trash:'<polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6M14 11v6"/><path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/>',
 logout:'<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/>',
 star:'<polygon points="12 2 15.1 8.3 22 9.3 17 14.1 18.2 21 12 17.8 5.8 21 7 14.1 2 9.3 8.9 8.3 12 2"/>',
 trend:'<polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/>',
 clock:'<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
 left:'<polyline points="15 18 9 12 15 6"/>',right:'<polyline points="9 18 15 12 9 6"/>',
 server:'<rect x="2" y="2" width="20" height="8" rx="2"/><rect x="2" y="14" width="20" height="8" rx="2"/><line x1="6" y1="6" x2="6.01" y2="6"/><line x1="6" y1="18" x2="6.01" y2="18"/>',
 shield:'<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>',
 globe:'<circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15 15 0 0 1 4 10 15 15 0 0 1-4 10 15 15 0 0 1-4-10 15 15 0 0 1 4-10z"/>',
 refresh:'<polyline points="23 4 23 10 17 10"/><path d="M20.5 15a9 9 0 1 1-2.1-9.4L23 10"/>',
 user:'<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>',
 edit:'<path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4z"/>',
 image:'<rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/>',
 key:'<path d="M21 2l-2 2m-7.6 7.6a5.5 5.5 0 1 1-7.8 7.8 5.5 5.5 0 0 1 7.8-7.8zm0 0L15.5 7.5m0 0l3 3L22 7l-3-3m-3.5 3.5L19 4"/>',
};
const ic=(n,c='')=>`<svg class="ic ${c}" viewBox="0 0 24 24" aria-hidden="true">${P[n]}</svg>`;
const STATUS={waiting:'En espera',downloading:'Descargando',paused:'En pausa',finishing:'Finalizando',finished:'Completada',hash_checking:'Comprobando',seeding:'Compartiendo',filehosting_waiting:'En espera',extracting:'Extrayendo',error:'Error'};

async function api(u,o){const r=await fetch(u,o);const j=await r.json().catch(()=>({}));
  if(r.status===401&&!u.startsWith('/api/auth/'))boot();
  if(!r.ok)throw new Error(j.detail||('Error '+r.status));return j}
const J=(method,b)=>({method,headers:{'Content-Type':'application/json'},body:JSON.stringify(b)});
function toast(t,bad){const d=document.createElement('div');d.className='toast'+(bad?' bad':'');d.textContent=t;document.body.appendChild(d);setTimeout(()=>d.remove(),3500)}
const fail=e=>{m.innerHTML='<div class="err">'+esc(e.message)+'</div>'};

// ---------- sesión ----------
const authBox=$('#auth'),appBox=$('#app');
async function boot(){
  const s=await fetch('/api/auth/status').then(r=>r.json());
  if(s.authenticated){authBox.hidden=true;appBox.hidden=false;$('#who').textContent=s.username;startApp();return}
  appBox.hidden=true;authBox.hidden=false;
  const setup=s.setup_needed;
  authBox.innerHTML=`<form class="authbox" id="af"><div class="brand">${ic('logo')}<span>media-server-utility</span></div>
  <p class="sub">${setup?'Crea la cuenta de administrador para empezar':'Inicia sesión para continuar'}</p>
  <label for="u">Usuario</label><input id="u" autocomplete="username" required autofocus>
  <label for="p">Contraseña${setup?' (mínimo 8 caracteres)':''}</label><input id="p" type="password" autocomplete="${setup?'new-password':'current-password'}" required minlength="${setup?8:1}">
  ${setup?'<label for="p2">Repite la contraseña</label><input id="p2" type="password" autocomplete="new-password" required>':''}
  <div class="err" id="ae" hidden></div><button class="btn" type="submit">${setup?'Crear cuenta':'Iniciar sesión'}</button></form>`;
  $('#af').onsubmit=async e=>{e.preventDefault();const er=$('#ae');er.hidden=true;
    if(setup&&$('#p').value!==$('#p2').value){er.textContent='Las contraseñas no coinciden';er.hidden=false;return}
    try{await api(setup?'/api/auth/setup':'/api/auth/login',J('POST',{username:$('#u').value,password:$('#p').value}));boot()}
    catch(x){er.textContent=x.message;er.hidden=false}};
}
$('#logout').innerHTML=ic('logout');$('#logout').onclick=()=>api('/api/auth/logout',{method:'POST'}).then(boot);
$('#logout').style.cursor='pointer';$('#logo').innerHTML=ic('logo')+'<span>media-server-utility</span>';

// ---------- aplicación ----------
const key=i=>i.media_type+':'+(i.tmdb_id??'f:'+i.folder);
const cache={};let mine={};
const loadMine=()=>api('/api/watchlist').then(l=>{mine={};l.forEach(i=>mine[key(i)]=i)}).catch(()=>{});
const NAV=[['discover','compass','Descubrir'],['movies','film','Películas'],['series','tv','Series'],['calendar','calendar','Calendario'],['list','bookmark','Mi lista'],['downloads','download','Descargas'],['settings','settings','Ajustes']];
$('#menu').innerHTML=NAV.map(n=>`<a data-v="${n[0]}">${ic(n[1])}${n[2]}</a>`).join('');

function card(i){
  cache[key(i)]=i;const st=mine[key(i)]?.status;
  const badge=st==='downloaded'?`<span class="badge dl" title="Descargada">${ic('download')}</span>`:st?`<span class="badge" title="En tu lista">${ic('check')}</span>`:'';
  const img=i.poster?`<img loading="lazy" src="${esc(i.poster)}" alt="">`:`<div class="noimg">${esc(i.title)}</div>`;
  return `<div class="card" data-k="${esc(key(i))}">${img}<span class="chip ${i.media_type}">${i.media_type==='tv'?'SERIE':'PELÍCULA'}</span>${badge}
  <div class="ov"><span class="y">${esc(i.year)} ${i.rating?`<span class="star">${ic('star','fill')}</span> ${i.rating.toFixed(1).replace('.',',')}`:''}</span><span class="t">${esc(i.title)}</span><span class="d">${esc(i.overview)}</span></div></div>`}
const slider=(t,icn,l)=>`<h2>${ic(icn)}${t}</h2><div class="slider">${l.map(card).join('')||'<div class="empty">Sin resultados</div>'}</div>`;
const grid=l=>l.length?`<div class="grid">${l.map(card).join('')}</div>`:'<div class="empty">No hay nada todavía</div>';
m.addEventListener('click',e=>{const fb=e.target.closest('.fixb');if(fb){e.stopPropagation();fb.dataset.poster?posterDialog(fb.dataset.poster,fb.dataset.f):fixDialog(fb.dataset.fix,fb.dataset.f);return}const c=e.target.closest('.card');const i=c&&cache[c.dataset.k];if(i&&i.tmdb_id)openModal(i)});

const views={
 async discover(){const rows=[['Tendencias · Películas','trend','trending_movie'],['Tendencias · Series','trend','trending_tv'],['Películas populares','film','popular_movie'],['Series populares','tv','popular_tv'],['Próximos estrenos','clock','upcoming']];
  m.innerHTML='<div class="empty">Cargando…</div>';const data=await Promise.all(rows.map(r=>api('/api/discover/'+r[2])));
  m.innerHTML=rows.map((r,n)=>slider(r[0],r[1],data[n])).join('')},
 async movies(){await lib('Películas','film',[['movies','Películas'],['movies_anim','Películas de animación']])},
 async series(){await lib('Series','tv',[['series','Series'],['series_anim','Series de animación']])},
 async list(){m.innerHTML=`<h2>${ic('bookmark')}Mi lista</h2>`+grid(await api('/api/watchlist'))},
 calendar:calView,downloads:dl,settings:cfg};
let LS={};
const flt=()=>localStorage.getItem('libFilter')||'all';
async function lib(title,icn,kinds){
  m.innerHTML='<div class="empty">Leyendo biblioteca…</div>';
  const mv=kinds[0][0].startsWith('movies'),cfgs=await api('/api/settings'),group=mv&&cfgs.group_sagas==='1';
  const data=await Promise.all(kinds.map(k=>api('/api/library/'+k[0]+(group?'?collections=1':''))));
  LS={title,icn,kinds,data,s:cfgs,mv,group};libRender();
}
function libCard(k,i){
  const btn=`<button class="fixb" data-fix="${esc(k)}" data-f="${esc(i.folder)}" title="Corregir identificación">${ic('edit')}</button>`+
   (i.tmdb_id?`<button class="fixb p" data-poster="${esc(k)}" data-f="${esc(i.folder)}" title="Elegir carátula">${ic('image')}</button>`:'');
  return card(i).replace('<div class="ov">',btn+'<div class="ov">');
}
function libSection(k,list,mv,group){
  if(!list.length)return '<div class="empty">Sin contenido. Configura la ruta en Ajustes → Bibliotecas.</div>';
  const cells=l=>`<div class="grid">${l.map(i=>libCard(k,i)).join('')}</div>`;
  if(!group)return cells(list);
  const by={};list.forEach(i=>{const n=i.collection?.name||'';(by[n]=by[n]||[]).push(i)});
  const names=Object.keys(by).filter(Boolean).sort((x,y)=>x.localeCompare(y,'es'));
  return names.map(n=>`<h3 class="saga">${esc(n)} <small>(${by[n].length})</small></h3>`+cells(by[n])).join('')+
   (by['']?(names.length?'<h3 class="saga">Sin saga</h3>':'')+cells(by['']):'');
}
function libRender(){
  const {title,icn,kinds,data,mv,group}=LS,f=flt();
  const bar=`<div class="toolbar"><div class="seg">${[['all','Todo'],['normal','Normales'],['anim','Animación']].map(x=>`<button class="${f===x[0]?'on':''}" data-flt="${x[0]}">${x[1]}</button>`).join('')}</div>
   ${mv?`<label class="chk"><input type="checkbox" id="gs" ${group?'checked':''}> Agrupar sagas</label>`:''}
   <button class="btn sec sm" id="rn">${ic('edit')}Renombrar</button></div>`;
  m.innerHTML=`<h2>${ic(icn)}${title}</h2>${bar}`+kinds.map((k,n)=>(f==='normal'&&n!==0)||(f==='anim'&&n!==1)?'':
   `<h2 class="sub">${k[1]} <small>(${data[n].length})</small></h2>`+libSection(k[0],data[n],mv,group)).join('');
  m.querySelectorAll('[data-flt]').forEach(b=>b.onclick=()=>{localStorage.setItem('libFilter',b.dataset.flt);libRender()});
  const gs=$('#gs');if(gs)gs.onchange=async()=>{try{await api('/api/settings',J('PUT',{group_sagas:gs.checked?'1':'0'}));lib(title,icn,kinds)}catch(e){toast(e.message,1)}};
  $('#rn').onclick=renameDialog;
}
let current='discover',started=false;
async function go(v){current=v;$('#q').value='';document.querySelectorAll('#menu a').forEach(a=>a.classList.toggle('on',a.dataset.v===v));
  try{await loadMine();await views[v]()}catch(e){fail(e)}}
function startApp(){if(started){go(current);return}started=true;
  document.querySelectorAll('#menu a').forEach(a=>a.onclick=()=>go(a.dataset.v));go('discover')}
let t;$('#q').oninput=e=>{clearTimeout(t);const v=e.target.value.trim();if(!v){go(current);return}
  t=setTimeout(async()=>{try{await loadMine();const r=await api('/api/search?q='+encodeURIComponent(v));m.innerHTML=`<h2>${ic('search')}Resultados para «${esc(v)}»</h2>`+grid(r)}catch(e){fail(e)}},350)};

// ---------- corregir identificación ----------
function fixDialog(kind,folder){
  const mt=kind.startsWith('series')?'tv':'movie';
  const ov=document.createElement('div');ov.className='open';ov.id='bro';document.body.appendChild(ov);
  ov.innerHTML=`<div class="dlg"><div class="body"><h3>Corregir identificación</h3><p><code>${esc(folder)}</code></p>
   <div class="actions"><input id="fq" value="${esc(folder.replace(/[._]/g,' ').replace(/\s*[\(\[]?(19|20)\d{2}.*$/,'').trim())}"><button class="btn" id="fgo">${ic('search')}Buscar</button></div>
   <div id="fres" class="panel"></div><div class="actions"><button class="btn sec" id="frs">Restablecer automático</button><button class="btn sec" id="fcl">Cancelar</button></div></div></div>`;
  const done=()=>{ov.remove();views[current]().catch(fail)};
  const send=async id=>{try{await api('/api/library/'+kind+'/fix',J('POST',{folder,tmdb_id:id}));done()}catch(e){toast(e.message,1)}};
  const go=async()=>{const q=$('#fq').value.trim();if(!q)return;$('#fres').innerHTML='<div class="empty">Buscando…</div>';
   try{const r=(await api('/api/search?q='+encodeURIComponent(q))).filter(x=>x.media_type===mt);
    $('#fres').innerHTML=r.length?`<table>${r.map(x=>`<tr><td>${x.poster?`<img src="${esc(x.poster)}" width="40" alt="">`:''}</td><td>${esc(x.title)} <small>${esc(x.year)}</small><br><small>${esc((x.overview||'').slice(0,110))}</small></td><td><button class="btn sm" data-id="${x.tmdb_id}">Elegir</button></td></tr>`).join('')}</table>`:'<div class="empty">Sin resultados</div>';
    $('#fres').querySelectorAll('[data-id]').forEach(b=>b.onclick=()=>send(+b.dataset.id))}catch(e){$('#fres').innerHTML=`<div class="err">${esc(e.message)}</div>`}};
  $('#fgo').onclick=go;$('#fq').onkeydown=e=>{if(e.key==='Enter')go()};$('#frs').onclick=()=>send(null);$('#fcl').onclick=()=>ov.remove();go();
}

// ---------- carátulas ----------
async function posterDialog(kind,folder){
  const item=LS.data.flat().find(i=>i.folder===folder);if(!item)return;
  const ov=document.createElement('div');ov.className='open';ov.id='bro';document.body.appendChild(ov);
  ov.innerHTML=`<div class="dlg wide"><div class="body"><h3>Elegir carátula</h3><p>${esc(item.title)} <small>${esc(item.year)}</small></p>
   <label class="chk"><input type="checkbox" id="pf"> Guardar también como <code>poster.jpg</code> en la carpeta</label>
   <div id="pl" class="posters"><div class="empty">Cargando…</div></div><div class="actions"><button class="btn sec" id="pc">Cerrar</button></div></div></div>`;
  $('#pc').onclick=()=>ov.remove();
  try{const l=await api(`/api/posters/${item.media_type}/${item.tmdb_id}`);
   $('#pl').innerHTML=l.length?l.map((p,n)=>`<figure data-n="${n}"><img loading="lazy" src="${esc(p.poster)}" alt=""><figcaption>${esc(p.lang||'sin texto')}</figcaption></figure>`).join(''):'<div class="empty">Sin carátulas disponibles</div>';
   $('#pl').querySelectorAll('figure').forEach(f=>f.onclick=async()=>{const p=l[f.dataset.n];
    try{const r=await api(`/api/library/${kind}/poster`,J('POST',{folder,poster:p.poster,full:p.full,save_file:$('#pf').checked}));
     toast(r.saved_file===false?'Carátula elegida, pero no se pudo guardar poster.jpg (¿solo lectura?)':'Carátula actualizada',r.saved_file===false);ov.remove();lib(LS.title,LS.icn,LS.kinds)}catch(e){toast(e.message,1)}})
  }catch(e){$('#pl').innerHTML=`<div class="err">${esc(e.message)}</div>`}
}

// ---------- renombrar ----------
function renameDialog(){
  const f=flt(),kinds=LS.kinds.filter((k,n)=>!((f==='normal'&&n!==0)||(f==='anim'&&n!==1))).map(k=>k[0]);
  const ov=document.createElement('div');ov.className='open';ov.id='bro';document.body.appendChild(ov);
  ov.innerHTML=`<div class="dlg wide"><div class="body"><h3>Renombrar ${esc(LS.title.toLowerCase())}</h3>
   <p class="desc">Renombra carpetas y archivos a «Título (Año)» en castellano. En series, los episodios pasan a «Título - S01E02». Revisa la vista previa antes de aplicar.</p>
   <label for="rp">Fuente de los títulos</label><select id="rp"><option value="tmdb">TheMovieDB</option><option value="tvdb">TheTVDB</option></select>
   ${LS.mv?`<label class="chk"><input type="checkbox" id="rg" ${LS.s.group_sagas==='1'?'checked':''}> Mover las películas a carpetas de saga («Nombre (Saga)»)</label>`:''}
   <div class="actions"><button class="btn" id="rv">${ic('search')}Vista previa</button><button class="btn sec" id="rc">Cerrar</button></div><div id="rr"></div></div></div>`;
  $('#rp').value=LS.s.rename_provider||'tmdb';$('#rc').onclick=()=>ov.remove();
  const body=(extra={})=>({kinds,provider:$('#rp').value,group_sagas:!!$('#rg')?.checked,...extra});
  $('#rv').onclick=async()=>{const box=$('#rr');box.innerHTML='<div class="empty">Calculando…</div>';
    try{const {entries}=await api('/api/library/rename',J('POST',body()));
     const LBL={unidentified:'Sin identificar',conflict:'Ya existe el destino',error:'Error'};
     const ch=entries.filter(e=>e.status!=='same');
     box.innerHTML=ch.length?`<div class="panel"><table>${ch.map(e=>`<tr><td>${e.status==='ok'?`<input type="checkbox" class="rk" checked data-k="${esc(e.kind+'|'+e.folder)}">`:''}</td>
       <td>${esc(e.folder)}${e.new!==e.folder?`<br>→ <b>${esc(e.new)}</b>`:''}${e.episodes.length?`<br><small>${e.episodes.filter(x=>!x.conflict).length} episodio(s) a renombrar</small>`:''}</td>
       <td>${e.status==='ok'?'':`<span class="pill">${esc(LBL[e.status])}</span>`}${e.error?`<br><small>${esc(e.error)}</small>`:''}</td></tr>`).join('')}</table></div>
       <div class="actions"><button class="btn" id="ra">${ic('check')}Aplicar a los seleccionados</button></div>`:'<div class="empty">Todo está ya con el nombre correcto</div>';
     const ra=$('#ra');if(ra)ra.onclick=async()=>{ra.disabled=true;
      const only=[...box.querySelectorAll('.rk:checked')].map(x=>x.dataset.k);
      try{const {results}=await api('/api/library/rename',J('POST',body({apply:true,only})));
       const bad=results.filter(r=>!r.ok);
       box.innerHTML=`<div class="${bad.length?'err':'empty'}">${results.length-bad.length} renombrado(s)${bad.length?` · ${bad.length} con error:<br>${bad.map(r=>esc(r.folder)+': '+esc(r.error)).join('<br>')}`:''}</div>`;
       lib(LS.title,LS.icn,LS.kinds)}catch(e){ra.disabled=false;toast(e.message,1)}}
    }catch(e){box.innerHTML=`<div class="err">${esc(e.message)}</div>`}};
}

// ---------- ficha ----------
const modal=$('#modal'),dlg=$('#dlg'),closeModal=()=>modal.classList.remove('open');
modal.onclick=e=>{if(e.target===modal)closeModal()};document.addEventListener('keydown',e=>{if(e.key==='Escape')closeModal()});
let cur,results=[];
async function openModal(i){cur=i;modal.classList.add('open');render(i,null);
  try{const d=await api(`/api/details/${i.media_type}/${i.tmdb_id}`);cur={...i,...d};cache[key(i)]=cur;render(cur,d)}catch(e){}}
function render(i,d){
  const inList=!!mine[key(i)];
  dlg.innerHTML=`<div class="hero" style="background-image:url('${esc(i.backdrop||'')}')"><button class="close" id="cl" aria-label="Cerrar">${ic('x')}</button>
  <div class="row">${i.poster?`<img class="p" src="${esc(i.poster)}" alt="">`:''}<div><h1>${esc(i.title)} <small style="color:#9ca3af;font-weight:400">${i.year?'('+esc(i.year)+')':''}</small></h1>
  <div class="meta"><span class="chip ${i.media_type}" style="position:static">${i.media_type==='tv'?'SERIE':'PELÍCULA'}</span>
  ${i.rating?`<span><span class="star">${ic('star','fill')}</span> ${i.rating.toFixed(1).replace('.',',')}</span>`:''}${d?.runtime?`<span>${d.runtime} min</span>`:''}</div>
  <div class="tags">${(d?.genres||[]).map(g=>`<span>${esc(g)}</span>`).join('')}</div>
  <button class="btn ${inList?'ok':''}" id="bList" ${inList?'disabled':''}>${ic(inList?'check':'plus')}${inList?'En tu lista':'Añadir a mi lista'}</button>
  <button class="btn sec" id="bTor">${ic('search')}Buscar torrents</button></div></div></div>
  <div class="body">${d?.tagline?`<p><i>${esc(d.tagline)}</i></p>`:''}<p>${esc(i.overview||'Sin sinopsis en castellano.')}</p><div id="tor"></div></div>`;
  $('#cl').onclick=closeModal;
  $('#bList').onclick=async()=>{try{await api('/api/watchlist',J('POST',i));mine[key(i)]=i;render(i,d);if(['discover','movies','series','list'].includes(current)&&!$('#q').value)views[current]().catch(fail)}catch(e){toast(e.message,1)}};
  $('#bTor').onclick=()=>torrents(i);
}
async function torrents(i){
  const box=$('#tor');box.innerHTML='<div class="empty">Buscando en fuentes en castellano…</div>';
  try{const r=await api('/api/torrents?q='+encodeURIComponent(i.title)+'&media_type='+i.media_type);results=r.results;
   box.innerHTML=r.errors.map(e=>`<div class="err">${esc(e)}</div>`).join('')+(r.results.length?`<div class="panel"><table><tr><th>Título</th><th>Fuente</th><th>Semillas</th><th></th></tr>${r.results.map((x,k)=>
   `<tr><td>${esc(x.title)} ${x.spanish?'<span class="pill es">ES</span>':''}</td><td>${esc(x.source)}</td><td>${x.seeders}</td><td><button class="btn sm" data-k="${k}">${ic('download')}Descargar</button></td></tr>`).join('')}</table></div>`:'<div class="empty">No se han encontrado torrents en castellano</div>');
   box.querySelectorAll('button[data-k]').forEach(b=>b.onclick=async()=>{b.disabled=true;
    try{await api('/api/grab',J('POST',results[b.dataset.k]));b.innerHTML=ic('check')+'Enviado';toast('Enviado a Download Station')}catch(e){b.disabled=false;toast(e.message,1)}})
  }catch(e){box.innerHTML=`<div class="err">${esc(e.message)}</div>`}
}

// ---------- calendario ----------
let calMonth=new Date();calMonth.setDate(1);let calEvents=[];
const iso=d=>d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');
async function calView(shift){
  if(typeof shift==='number')calMonth.setMonth(calMonth.getMonth()+shift);
  const y=calMonth.getFullYear(),mo=calMonth.getMonth(),last=new Date(y,mo+1,0).getDate(),today=iso(new Date());
  m.innerHTML='<div class="empty">Cargando…</div>';
  const ev=await api('/api/calendar?start='+iso(calMonth)+'&end='+iso(new Date(y,mo,last)));calEvents=ev;
  const lead=(calMonth.getDay()+6)%7;
  let h=`<h2><button class="btn sec sm" id="cp" aria-label="Mes anterior">${ic('left')}</button> ${esc(calMonth.toLocaleDateString('es-ES',{month:'long',year:'numeric'}))} <button class="btn sec sm" id="cn" aria-label="Mes siguiente">${ic('right')}</button></h2><div class="cal">`;
  ['L','M','X','J','V','S','D'].forEach(d=>h+=`<div class="h">${d}</div>`);for(let i=0;i<lead;i++)h+='<div></div>';
  for(let d=1;d<=last;d++){const k=iso(new Date(y,mo,d));
   h+=`<div class="day ${k===today?'today':''}"><h6>${d}</h6>${ev.map((e,n)=>e.date===k?`<span class="ev ${e.media_type} ${e.in_list?'mine':''}" data-n="${n}" title="${esc(e.title)}">${esc(e.title)}${e.season?` T${e.season}x${String(e.episode).padStart(2,'0')}`:''}</span>`:'').join('')}</div>`}
  m.innerHTML=h+'</div><p style="color:var(--mut)">Fondo verde: en tu lista · borde azul: película · borde morado: serie</p>';
  $('#cp').onclick=()=>calView(-1).catch(fail);$('#cn').onclick=()=>calView(1).catch(fail);
  m.querySelectorAll('.ev').forEach(el=>el.onclick=()=>{const e=calEvents[el.dataset.n];cache[key(e)]=e;openModal(e)});
}

// ---------- descargas ----------
const fmtSpeed=b=>b?(b/1048576).toFixed(1).replace('.',',')+' MB/s':'';
async function dl(){
  const l=await api('/api/downloads');
  m.innerHTML=`<h2>${ic('download')}Download Station</h2>`+(l.length?`<div class="panel"><table><tr><th>Título</th><th>Estado</th><th>Progreso</th><th></th></tr>${l.map(x=>
   `<tr><td>${esc(x.title)}</td><td><span class="pill">${esc(STATUS[x.status]||x.status)}</span></td><td><div class="bar"><i style="width:${x.progress}%"></i></div>${String(x.progress).replace('.',',')} % ${fmtSpeed(x.speed)}</td>
   <td><button class="btn sec sm" data-a="pause" data-id="${esc(x.id)}" title="Pausar">${ic('pause')}</button> <button class="btn sec sm" data-a="resume" data-id="${esc(x.id)}" title="Reanudar">${ic('play')}</button> <button class="btn bad sm" data-a="delete" data-id="${esc(x.id)}" title="Eliminar">${ic('trash')}</button></td></tr>`).join('')}</table></div>`:'<div class="empty">No hay descargas visibles para el usuario configurado en Ajustes → Download Station</div>');
  m.querySelectorAll('button[data-a]').forEach(b=>b.onclick=()=>api('/api/downloads/'+encodeURIComponent(b.dataset.id)+'/'+b.dataset.a,{method:'POST'}).then(dl).catch(e=>toast(e.message,1)));
}

// ---------- ajustes ----------
const SECTIONS=[
 {icon:'globe',title:'Metadatos (TMDB)',desc:'Información de películas y series en castellano (es-ES). Necesitas una clave API gratuita de themoviedb.org.',test:'tmdb',
  fields:[['tmdb_api_key','Clave API de TMDB','password','Ajustes de tu cuenta de TMDB → API']]},
 {icon:'search',title:'Jackett (fuente de torrents)',desc:'Tu JackettVPN con el indexador Wolfmax4k. Solo se muestran resultados en castellano. Mantén Jackett actualizado: Wolfmax4k cambia a menudo.',test:'torznab',
  fields:[['torznab_url','URL Torznab','text','Ej.: http://IP_NAS:9117/api/v2.0/indexers/all/results/torznab/api'],['torznab_apikey','Clave API de Jackett','password','Arriba a la derecha en el panel de Jackett']]},
 {icon:'image',title:'Renombrado y carátulas',desc:'Fuente de los títulos al renombrar (siempre en castellano) y agrupación de sagas. TheTVDB necesita una clave API gratuita de thetvdb.com; las carátulas se eligen siempre entre las de TMDB.',test:'tvdb',
  fields:[['tvdb_api_key','Clave API de TheTVDB','password','Opcional: solo si renombras con TheTVDB'],['rename_provider','Fuente por defecto','select','',[['tmdb','TheMovieDB'],['tvdb','TheTVDB']]],['group_sagas','Agrupar sagas de películas','select','Muestra las sagas juntas en Películas y, al renombrar, las mueve a carpetas «(Saga)»',[['0','No'],['1','Sí']]]]},
 {icon:'server',title:'Download Station (XPEnology / Synology)',desc:'Usa un usuario de DSM con permiso para Download Station y sin verificación en dos pasos.',test:'ds',
  fields:[['ds_url','URL de DSM','text','Ej.: http://192.168.1.10:5000'],['ds_user','Usuario','text',''],['ds_password','Contraseña','password',''],['ds_destination','Carpeta de destino','text','Carpeta compartida, p. ej. video/peliculas. Vacío = la predeterminada']]},
 {icon:'film',title:'Bibliotecas',desc:'Rutas de las carpetas del NAS tal como las ve el contenedor (por ejemplo /media/peliculas). Cada tipo va en su propia carpeta.',test:'library',
  fields:[['lib_movies','Películas','text','/media/peliculas'],['lib_movies_anim','Películas de animación','text','/media/peliculas-animacion'],['lib_series','Series','text','/media/series'],['lib_series_anim','Series de animación','text','/media/series-animacion']]},
 {icon:'refresh',title:'Descarga automática',desc:'Revisa tu lista y envía a Download Station los estrenos y episodios nuevos.',
  fields:[['auto_interval_min','Frecuencia de revisión (minutos)','number','Mínimo 5']],extra:'auto'},
];
async function browse(input){
  const ov=document.createElement('div');ov.className='open';ov.id='bro';document.body.appendChild(ov);
  const load=async p=>{try{const d=await api('/api/browse?path='+encodeURIComponent(p));
    ov.innerHTML=`<div class="dlg"><div class="body"><h3>Elegir carpeta</h3><p><code>${esc(d.path)}</code></p><div class="panel"><table>${d.parent?`<tr><td><a data-p="${esc(d.parent)}" style="cursor:pointer">${ic('left')} Subir</a></td></tr>`:''}${d.dirs.map(n=>`<tr><td><a data-p="${esc(d.path.replace(/\/$/,'')+'/'+n)}" style="cursor:pointer">${esc(n)}</a></td></tr>`).join('')||'<tr><td>Sin subcarpetas</td></tr>'}</table></div>
    <div class="actions"><button class="btn" id="bsel">Seleccionar esta carpeta</button><button class="btn sec" id="bcan">Cancelar</button></div></div></div>`;
    ov.querySelectorAll('[data-p]').forEach(a=>a.onclick=()=>load(a.dataset.p));
    $('#bsel').onclick=()=>{input.value=d.path;ov.remove()};$('#bcan').onclick=()=>ov.remove()}catch(e){toast(e.message,1);if(p!=='/')load('/');else ov.remove()}};
  load(input.value||'/media');
}
async function cfg(){
  const s=await api('/api/settings');
  m.innerHTML=`<h2>${ic('settings')}Ajustes</h2>`+SECTIONS.map((sec,n)=>`<form class="sect form" data-n="${n}"><h3>${ic(sec.icon)}${sec.title}</h3><p class="desc">${sec.desc}</p>
   ${sec.fields.map(f=>`<label for="f_${f[0]}">${f[1]}</label>${f[2]==='select'?`<select id="f_${f[0]}" name="${f[0]}">${f[4].map(o=>`<option value="${o[0]}" ${String(s[f[0]])===o[0]?'selected':''}>${o[1]}</option>`).join('')}</select>`:`<input id="f_${f[0]}" name="${f[0]}" type="${f[2]}" value="${esc(s[f[0]])}" autocomplete="off">`}${f[0].startsWith('lib_')?`<button class="btn sec sm" type="button" data-browse="${f[0]}">Examinar…</button>`:''}${f[3]?`<small>${f[3]}</small>`:''}`).join('')}
   <div class="actions"><button class="btn" type="submit">${ic('check')}Guardar</button>${sec.test?`<button class="btn sec" type="button" data-test="${sec.test}">Probar</button>`:''}
   ${sec.extra==='auto'?`<button class="btn sec" type="button" data-auto>Ejecutar ahora</button>`:''}<span class="msg"></span></div></form>`).join('')+
  `<form class="sect form" id="pwf"><h3>${ic('key')}Cuenta</h3><p class="desc">Cambia la contraseña de acceso a media-server-utility.</p>
   <label for="pw0">Contraseña actual</label><input id="pw0" type="password" autocomplete="current-password" required>
   <label for="pw1">Nueva contraseña (mínimo 8 caracteres)</label><input id="pw1" type="password" autocomplete="new-password" required minlength="8">
   <div class="actions"><button class="btn" type="submit">${ic('check')}Cambiar contraseña</button><span class="msg"></span></div></form>`;
  const say=(f,t,ok)=>{const e=f.querySelector('.msg');e.textContent=t;e.className='msg '+(ok?'ok':'bad')};
  const save=f=>{const b={};f.querySelectorAll('input[name],select[name]').forEach(i=>b[i.name]=i.value);return api('/api/settings',J('PUT',b))};
  m.querySelectorAll('form.sect[data-n]').forEach(f=>{
    f.onsubmit=async e=>{e.preventDefault();try{await save(f);say(f,'Guardado',1)}catch(x){say(f,x.message)}};
    const tb=f.querySelector('[data-test]');if(tb)tb.onclick=async()=>{say(f,'Probando…',1);try{await save(f);say(f,(await api('/api/test/'+tb.dataset.test,{method:'POST'})).message,1)}catch(x){say(f,x.message)}};
    f.querySelectorAll('[data-browse]').forEach(b=>b.onclick=()=>browse($('#f_'+b.dataset.browse)));
    const ab=f.querySelector('[data-auto]');if(ab)ab.onclick=async()=>{say(f,'Ejecutando…',1);try{await save(f);const r=await api('/api/auto/run',{method:'POST'});say(f,r.skipped?'Ya hay una revisión en curso':`Revisados ${r.checked} títulos`+(r.errors.length?` · ${r.errors.length} con error`:''),!r.errors?.length)}catch(x){say(f,x.message)}};
  });
  $('#pwf').onsubmit=async e=>{e.preventDefault();const f=e.target;try{await api('/api/auth/password',J('POST',{password:$('#pw0').value,new_password:$('#pw1').value}));f.reset();say(f,'Contraseña actualizada',1)}catch(x){say(f,x.message)}};
}
boot();
