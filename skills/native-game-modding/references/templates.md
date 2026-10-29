# Templates

## MODLOG.md

```markdown
# <Game> — <mod name> log

## Setup
- Game build / exe timestamp:
- Install path:
- Build:   `<command>`
- Install: `<command>` (game must be stopped)
- Log:     `<path>` (truncated on start)
- Decompile: `<path>` (outside the repo)

## Confirmed facts
- <addr / offset> — <what it is> — <how verified (log line, date)>

## Sessions
### YYYY-MM-DD
- Goal:
- Done / verified:
- Next:
```

## docs/mechanics/<subsystem>.md

```markdown
# <Subsystem> — how the game does it

## Entry points
| Address | Name | Role | Variants (other callers of the same helper) |

## States
<state bytes, order, measured timings>

## The game's controls
| Value (address/offset) | Meant for | Normal range | Measured scale | Evidence (observed / inferred / unknown) |

## Frame order
input → … → skeleton → effects (laser) → camera → render

## What the mod changes (and why it is safe)
```

## dead_ends.md

```markdown
# Dead ends

Read before proposing a design. Append whenever the circuit breaker trips.

## <Subsystem> — <approach in a few words> (YYYY-MM-DD)
- **Tried:**
- **Failed because:** (root cause, not the symptom)
- **Better approach:**
```
