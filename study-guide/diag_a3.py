"""Set A diagrams, questions 13 to 20."""
from diag_lib import *

WD = 482


def col_box(d, x, y, w, h, kind, title, rows, fs=7.1):
    d.rect(x, y, w, h, kind, r=5)
    d.text(x + 9, y + 15, title, 8.6, KIND[kind][2], 'start', 'Sans-B')
    for i, r in enumerate(rows): d.text(x + 9, y + 29 + i * 11.5, r, fs, INK)


def follows_part():
    d = D(WD, 222)
    d.server(0, 18, 160, 30, 'Server A (original, failing)', leds=('bad',))
    d.gpu(24, 84, 112, 36, 'GPU X (suspect)')
    d.server(322, 18, 160, 30, 'Server B (known-good before)', leds=('bad',))
    d.gpu(346, 84, 112, 36, 'GPU X now in B')
    d.arrow([(140, 102), (340, 102)], 'acc', 'move GPU X', sw=1.8)
    d.text(240, 124, 'Server B now fails the same way', 7.8, C['bad'], 'middle', 'Sans-B')
    col_box(d, 0, 138, 154, 82, 'ok', 'Proves', ['GPU X is very likely bad:', 'the fault moved with it.'])
    col_box(d, 164, 138, 154, 82, 'warn', 'Does NOT prove', ['that Server A is healthy.', 'Its slot or power may have', 'damaged the GPU first.'])
    col_box(d, 328, 138, 154, 82, 'acc', 'Next', ['1 tag + quarantine GPU X', '2 restore + retest Server B', '3 test A with a good GPU', '4 document serials, RMA'])
    return d.d, 'When the failure follows the part into a good system, the part is bad. The original system still has to be checked before it gets another good part.'


def vlan_dhcp():
    d = D(WD, 214)
    d.box(0, 64, 104, 48, 'Server', ['ens2f1: UP, LOWER_UP', '169.254.88.4/16'], 'warn', fs=8.5, sfs=6.6)
    d.rect(124, 16, 198, 140, 'warn', r=8, dash=[4, 3], fill=H('#fffaf0'))
    d.text(134, 30, 'VLAN 30  (port set to the wrong VLAN)', 7.4, KIND['warn'][2], 'start', 'Sans-B')
    d.switch(150, 74, 140, 26, 'switch port 3', ports=12, hi=2, hik='warn')
    d.rect(334, 16, 148, 140, 'ok', r=8, dash=[4, 3], fill=H('#f6fbf8'))
    d.text(344, 30, 'VLAN 20  (servers)', 7.4, KIND['ok'][2], 'start', 'Sans-B')
    d.box(360, 66, 104, 42, 'DHCP server', '10.20.5.2', 'ok')
    d.line(104, 88, 150, 88, 'ok', sw=2.4)
    d.text(127, 82, 'link OK', 6.6, C['ok'], 'middle', 'Sans-B')
    d.arrow([(290, 88), (330, 88)], 'acc', 'DISCOVER', ldy=-6, lfs=6.8)
    d.cross(326, 88, 5.5)
    d.text(228, 124, 'the broadcast never reaches', 6.8, C['bad'], 'middle', 'Sans-B'); d.text(228, 133, 'the DHCP server: no OFFER', 6.8, C['bad'], 'middle', 'Sans-B')
    steps = [('DISCOVER...', 'acc'), ('DISCOVER...', 'acc'), ('no OFFER', 'bad'), ('gives itself 169.254.88.4', 'warn'), ('reaches nothing', 'bad')]
    x = 0
    for i, (t, k) in enumerate(steps):
        w = d.pill(x, 176, t, k, fs=7)
        if i < len(steps) - 1: d.arrow([(x + w + 2, 182.5), (x + w + 12, 182.5)], 'n', sw=0.9)
        x += w + 14
    d.text(0, 208, 'Also check: DHCP server up, relay on the router, cable in the right port, MTU 9000 matches the switch.', 7, MUTED)
    return d.d, '169.254.x.x means "I asked DHCP and nobody answered". The link is up, so look at what stands between the server and the DHCP server.'


