# Hardware inventory — template

Keep the filled-in copy **private** (e.g. your agent's local skill dir or KB), not in this public repo.
The skill reads it if present to pre-resolve device names and remember past repairs.

| Device (exact model / type no.) | iFixit status | Notes / past repairs |
|---|---|---|
| Example Phone 8 | Device page + guides (battery guideid …) | Opening breaks IP seal. |
| Example Mini PC Gen 2 | No exact page — sibling model used | Repasted YYYY-MM-DD; HMM more accurate than iFixit. |

Fill `iFixit status` with `scripts/ifixit.py suggest "<name>"`. After each repair, record what differed from the guide, parts source and price.
