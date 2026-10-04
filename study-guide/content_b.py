from content_a2 import E

E[21] = dict(part='Foundations', topic='What Linux is and why servers use it', reread='Module 2: What Linux is and why data centers use it',
q='In your own words, what is Linux? Name two Linux distributions used on servers, and give four specific reasons Linux runs most data center servers.',
hook='Linux = <b>kernel</b>; distro = kernel + tools. Reasons: <b>S-L-R-T</b> ("Servers Love Running Tux").',
ans="""Linux is an operating system. Strictly, "Linux" is the kernel: the core part that talks to the hardware. It is packaged with tools into distributions. It is open source: the code is public and free to use.
Two server distributions: Red Hat Enterprise Linux (RHEL) and Ubuntu Server. (Also Rocky Linux and SUSE.)
Four reasons it runs most data center servers:
1. Stable: servers run for months without a reboot.
2. Low cost: most distributions are free; paid ones like RHEL charge for support, not the software.
3. Built for remote work: everything is done by command line and scripts over the network, with no screen. One person can manage hundreds of servers.
4. Transparent about hardware: tools like lspci and dmesg show exactly what the hardware is doing, which is what diagnostics need.
Also: secure, efficient, frequently updated, and most AI and cloud software is built for Linux first.""",
exp="""Think of the kernel as a car's engine, and a distribution as the whole car built around it: same engine, different models (RHEL, Rocky, Ubuntu, SUSE). In a data center the "car" has no dashboard screen: you drive it by typing commands over the network.""",
fig=('diag_a', 'q1'),
outs=[dict(t='Which Linux, which kernel, how long running', lines="""$ cat /etc/os-release | head -2
NAME="{{Rocky Linux}}"
VERSION="9.4 (Blue Onyx)"
$ uname -r
{{5.14.0-427.13.1.el9_4.x86_64}}
$ uptime
 09:14:02 up {{182 days}},  4:11,  1 user,  load average: 3.12, 3.40, 3.38""", notes=['The distribution is Rocky Linux 9.4; <b>uname -r</b> shows the kernel version.', '182 days without a reboot: "stable".'])])

E[22] = dict(part='Foundations', topic='Reading ip a output', reread='Module 7: Reading ip a',
q='Here is part of the ip a output from a server. List every piece of information you can read from it. Then name two things this command does not show, and where you would find them.',
code="""2: ens1f0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 9000 qdisc mq state UP
    link/ether 3c:ec:ef:12:34:56 brd ff:ff:ff:ff:ff:ff
    inet 10.20.5.14/22 brd 10.20.7.255 scope global dynamic ens1f0""",
hook='Read left to right: <b>Name, Flags, MTU, MAC, IP/mask, brd, dynamic</b>. Not shown: <b>Gateway, DNS, Speed</b>.',
ans="""What I can read:
- Interface number 2, named ens1f0 (Ethernet, slot 1, port 0). The name can change if the card moves slots.
- UP: the interface is enabled. LOWER_UP: it has a physical link (cable and switch port work). BROADCAST, MULTICAST: it can send those types of traffic.
- mtu 9000: jumbo frames. The switch port must use the same MTU.
- qdisc mq: the queue setup (multi-queue); state UP: the link is up.
- link/ether 3c:ec:ef:12:34:56: the MAC address. brd ff:ff:ff:ff:ff:ff: the broadcast MAC.
- inet 10.20.5.14/22: the IPv4 address and a /22 mask (255.255.252.0), so the subnet is 10.20.4.0 to 10.20.7.255.
- brd 10.20.7.255: the broadcast address of that subnet.
- scope global: a normal, routable address.
- dynamic: it came from DHCP (a static address shows "forever" for the lease).
Two things it does not show:
- The default gateway: use ip route.
- The DNS servers: look in /etc/resolv.conf.
(Also the link speed: ethtool ens1f0.)""",
exp="""ip a answers "who am I on the network?": my name, my MAC, my IP and mask, and whether my link is up. It does not answer "where do I send traffic?" (the gateway, in ip route) or "who turns names into IPs?" (DNS, in resolv.conf).
The /22 is a bigger subnet than the usual /24: four blocks of 256 addresses, 10.20.4.x to 10.20.7.x.""",
fig=('diag_a', 'q2'),
outs=[dict(t='The things ip a does not show', lines="""$ ip route
{{default via 10.20.4.1}} dev ens1f0 proto dhcp src 10.20.5.14 metric 100
10.20.4.0/22 dev ens1f0 proto kernel scope link src 10.20.5.14 metric 100
$ cat /etc/resolv.conf
search lab.local
{{nameserver 10.20.5.5}}
$ ethtool ens1f0 | grep -E "Speed|Link detected"
        Speed: {{25000Mb/s}}
        Link detected: yes""", notes=['Gateway from <b>ip route</b>, DNS from <b>resolv.conf</b>, speed from <b>ethtool</b>.'])])

E[23] = dict(part='Foundations', topic='How a name becomes an IP address', reread='Module 7: DNS',
q='Explain how a Linux server turns the name db01 into an IP address. Include which files are involved, the order they are checked, and what DNS records and caching are.',
hook='<b>hosts first, then resolv.conf, then the DNS server, then cache.</b> A record = name to IPv4.',
ans="""1. Linux checks /etc/hosts first. It is a local file that maps names to IP addresses. If db01 is listed there, Linux uses that and stops. (The order "files, then DNS" is set in /etc/nsswitch.conf.)
2. If db01 is not in /etc/hosts, Linux asks the DNS server listed in /etc/resolv.conf (the "nameserver" line). If I type a short name, the "search" domain is added, for example db01.lab.local.
3. The DNS server answers from its own records if it is in charge of that domain. If not, it asks other DNS servers and passes the answer back.
DNS records are the entries stored on the DNS server. An A record maps a name to an IPv4 address (db01 to 10.4.2.15). Others: AAAA (name to IPv6) and CNAME (an alias, another name for the same host).
Caching means the answer is saved for a while (its TTL, time to live), so the next lookup is fast and does not have to go out again. It also means that after a record changes, the old answer can stay until the cache expires.
To test: nslookup db01 or dig db01 (ask DNS directly), and getent hosts db01 (what the system really uses, including /etc/hosts).""",
exp="""It is like finding a phone number: first your own contact list (/etc/hosts), then directory assistance (the DNS server from resolv.conf). Directory assistance may phone another directory if it does not know, and you remember the answer for a while (cache).
This is why /etc/hosts can "win" over DNS: a wrong line in hosts gives a wrong answer even when DNS is perfect.""",
fig=('diag_b', 'dns_flow'),
outs=[dict(t='The two files, in order', lines="""$ cat /etc/hosts
127.0.0.1   localhost localhost.localdomain
::1         localhost localhost.localdomain
{{(no db01 line, so DNS is next)}}
$ cat /etc/resolv.conf
search lab.local
nameserver {{10.20.5.5}}""", notes=['db01 is not in the hosts file, so Linux asks 10.20.5.5.']),
      dict(t='The DNS answer: an A record with a TTL', lines="""$ dig db01.lab.local +noall +answer
db01.lab.local.         {{300}}     IN      {{A}}       {{10.4.2.15}}
$ getent hosts db01
10.4.2.15       db01.lab.local""", notes=['<b>A</b> = name to IPv4. <b>300</b> = the TTL: the answer may be cached for 300 seconds.'])])

