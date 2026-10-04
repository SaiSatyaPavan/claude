from content_a import E

E[11] = dict(part='Troubleshooting', topic='Isolation techniques', reread='Module 10: Isolation techniques',
q='Describe four techniques for proving which hardware part is causing a failure. For each, explain what result would convince you, and one risk or limitation.',
hook='Four ways to catch the bad part: <b>Swap, Strip, Split, Compare</b>.',
ans="""1. Swap with known-good: move the suspect part to a known-good slot or system, or put a known-good part in the suspect location.
Convinced when: the failure follows the part to its new place (the part is bad), or stays with the slot when a good part is there (the slot, cable or board is bad), and it repeats.
Risk: a bad slot or a power problem can damage the good part you put in. Inspect the slot first.
2. Minimum configuration: strip the server to the minimum (one CPU, one DIMM, no cards), then add parts back one at a time.
Convinced when: it works at minimum and fails the moment one particular part is added back.
Limit: slow, and a fault that only shows under full load may not appear with a minimal setup.
3. Half-splitting: split the possible causes into two halves and test which half has the problem; keep splitting.
Convinced when: the fault stays inside one half every time you split, down to one part.
Limit: you need parts you can test separately; it is hard when everything depends on everything.
4. Compare with a golden unit: compare the failing unit with a known-good identical unit: logs, firmware versions, BIOS settings, cabling, test results.
Convinced when: you find the one difference, and changing it on the failing unit fixes it.
Limit: the golden unit must really be identical and really good.
In all four, change only one thing at a time and document each result.""",
exp="""All four techniques do the same thing: they change one thing on purpose and watch what happens. "Follows the part" and "stays with the slot" are the two answers a swap can give you.
Say the risk in your answer. Graders like to see that you know a swap can kill a good part, and that a golden unit is only useful if it truly matches.""",
fig=('diag_a2', 'four_isolation'),
outs=[dict(t='Golden unit comparison finds the difference', lines="""$ diff golden_unit_versions.txt J7K2Q41_versions.txt
3c3
< BIOS Version : {{2.4b}}
---
> BIOS Version : {{2.1}}
7c7
< NIC FW       : 22.36.1010
---
> NIC FW       : 22.31.1014""", notes=['Lines with <b>&lt;</b> are the golden unit, <b>&gt;</b> the failing one. Two differences: update one, retest, then the other.']),
      dict(t='Swap log: does the fault follow the part?', lines="""$ cat swap_log.txt
GPU SN ...4417 in slot 3  ->  {{FAIL}}  (Xid 79)
GPU SN ...4417 in slot 5  ->  {{FAIL}}  (Xid 79)   <- moved the GPU
GPU SN ...8810 in slot 3  ->  PASS            <- known-good GPU in slot 3""", notes=['The fault followed GPU ...4417 to slot 5, and slot 3 passes with a good GPU: the GPU is bad.'])])

