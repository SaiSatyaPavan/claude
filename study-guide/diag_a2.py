"""Set A diagrams for the new practice exam (questions that are new in this version)."""
import math
from diag_lib import *

WD = 482


def bolt(d, x, y, s=1.0, color=None):
    pts = [(x + 6 * s, y), (x, y + 11 * s), (x + 5 * s, y + 11 * s), (x + 2 * s, y + 21 * s), (x + 11 * s, y + 7 * s), (x + 6 * s, y + 7 * s), (x + 9 * s, y)]
    d.poly(pts, fill=color or C['warn'], stroke=H('#7a4a00'), sw=0.6)


def ground(d, x, y, color=INK):
    d.line(x, y, x, y + 8, color=color, sw=1.2)
    for i, w in enumerate((12, 8, 4)): d.line(x - w / 2, y + 8 + i * 3, x + w / 2, y + 8 + i * 3, color=color, sw=1.2)


def servers_roles():
    d = D(WD, 240)
    d.title(0, 10, 'Jobs servers do')
    d.box(0, 18, 160, 30, 'Office users + customers', 'laptops, phones, apps', 'p', fs=8.5)
    d.arrow([(80, 48), (80, 64)], 'n')
    d.rect(0, 66, 160, 170, 'p', r=4, sw=1.4)
    roles = [('Web / app server', 'runs the website and business apps', 'acc'), ('Database server', 'stores orders, accounts, records', 'ok'),
             ('File / storage server', 'shared files and backups', 'cu'), ('AI / GPU compute server', 'trains and runs AI models', 'oob'),
             ('Network services server', 'DNS, DHCP, logins', 'warn')]
    for i, (t, s, k) in enumerate(roles):
        y = 72 + i * 32.5
        d.rect(6, y, 148, 28, k, r=3, sw=0.9)
        d.circle(16, y + 14, 3.2, fill=C['ok'], stroke=C['ok'])
        d.text(25, y + 12, t, 7.8, KIND[k][2], 'start', 'Sans-B')
        d.text(25, y + 22, s, 6.5, MUTED)
    d.title(180, 10, 'How the job changes the machine')
    cols = [(180, 58, ''), (238, 112, 'Office desktop'), (350, 132, 'Server')]
    rows = [('Runs', 'office hours, a person at it', '24/7, nobody in front of it'),
            ('Power', '1 power supply', '2 hot-swap PSUs (redundant)'),
            ('Cooling', 'a few fans', 'many fans + air baffles'),
            ('Memory', 'normal RAM', 'ECC registered DIMMs'),
            ('Managed', 'by the person using it', 'remotely: BMC, SSH, scripts'),
            ('Shape', 'tower under a desk', 'rack units (1U = 1.75 in)'),
            ('If it fails', 'one person waits', 'the whole company stops')]
    for x, w, t in cols[1:]:
        d.rect(x, 18, w - 3, 20, 'dark' if t == 'Server' else 'p', r=3, sw=0.8)
        d.text(x + (w - 3) / 2, 31, t, 8, WHITE if t == 'Server' else INK, 'middle', 'Sans-B')
    for i, (a, b, c) in enumerate(rows):
        y = 42 + i * 27.5
        d.rect(180, y, 299, 24, 'p' if i % 2 == 0 else 'n', r=2, sw=0.4, stroke=H('#e1e5ea'))
        d.text(186, y + 15, a, 7.6, INK, 'start', 'Sans-B')
        d.text(242, y + 15, b, 7.2, MUTED)
        d.text(354, y + 15, c, 7.2, C['ok'], 'start', 'Sans-B')
    return d.d, 'Different jobs, same rule: a server is built to run all day without anyone in front of it, so it gets redundancy, ECC, hot-swap parts and remote management.'