E[24] = dict(part='Foundations', topic='PCIe bandwidth and the math', reread='Module 4: Lanes, generations, and bandwidth',
q='What determines the bandwidth of a PCIe link? List the factors. Then estimate the bandwidth in each direction of a Gen 4 x8 link and show your math.',
hook='<b>GT/s x lanes / 8 = GB/s each way.</b> Gen 4 x8 = 16 x 8 / 8 = <b>16 GB/s</b>.',
ans="""Factors:
1. The generation: the speed per lane. Gen 3 = 8 GT/s, Gen 4 = 16 GT/s, Gen 5 = 32 GT/s. Each generation doubles the speed.
2. The width: the number of lanes (x1, x4, x8, x16).
3. Encoding overhead: Gen 3 to 5 lose about 1.5%; Gen 1 and 2 lost 20%.
4. The weakest part of the path: the link runs at the best speed and width that both ends and everything in between support. A Gen 5 card in a Gen 4 slot runs at Gen 4.
5. What the link actually trained to (LnkSta in lspci -vv), and how the slot is wired (an x16 slot may be wired x8).
6. Shared links: devices behind a PCIe switch share one uplink to the CPU.
Math for Gen 4 x8:
16 GT/s x 8 lanes = 128 Gb/s.
128 / 8 bits per byte = 16 GB/s.
Minus about 1.5% encoding = about 15.75 GB/s.
Answer: about 16 GB/s in each direction (about 32 GB/s in both directions together).""",
exp="""GT/s means "billions of transfers per second". Each transfer is one bit on one lane, so GT/s x lanes is roughly bits per second, and dividing by 8 turns bits into bytes.
Handy shortcut: Gen 4 is about 2 GB/s per lane each way, Gen 5 about 4 GB/s. So Gen 4 x8 = 8 x 2 = 16 GB/s, and Gen 5 x8 equals Gen 4 x16 (about 32 GB/s).""",
fig=('diag_a', 'q5'),
outs=[dict(t='Reading a Gen 4 x8 link', lines="""$ sudo lspci -vv -s 3b:00.0 | grep -E "LnkCap:|LnkSta:"
        LnkCap: Port #0, Speed {{16GT/s}}, Width {{x8}}, ASPM not supported
        LnkSta: Speed {{16GT/s}}, Width {{x8}}""", notes=['16 GT/s = Gen 4; x8 = 8 lanes. LnkSta matches LnkCap, so it got the full link: about 16 GB/s each way.'])])

E[25] = dict(part='Foundations', topic='Topology tree versus diagram', reread='Module 4: Topology diagram and topology tree',
q='Your service guide includes a drawing of how every PCIe slot is wired, and Linux can print the PCIe tree it actually found. Explain what each one shows, which command prints the tree, and how comparing the two helps you find a fault.',
hook='<b>Diagram = expected. Tree (lspci -tv) = actual.</b> The shape of what is missing points to the part.',
ans="""The drawing is the topology diagram: the expected picture. It shows which CPU and root port each slot connects to, which PCIe switches, risers, retimers and cables sit in between, the expected link width, how slots map to bus numbers, and which devices share a path.
The tree is the actual picture: what Linux really found. The command is lspci -tv. It shows the root ports, the switches and the devices under them, with bus numbers like [17-1a].
Comparing them shows where the fault is, from what is missing:
- A port is there but nothing is under it: that one device did not link. Suspect the device, its power cable, its seating, the slot, or a retimer.
- A whole branch is missing: something upstream failed. Suspect the riser, cable, switch, retimer, the CPU root port, or a slot disabled in the BIOS.
- Everything under one switch is missing: suspect the switch or its uplink, not each device.
So instead of swapping parts one by one, I go straight to the part that the missing devices have in common.""",
exp="""It is like a seating chart for a theater. The chart (diagram) says who should be in each seat. Looking at the room (the tree) shows who is actually there. One empty seat means one person did not come; a whole empty row means the row's door is locked.
<code>lspci -vv</code> on the port also helps: "Physical Slot" tells you which slot it is, and PresDet (presence detect) tells you whether a card is even sensed.""",
fig=('diag_b', 'topo_compare'),
outs=[dict(t='The actual tree', lines="""$ lspci -tv
-[0000:00]-+-01.0-[17-1a]----00.0-[18-1a]--+-00.0-[19]----00.0  NVIDIA Corporation GH100 [H100 PCIe]
           |                               {{\\-04.0-[1a]--}}
           +-03.0-[3b]----00.0  Mellanox Technologies MT2892 Family [ConnectX-6 Dx]
           \\-05.0-[5e]----00.0  Samsung Electronics Co Ltd NVMe SSD Controller""", notes=['Port <b>04.0</b> has a bus number [1a] but nothing under it: GPU slot 2 did not link.']),
      dict(t='Ask the empty port which slot it is', lines="""$ sudo lspci -vv -s 18:04.0 | grep -E "Physical Slot|SltSta|LnkSta:"
                Physical Slot: {{2}}
                LnkSta: Speed 2.5GT/s (downgraded), Width {{x0}} (downgraded)
                SltSta: Status: AttnBtn- PowerFlt- MRL- CmdCplt- {{PresDet+}} Interlock-""", notes=['Slot 2. <b>PresDet+</b>: a card is sensed in the slot, but the link is <b>x0</b>: it never trained. Suspect the GPU\'s power cable, seating, or a retimer.'])])

