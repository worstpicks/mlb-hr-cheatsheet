(function(){
 'use strict';
 var esc=function(s){return String(s==null?'':s).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];});};
 var num=function(v){return typeof v==='number'&&isFinite(v)?v.toFixed(1):'—';};
 function label(r){
  var x=r.recent_evidence;
  if(!x || x.gp<3 || !(x.baseline.sog>0) || r.small)return '';
  var change=100*(x.recent.sog/x.baseline.sog-1);
  if(Math.abs(change)<15)return '';
  return (change>0?'Rising':'Falling')+' shot volume: '+num(x.recent.sog)+' shots/game over '+x.gp+' recent games vs '+num(x.baseline.sog)+' before the recent blend ('+(change>0?'+':'')+Math.round(change)+'%). This describes shooting, not a guaranteed goal.';
 }
 function arrow(r){var text=label(r);if(!text)return '';return '<span class="nhl-trend-arrow '+(text.indexOf('Rising')===0?'is-up':'is-down')+'" tabindex="0" data-tooltip="'+esc(text)+'" aria-label="'+esc(text)+'">'+(text.indexOf('Rising')===0?'↑':'↓')+'</span>';}
 function why(r){
  var x=r.recent_evidence,bits=[];
  if(x)bits.push('Recent CSV: '+num(x.recent.sog)+' shots and '+num(x.raw.iscf)+' scoring chances/game, with '+num(x.toi)+' minutes/game over '+x.gp+' games.');
  bits.push('Model profile: '+num(r.sog)+' shots/game and '+num(r.iscf)+' scoring chances/game after its sample blends.');
  if(r.g_name)bits.push('Facing '+r.g_name+(r.g_note?' ('+r.g_note+')':'')+'.');
  if(r.why)bits.push(r.why);
  if(x&&x.gp<3)bits.push('Small recent sample; too few games for a trend arrow.');
  return '<h4 class="nrs-pf-h">Why this player?</h4><p class="nrs-bd-proj">'+esc(bits.join(' '))+'</p>';
 }
 function tooltip(r,key){
  var reason=(r.reasons||[]).filter(function(x){return x.part===key;})[0];
  var text=reason?reason.text:'No supporting detail available.',x=r.recent_evidence;
  if(x&&key==='volume')text+=' Recent CSV: '+num(x.recent.sog)+' shots/game in '+x.gp+' games; pre-recent baseline '+num(x.baseline.sog)+'.';
  if(x&&key==='quality')text+=' Recent CSV: '+num(x.raw.iscf)+' scoring chances and '+num(x.raw.ihdcf)+' high-danger chances/game (unscaled export rates).';
  if(x&&key==='form')text+=' Recent CSV: '+num(x.toi)+' minutes/game and '+num(x.recent.g)+' goals/game over '+x.gp+' games.';
  if(key==='goalie')text+=' Starter status: '+(r.g_note||'unconfirmed')+'.';
  return text;
 }

 function creation(r){
  var x=r.recent_evidence;if(!x)return '<p class="atgs-pf-note">Recent chance-creation CSV unavailable.</p>';
  var deltas={};var rows=[['sog','Shots on goal'],['iscf','Scoring chances'],['ihdcf','High-danger chances'],['g','Goals']].map(function(item){var k=item[0],base=x.baseline[k],recent=x.recent[k],diff=base>0?100*(recent/base-1):null;deltas[k]=diff;return '<tr><td>'+item[1]+'</td><td>'+Number(base).toFixed(k==='g'?2:1)+'</td><td>'+Number(recent).toFixed(k==='g'?2:1)+'</td><td>'+ (diff===null?'—':(diff>=0?'↑ ':'↓ ')+Math.abs(Math.round(diff))+'%')+'</td></tr>';}).join('');
  var opportunity=deltas.sog>=15&&deltas.iscf>=15;
  var lead=opportunity?'More opportunities':deltas.g>=15&&deltas.sog<15&&deltas.iscf<15?'Scoring ahead of opportunities':'Mixed opportunity profile';
  if(opportunity&&deltas.g>=15)lead='Scoring backed by more opportunities';
  if(opportunity&&deltas.g<15)lead='Opportunities ahead of scoring';
  return '<div class="nhl-detail"><h4>Chance creation vs scoring</h4><p>Per-game rates · '+x.gp+' recent games vs the baseline before recent weighting</p><table class="nrs-bd-table nrs-pf-table"><thead><tr><th>Measure</th><th>Baseline</th><th>Recent</th><th>Change</th></tr></thead><tbody>'+rows+'</tbody></table><p><b>'+lead+'</b></p><p class="atgs-pf-note">Shot and scoring-chance changes of at least 15% drive this description. Chance definitions are aligned using the model’s existing conversion. A zero baseline has no percentage change. '+(x.gp<3?'Small recent sample; early read only. ':'')+'This describes opportunities, not a promise of future goals.</p></div>';
 }
 function goalie(r){
  if(!r.g_name)return '';
  var x=r.goalie_evidence||{},has=!!x.date;
  var sa=has?x.sa:r.g_sa,sv=has?x.sv:(r.g_sv_raw!=null?r.g_sv_raw:r.g_sv_pct)*100,hdsv=has?x.hdsv:(r.g_hd_raw!=null?r.g_hd_raw:r.g_hd_sv_pct)*100;
  function tile(label,value,unit,note){return '<div class="nhl-detail-tile"><span>'+label+'</span><strong>'+ (typeof value==='number'&&isFinite(value)?value.toFixed(1):'—')+unit+'</strong><small>'+esc(note||'')+'</small></div>';}
  var interpretation=has?'Pressure faced and stopping percentages describe separate parts of this matchup.':'High-danger shots faced are unavailable in this sample; stopping percentages alone do not show how much dangerous pressure reaches him.';
  if(has&&x.sa_pct!=null&&x.hdsv_pct!=null)interpretation=(x.sa_pct<=25?'High shot workload':x.sa_pct>=75?'Lower shot workload':'Middle-range shot workload')+' · '+(x.hdsv_pct<=25?'lower high-danger stopping percentile':x.hdsv_pct>=75?'higher high-danger stopping percentile':'middle-range high-danger stopping percentile')+'. Percentiles describe this export, not a prediction.';
  return '<div class="nhl-detail"><h4>Goalie pressure & stopping</h4><p><b>'+esc(r.g_name)+'</b> · '+esc(r.g_src==='lineup'?(r.g_note||'starter unconfirmed'):'starter unconfirmed — busiest goalie fallback')+'</p><h5>Pressure faced</h5><div class="nhl-detail-grid">'+tile('Shots faced',sa,' / game',has?'CSV toughness percentile '+x.sa_pct+'; lower means more shots faced':'Existing goalie sample')+tile('High-danger shots faced',has?x.hdsa:null,' / game',has?'CSV toughness percentile '+x.hdsa_pct+'; lower means more dangerous shots':'No matching recent CSV')+'</div><h5>Stopping performance</h5><div class="nhl-detail-grid">'+tile('Overall save rate',sv,'%',has?'Stopping percentile '+x.sv_pct:'Existing goalie sample')+tile('High-danger save rate',hdsv,'%',has?'Stopping percentile '+x.hdsv_pct:'Existing goalie sample')+'</div><p>'+esc(interpretation)+'</p><p class="atgs-pf-note">'+esc(has?'Recent CSV: '+x.date+' · '+x.gp+' appearances. CSV starter status is not carried into tonight’s slate.':'Existing sample: '+(r.g_gp||'unknown')+' games. No matching recent goalie CSV.')+(has&&x.gp<3?' Small sample; early evidence only.':'')+'</p></div>';
 }
 window.NHLInsights={arrow:arrow,why:why,tooltip:tooltip,creation:creation,goalie:goalie};
})();
