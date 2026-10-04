"""Set B diagrams (questions 21-40; 21, 22 and 24 reuse diag_a)."""
import math, random
from diag_lib import *

WD = 482


def dns_flow():
    d = D(WD, 240)
    d.box(0, 74, 78, 40, 'ping db01', 'needs an IP', 'acc', fs=8.5)
    d.box(110, 10, 120, 54, '1  /etc/hosts', ['local file, checked FIRST', 'db01 not listed here'], 'p', fs=8.5, sfs=6.5)
    d.box(110, 118, 120, 50, '2  /etc/resolv.conf', ['nameserver 10.20.5.5', 'search lab.local'], 'p', fs=8.5, sfs=6.5)
    d.arrow([(78, 86), (110, 40)], 'acc'); d.arrow([(170, 64), (170, 118)], 'n')
    d.text(176, 94, 'not found', 6.4, MUTED)
    d.cylinder(262, 100, 96, 80, '3  DNS server', '10.20.5.5', 'ok')
    d.arrow([(230, 143), (262, 143)], 'ok')
    d.box(392, 10, 90, 40, 'Other DNS servers', 'if not its domain', 'ghost', fs=7.6, sfs=6.2)
    d.arrow([(330, 100), (392, 36)], 'ghost', dash=[3, 2], both=True)
    d.box(392, 72, 90, 44, '4  Cache', ['answer kept for', 'its TTL (300 s)'], 'warn', fs=8, sfs=6.4)
    d.arrow([(358, 120), (392, 100)], 'warn')
    d.arrow([(262, 186), (40, 186), (40, 114)], 'ok')
    d.text(150, 182, 'answer: db01 = 10.4.2.15', 7.4, C['ok'], 'middle', 'Sans-B')
    d.rect(0, 198, 482, 40, 'p', r=4)
    d.text(8, 211, 'DNS records on the server:', 7, INK, 'start', 'Sans-B')
    recs = [('A', 'db01  ->  10.4.2.15', 'name to IPv4'), ('AAAA', 'db01  ->  IPv6 address', 'name to IPv6'), ('CNAME', 'files  ->  fileserver01', 'an alias')]
    for i, (t, a, b) in enumerate(recs):
        x = 8 + i * 158
        d.text(x, 226, t, 7.2, C['ok'], 'start', 'Mono-B'); d.text(x + 34, 226, a, 6.4, INK, 'start', 'Mono')
        d.text(x + 34, 234, b, 5.9, MUTED)
    return d.d, 'Linux looks in /etc/hosts first, then asks the DNS server named in /etc/resolv.conf. The DNS server answers from its records (an A record maps a name to an IPv4 address) and the answer is cached.'


def topo_compare():
    d = D(WD, 252)
    d.title(0, 10, 'Expected: the diagram')
    d.box(0, 40, 64, 40, 'CPU 1', 'root complex', 'n', fs=8)
    d.line(64, 60, 74, 60, 'n'); d.line(74, 33, 74, 109, 'n')
    for y, t in ((22, '01.0'), (62, '03.0'), (98, '05.0')):
        d.line(74, y + 11, 84, y + 11, 'n'); d.box(84, y, 56, 22, 'port ' + t, None, 'p', fs=6.8)
    d.box(152, 22, 50, 22, 'switch', None, 'oob', fs=6.8); d.line(140, 33, 152, 33, 'n')
    d.box(216, 6, 72, 22, 'GPU slot 1', None, 'oob', fs=6.8); d.box(216, 36, 72, 22, 'GPU slot 2', None, 'oob', fs=6.8)
    d.line(202, 30, 216, 17, 'n'); d.line(202, 37, 216, 47, 'n')
    d.box(152, 62, 72, 22, 'NIC slot 3', None, 'acc', fs=6.8); d.line(140, 73, 152, 73, 'n')
    d.box(152, 98, 72, 22, 'NVMe bay 0', None, 'ok', fs=6.8); d.line(140, 109, 152, 109, 'n')
    d.rect(310, 16, 172, 104, 'p', r=5)
    d.text(320, 32, 'The diagram shows:', 7.8, INK, 'start', 'Sans-B')
    for i, t in enumerate(['which CPU + root port per slot', 'switches, risers, retimers, cables', 'expected link width', 'slot-to-bus-number mapping', 'which devices share a path']):
        d.text(322, 46 + i * 14, '• ' + t, 7, INK)
    d.title(0, 138, 'Actual: what Linux found  (lspci -tv)')
    d.rect(0, 146, 482, 70, 'dark', r=4)
    tree = ['-[0000:00]-+-01.0-[17-1a]----00.0-[18-1a]--+-00.0-[19]----00.0  NVIDIA GPU   (slot 1)',
            '           |                               \\-04.0-[1a]--                    (empty!)',
            '           +-03.0-[3b]----00.0  Mellanox ConnectX-6 NIC',
            '           \\-05.0-[5e]----00.0  NVMe SSD']
    for i, t in enumerate(tree):
        d.text(8, 162 + i * 14, t, 6.5, H('#ff8a80') if 'empty' in t else H('#d7e2f5'), 'start', 'Mono-B' if 'empty' in t else 'Mono')
    rules = [('port, nothing under it', 'the device, its power, seating, slot'), ('whole branch gone', 'riser, cable, switch, retimer, BIOS'), ('all under one switch', 'the switch or its uplink')]
    for i, (a, b) in enumerate(rules):
        x = i * 162
        d.rect(x, 222, 156, 28, 'bad' if i == 0 else 'p', r=4)
        d.text(x + 6, 233, a, 6.8, C['bad'] if i == 0 else INK, 'start', 'Sans-B'); d.text(x + 6, 244, '-> ' + b, 6.3, INK)
    return d.d, 'The diagram is what should be there; the tree is what Linux found. Here GPU slot 2\'s port (04.0) exists with nothing under it, so suspect that GPU, its power, seating or slot.'