def pcie_connects():
    d = D(WD, 236)
    d.title(0, 10, 'PCIe: the CPU\'s high-speed roads to every card')
    d.cpu(0, 22, 74, 206, 'CPU', sub='root complex')
    rows = [('GPU', 16, 50, 'x16  (Gen 5)', ['AI data in and out', 'of GPU memory'], 'oob'),
            ('100G NIC', 16, 128, 'x16  (Gen 4)', ['every network packet', 'crosses PCIe'], 'acc'),
            ('NVMe drive', 4, 200, 'x4  (Gen 4)', ['every disk read', 'and write'], 'ok')]
    for name, n, yc, lab, why, k in rows:
        gap = 1.7
        top = yc - (n - 1) * gap / 2
        for i in range(n): d.line(76, top + i * gap, 236, top + i * gap, k, sw=0.75)
        d.text(156, top - 5, f'{n} lanes', 7.4, C[k], 'middle', 'Sans-B')
        if name == 'GPU': d.gpu(244, yc - 22, 118, 40, '', power=True)
        elif name == '100G NIC': d.card(248, yc - 22, 112, 40, 16, 'QSFP 100G NIC', bracket=True)
        else: d.m2(248, yc - 10, 112, 20, '')
        d.text(372, yc - 12, name + '  ' + lab, 8.3, KIND[k][2], 'start', 'Sans-B')
        for j, row in enumerate(why): d.text(372, yc + 1 + j * 9, row, 7, MUTED)
    return d.d, 'Each device gets its own link from the CPU. A link is made of lanes; each lane sends and receives at the same time. More lanes = more data in parallel.'


def retimer_signal():
    d = D(WD, 226)
    stages = [(70, 'CPU'), (140, 'board trace'), (205, 'connector'), (270, 'riser'), (345, 'cable'), (440, 'device')]
    for x, s in stages:
        d.line(x, 18, x, 214, 'ghost', sw=0.6, dash=[2, 3]); d.text(x, 14, s, 6.8, MUTED, 'middle', 'Sans-B')
    rows = [('No help', 52, 'bad'), ('Redriver', 120, 'warn'), ('Retimer', 188, 'ok')]
    import random
    rnd = random.Random(4)
    for title, yc, k in rows:
        d.text(0, yc - 4, title, 8.5, C[k], 'start', 'Sans-B')
        d.line(70, yc - 9, 445, yc - 9, 'ghost', sw=0.5, dash=[1, 2]); d.line(70, yc + 9, 445, yc + 9, 'ghost', sw=0.5, dash=[1, 2])
        pts = []
        for x in range(70, 446, 2):
            t = x - 70
            if title == 'No help': A, noise = 20 * math.exp(-t / 150), 0
            elif title == 'Redriver':
                A = 20 * math.exp(-t / 150) if x < 270 else 20 * math.exp(-(x - 270) / 150)
                noise = 0 if x < 270 else rnd.uniform(-4.5, 4.5)
            else:
                A = 20 * math.exp(-t / 150) if x < 270 else 20 * math.exp(-(x - 270) / 150)
                noise = 0
            pts.append((x, yc - A * math.sin(t / 5.5) + noise))
        d.curve(pts, color=C[k], sw=1.3)
        if title != 'No help':
            d.box(254, yc - 30, 32, 16, title.upper()[:8], None, k, fs=5.6, r=3)
    d.cross(456, 52, 6); d.text(466, 55, 'errors', 7, C['bad'], 'start', 'Sans-B')
    d.text(452, 116, 'noisy', 7, C['warn'], 'start', 'Sans-B'); d.text(452, 126, 'errors', 7, C['warn'], 'start', 'Sans-B')
    d.tick(458, 186, 6); d.text(466, 190, 'clean', 7, C['ok'], 'start', 'Sans-B')
    d.text(70, 222, 'Dotted lines = the smallest signal the receiver can still read. A retimer re-sends a clean signal and resets the loss budget.', 6.9, MUTED)
    return d.d, 'Gen 5 signals fade fast over traces, connectors, risers and cables. A redriver amplifies everything, noise included. A retimer recovers the data and sends it again, clean.'


