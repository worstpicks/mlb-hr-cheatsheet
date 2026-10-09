"""Build NBA research from ESPN public schedule, roster and final box scores.
Run: python -m nba_research.build_slate --date 2026-10-08 --days 4
Preseason fills a 10-game window until current regular-season games replace it.
"""
import argparse
import concurrent.futures as cf
import hashlib
import json
import time
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / 'nba_research' / 'cache'
OUT = ROOT / 'preview' / 'data'
API = 'https://site.api.espn.com/apis/site/v2/sports/basketball/nba/'
ERRORS = []

def fetch(route, ttl=3600):
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / (hashlib.sha256(route.encode()).hexdigest() + '.json')
    if path.exists() and time.time() - path.stat().st_mtime < ttl:
        return json.loads(path.read_text(encoding='utf-8'))
    for attempt in range(3):
        try:
            req = urllib.request.Request(API + route, headers={'User-Agent': 'WorstPickz NBA Research/1.0'})
            with urllib.request.urlopen(req, timeout=25) as response:
                obj = json.load(response)
            path.write_text(json.dumps(obj), encoding='utf-8')
            return obj
        except Exception as exc:
            if attempt == 2:
                ERRORS.append({'route': route, 'error': str(exc)})
                return {}
            time.sleep(attempt + 1)

def parallel(items, fn):
    with cf.ThreadPoolExecutor(max_workers=8) as pool:
        return list(pool.map(fn, items))

def position(value):
    return 'G' if 'G' in value else 'C' if 'C' in value else 'F'