def bmc_board():
    d = D(WD, 236)
    d.rect(0, 8, 316, 220, 'p', r=6)
    d.text(10, 22, 'MOTHERBOARD', 7.4, MUTED, 'start', 'Sans-B')
    d.box(14, 32, 64, 50, 'CPU 1', 'main power', 'ghost', fs=8)
    d.box(88, 32, 64, 50, 'CPU 2', 'main power', 'ghost', fs=8)
    d.box(162, 32, 140, 50, 'Operating system', 'crashed / hung', 'bad', fs=8.5)
    d.cross(290, 42, 5)
    d.rect(14, 100, 156, 120, 'oob', r=6)
    d.text(24, 116, 'BMC', 11, KIND['oob'][2], 'start', 'Sans-B')
    d.text(24, 128, 'a small separate computer', 6.8, MUTED)
    d.box(24, 136, 64, 32, 'own CPU', 'own firmware', 'n', fs=7.4, sfs=6)
    d.box(96, 136, 64, 32, 'own NIC', 'mgmt port', 'n', fs=7.4, sfs=6)
    d.box(24, 176, 136, 34, 'standby power', 'on while plugged in, even when off', 'warn', fs=7.4, sfs=6)
    feeds = [('sensors: temp, fans, PSU, volts', 112), ('SEL: event log with times', 136), ('power control: on/off/cycle/NMI', 160), ('video + serial: KVM and SOL', 184), ('boot order, virtual media', 208)]
    for t, y in feeds:
        d.arrow([(170, y - 3), (184, y - 3)], 'oob', sw=1)
        d.text(188, y, t, 6.7, INK)
    d.laptop(352, 128, 62, 'Your laptop')
    d.arrow([(352, 150), (160, 150)], 'oob', 'management network', dash=[4, 2], lfs=6.8, lpos=0.18, ldy=-5)
    d.rect(330, 8, 152, 106, 'ok', r=6)
    d.text(340, 24, 'Works when...', 8.6, KIND['ok'][2], 'start', 'Sans-B')
    for i, t in enumerate(['the OS has crashed', 'the server is powered off', 'no OS is installed', 'the data network is down']):
        d.tick(344, 40 + i * 17, 3.6, sw=1.6); d.text(352, 43 + i * 17, t, 7.2, INK)
    d.text(406, 230, 'iDRAC (Dell)  iLO (HPE)  XCC (Lenovo)', 6.4, MUTED, 'middle')
    return d.d, 'The BMC has its own processor, firmware, network port and standby power. It does not need the operating system, so it keeps working when the OS is gone.'


def lnk_training():
    d = D(WD, 210)
    d.rect(0, 22, 26, 150, 'dark', r=3, fill=H('#2b2f36'))
    d.text(13, 186, 'slot', 7, INK, 'middle', 'Sans-B')
    for i in range(16):
        y = 28 + i * 9
        ok = i < 4
        d.line(26, y, 210, y, 'ok' if ok else 'ghost', sw=2 if ok else 1, dash=None if ok else [3, 3])
    d.card(214, 50, 110, 80, 16, 'x16 card', bracket=False)
    d.text(118, 12, '4 lanes trained (green)', 7.6, C['ok'], 'middle', 'Sans-B')
    d.rect(76, 104, 84, 14, 'n', r=3, fill=WHITE, stroke=WHITE)
    d.text(118, 114, '12 lanes unused', 7.4, MUTED, 'middle', 'Sans-B')
    d.rect(340, 22, 142, 70, 'dark', r=4)
    d.text(348, 40, 'LnkCap: Speed 16GT/s,', 6.8, H('#d7e2f5'), 'start', 'Mono')
    d.text(348, 51, '        Width x16', 6.8, H('#d7e2f5'), 'start', 'Mono')
    d.text(348, 66, 'LnkSta: Speed 16GT/s,', 6.8, H('#d7e2f5'), 'start', 'Mono')
    d.text(348, 77, '        Width x4 (downgraded)', 6.8, H('#ff8a80'), 'start', 'Mono-B')
    d.text(340, 108, 'Cap = what it CAN do', 8, INK, 'start', 'Sans-B')
    d.text(340, 121, 'Sta = what it GOT (status)', 8, INK, 'start', 'Sans-B')
    d.text(340, 136, 'x4 of x16 = a quarter of the bandwidth', 7, C['bad'], 'start', 'Sans-B')
    causes = [('slot only wired x8 / Gen 4 slot', 'p'), ('poor seating', 'warn'), ('dirty connector', 'warn'), ('bad riser / cable / retimer', 'bad'), ('BIOS: forced speed, bifurcation', 'acc')]
    x = 0; y = 194
    for t, k in causes:
        w = d.pill(x, y, t, k, fs=6.6)
        x += w + 5
    return d.d, 'At power on each link trains its speed and width. LnkSta lower than LnkCap means the link is downtrained: it works, just slower.'


