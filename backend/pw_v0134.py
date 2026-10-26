"""Pixel Works 0.13.4: safe playable bootstrap for newly created game projects.

Create a tiny honest HTML5 vertical slice and a local, initial Git snapshot.
No AI call, no internet, no writes outside the just-created project work/ and
its existing Game Bible. Existing games are NEVER modified or migrated.
"""
from __future__ import annotations

import html
import json
import re
import io
from urllib.parse import urlparse,parse_qs
import subprocess
from pathlib import Path

VERSION = '0.13.4'

BASE_CSS = r'''*{box-sizing:border-box}html,body{margin:0;min-height:100%;font:16px/1.5 system-ui,sans-serif;background:#0b1930;color:#f0f7ff}body{display:grid;place-items:center;padding:18px}main{width:min(700px,100%);padding:24px;border:4px solid #53bfbe;border-radius:12px;background:#1a3250;box-shadow:0 13px 35px #020812aa}h1{margin:0 0 6px;font-size:clamp(1.4rem,4vw,2rem)}h2{font-size:1rem}p{margin:6px 0 12px}button{font:inherit;cursor:pointer;border:2px solid #215369;border-radius:6px;padding:9px;min-width:36px;background:#f8e5ab;color:#122e41;font-weight:700}button:focus-visible{outline:3px solid #fe8f73;outline-offset:2px}button:hover{filter:brightness(1.1)}.hud{display:flex;align-items:center;gap:14px;flex-wrap:wrap;margin:10px 0 16px}.board{display:grid;grid-template-columns:repeat(8,minmax(0,1fr));gap:4px;max-width:540px;margin:auto}.tile{aspect-ratio:1;min-width:0;padding:2px;font-weight:900;font-size:clamp(.75rem,3vw,1.1rem)}.tile.open{background:#d3ebed}.tile.flagged{background:#f0bc86}.tile.mine{background:#ff8d87}.note{color:#bcd6e9;font-size:.9rem;margin-top:15px}#message{font-weight:700;color:#8ef8d2;min-height:1.5rem}.target{aspect-ratio:1;min-width:0;font-size:2rem}.target.active{background:#7be7a5;transform:scale(1.01)}'''

MINES_JS = r'''"use strict";
const SIZE=8,COUNT=10;const board=document.getElementById('board');const status=document.getElementById('message');const count=document.getElementById('count');const clock=document.getElementById('clock');let cells=[],mines=new Set(),ended=false,started=0,tick=null;
function adjacent(i){const x=i%SIZE,y=Math.floor(i/SIZE),out=[];for(let dy=-1;dy<=1;dy++)for(let dx=-1;dx<=1;dx++){if(!dx&&!dy)continue;let nx=x+dx,ny=y+dy;if(nx>=0&&nx<SIZE&&ny>=0&&ny<SIZE)out.push(ny*SIZE+nx)}return out}
function placeMines(safe){const available=Array.from({length:SIZE*SIZE},(_,i)=>i).filter(i=>i!==safe);for(let i=available.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[available[i],available[j]]=[available[j],available[i]]}mines=new Set(available.slice(0,COUNT))}
function render(){board.innerHTML='';cells.forEach((c,i)=>{const b=document.createElement('button');b.className='tile'+(c.open?' open':'')+(c.flag?' flagged':'')+(c.open&&mines.has(i)?' mine':'');b.type='button';b.textContent=c.open?(mines.has(i)?'💥':String(adjacent(i).filter(n=>mines.has(n)).length||'')):(c.flag?'🚩':'');b.setAttribute('aria-label',`Ruta ${i+1}, ${c.open?'öppen':c.flag?'flaggad':'stängd'}`);b.addEventListener('click',()=>reveal(i));b.addEventListener('contextmenu',e=>{e.preventDefault();flag(i)});board.append(b)});count.textContent=String(COUNT-cells.filter(c=>c.flag).length)}
function begin(i){if(started)return;placeMines(i);started=Date.now();tick=setInterval(()=>{clock.textContent=String(Math.floor((Date.now()-started)/1000))},250)}
function reveal(i){if(ended||cells[i].flag||cells[i].open)return;begin(i);const queue=[i];while(queue.length){const k=queue.pop(),c=cells[k];if(c.open||c.flag)continue;c.open=true;if(mines.has(k)){ended=true;status.textContent='En mina! Testa igen.';clearInterval(tick);break}if(!adjacent(k).some(n=>mines.has(n)))queue.push(...adjacent(k).filter(n=>!cells[n].open))}if(!ended&&cells.filter(c=>c.open).length===SIZE*SIZE-COUNT){ended=true;status.textContent='Du vann! 🎉';clearInterval(tick)}render()}
function flag(i){if(ended||cells[i].open)return;cells[i].flag=!cells[i].flag;render()}
function reset(){clearInterval(tick);cells=Array.from({length:SIZE*SIZE},()=>({open:false,flag:false}));mines.clear();ended=false;started=0;clock.textContent='0';status.textContent='Öppna en ruta för att börja.';render()}
document.getElementById('restart').addEventListener('click',reset);reset();
'''

