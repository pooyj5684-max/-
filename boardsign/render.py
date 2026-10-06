# Board sign with a full-bleed festive background behind the artwork.
import sys, math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops
sys.path.insert(0, sys.argv[0].rsplit('/',1)[0])
DPI=300; k=DPI/72
W,H=867.401,612.283
SX0,SX1,SY0,SY1=69.574,797.227,65.121,546.445
PW,PH=round(W*k),round(H*k)
PURPLE=(75,26,140); VIOLET=(140,60,210); GREEN=(140,198,63); LIME=(186,226,80)
YELLOW=(255,196,30); PINK=(240,150,220)

def write_pdf(rgb,path):
    """Minimal PDF: one page, one lossless (Flate) RGB image, no fonts or text."""
    import zlib
    h,w,_=rgb.shape
    data=zlib.compress(rgb.tobytes(),9)
    content=f"q {W} 0 0 {H} 0 0 cm /Im0 Do Q".encode()
    objs=[b"<< /Type /Catalog /Pages 2 0 R >>",
          b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
          f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {W} {H}] /Resources << /XObject << /Im0 4 0 R >> >> /Contents 5 0 R >>".encode(),
          f"<< /Type /XObject /Subtype /Image /Width {w} /Height {h} /ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /FlateDecode /Length {len(data)} >>\nstream\n".encode()+data+b"\nendstream",
          f"<< /Length {len(content)} >>\nstream\n".encode()+content+b"\nendstream"]
    out=bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"); offs=[]
    for n,o in enumerate(objs,1):
        offs.append(len(out)); out+=f"{n} 0 obj\n".encode()+o+b"\nendobj\n"
    x=len(out)
    out+=f"xref\n0 {len(objs)+1}\n0000000000 65535 f \n".encode()+b"".join(f"{o:010d} 00000 n \n".encode() for o in offs)
    out+=f"trailer\n<< /Size {len(objs)+1} /Root 1 0 R >>\nstartxref\n{x}\n%%EOF\n".encode()
    open(path,"wb").write(out)

def load_art(src):
    im=Image.open(src).convert('RGBA'); a=np.array(im)
    if a[...,3].min()==255:                       # opaque JPG: cut white background by flood fill from the border
        near=(a[...,:3]>=235).all(2)
        m=Image.fromarray(np.dstack([near*255]*3).astype(np.uint8),'RGB')   # (L-mode floodfill is a no-op here)
        for p in [(0,0),(m.width-1,0),(0,m.height-1),(m.width-1,m.height-1)]:
            ImageDraw.floodfill(m,p,(255,0,0))
        bg=(np.array(m)==[255,0,0]).all(2)
        alpha=Image.fromarray(((~bg)*255).astype(np.uint8)).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.2))
        im.putalpha(alpha)
    return im.crop(im.getchannel('A').getbbox())

def dilate(a,r):
    """Approximate dilation of a binary L mask by r px (blur + threshold, fast for big r)."""
    return a.filter(ImageFilter.GaussianBlur(r/2)).point(lambda v:255 if v>8 else 0) if r else a

def sticker(im, border, shadow_r):
    """White sticker outline + soft purple drop shadow around the artwork alpha."""
    pad=border+shadow_r*3
    big=Image.new('RGBA',(im.width+2*pad,im.height+2*pad),(0,0,0,0)); big.alpha_composite(im,(pad,pad))
    a=big.getchannel('A').point(lambda v:255 if v>40 else 0)
    out=dilate(a,border).filter(ImageFilter.GaussianBlur(1.5))
    shadow=Image.new('RGBA',big.size,PURPLE+(0,)); shadow.putalpha(out.filter(ImageFilter.GaussianBlur(shadow_r)).point(lambda v:int(v*0.4)))
    res=Image.new('RGBA',big.size,(0,0,0,0))
    res.alpha_composite(shadow,(0,int(shadow_r*0.5)))
    white=Image.new('RGBA',big.size,(255,255,255,0)); white.putalpha(out)
    res.alpha_composite(white); res.alpha_composite(big)
    return res, out

