#!/usr/bin/env python3
"""Generate the bilingual README SVG suite. Python standard library only."""
from pathlib import Path
from html import escape
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets'
NAVY='#142d47'; BLUE='#2462d2'; TEAL='#137d85'; INK='#183249'; MUTED='#526a7e'; LINE='#cfdae2'; PAPER='#fafbf9'; PALE='#edf3f8'; GOLD='#9c6522'
FONT="-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, 'PingFang SC', 'Microsoft YaHei', sans-serif"

class SVG:
    def __init__(self,w,h,title,desc):
        self.w=w; self.h=h
        self.s=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc"><title id="title">{escape(title)}</title><desc id="desc">{escape(desc)}</desc>',f'<defs><marker id="arrow" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 8 4 0 8" fill="none" stroke="{BLUE}" stroke-width="1.3"/></marker><pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse"><path d="M24 0H0V24" fill="none" stroke="#dce6ed" stroke-width="0.7"/></pattern></defs>',f'<rect width="{w}" height="{h}" rx="4" fill="{PAPER}"/>']
    def add(self,s):self.s.append(s)
    def rect(self,x,y,w,h,fill='none',stroke=None,rx=0):self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"'+(f' stroke="{stroke}"' if stroke else '')+'/>')
    def line(self,x1,y1,x2,y2,color=LINE,width=1,dash=None,arrow=False):self.add(f'<path d="M{x1} {y1}L{x2} {y2}" fill="none" stroke="{color}" stroke-width="{width}"'+(f' stroke-dasharray="{dash}"' if dash else '')+(' marker-end="url(#arrow)"' if arrow else '')+'/>')
    def path(self,d,color=BLUE,width=2,dash=None,arrow=False):self.add(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linejoin="round"'+(f' stroke-dasharray="{dash}"' if dash else '')+(' marker-end="url(#arrow)"' if arrow else '')+'/>')
    def text(self,x,y,txt,size=20,color=INK,weight=400,anchor='start',spacing=None):self.add(f'<text x="{x}" y="{y}" fill="{color}" font-family="{FONT}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}"'+(f' letter-spacing="{spacing}"' if spacing else '')+f'>{escape(txt)}</text>')
    def circle(self,x,y,r,color):self.add(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{color}"/>')
    def check(self,x,y,color=TEAL):self.path(f'M{x} {y}l5 5 10 -12',color,2.5)
    def save(self,name):
        self.add('</svg>'); data='\n'.join(self.s)+'\n';ET.fromstring(data);(OUT/name).write_text(data)

def label(s,x,y,t,color=BLUE):s.text(x,y,t,15,color,650,spacing='1.4')
def sheet(s,x,y,w,h,title,lines,accent=BLUE):
    s.rect(x,y,w,h,'#ffffff',LINE,3);s.line(x,y,x+w,y,accent,3);s.text(x+18,y+30,title,19,INK,650)
    for i,t in enumerate(lines):s.text(x+18,y+61+i*28,t,17,MUTED)

def header(s,title,zh=False,tag='WORKFLOW / 01'):
    label(s,38,35,tag);s.text(38,77,title,29,NAVY,650);s.line(38,101,1162,101)

def brand(zh):
    s=SVG(1200,310,'autodev — '+('让复杂变更看得清，验得明。' if zh else 'Clarity for consequential changes.'),'autodev 将意图转化为约定的系统范围、经过核验的实现和可见的交付证据。' if zh else 'autodev turns intent into an agreed system slice, a checked implementation, and visible delivery evidence.')
    s.rect(784,0,416,310,PALE);s.rect(784,0,416,310,'url(#grid)');s.line(784,0,784,310,LINE)
    # Folded engineering mark: explicit boundary + advancing path.
    s.path('M43 56H78V91H43Z',NAVY,3);s.path('M51 79L60 65H70M60 65V82H74',BLUE,3)
    s.text(94,88,'autodev',53,NAVY,700,spacing='-2')
    label(s,44,123,'CLARIFY  /  LOOP  /  HANDOFF',MUTED)
    slogan='让复杂变更看得清，验得明。' if zh else 'Clarity for consequential changes.'
    s.text(44,187,slogan,31 if zh else 30,NAVY,550,spacing='-0.7' if not zh else None)
    s.text(44,229,'先对齐意图，再交付可核验的结果。' if zh else 'Align on intent. Deliver evidence you can inspect.',21,MUTED)
    s.text(44,279,'开发 · 修复 · 优化' if zh else 'DEVELOPMENT  ·  BUG FIXES  ·  OPTIMIZATION',14,MUTED,500,spacing='1' if not zh else None)
    s.circle(985,150,102,'#e3ecf5')
    s.path('M911 105H1045V197H911Z',BLUE,2,dash='5 5')
    for x,y,done in [(895,87,False),(1028,132,True),(937,194,True)]:
        s.rect(x,y,56,42,'#e5f3ef' if done else 'white',TEAL if done else BLUE,8)
        if done:s.check(x+19,y+22)
        else:s.path(f'M{x+18} {y+12}l-8 9 8 9M{x+38} {y+12}l8 9 -8 9',BLUE,2)
    s.path('M951 108H1056V131M1056 174V215H994',BLUE,2,arrow=True)
    s.path('M936 215H923V132',BLUE,2,arrow=True)
    s.save('autodev-brand'+('.zh' if zh else '')+'.svg')

def stage_headers(s, zh, labels=None):
    for i,x in enumerate([48,448,848]):
        s.text(x,151,f"0{i+1}",16,BLUE,650)
        s.text(x+36,153,['Clarify','Loop','Handoff'][i],25,NAVY,650)
        if i<2:s.line(x+295,145,x+350,145,BLUE,2,arrow=True)


def node(s,x,y,name,state='solid',kind='service'):
    color=TEAL if state=='done' else BLUE if state=='solid' else MUTED
    if state=='pending':
        s.add(f'<rect x="{x}" y="{y}" width="76" height="58" rx="10" fill="{PAPER}" stroke="{color}" stroke-width="2" stroke-dasharray="5 5"/>')
    else:s.rect(x,y,76,58,'#e5f3ef' if state=='done' else PALE,color,10)
    if kind=='database':
        s.add(f'<ellipse cx="{x+38}" cy="{y+18}" rx="17" ry="6" fill="none" stroke="{color}" stroke-width="2"/>')
        s.path(f'M{x+21} {y+18}v19c0 8 34 8 34 0V{y+18}',color,2)
    elif kind=='queue':
        for dx in [20,32,44]:s.rect(x+dx,y+17,8,24,color,rx=2)
    else:
        s.path(f'M{x+28} {y+16}l-10 12 10 12M{x+48} {y+16}l10 12 -10 12',color,2)
    s.text(x+38,y+81,name,16,color,550,anchor='middle')


def system(s,x,y,zh,mode='solid'):
    states=['solid']*3 if mode=='solid' else ['done','done','pending'] if mode=='partial' else ['done']*3
    names=['API','Queue','Ledger'] if not zh else ['API','队列','账本']
    for i,(name,state) in enumerate(zip(names,states)):
        node(s,x+i*112,y,name,state,['service','queue','database'][i])
        if i<2:s.line(x+i*112+78,y+29,x+(i+1)*112-5,y+29,TEAL if mode=='done' else BLUE,2,dash='4 4' if mode=='partial' and i==1 else None,arrow=True)
    s.path(f'M{x+150} {y-7}v-25H{x+38}v25',BLUE,2,arrow=True)
    s.text(x+94,y-42,'retry' if not zh else '重试',14,MUTED,anchor='middle')


def review(s,x,y,zh):
    s.circle(x,y-7,8,GOLD);s.path(f'M{x-13} {y+17}v-5q13-17 26 0v5',GOLD,2)
    s.text(x+25,y+3,'review' if not zh else '审阅',15,GOLD,550)


def overview(zh):
    title='同一个变更，从目标到交付' if zh else 'One change. Visible from intent to delivery.'
    s=SVG(1200,520,title,'Illustrative billing retry workflow; dashed paths remain unfinished. Check records support specific paths, not universal correctness.')
    header(s,title,zh);stage_headers(s,zh)
    for x,mode in [(48,'solid'),(448,'partial'),(848,'done')]:system(s,x,251,zh,mode)
    s.rect(33,195,338,168,'none',BLUE,12)
    s.text(225,348,'约定范围' if zh else 'Agreed scope',14,BLUE,550)
    s.line(48,403,1144,403,LINE,2)
    for x,status in [(90,'fail'),(490,'pass'),(602,'gap'),(890,'pass'),(1002,'pass')]:
        s.line(x,350,x,390,LINE,1,dash='3 4');s.circle(x,403,12,TEAL if status=='pass' else GOLD if status=='gap' else '#b85649')
        if status=='pass':s.check(x-7,404,'white')
        else:s.text(x,408,'?' if status=='gap' else '×',18,'white',650,anchor='middle')
    for x,t in [(48,'baseline / 基线' if zh else 'Baseline'),(448,'checks + gaps / 检查与缺口' if zh else 'Checks + gaps'),(848,'retained source + evidence' if not zh else '保留源码 + 证据')]:s.text(x,446,t,17,MUTED)
    review(s,270,480,zh);review(s,1070,480,zh)
    s.text(448,488,'虚线 = 尚未实现' if zh else 'Dashed = unfinished',15,MUTED)
    s.save('autodev-overview'+('.zh' if zh else '')+'.svg')


def development(s,zh):
    for x,mode in [(48,'solid'),(448,'partial'),(848,'done')]:
        system(s,x,270,zh,mode)
    for x in [48,448,848]:
        s.rect(x,389,300,62,'white',LINE,8)
        for i in range(3):
            color=TEAL if x==848 or (x==448 and i<2) else BLUE if x==48 else LINE
            s.rect(x+18+i*94,409,76,20,color,rx=3)
    s.text(48,490,'蓝图' if zh else 'Blueprint',18,BLUE,600)
    s.text(448,490,'2 / 3 已实现' if zh else '2 / 3 implemented',18,TEAL,600)
    s.text(848,490,'逐路径对照代码与检查' if zh else 'Compare paths with code + checks',17,TEAL,600)


def bugfix(s,zh):
    for x,fixed in [(48,False),(448,True),(848,True)]:
        s.line(x+26,241,x+272,241,LINE,2)
        for j in range(2):
            y=269+j*57
            s.path(f'M{x+25} {y}H{x+160}',BLUE,2,arrow=True)
            s.rect(x+4,y-9,15,18,BLUE,rx=3)
            s.text(x+35,y-13,'same key' if not zh else '同一 key',14,MUTED)
            s.rect(x+185,y-15,84,30,'#f9eae6' if not fixed else '#e5f3ef',rx=5)
            s.text(x+227,y+5,('WRITE' if not fixed or j==0 else 'REUSE') if not zh else ('写入' if not fixed or j==0 else '复用'),14,'#b85649' if not fixed else TEAL,600,anchor='middle')
        s.text(x,387,'重复扣费' if not fixed and zh else 'Duplicate charge' if not fixed else '一次写入' if zh else 'One ledger write',18,'#b85649' if not fixed else TEAL,600)
        for j in range(4):
            color='#b85649' if j==0 and not fixed else TEAL
            s.rect(x+j*73,423,57,34,color,rx=5)
            if j==0 and not fixed:s.text(x+28,446,'×',24,'white',600,anchor='middle')
            else:s.check(x+j*73+20,440,'white')
        s.text(x,491,'同一组约定测试' if zh else 'Same agreed test set',17,MUTED)


def optimization(s,zh):
    s.text(48,222,'固定负载' if zh else 'Fixed workload',18,BLUE,600)
    for i,h in enumerate([36,68,48,84,58]):s.rect(52+i*43,345-h,25,h,PALE,BLUE,3)
    s.line(48,362,333,362,BLUE,2)
    for x in range(48,334,24):s.line(x,362,x,373,BLUE,1)
    s.text(48,408,'同一标尺 · 同一环境' if zh else 'Same ruler · same environment',17,MUTED)
    s.text(448,222,'尝试与回滚' if zh else 'Attempts + rollback',18,BLUE,600)
    s.line(461,350,750,350,TEAL,3)
    for x,y,keep in [(485,350,True),(565,275,False),(650,350,True),(725,285,False)]:
        if not keep:
            s.path(f'M{x-32} 350L{x} {y}',MUTED,2)
            s.path(f'M{x} {y+12}Q{x+38} 335 {x+16} 348',MUTED,1.5,dash='4 4',arrow=True)
        s.circle(x,y,9,TEAL if keep else GOLD)
        if not keep:s.text(x,y+5,'×',15,'white',600,anchor='middle')
    s.text(448,408,'保留有效版本' if zh else 'Retain the valid state',17,TEAL)
    s.text(848,222,'保留结果与复测' if zh else 'Retained state + rerun',18,TEAL,600)
    s.rect(857,264,58,87,PALE,BLUE,5);s.rect(945,303,58,48,'#e5f3ef',TEAL,5)
    s.line(974,295,974,311,TEAL,2);s.line(962,295,986,295,TEAL,2)
    s.line(848,362,1145,362,LINE,2)
    s.text(886,389,'baseline',14,MUTED,anchor='middle');s.text(974,389,'retained',14,TEAL,anchor='middle')
    s.text(848,439,'示意，非实测数据' if zh else 'Schematic · not measured data',16,MUTED)
    s.text(48,491,'真实测量轨迹见下方实测案例' if zh else 'Measured trajectories appear in the recorded cases below.',17,MUTED)


SCENARIOS=['development','bugfix','optimization']
def scenario(kind,zh):
    titles={'development':('See what is built. See what is still missing.','看见已实现，也看见未完成'), 'bugfix':('A failure path becomes a regression check.','让故障路径对应到回归检查'), 'optimization':('Keep the ruler. Keep the history.','固定标尺，保留全部尝试')}
    title=titles[kind][int(zh)]
    s=SVG(1200,550,title,'Illustrative workflow only, not benchmark results. The diagram does not establish correctness or measured improvement.')
    header(s,title,zh,'DEVELOPMENT' if kind=='development' else 'BUG FIX' if kind=='bugfix' else 'OPTIMIZATION')
    stage_headers(s,zh)
    {'development':development,'bugfix':bugfix,'optimization':optimization}[kind](s,zh)
    s.text(48,530,'结构示意 · 结论依赖实际代码与原始证据' if zh else 'Schematic · conclusions depend on actual code and raw evidence.',14,MUTED)
    s.save('autodev-'+kind+('.zh' if zh else '')+'.svg')

if __name__=='__main__':
    OUT.mkdir(exist_ok=True)
    for zh in [False,True]:
        brand(zh);overview(zh)
        for kind in SCENARIOS:scenario(kind,zh)
    print('Generated 10 accessible SVG assets in docs/assets/.')
