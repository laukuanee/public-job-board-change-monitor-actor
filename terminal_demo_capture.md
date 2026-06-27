# Terminal Demo Capture

Command:

```powershell
C:\Users\lauku\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe .\job_board_monitor.py --input .\samples\input.json --out .\samples\output.json
```

Observed summary:

```text
page_count: 1
total_jobs: 2
total_changes: 3
changes: new Product Manager; unchanged Data Engineer; removed Support Specialist
```

Verification:

```powershell
C:\Users\lauku\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m unittest discover -s tests -v
```

Result: 6 tests passed.