E[26] = dict(part='Foundations', topic='What the BMC is and does', reread='Module 8: The BMC',
q='What is a BMC, and why does it keep working when the server’s operating system has crashed? List at least six things a technician can do with it.',
hook='BMC = <b>own CPU, own network port, standby power</b>. Does: <b>SEL, Sensors, Inventory, KVM, SOL, Power, NMI, Boot/ISO</b>.',
ans="""The BMC (Baseboard Management Controller) is a small separate computer on the motherboard, with its own processor, firmware and network port. Vendor names: iDRAC (Dell), iLO (HPE), XCC (Lenovo), IPMI/BMC (Supermicro and others).
Why it keeps working when the OS has crashed: it does not depend on the OS at all. It runs on standby power, which is on whenever the server is plugged in, even when the server is off. It has its own network connection (the management network). This is called out-of-band management.
Things a technician can do with it (web page, ipmitool or Redfish):
1. Read the System Event Log (SEL): memory, PCIe, power, fan and temperature events with times (ipmitool sel elist).
2. Read sensors: temperatures, voltages, fan speeds, PSU status, power draw (ipmitool sensor).
3. See hardware inventory, health, serial numbers (ipmitool fru print) and firmware versions.
4. Use the virtual console (KVM) to see the screen.
5. Use Serial Over LAN for a text console (ipmitool sol activate).
6. Control power: on, off, reset, power cycle (ipmitool power cycle).
7. Send an NMI to force a crash dump.
8. Change the boot order and mount an ISO as virtual media.""",
exp="""The BMC is like the night security guard of a building: separate from the office workers (the OS), on its own power line, with cameras (sensors), a logbook (SEL) and the keys to every door (power control). When the offices are dark, the guard is still there.
That is why the first step for a frozen or unreachable server is almost always "open the BMC".""",
fig=('diag_b', 'bmc_board'),
outs=[dict(t='Sensors and the event log', lines="""$ sudo ipmitool sensor | head -5
CPU1 Temp        | 58.000     | degrees C  | ok
Inlet Temp       | 24.000     | degrees C  | ok
FAN1             | 7800.000   | RPM        | ok
PSU1 Status      | 0x1        | discrete   | 0x0100| na
PSU2 Status      | 0x1        | discrete   | 0x0100| na
$ sudo ipmitool sel elist | tail -2
  91 | 10/02/2026 | 03:12:44 | Memory DIMM_C1 | Correctable ECC | Asserted
  92 | 10/02/2026 | 03:40:02 | {{Watchdog2}} | Hard reset | Asserted""", notes=['Live readings, and a timeline of hardware events. These work even when the OS is down.']),
      dict(t='Inventory and power control', lines="""$ sudo ipmitool fru print 0 | grep -E "Product Name|Serial"
 Board Serial          : {{WM21AS003127}}
 Product Name          : SYS-421GE-TNRT
 Product Serial        : {{S421A0991}}
$ sudo ipmitool power status
Chassis Power is on""", notes=['Serial numbers for the repair record, and the power state.'])])

E[27] = dict(part='Foundations', topic='LnkCap versus LnkSta', reread='Module 4: Link training',
q='Explain what LnkCap and LnkSta mean in lspci -vv output. What does it mean when they do not match, and what could cause it?',
hook='<b>Cap = Can. Sta = Status (what it got).</b> Sta lower than Cap = downtrained: works, but slower.',
ans="""LnkCap (link capability): the best speed and width the device can do, for example Speed 16GT/s (Gen 4), Width x16.
LnkSta (link status): what the link actually trained to when the system powered on.
At power on, every PCIe link negotiates ("trains") its speed and width. If LnkSta matches LnkCap, the device got its full link. If LnkSta is lower, the link is downtrained: the device works, but slower. For example LnkCap x16 and LnkSta x4 = a quarter of the bandwidth.
Possible causes:
- The slot or path cannot do more: a Gen 5 card in a Gen 4 slot, or an x16 slot that is only wired x8. This one is expected, not a fault (check the topology diagram).
- Poor seating or a dirty connector.
- A bad riser, cable or retimer.
- A BIOS setting: link speed forced lower, or the wrong bifurcation.
- Signal problems, which usually also show as AER errors in dmesg.
Fix one thing at a time (reseat, clean, swap the riser or cable) and check LnkSta again after each change.""",
exp="""Link training is like two people agreeing how fast to talk on a noisy phone line. If the line is clean, they talk at full speed. If it is noisy, they slow down until they can understand each other. A downtrained link is a noisy line.
Modern lspci even prints "(downgraded)" next to the speed or width in LnkSta when it is lower than LnkCap.""",
fig=('diag_b', 'lnk_training'),
outs=[dict(t='A downtrained x16 card', lines="""$ sudo lspci -vv -s 19:00.0 | grep -E "LnkCap:|LnkSta:"
        LnkCap: Port #0, Speed 16GT/s, Width {{x16}}, ASPM not supported
        LnkSta: Speed 16GT/s, Width {{x4 (downgraded)}}""", notes=['Full speed (Gen 4) but only 4 of 16 lanes: a quarter of the bandwidth. Check the slot wiring first, then seating, riser, cable, retimer and BIOS.']),
      dict(t='Often seen together: corrected PCIe errors', lines="""$ dmesg | grep -c "AER: Corrected"
{{1832}}""", notes=['A steady stream of corrected errors on the same path points to a signal problem, not a slot that is simply wired x4.'])])

E[28] = dict(part='Foundations', topic='The four layers of a working device', reread='Module 3: The four layers',
q='Describe the four layers you check to decide whether a device is really working in Linux, and name the command or check you would use at each layer. Give an example where a device passes one layer and fails the next.',
hook='<b>P-B-D-F: Physical, Bus, Driver, Function</b> ("Please Buy Donuts Friday"). Find the first layer that fails.',
ans="""1. Physical: is it installed, seated and powered, and does the BIOS or BMC see it? Check: look at it, its LEDs, and the BIOS or BMC inventory.
2. Bus: does the OS see it on the bus? Check: lspci for PCIe devices, lsblk or nvme list for drives.
3. Driver: is a driver attached? Check: lspci -k ("Kernel driver in use"), and dmesg for driver errors.
4. Function: is it configured and actually working? Check: ip a for a NIC, nvidia-smi for a GPU, or a functional test.
Example 1: a NIC shows in lspci (passes Bus), but lspci -k has no "Kernel driver in use" line (fails Driver). The hardware is fine; the driver is missing. Fix the driver; do not replace the card.
Example 2: a GPU shows in lspci (passes Bus) but not in nvidia-smi (fails Driver/Function). That is a driver or firmware problem, not hardware.""",
exp="""Each layer depends on the one below it. A card that is not seated cannot be on the bus; a device not on the bus cannot get a driver; without a driver it cannot work. So you check from the bottom up and stop at the first layer that fails: that is where the problem lives, and it tells you what kind of fix to make (hardware, driver or configuration).""",
fig=('diag_b', 'four_layers'),
outs=[dict(t='Passes Bus, fails Driver (a NIC)', lines="""$ lspci | grep -i ethernet
{{3b:00.0 Ethernet controller}}: Mellanox Technologies MT2892 Family [ConnectX-6 Dx]
$ lspci -k -s 3b:00.0
3b:00.0 Ethernet controller: Mellanox Technologies MT2892 Family [ConnectX-6 Dx]
        Subsystem: Mellanox Technologies Device 0016
        {{(no "Kernel driver in use" line)}}
$ modinfo mlx5_core
{{modinfo: ERROR: Module mlx5_core not found.}}""", notes=['On the bus, but no driver installed: install the driver package. The card is fine.']),
      dict(t='Passes Bus, fails Function (a GPU)', lines="""$ lspci | grep -ic nvidia
{{8}}
$ nvidia-smi
{{NVIDIA-SMI has failed because it couldn't communicate with the NVIDIA driver.}}
Make sure that the latest NVIDIA driver is installed and running.""", notes=['All 8 GPUs are on the bus, but the driver is not running: a driver problem, not 8 bad GPUs.'])])

