"""Diagrams for Set A (questions 1-20). Each returns (Drawing, caption)."""
from diag_lib import *

WD = 482


def q1():
    d = D(WD, 210)
    d.title(0, 10, 'What "Linux" means')
    layers = [('Hardware', 'CPU, memory, PCIe cards, drives, NICs', 'p'),
              ('Linux kernel', 'the core: talks to the hardware, loads drivers', 'acc'),
              ('Tools + shell', 'bash, lspci, dmesg, grep, ip, systemd...', 'n'),
              ('Distribution', 'kernel + tools packaged: RHEL, Rocky, Ubuntu Server, SUSE', 'ok')]
    for i, (t, s, k) in enumerate(reversed(layers)):
        d.box(0, 22 + i * 44, 250, 38, t, s, k)
    d.text(125, 205, 'Strictly, "Linux" = the kernel. A distro = kernel + tools.', 7.5, MUTED, 'middle', 'Sans')
    d.title(275, 10, 'Why data centers run it: S-L-R-T')
    why = [('S', 'Stable', 'runs for months without a reboot', 'ok'), ('L', 'Low cost', 'free; RHEL charges for support', 'acc'),
           ('R', 'Remote', 'command line + scripts over the network:\none tech, hundreds of servers', 'oob'),
           ('T', 'Transparent', 'lspci and dmesg show exactly what\nthe hardware is doing', 'cu')]
    for i, (L, t, s, k) in enumerate(why):
        y = 22 + i * 44
        d.rect(275, y, 207, 38, k, r=5)
        d.circle(294, y + 19, 12, kind=k, fill=C[k], stroke=C[k])
        d.text(294, y + 23.5, L, 12, WHITE, 'middle', 'Sans-B')
        d.text(314, y + 15, t, 9, KIND[k][2], 'start', 'Sans-B')
        for j, row in enumerate(s.split('\n')): d.text(314, y + 26 + j * 8.5, row, 6.9, MUTED)
    d.text(378, 205, 'Bonus: secure, efficient, AI and cloud software built for Linux first', 7.2, MUTED, 'middle')
    return d.d, 'The Linux stack (left) and the four reasons to memorize (right). Mnemonic: "Servers Love Running Tux" = Stable, Low cost, Remote, Transparent.'


def q2():
    d = D(WD, 200)
    d.title(0, 10, 'What ip a tells you about ens1f0 (and what it does not)')
    d.server(0, 40, 150, 40, 'srv-r07-u12', leds=('ok',))
    d.rect(150, 46, 64, 28, 'acc', r=4)
    d.text(182, 58, 'ens1f0', 8, KIND['acc'][2], 'middle', 'Sans-B')
    d.text(182, 68, 'slot 1, port 0', 6.4, MUTED, 'middle')
    d.line(214, 60, 290, 60, 'ok', sw=2.4)
    d.text(252, 54, 'LOWER_UP', 7, C['ok'], 'middle', 'Sans-B')
    d.text(252, 72, 'mtu 9000 (jumbo)', 6.6, MUTED, 'middle')
    d.switch(290, 47, 110, 26, 'switch port (MTU must match)', ports=10, hi=2, hik='ok')
    d.box(420, 30, 62, 38, 'Gateway', ['not in ip a', 'ip route'], 'warn', fs=8, sfs=6.4)
    d.box(420, 76, 62, 38, 'DNS', ['not in ip a', 'resolv.conf'], 'warn', fs=8, sfs=6.4)
    d.line(400, 60, 420, 50, 'ghost', dash=[2, 2]); d.line(400, 60, 420, 95, 'ghost', dash=[2, 2])
    rows = [('UP / LOWER_UP', 'enabled / physical link present', 'ok'), ('mtu 9000', 'jumbo frames; switch must match', 'acc'),
            ('link/ether 3c:ec:ef:12:34:56', 'MAC address', 'acc'), ('inet 10.20.5.14/22', 'IPv4 + mask 255.255.252.0', 'acc'),
            ('brd 10.20.7.255', 'broadcast: subnet 10.20.4.0 - 10.20.7.255', 'acc'), ('dynamic', 'came from DHCP (static = "forever")', 'acc')]
    for i, (a, b, k) in enumerate(rows):
        x = 0 if i < 3 else 245; y = 128 + (i % 3) * 22
        w = d.pill(x, y, a, k, fs=6.9)
        d.text(x + w + 6, y + 9.5, b, 7.2, INK)
    d.text(0, 196, 'Also not in ip a: link speed  ->  ethtool ens1f0', 7.4, C['warn'], 'start', 'Sans-B')
    return d.d, 'Read ip a left to right: name, flags, MTU, MAC, IP/mask, broadcast, dynamic. Gateway, DNS and speed live elsewhere.'