def mem_upgrade():
    d = D(WD, 252)
    d.cpu(196, 48, 90, 118, 'CPU 1', sub='8 memory channels')
    chans = 'ABCDEFGH'
    for i, ch in enumerate(chans):
        left = i < 4
        row = i % 4
        y = 40 + row * 34
        xs = (22, 104) if left else (300, 382)
        d.text(8 if left else 474, y + 11, ch, 9, INK, 'start' if left else 'end', 'Sans-B')
        for j, x in enumerate(xs):
            name = f'{ch}{j + 1}'
            missing = name == 'H2'
            err = name in ('C2', 'F2')
            if missing:
                d.rect(x, y, 76, 18, 'bad', r=2, dash=[3, 2], fill=WHITE)
                d.text(x + 38, y + 12, 'H2: no module', 6.5, C['bad'], 'middle', 'Sans-B')
            else:
                d.rect(x, y, 76, 18, 'n', r=2, sw=0.6, fill=H('#2f7d4f') if j == 0 else C['acc'], stroke=C['bad'] if err else H('#1f5a37'))
                d.text(x + 38, y + 12, name + ('  old' if j == 0 else '  new'), 6.6, WHITE, 'middle', 'Sans-B')
            if err:
                d.rect(x - 2, y - 2, 80, 22, 'bad', r=3, sw=2, fill='none')
                d.text(x + 38, y - 4, 'corrected errors', 6.4, C['bad'], 'middle', 'Sans-B')
    d.rect(0, 186, 482, 64, 'p', r=6)
    rows = [('New DIMMs', 'errors follow them when moved to another channel', 'acc'), ('Slots / board', 'errors stay in the slot with a known-good DIMM', 'cu'),
            ('CPU', 'errors on many channels of one CPU: reseat, check pins', 'oob'), ('Install / config', 'wrong slots, mixed parts, not latched, BIOS, mirroring', 'warn')]
    for i, (a, b, k) in enumerate(rows):
        x = 8 + (i % 2) * 238; y = 194 + (i // 2) * 28
        w = d.pill(x, y, a, k, fs=7)
        d.text(x + w + 5, y + 9.5, b, 6.5, INK)
    return d.d, 'Map the errors to slots and channels first. Two channels with new DIMMs and errors, plus a missing module, point you at the new parts and how they were installed.'


def same_slot():
    d = D(WD, 222)
    d.gpu(0, 30, 112, 34, 'GPU #1 (serial ...4417)')
    d.cross(124, 47, 6); d.text(0, 82, 'failed the stress test', 7, C['bad'], 'start', 'Sans-B')
    d.gpu(0, 112, 112, 34, 'GPU #2 (new, serial ...9902)')
    d.cross(124, 129, 6); d.text(0, 164, 'same test, same failure', 7, C['bad'], 'start', 'Sans-B')
    d.arrow([(134, 47), (176, 92)], 'bad'); d.arrow([(134, 129), (176, 104)], 'bad')
    d.box(176, 78, 104, 42, 'Slot 3 path', 'the common factor', 'bad', fs=9)
    parts = [('Riser + PCIe cable', 'acc'), ('Aux power cable + PSU', 'warn'), ('Retimer on that path', 'oob'),
             ('Cooling: airflow, baffle', 'cu'), ('BIOS / firmware / driver', 'ok'), ('The test or its settings', 'p')]
    for i, (t, k) in enumerate(parts):
        y = 8 + i * 30
        d.box(326, y, 156, 24, t, None, k, fs=7.6)
        d.arrow([(280, 99), (326, y + 12)], 'n', sw=0.8)
    d.rect(0, 190, 482, 30, 'warn', r=5)
    d.text(241, 209, 'New part, same failure, same slot = the GPU was not the cause. Stop swapping parts: collect data first.', 7.6, KIND['warn'][2], 'middle', 'Sans-B')
    return d.d, 'Two different GPUs failing the same way in the same slot point away from the GPU and towards everything that slot shares.'


def journal_funnel():
    d = D(WD, 214)
    d.title(0, 10, '(a) and (c): narrow it down')
    rows = [('journalctl', 'everything, all boots', '412,315 lines', 250, 'p'), ('-b', 'this boot only', '96,402', 210, 'acc'),
            ('-p err', 'errors and worse', '1,284', 170, 'warn'), ('| sort | uniq -c | sort -rn', 'count repeats, biggest first', 'top: 912 x', 130, 'bad')]
    cx = 128
    for i, (cmd, what, n, w, k) in enumerate(rows):
        y = 20 + i * 44
        w2 = rows[i + 1][3] if i + 1 < len(rows) else w - 30
        d.poly([(cx - w / 2, y), (cx + w / 2, y), (cx + w2 / 2, y + 40), (cx - w2 / 2, y + 40)], k, sw=1)
        d.text(cx, y + 15, cmd, 8.4 if i < 3 else 6.6, KIND[k][2], 'middle', 'Mono-B')
        d.text(cx, y + 27, what, 6.8, MUTED, 'middle')
        d.text(cx, y + 37, n, 7, INK, 'middle', 'Sans-B')
    d.title(290, 10, '(b): a time window')
    d.line(290, 80, 482, 80, 'n', sw=1.2)
    for i, t in enumerate(['08:00', '08:30', '09:00', '09:30', '10:00']):
        x = 290 + i * 48
        d.line(x, 76, x, 84, 'n'); d.text(x, 96, t, 6.8, MUTED, 'middle')
    d.rect(386, 58, 24, 22, 'acc', r=2, fill=C['acc'])
    d.text(398, 52, '09:00 to 09:15', 7, C['acc'], 'middle', 'Sans-B')
    d.lines(290, 118, ['journalctl --since "09:00" \\', '           --until "09:15"'], 7.6, INK, font='Mono-B', lead=11)
    d.lines(290, 146, ['Times without a date mean today.', 'Result: 3,140 lines from those', '15 minutes only.'], 7, MUTED)
    return d.d, 'Each option throws away lines you do not need: this boot, then errors only, then count the repeats. A time window lines the logs up with when the problem happened.'


def nic_ladder():
    d = D(WD, 228)
    steps = [('1  Found it?', 'lspci | grep -i ethernet', '3b:00.0 Ethernet controller', 'acc'),
             ('2  Driver?', 'lspci -k -s 3b:00.0', 'driver in use: mlx5_core', 'oob'),
             ('3  Link?', 'ip link  /  ethtool ens3f0', 'LOWER_UP, Link: yes', 'ok'),
             ('4  Address?', 'ip a show ens3f0', 'inet 10.20.5.31/24 dynamic', 'cu')]
    for i, (t, c, s, k) in enumerate(steps):
        x = i * 121; y = 150 - i * 44
        d.rect(x, y, 117, 74, k, r=5)
        d.text(x + 8, y + 15, t, 9, KIND[k][2], 'start', 'Sans-B')
        d.text(x + 8, y + 30, c, 6.2, INK, 'start', 'Mono-B')
        d.text(x + 8, y + 44, 'good sign:', 6.3, MUTED)
        d.text(x + 8, y + 55, s, 6.1, C['ok'], 'start', 'Mono')
        if i < 3: d.arrow([(x + 60, y - 2), (x + 121 + 30, y - 18)], 'n', sw=1)
    d.card(10, 30, 120, 40, 16, 'new 100G NIC')
    d.rect(118, 44, 12, 12, 'n', r=1, fill=H('#9aa3ad'))
    d.text(250, 220, 'Then: ip route and ping the gateway to prove it can talk.', 7.4, MUTED, 'middle', 'Sans-B')
    return d.d, 'Climb one step at a time: the bus sees it, a driver owns it, the cable gives a link, and the network gives an address.'


def first_commands():
    d = D(WD, 206)
    cols = [('1  Where am I?', ['hostname', 'cat /etc/os-release', 'uptime'], 'p'),
            ('2  What hardware?', ['lscpu', 'free -h', 'lsblk', 'lspci'], 'acc'),
            ('3  Errors now?', ['dmesg -T -l err,warn', 'journalctl -p err -b', 'journalctl --list-boots'], 'bad'),
            ('4  BMC view', ['ipmitool sel elist', 'ipmitool sensor'], 'oob'),
            ('5  Network', ['ip a', 'ip route'], 'ok')]
    for i, (t, cmds, k) in enumerate(cols):
        x = i * 97
        d.rect(x, 8, 92, 150, k, r=5)
        d.text(x + 7, 24, t, 8.2, KIND[k][2], 'start', 'Sans-B')
        for j, c in enumerate(cmds): d.text(x + 6, 44 + j * 16, c, 5.9, INK, 'start', 'Mono-B')
        if i < 4: d.arrow([(x + 92, 84), (x + 97, 84)], 'n', sw=1)
    d.rect(0, 168, 482, 34, 'p', r=5)
    d.text(10, 181, 'Then save it:', 7.2, INK, 'start', 'Sans-B')
    d.text(70, 181, 'dmesg -T > unit123_dmesg.txt     journalctl -b > unit123_journal.txt', 6.6, INK, 'start', 'Mono')
    d.text(70, 194, 'ipmitool sel elist > unit123_sel.txt     (look first, change nothing yet)', 6.6, INK, 'start', 'Mono')
    return d.d, 'A sensible order: who and what the server is, what hardware it has, what is going wrong now, what the BMC recorded, and how it is connected.'


def slow_server():
    d = D(WD, 230)
    d.rect(0, 6, 482, 40, 'p', r=5)
    d.text(10, 22, 'Who is using it?', 8.4, INK, 'start', 'Sans-B')
    d.text(10, 36, 'top          ps aux --sort=-%cpu | head          ps aux --sort=-%mem | head', 7.4, INK, 'start', 'Mono-B')
    cols = [('CPU', 'acc', ['uptime   (load average)', 'nproc    (number of cores)', 'top      (%us  %sy)'], ['load average above the', 'number of cores, %us high,', '%wa low'], 0.86),
            ('Memory', 'oob', ['free -h  (available)', 'vmstat 1 (si  so)', 'top      (MiB Swap used)'], ['"available" near zero,', 'swap in / out (si, so)', 'busy every second'], 0.55),
            ('Storage', 'cu', ['top      (%wa = iowait)', 'iostat -x 1', '         (%util, await)'], ['%wa high, a disk at', '~100 %util, await of', 'many milliseconds'], 0.3)]
    for i, (t, k, cmds, rule, lvl) in enumerate(cols):
        x = i * 163
        d.rect(x, 56, 156, 170, k, r=6)
        d.text(x + 10, 74, t, 10, KIND[k][2], 'start', 'Sans-B')
        d.rect(x + 74, 64, 72, 12, 'n', r=6, fill=WHITE)
        d.rect(x + 74, 64, 72 * lvl, 12, k, r=6, fill=C[k])
        for j, c in enumerate(cmds): d.text(x + 10, 94 + j * 12, c, 6.5, INK, 'start', 'Mono')
        d.text(x + 10, 146, 'It is the bottleneck when:', 7, INK, 'start', 'Sans-B')
        for j, r in enumerate(rule): d.text(x + 10, 160 + j * 11, r, 7, KIND[k][2])
    return d.d, 'Find the busy processes, then decide which resource is full. Compare load with the number of cores, check available memory and swap, and check iowait and disk %util.'