E[29] = dict(part='Foundations', topic='Symptom versus root cause', reread='Module 10: Symptom versus root cause',
q='A technician writes “Root cause: GPU not detected” on a repair ticket. Explain why that is a symptom and not a root cause. Then use the 5 Whys to trace an example of your own down to a process root cause.',
hook='<b>Symptom = what you see. Root cause = why.</b> Ask "why?" until you reach a <b>process</b>.',
ans=""""GPU not detected" is what was observed, so it is the symptom. The root cause is why it happened. If you only fix the symptom (reseat the GPU and ship the unit), the same thing happens again on the next unit.
Example with the 5 Whys:
1. Why was the GPU not detected? Its power cable was not connected.
2. Why was it not connected? The cable was routed where it could not reach the GPU.
3. Why was it routed that way? The assembler followed the work instruction.
4. Why did the work instruction show that routing? It showed an old layout.
5. Why did it show an old layout? It was not updated after a design change to the chassis.
Root cause: the out-of-date work instruction, a process problem, not this one unit. Fix: update the work instruction, add a step so design changes always update the instructions, and check other units built with the old version.""",
exp="""A symptom tells you what is wrong; a root cause tells you how to stop it happening again. If a ticket's "root cause" could also be read as "the problem", it is still a symptom.
Stop asking "why?" when you reach something you can change in the process (an instruction, a check, a tool), not when you reach a person to blame.""",
fig=('diag_b', 'five_whys'),
outs=[dict(t='The symptom', lines="""$ nvidia-smi -L | wc -l
{{7}}
$ nvidia-smi -L | tail -2
GPU 5: NVIDIA H100 80GB HBM3 (UUID: GPU-6f1c...)
GPU 6: NVIDIA H100 80GB HBM3 (UUID: GPU-a207...)""", notes=['7 of 8 GPUs: that is <b>what</b> is wrong, not <b>why</b>.']),
      dict(t='Weak ticket vs strong ticket', lines="""WEAK    Root cause: GPU not detected.  Action: reseated GPU.
STRONG  Symptom:    GPU slot 7 not detected (7 of 8 in nvidia-smi).
        Cause:      aux power cable not connected; routing in WI rev C cannot reach.
        {{Root cause: WI not updated after chassis change ECO-1142.}}
        Action:     cable connected, all 8 GPUs pass; WI updated to rev D;
                    shift 2 units from the same build checked.""", notes=['The strong ticket names the process problem and what was done about it.'])])

E[30] = dict(part='Troubleshooting', topic='Server lost network after a move', reread='Module 7: A server that stops responding; Module 8',
q='A Linux server stopped answering ping and SSH right after it was moved to a new rack position. What is your very first check, and what is the reason for it? Then walk through the rest of your process in order.',
hook='First: <b>is it alive? Ask the BMC.</b> Then bottom-up: <b>Link, NIC, IP, Gateway, Name, Service</b>.',
ans="""First check: is the server actually up? Use the BMC (virtual console or SOL, and power status). Reason: you cannot SSH into a server that is off or crashed. After a move it may not have powered back on, may be stuck in POST, or may show an error. The BMC tells me if it is a server problem or a network problem before I start pulling cables.
Then, in order:
1. Physical link: cable plugged in at both ends, link lights on, transceiver seated, cable in the right switch port for the new position. ethtool shows "Link detected", ip a shows LOWER_UP or NO-CARRIER. Try a known-good cable or port.
2. NIC and driver: lspci, lspci -k and dmesg. A card or riser can come loose during a move.
3. IP address: ip a. Is there an address? 169.254 means DHCP failed, which happens if the new switch port is on a different VLAN.
4. Gateway: ip route, ping the gateway, then ping past it and use traceroute.
5. Names: test by IP and by name.
6. Service and firewall: systemctl status sshd, ss -tulpn, firewall rules.
7. Ask what changed with the move (new port, VLAN, cable), test from another machine, fix it, confirm ping and SSH work, and document every check.""",
exp="""A move changes physical things: power cables, network cables, the switch port and maybe the VLAN. So the most likely causes are at the bottom of the stack.
The BMC check comes first because it splits the problem in half in one minute: either the server is down (power, POST, boot), or it is up and the network path is the problem.""",
fig=('diag_b', 'rack_move'),
outs=[dict(t='Step 0: the BMC says it is alive', lines="""$ ipmitool -I lanplus -H 10.20.9.14 -U admin -P ******** power status
{{Chassis Power is on}}
$ ipmitool -I lanplus -H 10.20.9.14 -U admin -P ******** sol activate
srv-r07-u12 login: {{_}}""", notes=['Powered on and sitting at a login prompt: the OS is up, so this is a network problem.']),
      dict(t='Step 1 (on the console): no link', lines="""$ ip a show ens1f0 | head -1
2: ens1f0: <{{NO-CARRIER}},BROADCAST,MULTICAST,UP> mtu 9000 qdisc mq state {{DOWN}}
$ ethtool ens1f0 | grep "Link detected"
        {{Link detected: no}}""", notes=['NO-CARRIER: no physical link. Check the cable at both ends and the switch port for the new position.'])])