E[12] = dict(part='Troubleshooting', topic='Slow NVMe drive', reread='Module 6: A drive that is slower than it should be',
q='Two identical NVMe drives in the same server are tested the same way. One reaches its rated speed; the other gets about half. List the possible causes and how you would check each one.',
hook='Half speed? Check <b>Link, Path, Heat, Firmware, Format, Test, Health</b>. Then <b>swap bays</b>.',
ans="""1. Downtrained link: the slow drive may have trained at x2 or Gen 3 instead of Gen 4 x4. Check sudo lspci -vv on both drives and compare LnkSta with LnkCap. Half the lanes = about half the speed.
2. A different path: the slow drive may share a PCIe switch uplink with other busy devices, or sit behind the other CPU. Check lspci -tv against the topology diagram.
3. Heat: the drive may be throttling because its bay is hot. Check nvme smart-log for temperature and thermal throttling counts, and the BMC sensors.
4. Different firmware: check nvme list; the firmware version should match.
5. Drive state or format: a nearly full drive, a different sector format (nvme id-ns), or one that was never trimmed is slower. Check usage and format.
6. The test is not really the same: wrong device, different queue depth or block size, or another program using the drive. Re-run the identical fio command on both.
7. Signal problems or a failing drive: check dmesg for AER errors and nvme smart-log for media errors and warnings.
Then isolate: swap the two drives between bays. If the slowness follows the drive, it is the drive; if it stays with the bay, it is the bay, backplane, cable or path. Change one thing at a time and document.""",
exp="""Two identical drives should give identical results. So the job is to find what is different: the link, the path, the temperature, the firmware, or the test.
Start with checks that change nothing (read LnkSta, temperatures, firmware) before you move hardware. Then the bay swap tells you whether to blame the drive or the slot it sits in.""",
fig=('diag_a2', 'nvme_half'),
outs=[dict(t='Same test, different results', lines="""$ sudo fio --name=t --filename=/dev/nvme0n1 --rw=read --bs=128k --iodepth=32 --direct=1 --runtime=60 | grep READ:
   READ: bw={{6812MiB/s}} (7143MB/s), io=399GiB, run=60001msec
$ sudo fio --name=t --filename=/dev/nvme1n1 --rw=read --bs=128k --iodepth=32 --direct=1 --runtime=60 | grep READ:
   READ: bw={{3321MiB/s}} (3482MB/s), io=195GiB, run=60001msec""", notes=['nvme1 gets about half of nvme0, with the identical command.']),
      dict(t='Link, firmware and heat', lines="""$ sudo lspci -vv -s 5e:00.0 | grep LnkSta: ; sudo lspci -vv -s 5f:00.0 | grep LnkSta:
        LnkSta: Speed 16GT/s, Width x4
        LnkSta: Speed 16GT/s, Width x4
$ sudo nvme list | awk '{print $1, $NF}'
/dev/nvme0n1 GDC5602Q
/dev/nvme1n1 GDC5602Q
$ sudo nvme smart-log /dev/nvme1 | grep -i -E "^temperature|T1 Trans"
temperature                             : {{79 C}} (352 Kelvin)
Thermal Management T1 Trans Count       : {{118}}""", notes=['Both links are Gen 4 x4 and firmware matches, so those are ruled out.', '<b>79 C</b> and <b>118</b> throttling events: the drive slows itself down to cool off. Check that bay\'s airflow.'])])

E[13] = dict(part='Troubleshooting', topic='Failure follows the part', reread='Module 10: Isolation techniques',
q='You move a suspect GPU from Server A into known-good Server B, and Server B now fails the same way. What does this prove, what does it not prove, and what do you do next with both servers and the GPU?',
hook='<b>Follows the part = bad part.</b> But it does <b>not</b> prove Server A is OK.',
ans="""What it proves: the GPU is very likely bad, because the failure moved with it into a system that was working.
What it does not prove: that Server A is healthy. A bad slot or a power problem in Server A could have damaged the GPU in the first place, and it could damage the next good GPU too.
Next steps:
1. Tag the GPU as bad and quarantine it, so nobody reuses it.
2. Put Server B back to its original state (its own good GPU) and retest it, to make sure it still passes.
3. Inspect Server A's slot (bent pins, damage, burn marks) and the GPU power cable, then test Server A with a known-good GPU.
4. Document the serial numbers of both servers and the GPU, the slots, and every test result.
5. Start the RMA for the GPU, with failure analysis (FA) if needed.""",
exp="""A swap answers one question: "Is it the part?" It does not answer "Why did the part fail?" If Server A's slot fried the GPU, putting a new GPU into Server A just fries another one.
So you finish the job on both sides: prove Server B is still good, and prove Server A is safe for a new part.""",
fig=('diag_a3', 'follows_part'),
outs=[dict(t='In Server B: the same error, from the same GPU', lines="""$ nvidia-smi -q | grep -E "Serial Number|Bus Id"
    Serial Number                         : {{1652322004417}}
    Bus Id                                : 00000000:3D:00.0
$ dmesg -T | grep -i xid
[Fri Oct  2 11:05:43 2026] NVRM: Xid (PCI:0000:3d:00): {{79}}, pid=0, GPU has fallen off the bus.""", notes=['Serial ...4417 is the GPU that came from Server A, and it shows the same Xid 79 in Server B.']),
      dict(t='Record both servers', lines="""$ sudo dmidecode -s system-serial-number     # on Server A, then Server B
{{S421A0991}}
{{S421A1047}}""", notes=['The repair record needs all three serials: Server A, Server B and the GPU.'])])

