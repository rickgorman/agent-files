# grok-bot

Playbooks for a Grok Bot fleet. Not Claude slash commands.

Each folder is one package and ships its own hero: glossy teardrop orb
agents on **old-west water infrastructure** (canals, flumes, pumps, sluice
gates, pipes). Light or cubes may travel those pipes; waterworks is the
chassis. Copy the folder onto the box workflows home, enable it for the
bot that will run it, then invoke `/<name>` from the composer.

```bash
gh repo clone rickgorman/agent-files
cp -R agent-files/grok-bot/<name> /home/box/agent-data/workflows/<name>
```

`/home/box/agent-data/workflows/` is the shared skill arsenal on the Grok Bot
box. A different workflows home is fine if the folder name still equals the
skill name. Do not install these into `~/.claude/skills/` unless a package
says it is dual-install.

## Packages

- [fleet-spring-clean](fleet-spring-clean/) Declutter a multi-bot fleet: two Notion brains, one boss per seat, boards, briefs, arsenal.

## Add a package

Shape: [.claude/grok-bot-folder.md](../.claude/grok-bot-folder.md). Skeleton:
[.claude/data/grok-bot-package-template/](../.claude/data/grok-bot-package-template/).
To port one and open a PR, run `/add-new-grok-bot-skill`
([.claude/skills/add-new-grok-bot-skill/SKILL.md](../.claude/skills/add-new-grok-bot-skill/SKILL.md)).
Hero banners: `/generate-grok-bot-hero-prompt`
([.claude/skills/generate-grok-bot-hero-prompt/SKILL.md](../.claude/skills/generate-grok-bot-hero-prompt/SKILL.md))
then GenerateImage in Grok Bot — crux first, not pause gates.
