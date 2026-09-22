# Knowledge rebuild benchmark

*Read-only asset inventory and recovery rehearsal · status: plan*

This experiment inventories a `memPed` workspace and writes a hash manifest under
`outputs/memped-upgrade/<run-id>/`. It does not import, migrate, rebuild, publish, or
delete runtime assets.

Run from the repository root:

```powershell
.\.venv\Scripts\python experiments/benchmark-knowledge-rebuild-20260922/inventory.py `
  --memped-root memPed `
  --output outputs/memped-upgrade/inventory-001/inventory.json `
  --catalog-backup outputs/memped-upgrade/inventory-001/knowledge.sqlite3
```
