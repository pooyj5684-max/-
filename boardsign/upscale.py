import sys, torch, numpy as np
from PIL import Image
from spandrel import ModelLoader
torch.set_num_threads(4)
model,src,out=sys.argv[1:4]
m=ModelLoader().load_from_file(model).eval()
im=Image.open(src).convert('RGBA'); a=np.array(im)
def run(rgb):
    x=torch.from_numpy(rgb).permute(2,0,1).float().div(255)[None]
    T,P=256,16; _,_,h,w=x.shape; o=torch.zeros(1,3,h*4,w*4)
    with torch.no_grad():
        for y in range(0,h,T):
            for xx in range(0,w,T):
                y0,x0=max(y-P,0),max(xx-P,0); y1,x1=min(y+T+P,h),min(xx+T+P,w)
                r=m(x[:,:,y0:y1,x0:x1])
                o[:,:,y*4:min(y+T,h)*4,xx*4:min(xx+T,w)*4]=r[:,:,(y-y0)*4:(y-y0+min(T,h-y))*4,(xx-x0)*4:(xx-x0+min(T,w-xx))*4]
    return (o[0].clamp(0,1).permute(1,2,0).numpy()*255).round().astype(np.uint8)
rgb=run(np.ascontiguousarray(a[:,:,:3]))
alpha=np.array(Image.fromarray(a[:,:,3]).resize((rgb.shape[1],rgb.shape[0]),Image.LANCZOS))
Image.fromarray(np.dstack([rgb,alpha])).save(out); print(out, rgb.shape)
