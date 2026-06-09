import json
from residue.server.mcp_server import add_task_tool, get_pending_tasks_tool, complete_task_tool, snooze_task_tool

log = []
log.append('# Residue E2E Test Logs\n')
log.append('This document tracks End-to-End (E2E) feature verification simulating interactions from multiple AI agents (Codex, Gemini, Cursor, Claude Code).\n')

# Test 1: User implicit deferral (owner='user')
log.append('## Test 1: Codex User Implicit Deferral')
log.append('**Scenario:** User in Codex CLI says "I will fix the DB timeout later." Codex silently defers it.')
res1 = add_task_tool('Fix database connection timeout', owner='user', urgency='high')
log.append(f'> **Result (add_task_tool):** `{res1}`\n')
user_task_id = json.loads(res1)['id']

# Test 2: AI creates a background check task (owner='ai')
log.append('## Test 2: Gemini Autonomous Verification Task')
log.append('**Scenario:** Gemini runs a Vercel deployment. It silently adds a task to check the Vercel URL later.')
res2 = add_task_tool('Verify deployment success on Vercel', owner='ai', urgency='low')
log.append(f'> **Result (add_task_tool):** `{res2}`\n')
ai_task_id = json.loads(res2)['id']

# Test 3: Session boot (get_pending_tasks)
log.append('## Test 3: Claude Code Session Boot')
log.append('**Scenario:** Next morning, user opens Claude Code. Claude automatically runs get_pending_tasks_tool().')
res3 = get_pending_tasks_tool()
log.append(f'> **Result (get_pending_tasks_tool):**\n```json\n{json.dumps(json.loads(res3), indent=2)}\n```\n')

# Test 4: AI Auto-Resolution (AI realizes it already checked Vercel, closes it)
log.append('## Test 4: Gemini Contextual Auto-Resolution')
log.append('**Scenario:** The AI reads the pending list. It sees its AI task (`owner: ai`) and realizes the deployment finished successfully yesterday. It auto-resolves it.')
res4 = complete_task_tool(ai_task_id)
log.append(f'> **Result (complete_task_tool):** `{res4}`\n')

# Test 5: User Snoozes the database task
log.append('## Test 5: Cursor Explicit Snooze')
log.append('**Scenario:** The AI asks the user about the DB timeout task. User says "Not right now." AI snoozes it.')
res5 = snooze_task_tool(user_task_id, hours=4)
log.append(f'> **Result (snooze_task_tool):** `{res5}`\n')

# Test 6: Verify final state
log.append('## Test 6: Antigravity Cross-Session Sync')
log.append('**Scenario:** User opens Antigravity. The AI fetches tasks. Since the AI task was auto-resolved and the User task was snoozed, the plate should be clean.')
res6 = get_pending_tasks_tool()
log.append(f'> **Result (get_pending_tasks_tool):** `{res6}`\n')

with open('E2E_TEST_LOGS.md', 'w') as f:
    for line in log:
        f.write(line + '\n')