def four_layers():
    d = D(WD, 214)
    layers = [('4  Function', 'configured and working?', 'ip a,  nvidia-smi,  a test', 'ok'),
              ('3  Driver', 'is a driver attached?', 'lspci -k  ("Kernel driver in use"), dmesg', 'oob'),
              ('2  Bus', 'does the OS see it?', 'lspci,  lsblk,  nvme list', 'acc'),
              ('1  Physical', 'installed, seated, powered?', 'look, LEDs, BIOS / BMC inventory', 'p')]
    for i, (t, q, c, k) in enumerate(layers):
        y = 8 + i * 48
        d.rect(0, y, 316, 44, k, r=5)
        d.text(10, y + 17, t, 9.2, KIND[k][2], 'start', 'Sans-B')
        d.text(104, y + 17, q, 7.6, INK, 'start', 'Sans-B')
        d.text(10, y + 33, c, 7, INK, 'start', 'Mono')
    d.arrow([(330, 196), (330, 12)], 'n', None, sw=1.2)
    d.text(330, 206, 'bottom up', 6.6, MUTED, 'middle')
    d.rect(352, 8, 130, 196, 'n', r=6)
    d.text(362, 24, 'Example: a NIC', 8.6, INK, 'start', 'Sans-B')
    res = [('Function', 'no interface in ip a', 'ghost'), ('Driver', 'no driver line!', 'bad'), ('Bus', 'shows in lspci', 'ok'), ('Physical', 'seated, LEDs on', 'ok')]
    for i, (a, b, k) in enumerate(res):
        y = 34 + i * 34
        if k == 'ok': d.tick(368, y + 10, 4.5)
        elif k == 'bad': d.cross(368, y + 10, 4.5)
        else: d.line(364, y + 10, 372, y + 10, 'ghost', sw=2)
        d.text(380, y + 9, a, 7.6, INK, 'start', 'Sans-B'); d.text(380, y + 20, b, 7, C[k] if k != 'ghost' else MUTED, 'start', 'Sans-B')
    d.text(417, 184, 'Fix the driver,', 7.2, C['acc'], 'middle', 'Sans-B'); d.text(417, 194, 'not the card', 7.2, C['acc'], 'middle', 'Sans-B')
    return d.d, 'Physical, Bus, Driver, Function ("Please Buy Donuts Friday"). Find the first layer that fails: that is where the problem is.'


def five_whys():
    d = D(WD, 226)
    chain = [('Symptom', 'The GPU was not detected.', 'bad'), ('Why?', 'Its power cable was not connected.', 'warn'),
             ('Why?', 'The cable was routed where it could not reach.', 'warn'), ('Why?', 'The work instruction showed an old layout.', 'warn'),
             ('Why?', 'It was not updated after a design change.', 'warn'), ('Root cause', 'Process: no step to update instructions on design changes.', 'ok')]
    for i, (t, s, k) in enumerate(chain):
        x = i * 12; y = 4 + i * 37
        d.rect(x, y, 262, 32, k, r=5)
        d.text(x + 10, y + 13, t, 8, KIND[k][2], 'start', 'Sans-B')
        d.text(x + 10, y + 25, s, 7, INK)
        if i: d.arrow([(x - 6, y - 5), (x - 6, y + 10), (x, y + 10)], 'n', sw=0.9)
    d.rect(336, 4, 146, 216, 'p', r=6)
    d.text(346, 22, 'Symptom', 8.8, C['bad'], 'start', 'Sans-B')
    d.lines(346, 34, ['what you SEE:', '"GPU not detected"'], 7.2, INK)
    d.text(346, 70, 'Root cause', 8.8, C['ok'], 'start', 'Sans-B')
    d.lines(346, 82, ['WHY it happened.', 'Keep asking "why?"', 'until you reach a', 'process you can fix.'], 7.2, INK)
    d.text(346, 140, 'Fix only the symptom', 8, INK, 'start', 'Sans-B')
    d.lines(346, 152, ['(reseat, ship) and the', 'next unit fails the same', 'way. Fix the root cause', 'and it stops on every unit.'], 7.2, MUTED)
    return d.d, 'Each "why?" goes one level deeper. Stop when you reach a process, not a person or a single unit.'


