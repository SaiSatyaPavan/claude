# Builds practice-exam-answers-explained.pdf:  pip install reportlab;  cd study-guide && python3 make_guide.py ../practice-exam-answers-explained.pdf
import re, sys, importlib
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle, PageBreak,
                                KeepTogether, CondPageBreak, Flowable)
from reportlab.platypus.tableofcontents import TableOfContents
import diag_lib  # registers fonts
from content_v23 import E

OUT = sys.argv[1]
H = colors.HexColor
INK, MUTED, RULE, PANEL = H('#1d2330'), H('#5a6474'), H('#d5d9e0'), H('#f4f6f9')
ACC, OK, WARN, BAD, OOB = H('#1f5fd1'), H('#1c7a48'), H('#b26a00'), H('#c0392b'), H('#6a3fb5')
TERM_BG, TERM_FG, TERM_DIM, TERM_HI, TERM_PROMPT = H('#151a22'), H('#d7dee9'), H('#8b96a8'), H('#ffd166'), H('#7ee2a8')

S = {}
def st(name, **k):
    base = k.pop('parent', None)
    S[name] = ParagraphStyle(name, parent=S[base] if base else None, **k)
st('body', fontName='Serif', fontSize=10.6, leading=14.6, textColor=INK, spaceAfter=4, bulletFontName='Serif')
st('step', parent='body', leftIndent=20, bulletIndent=3, spaceAfter=2.5)
st('bul', parent='body', leftIndent=20, bulletIndent=8, spaceAfter=2.5)
st('bul2', parent='body', leftIndent=36, bulletIndent=24, spaceAfter=2.5)
st('exp', fontName='Sans', fontSize=9.6, leading=13.6, textColor=INK, spaceAfter=5)
st('note', fontName='Sans', fontSize=8.8, leading=12, textColor=INK, leftIndent=12, bulletIndent=2, spaceAfter=2, bulletFontName='Sym')
st('cap', fontName='Sans', fontSize=8.2, leading=11, textColor=MUTED, spaceBefore=3)
st('q', fontName='Sans-B', fontSize=10.6, leading=14.6, textColor=INK)
st('qcode', fontName='Mono', fontSize=8, leading=10.5, textColor=INK)
st('label', fontName='Sans-B', fontSize=8.4, leading=11, textColor=MUTED, spaceBefore=10, spaceAfter=5)
st('hook', fontName='Sans', fontSize=10.4, leading=14.5, textColor=H('#5a3d00'))
st('term', fontName='Mono', fontSize=7.3, leading=9.6, textColor=TERM_FG)
st('termt', fontName='Sans-B', fontSize=8.6, leading=11, textColor=INK, spaceBefore=8, spaceAfter=3)
st('h1', fontName='Sans-B', fontSize=26, leading=31, textColor=INK, spaceAfter=6)
st('sub', fontName='Sans', fontSize=12, leading=16.5, textColor=MUTED, spaceAfter=14)
st('intro', fontName='Sans', fontSize=10, leading=14.2, textColor=INK, spaceAfter=6)
st('toc0', fontName='Sans-B', fontSize=10.5, leading=15, textColor=INK, spaceBefore=6)
st('toc1', fontName='Sans', fontSize=9, leading=12.4, textColor=INK, leftIndent=14)
st('seth', fontName='Sans-B', fontSize=30, leading=36, textColor=INK)
st('sets', fontName='Sans', fontSize=12, leading=17, textColor=MUTED)
st('rev', fontName='Sans', fontSize=8.6, leading=11.4, textColor=INK)


def esc(t): return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
def code_inline(t): return re.sub(r'`([^`]+)`', r'<font name="Mono" size="9">\1</font>', t)
def rich(t): return t.replace('<code>', '<font name="Mono">').replace('</code>', '</font>')