ARCADE_JS = r'''"use strict";
const board=document.getElementById('board');const count=document.getElementById('count');const clock=document.getElementById('clock');const message=document.getElementById('message');let score=0,remaining=30,timer=null,active=-1,playing=false;
function draw(){board.replaceChildren();for(let i=0;i<16;i++){const b=document.createElement('button');b.className='target'+(i===active?' active':'');b.type='button';b.textContent=i===active?'⭐':'·';b.setAttribute('aria-label',i===active?'Fånga stjärnan':'Tom ruta');b.onclick=()=>hit(i);board.append(b)}count.textContent=score;clock.textContent=remaining}
function move(){active=Math.floor(Math.random()*16);draw()}
function hit(i){if(!playing||i!==active)return;score++;if(score>=10){finish('Du vann – tio stjärnor! 🎉');return}move()}
function finish(text){playing=false;clearInterval(timer);active=-1;message.textContent=text;draw()}
function start(){clearInterval(timer);score=0;remaining=30;playing=true;message.textContent='Fånga tio stjärnor innan tiden går ut.';move();timer=setInterval(()=>{remaining--;if(remaining<=0)finish('Tiden är ute – spela igen!');else draw()},1000)}
document.getElementById('restart').onclick=start;start();
'''


def _kind(payload):
    # A tiny genre-aware fallback. Never promise production-quality generation.
    hint=' '.join(str(payload.get(k) or '')[:300] for k in ('name','idea','genre')).casefold()
    return 'mines' if re.search(r'minesweeper|minröj|minr[oö]j|minefält',hint) else 'arcade'


def _html(name,kind):
    name=html.escape(name,quote=True)
    mines=kind=='mines'
    header=('Minröjare – första spelbara grund' if mines else 'Första spelbara grund – samla stjärnor')
    instructions=('Öppna rutorna utan att träffa en mina. Högerklicka för att flagga. Första rutan är säker.' if mines else 'Klicka på tio stjärnor innan 30 sekunder har gått. Det här är en generell startprototyp, inte spelets färdiga mekanik.')
    label='Flaggor kvar' if mines else 'Poäng'
    return f'''<!doctype html>\n<html lang="sv"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{name} – prototyp</title><link rel="stylesheet" href="style.css"></head>\n<body><main><h1>{name}</h1><p>🎮 {header}</p><p>{instructions}</p><div class="hud"><span>{label}: <strong id="count">0</strong></span><span>Tid: <strong id="clock">0</strong> s</span><button id="restart" type="button">🔄 Starta om</button></div><div id="board" class="board" aria-label="Spelplan"></div><p id="message" role="status" aria-live="polite"></p><p class="note">Pixel Works · automatiskt skapad <strong>lokal startprototyp</strong>. Inte AI-genererat slutresultat. Game Bible och arbetsordrar styr vidare utveckling.</p></main><script src="game.js"></script></body></html>\n'''


def bootstrap(srv,slug,payload):
    """Idempotent only on brand-new project with no existing index.html.

    Not a migration tool: don't alter or overwrite any existing project files.
    """
    project=srv.path_for(slug)
    work=project/'work';bible=project/'studio-bible'/'GAME_BIBLE.md'
    if work.is_symlink() or bible.is_symlink() or not work.is_dir() or not bible.is_file():
        raise ValueError('Nyprojektets arbetsytor är inte säkra eller saknas')
    if any((work/n).exists() or (work/n).is_symlink() for n in ('index.html','style.css','game.js')):
        raise ValueError('Spelet har redan en startprototyp eller spelkod; inga filer skrivs över')
    # An older project may have unrelated worker-produced content. Never place
    # a generic starter alongside real game code or asset directories.
    other=[p.name for p in work.iterdir() if p.name not in ('AGENTS.md','README.md','.git')]
    if other:raise ValueError('Spelmappen har redan annat innehåll ('+', '.join(other[:3])+'). Ingen startmall får ersätta det.')
    kind=_kind(payload)
    name=str(payload.get('name') or slug)[:90]
    files={'index.html':_html(name,kind),'style.css':BASE_CSS+'\n', 'game.js':MINES_JS if kind=='mines' else ARCADE_JS}
    # Do not write arbitrary filenames or user-controlled JS/CSS. Only fixed assets.
    for key,content in files.items():
        (work/key).write_text(content,encoding='utf-8')
    with bible.open('a',encoding='utf-8') as out:
        out.write('\n## Första spelbara prototyp (automatisk startpunkt)\n'
                  'Status: SKAPAD LOKALT som en minimal HTML5-prototyp. Inte AI-granskad eller färdig spelproduktion.\n\n'
                  '- Körbar fil: `work/index.html` (med `style.css` och `game.js`).\n'
                  '- Grundmekanik: '+('8×8 minröjare med 10 minor, flaggor och omstart.' if kind=='mines' else '30 sekunders klickspel – samla tio stjärnor.')+'\n'
                  '- Spelguidens val och projektägarens vision har företräde framför startmallen.\n'
                  '- Chefen ska planera förbättringar, grafik, ljud, spelmekanik och tester som riktiga arbetsordrar.\n'
                  '- Programmeraren ska förbättra/ersätta prototypen, aldrig påstå att spelet redan är klart.\n')
    # Seed the first LOCAL snapshot: Codex worker-tree scheduler requires HEAD.
    # Stage a strict allowlist; do not accidentally commit secrets/user files.
    def git(*args):
        return subprocess.run(['git','-C',str(work),*args],capture_output=True,text=True,timeout=22)
    status=git('rev-parse','--show-toplevel')
    if status.returncode or Path(status.stdout.strip()).resolve()!=work.resolve():
        raise ValueError('Startprototypen skapades, men Git-arbetsytan kan inte verifieras')
    staged=git('add','--','index.html','style.css','game.js','AGENTS.md','README.md')
    if staged.returncode:raise ValueError('Startprototypen skapades men kunde inte förberedas i Git: '+staged.stderr[-150:])
    commit=subprocess.run(['git','-C',str(work),'-c','user.name=Pixel Works',
                '-c','user.email=pixelworks@localhost','commit','-m','Pixel Works: första spelbara grund'],
                capture_output=True,text=True,timeout=32)
    if commit.returncode:raise ValueError('Startprototypen skapades men första Git-versionen misslyckades: '+commit.stderr[-200:])
    return {'template':kind,'verified_on_disk':True,'first_local_commit':True,
            'status':'startprototyp','entry_point':'index.html','ai_generated':False}


