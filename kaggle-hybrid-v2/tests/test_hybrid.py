import json,os,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import story,dispatch,preflight,gpu_worker,assemble

class HybridTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.p=Path(self.tmp.name)
        self.story=ROOT/'examples/spicy_hybrid_story.json'
    def test_schema_and_identity(self):
        d=story.read_story(self.story)
        self.assertEqual(d['character_ref'],'mascot-lab/config/permanent_mascot.webp')
        self.assertEqual(len(d['clips']),4)
    def test_exact_gpu_budget(self):
        d=story.read_story(self.story)
        self.assertEqual(len(story.select_gpu(d,0)),0)
        self.assertEqual([s['id'] for s in story.select_gpu(d,2)],['scene_03'])
    def test_batch_validated(self):
        out=self.p/'batch.json';m=story.make_batch(self.story,out)
        self.assertEqual(story.validate_batch(out)['shots'],m['shots'])
        self.assertEqual(len(m['shots']),1)
    def test_reject_bad_reference(self):
        d=json.loads(self.story.read_text());d['character_ref']='unsafe.png';p=self.p/'story.json';p.write_text(json.dumps(d))
        with self.assertRaises(ValueError):story.read_story(p)
    def test_reject_duplicate_scenes(self):
        d=json.loads(self.story.read_text());d['clips'][1]['id']=d['clips'][0]['id'];p=self.p/'story.json';p.write_text(json.dumps(d))
        with self.assertRaises(ValueError):story.read_story(p)
    def test_preflight_reports_actual_cpu(self):
        x=preflight.probe(self.p/'report');self.assertIn('cuda_verified',x)
        self.assertFalse(x['model_inference_verified'])
        self.assertTrue((self.p/'report/GPU_PREFLIGHT.json').exists())
    def test_kaggle_packaging_private_and_no_secrets(self):
        bundle=self.p/'batch.json';story.make_batch(self.story,bundle)
        identifier=dispatch.package('valid_user','wan21-t2v',bundle,self.p/'job',12)
        md=json.loads((self.p/'job/kernel-metadata.json').read_text())
        self.assertEqual(identifier,md['id']);self.assertTrue(md['is_private'])
        self.assertEqual(md['machine_shape'],'NvidiaTeslaT4')
        self.assertEqual(len(md['dataset_sources']),0)
        self.assertNotIn('KAGGLE_API_TOKEN',(self.p/'job/gpu_job.py').read_text())
    def test_prohibit_headless_fake_h3_flags(self):
        with self.assertRaises(ValueError):dispatch.package('valid_user','minimax_h3_int8','',self.p/'job',15)
    def test_wangp_requires_real_exported_queue(self):
        batch=self.p/'batch.json';story.make_batch(self.story,batch)
        with self.assertRaises(ValueError):dispatch.package('valid_user','wangp-queue',batch,self.p/'job',15)
        fake=self.p/'queue.zip';fake.write_text('fake')
        with self.assertRaises(Exception):gpu_worker.safe_queue(fake)
    def test_wangp_valid_queue_safe(self):
        import zipfile
        fake=self.p/'queue.zip'
        with zipfile.ZipFile(fake,'w') as z:z.writestr('settings.json','{"version":1}')
        self.assertEqual(gpu_worker.safe_queue(fake),fake.resolve())
    def test_no_unguarded_cpu_fallback(self):
        with self.assertRaises(FileNotFoundError):assemble.assemble(self.story,self.p/'cpu',self.p/'gpu',self.p/'out.mp4')
    def test_silent_fallback_requires_flag(self):
        ffmpeg=['ffmpeg','-hide_banner','-loglevel','error','-y']
        source=self.p/'sample.mp4'
        subprocess.run(ffmpeg+['-f','lavfi','-i','color=c=white:s=160x240:d=3:r=24','-c:v','libx264','-pix_fmt','yuv420p',str(source)],check=True,timeout=25)
        cpu=self.p/'cpu';cpu.mkdir()
        for clip in story.read_story(self.story)['clips']:
            (cpu/(clip['id']+'.mp4')).write_bytes(source.read_bytes())
        dest=self.p/'test.mp4'
        with self.assertRaises(FileNotFoundError):assemble.assemble(self.story,cpu,self.p/'gpu',dest)
        r=assemble.assemble(self.story,cpu,self.p/'gpu',dest,allow_cpu_fallback=True)
        self.assertEqual(r['gpu_generated_scenes'],0)
        self.assertEqual(r['cpu_scenes'],4)
        self.assertTrue(dest.is_file());self.assertGreater(dest.stat().st_size,1000)

if __name__=='__main__':unittest.main()
