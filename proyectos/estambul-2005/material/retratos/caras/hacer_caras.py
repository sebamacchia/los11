import json,sys
from PIL import Image,ImageDraw,ImageOps,ImageFilter
# centro de la cara en el retrato de 460 px (medido en hojas de 300 px -> x1.533)
C={"nesta":(160,115),"kaka":(90,125),"seedorf":(90,140),"pirlo":(120,140),"stam":(112,120),"dida":(52,100),
   "gattuso":(70,140),"crespo":(85,145),"cafu":(115,120),"shevchenko":(70,140),"maldini":(65,105),
   "gerrard":(85,120),"dudek":(110,140),"carragher":(65,165),"kewell":(155,145),"baros":(70,150),
   "riise":(140,130),"luis-garcia":(150,125),"hyypia":(160,135),"finnan":(165,130),"xabi-alonso":(150,135)}
aj=json.loads(sys.argv[1]); guardar='--guardar' in sys.argv
ims=[]
for nom,(x,y) in C.items():
    dx,dy,L=aj.get(nom,[0,0,330])
    im=Image.open(f'material/retratos/{nom}.png').convert('RGB')
    P=200
    fondo=im.resize((460+2*P,460+2*P)).filter(ImageFilter.GaussianBlur(30))  # relleno si la cara está pegada al borde
    fondo.paste(im,(P,P))
    cx,cy=x*1.533+dx+P,y*1.533+dy+P
    c=fondo.crop((int(cx-L/2),int(cy-L/2),int(cx+L/2),int(cy+L/2)))
    if guardar: c.save(f'material/retratos/caras/{nom}.png'); continue
    c=c.resize((240,240)); d=ImageDraw.Draw(c); d.ellipse([0,0,239,239],outline='yellow',width=2)
    d.line([120,100,120,140],fill='yellow'); d.line([100,120,140,120],fill='yellow'); d.text((4,4),nom,fill='yellow')
    ims.append(c)
if not guardar:
    s=Image.new('RGB',(240*8,240*3))
    for i,c in enumerate(ims): s.paste(c,((i%8)*240,(i//8)*240))
    s.save(sys.argv[2])