def answer_flow(text, style_body='body'):
    out, prev = [], None
    for line in text.split('\n'):
        t = code_inline(esc(line))
        m = re.match(r'^(\d+)\. (.*)$', line)
        if m:
            out.append(Paragraph(code_inline(esc(m.group(2))), S['step'], bulletText=m.group(1) + '.')); prev = 'step'
        elif line.startswith('- '):
            sty = 'bul2' if prev in ('step', 'bul2') else 'bul'
            out.append(Paragraph(code_inline(esc(line[2:])), S[sty], bulletText='•')); prev = sty
        else:
            out.append(Paragraph(t, S[style_body])); prev = None
    return out


def term_block(lines):
    rows = []
    for ln in lines.split('\n'):
        cmd = ln.startswith('$ ')
        body = ln[2:] if cmd else ln
        body = esc(body)
        body = re.sub(r'^( +)', lambda m: '&nbsp;' * len(m.group(1)), body)
        body = re.sub(r'  +', lambda m: '&nbsp;' * len(m.group(0)), body)
        body = re.sub(r'\{\{(.+?)\}\}', lambda m: f'<font color="#ffd166"><b>{m.group(1)}</b></font>', body)
        if cmd:
            body = f'<font color="#7ee2a8"><b>$</b></font> <font color="#ffffff"><b>{body}</b></font>'
        rows.append([Paragraph(body or '&nbsp;', S['term'])])
    t = Table(rows, colWidths=['100%'])
    t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), TERM_BG), ('FONTNAME', (0, 0), (-1, -1), 'Mono'),
                           ('LEFTPADDING', (0, 0), (-1, -1), 9), ('RIGHTPADDING', (0, 0), (-1, -1), 9),
                           ('TOPPADDING', (0, 0), (-1, -1), 0.6), ('BOTTOMPADDING', (0, 0), (-1, -1), 0.6),
                           ('TOPPADDING', (0, 0), (-1, 0), 7), ('BOTTOMPADDING', (0, -1), (-1, -1), 7)]))
    return t


def boxed(flows, bg, line=None, pad=10, lw=3):
    t = Table([[flows]], colWidths=['100%'])
    sty = [('BACKGROUND', (0, 0), (-1, -1), bg), ('FONTNAME', (0, 0), (-1, -1), 'Sans'),
           ('LEFTPADDING', (0, 0), (-1, -1), pad + 2), ('RIGHTPADDING', (0, 0), (-1, -1), pad),
           ('TOPPADDING', (0, 0), (-1, -1), pad - 2), ('BOTTOMPADDING', (0, 0), (-1, -1), pad)]
    if line: sty.append(('LINEBEFORE', (0, 0), (0, -1), lw, line))
    t.setStyle(TableStyle(sty))
    return t


class Mark(Flowable):
    """Zero-size flowable that registers a TOC entry and the running footer label."""
    def __init__(self, level, text, key, foot):
        super().__init__(); self.level, self.text, self.key, self.foot = level, text, key, foot
    def wrap(self, *a): return (0, 0)
    def draw(self):
        self.canv.bookmarkPage(self.key)
        self.canv.addOutlineEntry(self.text, self.key, level=self.level, closed=False)
        self.canv._foot = self.foot


class Doc(BaseDocTemplate):
    def afterFlowable(self, f):
        if isinstance(f, Mark):
            self.notify('TOCEntry', (f.level, f.text, self.page, f.key))


class Numbered(canvas.Canvas):
    def __init__(self, *a, **k):
        k['initialFontName'] = 'Serif'
        super().__init__(*a, **k); self._pages = []; self._foot = ''
    def showPage(self):
        self._pages.append(dict(self.__dict__)); self._startPage()
    def save(self):
        n = len(self._pages)
        for stt in self._pages:
            self.__dict__.update(stt)
            if self._pageNumber > 1:
                self.setFont('Sans', 8); self.setFillColor(MUTED)
                self.drawString(0.85 * inch, 0.5 * inch, 'Practice exam: answers explained' + (('  ·  ' + self._foot) if self._foot else ''))
                self.drawRightString(letter[0] - 0.85 * inch, 0.5 * inch, f'Page {self._pageNumber} of {n}')
                self.setStrokeColor(RULE); self.setLineWidth(0.6)
                self.line(0.85 * inch, 0.66 * inch, letter[0] - 0.85 * inch, 0.66 * inch)
            super().showPage()
        super().save()


