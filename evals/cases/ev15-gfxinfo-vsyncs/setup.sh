#!/bin/bash
# ev15: a gfxinfo framestats dump where a Modal window and the activity share every vsync (2 rows per vsync),
# latency is 34 ms (pipelined, above one 16.7 ms period) and every vsync misses its FrameDeadline (emulator latency
# mode). Inside the spin window exactly ONE vsync is missing: the true answer is 1 dropped frame, 42 of 43 vsyncs.
set -euo pipefail
python3 - <<'PY'
P = 16_666_667                 # ns per vsync at 60 Hz
T0 = 7_283_000_000_000         # CLOCK_MONOTONIC ns of the first vsync in the dump
cols = ("Flags,FrameTimelineVsyncId,IntendedVsync,Vsync,InputEventId,HandleInputStart,AnimationStart,"
        "PerformTraversalsStart,DrawStart,FrameDeadline,FrameInterval,FrameStartTime,SyncQueued,SyncStart,"
        "IssueDrawCommandsStart,SwapBuffers,FrameCompleted,DequeueBufferDuration,QueueBufferDuration,"
        "GpuCompleted,SwapBuffersCompleted,DisplayPresentTime,CommandSubmissionId,").split(",")[:-1]
spin_from, spin_to = 30, 72    # vsync indices of the spin: 43 vsyncs, 30..72 inclusive (700 ms)
dropped = {51}                 # one vsync never produced inside the spin
rows = []
for k in range(0, 103):
    if k in dropped:
        continue
    iv = T0 + k * P
    renders = 2 if spin_from <= k <= spin_to else 1   # the Modal and the activity both draw during the spin
    for r in range(renders):
        v = dict.fromkeys(cols, 0)
        v.update(Flags=0, FrameTimelineVsyncId=1000 + k, IntendedVsync=iv, Vsync=iv, FrameDeadline=iv + P,
                 FrameInterval=P, FrameStartTime=iv, HandleInputStart=iv + 200_000, AnimationStart=iv + 300_000,
                 PerformTraversalsStart=iv + 400_000, DrawStart=iv + 500_000 + r * 100_000,
                 SyncQueued=iv + 1_500_000, SyncStart=iv + 1_600_000, IssueDrawCommandsStart=iv + 2_000_000,
                 SwapBuffers=iv + 4_000_000, FrameCompleted=iv + 34_000_000 + r * 50_000,
                 DequeueBufferDuration=14_000_000, QueueBufferDuration=300_000,
                 GpuCompleted=iv + 21_000_000, SwapBuffersCompleted=iv + 4_100_000, DisplayPresentTime=-1,
                 CommandSubmissionId=k)
        rows.append(",".join(str(v[c]) for c in cols) + ",")
with open("framestats.txt", "w") as f:
    f.write("Applications Graphics Acceleration Info:\nStats since: 7283000000000ns\nTotal frames rendered: %d\n"
            "Janky frames: 1 (0.97%%)\nJanky frames (legacy): %d (100.00%%)\n\n---PROFILEDATA---\n" % (len(rows), len(rows)))
    f.write(",".join(cols) + ",\n")
    f.write("\n".join(rows) + "\n---PROFILEDATA---\n")
with open("spin.log", "w") as f:   # logcat -v monotonic: seconds since boot, the same clock as IntendedVsync
    f.write("%15.6f  4242  4263 I ReactNativeJS: [globe] spin start\n" % ((T0 + spin_from * P) / 1e9 - 0.002))
    f.write("%15.6f  4242  4263 I ReactNativeJS: [globe] spin settle why=done\n" % ((T0 + spin_to * P) / 1e9 + 0.002))
PY
cat > NOTES.md <<'MD'
Dump: `adb shell dumpsys gfxinfo <app> framestats` taken right after a 700 ms globe spin on a 60 Hz emulator.
`spin.log` holds the app's own start/end lines, read with `logcat -v monotonic`.
A previous script counted every PROFILEDATA row in the window as a frame, called a frame janky when
FrameCompleted - IntendedVsync > 16.7 ms, and reported: "84 frames, 100 % janky, every frame missed its deadline".
MD
