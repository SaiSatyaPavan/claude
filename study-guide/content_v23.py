# Updates that align the answers with Prep Course v2.3 (the course the new practice exam is based on).
from content_b import E

E[1].update(
ans="""A server is a computer whose job is to provide a service to other computers (clients) over the network. When your laptop opens a website, loads email or saves a file to a shared drive, a server in a data center does the work.
Three jobs servers do:
1. Applications and websites: run the apps and sites that employees and customers use.
2. Databases, files and storage: store orders, inventory and customer records; shared files, backups and email.
3. AI and high-performance computing: GPU servers that train and run AI models, often hundreds working together.
(Others: directory and login services that decide who can access what, and virtual machines: one physical server split into many virtual servers.)
How those jobs shape the server:
- Many people and systems depend on each server, so one failure can stop a whole department or a customer's service. It is built for reliability: redundancy (two power supplies, many fans), ECC memory, and hot-swap parts that can be replaced while it runs.
- It runs all day with no one in front of it, so it has remote management: a BMC, SSH and scripts. One tech can manage hundreds.
- It lives in a rack, measured in rack units (1U = 1.75 inches), with no keyboard or monitor.
- Because so much depends on it, careful diagnosis and documentation matter on every repair.
A desktop is used by one person in office hours. If it breaks, one person waits.""")

E[2].update(
ans="""What it connects: PCIe (PCI Express) is the main high-speed connection inside a server. It links the CPUs to almost everything that moves data quickly: GPUs, network cards, NVMe drives, RAID and storage controllers, and DPUs. Each PCIe link is a private, point-to-point connection, so devices do not wait for each other on the same wires (unlike older shared buses).
Why lanes: a link is built from lanes (x1, x4, x8, x16). Each lane sends and receives at the same time. More lanes carry more data in parallel, like more lanes on a highway, so each link can be sized to what its device needs. Each new generation doubles the speed per lane (Gen 4 = 16 GT/s, Gen 5 = 32 GT/s).
How each device depends on it:
- GPU (usually x16): every piece of AI data goes into and out of GPU memory over PCIe. A slow or broken link means slow training or a missing GPU.
- Network card (x8 or x16): every network packet crosses PCIe between the NIC and the CPU. A 100G or 400G port needs a wide, fast link to reach full speed.
- NVMe drive (x4): the drive talks to the CPU directly over PCIe, with no SATA controller in between. That is why it is fast, and why PCIe problems make drives drop out or slow down.""")

E[5].update(
hook='ESD does 3 things: <b>kills now, kills later, confuses you</b>. Prevent: <b>tested Strap, Mat, Edges, Silver bags</b>.',
ans="""ESD (electrostatic discharge) is static electricity jumping from you to a part. You cannot feel a discharge below about 3,000 volts, but some chips are damaged by less than 100 volts.
Three ways it harms a part:
1. Immediate failure: the part is dead, or behaves erratically, right away. It may not be detected, or it fails its first test.
2. Latent damage (shows up weeks later): the part is weakened but passes every test. Weeks later it fails, or it fails only now and then. This is the most expensive kind, because it is hard to trace and often fails at the customer.
3. Wasted time: a damaged part creates confusing symptoms (random errors, a link that drops) that send troubleshooting in the wrong direction.
Precautions:
- Wear a grounded wrist strap, and test it.
- Work on a grounded mat.
- Hold parts by the edges; never touch contacts or chips.
- Keep parts in shielding bags (the silver ones) until you install them.
- Handle parts with the server powered off.""",
exp="""Static builds up on you when you walk or move, and it jumps to the first metal it finds. A modern chip has tiny parts that a small zap can burn or weaken, far below what you can feel.
The expensive one is <b>latent</b> damage: the unit passes test and ships, then fails weeks later, or only now and then, at the customer. Nobody can trace it back to the missing wrist strap, and the confusing symptoms waste hours of troubleshooting.""")