def q_header(n, e):
    setname = 'A' if n <= 20 else 'B'
    num = Paragraph(f'<font name="Sans-B" size="24" color="#ffffff">{n}</font>', ParagraphStyle('n', fontName='Sans-B', alignment=1, leading=26))
    meta = [Paragraph(f'<font name="Sans-B" size="7.6" color="#5a6474">SET {setname}  ·  {e["part"].upper()}</font>', S['cap']),
            Paragraph(f'<font name="Sans-B" size="15" color="#1d2330">{esc(e["topic"])}</font>', ParagraphStyle('t', fontName='Sans-B', leading=19)),
            Paragraph(f'<font name="Sans" size="8" color="#5a6474">Reread: {esc(e["reread"])}</font>', S['cap'])]
    t = Table([[num, meta]], colWidths=[0.62 * inch, None])
    t.setStyle(TableStyle([('BACKGROUND', (0, 0), (0, 0), ACC), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ('FONTNAME', (0, 0), (-1, -1), 'Sans'),
                           ('LEFTPADDING', (1, 0), (1, 0), 12), ('TOPPADDING', (0, 0), (-1, -1), 6), ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
                           ('LINEBELOW', (0, 0), (-1, -1), 0.8, RULE)]))
    return t


def question(n, e):
    story = [Mark(1, f'{n}. {e["topic"]}', f'q{n}', f'Question {n}: {e["topic"]}'), q_header(n, e), Spacer(1, 10)]
    qf = [Paragraph(esc(e['q']), S['q'])]
    if e.get('code'):
        qf += [Spacer(1, 6), term_block(e['code'])]
    story.append(boxed(qf, PANEL, ACC))
    story.append(Paragraph('<font color="#1c7a48"><font name="Sym-B">✎</font>  ANSWER</font>  <font color="#5a6474">(simple words: write this)</font>', S['label']))
    story += answer_flow(e['ans'])
    story.append(Spacer(1, 8))
    story.append(boxed([Paragraph('<font name="Sans-B" size="8" color="#b26a00">REMEMBER IT</font>', S['cap']), Spacer(1, 2), Paragraph(rich(e['hook']), S['hook'])], H('#fdf3dd'), WARN))
    story.append(CondPageBreak(1.6 * inch))
    story.append(Paragraph('<font color="#1f5fd1"><font name="Sym-B">▸</font>  EXPLANATION</font>  <font color="#5a6474">(understand it)</font>', S['label']))
    for para in e['exp'].split('\n'):
        story.append(Paragraph(rich(para), S['exp']))
    mod, fn = e['fig']
    dr, cap = getattr(importlib.import_module(mod), fn)()
    story.append(Spacer(1, 4))
    story.append(KeepTogether([Paragraph('<font name="Sans-B" size="8.4" color="#5a6474">SEE IT: TOPOLOGY / DIAGRAM</font>', S['cap']), Spacer(1, 5), dr, Paragraph(esc(cap), S['cap'])]))
    story.append(Spacer(1, 6))
    story.append(Paragraph('<font color="#5a6474">&gt;_  TRY IT: EXAMPLE COMMAND OUTPUT</font>  <font color="#8a94a3">(assumed values, to show what each command prints)</font>', S['label']))
    for o in e['outs']:
        blk = [Paragraph(esc(o['t']), S['termt']), term_block(o['lines']), Spacer(1, 4)]
        blk += [Paragraph(rich(nt), S['note'], bulletText='→') for nt in o['notes']]
        story.append(KeepTogether(blk))
        story.append(Spacer(1, 4))
    story.append(PageBreak())
    return story


