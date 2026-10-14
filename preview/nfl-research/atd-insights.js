(function () {
    'use strict';
    // Player extras for the NFL sheet, from the sheet's own game logs -- they never move
    // the TD chance. Two things earn a place: how steady his workload has been, and a
    // usage arrow when his last three games really break from his longer sample.
    var esc = function (v) { return String(v == null ? '' : v).replace(/[&<>"']/g, function (c) { return {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[c]; }); };
    var finite = function (v) { return typeof v === 'number' && isFinite(v); };
    var fmt = function (v) { return finite(v) ? v.toFixed(1) : '—'; };
    // A club's targets and carries in a typical game: the denominators of a share.
    var TEAM_VOLUME = { 'target share': 33, 'carry share': 26 };

    // Three games of a share is a small sample: a 20% target share over ~100 targets
    // swings about four points on chance alone. The arrow needs the last three games
    // two standard deviations away from his longer share.
    function trendZ(p) {
        var share = p.share, recent = p.share_l3, n = 3 * (TEAM_VOLUME[p.share_kind] || 30);
        if (!finite(share) || !finite(recent) || share <= 0 || share >= 100) return null;
        return (recent - share) / Math.sqrt(share * (100 - share) / n);
    }

    function get(sheet, id) {
        var p = (sheet.cards || {})[id];
        if (!p) return null;
        var logs = (p.workload_log || []).filter(function (g) { return g.team === p.team; }).slice(-5);
        var isRB = p.pos === 'RB', isReceiver = p.pos === 'WR' || p.pos === 'TE';
        var values = logs.map(function (g) {
            return isRB ? (finite(g.rush_att) && finite(g.rec) ? g.rush_att + g.rec : null) : isReceiver ? g.tgt : g.rush_att;
        }).filter(finite);
        var threshold = isRB ? 15 : isReceiver ? 5 : 3;
        return {
            p: p, z: trendZ(p), n: values.length, threshold: threshold,
            avg: values.length ? values.reduce(function (a, b) { return a + b; }, 0) / values.length : null,
            count: values.filter(function (v) { return v >= threshold; }).length,
            unit: isRB ? 'touches' : isReceiver ? 'targets' : 'carries'
        };
    }

    function moved(x) {
        return !!x && finite(x.z) && Math.abs(x.z) >= 2 && !x.p.new_team && x.p.games >= 4;
    }

    // One line for the player card's fact list, or '' when there are too few games.
    function workload(sheet, id) {
        var x = get(sheet, id);
        if (!x || x.n < 3) return '';
        var line = '<b>' + x.threshold + '+</b> ' + x.unit + ' in <b>' + x.count + ' of his last ' + x.n + '</b> games with ' +
                   esc(x.p.team) + ' · <b>' + fmt(x.avg) + '</b> a game';
        if (moved(x)) {
            line += ' · usage <b>' + (x.z > 0 ? 'rising' : 'falling') + '</b>, more than three games of normal swing';
        }
        return line;
    }

    function arrow(sheet, id) {
        var x = get(sheet, id);
        if (!moved(x)) return '';
        var rising = x.z > 0;
        var label = (rising ? 'Rising' : 'Falling') + ' usage: ' + fmt(x.p.share_l3) + '% ' + (x.p.share_kind || 'share') +
                    ' over the last 3 games vs ' + fmt(x.p.share) + '% over ' + x.p.games + ' — more than three games of normal swing';
        return '<span class="atd-trend-arrow ' + (rising ? 'is-up' : 'is-down') + '" data-tooltip="' + esc(label) + '" aria-label="' +
               esc(label) + '">' + (rising ? '↑' : '↓') + '</span>';
    }

    // Sheets built before 10/14 still call these; the bars and the summary they drew
    // repeated the card's own numbers, so both are retired.
    function none() { return ''; }

    window.NFLInsights = {workload: workload, arrow: arrow, get: get, summary: none, bars: none};
})();
