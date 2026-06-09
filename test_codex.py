import pexpect
import time
import sys

child = pexpect.spawn('codex', encoding='utf-8')
child.expect('>', timeout=30)
time.sleep(2)
child.send('/resid')
time.sleep(2)

# read whatever is on the screen right now
try:
    # prompt_toolkit renders the screen. We can just capture the output buffer
    print(child.read_nonblocking(size=10000, timeout=1))
except Exception as e:
    print("Exception reading:", e)

child.sendline()
child.sendline('/exit')
