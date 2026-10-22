"""Regression: office sprites must contain non-identical frames, without PIL dependency."""
from pathlib import Path
import re
import struct
import unittest
import zlib

from backend import server

ASSETS=server.APP/'assets'/'office-v2'
CSS=(server.APP/'visual-v2.css').read_text(encoding='utf-8')


def pixels_rgba(path):
    """Decode our simple 8-bit RGBA PNGs using stdlib only."""
    blob=path.read_bytes()
    if not blob.startswith(b'\x89PNG\r\n\x1a\n'):
        raise ValueError('Not PNG')
    off=8;payload=bytearray();width=height=None
    while off<len(blob):
        n=struct.unpack_from('>I',blob,off)[0]
        kind=blob[off+4:off+8]
        dat=blob[off+8:off+8+n]
        off+=12+n
        if kind==b'IHDR':
            width,height,depth,color,_,_,interlace=struct.unpack('>IIBBBBB',dat)
            if (depth,color,interlace)!=(8,6,0):
                raise ValueError('Unsupported sprite PNG')
        elif kind==b'IDAT':payload.extend(dat)
        elif kind==b'IEND':break
    if not width or not height:raise ValueError('Missing dimensions')
    raw=zlib.decompress(payload)
    stride=width*4
    rows=[];p=0;before=bytearray(stride)
    for _ in range(height):
        filtering=raw[p];p+=1
        scan=bytearray(raw[p:p+stride]);p+=stride
        if filtering>4:raise ValueError('PNG filter')
        for i in range(stride):
            a=scan[i-4] if i>=4 else 0
            b=before[i]
            c=before[i-4] if i>=4 else 0
            if filtering==1:scan[i]=(scan[i]+a)&255
            elif filtering==2:scan[i]=(scan[i]+b)&255
            elif filtering==3:scan[i]=(scan[i]+((a+b)//2))&255
            elif filtering==4:
                predictor=a+b-c
                distances=(abs(predictor-a),abs(predictor-b),abs(predictor-c))
                choice=(a,b,c)[distances.index(min(distances))]
                scan[i]=(scan[i]+choice)&255
        rows.append(scan);before=scan
    return width,height,rows


class SpriteAnimationTest(unittest.TestCase):
    def test_every_frame_differs_in_every_pose(self):
        for person in [f"{role}-{variant}" for role in ("programmer","qa","artist","musician","voice","research","lead","writer","allround") for variant in range(4)]:
            for pose in ('idle','walk','working','cafe'):
                with self.subTest(person=person,pose=pose):
                    w,h,rows=pixels_rgba(ASSETS/f'agent-{person}-{pose}.png')
                    self.assertEqual((w,h),(192,68))
                    frames=[b''.join(row[(frame*48)*4:((frame+1)*48)*4] for row in rows) for frame in range(4)]
                    for idx in range(1,4):
                        changed=sum(a!=b for a,b in zip(frames[0],frames[idx]))
                        self.assertGreater(changed,60, f'{person} {pose} frame {idx} looks identical')
    def test_animation_css_has_idle_walk_work_and_cafe(self):
        self.assertIn('body .agent.idle:not(.walking)',CSS)
        self.assertIn('body .agent.working:not(.walking)',CSS)
        self.assertIn('body .agent.walking{animation:',CSS)
        self.assertIn('@media(prefers-reduced-motion:reduce)',CSS)
        for i in [f"{role}-{variant}" for role in ("programmer","qa","artist","musician","voice","research","lead","writer","allround") for variant in range(4)]:
            self.assertIn(f'agent-{i}-cafe.png',CSS)
            for pose in ('idle','walk','working'):
                self.assertIn(f'agent-{i}-{pose}.png',CSS)
    def test_sprites_have_no_runtime_pillow_dependency(self):
        self.assertNotIn('PIL',CSS)
        self.assertFalse((server.APP/'backend'/'server.py').read_text().find('from PIL import Image')!=-1)

if __name__=='__main__':unittest.main()