E[31] = dict(part='Troubleshooting', topic='New card missing from lspci', reread='Module 3: lspci; Module 4: Topology; Module 11: Playbook A',
q='A technician installs a new 100G network card and says it is dead because lspci does not show it. What would you check, in order, before agreeing?',
hook='Walk the whole path: <b>Search, BIOS/BMC, Seat, Settings, Tree, Logs, Swap</b>. Only then call it dead.',
ans="""1. Check we searched correctly: a 100G Mellanox card shows as "Ethernet controller" (or "Infiniband controller"). Run lspci | grep -i -E "ethernet|mellanox|infiniband" and compare the count with the build sheet.
2. BIOS and BMC inventory: if they do not see the card either, it is physical or firmware. If they see it but Linux does not, it is something else.
3. Physical, powered off with an ESD strap: card fully seated and latched, riser seated, riser cable connected, any power cable connected, no bent pins or damage, and the card in the slot the build calls for.
4. BIOS settings: slot enabled, bifurcation right for that slot, link speed not forced.
5. Topology: compare lspci -tv with the topology diagram. Port there but empty: card, seating, slot. Whole branch missing: riser, cable, switch, retimer. Are other devices on the same riser missing too?
6. Logs: dmesg and the BMC SEL for PCIe or hot-plug messages ("Card not present").
7. Swap: put the card in a known-good slot, or a known-good card in this slot. If the problem follows the card, the card is bad.
Only then agree it is dead: tag it, document it, start an RMA.""",
exp=""""Not in lspci" means the card never appeared on the bus. That can be the card, but it is just as often the slot, the riser, a cable or a BIOS setting. A new card being dead on arrival is the least likely cause, so it is the last thing you conclude, after the swap proves it.""",
fig=('diag_b', 'card_missing'),
outs=[dict(t='Searching the right way, then the tree', lines="""$ lspci | grep -i -E "ethernet|mellanox|infiniband"
{{c1:00.0}} Ethernet controller: Intel Corporation Ethernet Controller X710 for 10GBASE-T
c1:00.1 Ethernet controller: Intel Corporation Ethernet Controller X710 for 10GBASE-T
{{(no Mellanox card)}}
$ lspci -tv | grep -A1 "30:02.0"
           +-02.0-[{{31}}]--""", notes=['Only the onboard 10G ports. The port that feeds slot 4 has a bus number but nothing under it.']),
      dict(t='The slot does not even sense a card', lines="""$ sudo lspci -vv -s 30:02.0 | grep -E "Physical Slot|SltSta"
                Physical Slot: {{4}}
                SltSta: Status: AttnBtn- PowerFlt- MRL- CmdCplt- {{PresDet-}} Interlock-
$ dmesg | grep -i "slot(4)"
[    6.211873] pcieport 0000:30:02.0: pciehp: {{Slot(4): Card not present}}""", notes=['<b>PresDet-</b> and "Card not present": the slot does not sense the card at all. Reseat it (and its riser) before blaming the card.'])])

E[32] = dict(part='Troubleshooting', topic='Intermittent failure', reread='Module 10: Intermittent problems',
q='A test fails roughly once every 15 runs, and you cannot make it fail on demand. List the data you would gather, and explain how you would turn it into a failure you can reproduce.',
hook='<b>Log every run, find the pattern, then cause it on purpose.</b> Loop + watch + one change at a time.',
ans="""Data to gather:
- The exact error message and which test step fails, every time.
- The timestamps and how often (which run numbers failed).
- Which tests pass and which fail.
- Temperature and load at the time of each failure.
- Logs from each failure: dmesg, journalctl and the BMC SEL.
- Serial numbers, and firmware and driver versions.
- Whether other units or other slots show the same thing.
Turning it into something I can reproduce:
1. Look for a pattern: only under heavy load, only when hot, only late in a long run, only in one slot or one unit.
2. Run the test in a loop and log every run, for example for i in $(seq 1 100); do ./test.sh >> results.txt; done, while watching dmesg -w and the sensors.
3. Push the suspected condition on purpose: more load, more heat, a longer run.
4. Look for corrected errors (PCIe AER, ECC) that warn about a weak part before it fails.
5. Check seating and cables, then change one variable at a time and rerun enough cycles to trust the result. At 1 failure in 15, twenty clean runs proves nothing; I want 100 or more.
6. Compare with a golden unit, and document every step and result.""",
exp="""An intermittent failure is not random; you just have not found its trigger yet. Logging every run lets you line up the failures with something else (temperature, load, time, a slot).
Once you can make it fail on purpose, you can test a fix properly: if it used to fail 1 in 15 and now passes 150 in a row, the fix worked.""",
fig=('diag_b', 'intermittent'),
outs=[dict(t='Which runs failed', lines="""$ grep -c FAIL results.txt
{{3}}
$ grep -n FAIL results.txt
9:run 9   {{FAIL}}  2026-10-02 10:41:07  dma_test: timeout on GPU 3
24:run 24  {{FAIL}}  2026-10-02 12:58:44  dma_test: timeout on GPU 3
38:run 38  {{FAIL}}  2026-10-02 15:02:19  dma_test: timeout on GPU 3""", notes=['Always the same GPU and the same step: a pattern already.']),
      dict(t='What happened at that exact time', lines="""$ journalctl -k --since "10:40:30" --until "10:41:30" | tail -2
Oct 02 10:41:05 srv-r07-u12 kernel: pcieport 0000:17:01.0: {{AER: Corrected error}} message received from 0000:3d:00.0
Oct 02 10:41:07 srv-r07-u12 kernel: NVRM: Xid (PCI:0000:3d:00): 79, pid=0, GPU has fallen off the bus.
$ grep "10:41" sensors_log.txt | grep GPU3
10:41:00  GPU3 Temp  {{83 C}}""", notes=['Corrected PCIe errors just before each failure, and GPU 3 is over 80 C: suspect heat plus a weak link. Now reproduce it with heat on purpose.'])])

E[33] = dict(part='Troubleshooting', topic='Powers on but no OS', reread='Module 9: Powers on but will not boot',
q='A server’s fans spin and its health LED is green, but you never get a login prompt. Describe your troubleshooting stage by stage, and where you would look at each stage.',
hook='Booting is a chain: <b>Power, POST, BIOS, GRUB, Kernel, Startup</b>. Watch the console and find where it stops.',
ans="""Fans and a green LED only prove the server has power. Booting is a chain, so I find how far it gets. I open the console through the BMC (virtual console or SOL), watch a whole boot, and note exactly where it stops. I also check the BMC event log for CPU, memory, PCIe or power errors.
1. POST: stuck on a POST code or beeping? Memory training on a large server takes minutes, so wait first. If truly stuck, look up the code and suspect memory, a CPU or a PCIe card; reseat. If needed, strip to a minimum configuration (one CPU, one DIMM, no cards) and add parts back one at a time.
2. UEFI/BIOS: "No bootable device" or a PXE loop? Check the boot drive appears in the BIOS, the boot order, UEFI versus Legacy, Secure Boot, the cables and the RAID controller.
3. Bootloader (GRUB): a grub rescue> prompt or "file not found" points to the boot partition or the drive.
4. Kernel: a kernel panic or "Unable to mount root fs" points to a storage driver, the root filesystem or the drive. Read the exact message.
5. System startup: emergency mode usually means a bad /etc/fstab entry or a failing disk. Log in on the console and read journalctl -xb.
6. If the console reaches a login prompt but I still cannot log in over the network, it booted and the problem is the network.
Always ask what changed, check firmware, and document where it stopped and what fixed it.""",
exp="""Think of the boot chain as a relay race: each runner hands the baton to the next. The console shows you exactly which runner dropped it. Without the console you are guessing; with it, the exact message usually tells you which module of the course to use next.""",
fig=('diag_b', 'boot_chain'),
outs=[dict(t='Watching the boot over SOL: it stops in GRUB', lines="""$ ipmitool -I lanplus -H 10.20.9.14 -U admin -P ******** sol activate
[SOL Session operational.  Use ~? for help]
error: {{no such partition.}}
Entering rescue mode...
{{grub rescue>}} _""", notes=['POST and the BIOS worked (it found a disk and started GRUB). GRUB cannot find its partition: look at the boot drive and partition, and ask what changed.']),
      dict(t='The BMC log for the same boot', lines="""$ ipmitool -I lanplus -H 10.20.9.14 -U admin -P ******** sel elist | tail -2
  a3 | 10/02/2026 | 08:05:44 | System Firmware Progress | Starting operating system boot process | Asserted
  a4 | 10/02/2026 | 08:05:45 | Drive Slot 0 | {{Drive Fault}} | Asserted""", notes=['A drive fault in slot 0 (the boot drive) right at boot: a strong lead.'])])

