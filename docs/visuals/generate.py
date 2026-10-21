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
    # A scope window becomes a checked assembly, with measured outputs below.
    label(s,814,37,'SYSTEM SLICE' if not zh else '系统切片',MUTED)
    s.rect(817,58,160,151,'#f9fbfd',BLUE,2);s.rect(817,58,160,29,PALE)
    s.text(829,78,'scope' if not zh else '范围',14,BLUE,600)
    s.rect(837,106,52,29,'white',BLUE,2);s.rect(910,151,48,29,'white',BLUE,2)
    s.path('M889 121H933V150',BLUE,2);s.rect(837,151,52,29,'white',LINE,2)
    s.path('M863 135V150',MUTED,1.6)
    s.line(988,133,1014,133,BLUE,2,arrow=True)
    s.rect(1030,83,133,126,NAVY,rx=3)
    s.text(1045,107,'as-built' if not zh else '实建',17,'#ffffff',600)
    for x,y in [(1048,127),(1115,161),(1048,161)]:s.rect(x,y,29,20,'#b8d6ef',rx=1)
    s.path('M1077 137H1129V160M1062 147V161','#b8d6ef',1.5)
    s.line(817,237,1163,237,LINE)
    s.check(823,266);s.text(850,269,'agreed' if not zh else '已对齐',15,TEAL,600)
    s.check(930,266);s.text(956,269,'checked' if not zh else '已核验',15,TEAL,600)
    s.check(1050,266);s.text(1076,269,'visible' if not zh else '可见',15,TEAL,600)
    s.save('autodev-brand'+('.zh' if zh else '')+'.svg')

def overview(zh):
    title='从意图到证据，变更始终可见' if zh else 'A visible path from intent to evidence'
    s=SVG(1200,650,title,'Clarify 一次审阅目标、基线与范围。Loop 持续更新实现并记录检查证据。Handoff 交付实建产物与核验结果，由人审阅接手。AI 判断与测量证据明确区分。' if zh else 'Clarify agrees the target, baseline and scope with one human review. Loop evolves implementation and recorded check evidence. Handoff delivers as-built artifacts and verification for human acceptance. AI judgment remains distinct from measured evidence.')
    header(s,title,zh)
    xs=[38,430,822]
    stages=[('01','Clarify','对齐系统与范围' if zh else 'Agree on the system slice'),('02','Loop','实施，并持续核验' if zh else 'Build against the agreement'),('03','Handoff','看清结果，再接手' if zh else 'Inspect the result. Take over.')]
    for x,(n,t,sub) in zip(xs,stages):
        label(s,x,137,n);s.text(x+35,139,t,26,NAVY,650);s.text(x,174,sub,21,INK,550)
    for x in [402,794]:s.line(x,126,x+15,126,BLUE,1.8,arrow=True)
    # Clarify's artifact is a real framed scope slice with target and baseline.
    s.rect(38,198,340,230,'#ffffff',LINE,3);label(s,57,228,'AGREEMENT' if not zh else '共同约定')
    s.rect(57,245,133,100,PALE,BLUE,2);s.text(68,268,'system slice' if not zh else '系统切片',16,BLUE,600)
    for x,y in [(70,283),(143,310),(70,310)]:s.rect(x,y,34,18,'white',BLUE,1)
    s.path('M104 292H160V310M87 301V310',BLUE,1.5)
    s.text(208,268,'Target' if not zh else '目标',18,INK,650);s.text(208,297,'Baseline' if not zh else '基线',18,INK,650);s.text(208,326,'Boundaries' if not zh else '边界',18,INK,650)
    s.line(57,363,359,363)
    s.circle(65,389,5,GOLD);s.text(80,395,'Human reviews the whole pass' if not zh else '人一次审阅整个 Clarify',17,GOLD,550)
    # Loop artifact: code patch and independent measured output track.
    s.rect(430,198,340,230,'#ffffff',LINE,3);label(s,449,228,'STATE + EVIDENCE' if not zh else '状态 + 证据')
    s.text(449,265,'Implement' if not zh else '实施变更',20,INK,650);s.line(571,258,619,258,BLUE,1.8,arrow=True);s.text(638,265,'Check' if not zh else '核验',20,INK,650)
    s.path('M708 279V298H490V280',BLUE,1.5,dash='5 4',arrow=True)
    s.text(590,318,'repeat within scope' if not zh else '在约定范围内迭代',15,MUTED,anchor='middle')
    s.line(449,337,751,337)
    s.rect(449,350,128,54,PALE,rx=2);s.text(461,373,'partial view' if not zh else '当前局部视图',17,BLUE,600);s.text(461,395,'next action' if not zh else '下一步行动',15,MUTED)
    s.rect(592,350,159,54,'#edf6f4',rx=2);s.text(604,373,'check output' if not zh else '检查原始输出',17,TEAL,600);s.text(604,395,'recorded' if not zh else '持续留存',15,MUTED)
    # Handoff artifact as paired delivered documents, no fake results.
    s.rect(822,198,340,230,'#ffffff',LINE,3);label(s,841,228,'DELIVERY' if not zh else '交付包')
    sheet(s,841,246,139,107,'As-built' if not zh else '实建产物',['Design' if not zh else '设计对照','Realized' if not zh else '实际落地'],BLUE)
    sheet(s,993,246,150,107,'Verification' if not zh else '核验证据',['Commands' if not zh else '命令与输出','Raw outputs' if not zh else '状态与限制'],TEAL)
    s.line(841,372,1143,372);s.circle(849,397,5,GOLD);s.text(864,403,'Human reviews the delivery' if not zh else '人审阅交付，再决定接手',17,GOLD,550)
    # Honest distinctions and review semantics below the primary artifact path.
    s.text(38,465,'What carries forward' if not zh else '每一阶段，都留下可接续的产物',17,MUTED,600)
    s.line(38,482,1162,482)
    if zh:
        s.text(38,514,'先看懂并认可目标，再让变更推进；最后看见实际交付与证据。',21,NAVY,550)
        a=['AI 判断','提出设计、选择路径、解释结果'];b=['测量证据','由约定检查产生，可回放核验']
    else:
        s.text(38,514,'Understand the target first. See what changed and what the checks establish.',21,NAVY,550)
        a=['AI judgment','Design choices, next steps, interpretation'];b=['Measured evidence','Recorded outputs from the agreed checks']
    s.circle(45,558,5,GOLD);s.text(60,564,a[0],18,GOLD,650);s.text(38,594,a[1],18,MUTED)
    s.line(600,544,600,604)
    s.circle(632,558,5,TEAL);s.text(647,564,b[0],18,TEAL,650);s.text(625,594,b[1],18,MUTED)
    s.save('autodev-overview'+('.zh' if zh else '')+'.svg')