E[14] = dict(part='Troubleshooting', topic='ip a shows 169.254', reread='Module 7: The basics; Reading ip a; DHCP',
q='Here is part of the ip a output from a server that cannot reach anything on the network. What does it tell you, what is most likely wrong, and what would you check next?',
code="""3: ens2f1: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 9000 qdisc mq state UP
    link/ether b8:ce:f6:4a:10:22 brd ff:ff:ff:ff:ff:ff
    inet 169.254.88.4/16 brd 169.254.255.255 scope link ens2f1""",
hook='<b>169.254 = "I asked DHCP and nobody answered."</b> The link is fine; the path to DHCP is not.',
ans="""What it tells me:
- Interface ens2f1 is UP and LOWER_UP, so the NIC is enabled and has a physical link. The cable and switch port pass a link.
- MTU 9000 (jumbo frames). MAC address b8:ce:f6:4a:10:22.
- The address 169.254.88.4/16 with "scope link" is a self-assigned link-local address. There is no "dynamic".
Most likely wrong: DHCP failed. The server asked for an address and no DHCP server answered, so it gave itself one. With a 169.254 address it cannot reach anything beyond its own link, and there is no default gateway.
What I would check next:
1. The switch port VLAN: if the port is on the wrong VLAN, there is no DHCP server there to answer.
2. The DHCP server: is it up, and does it have a free address or a reservation for this MAC?
3. The DHCP relay on the router, if the DHCP server is on another subnet.
4. The cable is in the right port. On a dual-port card the other port may be the one that is configured.
5. MTU 9000 matches the switch.
6. Then renew (for example sudo dhclient -v ens2f1, or restart the connection in NetworkManager) and confirm a real address with "dynamic", a default route in ip route, and DNS. Document the fix.""",
exp="""Read it from the bottom of the stack up: the link is good (LOWER_UP), so the cable and NIC are not the problem. The address is the clue: 169.254.x.x only appears when DHCP got no answer.
So the fault is between the server and the DHCP server: usually the VLAN on the switch port, a down DHCP server, or a missing relay.""",
fig=('diag_a3', 'vlan_dhcp'),
outs=[dict(t='No gateway, and DHCP gets no offers', lines="""$ ip route
169.254.0.0/16 dev ens2f1 proto kernel scope link src 169.254.88.4
{{(no "default via ..." line: no gateway)}}
$ sudo dhclient -v ens2f1
DHCPDISCOVER on ens2f1 to 255.255.255.255 port 67 interval 4
DHCPDISCOVER on ens2f1 to 255.255.255.255 port 67 interval 9
{{No DHCPOFFERS received.}}""", notes=['The server keeps asking; nobody answers. Look at the VLAN and the DHCP server next.']),
      dict(t='The link itself is fine', lines="""$ ethtool ens2f1 | grep -E "Speed|Link detected"
        Speed: 25000Mb/s
        {{Link detected: yes}}""", notes=['Physical layer OK, so do not swap the cable or the card yet.'])])

