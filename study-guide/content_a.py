# Set A: questions 1-20. Markup: "1. " numbered, "- " bullet, `code`, "$ " command line in outputs, {{x}} highlight.
E = {}

E[1] = dict(part='Foundations', topic='What servers do', reread='Module 1: What servers do; What makes a server different',
q='Describe three different jobs servers do inside a company. Then explain how those jobs shape the way a server is built and managed compared with an office desktop.',
hook='Servers = <b>24/7, nobody watching</b>. So they get <b>R-E-H-R</b>: Redundancy, ECC, Hot-swap, Remote management.',
ans="""Three jobs servers do:
1. Web and application server: runs the company website and business apps that many people use at once.
2. Database or file server: stores the company's data (orders, accounts, shared files, backups) and must never lose it.
3. AI / compute server: runs heavy work like training AI models on GPUs, all day.
(Others: DNS and DHCP servers that keep the network working.)
How the jobs shape the server:
- It runs 24/7 with nobody in front of it, so it has redundancy: two power supplies and many fans. One can fail and it keeps running.
- It holds important data, so it uses ECC memory to stop silent data errors.
- It must not stop for repairs, so drives, fans and PSUs are hot-swap.
- It is managed remotely, not with a screen: a BMC, SSH and scripts. One tech can manage hundreds.
- It lives in a rack (measured in U, 1U = 1.75 in), with no keyboard or monitor.
A desktop is used by one person in office hours. If it fails, one person waits. If a server fails, the whole company can stop.""",
exp="""Think of a desktop as a personal car and a server as a city bus: the bus runs all day, carries many people, and has to keep going even when one part has a problem.
The <b>job</b> decides the <b>design</b>. A database server cannot lose data, so it gets ECC memory and redundant drives. A web server must stay up, so it gets two power supplies. An AI server needs huge bandwidth, so it gets GPUs on wide PCIe links. Because nobody sits at a server, everything is done remotely through the BMC and the command line.""",
fig=('diag_a2', 'servers_roles'),
outs=[dict(t='How long has it been running? (24/7)', lines="""$ uptime
 09:14:02 up {{182 days}},  4:11,  1 user,  load average: 3.12, 3.40, 3.38""", notes=['<b>up 182 days</b>: the server has run for six months without a reboot.']),
      dict(t='Redundant power, read from the BMC', lines="""$ sudo ipmitool sdr type "Power Supply"
PSU1 Status      | 51h | ok  | 10.1 | Presence detected
PSU2 Status      | 52h | ok  | 10.2 | Presence detected
PS Redundancy    | 77h | ok  |  7.1 | {{Fully Redundant}}""", notes=['Two PSUs, and <b>Fully Redundant</b>: if one fails, the other carries the whole load.'])])

