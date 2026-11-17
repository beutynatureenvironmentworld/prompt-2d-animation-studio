"""Authenticated pull from completed PRIVATE Kaggle kernel, no exposed HTTP server."""
import argparse,json,os,re,subprocess
from pathlib import Path
ID=re.compile(r'^[A-Za-z0-9_-]{2,64}/[A-Za-z0-9_-]{4,100}$')
def collect(kernel,out,download=False):
 if not ID.fullmatch(kernel):raise ValueError('Invalid private Kaggle kernel ID')
 out=Path(out);out.mkdir(parents=True,exist_ok=True)
 if not os.getenv('KAGGLE_API_TOKEN'):raise RuntimeError('KAGGLE_API_TOKEN missing; refusing unauthenticated request')
 def call(args):return subprocess.run(args,capture_output=True,text=True,timeout=120,check=True)
 status=call(['kaggle','kernels','status',kernel])
 if 'complete' not in status.stdout.lower():raise RuntimeError('Kernel has not completed; no downloads attempted')
 if download:call(['kaggle','kernels','output',kernel,'-p',str(out)])
 return {'kernel_id':kernel,'verified_status':True,'downloaded':download,'path':str(out)}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('kernel_id');p.add_argument('--out',default='output/collected');p.add_argument('--download',action='store_true');a=p.parse_args()
 print(json.dumps(collect(a.kernel_id,a.out,a.download),indent=2))
