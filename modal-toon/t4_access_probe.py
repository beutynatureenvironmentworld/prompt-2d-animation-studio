"""One bounded, low-cost GPU entitlement probe. No model downloads or video generation."""
import modal,subprocess
app=modal.App("fasttoon-lowcost-gpu-access-probe")
@app.function(image=modal.Image.debian_slim(python_version="3.11"),gpu="T4",timeout=30,scaledown_window=2,max_containers=1)
def check_gpu():
    p=subprocess.run(["nvidia-smi","--query-gpu=name,memory.total","--format=csv,noheader"],capture_output=True,text=True,timeout=10)
    return {"returncode":p.returncode,"gpu":p.stdout.strip()[:100]}
@app.local_entrypoint()
def main():
    try:print("GPU_ACCESS_CHECK_RESULT",check_gpu.remote())
    except Exception as e:
        print("GPU_ACCESS_NOT_AVAILABLE",type(e).__name__,str(e)[:200])
        raise
