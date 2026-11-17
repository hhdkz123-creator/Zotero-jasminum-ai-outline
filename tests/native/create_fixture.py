"""Synthetic Chinese 297-page PDF: destinations are known, not a real book."""
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import sys
pdfmetrics.registerFont(TTFont('Chinese','/System/Library/Fonts/Supplemental/Arial Unicode.ttf'))
rows=[('第一章 理论基础',1,1),('第一节 研究方法',2,2),('一、核心概念',3,3),('第二章 历史分析',1,130),('第一节 材料分析',2,131),('一、史料说明',3,132),('第三章 结论',1,280)]
c=canvas.Canvas(sys.argv[1],pagesize=(600,800))
for page in range(1,298):
 c.setFont('Chinese',12)
 if page==3:
  c.setFont('Chinese',20);c.drawString(45,750,'目录');c.setFont('Chinese',12)
  for i,(title,level,printed) in enumerate(rows):c.drawString(45+(level-1)*20,700-i*30,title+' …… '+str(printed))
 else:
  for title,level,printed in rows:
   if page==printed+14:c.setFont('Chinese',22-level*2);c.drawString(45,700,title)
  c.setFont('Chinese',12);c.drawString(45,600,'用于大纲导航回归验证的中文测试文本。')
 c.drawCentredString(300,30,str(page-14) if page>=15 else str(page))
 c.showPage()
c.save()
