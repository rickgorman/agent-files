![agent-files](world-map.png)

# agent-files

Steal these. Run them on your wall. Stop.

Stealable Claude Code skills. Not a course. Not a prompt dump.

## Skills

Every skill below is a place on the map. The map is generated from
[.claude/data/skill-map.yaml](.claude/data/skill-map.yaml) — add a skill, add
its entry, repaint.

- [refine-plan](skills/refine-plan/) Four critics map-reduce a markdown plan in place until yield is zero.
- [dag-reader](skills/dag-reader/) Read a source into a thesis–claim–fact DAG and prune it to one crux paragraph.
- [dev-manager](skills/dev-manager/) The orchestrator judges; coder lanes emit by a fixed task→model fallback sequence.
- [screen-flow](skills/screen-flow/) Drive a browser through a product flow and compile viewport screenshots onto a plat of titled lanes.

## Install

Copy a skill folder into Claude Code:

```bash
cp -R skills/<name> ~/.claude/skills/<name>
# or into a project:  cp -R skills/<name> .claude/skills/<name>
```

Then invoke `/<name>`.

## License

MIT. See [LICENSE](LICENSE).