SCENARIOS={
'development':{
'en': {'title':'Feature development · from blueprint to as-built','artifact':'A design you can inspect before and after','clarify':['Inspect the existing system','Draw the target blueprint','Agree on scope and build order'],'loop':['Implement blueprint elements','Run the agreed regression checks','Update the partial system view'],'handoff':['Compare blueprint and as-built','Inspect element coverage','Review verification and limits'],'left':'Agreed blueprint','right':'As-built system','bottom':'The target is an agreed design. The delivery shows how the system actually changed.'},
'zh': {'title':'功能开发 · 从蓝图到实建','artifact':'动手前看清设计，交付时对照实建','clarify':['检查现有系统','绘制目标蓝图','约定范围与构建顺序'],'loop':['逐项实现蓝图元素','运行约定回归检查','同步更新实际局部视图'],'handoff':['对照蓝图与实建图','检查元素覆盖','审阅核验结果与限制'],'left':'约定蓝图','right':'实建系统','bottom':'目标是共同认可的设计；交付展示系统实际发生了什么变化。'}},
'bugfix':{
'en':{'title':'Bug fixes · from reproduction to passing evidence','artifact':'The same agreed tests, before and after','clarify':['Reproduce the failure in a test','Add relevant regression cases','Record baseline and agree scope'],'loop':['Fix within the approved scope','Keep the agreed test set frozen','Run all agreed tests and record output'],'handoff':['Inspect every agreed test result','Review raw outputs and limitations','Rerun the checks when taking over'],'left':'Before the fix','right':'After the fix','bottom':'A reproduction must fail on unchanged source. Broken setup is not proof of the bug.'},
'zh':{'title':'缺陷修复 · 从复现到通过证据','artifact':'修复前后，用同一组约定测试作对照','clarify':['用测试复现故障','补齐相关回归用例','记录基线，并约定影响范围'],'loop':['在批准范围内修复','冻结已约定的测试集合','运行全部测试并保留原始输出'],'handoff':['逐项查看约定测试结果','审阅原始输出与限制','接手时可以重新运行检查'],'left':'修复前','right':'修复后','bottom':'复现测试必须在原代码上失败；环境损坏不能充当缺陷证据。'}},
'optimization':{
'en':{'title':'Optimization · a fixed ruler, an honest history','artifact':'One benchmark · one score · comparable conditions','clarify':['Define the benchmark and target','Measure baseline and observed noise','Agree on scope, margin and time'],'loop':['Optimize, then measure','Retain the best verified change','Log every attempt, including failures'],'handoff':['Show baseline, attempts and final','Rerun verification on the retained state','State whether the target was met'],'left':'Fixed measurement','right':'Recorded history','bottom':'Stop at the agreed target or deadline. A timeout does not imply success.'},
'zh':{'title':'性能优化 · 固定标尺，如实记录过程','artifact':'一个基准 · 一个分数 · 可比的测量条件','clarify':['约定基准与目标','记录基线和观察到的波动','确认范围、改进幅度与时间'],'loop':['先优化，再测量','保留已验证的最优改动','记录每次尝试，包括失败'],'handoff':['展示基线、尝试与最终结果','在保留版本上重新核验','说明目标是否真正达到'],'left':'固定测量方式','right':'真实过程记录','bottom':'达到约定目标或时间用尽即停止；超时并不代表成功。'}}}

