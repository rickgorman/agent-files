# agent-files

Steal these. Run them on your wall. Stop.

Stealable Claude Code skills. Not a course. Not a prompt dump.

## Skills

- [refine_plan](skills/refine_plan/) Four critics map-reduce a markdown plan in place until yield is zero.
- [dag-reader](skills/dag-reader/) Read a source into a thesis–claim–fact DAG and prune it to one crux paragraph.

## Install

Copy a skill folder into Claude Code:

```bash
cp -R skills/<name> ~/.claude/skills/<name>
# or into a project:  cp -R skills/<name> .claude/skills/<name>
```

Then invoke `/<name>`.

## License

MIT. See [LICENSE](LICENSE).