E[2] = dict(part='Foundations', topic='What PCIe is for', reread='Module 4: What PCIe is for; Lanes, generations, and bandwidth',
q='What does PCIe connect inside a server, why is each link built from lanes, and how do a GPU, a network card, and an NVMe drive each depend on it?',
hook='PCIe = the <b>CPU\'s highways</b> to the cards. <b>Lanes = traffic lanes</b>: more lanes, more data at once.',
ans="""What it connects: PCIe is the high-speed connection between the CPU and the fast devices: GPUs, network cards (NICs), NVMe drives, and RAID or other add-in cards. Each device gets its own link back to the CPU (directly, or through a PCIe switch).
Why lanes: a link is built from lanes (x1, x4, x8, x16). Each lane is two pairs of wires: one pair sends and one pair receives, at the same time. More lanes carry more data in parallel, like more lanes on a highway. This lets the link be sized to the device.
How each device depends on it:
- GPU (usually x16): every piece of AI data goes into and out of GPU memory over PCIe. A slow or broken link means slow training or a GPU that is missing.
- Network card (x8 or x16): every network packet crosses PCIe between the NIC and the CPU. A 100G or 400G port needs a wide, fast link or it cannot reach full speed.
- NVMe drive (x4): the drive talks to the CPU directly over PCIe, with no SATA controller in between. That is why it is fast, and why PCIe problems make drives drop out or slow down.""",
exp="""If the PCIe link to a device is missing, the device disappears from <code>lspci</code>. If the link is narrower or slower than it should be (downtrained), the device works but slowly.
Each new PCIe generation doubles the speed per lane (Gen 4 = 16 GT/s, Gen 5 = 32 GT/s). A GPU and a 100G NIC use 16 lanes each; one NVMe drive uses 4. That is why a big AI server needs a lot of lanes and often PCIe switches.""",
fig=('diag_a2', 'pcie_connects'),
outs=[dict(t='Find the three devices on the PCIe bus', lines="""$ lspci | grep -i -E "nvidia|ethernet|non-volatile"
19:00.0 3D controller: {{NVIDIA}} Corporation GH100 [H100 PCIe] (rev a1)
3b:00.0 {{Ethernet controller}}: Mellanox Technologies MT2892 Family [ConnectX-6 Dx]
5e:00.0 {{Non-Volatile memory controller}}: Samsung Electronics Co Ltd NVMe SSD Controller""", notes=['Each line is one device on PCIe. The first part (19:00.0) is its address: bus:device.function.']),
      dict(t='How many lanes each one got', lines="""$ sudo lspci -vv -s 19:00.0 | grep LnkSta:
        LnkSta: Speed 32GT/s, Width {{x16}}
$ sudo lspci -vv -s 3b:00.0 | grep LnkSta:
        LnkSta: Speed 16GT/s, Width {{x16}}
$ sudo lspci -vv -s 5e:00.0 | grep LnkSta:
        LnkSta: Speed 16GT/s, Width {{x4}}""", notes=['GPU: Gen 5 x16. NIC: Gen 4 x16. NVMe drive: Gen 4 x4. Speed = generation, Width = number of lanes.'])])

E[3] = dict(part='Foundations', topic='Retimers versus redrivers', reread='Module 4: Retimers',
q='What is a PCIe retimer, how is it different from a redriver, why are retimers so common in Gen 5 servers, and how might a failed retimer show up during testing?',
hook='<b>Redriver = megaphone</b> (louder, noise too). <b>Retimer = translator</b>: listens, then says it again clearly.',
ans="""Retimer: a chip in the PCIe path that fully recovers the data and sends out a new, clean signal. This resets the "loss budget", so the signal can travel much farther. It takes part in link training, and the OS normally cannot see it (it is not in lspci). It sits on risers, backplanes, motherboards and GPU baseboards.
Redriver: a simple amplifier. It makes the signal stronger, but it also makes the noise stronger, and it does not take part in link training.
Why common in Gen 5: Gen 5 runs at 32 GT/s. Faster signals lose strength much faster over board traces, connectors, risers and cables. Long paths (to front drive bays, risers, GPU trays) cannot work at Gen 5 without a retimer, and a redriver is not good enough at that speed.
How a failed retimer shows up:
- Every device behind it disappears (a whole branch missing in lspci -tv).
- Links come up downtrained: LnkSta lower than LnkCap.
- A steady stream of corrected PCIe (AER) errors in dmesg.
- Devices that drop out under load or heat.
Because it is invisible to the OS, check the BMC (some report retimer health) and the retimer firmware version.""",
exp="""Imagine passing a message down a long line of people. A redriver shouts the message louder, including the mistakes. A retimer listens, writes the message down correctly, then reads it out fresh, so the next part of the trip starts clean.
At Gen 3 the signal could cross a server without help. At Gen 5 the same distance loses too much signal, so retimers are everywhere. When one fails, think "everything behind it": a whole group of devices goes missing or slow together.""",
fig=('diag_a2', 'retimer_signal'),
outs=[dict(t='A weak signal: a stream of corrected PCIe errors', lines="""$ dmesg -T | grep -i -A3 "aer" | tail -4
[Fri Oct  2 10:41:07 2026] pcieport 0000:17:01.0: {{AER: Corrected error}} message received from 0000:19:00.0
[Fri Oct  2 10:41:07 2026] nvidia 0000:19:00.0: PCIe Bus Error: severity=Corrected, type={{Physical Layer}}
[Fri Oct  2 10:41:07 2026] nvidia 0000:19:00.0:   device [10de:2331] error status/mask=00000001/0000e000
[Fri Oct  2 10:41:07 2026] nvidia 0000:19:00.0:    [ 0] {{RxErr}}
$ dmesg | grep -c "AER: Corrected"
{{4127}}""", notes=['<b>Physical Layer / RxErr</b> = the receiver could not read the signal cleanly. Thousands of them = a signal problem on the path (seating, riser, cable, retimer).']),
      dict(t='The link also trained lower', lines="""$ sudo lspci -vv -s 19:00.0 | grep -E "LnkCap|LnkSta"
        LnkCap: Port #0, Speed 32GT/s, Width x16, ASPM not supported
        LnkSta: Speed {{16GT/s (downgraded)}}, Width {{x8 (downgraded)}}""", notes=['The GPU can do Gen 5 x16 but only got Gen 4 x8. Together with the AER errors, suspect the path, including the retimer.'])])

