"""Verify notebook structure and no credential/tunnel leaks; no GPU inference."""
import argparse,ast,json
from pathlib import Path
def main():
    p=argparse.ArgumentParser()
    p.add_argument("file",type=Path)
    a=p.parse_args()
    data=json.loads(a.file.read_text(encoding="utf8"))
    assert data["nbformat"]==4
    assert len(data["cells"])>=7
    source="\n".join("".join(x.get("source",[])) for x in data["cells"] if x["cell_type"]=="code")
    assert "RUN_AI_VIDEO = False" in source
    assert "AnimateDiffPipeline" in source and "export_to_video" in source
    for cell in data["cells"]:
        if cell["cell_type"]=="code":
            ast.parse("".join(cell["source"]))
    for forbidden in ("AI_HORDE_API_KEY", "cloudflared tunnel", "KAGGLE_API_TOKEN", "R2_BUCKET"):
        assert forbidden not in source
    print("COLAB_NOTEBOOK_STRUCTURE_PASS — no Colab GPU run is claimed")
if __name__=="__main__":main()