def background(seed):
    rnd=random.Random(seed)
    yy,xx=np.mgrid[0:PH,0:PW].astype(np.float32)
    cx,cy=PW/2,PH*0.48
    r=np.hypot(xx-cx,yy-cy)/np.hypot(cx,cy)
    c0=np.array([255,252,236]); c1=np.array([226,208,250])      # cream centre -> lavender edge
    t=np.clip(r,0,1)[...,None]**1.3
    img=c0*(1-t)+c1*t
    ang=np.arctan2(yy-cy,xx-cx); rays=(np.floor((ang+math.pi)/(2*math.pi)*28)%2)==0
    img=np.where(rays[...,None], img*0.965+np.array([255,255,255])*0.035, img)   # subtle sunburst
    img=Image.fromarray(img.astype(np.uint8)).convert('RGBA')
    # dotted border pattern
    d=ImageDraw.Draw(img)
    for x in range(0,PW,70):
        for y in range(0,PH,70):
            if (x//70+y//70)%2==0: d.ellipse([x-6,y-6,x+6,y+6],fill=(255,255,255,110))
    return img

def heart(d,cx,cy,s,col):
    pts=[(cx+s*16*math.sin(t)**3/17, cy-s*(13*math.cos(t)-5*math.cos(2*t)-2*math.cos(3*t)-math.cos(4*t))/17) for t in np.linspace(0,2*math.pi,80)]
    d.polygon(pts,fill=col)
def star(d,cx,cy,s,col,rot):
    pts=[]
    for i in range(8):
        rr=s if i%2==0 else s*0.38; a=rot+i*math.pi/4
        pts.append((cx+rr*math.cos(a),cy+rr*math.sin(a)))
    d.polygon(pts,fill=col)
def dash(d,cx,cy,s,col,rot):
    dx,dy=math.cos(rot)*s,math.sin(rot)*s
    d.line([(cx-dx,cy-dy),(cx+dx,cy+dy)],fill=col,width=int(s*0.45)); 
    for e in [(cx-dx,cy-dy),(cx+dx,cy+dy)]: d.ellipse([e[0]-s*0.22,e[1]-s*0.22,e[0]+s*0.22,e[1]+s*0.22],fill=col)

def confetti(page, keepout, seed):
    rnd=random.Random(seed)
    layer=Image.new('RGBA',page.size,(0,0,0,0)); d=ImageDraw.Draw(layer)
    ko=np.array(keepout.filter(ImageFilter.MaxFilter(61)))>0
    placed=[]
    cols=[PURPLE,VIOLET,GREEN,LIME,YELLOW,PINK]
    tries=0
    while len(placed)<70 and tries<20000:
        tries+=1
        x,y=rnd.uniform(0,PW),rnd.uniform(0,PH)
        kind=rnd.choice(['heart','heart','star','star','dot','dash','dash'])
        s=rnd.uniform(45,95) if kind!='dot' else rnd.uniform(14,26)
        if ko[int(min(y,PH-1)),int(min(x,PW-1))]: continue
        xi0,xi1=int(max(x-s,0)),int(min(x+s,PW-1)); yi0,yi1=int(max(y-s,0)),int(min(y+s,PH-1))
        if ko[yi0:yi1,xi0:xi1].any(): continue
        if any(math.hypot(x-px,y-py)<(s+ps)*1.25 for px,py,ps in placed): continue
        placed.append((x,y,s)); col=rnd.choice(cols)+(235,)
        rot=rnd.uniform(0,math.pi)
        if kind=='heart': heart(d,x,y,s,col)
        elif kind=='star': star(d,x,y,s,col,rot)
        elif kind=='dot': d.ellipse([x-s,y-s,x+s,y+s],fill=col)
        else: dash(d,x,y,s*0.8,col,rot)
    page.alpha_composite(layer)

src,out,seed=sys.argv[1],sys.argv[2],int(sys.argv[3])
art=load_art(src)
border=int(sys.argv[4])           # white edge width in source px (0 when the art already has one)
st,mask=sticker(art,border,int(art.width*0.012))
aw,ah=(SX1-SX0)*k,(SY1-SY0)*k
s=min(aw/st.width,ah/st.height); w,h=round(st.width*s),round(st.height*s)
st=st.resize((w,h),Image.LANCZOS); mask=mask.resize((w,h),Image.LANCZOS)
x0,y0=round((SX0+SX1)/2*k-w/2),round((SY0+SY1)/2*k-h/2)
page=background(seed)
ko=Image.new('L',page.size,0); ko.paste(mask,(x0,y0))
confetti(page,ko,seed)
page.alpha_composite(st,(x0,y0))
write_pdf(np.array(page.convert('RGB')),out)
page.convert('RGB').resize((PW//5,PH//5),Image.LANCZOS).save(out.replace('.pdf','_preview.png'))
print(out,w/k/72*25.4,h/k/72*25.4)