def rack_move():
    d = D(WD, 222)
    d.rect(96, 6, 150, 168, 'p', r=4, sw=1.4)
    d.text(171, 186, 'rack: new position', 7.2, INK, 'middle', 'Sans-B')
    d.text(171, 196, '(moved server in blue)', 6.6, C['acc'], 'middle')
    for i in range(5):
        y = 14 + i * 32
        moved = i == 2
        d.server(102, y, 138, 26, None, leds=('ok',) if not moved else ('warn',))
        if moved: d.rect(99, y - 3, 144, 32, 'acc', r=4, sw=2, fill='none')
    d.laptop(0, 112, 62, 'Your laptop')
    d.arrow([(62, 120), (96, 92)], 'oob', dash=[4, 2]); d.badge(74, 98, 1, 'oob')
    d.switch(270, 46, 96, 30, 'switch port', ports=8, hi=3, hik='warn')
    d.box(270, 128, 96, 34, 'Gateway', '10.20.5.1', 'n', fs=8)
    d.line(244, 86, 270, 68, 'acc', sw=1.8); d.badge(256, 70, 2)
    d.badge(86, 74, 3); d.badge(86, 128, 4)
    d.line(318, 76, 318, 128, 'acc', sw=1.4); d.badge(318, 102, 5)
    steps = [('1', 'Alive?', 'BMC console, power status', 'oob'), ('2', 'Link', 'cable, LEDs, ethtool', 'acc'), ('3', 'NIC + driver', 'lspci -k, dmesg', 'acc'),
             ('4', 'IP address', 'ip a  (169.254? VLAN?)', 'acc'), ('5', 'Gateway', 'ip route, ping it', 'acc'), ('6', 'Names', 'test by IP vs by name', 'acc'), ('7', 'Service', 'sshd, firewall, what changed', 'acc')]
    for i, (n, t, s, k) in enumerate(steps):
        y = 6 + i * 30
        d.badge(386, y + 8, n, k, r=6.5, fs=7)
        d.text(396, y + 10, t, 7.4, INK, 'start', 'Sans-B'); d.text(396, y + 20, s, 6.4, MUTED)
    return d.d, 'First prove the server is alive through the BMC (you cannot SSH into a server that is off or crashed). Then work from the cable upward.'


def card_missing():
    d = D(WD, 214)
    d.cpu(0, 30, 70, 64, 'CPU', sub='root port')
    d.box(92, 40, 74, 44, 'Riser', 'riser cable', 'p', fs=8)
    d.box(188, 40, 70, 44, 'Slot 4', 'enabled?', 'p', fs=8)
    d.rect(282, 32, 126, 60, 'ghost', r=5, dash=[4, 3])
    d.text(345, 58, 'new 100G NIC', 8.4, MUTED, 'middle', 'Sans-B'); d.text(345, 71, 'not in lspci', 7.4, C['bad'], 'middle', 'Sans-B')
    for a, b in ((70, 92), (166, 188), (258, 282)): d.line(a, 62, b, 62, 'n', sw=1.6)
    d.box(188, 0, 120, 26, 'BIOS: slot, bifurcation', None, 'warn', fs=7)
    d.box(340, 0, 142, 26, 'BIOS / BMC inventory', None, 'oob', fs=7)
    d.badge(129, 36, 3); d.badge(223, 90, 4); d.badge(345, 100, 1); d.badge(330, 13, 2, 'oob'); d.badge(40, 100, 5)
    steps = [('1', 'Search right: lspci | grep -i -E "ethernet|mellanox"'), ('2', 'Does the BIOS or BMC inventory see it?'),
             ('3', 'Physical (off, ESD): seated, latched, riser, power'), ('4', 'BIOS: slot enabled, bifurcation, link speed'),
             ('5', 'Topology: lspci -tv vs diagram'), ('6', 'Logs: dmesg, BMC SEL for PCIe errors'), ('7', 'Swap: known-good slot or card')]
    for i, (n, t) in enumerate(steps):
        x = 0 if i < 4 else 262; y = 120 + (i % 4) * 22
        d.badge(x + 8, y + 7, n, 'oob' if n == '2' else 'acc', r=6.5, fs=7)
        d.text(x + 19, y + 10, t, 6.6, INK)
    return d.d, 'Before calling a card dead, walk its whole path: how you searched, BIOS and BMC, seating, settings, the PCIe tree, the logs, and a swap.'