E[15] = dict(part='Troubleshooting', topic='Memory: DIMM, board, CPU, or configuration', reread='Module 5: Is it the DIMM or the system?',
q='After a memory upgrade, a server shows less memory than installed and logs corrected errors on two different channels. How would you decide whether the cause is the new DIMMs, the slots or motherboard, the CPU, or how the memory was installed and configured?',
hook='Map it first: <b>which slots, which channels, which DIMMs are new</b>. Then: <b>Install, DIMM, Slot, CPU</b>.',
ans="""1. Record the evidence: free -h (how much is missing), dmidecode -t memory (which slots are filled, sizes, serials, "No Module Installed"), and the errors from the BMC SEL and ras-mc-ctl --summary (which slots and channels).
2. Check the installation and configuration first (most likely after an upgrade):
- Every new DIMM fully seated with both latches closed.
- The slots follow the population rules in the service guide.
- The new DIMMs match the old ones (same type: RDIMM, DDR5; supported part; same speed and size where required).
- The BIOS is current enough to support the new DIMMs, no DIMMs are disabled in the BIOS, and the memory mode is right (mirroring or sparing hide memory).
3. Look at the pattern:
- Errors only on the new DIMMs (on both channels) points to the new DIMMs or how they were installed.
- Errors on many channels of one CPU points to the CPU (seating, bent socket pins, memory controller).
4. Swap test, one change at a time: move a suspect new DIMM to a slot on another channel, and put a known-good DIMM in its slot. Clear the logs and run a memory test.
- Errors follow the DIMM: the DIMM is bad.
- Errors stay with the slot: the slot or motherboard.
5. If it points to the CPU: reseat it and check the socket pins, then try a known-good CPU.
6. Verify the full amount shows, run a stress test, and document slots, serials and results.""",
exp="""After an upgrade, start with what changed: the new DIMMs and how they went in. Most problems are a DIMM not fully latched, a DIMM in the wrong slot, or parts that should not be mixed.
The trick is to turn "errors on two channels" into a map. If both channels with errors are exactly the slots that got new DIMMs, suspect those DIMMs. If the errors stay with a slot after a swap, suspect the board. If they spread across one CPU, suspect that CPU.""",
fig=('diag_a3', 'mem_upgrade'),
outs=[dict(t='Less memory: one new DIMM is not seen', lines="""$ free -h | head -2
               total        used        free      shared  buff/cache   available
Mem:           {{944Gi}}        61Gi       871Gi       2.1Gi        14Gi       877Gi
$ sudo dmidecode -t memory | grep -E "Locator: DIMM_[GH]2|Size" | tail -4
        Size: 64 GB
        Locator: DIMM_G2
        Size: {{No Module Installed}}
        Locator: {{DIMM_H2}}""", notes=['16 x 64 GB were installed, but H2 is not detected: one DIMM missing. Reseat it (latches!) before anything else.']),
      dict(t='Corrected errors on two channels', lines="""$ sudo ras-mc-ctl --summary
Memory controller events summary:
        Corrected on DIMM Label(s): 'CPU_SrcID#0_MC#1_Chan#0_{{DIMM#1}}' location: 1:0:1:-1 errors: {{212}}
        Corrected on DIMM Label(s): 'CPU_SrcID#0_MC#2_Chan#1_{{DIMM#1}}' location: 2:1:1:-1 errors: {{87}}""", notes=['Both errors are on <b>DIMM#1</b> (the second slot of a channel), which is where the new DIMMs went. Suspect the new DIMMs or their installation, then prove it with a swap.'])])