E[4] = dict(part='Foundations', topic='DHCP messages and settings', reread='Module 7: DHCP',
q='A brand-new server is racked and plugged in. Describe every DHCP message exchanged before it has an address, who sends each one, which are broadcasts, what settings the server ends up with, and what you would see if no DHCP server answered.',
hook='<b>DORA</b>: Discover, Offer, Request, Acknowledge. Settings: <b>"I Must Get DNS Later"</b> = IP, Mask, Gateway, DNS, Lease.',
ans="""DHCP uses four messages (DORA):
1. Discover: the new server sends "I need an address." It has no IP yet, so it is a broadcast (from 0.0.0.0 to 255.255.255.255).
2. Offer: a DHCP server answers with an offer: an IP address and settings.
3. Request: the server broadcasts "I want that offer." Broadcast, so other DHCP servers know their offers were not taken.
4. Acknowledge (ACK): the DHCP server confirms. The server sets itself up with the address.
Who sends: Discover and Request come from the client (the new server) and are broadcasts. Offer and ACK come from the DHCP server (broadcast or unicast, depending on the setup).
Broadcasts do not cross routers, so a DHCP server on another subnet needs a DHCP relay.
Settings the server ends up with: IP address, subnet mask, default gateway, DNS servers, and a lease time. The lease is renewed partway through.
If no DHCP server answers: the server keeps sending Discover, then gives up. It has no IPv4 address, or a self-assigned 169.254.x.x address. In ip a there is no normal inet line (or a 169.254 one), there is no default route, and it cannot reach anything beyond its own link.""",
exp="""DHCP is like a hotel front desk. You walk in and shout "I need a room!" (Discover). The desk offers room 14 (Offer). You say "I'll take room 14" (Request). The desk gives you the key and the rules: Wi-Fi password, checkout time (ACK = IP, gateway, DNS, lease).
A <b>reservation</b> means the desk always gives the same room to the same guest (by MAC address). A <b>static</b> address means you never ask the desk at all.""",
fig=('diag_a', 'q4'),
outs=[dict(t='A normal DHCP exchange (dhclient -v shows all four steps)', lines="""$ sudo dhclient -v ens1f0
Listening on LPF/ens1f0/3c:ec:ef:12:34:56
{{DHCPDISCOVER}} on ens1f0 to 255.255.255.255 port 67 interval 3
{{DHCPOFFER}} of 10.20.5.14 from 10.20.5.2
{{DHCPREQUEST}} for 10.20.5.14 on ens1f0 to 255.255.255.255 port 67
{{DHCPACK}} of 10.20.5.14 from 10.20.5.2
bound to 10.20.5.14 -- renewal in 41413 seconds.""", notes=['Discover and Request go to 255.255.255.255 (broadcast). The offer comes from the DHCP server, 10.20.5.2.', '<b>renewal in 41413 seconds</b>: about halfway through the lease, it will renew.']),
      dict(t='When nobody answers', lines="""$ sudo dhclient -v ens1f0
DHCPDISCOVER on ens1f0 to 255.255.255.255 port 67 interval 3
DHCPDISCOVER on ens1f0 to 255.255.255.255 port 67 interval 8
DHCPDISCOVER on ens1f0 to 255.255.255.255 port 67 interval 14
{{No DHCPOFFERS received.}}
$ ip route
{{(nothing: no default gateway)}}""", notes=['Only Discovers, never an Offer. Check the VLAN, the DHCP server and the relay.'])])