def cover():
    s = [Spacer(1, 30), Paragraph('Practice Exam: Answers Explained', S['h1']),
         Paragraph('Diagnostic Technician practice exam, Sets A and B (40 questions). Simple answers to memorize, with explanations, topology diagrams and example command output. Checked against Prep Course v2.3.', S['sub'])]
    how = [Paragraph('<b>How each question is laid out</b>', S['intro'])]
    for b, t in [('Answer', 'in simple words, the way to write it on the exam (numbered steps for troubleshooting).'),
                 ('Remember it', 'a short memory hook or mnemonic.'),
                 ('Explanation', 'why the answer is right, in plain language.'),
                 ('See it', 'a topology or diagram of what is happening.'),
                 ('Try it', 'example command output with notes on what to look at. The values (addresses, serials, counts) are assumed, so you can see what each command prints; real servers will show their own values.')]:
        how.append(Paragraph(f'<b>{b}:</b> {t}', S['note'], bulletText='•'))
    s.append(boxed(how, PANEL, ACC, pad=12))
    s.append(Spacer(1, 10))
    s.append(boxed([Paragraph('<b>Study tip:</b> read the answer and the explanation, then cover the answer and write it from memory using only the memory hook. The last page lists every hook for quick review.', S['intro'])], H('#fdf3dd'), WARN, pad=12))
    s.append(Spacer(1, 14))
    toc = TableOfContents(tableStyle=TableStyle([('FONTNAME', (0, 0), (-1, -1), 'Sans'), ('VALIGN', (0, 0), (-1, -1), 'TOP'), ('RIGHTPADDING', (0, 0), (-1, -1), 0), ('LEFTPADDING', (0, 0), (-1, -1), 0)])); toc.levelStyles = [S['toc0'], S['toc1']]; toc.dotsMinLevel = 0
    s += [Paragraph('<b>Contents</b>', S['intro']), toc, PageBreak()]
    return s


def set_page(name, lo, hi, desc):
    return [Mark(0, f'Set {name}: questions {lo} to {hi}', f'set{name}', f'Set {name}'), Spacer(1, 200),
            Paragraph(f'Set {name}', S['seth']), Spacer(1, 6), Paragraph(f'Questions {lo} to {hi}', S['sets']), Spacer(1, 10),
            Paragraph(desc, S['intro']), PageBreak()]


def review():
    s = [Mark(0, 'Memory hooks: one-page review', 'review', 'Memory hooks'), Paragraph('Memory hooks: one-page review', ParagraphStyle('rh', parent=S['h1'], fontSize=18, leading=22)), Spacer(1, 6)]
    rows = []
    for n in range(1, 41):
        e = E[n]
        rows.append([Paragraph(f'<b>{n}</b>', S['rev']), Paragraph(f'<b>{esc(e["topic"])}</b>', S['rev']), Paragraph(rich(e['hook']), S['rev'])])
    t = Table(rows, colWidths=[0.3 * inch, 1.9 * inch, None], repeatRows=0)
    t.setStyle(TableStyle([('FONTNAME', (0, 0), (-1, -1), 'Sans'), ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                           ('ROWBACKGROUNDS', (0, 0), (-1, -1), [PANEL, colors.white]),
                           ('TOPPADDING', (0, 0), (-1, -1), 2.2), ('BOTTOMPADDING', (0, 0), (-1, -1), 2.4),
                           ('LINEBELOW', (0, 19), (-1, 19), 1.2, ACC)]))
    s.append(t)
    return s


doc = Doc(OUT, pagesize=letter, leftMargin=0.85 * inch, rightMargin=0.85 * inch, topMargin=0.7 * inch, bottomMargin=0.85 * inch,
          title='Practice Exam: Answers Explained', author='Study notes', subject='Diagnostic Technician practice exam: answers, explanations, diagrams and example output')
doc.addPageTemplates([PageTemplate(id='p', frames=[Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='f', leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)])])
story = cover()
story += set_page('A', 1, 20, 'Part 1, Foundations: questions 1 to 9.  Part 2, Troubleshooting: questions 10 to 16.  Part 3, Linux in practice: questions 17 to 20.')
for n in range(1, 21): story += question(n, E[n])
story += set_page('B', 21, 40, 'Part 1, Foundations: questions 21 to 29.  Part 2, Troubleshooting: questions 30 to 36.  Part 3, Linux in practice: questions 37 to 40.')
for n in range(21, 41): story += question(n, E[n])
story += review()
doc.multiBuild(story, canvasmaker=Numbered)
print('wrote', OUT)