E[16] = dict(part='Troubleshooting', topic='Replacement did not fix it', reread='Module 10: When a replacement does not fix it',
q='A GPU kept failing its stress test, so it was replaced. The new GPU fails the same test, the same way, in the same slot. What does this suggest, and what should happen next instead of replacing another part?',
hook='<b>New part, same failure, same slot = not the part.</b> Stop swapping; start measuring.',
ans="""What it suggests: the GPU was probably never the cause. Two different GPUs failing the same way in the same slot point to something that slot shares:
- the slot itself, the riser or the PCIe cable to it,
- the GPU's auxiliary power cable or the PSU feeding it,
- a retimer on that path,
- cooling for that slot (airflow, a missing baffle or blank, a failed fan),
- BIOS, firmware or driver settings,
- or the test itself.
The first GPU may be good, so do not send it for RMA yet.
What should happen next (instead of another part):
1. Stop replacing parts and collect data: the exact error (for example Xid 79, AER errors), temperatures and power during the test, the BMC SEL, and firmware and driver versions.
2. Compare with a golden unit running the same test.
3. Test the slot: put a known-good GPU from a passing server into this slot, and put this GPU into a known-good slot. One change at a time.
4. Inspect the slot path: riser seating, cables, power cable, airflow parts.
5. Retest the first GPU in a good system; if it passes, return it to stock.
6. If still unclear, escalate with the data. Document everything, including that the replacement did not fix it.""",
exp="""Replacing parts until the problem goes away is called "shotgunning" or using the "parts cannon". It wastes good parts and often never finds the real cause.
When a brand-new part fails exactly like the old one, the evidence is telling you the problem is around the part, not in it. That is the moment to stop and measure.""",
fig=('diag_a3', 'same_slot'),
outs=[dict(t='Two GPUs, same slot, same error', lines="""$ journalctl -k | grep -i xid
Oct 01 14:22:10 srv-r07-u12 kernel: NVRM: Xid (PCI:{{0000:3d:00}}): 79, pid=0, GPU has fallen off the bus.
Oct 02 11:05:43 srv-r07-u12 kernel: NVRM: Xid (PCI:{{0000:3d:00}}): 79, pid=0, GPU has fallen off the bus.
$ nvidia-smi -q -i 3 | grep "Serial Number"      # before and after the swap
    Serial Number                         : {{1652322004417}}
    Serial Number                         : {{1652322009902}}""", notes=['Same PCI address (the same slot) both days, but two different serial numbers. The common factor is the slot.']),
      dict(t='A clue from the BMC', lines="""$ sudo ipmitool sensor | grep -i -E "GPU[0-9] Temp"
GPU2 Temp        | 66.000     | degrees C  | ok
GPU3 Temp        | {{91.000}}     | degrees C  | {{cr}}
GPU4 Temp        | 64.000     | degrees C  | ok""", notes=['Slot 3 runs 25 degrees hotter than its neighbors: check that slot\'s airflow (baffle, blank, fan) before touching the GPU again.'])])

E[17] = dict(part='Linux in practice', topic='Filtering large logs', reread='Module 2: Finding one event in a large log',
q='The journal on a busy server has hundreds of thousands of lines. Write commands to (a) show only error-level messages from the current boot, (b) show everything logged from 9:00 to 9:15 this morning, and (c) find which error message repeats most often. Explain each part.',
hook='<b>-b</b> this boot, <b>-p err</b> errors, <b>--since/--until</b> a time window, <b>sort | uniq -c | sort -rn</b> top repeats.',
ans="""(a) Errors from the current boot only:
`journalctl -b -p err`
-b = this boot only. -p err = priority "err" and worse (crit, alert, emerg). Add -k for kernel messages only.
(b) Everything from 9:00 to 9:15 this morning:
`journalctl --since "09:00" --until "09:15"`
A time with no date means today. This lines the logs up with the time the problem happened.
(c) Which error repeats most often:
`journalctl -b -p err -o cat | sort | uniq -c | sort -rn | head`
- -o cat prints only the message text, without the time and host, so identical messages look identical.
- sort puts identical lines next to each other.
- uniq -c counts each group of identical lines.
- sort -rn sorts by that count, biggest first (r = reverse, n = numeric).
- head shows the top 10.
To save the result as evidence, add > errors_top.txt.""",
exp="""Each option throws away lines you do not need. Start wide, then narrow: this boot, then errors only, then count. A time window is the other way to narrow: if users say "it broke at 9:05", look at 9:00 to 9:15.
The pipe trick in (c) works with any command that prints lines, not just journalctl.""",
fig=('diag_a3', 'journal_funnel'),
outs=[dict(t='(a) Errors from this boot', lines="""$ journalctl -b -p err
Oct 02 08:05:51 srv-r07-u12 kernel: nvme nvme1: controller is down; will reset: CSTS=0xffffffff
Oct 02 09:07:13 srv-r07-u12 systemd[1]: {{data-sync.service: Failed with result 'exit-code'.}}
Oct 02 09:07:43 srv-r07-u12 systemd[1]: data-sync.service: Failed with result 'exit-code'.""", notes=['Only error-level lines from the current boot.']),
      dict(t='(b) A 15-minute window', lines="""$ journalctl --since "09:00" --until "09:15"
Oct 02 09:00:01 srv-r07-u12 CROND[44120]: (root) CMD (/usr/local/bin/backup.sh)
Oct 02 09:06:58 srv-r07-u12 kernel: nvme nvme1: I/O 412 QID 9 {{timeout, aborting}}
Oct 02 09:07:13 srv-r07-u12 systemd[1]: data-sync.service: Failed with result 'exit-code'.""", notes=['Everything at every level, but only from 09:00 to 09:15. Here a backup starts, the NVMe drive times out, and the sync job fails.']),
      dict(t='(c) The most repeated error', lines="""$ journalctl -b -p err -o cat | sort | uniq -c | sort -rn | head -3
    {{912}} data-sync.service: Failed with result 'exit-code'.
     36 nvme nvme1: controller is down; will reset: CSTS=0xffffffff
      4 mce: [Hardware Error]: Machine check events logged""", notes=['The first column is the count. The sync job failed 912 times, probably because of the NVMe drive below it.'])])

