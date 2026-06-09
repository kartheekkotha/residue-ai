# Residue E2E Test Logs

This document tracks End-to-End (E2E) feature verification simulating interactions from multiple AI agents (Codex, Gemini, Cursor, Claude Code).

## Test 1: Codex User Implicit Deferral
**Scenario:** User in Codex CLI says "I will fix the DB timeout later." Codex silently defers it.
> **Result (add_task_tool):** `{"saved": true, "id": 10, "title": "Fix database connection timeout", "owner": "user"}`

## Test 2: Gemini Autonomous Verification Task
**Scenario:** Gemini runs a Vercel deployment. It silently adds a task to check the Vercel URL later.
> **Result (add_task_tool):** `{"saved": true, "id": 11, "title": "Verify deployment success on Vercel", "owner": "ai"}`

## Test 3: Claude Code Session Boot
**Scenario:** Next morning, user opens Claude Code. Claude automatically runs get_pending_tasks_tool().
> **Result (get_pending_tasks_tool):**
```json
{
  "pending": [
    {
      "id": 10,
      "title": "Fix database connection timeout",
      "urgency": "high",
      "owner": "user"
    },
    {
      "id": 4,
      "title": "Book flight tickets",
      "urgency": "medium",
      "owner": "user"
    },
    {
      "id": 7,
      "title": "Check training loss curve",
      "urgency": "medium",
      "owner": "ai"
    },
    {
      "id": 6,
      "title": "Verify background pipeline",
      "urgency": "low",
      "owner": "user"
    },
    {
      "id": 11,
      "title": "Verify deployment success on Vercel",
      "urgency": "low",
      "owner": "ai"
    }
  ],
  "count": 5
}
```

## Test 4: Gemini Contextual Auto-Resolution
**Scenario:** The AI reads the pending list. It sees its AI task (`owner: ai`) and realizes the deployment finished successfully yesterday. It auto-resolves it.
> **Result (complete_task_tool):** `{"completed": true, "id": 11}`

## Test 5: Cursor Explicit Snooze
**Scenario:** The AI asks the user about the DB timeout task. User says "Not right now." AI snoozes it.
> **Result (snooze_task_tool):** `{"snoozed": true, "id": 10, "hours": 4}`

## Test 6: Antigravity Cross-Session Sync
**Scenario:** User opens Antigravity. The AI fetches tasks. Since the AI task was auto-resolved and the User task was snoozed, the plate should be clean.
> **Result (get_pending_tasks_tool):** `{"pending": [{"id": 4, "title": "Book flight tickets", "urgency": "medium", "owner": "user"}, {"id": 7, "title": "Check training loss curve", "urgency": "medium", "owner": "ai"}, {"id": 6, "title": "Verify background pipeline", "urgency": "low", "owner": "user"}], "count": 3}`

