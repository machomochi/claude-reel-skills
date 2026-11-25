# Claude reel skills

Skills for [Claude Code](https://code.claude.com/docs) that I built from Instagram reels I saved, plus the small tool that turns a reel into something Claude can read.

How it works: I save a reel about design, security, marketing or AI. Every day Claude transcribes it, reads the text on screen, **fact-checks it against official docs**, and only writes down the parts that hold up, in its own words. Wrong or exaggerated claims get dropped or labelled "unverified".

## What's here

| Folder | What it is |
|---|---|
| [`skills/ui-design-rules`](skills/ui-design-rules) | UI, CSS, colour, motion and UX rules that make a site look designed instead of AI-default |
| [`skills/web-launch-checklist`](skills/web-launch-checklist) | Pre-launch check for apps built fast with AI: surprise bills, database rules, leaked keys, ~30 common attacks, break-it tests |
| [`skills/human-writing`](skills/human-writing) | Make website and marketing copy sound like a person, not a chatbot |
| [`reel-watcher`](reel-watcher) | `transcribe.py` (reel to transcript + stills) and the daily instructions I give Claude |

Each skill folder has a `README.md` saying what I think the skill is and how far to trust it. `SKILL.md` is the file Claude reads.

## Use the skills

Copy a skill folder into your Claude Code skills folder:

- **All your projects:** `~/.claude/skills/<skill-name>/SKILL.md`
- **One project:** `<your-project>/.claude/skills/<skill-name>/SKILL.md`

```bash
git clone https://github.com/machomochi/claude-reel-skills
cp -r claude-reel-skills/skills/ui-design-rules ~/.claude/skills/
```

Claude picks the skill up by itself when your request matches its description (for example "restyle this page" or "check my app before launch"). You don't need to mention it. Other tools that support the `SKILL.md` format can use these files too.

## Use the reel tool (optional)

```bash
cd reel-watcher
python -m venv venv
venv/Scripts/pip install -r requirements.txt      # Windows (macOS/Linux: venv/bin/pip)
venv/Scripts/python -X utf8 transcribe.py "https://www.instagram.com/reel/<id>/"
```

It runs locally and needs no API key. The first run downloads a speech model of about 500 MB. Only process videos you're allowed to download, and respect the platform's terms. [`watcher-prompt.md`](reel-watcher/watcher-prompt.md) contains the scheduled-task instructions, with placeholders to fill in.

## Fair warning

- The rules are checked against sources, but they're still my notes, not official guidance. Case-study numbers are labelled as reported.
- The security checklist doesn't replace a real audit. The legal notes are general information, not legal advice.
- This is a personal project. It isn't affiliated with Anthropic, Instagram or any of the creators credited in the files.

## Credits

The ideas come from creators credited at the bottom of each `SKILL.md`. All wording is original, no reel content is copied, and screenshots and transcripts are not included.

MIT licence: use it, change it, share it.