E[18] = dict(part='Linux in practice', topic='Network card checks by command', reread='Module 3: The four layers; Module 7: Reading ip a',
q='A new network card was installed. Write the Linux commands you would run, in order, to confirm the system found it, a driver is attached, it has a link, and it has an address. Say what each output tells you.',
hook='Four steps up: <b>Found (lspci), Driver (lspci -k), Link (ethtool), Address (ip a)</b>.',
ans="""1. Found it? `lspci | grep -i ethernet`
Shows the card on the PCIe bus, with its address (for example 3b:00.0 and 3b:00.1 for two ports). If it is not here, it is a physical, BIOS or slot problem.
2. Driver attached? `lspci -k -s 3b:00.0` and `dmesg | grep -i mlx5`
lspci -k must show "Kernel driver in use: mlx5_core". dmesg shows the driver loading, the firmware version and the interface name. No driver line = a driver problem, not a bad card.
3. Link? `ip link show ens3f0` and `ethtool ens3f0`
ip link shows UP and LOWER_UP (link) or NO-CARRIER (no link). ethtool shows "Link detected: yes" and the speed (for example 100000Mb/s). No link = cable, transceiver, dirty fiber or switch port.
4. Address? `ip a show ens3f0` and `ip route`
ip a shows the inet line with the IP and mask, and "dynamic" if it came from DHCP (169.254 = DHCP failed). ip route shows the default gateway.
Finally: `ping -c 3 10.20.5.1` (the gateway) to prove it can talk.""",
exp="""This is the four-layer check done with commands: bus, driver, link, address. Go in order, because each step depends on the one before. A card with no driver can never have a link, and a port with no link can never get an address.
Write the exact command and say what a good result looks like. That is what "command questions" are graded on.""",
fig=('diag_a3', 'nic_ladder'),
outs=[dict(t='Steps 1 and 2: found, with a driver', lines="""$ lspci | grep -i ethernet
{{3b:00.0}} Ethernet controller: Mellanox Technologies MT2892 Family [ConnectX-6 Dx]
3b:00.1 Ethernet controller: Mellanox Technologies MT2892 Family [ConnectX-6 Dx]
$ lspci -k -s 3b:00.0
3b:00.0 Ethernet controller: Mellanox Technologies MT2892 Family [ConnectX-6 Dx]
        Subsystem: Mellanox Technologies Device 0016
        {{Kernel driver in use: mlx5_core}}
$ dmesg | grep -i mlx5 | tail -2
[    8.402117] mlx5_core 0000:3b:00.0: firmware version: 22.36.1010
[    9.115230] mlx5_core 0000:3b:00.0 {{ens3f0}}: renamed from eth0""", notes=['Two ports (.0 and .1). The driver is mlx5_core, and the first port became <b>ens3f0</b>.']),
      dict(t='Steps 3 and 4: link and address', lines="""$ ethtool ens3f0 | grep -E "Speed|Link detected"
        Speed: {{100000Mb/s}}
        {{Link detected: yes}}
$ ip a show ens3f0 | grep inet
    inet {{10.20.5.31/24}} brd 10.20.5.255 scope global {{dynamic}} ens3f0
$ ip route | grep default
default via 10.20.5.1 dev ens3f0 proto dhcp""", notes=['100G link up, a DHCP address and a default gateway. Last check: ping the gateway.'])])