def intermittent():
    d = D(WD, 222)
    d.title(0, 10, 'Runs 1 to 45 (log every run)')
    fails = {9, 24, 38}
    for i in range(45):
        x = i * 10.7
        k = 'bad' if (i + 1) in fails else 'ok'
        d.rect(x, 18, 9, 12, k, r=1.5, fill=C[k], stroke=C[k])
    for f in sorted(fails): d.text((f - 1) * 10.7 + 4.5, 42, f'#{f}', 6.4, C['bad'], 'middle', 'Sans-B')
    d.title(0, 64, 'GPU temperature during each run')
    base, top = 150, 76
    pts = []
    for i in range(45):
        t = 64 + 6 * math.sin(i / 2.3) + (16 if (i + 1) in fails else 0) + (6 if (i + 2) in fails or i in fails else 0)
        pts.append((i * 10.7 + 4.5, base - (t - 55) * 2.2))
    d.curve(pts, color=C['warn'], sw=1.6)
    thr = base - (80 - 55) * 2.2
    d.line(0, thr, 482, thr, 'bad', sw=0.9, dash=[4, 3]); d.text(482, thr - 3, '80 °C', 7, C['bad'], 'end', 'Sans-B')
    d.line(0, base, 482, base, 'n', sw=0.8)
    d.rect(0, 162, 482, 58, 'p', r=5)
    d.text(10, 177, 'Pattern: it fails only when the GPU passes 80 °C. Now you can reproduce it on purpose (more load, more heat).', 7.4, INK, 'start', 'Sans-B')
    d.text(10, 193, 'for i in $(seq 1 100); do ./test.sh >> results.txt; done', 7.6, INK, 'start', 'Mono-B')
    d.text(10, 208, 'Watch dmesg -w and the sensors while it loops. At 1 failure in 15 runs, you need 100+ clean runs to trust a fix.', 7, MUTED)
    return d.d, 'Turn "random" into a pattern: log every run, line it up with temperature, load and time, then make the condition happen on purpose.'


def boot_chain():
    d = D(WD, 232)
    rows = [('1 Power + BMC', 'no lights, shuts off, amber LED', 'PSUs, cords, BMC SEL'),
            ('2 POST', 'stuck POST code, beeps, memory errors', 'POST code, SEL; wait for memory training'),
            ('3 UEFI / BIOS', '"No bootable device", PXE loop', 'BIOS: drive seen? boot order, UEFI/Legacy'),
            ('4 Bootloader (GRUB)', 'grub rescue>, file not found', 'boot partition, the drive'),
            ('5 Kernel', 'kernel panic, cannot mount root fs', 'read the exact message; storage driver'),
            ('6 System startup', 'emergency mode', '/etc/fstab, failing disk: journalctl -xb')]
    d.text(0, 10, 'STAGE', 7, MUTED, 'start', 'Sans-B'); d.text(130, 10, 'FAILURE LOOKS LIKE', 7, MUTED, 'start', 'Sans-B'); d.text(300, 10, 'WHERE TO LOOK', 7, MUTED, 'start', 'Sans-B')
    kinds = ['p', 'cu', 'acc', 'oob', 'warn', 'ok']
    for i, (a, b, c) in enumerate(rows):
        y = 16 + i * 35
        k = kinds[i]
        d.rect(0, y, 120, 30, k, r=4)
        d.text(8, y + 19, a, 8.2, KIND[k][2], 'start', 'Sans-B')
        d.rect(126, y, 168, 30, 'n', r=4, sw=0.6)
        d.text(132, y + 19, b, 7, C['bad'], 'start', 'Sans-B')
        d.rect(300, y, 182, 30, 'p', r=4, sw=0.6)
        d.text(306, y + 19, c, 6.9, INK)
        if i < 5: d.arrow([(60, y + 30), (60, y + 35)], 'n', sw=1)
    d.text(0, 230, 'Watch the console (BMC virtual console or SOL) and note exactly where it stops. Fans and LEDs only prove power.', 7.2, C['acc'], 'start', 'Sans-B')
    return d.d, 'Booting is a chain. The stage where it stops tells you which link broke and where to look next.'


def nvme_drop():
    d = D(WD, 222)
    d.cpu(0, 24, 66, 60, 'CPU', sub='root port')
    d.box(86, 32, 66, 44, 'retimer', 'on the path', 'oob', fs=8)
    d.rect(172, 14, 230, 80, 'p', r=5)
    d.text(182, 28, 'BACKPLANE', 7, MUTED, 'start', 'Sans-B')
    for i in range(6):
        x = 182 + i * 36
        bad = i == 3
        d.rect(x, 34, 30, 52, 'bad' if bad else 'n', r=3, fill=W['bad'] if bad else H('#c8ced6'))
        d.text(x + 15, 64, f'bay {i}', 6.5, C['bad'] if bad else INK, 'middle', 'Sans-B')
    d.line(66, 54, 86, 54, 'n', sw=1.6); d.line(152, 54, 172, 54, 'n', sw=1.6)
    d.rect(406, 26, 9, 46, 'bad', r=4, fill=W['bad']); d.rect(407.5, 46, 6, 25, 'bad', r=2, fill=C['bad'])
    d.text(420, 44, 'hot', 7, C['bad'], 'start', 'Sans-B'); d.text(420, 54, 'under load?', 6.6, MUTED)
    d.arrow([(290, 92), (290, 104), (362, 104), (362, 92)], 'acc')
    d.text(326, 116, 'move to bay 5', 6.8, C['acc'], 'middle', 'Sans-B')
    d.title(0, 132, 'Evidence to collect')
    ev = [('Kernel log', ['journalctl -b -1 -k', '| grep -i nvme'], 'acc'), ('BMC SEL', ['ipmitool sel elist', '(drive, PCIe, temp)'], 'oob'),
          ('Health', ['nvme smart-log', '/dev/nvme1'], 'ok'), ('Link', ['lspci -vv: LnkSta,', 'AER errors'], 'cu'), ('Firmware', ['drive, backplane,', 'BIOS versions'], 'warn')]
    for i, (a, b, k) in enumerate(ev):
        x = i * 97
        d.rect(x, 140, 92, 44, k, r=4)
        d.text(x + 6, 154, a, 8, KIND[k][2], 'start', 'Sans-B')
        for j, row in enumerate(b): d.text(x + 6, 167 + j * 9, row, 6.1, INK, 'start', 'Mono')
    d.text(0, 202, 'Follows the drive to bay 5: the drive.   Stays with bay 3: the bay, backplane connector or cable.', 7.4, INK, 'start', 'Sans-B')
    d.text(0, 216, 'A reboot resets the link, so the drive comes back. The cause is still there.', 7, MUTED)
    return d.d, 'Save the kernel messages before rebooting (or read the previous boot after), then check heat, health, the link and firmware, and swap bays to isolate.'


