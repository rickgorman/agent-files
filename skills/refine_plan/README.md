# refine_plan

Steal when a plan is about to ship and you have only reviewed it from one seat.

## What

A Claude Code skill that reviews a plan from more than one seat before it ships. Default lenses: architecture, security, product, user-advocate. After each pass it counts new quality findings. If it is still finding, it invents new lenses and runs again. Stop at diminishing returns or a max pass count.

## When

The plan is about to ship. You have only reviewed it from one seat.

## How

Copy this folder into Claude Code skills:

```bash
cp -R skills/refine_plan .claude/skills/refine_plan
```

Then run `/refine_plan` against the plan.

See [SKILL.md](SKILL.md) for the full skill.