def esd():
    d = D(WD, 236)
    d.title(0, 10, 'Three ways ESD hurts a part')
    # 1 instant
    d.rect(0, 18, 296, 62, 'bad', r=5)
    d.rect(14, 32, 34, 34, 'dark', r=2); bolt(d, 26, 30, 1.25)
    d.text(58, 36, '1  Immediate failure', 9, KIND['bad'][2], 'start', 'Sans-B')
    d.lines(58, 48, ['Dead or erratic right away: not detected,', 'will not power on, or fails its first test.'], 7.2, MUTED)
    # 2 latent
    d.rect(0, 86, 296, 70, 'warn', r=5)
    d.text(14, 102, '2  Latent damage: weeks later (most costly)', 9, KIND['warn'][2], 'start', 'Sans-B')
    marks = [('Day 1', 'PASS', 'ok'), ('Week 1', 'PASS', 'ok'), ('Week 3', 'PASS', 'ok'), ('Week 6', 'FAIL', 'bad')]
    for i, (a, b, k) in enumerate(marks):
        x = 22 + i * 68
        d.line(x, 128, x + 68, 128, 'n', sw=1) if i < 3 else None
        d.circle(x, 128, 5, kind=k, fill=C[k], stroke=C[k])
        d.text(x, 118, a, 6.8, MUTED, 'middle'); d.text(x, 144, b, 7, C[k], 'middle', 'Sans-B')
    d.text(250, 132, 'weakened,', 6.8, MUTED, 'middle'); d.text(250, 141, 'not dead', 6.8, MUTED, 'middle')
    # 3 intermittent
    d.rect(0, 162, 296, 66, 'warn', r=5)
    d.text(14, 178, '3  Wasted time', 9, KIND['warn'][2], 'start', 'Sans-B')
    d.lines(14, 191, ['A damaged part gives confusing symptoms (random errors,', 'a link that drops) that send troubleshooting the wrong way.'], 7.2, MUTED)
    pts = [(14 + i * 3, 220 - (10 if i in (17, 41, 62) else 0)) for i in range(90)]
    d.curve(pts, color=C['warn'], sw=1.1)
    # prevention
    d.rect(312, 18, 170, 210, 'ok', r=6)
    d.text(324, 34, 'Prevent it', 9.5, KIND['ok'][2], 'start', 'Sans-B')
    # wrist strap drawing
    d.d.add(Circle(342, d.Y(62), 11, fillColor=None, strokeColor=C['ok'], strokeWidth=4))
    d.curve([(353, 62), (365, 58), (372, 66), (380, 58), (388, 66), (396, 62), (410, 62)], color=INK, sw=1)
    d.rect(410, 56, 26, 12, 'n', r=2); ground(d, 423, 68)
    d.text(342, 86, 'strap', 6.4, MUTED, 'middle'); d.text(423, 96, 'chassis / mat', 6.4, MUTED, 'middle')
    tips = ['Wear AND test a wrist strap', 'Work on a grounded mat', 'Hold parts by the edges', 'Never touch contacts or chips', 'Shielding bags (silver)', 'Power off before handling']
    for i, t in enumerate(tips):
        d.tick(326, 112 + i * 17, 3.6, sw=1.6); d.text(334, 115 + i * 17, t, 7.2, INK)
    d.text(397, 220, 'You feel ~3,000 V. Chips can die from < 100 V.', 6.3, KIND['ok'][2], 'middle', 'Sans-B')
    return d.d, 'ESD can kill a part at once, weaken it so it fails weeks later (the most costly kind), and waste hours with confusing symptoms. You cannot feel a zap that is big enough to damage a chip.'


def post_timeline():
    d = D(WD, 214)
    d.title(0, 10, 'What the firmware does before anything shows on screen (POST)')
    segs = [('Power', 'PSUs on,', 'BMC ready', 9, 'p'), ('CPU init', 'CPUs start,', 'microcode', 10, 'acc'),
            ('Memory training + test', 'tunes timing on every channel for', 'every DIMM, then tests it: the longest step', 42, 'cu'),
            ('PCIe', 'finds cards, trains', 'every link', 14, 'oob'), ('Option ROMs', 'RAID, NIC,', 'PXE firmware', 13, 'warn'), ('Boot', 'finds the', 'boot drive', 12, 'ok')]
    x = 0
    for t, a, b, w, k in segs:
        ww = w * 4.82
        d.rect(x, 52, ww - 2, 34, k, r=3, fill=C[k] if k != 'p' else H('#8a94a3'))
        d.text(x + ww / 2 - 1, 73, t, 7.6 if w > 9 else 6.6, WHITE, 'middle', 'Sans-B')
        d.text(x + ww / 2 - 1, 100, a, 6.6, MUTED, 'middle'); d.text(x + ww / 2 - 1, 109, b, 6.6, MUTED, 'middle')
        x += ww
    d.line(0, 36, 347, 36, 'n', sw=1); d.line(0, 32, 0, 40, 'n'); d.line(347, 32, 347, 40, 'n')
    d.text(173, 31, 'screen stays blank (several minutes on a big server)', 7.6, INK, 'middle', 'Sans-B')
    d.text(482, 31, 'logo / boot', 7.4, C['ok'], 'end', 'Sans-B')
    d.rect(0, 124, 482, 84, 'bad', r=6)
    d.text(12, 140, 'If you skipped these checks...', 9, KIND['bad'][2], 'start', 'Sans-B')
    risks = ['Hardware faults would reach the OS: crashes and corrupted data instead of a clear POST code.',
             'Devices would not start in a known state: memory and PCIe links untrained, cards missing or slow.',
             'You would lose your first clue: the POST code or BMC message that names the failing part.',
             'Be patient: on a server with lots of memory, minutes of blank screen is normal. Watch the POST code / BMC.']
    for i, r in enumerate(risks):
        d.text(14, 156 + i * 13, '•  ' + r, 7.4, INK if i < 3 else C['acc'], 'start', 'Sans' if i < 3 else 'Sans-B')
    return d.d, 'POST checks and sets up the hardware in order. Memory training is the long part, and it grows with the amount of memory installed.'