E[19] = dict(part='Linux in practice', topic='First commands on an unknown server', reread='Module 2; Module 3; Command Quick Reference',
q='You log in to a server you have never seen before to look for a hardware problem. Write the commands you would run in your first few minutes, in a sensible order, and what each one tells you.',
hook='<b>Who am I on? What hardware? What is wrong now? What did the BMC see? How is it connected?</b> Look before you touch.',
ans="""1. Where am I?
- `hostname` and `cat /etc/os-release`: which server and which Linux version.
- `uptime`: how long since the last reboot, and the load. A recent reboot may mean a crash.
2. What hardware does it have?
- `lscpu`: CPUs, sockets and cores.
- `free -h`: total memory (is it what it should be?).
- `lsblk` and `nvme list`: drives and their sizes.
- `lspci` (and `lspci -k`): every PCIe device and its driver. Compare with the build sheet.
3. What is going wrong now?
- `dmesg -T --level=err,warn | tail -50`: recent kernel errors and warnings, with readable times.
- `journalctl -p err -b`: errors from this boot.
- `journalctl --list-boots` and `journalctl -b -1`: earlier boots, and the boot before a crash.
4. What did the hardware log?
- `sudo ipmitool sel elist`: the BMC event log (memory, PCIe, power, temperature events).
- `sudo ipmitool sensor`: temperatures, fans, PSUs and voltages right now.
5. How is it connected?
- `ip a` and `ip route`: interfaces, addresses and the gateway.
Save what I find to files (for example dmesg -T > unit123_dmesg.txt) and change nothing until I understand it.""",
exp="""The order goes from general to specific: identify the machine, list what is in it, then look for errors in the OS logs and in the BMC. Reading changes nothing, so it is always safe to do first.
On an unknown server, compare what you see with what should be there: missing memory, a missing card or a missing drive is often the whole answer.""",
fig=('diag_a3', 'first_commands'),
outs=[dict(t='Who and what', lines="""$ hostname; grep PRETTY /etc/os-release; uptime
srv-r07-u12
PRETTY_NAME="Rocky Linux 9.4 (Blue Onyx)"
 09:14:02 up {{0 days,  0:41}},  1 user,  load average: 0.42, 0.51, 0.48
$ lscpu | grep -E "^Socket|^CPU\\(s\\)"; free -h | grep Mem
CPU(s):                  128
Socket(s):               2
Mem:           {{944Gi}}        12Gi       925Gi       1.1Gi       7.2Gi       931Gi""", notes=['Up only 41 minutes: it rebooted recently (crash?). 944 GiB looks short for a 1 TB build: one more clue.']),
      dict(t='Errors in the OS and in the BMC', lines="""$ dmesg -T --level=err,warn | tail -2
[Fri Oct  2 08:33:12 2026] {{EDAC MC1: 87 CE memory read error}} on CPU_SrcID#0_MC#1_Chan#0_DIMM#1
[Fri Oct  2 08:33:40 2026] mce: [Hardware Error]: Machine check events logged
$ sudo ipmitool sel elist | tail -2
  71 | 10/02/2026 | 08:31:55 | Memory DIMM_E2 | Correctable ECC | Asserted
  72 | 10/02/2026 | 08:31:56 | System Event | {{OEM System boot event}} | Asserted""", notes=['Memory errors in Linux and in the BMC, plus a reboot at 08:31: start with memory (Module 5).'])])