E[5] = dict(part='Foundations', topic='ESD risks', reread='Module 1: ESD',
q='Describe three different ways electrostatic discharge can harm a server part, including one that may not show up until weeks later, and the precautions that prevent them.',
hook='ESD does <b>3 things: Kill, Weaken, Glitch</b>. Prevent with <b>Strap, Mat, Bag, Edges</b>.',
ans="""ESD (electrostatic discharge) is a static zap. You often cannot feel it: you feel about 3,000 volts, but a chip can be damaged by less than 100 volts.
Three ways it harms a part:
1. Instant damage: the zap burns through part of a chip. The part is dead right away: not detected, will not power on, or fails its first test.
2. Latent damage (shows up weeks later): the zap only weakens the chip. It passes every test at the factory, then fails weeks later at the customer, after heat and use finish the damage.
3. Intermittent errors: the part works but now and then misbehaves: corrected memory errors, a PCIe or network link that drops, or random reboots. This is very hard to trace back.
Precautions:
- Wear a grounded wrist strap, connected to the chassis or an ESD mat.
- Work on a grounded ESD mat.
- Keep parts in anti-static bags until you install them.
- Hold parts by the edges; never touch pins, gold fingers or chips.
- Power off and unplug before handling parts, and use ESD-safe floors and shoes where provided.""",
exp="""Static builds up on you when you walk or move, and it jumps to the first metal it finds. A modern chip has tiny parts that a small zap can burn or weaken.
The scary one is <b>latent</b> damage: the unit passes test and ships, then fails weeks later. You saved nothing by skipping the wrist strap; you just moved the failure to the customer.""",
fig=('diag_a2', 'esd'),
outs=[dict(t='What latent damage can look like weeks later (one possible cause)', lines="""$ sudo ipmitool sel elist | tail -3
  41 | 11/06/2026 | 02:14:51 | Memory DIMM_B1 | {{Correctable ECC}} | Asserted
  44 | 11/09/2026 | 17:30:02 | Memory DIMM_B1 | {{Correctable ECC}} | Asserted
  4a | 11/12/2026 | 08:11:47 | Memory DIMM_B1 | Correctable ECC logging limit reached | Asserted""", notes=['This DIMM passed every test at build time in October. Errors start in November and grow. Handling damage is one possible cause, which is why the wrist strap matters every time.'])])

E[6] = dict(part='Foundations', topic='POST', reread='Module 9: POST',
q='A large server stays on a blank screen for several minutes after power on before anything appears. Explain what the firmware is doing during that time, and why skipping those checks would be risky.',
hook='POST = the server\'s <b>morning check-up</b>: <b>CPU, Memory, PCIe, ROMs, Boot</b>. Memory training is the long part.',
ans="""During the blank screen, the firmware (BIOS/UEFI) runs POST, the Power-On Self Test. It checks and sets up the hardware in order:
1. Power and BMC: the power supplies come up and the BMC hands over to the firmware.
2. CPU initialization: starts the CPUs and loads microcode.
3. Memory training and testing: tunes the timing of every memory channel for every DIMM, then tests the memory. On a server with hundreds of GB or several TB of memory, this takes minutes. It is the longest step.
4. PCIe enumeration: finds every card and trains every PCIe link (speed and width).
5. Option ROMs: starts the firmware on RAID cards, NICs and PXE.
6. Finds the boot device and hands over to the bootloader.
The screen stays blank because video starts late in this process. Be patient: several minutes is normal on a large server. Watch the POST code or the BMC to see progress.
Why skipping it is risky:
- Memory that is not trained and tested can give random errors, data corruption and crashes later in the OS.
- A bad DIMM, CPU or card would not be caught; the server would boot and fail later, maybe at the customer.
- PCIe links that are not trained properly leave cards missing or slow.""",
exp="""Memory training is like tuning a radio for every station: the firmware adjusts timing on each channel until the signal is clean. More DIMMs = more tuning = longer wait. A server with 2 TB of memory can take five minutes or more.
If a server stays blank much longer than normal, check the POST code and the BMC event log: that tells you where it stopped (memory, CPU or a PCIe card).""",
fig=('diag_a2', 'post_timeline'),
outs=[dict(t='Watching POST progress in the BMC event log', lines="""$ sudo ipmitool sel elist | tail -6
  1b | 10/02/2026 | 08:00:05 | System Firmware Progress | Primary CPU initialization | Asserted
  1c | 10/02/2026 | {{08:00:19}} | System Firmware Progress | {{Memory initialization}} | Asserted
  1d | 10/02/2026 | {{08:04:52}} | System Firmware Progress | PCI resource configuration | Asserted
  1e | 10/02/2026 | 08:05:20 | System Firmware Progress | Option ROM initialization | Asserted
  1f | 10/02/2026 | 08:05:31 | System Firmware Progress | {{Video initialization}} | Asserted
  20 | 10/02/2026 | 08:05:44 | System Firmware Progress | Starting operating system boot process | Asserted""", notes=['Memory took 08:00:19 to 08:04:52: about <b>4.5 minutes</b>.', 'Video starts at 08:05:31. Before that the screen is blank, which is normal.']),
      dict(t='Why it took so long', lines="""$ free -h | head -2
               total        used        free      shared  buff/cache   available
Mem:           {{2.0Ti}}        38Gi       1.9Ti       1.1Gi        12Gi       1.9Ti""", notes=['2 TB of memory to train and test.'])])