E[34] = dict(part='Troubleshooting', topic='NVMe drops out under load', reread='Module 6: A drive that drops out',
q='During a long stress test, an NVMe drive vanishes from lsblk. After a reboot it is back and looks healthy. What evidence would you look for, and what could be causing it?',
hook='<b>A reboot hides it, it does not fix it.</b> Evidence: <b>kernel log, SEL, smart-log, LnkSta, firmware</b>. Then swap bays.',
ans="""A reboot resets the link, so the drive comes back, but the cause is still there.
Evidence:
1. Kernel messages from when it dropped. If not rebooted yet: save dmesg > nvme_drop.txt first. After a reboot: journalctl -b -1 -k | grep -i nvme. Look for "I/O timeout, aborting", "controller is down; will reset", "Removing after probe failure", and PCIe AER errors.
2. The BMC event log for drive, PCIe or temperature events at the same time.
3. Drive health: nvme smart-log (temperature, critical warnings, media errors, unsafe shutdowns).
4. The link: sudo lspci -vv for LnkSta versus LnkCap, and AER errors on the port above the drive.
5. Firmware versions for the drive, the backplane and the BIOS.
Possible causes: poor seating or a worn backplane connector, a bad or misrouted cable, overheating under load, a power-saving feature that does not wake up, a firmware bug, a PCIe signal problem, or a failing drive.
Then isolate: move the drive to another bay. Follows the drive = the drive. Stays with the bay = the bay, backplane or cable. Reproduce under load (fio) while watching dmesg -w and the temperature, and document everything.""",
exp="""The test only fails "under load" and "after a long time": both point to heat, power or a weak signal that gives up when stressed. That is why temperature and AER errors are as important as the drive's own health.
The previous-boot journal is the key: dmesg after the reboot shows a healthy drive, but journalctl -b -1 shows the moment it fell off.""",
fig=('diag_b', 'nvme_drop'),
outs=[dict(t='The previous boot shows the drop', lines="""$ journalctl -b -1 -k | grep -i nvme | tail -3
Oct 02 03:14:51 srv-r07-u12 kernel: nvme nvme1: I/O 412 QID 9 {{timeout, aborting}}
Oct 02 03:15:22 srv-r07-u12 kernel: nvme nvme1: {{controller is down; will reset}}: CSTS=0xffffffff, PCI_STATUS=0x10
Oct 02 03:15:23 srv-r07-u12 kernel: nvme 0000:5e:00.0: {{Removing after probe failure}} status: -19""", notes=['Timeout, then the controller stopped answering, then Linux removed it.']),
      dict(t='Health and temperature', lines="""$ sudo nvme smart-log /dev/nvme1 | grep -i -E "critical|^temperature|media|unsafe"
critical_warning                        : {{0x2}}
temperature                             : {{82 C}} (355 Kelvin)
media_errors                            : 0
unsafe_shutdowns                        : 3""", notes=['critical_warning 0x2 = temperature warning; 82 C is hot. Media errors are 0. Suspect airflow in that bay before the drive.'])])

E[35] = dict(part='Troubleshooting', topic='GPU missing, empty port in lspci -tv', reread='Module 11: Playbook B; Module 4: Topology',
q='An 8-GPU server shows only seven GPUs. In lspci -tv, the PCIe port that should lead to GPU 6 is present but has nothing under it. List what could cause this, and explain how you would narrow it down.',
hook='<b>Empty port = the GPU end</b> (GPU, power cable, seating, slot, retimer). <b>Missing branch = upstream.</b>',
ans="""An empty port means the port exists but the device under it never linked. The path up to that port is working (otherwise the whole branch would be missing), so the problem is at the GPU end.
Possible causes:
- The GPU is not fully seated.
- Its auxiliary power cable is missing, loose or in the wrong connector.
- A bad slot or connector.
- A failed retimer on that path (on the riser or GPU baseboard).
- The slot disabled in the BIOS.
- The GPU itself is dead.
Narrowing it down:
1. Use the topology diagram to confirm which slot is GPU 6, and check the BMC inventory and SEL for power or PCIe events on it.
2. Check dmesg for PCIe errors on that port, and the BIOS slot settings.
3. Powered off with ESD protection: reseat GPU 6 and check its power cable is in the right connector. Check PSU status.
4. Swap test: move GPU 6 to a working slot, and put a known-good GPU in slot 6. Follows the GPU = bad GPU. Stays with slot 6 = slot, power cable or retimer.
5. Verify all eight GPUs show in lspci and nvidia-smi, run a full GPU test, and document.""",
exp="""An empty port is like a mailbox with your name on it but no mail: the address exists, but nothing arrived. So the street (switch, riser) is fine; the problem is at your house (the GPU, its power, its seating).
lspci -vv on the empty port helps: PresDet+ means the slot senses a card, so think power cable and seating; PresDet- means no card is sensed at all.""",
fig=('diag_b', 'gpu_tree'),
outs=[dict(t='Counting at each layer', lines="""$ nvidia-smi -L | wc -l
{{7}}
$ lspci | grep -ic nvidia
{{7}}""", notes=['Seven at the driver layer and seven on the bus: the eighth never reached the bus. A hardware path problem.']),
      dict(t='The empty port', lines="""$ lspci -tv | grep -B1 -A1 "0c.0"
           |               +-08.0-[cb]----00.0  NVIDIA Corporation GH100 [H100 SXM5 80GB]
           |               {{+-0c.0-[cc]--}}
           |               \\-10.0-[cd]----00.0  NVIDIA Corporation GH100 [H100 SXM5 80GB]
$ sudo lspci -vv -s c9:0c.0 | grep -E "SltSta|LnkSta:"
                LnkSta: Speed 2.5GT/s (downgraded), Width {{x0}} (downgraded)
                SltSta: Status: AttnBtn- PowerFlt- MRL- CmdCplt- {{PresDet+}} Interlock-""", notes=['Port 0c.0 is empty. PresDet+ (a card is sensed) but no link: check GPU 6\'s power cable and seating first.'])])

