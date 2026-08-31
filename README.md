# agent-files

Steal these. Run them on your wall. Stop.

Stealable Claude Code skills. Not a course. Not a prompt dump.

## Start here

[refine_plan](skills/refine_plan/). steal when a plan is about to become code and you've only reviewed it from one seat.

[dag-reader](skills/dag-reader/). steal when you need the spine of an argument, not a summary.

## Map

| Skill | Steal when | Install |
| --- | --- | --- |
| [refine_plan](skills/refine_plan/) | A plan is about to become code and you've only reviewed it from one seat | Copy `skills/refine_plan/` into `.claude/skills/` |
| [dag-reader](skills/dag-reader/) | You need the spine of an argument, not a summary | Copy `skills/dag-reader/` into `.claude/skills/` |

## Install

Copy a skill folder into Claude Code:

```bash
cp -R skills/refine_plan .claude/skills/refine_plan
cp -R skills/dag-reader .claude/skills/dag-reader
```

Then invoke `/refine_plan path/to/plan.md` or `/dag-reader path/to/article.md`.

## License

MIT. See [LICENSE](LICENSE).
