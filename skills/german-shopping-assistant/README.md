# german-shopping-assistant

Price comparison, product recommendations and shopping research for the German market (Idealo, Amazon.de, MediaMarkt, etc.). Handles constraints like budget, weight capacity, legal requirements (e.g. e-scooters on trains).

## Install

```bash
# Example for Claude / Grok skills dir
mkdir -p ~/.claude/skills && curl -fsSL https://github.com/TuxLux40/skills/archive/refs/heads/master.tar.gz \
  | tar -xz --strip-components=2 -C ~/.claude/skills skills-master/skills/german-shopping-assistant
```
