---
description: Advanced Expense Audit with MCP Integrations
---

### Workflow: Automated Audit & Multi-Channel Notification

1. **Transaction Submission**:
   - The user submits an expense via the Dashboard.
   - The `ExpenseAgentOrchestrator` receives the data.

2. **Compliance Analysis**:
   - The agent uses `fetch_policy` to verify the category rules.
   - If the merchant is over $50, it uses `verify_merchant_reputation`.

3. **MCP Action: Persistence & Archiving**:
   - The agent uses `archive_audit_log` (File System MCP) to store a deep legal archive of the reasoning.
   - The agent uses `log_to_sheets` (Google Sheets MCP) to update the corporate treasury tracker.

4. **MCP Action: Scheduling (If Flagged)**:
   - If the audit result is `FLAGGED`, the agent automatically uses `schedule_review` (Google Calendar MCP) to book time for a manager's review.

5. **MCP Action: Notification**:
   - The agent uses `send_notification` (Email MCP) to alert the employee of the outcome.

### Example Tool Invocation Pattern
// turbo
```python
# The agent will resolve these tools dynamically:
await schedule_review(merchant="Luxury Sushi", amount=320.0, reason="Individual meal exceeds cap")
await send_notification(recipient="employee@company.com", status="FLAGGED", message="Your expense requires manual review.")
```