def q3():
    d = D(WD, 230)
    d.laptop(0, 70, 62, 'Your laptop')
    d.rect(150, 18, 330, 196, 'p', r=8)
    d.text(160, 32, 'SERVER', 8, MUTED, 'start', 'Sans-B')
    # OS side
    d.rect(250, 40, 220, 72, 'acc', r=6)
    d.text(260, 54, 'Operating system (Linux)', 8.5, KIND['acc'][2], 'start', 'Sans-B')
    d.box(262, 62, 92, 40, 'sshd', 'service on TCP 22', 'n', fs=8.5)
    d.box(362, 62, 98, 40, 'Kernel + network', 'needs OS booted', 'n', fs=8.5)
    d.box(165, 62, 70, 40, 'NIC', 'data network', 'acc', fs=8.5)
    # BMC side
    d.box(165, 134, 70, 50, 'BMC', ['own CPU + port', 'standby power'], 'oob', fs=9)
    d.box(262, 134, 198, 50, 'Serial console', ['BIOS/POST, GRUB, kernel boot', 'messages, kernel panics'], 'oob', fs=8.5)
    d.arrow([(64, 78), (165, 78)], 'acc', 'SSH (in-band)', ldy=-5)
    d.arrow([(235, 82), (262, 82)], 'acc')
    d.arrow([(64, 100), (110, 100), (110, 159), (165, 159)], 'oob', 'SOL (out-of-band)\nmanagement network', lpos=0.5, ldy=-12, lanchor='middle')
    d.arrow([(235, 159), (262, 159)], 'oob')
    d.cross(248, 82, 6)
    d.text(470, 32, 'OS crashed? SSH is gone...', 7.2, C['bad'], 'end', 'Sans-B')
    d.text(262, 200, '...but SOL still shows the console through the BMC.', 7.2, C['oob'], 'start', 'Sans-B')
    return d.d, 'SSH reaches the operating system over the data network. SOL reaches the console through the BMC. Different roads, so SOL is not "slower SSH".'


def q4():
    d = D(WD, 230)
    xs = {'srv': 60, 'sw': 240, 'dhcp': 420}
    d.box(10, 6, 100, 36, 'New server', 'no IP yet (0.0.0.0)', 'acc')
    d.box(190, 6, 100, 36, 'Switch / VLAN', 'broadcast domain', 'p')
    d.box(370, 6, 100, 36, 'DHCP server', '10.20.5.2', 'ok')
    for x in xs.values(): d.line(x, 42, x, 222, 'ghost', dash=[3, 3])
    msgs = [('1  DISCOVER', 'broadcast to 255.255.255.255: "I need an address"', 'srv', 'dhcp', 'acc'),
            ('2  OFFER', 'server offers 10.20.5.14 + settings', 'dhcp', 'srv', 'ok'),
            ('3  REQUEST', 'broadcast: "I will take 10.20.5.14"', 'srv', 'dhcp', 'acc'),
            ('4  ACK', 'confirmed: lease starts, client configures itself', 'dhcp', 'srv', 'ok')]
    for i, (t, s, a, b, k) in enumerate(msgs):
        y = 66 + i * 40
        d.arrow([(xs[a], y), (xs[b], y)], k, sw=1.6)
        d.text(240, y - 6, t, 8.5, C[k], 'middle', 'Sans-B')
        d.text(240, y + 11, s, 6.8, MUTED, 'middle')
    return d.d, 'DORA: Discover and Request are broadcasts from the client; Offer and Ack come from the DHCP server. Result: IP, mask, gateway, DNS, lease time.'