def bios_settings():
    d = D(WD, 238)
    d.rect(0, 10, 282, 226, 'dark', r=4, fill=H('#1a3478'), stroke=H('#0f2152'))
    d.rect(0, 10, 282, 18, 'dark', r=4, fill=H('#0f2152'), stroke=H('#0f2152'))
    d.text(141, 22, 'Server Setup Utility (UEFI)', 7.6, WHITE, 'middle', 'Sans-B')
    tabs = ['Main', 'Boot', 'PCIe', 'Memory', 'CPU/Power', 'Mgmt']
    for i, t in enumerate(tabs): d.text(10 + i * 46, 41, t, 7, H('#ffd84d') if i == 1 else H('#c9d6f5'), 'start', 'Sans-B')
    rows = [('1', 'Boot Mode', 'UEFI'), ('1', 'Boot Option #1', 'NVMe: PM9A3 960G'), ('1', 'Secure Boot', 'Enabled'),
            ('2', 'Slot 3 Enable', 'Enabled'), ('2', 'Slot 3 Bifurcation', 'x4x4x4x4'), ('2', 'Link Speed', 'Auto'),
            ('2', 'Above 4G Decoding', 'Enabled'), ('2', 'Resizable BAR', 'Enabled'), ('3', 'Memory Mode', 'Independent'),
            ('3', 'Memory Speed', 'Auto'), ('4', 'VT-x / VT-d', 'Enabled'), ('4', 'Power Profile', 'Performance'), ('5', 'Console Redirect', 'COM1 115200')]
    cols = {'1': 'acc', '2': 'oob', '3': 'cu', '4': 'ok', '5': 'warn'}
    for i, (g, a, b) in enumerate(rows):
        y = 58 + i * 13.6
        d.circle(12, y - 3, 4, fill=C[cols[g]], stroke=C[cols[g]])
        d.text(12, y - 0.6, g, 5.5, WHITE, 'middle', 'Sans-B')
        d.text(22, y, a, 7.2, H('#e3eaf9'), 'start', 'Mono')
        d.text(272, y, '[' + b + ']', 7.2, H('#ffffff'), 'end', 'Mono-B')
    items = [('1', 'Boot settings', 'boot order, UEFI/Legacy, Secure Boot', '"No bootable device" or a PXE loop'),
             ('2', 'PCIe settings', 'slot on/off, bifurcation, speed, 4G, BAR', 'card missing, x4 not x16, GPU fails'),
             ('3', 'Memory settings', 'speed, mirroring, sparing', 'less memory shown, unstable'),
             ('4', 'CPU / power', 'virtualization, cores, power profile', 'VMs fail, slow server (power saving)'),
             ('5', 'Console / mgmt', 'serial redirect, BMC network', 'SOL shows nothing during POST')]
    for i, (g, t, a, b) in enumerate(items):
        y = 10 + i * 45.5
        k = cols[g]
        d.rect(294, y, 188, 41, k, r=4)
        d.badge(306, y + 12, g, k, r=6.5, fs=7)
        d.text(317, y + 15, t, 8.4, KIND[k][2], 'start', 'Sans-B')
        d.text(300, y + 26, a, 6.5, MUTED)
        d.text(300, y + 36, 'Wrong: ' + b, 6.5, C['bad'], 'start', 'Sans-B')
    return d.d, 'The BIOS/UEFI setup stores how the hardware starts. One wrong setting can hide a device, slow the server, or stop it booting.'