def inspect(srv,slug):
    """Pure read: preview readiness and whether safe user-triggered bootstrap exists."""
    project=srv.path_for(slug);work=project/'work'
    if work.is_symlink() or not work.is_dir():return {'can_bootstrap':False,'playable':False,'reason':'Spelmappen saknas'}
    playable=(work/'index.html').is_file() and not (work/'index.html').is_symlink()
    others=[p.name for p in work.iterdir() if p.name not in ('AGENTS.md','README.md','.git')]
    can_bootstrap=not others and (work/'AGENTS.md').is_file()
    return {'can_bootstrap':can_bootstrap,'playable':playable,
            'reason':('Startprototyp finns.' if playable else
                      'Du kan skapa en liten spelbar startpunkt utan AI-anrop.' if can_bootstrap else
                      'Spelmappen innehåller redan annat arbete; inget skrivs över.')}


def bootstrap_existing(srv,slug,payload):
    if payload.get('approval')!='CREATE_PLAYABLE_START_V0134':
        raise ValueError('Välj Skapa spelbar grund i det aktuella spelet')
    project=srv.path_for(slug);meta=project/'project.json'
    if meta.is_symlink() or not meta.is_file():raise ValueError('Projektfil saknas')
    data=json.loads(meta.read_text(encoding='utf-8'))
    if data.get('id')!=slug:raise ValueError('Fel projekt-ID')
    return bootstrap(srv,slug,{'name':data.get('name',slug),'idea':data.get('idea',''),'genre':data.get('genre','')})


def install(srv):
    if getattr(srv,'_PW_V0134',False):return
    srv._PW_V0134=True
    previous=srv.create_project
    def create_project(payload):
        result=previous(payload)
        slug=srv.validate_slug(payload.get('slug'))
        try:starter=bootstrap(srv,slug,payload)
        except (OSError,ValueError,RuntimeError,subprocess.TimeoutExpired) as e:
            # Never throw after the base project has already been created:
            # retrying the create route would cause a misleading slug collision.
            result['playable_bootstrap']={'status':'failed','reason':str(e)[:260]}
        else:result['playable_bootstrap']=starter
        return result
    srv.create_project=create_project
    old_get=srv.Handler.do_GET;old_post=srv.Handler.do_POST
    def get(self):
        if urlparse(self.path).path!='/api/pw-v0134/bootstrap':return old_get(self)
        if not self.allowed() or not self.auth():return self.reply(403,{'error':'Inte tillåtet'})
        try:
            slug=srv.validate_slug(parse_qs(urlparse(self.path).query).get('project',[''])[0])
            return self.reply(200,{'project':slug,**inspect(srv,slug)})
        except (ValueError,OSError,TypeError) as e:return self.reply(400,{'error':str(e)[:240]})
    def post(self):
        if urlparse(self.path).path!='/api/pw-v0134/bootstrap':return old_post(self)
        if not self.allowed() or not self.same_origin() or not self.auth():
            return self.reply(403,{'error':'Inte tillåtet'})
        n=self.headers.get('Content-Length','')
        if not n.isdecimal() or not 0<int(n)<=2500:return self.reply(413,{'error':'Ogiltig begäran'})
        try:
            data=json.loads(self.rfile.read(int(n)))
            if not isinstance(data,dict):raise ValueError('JSON-objekt krävs')
            slug=srv.validate_slug(data.get('project'))
            return self.reply(200,{'project':slug,**bootstrap_existing(srv,slug,data)})
        except (ValueError,OSError,RuntimeError,TypeError,subprocess.TimeoutExpired) as e:
            return self.reply(409,{'error':str(e)[:270]})
    srv.Handler.do_GET=get;srv.Handler.do_POST=post
    srv.APP_VERSION=VERSION
