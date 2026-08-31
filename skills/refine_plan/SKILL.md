---
name: refine_plan
description: Steal when a plan is about to ship and you have only reviewed it from one seat.
---

# refine_plan

Run this on a plan that is about to ship after you have only reviewed it from one seat.

## How

1. Read the plan as written. Do not implement yet.
2. Run a pass for each default lens, in order:
   - architecture
   - security
   - product
   - user-advocate
3. After each pass, count new quality findings (real holes, not nits). Write them down.
4. If the last full round of lenses still produced quality findings, invent new lenses aimed at those holes and run again.
5. Stop at diminishing returns (a round with no new quality findings) or at a max of 4 rounds. State which stop condition you hit.
6. Return: findings by lens, what you would change in the plan, and what you would leave.

Do not rewrite the plan unless asked. Do not inflate findings. Smallest reversible change to the plan wins.
