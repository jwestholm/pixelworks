"""Pixel Works – player-facing media decisions for real Freesound and worker outputs.

Game first: offers belong to the project's normal orders, not a second agent.
No AI or external calls on GET/poll. Sound previews are fetched only on click.
Only explicit YES imports sound; NO with feedback creates a normal work order.
Already-integrated worker code is never mislabeled as waiting for approval.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import re
import secrets
import shutil
import tempfile
import wave
import subprocess
import threading
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from urllib.request import Request, build_opener
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlparse

LOCK = threading.RLock()
HEX12 = re.compile(r'^[a-f0-9]{12}$')
HEX16 = re.compile(r'^[a-f0-9]{16}$')
SAFE_MEDIA = {'.png':'image/png','.jpg':'image/jpeg','.jpeg':'image/jpeg',
              '.gif':'image/gif','.webp':'image/webp',
              '.mp3':'audio/mpeg','.wav':'audio/wav','.ogg':'audio/ogg'}
MAX_BYTES = 8 * 1024 * 1024
MAX_IMAGES = 8
BASE = '/api/pw-tools/review'


def now(): return datetime.now(timezone.utc).isoformat()


def _base(srv, slug):
    slug = srv.validate_slug(slug)
    srv.verify_project(slug)
    folder = srv.path_for(slug) / 'management'
    if folder.is_symlink() or not folder.is_dir(): raise ValueError('Osäker projektmapp')
    return slug, folder


def _records(srv, slug):
    slug, folder = _base(srv, slug)
    path = folder / 'media-review.json'
    if path.is_symlink(): raise ValueError('Osäkert granskningsarkiv')
    if not path.is_file(): return []
    data = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(data,list) or len(data)>600: raise ValueError('Ogiltigt granskningsarkiv')
    return data


def _write(srv, slug, rows):
    _, folder = _base(srv, slug)
    target = folder/'media-review.json'
    if target.is_symlink():raise ValueError('Osäkert granskningsarkiv')
    temp = folder/('.media-review-'+secrets.token_hex(7))
    try:
        fd = os.open(temp, os.O_CREAT|os.O_EXCL|os.O_WRONLY, 0o600)
        with os.fdopen(fd,'w',encoding='utf-8') as f:json.dump(rows[-600:],f,ensure_ascii=False,indent=2)
        os.replace(temp,target)
    finally:temp.unlink(missing_ok=True)


def _short(item):
    return {k:item.get(k) for k in ('id','kind','title','description','employee','job_id','order_id',
           'source','preview_available','already_integrated','license','username','url','status',
           'feedback','created_at','station','reason','followup_order','tool_events')}


def _sound_offers(srv, slug):
    try: import pw_freesound as f
    except ImportError:return []
    try: jobs=f.overview(srv,slug).get('jobs',[])
    except (ValueError,OSError,TypeError):return []
    out=[]
    for job in jobs:
        if job.get('status') != 'done':continue
        for sound in job.get('suggestions') or []:
            if not isinstance(sound,dict) or type(sound.get('id')) is not int:continue
            key='sound:'+str(job['id'])+':'+str(sound['id'])
            if not f.safe_preview(sound.get('preview')):continue
            approved=any(x.get('sound_id')==sound['id'] for x in job.get('approved') or [])
            out.append({'id':key,'kind':'audio','title':sound.get('name') or 'Ljudförslag',
                'description':sound.get('reason') or 'Förslag utifrån Freesound-metadata, inte provlyssnat av AI.',
                'employee':job.get('employee'),'job_id':job.get('core_job_id') or job.get('id'),
                'order_id':job.get('order_id'),'station':'music','source':'freesound',
                'preview_available':True,'already_integrated':False,
                'license':sound.get('license'),'username':sound.get('username'),
                'url':sound.get('url'),'status':'approved' if approved else 'waiting',
                'tool_events':[{k:e.get(k) for k in ('kind','message','query','raw_count','result_count')}
                   for e in (job.get('tool_events') or [])[-12:] if isinstance(e,dict)],
                'reason':'Förslaget har inte infogats i spelkoden.'})
    return out


def overview(srv, slug):
    slug,_=_base(srv,slug)
    with LOCK:reviews=_records(srv,slug)
    statuses={x['id']:x for x in reviews}
    collection=_sound_offers(srv,slug)
    for rec in reviews:
        if rec.get('source')=='agent-file' or rec.get('source')=='missing-preview':
            collection.append(_short(rec))
    output=[]
    for item in collection:
        stored=statuses.get(item['id'])
        if stored and stored.get('status') in ('approved','rejected','maybe'):
            item={**item,'status':stored['status'],'feedback':stored.get('feedback',''),
                  'followup_order':stored.get('followup_order')}
        output.append(_short(item))
    output.sort(key=lambda x:x.get('created_at') or '',reverse=True)
    return {'offers':output[:80],'waiting':sum(x['status']=='waiting' for x in output),
            'note':'Syntetiska Web Audio-ljud utan exporterad fil kan ännu inte förhandslyssnas. Skicka feedback för att beställa en lyssningsfil.'}


def _safe_file(srv, slug, item):
    slug,_=_base(srv,slug)
    if item.get('source')!='agent-file':raise ValueError('Inte en fil från en agent')
    job_id=item.get('job_id')
    if not isinstance(job_id,str) or not HEX12.fullmatch(job_id):raise ValueError('Ogiltigt arbets-ID')
    rel=item.get('relative_path')
    if not isinstance(rel,str) or len(rel)>220:raise ValueError('Osäker filsökväg')
    part=PurePosixPath(rel)
    if part.is_absolute() or not part.parts or any(p in ('.','..') or p.startswith('.') for p in part.parts):
        raise ValueError('Osäker filsökväg')
    ext=part.suffix.lower()
    if ext not in SAFE_MEDIA: raise ValueError('Filtypen kan inte förhandsvisas')
    project=srv.path_for(slug)
    # Prefer integrated work; a still-unmerged result may remain in that exact job's worktree.
    roots=[project/'work',project/'management'/'worktrees'/('job-'+job_id)]
    for root in roots:
        if root.is_symlink() or not root.is_dir():continue
        path=root.joinpath(*part.parts)
        if path.is_symlink() or any(p.is_symlink() for p in list(path.parents)[:-1] if p!=root):continue
        try:
            if not path.is_file() or not path.resolve().is_relative_to(root.resolve()):continue
            size=path.stat().st_size
            if size<12 or size>MAX_BYTES:continue
            raw=path.read_bytes()
            if hashlib.sha256(raw).hexdigest()!=item.get('sha256'):continue
            mime=SAFE_MEDIA[ext]
            # Content-based validation for main formats.
            if ext=='.png' and not raw.startswith(b'\x89PNG\r\n\x1a\n'):continue
            if ext in ('.jpg','.jpeg') and not raw.startswith(b'\xff\xd8\xff'):continue
            if ext=='.webp' and not(raw.startswith(b'RIFF') and raw[8:12]==b'WEBP'):continue
            if ext=='.gif' and not raw.startswith((b'GIF87a',b'GIF89a')):continue
            if ext=='.wav' and not(raw.startswith(b'RIFF') and raw[8:12]==b'WAVE'):continue
            if ext=='.ogg' and not raw.startswith(b'OggS'):continue
            if ext=='.mp3' and not(raw.startswith(b'ID3') or (raw[0]==255 and (raw[1]&224)==224)):continue
            return raw,mime
        except OSError:continue
    raise ValueError('Förhandsfilen saknas, är för stor eller har ändrats')



def _audition(raw, mime):
    """Prepare a real, browser-decodable, bounded audition, never just a file signature.

    ffmpeg (when installed) decodes the input and exports 20s of standard PCM WAV.
    Without ffmpeg, validate WAV via the stdlib. MP3/OGG require ffprobe when
    available; if neither binary exists Firefox's decode check is authoritative.
    No external network, no shell and no project writes happen here.
    """
    if not mime.startswith('audio/'):
        raise ValueError('Ljudfil förväntas')
    # Do not claim a header is equivalent to an audible preview.
    decoder = shutil.which('ffmpeg')
    if decoder:
        with tempfile.TemporaryDirectory(prefix='pw-audition-') as d:
            folder = Path(d)
            src = folder / ('sound.mp3' if mime=='audio/mpeg' else 'sound.ogg' if mime=='audio/ogg' else 'sound.wav')
            dst = folder / 'audition.wav'
            src.write_bytes(raw)
            command=[decoder,'-nostdin','-hide_banner','-loglevel','error','-y',
                     '-protocol_whitelist','file,pipe','-i',str(src),'-map','0:a:0',
                     '-threads','1','-t','20','-vn','-ac','1',
                     '-ar','24000','-c:a','pcm_s16le',str(dst)]
            try: result = subprocess.run(command, capture_output=True, timeout=16, check=False)
            except (subprocess.TimeoutExpired,OSError):
                raise ValueError('Ljudavkodning tog för lång tid. Prova ett annat förslag.') from None
            if result.returncode or not dst.is_file():
                raise ValueError('Ljudfilen kunde inte avkodas. Välj ett annat ljud eller be agenten exportera WAV.')
            normalized=dst.read_bytes()
        try:
            with wave.open(__import__('io').BytesIO(normalized),'rb') as wav:
                seconds=wav.getnframes()/wav.getframerate() if wav.getframerate() else 0
                if wav.getnchannels()!=1 or wav.getsampwidth()!=2 or seconds<=0.04:
                    raise ValueError('Ljudfilen saknar spelbart ljud')
        except (wave.Error, EOFError, OSError, ZeroDivisionError):
            raise ValueError('Förhandsfilen gick inte att avkoda till WAV.') from None
        return {'mime':'audio/wav','base64':base64.b64encode(normalized).decode('ascii'),
                'bytes':len(normalized),'seconds':round(seconds,2),
                'excerpt':seconds>=19.9,'verified_decode':True}
    if mime=='audio/wav':
        try:
            with wave.open(__import__('io').BytesIO(raw),'rb') as wav:
                seconds=wav.getnframes()/wav.getframerate() if wav.getframerate() else 0
                if seconds<=0.04 or wav.getsampwidth() not in (1,2,3,4):
                    raise ValueError('Ljudfilen saknar spelbart ljud')
        except (wave.Error, EOFError, OSError, ZeroDivisionError):
            raise ValueError('WAV-filen går inte att läsa. Be agenten exportera en vanlig PCM-WAV.') from None
        return {'mime':mime,'base64':base64.b64encode(raw).decode('ascii'),
                'bytes':len(raw),'seconds':round(seconds,2),'excerpt':False,'verified_decode':True}
    # ffprobe can validate MP3/OGG even when conversion isn't installed.
    probe=shutil.which('ffprobe')
    seconds=0.0
    if probe:
        with tempfile.TemporaryDirectory(prefix='pw-probe-') as d:
            path=Path(d)/('audio.mp3' if mime=='audio/mpeg' else 'audio.ogg')
            path.write_bytes(raw)
            try:
                r=subprocess.run([probe,'-v','error','-show_entries',
                    'format=duration:stream=codec_type','-of','json',str(path)],
                    capture_output=True,text=True,timeout=8,check=False)
                data=json.loads(r.stdout) if r.returncode==0 else {}
                seconds=float((data.get('format') or {}).get('duration') or 0)
                if not any(x.get('codec_type')=='audio' for x in data.get('streams',[])) or seconds<=0.04:
                    raise ValueError('Filen innehåller inte avkodningsbart ljud')
            except (ValueError,TypeError,subprocess.TimeoutExpired,OSError):
                raise ValueError('Ljudfilen gick inte att avkoda. Prova ett annat ljud.') from None
    return {'mime':mime,'base64':base64.b64encode(raw).decode('ascii'),
            'bytes':len(raw),'seconds':round(seconds,2),'excerpt':False,
            'verified_decode':bool(probe)}


def preview(srv, slug, offer_id):
    slug,_=_base(srv,slug)
    offer=next((x for x in overview(srv,slug)['offers'] if x['id']==offer_id),None)
    if not offer or not offer.get('preview_available'):raise ValueError('Inget tillgängligt förhandsprov')
    if offer['source']=='freesound':
        import pw_freesound as f
        # Re-resolve the server-stored URI, never accept URLs from the browser.
        parts=offer_id.split(':')
        if len(parts)!=3 or not HEX16.fullmatch(parts[1]) or not parts[2].isdigit():raise ValueError('Ogiltigt förslag')
        rec=f.read(srv,slug,parts[1])
        sound=next((x for x in rec.get('suggestions',[]) if str(x.get('id'))==parts[2]),None)
        if not sound:raise ValueError('Ljudförslaget finns inte')
        url=f.safe_preview(sound.get('preview'))
        if not url:raise ValueError('Osäker ljudlänk')
        # Accept only a Freesound-owned preview, no redirects to untrusted hosts.
        with build_opener(f.NoRedirect()).open(Request(url,headers={'User-Agent':'PixelWorksMediaReview/1.0'}),timeout=18) as resp:
            content_type=resp.headers.get('Content-Type','').split(';')[0].strip().lower()
            if content_type not in ('audio/mpeg','audio/mp3','application/octet-stream'):
                raise ValueError('Freesound lämnade ingen MP3-fil')
            raw=resp.read(MAX_BYTES+1)
        if len(raw)<16 or len(raw)>MAX_BYTES or not(raw.startswith(b'ID3') or(raw[0]==255 and(raw[1]&224)==224)):
            raise ValueError('Förhandsprovet är inte en giltig MP3-fil')
        return _audition(raw,'audio/mpeg')
    with LOCK:
        rec=next((r for r in _records(srv,slug) if r.get('id')==offer_id),None)
    if not rec:raise ValueError('Förhandsfilen finns inte')
    raw,mime=_safe_file(srv,slug,rec)
    if mime.startswith('audio/'):
        return _audition(raw,mime)
    return {'mime':mime,'base64':base64.b64encode(raw).decode('ascii'),'bytes':len(raw)}



def _material_from_agent(srv, slug, offer, station):
    """Copy an approved/revision source to the existing protected task-materials store.

    A source-file name is never accepted from the browser: the recorded worktree
    path, project ownership and recorded SHA-256 are rechecked by _safe_file.
    """
    import pw_v01210
    with LOCK:
        item=next((x for x in _records(srv,slug) if x.get('id')==offer['id']),None)
    if not item:raise ValueError('Agentens ursprungliga fil saknas')
    raw,_mime=_safe_file(srv,slug,item)
    name=PurePosixPath(item['relative_path']).name[:115]
    return pw_v01210.save_material(srv,{
        'project':slug,'station':station,'name':name,
        'comment':'Arbetsunderlag valt från agentens faktiska resultat. Säkert kopierad från tidigare arbetsgren.',
        'data':base64.b64encode(raw).decode('ascii')})


def decide(srv, body):
    slug,_=_base(srv,body.get('project'))
    ident=body.get('offer_id')
    if not isinstance(ident,str) or len(ident)>90:raise ValueError('Ogiltigt förslags-ID')
    decision=body.get('decision')
    if decision not in ('yes','no','maybe'):raise ValueError('Välj Ja, Nej eller Kanske')
    feedback=body.get('feedback','')
    if not isinstance(feedback,str) or len(feedback)>700:raise ValueError('Feedback får vara högst 700 tecken')
    feedback=feedback.strip()
    with LOCK:
        candidates={x['id']:x for x in overview(srv,slug)['offers']}
        offer=candidates.get(ident)
        if not offer:raise ValueError('Förslaget finns inte i detta projekt')
        saved=_records(srv,slug)
        old=next((r for r in saved if r.get('id')==ident),None)
        if old and old.get('status') in ('approved','rejected'):
            raise ValueError('Det här förslaget är redan avslutat')
        if decision=='yes' and not offer.get('preview_available'):
            raise ValueError('Inget ljud eller bild att godkänna. Be om en exporterad förhandsfil.')
        order_id=None
        if decision=='yes' and offer['source']=='freesound':
            import pw_freesound as f
            _, jid, sid=ident.split(':')
            item=f.approve(srv,{'project':slug,'job_id':jid,'sound_id':int(sid),'approval':'APPROVE_FREESOUND_PREVIEW'})
            # Also copy the approved preview into the existing job-material system.
            # The agent gets a safe, staged file path (never our secrets folder).
            # No external search or AI call occurs here; the player already chose YES.
            import pw_v01210
            asset=item['asset']
            if not asset.get('filename'):
                # An older dialog may have approved this before this inbox did.
                entry=next((a for a in f.overview(srv,slug)['library']
                            if a.get('id')==asset.get('asset_id')),None)
                if not entry:raise ValueError('Importerat ljud saknar en användbar biblioteksfil')
                asset=entry
            name='freesound-'+str(sid)+'.mp3'
            lib=f.library_path(srv,slug)
            audio=lib/asset['filename']
            if (audio.is_symlink() or not audio.is_file() or
                    audio.resolve().parent!=lib.resolve() or audio.stat().st_size>8*1024*1024):
                raise ValueError('Ljudfilen kan inte överföras till arbetaren på ett säkert sätt')
            material=pw_v01210.save_material(srv,{'project':slug,'station':'music',
                'name':name,'comment':'Spelägaren valde detta Freesound-förhandsprov. Källan och licensen finns i Freesound-biblioteket.',
                'data':base64.b64encode(audio.read_bytes()).decode('ascii')})
            note=('Godkänt Freesound-ljud: '+str(asset.get('name') or name)[:110]
                  +'. [[PW12_ATTACH:'+material['id']+']]'
                  +' Använd den iscensatta MP3-filen som data, infoga den där den passar och dokumentera exakt vad som införts. '
                  +'Originalkvaliteten är inte hämtad – detta är ett MP3-förhandsprov. '
                  +'Spelarens feedback: '+(feedback or 'Använd ljudet i spelet.'))
            result=srv.order_action(slug,{'action':'create','station':'music','priority':2,
                                        'instruction':note[:2000]})
            order_id=(result.get('item') or {}).get('id') if isinstance(result,dict) else None
        elif decision=='yes' and offer['source']=='agent-file':
            # Actual assets already in code are NOT rolled back or reintegrated.
            # An unmerged agent-file needs a normal integration task; approval by
            # itself must never silently merge an arbitrary Codex worktree.
            if not offer.get('already_integrated'):
                station=offer.get('station') or ('art' if offer.get('kind')=='image' else 'music')
                if station not in ('art','music','voice','code'):station='art' if offer.get('kind')=='image' else 'music'
                material=_material_from_agent(srv,slug,offer,station)
                instruction=('Spelägaren godkände '+str(offer.get('title') or 'mediefilen')[:110]
                     +' som ska användas i spelet. [[PW12_ATTACH:'+material['id']+']] '
                     +'Arbeta med den iscensatta originalfilen från agentens resultat; integrera '
                     +'den bara där den passar Game Bible och redovisa faktiskt testade saker. '
                     +'Eventuell extra feedback: '+(feedback or 'Ingen.') )
                result=srv.order_action(slug,{'action':'create','station':station,'priority':2,
                                             'instruction':instruction[:2000]})
                order_id=(result.get('item') or {}).get('id') if isinstance(result,dict) else None
        elif decision=='no' and feedback:
            # Revisions go through the real queue, never an unapproved immediate AI call.
            station=offer.get('station') or ('art' if offer.get('kind')=='image' else 'music')
            if station not in ('art','music','voice','code'):
                station='art' if offer.get('kind')=='image' else 'music'
            source_note=''
            if offer.get('source')=='agent-file':
                material=_material_from_agent(srv,slug,offer,station)
                source_note='\nUrsprunglig fil som data: [[PW12_ATTACH:'+material['id']+']]'
            prompt=('Ändra tidigare förslag: '+str(offer.get('title') or 'medieförslag')+'\n'
                    'Spelarens feedback: '+feedback+source_note+'\n'
                    'Förhandsgranska det nya resultatet med en riktig exporterad '
                    'PNG/JPEG/WebP/GIF-bild eller MP3/WAV/OGG-fil. '
                    'Rapportera vilka tester som faktiskt körts. Gör inga externa publiceringar.')
            result=srv.order_action(slug,{'action':'create','station':station,'priority':2,'instruction':prompt[:2000]})
            order_id=(result.get('item') or {}).get('id') if isinstance(result,dict) else None
        new_status={'yes':'approved','no':'rejected','maybe':'maybe'}[decision]
        entry={**(old or {}),'id':ident,'project':slug,'status':new_status,
               'feedback':feedback,'followup_order':order_id,'updated_at':now()}
        if old:saved[saved.index(old)]=entry
        else:saved.append(entry)
        _write(srv,slug,saved)
        return {'decision':new_status,'followup_order':order_id,'offer_id':ident}


def _new_worker_media(srv, job, instruction):
    """Record actual media files newly added/modified by one completed worker commit.

    This is never a broad project scan. A core job's branch HEAD must have an
    exact agent-result commit subject. Manifest is optional; the repository's
    own changed-file list is authoritative for file provenance.
    """
    slug=job.get('project'); jid=job.get('id')
    if not isinstance(jid,str) or not HEX12.fullmatch(jid):return []
    if job.get('state') not in ('done','review'):return []
    slug,_=_base(srv,slug)
    root=srv.path_for(slug)/'management'/'worktrees'/('job-'+jid)
    if root.is_symlink() or not root.is_dir():return []
    try:
        def git(*args):
            p=subprocess.run(['git','-C',str(root),*args],capture_output=True,text=True,timeout=7,check=False)
            if p.returncode:raise RuntimeError('Git kunde inte läsa arbetsresultatet')
            return p.stdout
        header=git('log','-1','--pretty=%s').strip()
        if header!='Pixel Works: agentresultat '+jid:return []
        names=git('diff-tree','--root','--no-commit-id','--name-only','--diff-filter=AM','-r','HEAD').splitlines()
    except (OSError,RuntimeError,subprocess.TimeoutExpired):return []
    out=[]
    for name in names:
        path=PurePosixPath(name)
        if path.suffix.lower() not in SAFE_MEDIA:continue
        source={'id':'file:'+jid+':'+hashlib.sha256(name.encode()).hexdigest()[:16],
                'project':slug,'source':'agent-file','job_id':jid,'order_id':job.get('order_id'),
                'employee':job.get('agent_name'),'station':job.get('station'),
                'kind':'image' if SAFE_MEDIA[path.suffix.lower()].startswith('image/') else 'audio',
                'title':path.name[:110],'description':'Fil från ett verkligt Codex-jobb; inga påstådda automatiska kvalitetskontroller.',
                'relative_path':name,'already_integrated':bool(job.get('integrated')),
                'preview_available':True,'created_at':now(),'status':'waiting'}
        try:
            file=root.joinpath(*path.parts)
            if file.is_symlink() or not file.is_file() or not file.resolve().is_relative_to(root.resolve()):continue
            if not 12<=file.stat().st_size<=MAX_BYTES:continue
            source['sha256']=hashlib.sha256(file.read_bytes()).hexdigest()
            _safe_file(srv,slug,source)
            out.append(source)
            if len(out)>=MAX_IMAGES:break
        except (ValueError,OSError):continue
    return out


def capture_worker(srv, job):
    if not isinstance(job,dict) or not job.get('id') or job.get('state') not in ('done','review'):return
    if job.get('station') not in ('music','voice','art','code'):return
    try:
        captured=_new_worker_media(srv,job,'')
        slug=job['project']
        with LOCK:
            rows=_records(srv,slug)
            ids={x.get('id') for x in rows}
            added=0
            for item in captured:
                if item['id'] not in ids:
                    rows.append(item);added+=1
            # Pure procedural Web Audio has no file to preview; honestly request export.
            if not captured and job.get('station') in ('music','voice','art'):
                missing='missing:'+str(job['id'])
                if missing not in ids:
                    rows.append({'id':missing,'project':slug,'source':'missing-preview','job_id':job['id'],
                        'order_id':job.get('order_id'),'employee':job.get('agent_name'),
                        'station':job.get('station'),'kind':'image' if job['station']=='art' else 'audio',
                        'title':'Förhandsprov saknas',
                        'description':'Agenten avslutade arbetet men levererade ingen faktisk bild/ljudfil att förhandsvisa. Om ljudet genereras av Web Audio måste en lyssningsfil exporteras.',
                        'preview_available':False,'already_integrated':bool(job.get('integrated')),
                        'status':'waiting','created_at':now()});added+=1
            if added:_write(srv,slug,rows)
    except (ValueError,OSError,TypeError,KeyError):return


def _allow_local_media_previews(csp):
    """Allow only locally-created image/audio Blob URLs in Pixel Works' CSP.

    The stable core sets default-src 'self' and img-src 'self' data:.
    Without explicit media-src blob: and img-src blob:, Firefox blocks valid
    locally decoded preview bytes (the same bug affects Chromium). Keep all
    script/connect/object and other CSP directives unchanged.
    """
    if not isinstance(csp,str):return csp
    directives=[part.strip() for part in csp.split(';') if part.strip()]
    found_media=False
    found_img=False
    for index,part in enumerate(directives):
        words=part.split()
        if not words:continue
        key=words[0].lower()
        if key=='media-src':
            found_media=True
            if 'blob:' not in words: directives[index]=part+' blob:'
        elif key=='img-src':
            found_img=True
            if 'blob:' not in words: directives[index]=part+' blob:'
    if not found_media:directives.append("media-src 'self' blob:")
    if not found_img:directives.append("img-src 'self' blob:")
    return '; '.join(directives)


def install(srv):
    if getattr(srv,'_PW_MEDIA_REVIEW_INSTALLED',False):return
    srv._PW_MEDIA_REVIEW_INSTALLED=True
    # This wrapper is installed after Freesound's preflight wrapper.
    # It adds a short instruction to produce *real* preview files if creating
    # art/audio, and records output files after the normal worker has finished.
    worker=getattr(srv,'run_codex',None)
    if callable(worker):
        def with_review(jid,slug,instruction):
            with srv.LOCK:job=dict(srv.JOBS.get(jid) or {})
            extra=''
            if job.get('station') in ('art','music','voice'):
                extra=('\n\nSPELARENS MEDIAFÖRHANDSGRANSKNING: Om du skapar eller ändrar bild eller ljud, '
                       'leverera också en riktig förhandsfil i projektets arbetsyta: PNG/JPEG/WebP/GIF för bilder, '
                       'MP3/WAV/OGG för ljud. Högst 8 MB per fil. Gör inte påståenden om att förhandsprovet '
                       'spelats upp eller granskats om det inte faktiskt skett. '
                       'För procedurellt Web Audio: dokumentera om export till WAV inte är möjlig i arbetsmiljön. '
                       'Inga externa licens- eller nätverksanrop krävs för detta. ')
            result=worker(jid,slug,instruction+extra)
            with srv.LOCK:completed=dict(srv.JOBS.get(jid) or {})
            capture_worker(srv,completed)
            return result
        srv.run_codex=with_review
    if not hasattr(srv,'Handler'):return
    # The core's end_headers() emits the CSP via send_header(). Intercept only
    # that header rather than sending a SECOND CSP (browsers intersect policies).
    # This preserves the stable core and leaves script-src, connect-src and
    # frame-ancestors exactly as restrictive as before.
    previous_send_header=srv.Handler.send_header
    def send_header(self, keyword, value):
        if str(keyword).lower()=='content-security-policy':
            value=_allow_local_media_previews(value)
        return previous_send_header(self,keyword,value)
    srv.Handler.send_header=send_header
    prev_get=srv.Handler.do_GET;prev_post=srv.Handler.do_POST
    def do_GET(self):
        url=urlparse(self.path)
        if url.path not in (BASE,BASE+'/preview'):return prev_get(self)
        if not self.allowed() or not self.auth():return self.reply(403,{'error':'Ogiltig session'})
        try:
            qs=parse_qs(url.query);slug=qs.get('project',[''])[0]
            if url.path==BASE+'/preview':
                return self.reply(200,preview(srv,slug,qs.get('id',[''])[0]))
            return self.reply(200,overview(srv,slug))
        except (ValueError,RuntimeError,HTTPError,URLError,OSError,TypeError,KeyError) as err:
            return self.reply(400,{'error':str(err)[:200]})
    def do_POST(self):
        if urlparse(self.path).path!=BASE:return prev_post(self)
        if not self.allowed() or not self.auth() or not self.same_origin():
            return self.reply(403,{'error':'Otillåten begäran'})
        size=self.headers.get('Content-Length','')
        if not size.isdecimal() or not 0<int(size)<=2500:return self.reply(413,{'error':'Ogiltig begäran'})
        try:
            payload=json.loads(self.rfile.read(int(size)))
            if not isinstance(payload,dict):raise ValueError('Ogiltigt formulär')
            return self.reply(200,decide(srv,payload))
        except (ValueError,RuntimeError,HTTPError,URLError,OSError,TypeError,KeyError) as err:
            return self.reply(400,{'error':str(err)[:250]})
    srv.Handler.do_GET=do_GET;srv.Handler.do_POST=do_POST
