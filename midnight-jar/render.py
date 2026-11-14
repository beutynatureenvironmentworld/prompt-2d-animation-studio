"""Rasterize Node-generated SVG frames with librsvg and stream them to FFmpeg."""
import argparse
import ctypes as ct
from pathlib import Path
import subprocess as sp

def bind(library,name,restype,*types):
    func=getattr(library,name);func.restype=restype;func.argtypes=types;return func

ptr=ct.c_void_p;integer=ct.c_int
cairo=ct.CDLL('libcairo.so.2');rsvg=ct.CDLL('librsvg-2.so.2');glib=ct.CDLL('libgobject-2.0.so.0')
surface=bind(cairo,'cairo_image_surface_create',ptr,integer,integer,integer)
context=bind(cairo,'cairo_create',ptr,ptr)
destroy=bind(cairo,'cairo_destroy',None,ptr)
release=bind(cairo,'cairo_surface_destroy',None,ptr)
flush=bind(cairo,'cairo_surface_flush',None,ptr)
pixels=bind(cairo,'cairo_image_surface_get_data',ptr,ptr)
parse=bind(rsvg,'rsvg_handle_new_from_data',ptr,ct.c_char_p,ct.c_size_t,ptr)
class Rect(ct.Structure):
    _fields_=[(k,ct.c_double) for k in ('x','y','width','height')]
draw=bind(rsvg,'rsvg_handle_render_document',integer,ptr,ptr,ct.POINTER(Rect),ptr)
unref=bind(glib,'g_object_unref',None,ptr)
save=bind(cairo,'cairo_surface_write_to_png',integer,ptr,ct.c_char_p)
def render(story,out,w,fps,layers):
    h=w*16//9;rect=Rect(0,0,w,h)
    for layer in range(5) if layers else [None]:
        node=['node',str(Path(__file__).with_name('scene.cjs')),str(story),str(fps)]
        if layers:
            dest=out/str(layer);dest.mkdir(parents=True,exist_ok=True);node.append(str(layer))
        else:
            cmd=['ffmpeg','-loglevel','error','-y','-f','rawvideo','-pix_fmt','bgra','-s',f'{w}x{h}','-r',str(fps),'-i','-','-an','-c:v','libx264','-threads','2','-crf','17','-preset','veryfast','-pix_fmt','yuv420p','-movflags','+faststart',str(out)]
            enc=sp.Popen(cmd,stdin=sp.PIPE)
        try:
            with sp.Popen(node,stdout=sp.PIPE) as src:
                for i,line in enumerate(src.stdout,1):
                    handle=parse(line,len(line),None)
                    if not handle: raise ValueError('Invalid SVG')
                    img=surface(0,w,h);ctx=context(img)
                    try:
                        if not draw(handle,ctx,ct.byref(rect),None): raise ValueError('Invalid frame')
                        flush(img)
                        if layers:
                            if save(img,str(dest/f'{i:05}.png').encode()): raise IOError('PNG write failed')
                        else: enc.stdin.write(ct.string_at(pixels(img),w*h*4))
                    finally: destroy(ctx);release(img);unref(handle)
                if src.wait(): raise RuntimeError('Scene generation failed')
        finally:
            if not layers: enc.stdin.close();status=enc.wait()
        if not layers and status: raise RuntimeError('Encoding failed')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('story',type=Path);p.add_argument('output',type=Path)
    p.add_argument('--width',choices=[180,360,540,720,1080],type=int,default=1080)
    p.add_argument('--fps',type=int,choices=[2,12,24,30],default=24);p.add_argument('--layers',action='store_true')
    a=p.parse_args();render(a.story,a.output,a.width,a.fps,a.layers)