def gpu_tree():
    d = D(WD, 222)
    d.box(196, 4, 90, 30, 'CPU root ports', None, 'n', fs=8)
    for s, x in ((0, 60), (1, 302)):
        d.box(x, 54, 120, 28, f'PCIe switch {s + 1}', None, 'oob', fs=8)
        d.line(241, 34, x + 60, 54, 'n', sw=1.2)
        for g in range(4):
            gi = s * 4 + g
            gx = x - 50 + g * 56 + (0 if s == 0 else 0)
            empty = gi == 6
            if empty:
                d.rect(gx, 110, 50, 44, 'bad', r=4, dash=[3, 2], fill=WHITE)
                d.text(gx + 25, 128, 'port 0c.0', 6.4, C['bad'], 'middle', 'Mono-B'); d.text(gx + 25, 140, 'nothing', 6.4, C['bad'], 'middle', 'Sans-B'); d.text(gx + 25, 149, 'under it', 6.4, C['bad'], 'middle', 'Sans-B')
            else:
                d.rect(gx, 110, 50, 44, 'n', r=4, fill=H('#3a3f48'), stroke=H('#22262c'))
                d.circle(gx + 25, 132, 12, fill=H('#22262c'), stroke=H('#5b6270'))
            d.text(gx + 25, 166, f'GPU {gi}', 7, C['bad'] if empty else INK, 'middle', 'Sans-B')
            d.line(x + 60, 82, gx + 25, 110, 'bad' if empty else 'n', sw=1, dash=[2, 2] if empty else None)
    d.rect(0, 180, 236, 40, 'bad', r=5)
    d.text(8, 194, 'Empty port = the GPU end:', 7.6, KIND['bad'][2], 'start', 'Sans-B')
    d.text(8, 207, 'GPU, aux power cable, seating, slot, retimer', 6.8, INK)
    d.rect(246, 180, 236, 40, 'p', r=5)
    d.text(254, 194, 'Missing branch = upstream:', 7.6, INK, 'start', 'Sans-B')
    d.text(254, 207, 'whole switch gone: riser, cable, switch, BIOS', 6.8, MUTED)
    return d.d, 'Seven of eight GPUs. The port for GPU 6 exists, so the path is fine up to the port: look at the GPU, its power cable, its seating and the slot.'


def assembly_line():
    d = D(WD, 226)
    st = [('Kitting', 'parts + cables'), ('Assembly', 'routes cables'), ('Inspection', 'visual check'), ('Test', '3 units fail'), ('Ship', 'to customer')]
    for i, (t, s) in enumerate(st):
        x = i * 98
        d.box(x, 40, 86, 38, t, s, 'bad' if t == 'Test' else 'n', fs=8.5)
        if i: d.arrow([(x - 12, 59), (x, 59)], 'n')
    d.box(84, 0, 110, 28, 'Work instruction', 'old picture: update it', 'warn', fs=7.8, sfs=6.2)
    d.arrow([(139, 28), (139, 40)], 'warn')
    d.rect(186, 30, 296, 58, 'warn', r=8, dash=[4, 3], fill='none')
    d.text(334, 100, 'CONTAIN: same line, shift, batch, incl. waiting to ship', 7, KIND['warn'][2], 'middle', 'Sans-B')
    d.box(296, 112, 120, 30, 'Lead + Quality + Assembly', None, 'acc', fs=7.2)
    d.box(130, 112, 130, 30, 'CAPA', 'tracks the fix, updates the WI', 'ok', fs=8)
    d.arrow([(296, 127), (260, 127)], 'ok'); d.arrow([(343, 78), (343, 112)], 'acc')
    steps = [('Verify', 'all 3 pass, no damage'), ('Document', 'serials, cable, ports, photos'), ('Notify', 'lead, quality, assembly'),
             ('Contain', 'check the batch'), ('Prevent', 'pictures, labels, keyed, inspect'), ('CAPA', 'track it')]
    for i, (a, b) in enumerate(steps):
        x = i * 81
        d.rect(x, 158, 76, 46, 'p', r=4)
        d.badge(x + 10, 170, i + 1, 'acc', r=6, fs=6.8)
        d.text(x + 20, 173, a, 8, INK, 'start', 'Sans-B')
        words = b.split(', ')
        d.lines(x + 6, 186, [', '.join(words[:2]), ', '.join(words[2:])] if len(words) > 2 else [b], 6, MUTED, lead=8)
    d.text(241, 222, 'Fix the process, not the person.', 7.6, C['acc'], 'middle', 'Sans-B')
    return d.d, 'Fixing three units is not the end. Contain the rest of the batch, then change the process so the wrong connection cannot happen again.'


