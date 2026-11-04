/* Small progressive enhancements. No SPA and no runtime CDN dependency. */
'use strict';
const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;
function toast(message, error = false) {
  const item = document.createElement('div'); item.className = `toast-message${error ? ' error' : ''}`;
  item.textContent = message; $('#toast-region').append(item); setTimeout(() => item.remove(), 5500);
}
// These release-locked controls never submit a generation request.
const futurePaths=new Map([['/counselor','AI career counselor'],['/chatbot1','AI career counselor'],['/chatbot2','AI career counselor'],['/interview','AI interview practice']]);
$$('a[href]').forEach(link=>{const url=new URL(link.getAttribute('href'),location.origin);if(url.origin!==location.origin||!futurePaths.has(url.pathname))return;link.dataset.futureFeature=futurePaths.get(url.pathname);link.classList.add('future-link');link.setAttribute('aria-haspopup','dialog');link.title='Future feature — coming soon';const badge=$('.mini-badge',link);if(badge)badge.textContent='Soon';else{const label=document.createElement('span');label.className='future-badge';label.textContent=link.classList.contains('nav-item')?'Soon':'Coming soon';const target=link.classList.contains('tool-card')?$('.tool-link',link):link;target.append(label);}});
document.addEventListener('click',event=>{const control=event.target.closest('[data-future-feature]');if(!control)return;event.preventDefault();const dialog=$('#future-dialog');$('#future-description').textContent=control.dataset.futureFeature+' is a future feature. It is currently locked and will be available in a future release.';if(dialog?.showModal)dialog.showModal();else toast('Future feature: '+control.dataset.futureFeature+' is coming soon.');});
$('#future-dialog')?.addEventListener('click',event=>{if(event.target===$('#future-dialog'))$('#future-dialog').close();});
async function api(url, data, method = 'POST', signal) {
  const response = await fetch(url, {method, credentials: 'same-origin', signal,
    headers: {'Content-Type': 'application/json', 'X-CSRFToken': $('meta[name="csrf-token"]').content},
    ...(method === 'GET' ? {} : {body: JSON.stringify(data || {})})});
  if (response.redirected || !response.headers.get('content-type')?.includes('application/json')) throw new Error('Your session expired. Sign in again and retry.');
  const result = await response.json(); if (!response.ok) throw new Error(result.error || 'Something went wrong. Please retry.'); return result;
}
// Markdown is constructed from text nodes. Raw HTML, image embeds and arbitrary links never execute.
function inlineMarkdown(parent, text) {
  for (const part of text.split(/(\*\*[^*]+\*\*|`[^`]+`)/g)) {
    if (part.startsWith('**') && part.endsWith('**')) { const el = document.createElement('strong'); el.textContent = part.slice(2,-2); parent.append(el); }
    else if (part.startsWith('`') && part.endsWith('`')) { const el = document.createElement('code'); el.textContent = part.slice(1,-1); parent.append(el); }
    else parent.append(document.createTextNode(part));
  }
}
function markdown(target, text) {
  target.replaceChildren(); let list = null;
  for (const line of text.split('\n')) {
    const heading = line.match(/^(#{1,4})\s+(.+)/); const bullet = line.match(/^\s*(?:[-*]|\d+\.)\s+(.+)/);
    if (!line.trim()) { list = null; continue; }
    if (heading) { list = null; const el = document.createElement(heading[1].length <= 2 ? 'h3':'h4'); inlineMarkdown(el, heading[2]); target.append(el); }
    else if (bullet) { if (!list) { list = document.createElement('ul'); target.append(list); } const el = document.createElement('li'); inlineMarkdown(el, bullet[1]); list.append(el); }
    else { list = null; const el = document.createElement('p'); inlineMarkdown(el,line); target.append(el); }
  }
}
$$('[data-markdown]').forEach(el => markdown(el,el.textContent));
$$('.theme-toggle').forEach(button => button.addEventListener('click', () => {
  const theme = document.documentElement.dataset.theme === 'dark' ? 'light':'dark'; document.documentElement.dataset.theme = theme;
  try { localStorage.setItem('cg-theme',theme); } catch (_) {} button.setAttribute('aria-pressed',String(theme==='dark'));
}));
const menu = $('.mobile-menu');
const mobileMedia=matchMedia('(max-width: 760px)');
function sidebarAccess(){if($('#sidebar'))$('#sidebar').inert=mobileMedia.matches&&!$('#sidebar').classList.contains('open');}
function closeMenu() { $('#sidebar')?.classList.remove('open'); $('#sidebar-overlay')?.classList.remove('open'); menu?.setAttribute('aria-expanded','false'); sidebarAccess(); }
mobileMedia.addEventListener('change',closeMenu);sidebarAccess();
menu?.addEventListener('click', () => { const open = !$('#sidebar').classList.contains('open'); $('#sidebar').classList.toggle('open',open); $('#sidebar-overlay').classList.toggle('open',open); menu.setAttribute('aria-expanded',String(open)); sidebarAccess(); if(open) $('.sidebar a')?.focus(); });
$('#sidebar-overlay')?.addEventListener('click',closeMenu);
document.addEventListener('keydown',e => { if(e.key==='Escape' && $('.sidebar.open')) {closeMenu(); menu.focus();} });
document.addEventListener('keydown',e=>{if(e.key!=='Tab'||!mobileMedia.matches||!$('.sidebar.open'))return;const links=$$('a,button,input,select,textarea',$('#sidebar')).filter(el=>!el.disabled);const first=links[0],last=links.at(-1);if(e.shiftKey&&document.activeElement===first){e.preventDefault();last.focus();}else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first.focus();}});
$$('.dismiss').forEach(el => el.addEventListener('click',()=>el.closest('.alert').remove()));
$$('.password-toggle').forEach(el=>el.addEventListener('click',()=>{ const input=$('input',el.parentElement); input.type=input.type==='password'?'text':'password'; el.textContent=input.type==='password'?'Show':'Hide'; el.setAttribute('aria-label',input.type==='password'?'Show password':'Hide password'); }));
$$('form').forEach(form=>form.addEventListener('submit',e=>{
  if(form.dataset.confirm && !confirm(form.dataset.confirm)){e.preventDefault();return;}
  if(form.id==='bulk-form' && !$$('.row-select:checked').length){e.preventDefault();toast('Select at least one record.',true);return;}
  if(!['chat-form'].includes(form.id) && form.method==='post'){
    const button=e.submitter; if(button){button.setAttribute('aria-busy','true');button.classList.add('is-loading');}
  }
}));
if ('IntersectionObserver' in window && !reducedMotion) {
  const observer = new IntersectionObserver(entries=>entries.forEach(entry=>{if(entry.isIntersecting){entry.target.classList.add('visible');observer.unobserve(entry.target);}}),{threshold:.06});
  $$('.reveal').forEach(el=>{if(el.getBoundingClientRect().top>innerHeight){el.classList.add('reveal-ready');observer.observe(el);}});
}
$$('.resume-report-heading .score-circle').forEach(el=>{el.classList.add('resume-score');el.style.setProperty('--score',Number($('[data-count]',el)?.dataset.count)||0);});
$$('[data-count]').forEach(el=>{ const final=Number(el.dataset.count); if(reducedMotion || !final) return; const start=performance.now(); function tick(t){const p=Math.min((t-start)/850,1);el.textContent=Math.round(final*(1-Math.pow(1-p,3)));if(p<1)requestAnimationFrame(tick);}requestAnimationFrame(tick); });
// Client-side career browsing.
if ($('#career-grid')) {
  const grid=$('#career-grid'), cards=$$('.career-item',grid);
  const update=()=>{const q=$('#career-search').value.toLowerCase().trim(),cluster=$('#career-cluster').value,sort=$('#career-sort').value;let visible=0;
    cards.sort((a,b)=>sort==='default'?Number(a.dataset.order)-Number(b.dataset.order):a.dataset.title.localeCompare(b.dataset.title)*(sort==='za'?-1:1)).forEach(card=>{
      card.hidden=!(card.dataset.search.toLowerCase().includes(q)&&(!cluster||card.dataset.cluster===cluster));if(!card.hidden)visible++;grid.append(card);
    });$('#career-count').textContent=visible;$('#career-empty').hidden=visible!==0;
  };
  $('#career-search').addEventListener('input',update);$('#career-cluster').addEventListener('change',update);$('#career-sort').addEventListener('change',update);
  $('#clear-filters').addEventListener('click',()=>{$('#career-search').value='';$('#career-cluster').value='';update();});
}
$$('.save-career').forEach(button=>button.addEventListener('click',async()=>{button.disabled=true;try{const result=await api(`/api/careers/${button.dataset.id}/save`);$('span',button).textContent=result.saved?'Saved to my paths':'Save this path';button.setAttribute('aria-pressed',String(result.saved));toast(result.saved?'Saved to your career paths.':'Removed from saved paths.');}catch(e){toast(e.message,true);}finally{button.disabled=false;}}));
// Everyday interests remain ordinary comma-separated text, with optional shortcuts.
if($('#interest-form')){
  const input=$('#interests'),chips=$$('.interest-chip');
  const values=()=>[...new Map(input.value.split(/[,;\n]+/).map(value=>value.trim()).filter(Boolean).map(value=>[value.toLowerCase(),value])).values()];
  const sync=()=>{const selected=values().map(value=>value.toLowerCase());chips.forEach(chip=>chip.setAttribute('aria-pressed',String(selected.includes(chip.dataset.interest.toLowerCase()))));};
  chips.forEach(chip=>chip.addEventListener('click',()=>{const current=values(),interest=chip.dataset.interest,index=current.findIndex(value=>value.toLowerCase()===interest.toLowerCase());if(index>=0)current.splice(index,1);else current.push(interest);input.value=current.join(', ');sync();}));
  input.addEventListener('input',sync);input.addEventListener('blur',()=>{input.value=values().join(', ');sync();});sync();
}
// Quiz: draft progress survives refresh; answers can be changed before submission.
if ($('#quiz-app')) {
  const questions=JSON.parse($('#quiz-data').textContent), answers=Array(questions.length).fill(null);let index=0;let submitting=false;
  const key='cg-quiz-draft-'+($('#quiz-app').dataset.user||'user');
  try{const draft=JSON.parse(sessionStorage.getItem(key));if(draft&&Array.isArray(draft.answers)&&draft.answers.length===questions.length){draft.answers.forEach((a,i)=>{if(Number.isInteger(a)&&a>=1&&a<=5)answers[i]=a;});index=Math.max(0,Math.min(draft.index||0,questions.length-1));}}catch(_){}
  const save=()=>{try{sessionStorage.setItem(key,JSON.stringify({answers,index}));}catch(_){}};
  function render(focus=false){$('#question-count').textContent=`${String(index+1).padStart(2,'0')} / ${questions.length}`;$('#question-category').textContent=questions[index][0]+' interests';$('#question-text').textContent=questions[index][1];$('#quiz-progress').style.width=((index+1)/questions.length*100)+'%';$('#quiz-progress').setAttribute('aria-valuenow',index+1);$$('[name="quiz-answer"]').forEach(input=>input.checked=Number(input.value)===answers[index]);$('#quiz-back').disabled=index===0;$('#quiz-next').textContent=index===questions.length-1?'See my matches →':'Next →';$('#quiz-error').textContent='';save();if(focus)$('#question-text').focus({preventScroll:true});}
  $$('[name="quiz-answer"]').forEach(input=>input.addEventListener('change',()=>{answers[index]=Number(input.value);$('#quiz-error').textContent='';save();}));
  $('#quiz-back').addEventListener('click',()=>{if(index>0&&!submitting){index--;render(true);}});
  $('#quiz-next').addEventListener('click',async()=>{if(submitting)return;if(!answers[index]){$('#quiz-error').textContent='Choose an answer before moving on.';return;}if(index<questions.length-1){index++;render(true);return;}submitting=true;$('#quiz-next').disabled=true;$('#quiz-next').textContent='Finding your direction…';$('#quiz-back').disabled=true;
    try{const result=await api('/api/quiz',{answers});try{sessionStorage.removeItem(key);}catch(_){}location.assign(result.redirect);}catch(e){$('#quiz-error').textContent=e.message;submitting=false;$('#quiz-next').disabled=false;render();$('#quiz-error').textContent=e.message;}
  });render();
}
// Resume upload feedback and real drag-and-drop.
if($('#resume-file')){
  const input=$('#resume-file'),drop=$('#resume-drop');
  const changed=()=>{const file=input.files[0];$('#resume-file-label').textContent=file?file.name:'Choose a resume or drop it here';if(file&&file.size>4*1024*1024){toast('Use a resume under 4 MB.',true);input.value='';$('#resume-file-label').textContent='Choose a smaller resume';}};
  input.addEventListener('change',changed);['dragenter','dragover'].forEach(type=>drop.addEventListener(type,e=>{e.preventDefault();drop.classList.add('drag-over');}));['dragleave','drop'].forEach(type=>drop.addEventListener(type,e=>{e.preventDefault();drop.classList.remove('drag-over');}));drop.addEventListener('drop',e=>{if(e.dataTransfer.files.length===1){input.files=e.dataTransfer.files;changed();}else toast('Choose one resume at a time.',true);});
}
// Chat streaming with per-user persisted conversation history.
if($('#chat-app')){
  const root=$('#chat-app'),messages=$('#chat-messages'),welcome=$('#chat-welcome').cloneNode(true),input=$('#chat-input'),send=$('#send-chat'),stop=$('#stop-chat');
  let conversationId=null,controller=null,busy=false;
  const error=(text)=>{const el=$('#chat-error');el.textContent=text;el.hidden=!text;};
  function message(role,text){$('#chat-welcome')?.remove();const row=document.createElement('div');row.className='chat-message '+role;const avatar=document.createElement('span');avatar.className='message-avatar';avatar.textContent=role==='assistant'?'CG':'You';const body=document.createElement('div');body.className='message-body markdown-content';if(role==='assistant')markdown(body,text);else body.textContent=text;row.append(avatar,body);messages.append(row);messages.scrollTop=messages.scrollHeight;return body;}
  function lock(value){busy=value;send.disabled=value;input.disabled=value;stop.hidden=!value;$('#new-chat').disabled=value;$$('.history-open,.history-delete,.suggestion').forEach(el=>el.disabled=value);}
  function select(id){$$('.history-row').forEach(el=>el.classList.toggle('selected',Number(el.dataset.conversation)===id));}
  function addHistory(id,title){if($(`.history-row[data-conversation="${id}"]`))return;$('.history-empty')?.remove();const row=document.createElement('div');row.className='history-row';row.dataset.conversation=id;const open=document.createElement('button');open.className='history-open';open.dataset.id=id;open.textContent=title.slice(0,80);const remove=document.createElement('button');remove.className='icon-button history-delete';remove.dataset.id=id;remove.textContent='×';remove.setAttribute('aria-label','Delete conversation');row.append(open,remove);$('#conversation-list').prepend(row);}
  async function submit(text){if(busy||!text.trim())return;error('');message('user',text);input.value='';input.style.height='auto';lock(true);const body=message('assistant','');const dots=document.createElement('span');dots.className='typing-dots';for(let i=0;i<3;i++)dots.append(document.createElement('i'));body.append(dots);let output='',finished=false;
    controller=new AbortController();
    try{const response=await fetch('/api/chat',{method:'POST',credentials:'same-origin',signal:controller.signal,headers:{'Content-Type':'application/json','X-CSRFToken':$('meta[name="csrf-token"]').content},body:JSON.stringify({message:text,kind:root.dataset.kind,conversation_id:conversationId})});
      if(!response.ok){const result=await response.json();throw new Error(result.error||'Unable to start the conversation.');}
      if(!response.headers.get('content-type')?.includes('text/event-stream'))throw new Error('Your session expired. Please sign in again.');
      const reader=response.body.getReader(),decoder=new TextDecoder();let buffer='';
      function process(event){if(!event.startsWith('data: '))return;const data=JSON.parse(event.slice(6));if(data.conversation_id){conversationId=data.conversation_id;addHistory(conversationId,text);select(conversationId);}if(data.delta){output+=data.delta;markdown(body,output);messages.scrollTop=messages.scrollHeight;}if(data.error)throw new Error(data.error);if(data.done)finished=true;}
      while(true){const {done,value}=await reader.read();if(done)break;buffer+=decoder.decode(value,{stream:true});let boundary;while((boundary=buffer.indexOf('\n\n'))!==-1){const event=buffer.slice(0,boundary);buffer=buffer.slice(boundary+2);process(event);}}
      if(!finished)throw new Error('The response ended early. Any partial answer may be incomplete.');
    }catch(e){if(e.name==='AbortError')error('Response stopped. Partial text is not saved. Continue with another message when ready.');else error(e.message);if(!output)body.closest('.chat-message').remove();input.value=text;}
    finally{lock(false);controller=null;input.focus();}
  }
  $('#chat-form').addEventListener('submit',e=>{e.preventDefault();submit(input.value.trim());});
  input.addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.shiftKey&&!e.isComposing){e.preventDefault();submit(input.value.trim());}});
  input.addEventListener('input',()=>{input.style.height='auto';input.style.height=Math.min(input.scrollHeight,130)+'px';});
  messages.addEventListener('click',e=>{const button=e.target.closest('.suggestion');if(button){input.value=button.textContent.trim();input.focus();}});
  stop.addEventListener('click',()=>controller?.abort());
  $('#new-chat').addEventListener('click',()=>{if(busy)return;conversationId=null;messages.replaceChildren(welcome.cloneNode(true));select(null);error('');input.value='';input.focus();});
  $('#conversation-list').addEventListener('click',async e=>{if(busy)return;const open=e.target.closest('.history-open'),remove=e.target.closest('.history-delete');try{
    if(open){lock(true);const result=await api('/api/conversations/'+open.dataset.id,null,'GET');if(result.kind!==root.dataset.kind)throw new Error('Open this conversation in the correct tool.');conversationId=result.id;messages.replaceChildren();result.messages.forEach(m=>message(m.role,m.content));select(conversationId);error('');}
    else if(remove&&confirm('Delete this conversation and all its messages?')){await api(`/api/conversations/${remove.dataset.id}/delete`);remove.closest('.history-row').remove();if(Number(remove.dataset.id)===conversationId){conversationId=null;messages.replaceChildren(welcome.cloneNode(true));}toast('Conversation deleted.');}
  }catch(err){error(err.message);}finally{lock(false);}});
  $('#flag-chat').addEventListener('click',async()=>{if(!conversationId){toast('Open a conversation first.',true);return;}try{await api('/api/chat/flag',{conversation_id:conversationId});toast('Sent to the admin review queue.');}catch(e){toast(e.message,true);}});
  const role=new URLSearchParams(location.search).get('role');if(role&&root.dataset.kind==='interview')input.value='Practice an interview for '+role;
}
// Management tables, content filtering and accessible reorder controls.
$$('.list-search').forEach(input=>input.addEventListener('input',()=>{const q=input.value.toLowerCase();$$('[data-search]',$('#'+input.dataset.target)).forEach(row=>row.hidden=!row.dataset.search.toLowerCase().includes(q));}));
function selection(){const selected=$$('.row-select:checked').length;if($('#selection-count'))$('#selection-count').textContent=`· ${selected} selected`;if($('#select-all')){const enabled=$$('.row-select:not(:disabled)');$('#select-all').checked=enabled.length>0&&selected===enabled.length;$('#select-all').indeterminate=selected>0&&selected<enabled.length;}}
$('#select-all')?.addEventListener('change',e=>{$$('.row-select:not(:disabled)').forEach(row=>row.checked=e.target.checked);selection();});$$('.row-select').forEach(el=>el.addEventListener('change',selection));
if($('#content-list')?.dataset.reorder==='true'){
  const list=$('#content-list');let dragged=null,saving=false;
  async function saveOrder(previous){if(saving)return;saving=true;try{await api('/api/admin/careers/reorder',{ids:$$('.content-row',list).map(row=>Number(row.dataset.id))});toast('Career order saved.');}catch(e){previous.forEach(row=>list.append(row));toast(e.message,true);}finally{saving=false;}}
  list.addEventListener('click',e=>{const up=e.target.closest('.reorder-up'),down=e.target.closest('.reorder-down');if((!up&&!down)||saving)return;const row=(up||down).closest('.content-row'),previous=$$('.content-row',list),other=up?row.previousElementSibling:row.nextElementSibling;if(!other)return;if(up)list.insertBefore(row,other);else list.insertBefore(other,row);saveOrder(previous);});
  list.addEventListener('dragstart',e=>{const row=e.target.closest('.content-row');if(!row||saving){e.preventDefault();return;}dragged=row;row.classList.add('dragging');e.dataTransfer.effectAllowed='move';e.dataTransfer.setData('text/plain',row.dataset.id);});
  list.addEventListener('dragover',e=>{if(dragged){e.preventDefault();$$('.drag-target',list).forEach(el=>el.classList.remove('drag-target'));const target=e.target.closest('.content-row');if(target&&target!==dragged)target.classList.add('drag-target');}});
  list.addEventListener('drop',e=>{e.preventDefault();const target=e.target.closest('.content-row');if(dragged&&target&&target!==dragged&&!saving){const previous=$$('.content-row',list);list.insertBefore(dragged,target);saveOrder(previous);}$$('.drag-target',list).forEach(el=>el.classList.remove('drag-target'));});
  list.addEventListener('dragend',()=>{dragged?.classList.remove('dragging');dragged=null;$$('.drag-target',list).forEach(el=>el.classList.remove('drag-target'));});
}
// Animated SVG charts use live aggregates; tooltips expose each actual data point.
if($('#analytics')){
  function svgNode(tag,attrs={},text){const el=document.createElementNS('http://www.w3.org/2000/svg',tag);Object.entries(attrs).forEach(([key,value])=>el.setAttribute(key,String(value)));if(text!==undefined)el.textContent=text;return el;}
  function chart(target,labels,series,title){target.classList.remove('skeleton');target.setAttribute('role','group');target.replaceChildren();const w=450,h=215,left=28,right=14,top=20,bottom=30;const max=Math.max(1,...series.flatMap(s=>s.values));const svg=svgNode('svg',{viewBox:`0 0 ${w} ${h}`,role:'img','aria-label':title});svg.append(svgNode('title',{},title));
    for(let i=0;i<4;i++){const value=max*i/3,y=h-bottom-(h-bottom-top)*i/3;svg.append(svgNode('line',{x1:left,y1:y,x2:w-right,y2:y}));svg.append(svgNode('text',{x:left-8,y:y+3,'text-anchor':'end'},Number.isInteger(value)?value:value.toFixed(1)));}
    const x=i=>left+(w-left-right)*i/(labels.length-1), y=value=>h-bottom-(h-top-bottom)*value/max;
    [0,Math.floor(labels.length/2),labels.length-1].forEach(i=>svg.append(svgNode('text',{x:x(i),y:h-9,'text-anchor':i===0?'start':i===labels.length-1?'end':'middle'},labels[i].slice(5))));
    series.forEach(s=>{const d=s.values.map((v,i)=>`${i?'L':'M'}${x(i)},${y(v)}`).join(' ');svg.append(svgNode('path',{d,class:'line',stroke:s.color}));s.values.forEach((v,i)=>{const dot=svgNode('circle',{cx:x(i),cy:y(v),r:3,style:`stroke:${s.color}`});dot.append(svgNode('title',{},`${labels[i]}: ${s.name} ${v}`));svg.append(dot);});});target.append(svg);target.setAttribute('aria-label',title+' '+series.map(s=>`${s.name}: ${s.values.reduce((a,b)=>a+b,0)} total`).join('; '));
    const details=document.createElement('details');details.className='chart-data';const summary=document.createElement('summary');summary.textContent='View chart data';details.append(summary);const table=document.createElement('table');table.className='chart-data-table';labels.forEach((label,i)=>{const tr=document.createElement('tr');[label,...series.map(s=>`${s.name}: ${s.values[i]}`)].forEach(value=>{const td=document.createElement('td');td.textContent=value;tr.append(td);});table.append(tr);});details.append(table);target.append(details);
  }
  async function loadAnalytics(){try{const data=await api('/api/admin/analytics',null,'GET');chart($('#signup-chart'),data.labels,[{name:'Signups',values:data.signups,color:'var(--green)'}],'Daily new signups');chart($('#booking-chart'),data.labels,[{name:'Consultations',values:data.bookings,color:'var(--green)'},{name:'Review queries',values:data.unanswered,color:'#b78760'}],'Consultation and review request volume');const popular=$('#popular-careers');popular.classList.remove('skeleton','chart');popular.replaceChildren();if(!data.popular.length){const empty=document.createElement('div');empty.className='empty-state';empty.textContent='No career views yet. Real exploration activity will appear here.';popular.append(empty);}data.popular.forEach((row,i)=>{const el=document.createElement('div');el.className='popular-row';const rank=document.createElement('span');rank.textContent=String(i+1).padStart(2,'0');const title=document.createElement('strong');title.textContent=row.title;const count=document.createElement('span');count.className='badge soft';count.textContent=row.views+' views';el.append(rank,title,count);popular.append(el);});}
    catch(e){$$('.skeleton').forEach(el=>{el.classList.remove('skeleton');el.textContent=e.message;});toast('Analytics could not refresh.',true);}}
  loadAnalytics();setInterval(()=>{if(!document.hidden)loadAnalytics();},60000);
}