E[7] = dict(part='Foundations', topic='SSH versus Serial Over LAN', reread='Module 8: SSH versus Serial Over LAN',
q='A coworker says: “Serial Over LAN is just a slower version of SSH.” Explain why that is wrong. Describe how each one reaches the server, what each depends on, and give one situation where only SOL will help.',
hook='<b>SSH talks to the OS. SOL talks to the console through the BMC.</b> OS broken = SSH gone, SOL still works.',
ans="""It is wrong because SSH and SOL reach the server by completely different roads and show different things.
SSH (in-band):
- Runs inside the operating system, over the server's normal network, to the sshd service on TCP port 22.
- Needs: the OS booted, the network working, and sshd running.
- You get a login shell, only after the OS is up.
SOL, Serial Over LAN (out-of-band):
- Goes through the BMC over the management network, to the server's serial console.
- Needs only the BMC, which runs on standby power. It does not need the OS.
- You see the console: BIOS/POST (if console redirection is on), the GRUB menu, kernel boot messages, and kernel panics.
So SOL is not "slow SSH". It is a different door into the server.
Situation where only SOL helps: a server boots into emergency mode because of a bad line in /etc/fstab. The network never starts, so SSH fails. With SOL (ipmitool sol activate) I can watch the boot, log in at the emergency prompt and fix fstab.""",
exp="""SSH is like phoning someone at their desk: it only works if they are at work and the phone line is up. SOL is like the building's intercom from the security desk: it works even when the office is closed.
The virtual console (KVM) in the BMC web page is the graphical version of SOL. Use SSH for daily work on a healthy server; use SOL or KVM when the OS is broken, frozen, or has lost its network.""",
fig=('diag_a', 'q3'),
outs=[dict(t='SSH fails: the OS never brought up its network', lines="""$ ssh tech@10.20.5.14
ssh: connect to host 10.20.5.14 port 22: {{No route to host}}""", notes=['SSH needs the OS and its network. Neither is up.']),
      dict(t='SOL still works, through the BMC', lines="""$ ipmitool -I lanplus -H {{10.20.9.14}} -U admin -P ******** sol activate
[SOL Session operational.  Use ~? for help]
[ TIME ] Timed out waiting for device /dev/disk/by-uuid/9f1c2a7e...
[DEPEND] Dependency failed for /data.
{{You are in emergency mode.}} After logging in, type "journalctl -xb" to view
system logs, "systemctl reboot" to reboot, or "exit" to boot into default mode.
Give root password for maintenance""", notes=['10.20.9.14 is the <b>BMC</b> address on the management network, not the server\'s OS address.', 'SOL shows the boot itself, and the exact reason it stopped.'])])