def grep_anatomy():
    d = D(WD, 222)
    parts = [('grep ', None), ('-', None), ('r', 'acc'), ('i', 'ok'), ('n', 'oob'), (' "nvme" ', 'cu'), ('/var/log/', 'warn')]
    x = 200; fs = 16
    pos = {}
    for t, k in parts:
        w = pdfmetrics.stringWidth(t, 'Mono-B', fs)
        d.text(x, 30, t, fs, C[k] if k else INK, 'start', 'Mono-B')
        pos[t] = (x + w / 2, k); x += w
    for t, (a, b), y in (('r', ('-r  recursive', 'every subfolder too'), 52), ('i', ('-i  ignore case', 'nvme = NVMe = NVME'), 78), ('n', ('-n  line numbers', '(+ file name with -r)'), 104)):
        cx, k = pos[t]
        d.line(cx, 36, cx, y - 3, k, sw=0.9); d.line(cx, y - 3, 186, y - 3, k, sw=0.9)
        d.text(182, y - 1, a, 8, C[k], 'end', 'Sans-B'); d.text(182, y + 9, b, 6.8, MUTED, 'end')
    for t, (a, b) in ((' "nvme" ', ('the word', 'to find')), ('/var/log/', ('where', 'to look'))):
        cx, k = pos[t]
        d.line(cx, 36, cx, 46, k, sw=0.9)
        d.text(cx, 56, a, 8, C[k], 'middle', 'Sans-B'); d.text(cx, 66, b, 6.8, MUTED, 'middle')
    d.title(0, 134, 'grep -r walks the whole tree')
    tree = [('/var/log/', 0, False), ('messages', 1, True), ('boot.log', 1, False), ('dmesg', 1, True), ('anaconda/', 1, False), ('syslog', 2, True), ('audit/', 1, False), ('audit.log', 2, False)]
    for i, (t, lvl, hit) in enumerate(tree):
        y = 146 + i * 9.2
        d.text(6 + lvl * 16, y, t, 7, C['ok'] if hit else INK, 'start', 'Mono-B' if hit else 'Mono')
        if hit: d.text(150, y, 'match', 6.4, C['ok'], 'start', 'Sans-B')
    d.rect(240, 130, 242, 86, 'p', r=5)
    d.text(250, 146, 'Count instead of listing', 8.4, INK, 'start', 'Sans-B')
    d.text(250, 164, 'grep -ric "nvme" /var/log/', 7.6, INK, 'start', 'Mono-B'); d.text(250, 175, 'count per file (-c replaces -n)', 6.8, MUTED)
    d.text(250, 194, 'grep -ri "nvme" /var/log/ | wc -l', 7.6, INK, 'start', 'Mono-B'); d.text(250, 205, 'one total for everything', 6.8, MUTED)
    return d.d, 'Read the options as "R-I-N": recursive, ignore case, numbers. Swap -n for -c to count. Add sudo: some logs are readable only by root.'


def dmesg_journal():
    d = D(WD, 220)
    d.title(0, 10, 'Timeline')
    d.text(226, 10, 'crash + reboot', 7, C['bad'], 'middle', 'Sans-B')
    d.rect(0, 18, 220, 28, 'p', r=4); d.text(110, 36, 'Boot -1  (last night)', 8.4, INK, 'middle', 'Sans-B')
    d.rect(232, 18, 250, 28, 'acc', r=4); d.text(357, 36, 'Boot 0  (now, after the reboot)', 8.4, KIND['acc'][2], 'middle', 'Sans-B')
    d.cross(226, 32, 6)
    d.rect(232, 52, 250, 9, 'warn', r=3, fill=C['warn']); d.text(226, 59, 'dmesg sees only this', 6.6, KIND['warn'][2], 'end', 'Sans-B')
    d.rect(0, 66, 220, 9, 'ok', r=3, fill=C['ok']); d.text(226, 73, 'journalctl -b -1 sees this', 6.6, KIND['ok'][2], 'start', 'Sans-B')
    d.rect(0, 86, 482, 50, 'warn', r=5)
    d.text(10, 102, 'dmesg  =  a whiteboard (RAM buffer)', 8.6, KIND['warn'][2], 'start', 'Sans-B')
    d.lines(10, 116, ['Shows kernel messages from THIS boot only. Wiped at every reboot,', 'so the messages from before the crash are already gone.'], 7.2, INK)
    d.rect(0, 144, 482, 50, 'ok', r=5)
    d.text(10, 160, 'journalctl -b -1  =  a notebook (journal on disk)', 8.6, KIND['ok'][2], 'start', 'Sans-B')
    d.lines(10, 174, ['Reads the PREVIOUS boot from the journal on disk: the last messages before', 'the crash (if the journal is persistent). Add -k for kernel messages only.'], 7.2, INK)
    d.text(0, 214, 'Before rebooting a failing server:  dmesg -T > before_reboot.txt  + BMC SEL + sensors + console screenshot', 7, C['acc'], 'start', 'Sans-B')
    return d.d, 'After a crash and reboot, dmesg only shows the new boot. journalctl -b -1 shows what happened before the crash.'