def scenario(kind,zh):
    t=SCENARIOS[kind]['zh' if zh else 'en'];s=SVG(1200,624,t['title'],t['artifact']+('。人一次审阅整个 Clarify；Loop 重复实施与检查；Handoff 由人审阅接手。本图为结构示意，不是实测案例数据。' if zh else '. Clarify is reviewed once as a whole. Loop repeats implementation and checks. Handoff is reviewed by the human. Diagram is schematic, not measured case data.'))
    header(s,t['title'],zh,{'development':'SCENARIO / 01','bugfix':'SCENARIO / 02','optimization':'SCENARIO / 03'}[kind])
    s.text(38,137,t['artifact'],20,MUTED)
    xs=[38,430,822]
    for i,(x,stage) in enumerate(zip(xs,['Clarify','Loop','Handoff'])):
        label(s,x,186,f'0{i+1}');s.text(x+35,188,stage,25,NAVY,650)
        for j,line in enumerate(t[stage.lower()]):s.text(x,228+j*29,line,18,INK)
        if i<2:s.line(x+328,181,x+349,181,BLUE,1.7,arrow=True)
    # Single human review after the whole clarification, acceptance at delivery.
    s.circle(44,322,5,GOLD);s.text(59,328,'Review the whole pass once' if not zh else '一次审阅整个 Clarify',17,GOLD,550)
    s.path('M750 316V336H460V316',BLUE,1.5,dash='5 4',arrow=True);s.text(600,361,'repeat change + check' if not zh else '变更与检查持续迭代',16,MUTED,anchor='middle')
    s.circle(828,322,5,GOLD);s.text(843,328,'Review the delivery' if not zh else '审阅交付，决定接手',17,GOLD,550)
    s.line(38,382,1162,382)
    if kind=='development':
        for x,key in [(57,'left'),(658,'right')]:
            label(s,x,416,t[key]);s.rect(x,434,100,49,PALE,BLUE,2);s.text(x+50,464,'UI',17,BLUE,600,anchor='middle');s.rect(x+155,434,100,49,PALE,BLUE,2);s.text(x+205,464,'Logic' if not zh else '逻辑',17,BLUE,600,anchor='middle');s.line(x+100,459,x+154,459,BLUE,1.7,arrow=True);s.rect(x+310,434,100,49,PALE,BLUE,2);s.text(x+360,464,'Data' if not zh else '数据',17,BLUE,600,anchor='middle');s.line(x+255,459,x+309,459,BLUE,1.7,arrow=True)
        s.text(600,466,'→',29,MUTED,anchor='middle');s.text(57,518,'Schematic · stable element identities' if not zh else '结构示意 · 元素身份保持一致',16,MUTED);s.check(659,514);s.text(685,520,'Element coverage + regression evidence' if not zh else '元素覆盖 + 回归检查证据',17,TEAL)
    elif kind=='bugfix':
        for x,key in [(57,'left'),(658,'right')]:
            label(s,x,416,t[key]);s.text(x,451,'reproduction' if not zh else '复现用例',19,INK);s.text(x,486,'regression set' if not zh else '回归测试组',19,INK)
        s.text(342,451,'FAIL' if not zh else '失败',18,'#a24936',650);s.text(342,486,'recorded' if not zh else '已记录',18,MUTED)
        s.check(1013,446);s.text(1041,451,'PASS' if not zh else '通过',18,TEAL,650);s.check(1013,481);s.text(1041,486,'PASS' if not zh else '通过',18,TEAL,650)
        s.line(600,407,600,507);s.text(57,530,'Expected evidence pattern · no real test counts shown' if not zh else '预期证据形态示意 · 不代表真实用例数量',16,MUTED)
    else:
        label(s,57,416,t['left']);s.text(57,454,'Workload · unit · direction' if not zh else '负载 · 单位 · 优化方向',20,INK,550);s.text(57,488,'Method · margin · budget' if not zh else '方法 · 改进幅度 · 时间',20,INK,550)
        label(s,658,416,t['right']);items=[('baseline' if not zh else '基线',BLUE),('attempts' if not zh else '各次尝试',MUTED),('final' if not zh else '最终状态',TEAL)]
        s.line(674,459,1100,459,LINE,2)
        for x,(txt,col) in zip([674,879,1100],items):s.circle(x,459,6,col);s.text(x,494,txt,18,col,550,anchor='middle')
        s.text(658,530,'Process schematic · no invented scores or trajectory' if not zh else '过程结构示意 · 不虚构分数或提升曲线',16,MUTED)
    s.line(38,551,1162,551);s.text(38,589,t['bottom'],19,NAVY,550)
    s.save('autodev-'+kind+('.zh' if zh else '')+'.svg')

if __name__=='__main__':
    OUT.mkdir(exist_ok=True)
    for zh in [False,True]:
        brand(zh);overview(zh)
        for kind in SCENARIOS:scenario(kind,zh)
    print('Generated 10 accessible SVG assets in docs/assets/.')