E[8] = dict(part='Foundations', topic='BIOS and UEFI settings', reread='Module 9: Firmware; Module 4: PCIe errors and BIOS settings',
q='List four kinds of settings stored in a server’s BIOS or UEFI setup. For each one, describe a problem a wrong setting could cause.',
hook='BIOS settings: <b>Boot, PCIe, Memory, CPU/Power</b> (+ Console). <b>"Big PCs Make Commotion"</b>.',
ans="""1. Boot settings: boot order, UEFI or Legacy mode, Secure Boot, PXE (network boot).
Wrong setting: "No bootable device", booting from the network in a loop (PXE loop), or the OS will not load because the mode is wrong.
2. PCIe settings: slot enabled or disabled, bifurcation (splitting an x16 slot into x4 links), link speed, Above 4G Decoding, Resizable BAR.
Wrong setting: a card does not appear in lspci, a link runs at x4 instead of x16, an NVMe adapter shows only one drive, or a large GPU will not start.
3. Memory settings: memory speed, memory mode (mirroring or sparing), patrol scrub.
Wrong setting: the OS shows less memory than installed (mirroring hides half), or the server is unstable at a speed the DIMMs do not support.
4. CPU and power settings: virtualization (VT-x/VT-d), number of cores, Hyper-Threading, power profile.
Wrong setting: virtual machines will not start (virtualization off), or the server is slow because a power-saving profile limits the CPU.
Also: console redirection (serial) and BMC network settings. If console redirection is off, SOL shows nothing during POST.""",
exp="""The BIOS/UEFI setup is the server's "control panel" before the OS starts. It is stored in firmware, so it stays even when the OS is reinstalled. A wrong setting looks like a hardware fault: the card is fine, but the slot is switched off.
That is why a good technician checks BIOS settings before replacing parts, and records BIOS versions and settings when comparing with a golden unit.""",
fig=('diag_a2', 'bios_settings'),
outs=[dict(t='Checking a few BIOS effects from Linux', lines="""$ sudo dmidecode -s bios-version
{{2.4b}}
$ lscpu | grep -i virtualization
Virtualization:                  {{VT-x}}
$ mokutil --sb-state
{{SecureBoot enabled}}""", notes=['BIOS version: compare it with the approved version.', 'If VT-x were disabled in the BIOS, the Virtualization line would be missing and VMs would fail.', 'Secure Boot state comes from the UEFI setting.']),
      dict(t='A PCIe setting that hides devices: bifurcation', lines="""$ sudo nvme list | grep -c nvme
{{1}}""", notes=['A 4-drive NVMe adapter in a slot that is NOT bifurcated (x16 instead of x4x4x4x4) shows only one drive. The drives are fine; the setting is wrong.'])])

E[9] = dict(part='Foundations', topic='ECC memory', reread='Module 5: Memory and ECC',
q='A manager asks why servers use ECC memory when most desktops do not. Explain how ECC works, what it can and cannot fix, and why the log of corrected errors matters.',
hook='ECC: <b>1 bit = fix it, 2 bits = flag it (stop)</b>. A rising corrected count = <b>replace soon</b>.',
ans="""How ECC works: ECC (Error-Correcting Code) memory stores extra check bits with the data. When the data is read back, the memory controller uses the check bits to see if anything changed.
What it can fix: a single-bit error. One flipped bit is found and fixed on the spot. This is a correctable error: the server keeps running and logs it.
What it cannot fix: a double-bit error. It is detected but cannot be fixed. This is an uncorrectable error, and the server usually stops or crashes on purpose rather than use bad data. ECC also cannot save a DIMM that has completely failed.
Why servers need it (and desktops usually do not): servers run 24/7 with huge amounts of memory, so bit flips will happen. Without ECC, a flipped bit causes silent data corruption or a random crash, and nobody knows why. For a database server, wrong data is much worse than a crash.
Why the corrected-error log matters: it is an early warning. A DIMM that logs more and more corrected errors is likely to fail. You see it in the BMC event log (e.g. "Correctable ECC logging limit reached, DIMM C1"), dmesg | grep -i edac, or ras-mc-ctl --summary. Then you replace the DIMM in a planned window, before it causes an uncorrectable error and an outage.""",
exp="""ECC is like a spell-checker with one rule: it can fix one wrong letter in a word, and it can tell you a word has two wrong letters, but it cannot fix that word.
Corrected errors are not "fine because they were fixed". They are a warning light: the DIMM is wearing out or something (seating, the slot, the CPU) is not right. Track the count over time.""",
fig=('diag_a', 'q6'),
outs=[dict(t='The BMC event log: the warning, then the limit', lines="""$ sudo ipmitool sel elist | grep -i ecc
  51 | 09/28/2026 | 03:12:44 | Memory DIMM_C1 | {{Correctable ECC}} | Asserted
  5c | 10/01/2026 | 22:40:19 | Memory DIMM_C1 | {{Correctable ECC logging limit reached}} | Asserted""", notes=['Same DIMM, more and more errors, until the BMC stops logging each one. Plan a replacement.']),
      dict(t='The Linux side', lines="""$ sudo ras-mc-ctl --summary
Memory controller events summary:
        {{Corrected}} on DIMM Label(s): 'CPU_SrcID#0_MC#0_Chan#2_DIMM#0' location: 0:2:0:-1 errors: {{37}}
$ dmesg | grep -i edac | tail -1
[812345.120411] EDAC MC0: 1 {{CE}} memory read error on CPU_SrcID#0_MC#0_Chan#2_DIMM#0 (channel:2 slot:0 ...)""", notes=['<b>CE</b> = Corrected Error. 37 so far on one DIMM. Map the label to a slot and serial with <code>dmidecode -t memory</code>.'])])