E[36] = dict(part='Troubleshooting', topic='Assembly cable error on three units', reread='Module 11: Playbook D',
q='Three servers from the same shift fail test because a cable was plugged into the wrong connector during assembly. After fixing them, what do you do, and how do you keep it from happening again?',
hook='<b>V-D-N-C-P + CAPA</b>: Verify, Document, Notify, Contain, Prevent. Fix the <b>process</b>, not the person.',
ans="""1. Verify: each of the three servers fully passes test after the fix, and the wrong connection did not damage anything.
2. Document: the unit serials, which cable, the wrong port and the correct port, the test results, and photos if allowed.
3. Notify: my lead, quality and the assembly team.
4. Contain: three units from one shift means there may be more. Check other units from the same line, shift or batch, including units that already passed and units waiting to ship.
5. Prevent it:
- Update the work instruction with clear pictures of the right connection.
- Add labels or color coding on the cable and the connector.
- Use mistake-proofing: keyed connectors, or cable lengths that only reach the right port.
- Add an inspection step that checks this cable before test.
6. Track it through the site's corrective action process (CAPA) so it gets followed up.
The focus is on fixing the process, not blaming the person who plugged it in.""",
exp="""Fixing the three units fixes today. Containment protects the customer from units you have not found yet, and prevention protects tomorrow. If the same mistake happened three times in one shift, the process made it easy to do; change the process so it becomes hard or impossible.""",
fig=('diag_b', 'assembly_line'),
outs=[dict(t='Test logs: same failure, same shift', lines="""$ grep -H "RESULT" /testlogs/2026-10-01/shift2/*.log
J7K2Q38.log: RESULT PASS
J7K2Q39.log: RESULT {{FAIL}}  nvme: 4 of 8 drives missing (bays 4-7)
J7K2Q40.log: RESULT PASS
J7K2Q41.log: RESULT {{FAIL}}  nvme: 4 of 8 drives missing (bays 4-7)
J7K2Q42.log: RESULT {{FAIL}}  nvme: 4 of 8 drives missing (bays 4-7)""", notes=['Same symptom on three units from one shift: bays 4-7 = one backplane cable, plugged into the wrong connector.']),
      dict(t='Containment: units that passed or are waiting to ship', lines="""$ grep -l "shift2" /travelers/2026-10-01/*.txt | xargs grep -H "STATUS"
J7K2Q38.txt: STATUS {{WAITING TO SHIP}}
J7K2Q40.txt: STATUS {{WAITING TO SHIP}}
J7K2Q44.txt: STATUS IN TEST""", notes=['Inspect these units\' cable too, even though they passed or have not been tested yet.'])])

E[37] = dict(part='Linux in practice', topic='grep across a folder', reread='Module 2: Searching with grep',
q='Write one command that searches every log file under /var/log, including subfolders, for the word nvme, ignoring upper and lower case and showing line numbers. Explain what each option does, and how you would count the matches instead.',
hook='<b>grep -rin</b> = <b>R</b>ecursive, <b>I</b>gnore case, line <b>N</b>umbers. Count: <b>-c</b> or <b>| wc -l</b>.',
ans="""sudo grep -rin "nvme" /var/log/
- -r: recursive: search the folder and every subfolder.
- -i: ignore case: matches nvme, NVMe and NVME.
- -n: show the line number of each match (with -r it also shows the file name).
- "nvme" is the word to find, /var/log/ is where to look. sudo because some logs are readable only by root.
To count instead:
- sudo grep -ric "nvme" /var/log/ : swap -n for -c to get the number of matching lines in each file.
- sudo grep -ri "nvme" /var/log/ | wc -l : one total number for everything.""",
exp="""Each output line looks like file:line-number:the line, so you can open the file at exactly that line. The journal itself is a binary file, so grep finds text logs (messages, dmesg, syslog); for the journal use journalctl | grep -i nvme.""",
fig=('diag_b', 'grep_anatomy'),
outs=[dict(t='List the matches', lines="""$ sudo grep -rin "nvme" /var/log/ | head -3
{{/var/log/messages}}:{{48211}}:Oct  2 03:14:51 srv-r07-u12 kernel: nvme nvme1: I/O 412 QID 9 timeout, aborting
/var/log/messages:48233:Oct  2 03:15:22 srv-r07-u12 kernel: nvme nvme1: controller is down; will reset
/var/log/anaconda/syslog:902:[    3.114] {{NVMe}} drive /dev/nvme0n1 detected""", notes=['file : line number : text. The last match is "NVMe" in capitals, found because of -i.']),
      dict(t='Count them', lines="""$ sudo grep -ric "nvme" /var/log/ | grep -v ":0$"
/var/log/messages:{{57}}
/var/log/anaconda/syslog:{{12}}
/var/log/dmesg:{{9}}
$ sudo grep -ri "nvme" /var/log/ | wc -l
{{78}}""", notes=['Per file with -c (the extra grep hides files with 0), or one total with wc -l.'])])

E[38] = dict(part='Linux in practice', topic='dmesg versus journalctl -b -1', reread='Module 2: Kernel and system logs',
q='A server crashed overnight and rebooted itself. Which one shows you what happened before the crash, dmesg or journalctl -b -1? Explain what each one shows, and what you should save before you reboot a failing server.',
hook='<b>dmesg = whiteboard</b> (wiped every reboot). <b>journalctl -b -1 = notebook</b> (last boot is still there).',
ans="""journalctl -b -1 shows what happened before the crash.
dmesg shows kernel messages from the current boot only. It reads a buffer in memory that is cleared at every reboot, so after the crash and reboot, the messages from before the crash are gone from dmesg.
journalctl reads the systemd journal. -b -1 means the previous boot, so it shows the messages leading up to the crash (add -k for kernel messages only). This only works if the journal is kept on disk (persistent); if it says there is no previous boot, that evidence is lost.
If the journal just stops with no shutdown messages, that points to a sudden power loss or hardware reset, so I also check the BMC event log for the same time.
Before rebooting a failing server, save:
- The kernel messages: dmesg -T > before_reboot.txt
- The journal: journalctl -b > journal_now.txt
- The BMC event log and sensors (ipmitool sel elist, ipmitool sensor).
- A screenshot of the console if it shows an error.
Then copy the files off the server before the reboot.""",
exp="""After a crash, "dmesg" is the most common wrong answer: it looks at the new boot, which is healthy. journalctl --list-boots shows every boot the journal remembers; -1 is the one before this one, -2 the one before that.""",
fig=('diag_b', 'dmesg_journal'),
outs=[dict(t='dmesg starts fresh at the new boot', lines="""$ dmesg -T | head -1
[Fri Oct  2 03:42:10 2026] {{Linux version 5.14.0-427.13.1.el9_4.x86_64}} ...
$ journalctl --list-boots | tail -2
 {{-1}} 6a1f... Thu 2026-10-01 08:02:11 EDT  Fri 2026-10-02 {{03:40:01}} EDT
  0 c93e... Fri 2026-10-02 03:42:10 EDT  Fri 2026-10-02 09:14:02 EDT""", notes=['dmesg begins at 03:42 (the new boot). The previous boot ended at 03:40.']),
      dict(t='The last messages before the crash', lines="""$ journalctl -b -1 -n 3 --no-pager
Oct 02 03:39:58 srv-r07-u12 kernel: {{mce: [Hardware Error]: CPU 12: Machine Check: 0 Bank 7}}
Oct 02 03:39:58 srv-r07-u12 kernel: mce: [Hardware Error]: TSC 0 ADDR 5f2a3240 MISC 8c Uncorrected
Oct 02 03:40:01 srv-r07-u12 kernel: {{Kernel panic - not syncing: Fatal machine check}}""", notes=['An uncorrected machine check (often memory) caused the panic. dmesg could not show you this.'])])

