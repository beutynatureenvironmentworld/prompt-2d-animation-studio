import copy
import importlib.util
import json
import math
import subprocess
import tempfile
import unittest
from pathlib import Path

SRC=Path(__file__).resolve().parents[1] / 'rapid_cartoon.py'
spec=importlib.util.spec_from_file_location('rapid_cartoon',SRC)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class VideoTest(unittest.TestCase):
    def test_default(self):
        plan=m.storyboard('A chase for the last cookie')
        self.assertGreater(len(plan['shots']),5)
        self.assertEqual(m.validate(plan),13.6)
        self.assertFalse(plan['sound'])
    def test_prompt_to_beats(self):
        plan=m.storyboard('Funny cartoon shots: sneak, glare, chase, shock')
        names=[s['name'] for s in plan['shots']]
        self.assertEqual(names,['setup','sneak','glare','chase','shock','button'])
        self.assertGreater(m.validate(plan),0)
    def test_deterministic(self):
        self.assertEqual(m.storyboard('A chase'),m.storyboard('A chase'))
    def test_injection_not_exec(self):
        with self.assertRaises(ValueError):
            m.storyboard('shots: sneak, __import__')
    def test_no_arbitrary_beats(self):
        with self.assertRaises(ValueError):
            m.storyboard('shots: badaction')
    def test_invalid_dimensions(self):
        board=m.storyboard()
        board['width']=300
        with self.assertRaises(ValueError):m.validate(board)
    def test_invalid_fps(self):
        board=m.storyboard()
        board['fps']=1000
        with self.assertRaises(ValueError):m.validate(board)
    def test_invalid_nan_duration(self):
        board=m.storyboard()
        board['shots'][0]['duration']=float('nan')
        with self.assertRaises(ValueError):m.validate(board)
    def test_invalid_noncontiguous(self):
        board=m.storyboard()
        board['shots'][1]['start']=999
        with self.assertRaises(ValueError):m.validate(board)
    def test_max_length(self):
        with self.assertRaises(ValueError):m.storyboard('!'*1000)
    def test_shot_changes_pixels(self):
        import cairo
        surface=cairo.ImageSurface(cairo.FORMAT_ARGB32,360,640)
        ctx=cairo.Context(surface)
        ctx.save();ctx.scale(360/540,640/960);m.frame(ctx,0,'setup',.3,1.10);ctx.restore()
        before=bytes(surface.get_data())
        ctx.save();ctx.scale(360/540,640/960);m.frame(ctx,1.0,'shock',.3,1.1);ctx.restore()
        after=bytes(surface.get_data())
        self.assertNotEqual(before,after)
    def test_smoke_video_no_audio(self):
        with tempfile.TemporaryDirectory() as tmp:
            board=m.storyboard();board['shots']=board['shots'][:1];board['width']=360;board['height']=640;board['fps']=12
            output=Path(tmp)/'smoke.mp4'
            frames=m.render(board,output)
            self.assertEqual(frames,13)
            p=subprocess.check_output(['ffprobe','-v','error','-show_entries','stream=codec_type', '-of','json',str(output)])
            self.assertEqual([s['codec_type'] for s in json.loads(p)['streams']],['video'])
            with self.assertRaises(FileExistsError):m.render(board,output)

if __name__=='__main__':unittest.main()