def no_power():
    d = D(WD, 230)
    d.rect(0, 14, 26, 150, 'dark', r=3, fill=H('#2b2f36'))
    d.text(13, 176, 'PDU', 7.5, INK, 'middle', 'Sans-B')
    for i in range(7):
        d.rect(6, 22 + i * 20, 14, 12, 'n', r=2, fill=H('#4b5160'), stroke=H('#6b7280'))
    d.d.add(Circle(13, d.Y(28), 2, fillColor=C['ok'], strokeColor=None))
    d.d.add(Circle(13, d.Y(48), 2, fillColor=H('#9aa3ad'), strokeColor=None))
    d.server(60, 18, 170, 30, None, leds=('ok', 'ok'))
    d.text(240, 37, 'Server above: running', 7.8, C['ok'], 'start', 'Sans-B')
    d.server(60, 58, 170, 30, None, leds=('ghost', 'ghost'))
    d.text(240, 72, 'This server: no lights,', 7.8, C['bad'], 'start', 'Sans-B'); d.text(240, 82, 'button does nothing', 7.8, C['bad'], 'start', 'Sans-B')
    d.curve([(20, 28), (40, 28), (40, 33), (60, 33)], color=INK, sw=1.4)
    d.curve([(20, 48), (46, 48), (46, 73), (60, 73)], color=INK, sw=1.4, dash=[3, 2])
    d.rect(330, 14, 152, 118, 'oob', r=6)
    d.text(342, 30, 'Ask the BMC first', 8.8, KIND['oob'][2], 'start', 'Sans-B')
    d.text(342, 46, 'BMC answers (ping / web / ipmitool):', 7, INK, 'start', 'Sans-B')
    d.lines(342, 56, ['standby power is reaching the board.', 'Look at the power-on path: button,', 'PSU output, board, SEL events.'], 6.8, MUTED)
    d.text(342, 92, 'BMC is dead too:', 7, INK, 'start', 'Sans-B')
    d.lines(342, 102, ['no standby power at all. Look at the', 'outlet, breaker, cords and PSUs.'], 6.8, MUTED)
    d.title(0, 196, 'Follow the power, one link at a time')
    chain = [('1 Power source', 'outlet, breaker'), ('2 Cords + PSUs', 'clips, latched, LEDs'), ('3 The BMC', 'answers? power on'), ('4 Interlocks', 'lid, intrusion'),
             ('5 Shorted part', 'minimum config'), ('6 Motherboard', 'last')]
    for i, (t, s) in enumerate(chain):
        x = i * 81
        d.box(x, 204, 74, 26, t, s, 'oob' if i == 2 else 'n', fs=7, sfs=5.9)
        if i: d.arrow([(x - 7, 217), (x, 217)], 'n', sw=1)
    return d.d, 'The server above works on the same PDU, so the PDU has power. Check this server\'s outlet, cords and PSUs, and use the BMC to see whether standby power arrives.'