def q5():
    d = D(WD, 210)
    d.title(0, 10, 'A Gen 4 x8 link: 8 lanes, each sending and receiving at once')
    d.cpu(0, 26, 74, 70, 'CPU', sub='root port')
    d.card(330, 36, 130, 50, 8, 'NIC / NVMe / GPU', bracket=False)
    for i in range(8):
        y = 30 + i * 8.6
        d.line(80, y, 322, y, 'acc', sw=1.1)
        d.head(300, y, 322, y, C['acc'], 3.8); d.head(102, y, 80, y, C['ok'], 3.8)
    d.text(200, 108, '8 lanes  x  16 GT/s (Gen 4)', 8.5, INK, 'middle', 'Sans-B')
    d.rect(0, 122, 482, 46, 'acc', r=6)
    d.text(14, 140, '16 GT/s x 8 lanes = 128 Gb/s     128 / 8 bits = 16 GB/s     minus ~1.5% encoding = ~15.75 GB/s', 8.6, KIND['acc'][2], 'start', 'Sans-B')
    d.text(14, 157, 'Answer: about 16 GB/s in EACH direction (about 32 GB/s both ways together)', 8.6, C['ok'], 'start', 'Sans-B')
    d.title(0, 186, 'Slot sizes (physical)')
    x = 120
    for ln in (1, 4, 8, 16):
        x += d.slot(x, 176, ln, sc=4.2) + 14
    return d.d, 'Quick math: GT/s x lanes / 8 = GB/s per direction. Generation sets speed per lane, width sets the number of lanes.'


def q6():
    d = D(WD, 225)
    d.title(0, 10, 'An ECC RDIMM has a 9th chip for check bits')
    d.dimm(0, 22, 230, 50, chips=9, ecc=True, label='8 data chips + 1 ECC chip (blue)')
    d.title(262, 10, 'What ECC can and cannot do')
    def bits(x, y, flips, kind, title, sub):
        d.text(x, y - 6, title, 8.3, C[kind], 'start', 'Sans-B')
        for i in range(8):
            fl = i in flips
            d.rect(x + i * 15, y, 13, 15, 'bad' if fl else 'p', r=2, sw=0.8)
            d.text(x + i * 15 + 6.5, y + 11, '1' if (i % 3 == 0) != fl else '0', 8, C['bad'] if fl else INK, 'middle', 'Mono-B')
        d.text(x + 128, y + 11, sub, 7.4, C[kind], 'start', 'Sans-B')
    bits(262, 34, [3], 'ok', '1 bit flipped: correctable', 'fixed, logged')
    bits(262, 80, [2, 5], 'bad', '2 bits flipped: uncorrectable', 'detected, crash')
    d.title(0, 120, 'Corrected errors per day on DIMM C1: the early warning')
    vals = [0, 0, 1, 0, 2, 3, 5, 8, 12, 19, 27]
    for i, v in enumerate(vals):
        h = v * 2.3
        k = 'warn' if v < 12 else 'bad'
        d.rect(10 + i * 26, 205 - h, 18, max(h, 0.8), k, r=1, sw=0.6, fill=C[k])
        if v: d.text(19 + i * 26, 201 - h, str(v), 6.5, MUTED, 'middle')
    d.line(6, 205, 300, 205, 'n', sw=0.8)
    d.text(150, 218, 'days', 7, MUTED, 'middle')
    d.box(320, 140, 162, 60, 'Replace it in a planned window', ['before it becomes an', 'uncorrectable error and an outage'], 'ok', fs=8.4, sfs=7)
    d.arrow([(300, 170), (320, 170)], 'ok')
    return d.d, 'ECC: one bit fixed, two bits flagged. A rising count of corrected errors means the DIMM is wearing out.'
