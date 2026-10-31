"""Player-audible preview regression tests. No network; real decodable local files."""
import io, math, os, struct, subprocess, tempfile, unittest, wave, shutil
from pathlib import Path
import pw_media_review as review


def wav_tone(seconds=0.72, rate=24000):
    b=io.BytesIO()
    with wave.open(b,'wb') as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(rate)
        w.writeframes(b''.join(struct.pack('<h',int(5000*math.sin(i*math.tau*440/rate)))
                               for i in range(int(seconds*rate))))
    return b.getvalue()


class AudioPlayerTests(unittest.TestCase):
    def test_actual_wave_decodes_and_has_duration(self):
        sample=review._audition(wav_tone(),'audio/wav')
        self.assertEqual(sample['mime'],'audio/wav')
        self.assertTrue(sample['verified_decode'])
        self.assertGreater(sample['seconds'],0.5)
        self.assertLess(sample['seconds'],1)
        import base64
        raw=base64.b64decode(sample['base64'])
        with wave.open(io.BytesIO(raw),'rb') as s:
            self.assertGreater(s.getnframes(),0)

    def test_broken_header_rejected_not_0000_player(self):
        if shutil.which('ffmpeg'):
            with self.assertRaisesRegex(ValueError,'kunde inte avkodas'):
                review._audition(b'ID3'+b'0'*100,'audio/mpeg')
        else:
            self.skipTest('Serverns ffmpeg saknas; browser-kontrollen tar över')

    def test_corrupt_wav_is_rejected(self):
        with self.assertRaises(ValueError):
            review._audition(b'RIFF'+b'x'*100,'audio/wav')

    def test_real_mp3_converted_to_wav_for_firefox(self):
        if not shutil.which('ffmpeg'):self.skipTest('ffmpeg saknas')
        with tempfile.TemporaryDirectory() as d:
            src=Path(d)/'tone.wav';dst=Path(d)/'tone.mp3'
            src.write_bytes(wav_tone(1.3))
            result=subprocess.run(['ffmpeg','-nostdin','-v','error','-y','-i',str(src),str(dst)],
                                  capture_output=True,timeout=12,check=False)
            if result.returncode:self.skipTest('MP3-kodare saknas')
            sample=review._audition(dst.read_bytes(),'audio/mpeg')
            self.assertEqual(sample['mime'],'audio/wav')
            self.assertTrue(sample['verified_decode'])
            self.assertGreater(sample['seconds'],0.8)

    def test_excerpt_stays_under_twenty_seconds(self):
        if not shutil.which('ffmpeg'):self.skipTest('ffmpeg saknas')
        out=review._audition(wav_tone(20.4),'audio/wav')
        self.assertLessEqual(out['seconds'],20.01)
        self.assertTrue(out['excerpt'])
        self.assertLess(out['bytes'],1_050_000)


if __name__=='__main__':unittest.main()