def two_cases():
    d = D(WD, 222)
    for row, (title, k, dns_ok, path_ok, verdict, checks) in enumerate([
            ('(a)  ping 10.4.2.15 works,  ping db01: "Name or service not known"', 'acc', False, True, 'DNS problem', 'resolv.conf, DNS reachable, nslookup / dig, /etc/hosts, FQDN'),
            ('(b)  db01 resolves to 10.4.2.15,  but no replies', 'cu', True, False, 'Network / target problem', 'right IP? ip route, ping gateway, traceroute, is db01 up, firewall')]):
        y = 4 + row * 110
        d.text(0, y + 10, title, 8, INK, 'start', 'Sans-B')
        d.box(0, y + 22, 76, 34, 'Server', None, 'n', fs=8)
        d.box(130, y + 22, 76, 34, 'DNS server', None, 'ok' if dns_ok else 'bad', fs=8)
        d.box(300, y + 22, 76, 34, 'db01', '10.4.2.15', 'ok' if path_ok else 'bad', fs=8)
        d.arrow([(76, y + 32), (130, y + 32)], 'ok' if dns_ok else 'bad', 'name?' , lfs=6.4)
        (d.tick if dns_ok else d.cross)(103, y + 46, 4)
        d.arrow([(76, y + 50), (100, y + 50), (100, y + 66), (338, y + 66), (338, y + 56)], 'ok' if path_ok else 'bad', 'ping by IP', lfs=6.4, ldy=10)
        (d.tick if path_ok else d.cross)(255, y + 66, 4)
        d.rect(392, y + 18, 90, 42, k, r=5)
        d.text(437, y + 36, verdict.split(' / ')[0] if '/' in verdict else verdict, 7.8, KIND[k][2], 'middle', 'Sans-B')
        if '/' in verdict: d.text(437, y + 48, verdict.split(' / ')[1], 7.8, KIND[k][2], 'middle', 'Sans-B')
        d.text(0, y + 92, 'Check: ' + checks, 7, INK)
    return d.d, 'IP works but the name fails: the network is fine and DNS is the problem. The name works but the IP does not answer: DNS is fine and the path or the target is the problem.'


def evidence_bundle():
    d = D(WD, 230)
    d.server(0, 30, 120, 30, 'failing server', leds=('bad',))
    d.circle(60, 104, 22, 'bad', sw=2)
    d.text(60, 103, '10:00', 9, C['bad'], 'middle', 'Sans-B'); d.text(60, 113, 'minutes', 6.4, MUTED, 'middle')
    files = [('unit123_dmesg.txt', 'kernel messages, this boot'), ('unit123_journal.txt', 'full journal, this boot'), ('unit123_prevboot.txt', 'journal of the boot before'),
             ('unit123_sel.txt', 'BMC events with times'), ('unit123_sensors.txt', 'temps, fans, PSUs, volts'), ('unit123_lspci.txt', 'devices, links, LnkSta'),
             ('unit123_dmidecode.txt', 'serials, BIOS, DIMMs'), ('unit123_ip.txt', 'interfaces and addresses')]
    for i, (f, w) in enumerate(files):
        y = 8 + i * 25
        d.rect(150, y, 196, 21, 'p', r=3)
        d.rect(154, y + 4, 10, 13, 'n', r=1, fill=WHITE)
        d.text(170, y + 10, f, 6.8, INK, 'start', 'Mono-B'); d.text(170, y + 18, w, 6, MUTED)
        d.arrow([(120, 45), (150, y + 10)], 'ghost', sw=0.5)
    d.box(380, 70, 102, 48, 'Copy off', ['scp unit123_* to', 'the share / ticket'], 'acc', fs=8.4, sfs=6.4)
    d.arrow([(346, 94), (380, 94)], 'acc')
    d.box(380, 140, 102, 40, 'Engineer', 'reads it later', 'ok', fs=8.4)
    d.arrow([(431, 118), (431, 140)], 'ok')
    d.text(0, 222, 'Name every file with the unit serial. Copy the files OFF the server before the power cycle.', 7.4, C['acc'], 'start', 'Sans-B')
    return d.d, 'Ten minutes is enough to save the evidence that would otherwise be lost: kernel messages, the journal, BMC events and sensors, the device list and the serials.'