E[6].update(
hook='POST = the server\'s <b>morning check-up</b>: <b>CPUs, Memory, PCIe, Controllers, Fans/Power</b>, then boot. Memory training is the long part.',
ans="""During the blank screen, the firmware (the BIOS, or on modern servers UEFI) is running. It is the first code the CPUs run. It initializes the hardware and runs POST, the power-on self-test:
1. Checks that the CPUs work and starts them.
2. Detects, trains and tests the memory. Training tunes the timing for every DIMM on every channel. On servers with a lot of memory this takes minutes: it is the longest step.
3. Discovers the PCIe devices and trains their links (speed and width).
4. Finds the storage, network and GPU controllers, and loads the firmware of cards such as NICs and RAID controllers.
5. Checks fans, power and temperatures with the BMC.
6. Then finds a boot device in the boot order, passes hardware information (memory map, device list) to the operating system, and hands over to the bootloader.
Progress shows as POST codes on a small display, in the BMC, or on screen; some servers use beep codes. Video comes up late, so several minutes of blank screen is normal on a big server.
Why skipping it would be risky:
- POST catches hardware faults before the operating system and data are at risk. Without it, a bad DIMM or card would cause crashes or corrupted data later.
- It puts every device into a known state (memory and links trained). Without it, devices could be missing, slow or unstable.
- It gives you your first clue: a serious fault stops POST with a code or message. For some faults POST disables the bad part and continues, which is why a server can boot with less memory than is installed.""")

E[8].update(ans=E[8]['ans'] + """
Settings can change after a BIOS update or a reset to defaults, so record them before and after any firmware work.""")

E[10].update(
hook='Follow the power: <b>Source, Cords + PSUs, BMC, Interlocks, Short, Board</b>. A BMC that answers = standby power arrives.',
ans="""The server next to it runs on the same PDU, so the PDU has power. I follow the power from the outlet to the motherboard, one link at a time:
1. Power source: is this server's outlet or circuit live? Check the breaker and the outlet (PDU outlets can be switched off one by one). Is the cord in the right outlet?
2. Cords and PSUs: cords fully seated with their retention clips, PSUs fully latched. Check the PSU LEDs: off (no input power), amber (fault) or green. Swap in a known-good cord, outlet or PSU.
3. The BMC: it runs on standby power, so if it answers (web page, ping, ipmitool), power is reaching the board.
- Check ipmitool power status and the event log for power faults or a PSU mismatch, then try ipmitool power on.
- If it starts from the BMC but not from the button, suspect the front panel button or its cable.
- If the BMC is dead too, suspect the input power, the PSUs or the board.
4. Interlocks: some chassis will not start with the lid off or an intrusion switch open.
5. A shorted part: strip to a minimum configuration (one CPU, one DIMM, no cards or drives) and add parts back one at a time. Look and smell for burnt parts.
6. The motherboard last, once everything else is ruled out.
Document each check, then verify it powers on and passes test.""")

E[12].update(
ans="""First compare the slow drive's real speed with its rated speed and with the good drive. Then check each possible cause:
1. The link: sudo lspci -vv, LnkSta versus LnkCap. A Gen 4 x4 drive that trained at Gen 3 or x2 loses half its bandwidth or more. Also check which bay it is in: some bays are wired for fewer lanes or an older generation.
2. Shared paths: drives behind one PCIe switch share its uplink, and a drive attached to the other CPU adds delay. Check lspci -tv against the topology diagram.
3. Heat: drives slow themselves down (thermal throttling) when hot. Check the temperature and warnings in nvme smart-log, the airflow, and missing blanks or baffles.
4. Health and firmware: media errors and wear (percentage used) in nvme smart-log, and the firmware version in nvme list (both drives should match; check for known firmware issues).
5. The drive's state: a nearly full drive is slower, and so is one busy with other work.
6. The test: the benchmark must match how the drive is rated (sequential or random, block size, queue depth) and be identical on both drives.
Then isolate: swap the two drives between bays. If the slowness follows the drive, it is the drive; if it stays with the bay, it is the bay, backplane, cable or path. One change at a time, and document.""")

E[15].update(
ans="""1. Record the evidence: free -h (how much is missing), dmidecode -t memory (which slots are filled, sizes, serials, "No Module Installed"), and the errors from the BMC SEL and ras-mc-ctl --summary (which slots and channels, how many, and when).
2. Check the simple things: every new DIMM seated with both latches closed, the correct part, in the correct slot, and a current BIOS that supports the new DIMMs.
3. Rule out configuration: the population rules are followed, there are no mixed sizes, speeds or types (RDIMM with UDIMM, DDR4 with DDR5), and the BIOS memory settings are as specified (mirroring or sparing hide memory, no DIMMs disabled). A configuration problem usually affects many DIMMs, or starts right after a change or upgrade, which fits this case.
4. Remember POST: for some faults it disables a bad DIMM and continues, so "less memory" can mean POST turned a DIMM off. Check the BIOS memory screen and the SEL.
5. Swap test, one change at a time: move a suspect DIMM to a slot on a different channel, and put a known-good DIMM in its slot. Clear the logs and run a memory test.
- Errors follow the DIMM: the DIMM is bad.
- Errors stay with the slot: the slot, the motherboard or the CPU.
6. Look for patterns: errors on many DIMMs of one channel or one CPU point to the CPU's memory controller, CPU seating or bent socket pins.
7. Stress test after each change (vendor diagnostics, MemTest86, stress-ng), verify the full amount shows, and document slots, serials and results.""")