def four_isolation():
    d = D(WD, 252)
    panels = [('1', 'Swap with known-good', 'Convinced: fault follows the part (or stays with the slot) every time.', 'Risk: a bad slot can damage the good part.'),
              ('2', 'Minimum configuration', 'Convinced: it fails the moment one part is added back.', 'Limit: slow; a load-only fault may not appear.'),
              ('3', 'Half-splitting', 'Convinced: the fault stays in one half as you keep splitting.', 'Limit: needs parts you can test separately.'),
              ('4', 'Compare with a golden unit', 'Convinced: you find the one difference, and changing it fixes it.', 'Limit: the golden unit must really match.')]
    for i, (n, t, a, b) in enumerate(panels):
        x = (i % 2) * 245; y = 4 + (i // 2) * 126
        d.rect(x, y, 237, 118, 'p', r=6)
        d.badge(x + 14, y + 15, n, 'acc'); d.text(x + 26, y + 18, t, 9, INK, 'start', 'Sans-B')
        cy = y + 30
        if n == '1':
            d.box(x + 20, cy + 6, 60, 26, 'Slot A', 'suspect', 'bad', fs=7.5, sfs=6.2)
            d.box(x + 150, cy + 6, 60, 26, 'Slot B', 'known-good', 'ok', fs=7.5, sfs=6.2)
            d.arrow([(x + 80, cy + 14), (x + 150, cy + 14)], 'acc', 'move the part', lfs=6.5)
            d.arrow([(x + 150, cy + 26), (x + 80, cy + 26)], 'ok', None)
        elif n == '2':
            d.rect(x + 20, cy + 2, 110, 36, 'n', r=3)
            d.box(x + 26, cy + 8, 30, 24, 'CPU', None, 'ok', fs=7)
            d.dimm(x + 64, cy + 12, 56, 14, chips=5, ecc=False)
            d.text(x + 140, cy + 17, '+ 1 part at a time', 7, C['acc'], 'start', 'Sans-B')
            d.text(x + 140, cy + 28, 'until it fails', 7, MUTED)
        elif n == '3':
            for j in range(8):
                k = 'ghost' if j < 4 else ('bad' if j == 6 else 'acc')
                d.rect(x + 18 + j * 25, cy + 10, 21, 18, k, r=2, fill=W[k])
            d.line(x + 117, cy + 2, x + 117, cy + 36, 'bad', sw=1.6, dash=[3, 2])
            d.text(x + 60, cy + 42, 'good half', 6.6, MUTED, 'middle'); d.text(x + 168, cy + 42, 'fault is here', 6.6, C['bad'], 'middle', 'Sans-B')
        else:
            d.server(x + 18, cy + 4, 82, 22, 'golden', leds=('ok',))
            d.server(x + 130, cy + 4, 82, 22, 'suspect', leds=('bad',))
            d.text(x + 115, cy + 18, 'diff', 7, C['acc'], 'middle', 'Sans-B')
        d.text(x + 10, y + 88, a, 6.7, C['ok'], 'start', 'Sans-B')
        d.text(x + 10, y + 104, b, 6.7, C['bad'], 'start', 'Sans-B')
    return d.d, 'Four ways to prove the faulty part. Each one changes only one thing at a time, and each has a limit you should say out loud in your answer.'


def nvme_half():
    d = D(WD, 222)
    d.cpu(0, 40, 66, 120, 'CPU', sub='root ports')
    d.box(110, 20, 92, 36, 'Root port A', 'Gen 4 x4 trained', 'ok', fs=7.8, sfs=6.4)
    d.box(110, 132, 92, 36, 'Root port B', 'only x2 trained?', 'warn', fs=7.8, sfs=6.4)
    for i in range(4): d.line(66, 32 + i * 2.2, 110, 32 + i * 2.2, 'ok', sw=0.8)
    for i in range(4): d.line(66, 146 + i * 2.2, 110, 146 + i * 2.2, 'warn' if i < 2 else 'ghost', sw=0.8)
    for i in range(4): d.line(202, 32 + i * 2.2, 250, 32 + i * 2.2, 'ok', sw=0.8)
    for i in range(4): d.line(202, 146 + i * 2.2, 250, 146 + i * 2.2, 'warn' if i < 2 else 'ghost', sw=0.8)
    d.nvme_u2(252, 6, 44, 56, 'Drive A (bay 0)')
    d.nvme_u2(252, 120, 44, 56, 'Drive B (bay 5)')
    # thermometer
    d.rect(306, 124, 8, 38, 'bad', r=4, fill=W['bad']); d.rect(307.5, 140, 5, 21, 'bad', r=2, fill=C['bad'])
    d.text(320, 140, 'hot bay?', 7, C['bad'], 'start', 'Sans-B'); d.text(320, 150, 'throttling', 6.6, MUTED)
    d.title(370, 10, 'Same fio test')
    for i, (lab, v, k) in enumerate([('A', 6.8, 'ok'), ('B', 3.3, 'warn')]):
        y = 26 + i * 36
        d.text(370, y + 15, lab, 9, INK, 'start', 'Sans-B')
        d.rect(384, y, v * 13, 22, k, r=2, fill=C[k])
        d.text(384 + v * 13 + 4, y + 15, f'{v} GB/s', 7.4, INK, 'start', 'Sans-B')
    d.title(0, 194, 'Possible causes (check each)')
    causes = [('link x2 / Gen 3', 'warn'), ('bay wired for fewer lanes', 'warn'), ('shared switch / other CPU', 'acc'), ('hot: throttling', 'bad'),
              ('wear / firmware', 'cu'), ('drive full or busy', 'p'), ('test not like the rating', 'p')]
    x = 0; y = 202
    for t, k in causes:
        w = d.pill(x, y, t, k, fs=6.6)
        x += w + 5
    return d.d, 'Two identical drives should match. Compare the link each one trained to, the path it takes, its temperature, firmware and format. Then swap bays.'
