# agent-files

Steal these. Run them on your wall. Stop.

Stealable Claude Code skills. Not a course. Not a prompt dump.

## Start here

[refine_plan](skills/refine_plan/). steal when a plan is about to become code and you've only reviewed it from one seat.

## Map

| Skill | Steal when | Install |
| --- | --- | --- |
| [refine_plan](skills/refine_plan/) | A plan is about to become code and you've only reviewed it from one seat | Copy `skills/refine_plan/` into `.claude/skills/` |

## Install

Copy the skill folder into Claude Code:

```bash
cp -R skills/refine_plan .claude/skills/refine_plan
```

Then invoke `/refine_plan path/to/plan.md`. It edits the plan in place until four critics per cycle find nothing material.

## License

MIT. See [LICENSE](LICENSE).