E[39] = dict(part='Linux in practice', topic='IP works but name fails, and the reverse', reread='Module 7: DNS; A server that stops responding',
q='Compare these two cases: (a) ping 10.4.2.15 works but ping db01 fails with “Name or service not known”; (b) ping db01 resolves to 10.4.2.15 but gets no replies. What does each result point to, and what would you check in each case?',
hook='<b>IP works, name fails = DNS.</b> <b>Name works, IP fails = network or target.</b>',
ans="""(a) The IP works, so the network is fine. The problem is name resolution (DNS). Check:
- /etc/resolv.conf: is the right DNS server listed?
- Can I reach that DNS server (ping it)?
- nslookup db01 or dig db01 to ask DNS directly.
- /etc/hosts for a missing or wrong entry.
- Whether I need the full name (FQDN, for example db01.lab.local) or the right search domain.
(b) The name resolved, so DNS is working. The problem is reaching the address, or db01 itself. Check:
- Is 10.4.2.15 still the right address for db01? An old DNS record or hosts entry could point to the wrong place.
- My own side: ip a, ip route, and ping the gateway.
- traceroute 10.4.2.15 to see where the traffic stops.
- Is db01 actually up? Check its console or BMC.
- Is a firewall on db01 or in between blocking ping?""",
exp="""Separate the two jobs: "turn the name into a number" (DNS) and "deliver packets to that number" (the network). Each case tells you which job failed, so you only troubleshoot half the problem.""",
fig=('diag_b', 'two_cases'),
outs=[dict(t='Case (a): the network works, DNS does not', lines="""$ ping -c 1 10.4.2.15
64 bytes from 10.4.2.15: icmp_seq=1 ttl=63 time=0.52 ms
$ ping -c 1 db01
ping: db01: {{Name or service not known}}
$ nslookup db01
;; connection timed out; {{no servers could be reached}}""", notes=['The DNS server itself cannot be reached: check resolv.conf and whether 10.20.5.5 is up.']),
      dict(t='Case (b): DNS works, the path does not', lines="""$ ping -c 3 db01
PING db01.lab.local ({{10.4.2.15}}) 56(84) bytes of data.
--- db01.lab.local ping statistics ---
3 packets transmitted, 0 received, {{100% packet loss}}
$ traceroute -n 10.4.2.15
 1  10.20.4.1  0.41 ms  0.38 ms  0.36 ms
 2  {{* * *}}""", notes=['The name resolved, but packets stop after the gateway: a routing or firewall problem, or db01 is down.'])])

E[40] = dict(part='Linux in practice', topic='Saving evidence before a reboot', reread='Module 2: Kernel and system logs; Module 8',
q='A failing server must be power cycled in ten minutes. Write the commands you would run first to save the evidence to files, and explain what each file would show an engineer later.',
hook='Save before you reboot: <b>Kernel, Journal, BMC, Hardware</b>. Name files with the serial, <b>copy them off</b>.',
ans="""Commands (name each file with the unit serial):
1. dmesg -T > unit123_dmesg.txt
Kernel messages from this boot, with readable times: hardware errors, driver problems, PCIe and memory errors. Lost at the reboot.
2. journalctl -b > unit123_journal.txt
Everything logged this boot (kernel and services), to see what happened and in what order.
3. journalctl -b -1 > unit123_prevboot.txt
The boot before, if the problem started then.
4. sudo ipmitool sel elist > unit123_sel.txt
The BMC event log: memory, PCIe, power, fan and temperature events with times.
5. sudo ipmitool sensor > unit123_sensors.txt
Temperatures, fan speeds, PSU status and voltages at the moment of failure.
6. sudo lspci -vv > unit123_lspci.txt
Every PCIe device and its link status: which devices were present and how they trained.
7. sudo dmidecode > unit123_dmidecode.txt
Serial numbers, BIOS version and the DIMM in each slot.
8. ip a > unit123_ip.txt (and nvidia-smi -q > unit123_gpu.txt on a GPU server)
Network and GPU state.
Then copy the files off the server before the power cycle, for example scp unit123_* tech@10.1.1.50:/evidence/, and note the time and what was seen on the console.""",
exp="""A power cycle wipes the dmesg buffer, the live sensor readings and the current state of every device. If you do not save them, the engineer gets a server that "works fine now" and no way to find the cause.
Ten minutes is plenty: each command takes seconds. Copying the files off the server matters because if the disk is part of the problem, files saved only on it may be lost too.""",
fig=('diag_b', 'evidence_bundle'),
outs=[dict(t='Saving everything (seconds each)', lines="""$ dmesg -T > unit123_dmesg.txt
$ journalctl -b > unit123_journal.txt
$ sudo ipmitool sel elist > unit123_sel.txt
$ sudo ipmitool sensor > unit123_sensors.txt
$ sudo lspci -vv > unit123_lspci.txt
$ sudo dmidecode > unit123_dmidecode.txt
$ ls -lh unit123_*
-rw-r--r--. 1 tech tech  88K Oct  2 09:21 unit123_dmesg.txt
-rw-r--r--. 1 tech tech 4.1M Oct  2 09:21 unit123_journal.txt
-rw-r--r--. 1 tech tech  12K Oct  2 09:21 unit123_sel.txt
-rw-r--r--. 1 tech tech 9.6K Oct  2 09:21 unit123_sensors.txt""", notes=['Each file is a snapshot of one kind of evidence.']),
      dict(t='Copy it off the server', lines="""$ scp unit123_* tech@10.1.1.50:/evidence/J7K2Q41/
unit123_dmesg.txt                     100%   88KB  31.2MB/s   00:00
unit123_journal.txt                   100% 4196KB 101.4MB/s   00:00
...""", notes=['Now the evidence survives even if the server never comes back.'])])
