"""Rebuild ER visuals from the Mermaid sources retained in the documents."""
import html
import re
from pathlib import Path
DST=Path(__file__).resolve().parent
def save(name, text):
    (DST / name).write_text(text.rstrip()+'\n', encoding='utf-8')

def svg_begin(w,h,title,subtitle):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc">',
            f'<title id="title">{html.escape(title)}</title><desc id="desc">{html.escape(subtitle)}</desc>',
            f'<rect width="{w}" height="{h}" rx="16" fill="#0b1420"/>',
            f'<text x="40" y="42" fill="#f1f5f9" font-family="Arial,sans-serif" font-weight="700" font-size="25">{html.escape(title)}</text>',
            f'<text x="40" y="72" fill="#94a3b8" font-family="Arial,sans-serif" font-size="16">{html.escape(subtitle)}</text>']

def diagram(code, filename, title):
    edges = re.findall(r'^\s*(\w+)\s+([|}o{]+)--([|}o{]+)\s+(\w+)\s*:\s*(\w+)', code, re.M)
    nodes=[]
    for a,_,_,b,_ in edges:
        for n in (a,b):
            if n not in nodes: nodes.append(n)
    fields={n:[] for n in nodes}
    for node,body in re.findall(r'^\s*(\w+)\s*\{\s*\n(.*?)^\s*\}',code,re.M|re.S):
        fields[node]=[line.split() for line in body.splitlines() if line.strip()]
    sizes={n:70+30*len(fields[n]) for n in nodes}
    w=1200
    if len(nodes)==5:
        positions={'MACHINE':(40,120),'MAINT_JOB':(450,120),'TECHNICIAN':(860,120),'JOB_PART':(450,500),'PART':(860,500)}
        cw,h=300,790
    elif len(nodes)==3:
        parents=[n for n in nodes if n not in {e[3] for e in edges}]
        child=next(n for n in nodes if n not in parents)
        positions={parents[0]:(100,120),parents[1]:(760,120),child:(430,440)}
        cw,h=340,440+sizes[child]+85
    else:
        # Independent relationship pairs, one pair per row.
        positions={}
        y=120
        for index in range(0,len(nodes),2):
            positions[nodes[index]]=(80,y)
            positions[nodes[index+1]]=(780,y)
            y+=max(sizes[nodes[index]],sizes[nodes[index+1]])+100
        cw,h=340,y+25
    parts=svg_begin(w,h,title,'Endpoint labels show allowed participation: 1 = exactly one; 0..N = zero or many; 0..1 = optional one.')
    def label(x,y,s,color='#94a3b8',anchor='middle',size=14):
        parts.append(f'<text x="{x}" y="{y}" text-anchor="{anchor}" fill="{color}" font-family="Arial,sans-serif" font-size="{size}">{html.escape(s)}</text>')
    cardinality={'||':'1','o{':'0..N','}o':'0..N','o|':'0..1','|o':'0..1','|{':'1..N','}|':'1..N'}
    for a,left,right,b,relationship in edges:
        ax,ay=positions[a];bx,by=positions[b]
        ah,bh=sizes[a],sizes[b]
        if ay==by:
            direction=1 if bx>ax else -1
            x1=ax+cw if direction==1 else ax
            x2=bx if direction==1 else bx+cw
            y1,y2=ay+ah/2,by+bh/2
            mx=(x1+x2)/2
            d=f'M{x1} {y1} H{mx} V{y2} H{x2}'
            label(x1+direction*20,y1-12,cardinality[left], '#5eead4')
            label(x2-direction*26,y2-12,cardinality[right], '#5eead4')
            label(mx,max(y1,y2)+34,relationship.replace('_',' '),size=13)
        else:
            x1=ax+cw/2
            x2=bx+cw/2 if ax==bx else bx+cw*(.25 if ax<bx else .75)
            y1,y2=ay+ah,by
            my=(y1+y2)/2
            d=f'M{x1} {y1} V{my} H{x2} V{y2}'
            label(x1-12,y1+25,cardinality[left], '#5eead4',anchor='end')
            label(x2+12,y2-14,cardinality[right], '#5eead4',anchor='start')
            if x1==x2:
                label(x1+18,my,relationship.replace('_',' '),anchor='start',size=13)
            else:
                label((x1+x2)/2,my-12,relationship.replace('_',' '),size=13)
        parts.append(f'<path d="{d}" fill="none" stroke="#38bdf8" stroke-width="2"/>')
    for n in nodes:
        x,y=positions[n]; nh=sizes[n]
        parts.append(f'<rect x="{x}" y="{y}" width="{cw}" height="{nh}" rx="9" fill="#101e2e" stroke="#31516a"/>')
        parts.append(f'<path d="M{x+1} {y+46} H{x+cw-1}" stroke="#31516a"/>')
        label(x+18,y+30,n,'#5eead4','start',17)
        for i,field in enumerate(fields[n]):
            kind,name,*keys=field
            yy=y+72+i*30
            label(x+18,yy,name,'#e2e8f0','start',15)
            label(x+cw-18,yy,' '.join([kind,*keys]),'#94a3b8','end',12)
    label(40,h-26,'PK = primary key   /   FK = foreign key   /   UK = unique key',anchor='start',size=14)
    parts.append('</svg>')
    save('assets/'+filename,'\n'.join(parts))
    return f'![{title}](assets/{filename})\n\n<details>\n<summary>Diagram source (Mermaid)</summary>\n\n```mermaid\n{code.strip()}\n```\n\n</details>'

def slug(s):
    return re.sub(r'[^\w -]','',s.lower()).replace(' ','-')
for doc in sorted(DST.glob('*.md')):
    pattern=r'!\[([^\]]+)\]\(assets/([^\)]+\.svg)\).*?```mermaid\n(.*?)```'
    for title, filename, code in re.findall(pattern,doc.read_text(encoding='utf-8'),re.S):
        diagram(code,filename,title)
print('Rebuilt ER diagrams from their recorded Mermaid sources.')