E[16].update(
ans="""What it suggests: the GPU was probably not the cause, or not the only cause. Two different GPUs failing the same way in the same slot point to something that slot shares. Do not keep replacing parts.
What should happen next:
1. Confirm the replacement: the correct part number and revision, compatible firmware, known-good, fully seated, and its power cable connected.
2. Recheck the symptom: is it exactly the same, or slightly different? Reread the original logs and timestamps (for example the same Xid 79 at the same PCI address).
3. Look at everything else in the path: the slot, riser, PCIe cable, power cable and PSU, BIOS settings, firmware, driver and configuration. Use the four layers and the topology diagram.
4. Isolate the location: try a known-good GPU in a different slot, or move the setup to a golden unit; and test this slot with a GPU from a passing server.
5. Consider outside causes: heat (airflow, baffles and fans for that slot), power, or the test itself.
6. Escalate with my data, and document that the replacement did not fix it, so the removed GPU is not wrongly blamed (retest it before any RMA).""")

E[17].update(
ans="""(a) Errors from the current boot only:
`journalctl -b -p err`
-b = this boot only. -p err = error priority and worse (crit, alert, emerg).
(b) Everything from 9:00 to 9:15 this morning:
`journalctl --since "09:00" --until "09:15"`
A time with no date means today. The full form is --since "2026-10-02 09:00" --until "2026-10-02 09:15"; you can also write --since "1 hour ago".
(c) Which error repeats most often:
`journalctl -b -p err -o cat | sort | uniq -c | sort -rn | head`
- -o cat prints only the message text, without the time and host, so identical messages look identical.
- sort puts identical lines together; uniq -c counts each group; sort -rn sorts by that count, biggest first; head shows the top 10.
- For a text log, the course's version is: grep -i "error" /var/log/syslog | sort | uniq -c | sort -rn | head
Once you find the event, note its exact timestamp and look at what happened just before it in every log, including the BMC event log. The first error is usually closer to the cause than the last one.""",
exp="""Narrow a big log step by step: by time, by severity, by source (journalctl -u sshd for one service), then by keyword (grep -iE "error|fail|timeout"). Start wide, then cut it down.
In a text log every line starts with a timestamp, so identical messages only group together in uniq -c after the time is removed. journalctl -o cat does that for you, which is why it is used in (c).""")

E[20].update(
ans="""Find the busy processes:
- `top` (or htop): live view. Press P to sort by CPU and M to sort by memory. %CPU above 100 means a process is using more than one core.
- `ps aux --sort=-%cpu | head` and `ps aux --sort=-%mem | head`: the top users once, for my notes.
Compare load with cores:
- `uptime` shows the load average over 1, 5 and 15 minutes: roughly how many tasks are running or waiting. `nproc` (or lscpu) shows the number of cores.
- A load of 16 on a 64-core server is light; 48 on a 16-core server is overloaded.
Find the bottleneck:
- CPU: load above the number of cores, %us high and %id near 0 in top, with low wa.
- Memory: `free -h` shows little available memory and heavy swap use: the server is short of memory.
- Storage: high wa (I/O wait) in top's summary line means the CPU is waiting on storage, not busy computing. iostat -x 1 shows a disk near 100 %util.
Judge the impact: which process it is and who owns it (an expected test or service, or something stuck in a loop), and whether other services are slowing down. Check the logs around when it started. Do not kill a process unless I know what it is and am authorized; ask first.""")

E[40].update(
ans="""First look at the console (BMC virtual console or SOL): is there a kernel panic or error on screen? Take a screenshot.
Then save the evidence to files, named with the unit serial:
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
Copy the files off the server before the power cycle (for example scp unit123_* tech@10.1.1.50:/evidence/). After it boots, read journalctl -b -1 to see the last messages before the power cycle.""")
