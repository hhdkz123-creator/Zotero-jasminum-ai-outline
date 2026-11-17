from PIL import Image,ImageDraw,ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from pypdf import PdfReader,PdfWriter
from pathlib import Path
rows=[('第一章 理论基础',1,1),('第一节 研究方法',2,2),('一、核心概念',3,3),('第二章 历史分析',1,130),('第一节 材料分析',2,131),('一、史料说明',3,132),('第三章 结论',1,280)]
font=lambda size:ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Unicode.ttf',size)
c=canvas.Canvas('native/scanned-297.pdf',pagesize=(600,800))
for p in range(1,298):
 img=Image.new('RGB',(600,800),'white');d=ImageDraw.Draw(img)
 if p==3:
  d.text((45,30),'目录',fill='black',font=font(20))
  for i,(title,level,printed) in enumerate(rows):d.text((45+(level-1)*20,80+i*30),title+' ...... '+str(printed),fill='black',font=font(12))
 else:
  for title,level,printed in rows:
   if p==printed+14:d.text((45,85),title,fill='black',font=font(22-level*2))
  d.text((45,185),'用于大纲导航回归验证的中文测试文本。',fill='black',font=font(12))
 d.text((295,755),str(p-14) if p>=15 else str(p),fill='black',font=font(12))
 c.drawImage(ImageReader(img),0,0,600,800);c.showPage()
c.save()
w=PdfWriter()
for page in PdfReader('native/scanned-297.pdf').pages[:17]:w.add_page(page)
w.write('native/full-17.pdf')
