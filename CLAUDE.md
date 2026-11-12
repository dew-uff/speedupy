# SpeeduPy — instructions for agents

A software-engineering retrofit of this repository is in progress. Its plan,
its status table and the protocol to follow are in `RETROFIT.md`.

- When asked for the next retrofit task, in any wording or language, or asked
  to work on one, read `RETROFIT.md` and follow "Protocol" there.
- When you finish a retrofit task, tell the dev the next one without being
  asked: the task, the model, the effort, and whether to `/clear` first.
- Do not run the test suite or `setup_exp/setup.py` before reading "Safety" in
  `RETROFIT.md`: both erase data in the database servers on localhost.
- When a tool is missing on the machine (uv, Python, Docker, `gh`), do not
  replace it with a weaker one: follow "Tools on the dev's machine" in
  `RETROFIT.md`, which starts by asking the dev's go-ahead to install it.

Task 1 of the retrofit replaces this file with `@AGENTS.md`.