E[10] = dict(part='Troubleshooting', topic='Server will not power on', reread='Module 9: A server that will not power on',
q='A server shows no lights and does not start from its front panel, while the server above it on the same PDU runs normally. Describe your checks in order, and explain how the BMC helps you decide where the problem is.',
hook='Follow the power: <b>Outlet, Cord, PSU, Standby/BMC, Button, Board</b>. The BMC tells you if standby power arrives.',
ans="""The server above works on the same PDU, so the PDU itself has power. The problem is between this server's outlet and its board.
1. Check the PDU outlet for this server: is that outlet switched on, or did its breaker or outlet group trip? Is the cord in the right outlet?
2. Check both power cords: seated at the PDU and at the PSUs, not damaged. Try a known-good cord and a known-good outlet.
3. Check the PSU LEDs: is there an AC/standby light on each PSU? Reseat each PSU.
4. Ask the BMC (ping, web page or ipmitool):
- If the BMC answers, standby power is reaching the board, so the cords and outlet are OK. Look at the power-on path: chassis status (Last Power Event, faults), the SEL (PSU or power events), try ipmitool power on (if that works, suspect the front panel button or its cable).
- If the BMC is dead too, there is no standby power at all: focus on the outlet, cords and PSUs.
5. Swap a PSU with a known-good one.
6. If the PSUs are fine but it still will not start, suspect the board or a short: remove cards and extra parts and try a minimum configuration.
7. Record what you found, verify it powers on and passes test, and document.""",
exp="""Power reaches a server in a chain: PDU outlet, cord, PSU, standby power to the board (which runs the BMC), then main power when the button is pressed. Check the links in that order, one at a time.
The BMC is your "is standby power arriving?" test. A BMC that answers proves the outlet, cord and at least one PSU are working, and its logs often show exactly what happened (for example AC lost, a PSU fault, or a power policy that keeps it off).""",
fig=('diag_a2', 'no_power'),
outs=[dict(t='The BMC answers, so standby power is there', lines="""$ ping -c 2 10.20.9.15
64 bytes from 10.20.9.15: icmp_seq=1 ttl=64 time=0.41 ms
$ ipmitool -I lanplus -H 10.20.9.15 -U admin -P ******** chassis status
System Power         : {{off}}
Power Overload       : false
Main Power Fault     : false
Power Control Fault  : false
Power Restore Policy : {{always-off}}
Last Power Event     : {{ac-failed}}""", notes=['<b>ac-failed</b>: it lost AC power (outlet, breaker or cord).', '<b>always-off</b>: when power came back, the BMC kept it off on purpose. That is why it looks dead.']),
      dict(t='The event log confirms it, then power on', lines="""$ ipmitool -I lanplus -H 10.20.9.15 -U admin -P ******** sel elist | tail -2
  8a | 10/02/2026 | 06:12:30 | Power Supply PSU1 | {{Power Supply AC lost}} | Asserted
  8b | 10/02/2026 | 06:12:30 | Power Supply PSU2 | {{Power Supply AC lost}} | Asserted
$ ipmitool -I lanplus -H 10.20.9.15 -U admin -P ******** power on
Chassis Power Control: Up/On""", notes=['Both PSUs lost AC at the same second: the outlet or its breaker, not the PSUs. Find out why before you close the ticket.'])])