def number(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None

def stats(names, values):
    data = dict(zip(names, values))
    out = {}
    mapping = {'PTS':'pts','REB':'reb','AST':'ast','STL':'stl','BLK':'blk','TO':'tov','OREB':'oreb','DREB':'dreb','PF':'pf','+/-':'pm'}
    for key, target in mapping.items():
        out[target] = number(data.get(key))
    minute = str(data.get('MIN', ''))
    try:
        out['min'] = float(minute.split(':')[0]) + (float(minute.split(':')[1])/60 if ':' in minute else 0)
    except ValueError:
        out['min'] = None
    for key, prefix in [('FG','fg'),('3PT','three'),('FT','ft')]:
        pair = str(data.get(key, '')).split('-')
        out[prefix+'m'] = number(pair[0]) if len(pair)==2 else None
        out[prefix+'a'] = number(pair[1]) if len(pair)==2 else None
    out['twom'] = out['fgm'] - out['threem'] if out['fgm'] is not None and out['threem'] is not None else None
    out['twoa'] = out['fga'] - out['threea'] if out['fga'] is not None and out['threea'] is not None else None
    for key, parts in {'pra':['pts','reb','ast'],'pr':['pts','reb'],'pa':['pts','ast'],'ra':['reb','ast'],'stocks':['stl','blk']}.items():
        out[key] = sum(out[k] for k in parts) if all(out.get(k) is not None for k in parts) else None
    double_stats = [out.get(k) for k in ('pts', 'reb', 'ast', 'stl', 'blk')]
    doubles = sum(v >= 10 for v in double_stats if v is not None)
    out['dd'] = int(doubles >= 2) if all(v is not None for v in double_stats) else None
    out['td'] = int(doubles >= 3) if all(v is not None for v in double_stats) else None
    return out

def parse_summary(event, summary):
    groups = summary.get('boxscore', {}).get('players', [])
    if len(groups) != 2:
        return []
    competitors = {c['id']:c for c in event['competitions'][0]['competitors']}
    output = []
    for group in groups:
        team = group['team']; tid = team['id']
        opponent = next((g['team'] for g in groups if g['team']['id'] != tid), None)
        comp = competitors.get(tid, {})
        rows = []
        for section in group.get('statistics', []):
            for player in section.get('athletes', []):
                if player.get('didNotPlay') or not player.get('stats'):
                    continue
                athlete = player['athlete']; values = stats(section['names'], player['stats'])
                if not values.get('min'):
                    continue
                rows.append({'id':athlete['id'],'name':athlete['displayName'],
                             'pos':position(athlete.get('position',{}).get('abbreviation','F')),
                             'starter':bool(player.get('starter')), **values})
        if not rows:
            continue
        totals = {key:sum(p[key] for p in rows if p.get(key) is not None) for key in ('pts','reb','ast','stl','blk','tov','oreb','fga','fgm','fta','ftm','threem','threea')}
        poss = totals['fga'] + .44 * totals['fta'] - totals['oreb'] + totals['tov']
        output.append({'event':event['id'],'date':event['date'],'season':event.get('season',{}).get('year'),
                       'type':int(event.get('seasonType',{}).get('type',2)),
                       'team_id':tid,'team':team['abbreviation'],'opp_id':opponent['id'],'opp':opponent['abbreviation'],
                       'home':comp.get('homeAway')=='home','players':rows,'totals':totals,'possessions_est':round(poss,1),
                       'team_minutes':sum(p['min'] for p in rows)})
    return output

def build(first, days):
    start = date.fromisoformat(first)
    season = start.year + 1 if start.month >= 7 else start.year
    dates = [(start + timedelta(days=i)).isoformat() for i in range(days)]
    boards = dict(zip(dates, parallel(dates, lambda d:fetch('scoreboard?dates='+d.replace('-','')))))
    teams_data = fetch('teams?limit=100')
    teams = [entry['team'] for entry in teams_data.get('sports',[{}])[0].get('leagues',[{}])[0].get('teams',[])]
    if not teams:
        raise RuntimeError('NBA teams unavailable; no output written')
    print(f'[NBA] {len(teams)} teams; loading rosters and recent schedules', flush=True)
    roster_results = parallel(teams, lambda t:fetch('teams/'+t['id']+'/roster'))
    rosters = dict(zip([t['id'] for t in teams], roster_results))
    schedules = parallel([(t['id'],y,kind) for t in teams for y,kind in [(season,1),(season,2),(season-1,2)]],
                         lambda args:fetch(f'teams/{args[0]}/schedule?season={args[1]}&seasontype={args[2]}'))
    events = {}
    cutoff = dates[-1]+'T23:59:59Z'
    for schedule in schedules:
        available = [e for e in schedule.get('events',[]) if e['date'] < cutoff and e['competitions'][0].get('status',{}).get('type',{}).get('completed')]
        for event in sorted(available,key=lambda e:e['date'])[-10:]:
            events[event['id']] = event
    print(f'[NBA] Loading {len(events)} final box scores (cached on later runs)', flush=True)
    summaries = parallel(list(events.values()),lambda e:(e,fetch('summary?event='+e['id'],ttl=31536000)))
    logs = []
    for event, summary in summaries:
        logs.extend(parse_summary(event,summary))
    if not logs:
        raise RuntimeError('No completed NBA box scores available; no output written')
    print(f'[NBA] Parsed {len(logs)} team-game logs',flush=True)
    for d, board in boards.items():
        if 'events' not in board:
            print('[NBA] Skipping unavailable scoreboard '+d,flush=True)
            continue
        prior = [g for g in logs if datetime.fromisoformat(g['date'].replace('Z', '+00:00')).astimezone(ZoneInfo('America/New_York')).date().isoformat() < d]
        team_logs = {t['id']:sorted([g for g in prior if g['team_id']==t['id']],key=lambda g:g['date']) for t in teams}
        player_logs = {}
        for game in prior:
            for player in game['players']:
                usage = player.get('fga',0) + .44*(player.get('fta') or 0) + (player.get('tov') or 0)
                team_usage = game['totals']['fga'] + .44*game['totals']['fta'] + game['totals']['tov']
                usg = 100*usage*(game['team_minutes']/5)/(player['min']*team_usage) if team_usage else None
                player_logs.setdefault(player['id'],[]).append({**{k:v for k,v in player.items() if k not in ('id','name','pos')},
                    'date':game['date'],'event':game['event'],'team':game['team'],'opp':game['opp'],'home':game['home'],
                    'season':game['season'],'type':game['type'],'usage_est':round(usg,1) if usg is not None else None})
        games = []
        for event in board['events']:
            comp=event['competitions'][0]; sides={}
            for competitor in comp['competitors']:
                team=competitor['team'];tid=team['id'];side=competitor['homeAway']
                other=next(c for c in comp['competitors'] if c['id']!=tid)
                players=[]
                for athlete in rosters.get(tid,{}).get('athletes',[]):
                    injury=athlete.get('injuries',[]);note=injury[0] if injury else {}
                    players.append({'id':athlete['id'],'name':athlete['displayName'],
                        'pos':position(athlete.get('position',{}).get('abbreviation','F')),
                        'position':athlete.get('position',{}).get('displayName',''),
                        'headshot':athlete.get('headshot',{}).get('href',''),
                        'injury':note.get('status',''),'injury_note':note.get('details',{}).get('detail','') or note.get('longComment',''),
                        'logs':sorted(player_logs.get(athlete['id'],[]),key=lambda g:g['date'])})
                # Every defensive log is exactly one opponent-position total for a final game.
                defensive=[]
                for g in team_logs.get(tid,[]):
                    opp_game=next((x for x in prior if x['event']==g['event'] and x['team_id']==g['opp_id']),None)
                    if not opp_game:continue
                    groups={}
                    for pos in ('G','F','C'):
                        rows=[p for p in opp_game['players'] if p['pos']==pos]
                        groups[pos]={k:sum(p[k] for p in rows if p.get(k) is not None) for k in ('pts','reb','ast','threem','stl','blk','tov','pra','pr','pa','ra','stocks','fga','fgm','fta','ftm','threea','twom','twoa','oreb','dreb','pf','pm','dd','td','min')}
                        groups[pos]['players']=len(rows)
                    defensive.append({**{k:g[k] for k in ('date','event','season','type','opp','home')},'groups':groups,
                                      'allowed':opp_game['totals'],'own':g['totals'],'possessions_est':(g['possessions_est']+opp_game['possessions_est'])/2})
                sides[side]={'id':tid,'abbr':team['abbreviation'],'name':team['displayName'],'logo':team.get('logo',''),
                             'players':players,'defense':defensive,'record':next((r.get('summary') for r in competitor.get('records',[]) if r.get('type')=='total'),'')}
            if set(sides)=={'home','away'}:
                games.append({'id':event['id'],'date':event['date'],'label':event['shortName'],'status':event.get('status',{}).get('type',{}).get('detail',''),
                    'type':int(event.get('season',{}).get('type',1)), 'venue':comp.get('venue',{}).get('fullName',''),
                    'odds':comp.get('odds',[{}])[0] if comp.get('odds') else {},'sides':sides})
        league = {}
        for team in teams:
            league_rows = []
            for game in team_logs[team['id']]:
                groups = {}
                for pos in ('G', 'F', 'C'):
                    players = [p for p in game['players'] if p['pos'] == pos]
                    if players:
                        groups[pos] = {k: sum(p[k] for p in players if p.get(k) is not None) / len(players)
                                       for k in ('pts', 'reb', 'ast', 'threem', 'stl', 'blk', 'tov', 'min')}
                league_rows.append({**{k: game[k] for k in ('date', 'season', 'type', 'home')}, 'groups': groups})
            league[team['id']] = league_rows
        data={'date':d,'season':season,'built':datetime.now(timezone.utc).isoformat(), 'league':league,
              'source':'ESPN public final box scores, rosters and schedule','source_url':API+'scoreboard?dates='+d.replace('-',''),
              'games':games,'errors':ERRORS,
              'policy':'Auto: current regular season, then current preseason, then previous regular season to fill 10 appearances. DNPs excluded. Preseason phases out per player after 10 regular-season appearances.'}
        OUT.mkdir(parents=True,exist_ok=True)
        (OUT/f'nba-research-{d}.json').write_text(json.dumps(data,separators=(',',':')),encoding='utf-8')
        print(f'[NBA] {d}: {len(games)} games, {sum(len(s["players"]) for g in games for s in g["sides"].values())} rostered players',flush=True)
    manifest={'dates':sorted(p.stem.removeprefix('nba-research-') for p in OUT.glob('nba-research-????-??-??.json'))}
    (OUT/'nba-research-manifest.json').write_text(json.dumps(manifest),encoding='utf-8')
    if ERRORS:print(f'[NBA] {len(ERRORS)} upstream requests failed; displayed as incomplete coverage',flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--date',required=True);parser.add_argument('--days',type=int,default=4)
    args=parser.parse_args();build(args.date,args.days)