E[20] = dict(part='Linux in practice', topic='Slow server: processes and load', reread='Module 2: Processes and system load',
q='Users report that a server has become slow. Write the commands you would use to find which processes use the most CPU and memory, compare the load with the number of cores, and tell whether CPU, memory, or storage is the bottleneck. Explain how to read the key numbers.',
hook='Compare <b>load average to cores</b>. Then look at <b>%us, %wa, available, swap</b>. Busy CPU, short memory, or waiting disk?',
ans="""Find the busy processes:
- `top` (press P to sort by CPU, M by memory): live view of the busiest processes.
- `ps aux --sort=-%cpu | head` and `ps aux --sort=-%mem | head`: the top processes by CPU and by memory.
Compare load with cores:
- `uptime` shows the load average for 1, 5 and 15 minutes. `nproc` shows the number of CPU cores.
- If the load is higher than the number of cores, work is waiting for CPU. Load 62 on 32 cores means about twice as much work as the CPUs can do.
Find the bottleneck:
- CPU: in top, %us (user) and %sy (system) are high and %id (idle) is near 0, while %wa is low.
- Memory: `free -h` shows "available" near zero, swap is being used, and `vmstat 1` shows si/so (swap in/out) above 0 every second. The server is swapping, which is very slow.
- Storage: in top, %wa (iowait) is high: the CPU is waiting for disk. `iostat -x 1` shows a disk near 100 %util with high await (milliseconds per request).
Then look at the process using that resource, and compare with normal behavior or a golden unit before changing anything.""",
exp="""Load average is the number of tasks running or waiting. Compare it to the number of cores: on 32 cores, a load of 32 means "fully busy", 64 means "a queue as long as the work".
The three key questions: are the CPUs busy (%us)? Is memory full and swapping (available, si/so)? Is the CPU waiting for disks (%wa, %util)? Only one of them is usually the main bottleneck.""",
fig=('diag_a3', 'slow_server'),
outs=[dict(t='Load versus cores', lines="""$ uptime
 14:02:11 up 41 days,  3:12,  2 users,  load average: {{62.14}}, 58.90, 41.22
$ nproc
{{32}}""", notes=['Load 62 on 32 cores: about twice as much work as the CPUs can handle.']),
      dict(t='top: who is using it, and which resource', lines="""$ top -b -n 1 | head -9
top - 14:02:12 up 41 days,  3:12,  2 users,  load average: 62.14, 58.90, 41.22
Tasks: 612 total,  59 running, 553 sleeping,   0 stopped,   0 zombie
%Cpu(s): {{95.1 us}},  3.2 sy,  0.0 ni,  {{1.2 id}},  {{0.3 wa}},  0.0 hi,  0.2 si,  0.0 st
MiB Mem : 257612.4 total,  41250.1 free, 190112.7 used,  26249.6 buff/cache
MiB Swap:   8192.0 total,   8192.0 free,      {{0.0 used}}.  64188.3 avail Mem

    PID USER      PR  NI    VIRT    RES    SHR S  %CPU  %MEM     TIME+ COMMAND
  48211 app       20   0   92.1g  61.3g  12.1g R  {{2890}}  24.3  812:44.10 {{java}}
  50112 etl       20   0   12.4g   8.1g   1.2g R   201   3.2   41:02.33 python3""", notes=['<b>95% us, 1% idle, 0.3% wa</b>: the CPUs are full; disks are not the problem.', '<b>Swap 0 used</b>, 64 GB available: memory is fine.', 'One java process uses 2890% CPU (about 29 cores). <b>Bottleneck: CPU</b>, caused by that process.']),
      dict(t='If it were storage instead', lines="""$ iostat -x 1 1 | grep -E "Device|nvme0n1"
Device   r/s     w/s    rkB/s    wkB/s  r_await  w_await  aqu-sz  %util
nvme0n1  412.0  9120.0  52736.0  1167360.0   1.21   {{48.30}}   441.2  {{99.8}}""", notes=['A disk at <b>99.8% util</b> with 48 ms per write: storage is the bottleneck in that case (and top would show high %wa).'])])
