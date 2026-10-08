(function () {
    'use strict';
    var esc = function (v) { return String(v == null ? '' : v).replace(/[&<>"']/g, function (c) { return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]; }); };
    var finite = function (v) { return typeof v === 'number' && isFinite(v); };
    var fmt = function (v) { return finite(v) ? v.toFixed(1) : '—'; };
    function percentRank(value, peers) {
        var valid = peers.filter(finite);
        if (!finite(value) || valid.length < 2) return null;
        return 100 * (valid.filter(function(v) {return v < value;}).length + .5 * valid.filter(function(v) {return v === value;}).length) / valid.length;
    }
    function get(sheet, id) {
        var p = (sheet.cards || {})[id];
        if (!p) return null;
        var csv = p.csv || {}, share = p.share, recent = p.share_l3;
        var trend = finite(share) && finite(recent) && p.games >= 3 ? recent - share : null;
        var peers = Object.keys(sheet.cards || {}).map(function(key) {return sheet.cards[key];}).filter(function(q) {return q.pos === p.pos && q.csv;});
        var logs = (p.workload_log || []).filter(function(g) {return g.team === p.team;}).slice(-5);
        var isRB = p.pos === 'RB', isReceiver = p.pos === 'WR' || p.pos === 'TE';
        var values = logs.map(function(g) {return isRB ? (finite(g.rush_att) && finite(g.rec) ? g.rush_att + g.rec : null) : isReceiver ? g.tgt : g.rush_att;});
        var valid = values.filter(finite), avg = valid.length ? valid.reduce(function(a,b) {return a+b;},0)/valid.length : null;
        var threshold = isRB ? 15 : isReceiver ? 5 : 3;
        return {p:p,csv:csv,trend:trend,logs:logs,values:values,avg:avg,threshold:threshold,
            count:valid.filter(function(v) {return v >= threshold;}).length, n:valid.length,
            unit:isRB ? 'touches' : isReceiver ? 'targets' : 'rushing attempts',
            volume:percentRank(csv.volume,peers.map(function(q) {return q.csv.volume;})),
            redzone:percentRank(csv.rz_looks,peers.map(function(q) {return q.csv.rz_looks;}))};
    }
    function summary(sheet,id) {
        var x=get(sheet,id); if(!x) return '';
        var p=x.p,c=x.csv,bits=[];
        if (finite(c.volume)) bits.push(fmt(c.volume)+' '+(c.volume_unit || x.unit)+'/game in the CSV');
        if (finite(p.share)) bits.push(fmt(p.share)+'% '+(p.share_kind || 'team usage')+' across '+p.games+' games');
        if (finite(c.rz_looks) && p.pos !== 'QB') bits.push(fmt(c.rz_looks)+' red-zone looks/game');
        if (p.pos !== 'QB' && finite(c.delta)) bits.push('matchup '+(c.delta >= 0 ? '+' : '')+c.delta.toFixed(2)+' projected TD/game vs his baseline');
        if (p.pos === 'QB') bits.push('touchdown chance counts his own scores; passing TD projections are separate');
        return '<div class="atd-player-why"><b>Why this player?</b><p>'+esc(bits.join(' · ') || 'Not enough workload data available.')+'.</p>'+workload(x)+'</div>';
    }
    function workload(x) {
        var p=x.p,lines=[];
        if (x.n >= 3) lines.push(x.threshold+'+ '+x.unit+' in '+x.count+' of the last '+x.n+' logged games on '+p.team+' (average '+fmt(x.avg)+').');
        else lines.push('Too few logged games on '+p.team+' to assess workload consistency.');
        if(finite(x.trend)) lines.push((x.trend >= 2 ? 'Rising' : x.trend <= -2 ? 'Falling' : 'Steady')+' usage: '+fmt(p.share_l3)+'% last 3 vs '+fmt(p.share)+'% over '+p.games+' games.');
        if(p.new_team) lines.push('New team: the longer usage sample includes his previous club.');
        if(p.low_volume || x.csv.low_volume) lines.push('Low workload flagged.');
        return '<p class="atd-workload">'+esc(lines.join(' '))+'</p>';
    }
    function bars(sheet,id) {
        var x=get(sheet,id); if(!x)return '';
        var c=x.csv,p=x.p;
        var items=[
            ['Workload',x.volume,'CSV volume percentile among listed '+p.pos+' players; '+fmt(c.volume)+' '+(c.volume_unit || x.unit)+'/game'],
            ['Usage',p.share,fmt(p.share)+'% '+(p.share_kind || 'team usage')+' across '+p.games+' games'],
            ['Red zone',p.pos === 'QB' ? null : x.redzone,'CSV red-zone looks percentile among listed '+p.pos+' players; '+fmt(c.rz_looks)+'/game'],
            ['Matchup',finite(c.role_leak)?50+(c.role_leak-1)*100:null,'CSV role matchup: '+(finite(c.role_leak)?fmt(c.role_leak)+'×':'unavailable')+'; 1× / midpoint is neutral'],
            ['Trend',finite(x.trend)?50+x.trend*5:null,'Usage last 3 vs full sample: '+(finite(x.trend)?(x.trend>=0?'+':'')+fmt(x.trend)+' percentage points':'unavailable')+'; midpoint is steady, endpoints ±10 points']
        ];
        return '<div class="atd-factor-bars">'+items.map(function(item) {
            var known=finite(item[1]),v=known?Math.max(0,Math.min(100,item[1])):0;
            return '<div class="atd-factor '+(!known?'is-missing':'')+'" tabindex="0" title="'+esc(item[2])+'" aria-label="'+esc(item[0]+': '+item[2])+'"><div class="atd-factor-track"><span style="width:'+v+'%"></span></div><span>'+item[0]+(!known?' —':'')+'</span></div>';
        }).join('')+'</div>';
    }
    function arrow(sheet,id) {
        var x=get(sheet,id);
        if (!x || !finite(x.trend) || x.p.new_team || x.p.games < 4 || Math.abs(x.trend) < 2) return '';
        var rising=x.trend > 0;
        var label=(rising?'Rising':'Falling')+' usage: '+fmt(x.p.share_l3)+'% last 3 games vs '+fmt(x.p.share)+'% over '+x.p.games+' games';
        return '<span class="atd-trend-arrow '+(rising?'is-up':'is-down')+'" tabindex="0" data-tooltip="'+esc(label)+'" aria-label="'+esc(label)+'">'+(rising?'↑':'↓')+'</span>';
    }
    window.NFLInsights={summary:summary,bars:bars,arrow:arrow,get:get};
})();
