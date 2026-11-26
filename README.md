# Gemini 4 model tests

The tasks, checkers and raw results behind [Choosing Between Gemini 4 Hydrogen, Neon, Carbon and Argon](https://abuango.me/blog/choosing-between-gemini-4-models/).

Each run sends one task to one model through Google's Antigravity CLI (`agy`). A script then scores the answer against a known result.

## Files

| File | What it holds |
|---|---|
| `tasks.py`, `tasks2.py` | The twelve small tasks and the prompt pairs, each with its checker |
| `tasks3.py`, `hard/` | The four harder tasks, their checkers and the reference solutions |
| `repo/`, `review_src.py`, `review_key.json`, `hidden_test.py` | Inputs for the bug-fix and code-review tasks |
| `run.py` | Runs a plan of (model, task, repeat) jobs and appends each result to `results/results.jsonl` |
| `plan.json` | The plan used for the 324 runs |
| `probe.py` | The test of three puzzles in three wordings on Argon |
| `analyse.py`, `cost.py` | The summaries and the cost figures used in the post |
| `results/` | Raw results: model, task, score, time, token usage and the full response of every run |

## Run it

```bash
python3 run.py plan.json 50 4   # plan, five-hour quota floor (%), parallel workers
python3 analyse.py
python3 cost.py
```

Paths in the saved responses are shortened to `<bench>` and `<runs>`.
