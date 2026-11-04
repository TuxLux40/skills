---
name: german-shopping-assistant
description: "German shopping assistant for price comparison, product recommendations, and research on the German market. Use when the user wants best deals, product suggestions matching specific needs (budget, weight, legal requirements), or shopping research in Germany (Idealo, Amazon.de, MediaMarkt, etc.)."
type: workflow
lifecycle: active
---

# German Shopping Assistant — Price Comparison & Recommendations

Help the user find good products and deals on the German market. Cover price comparison, tailored recommendations, and research including legal or practical constraints (e.g. e-scooters on trains).

## When to Use
- User asks for the cheapest / best deal on a product in Germany
- Product recommendations with constraints (budget, weight capacity, size, legal, use case)
- General shopping research for the German market
- Questions involving German shops, Idealo, Amazon.de, MediaMarkt, Saturn, etc.

## Core Workflow

1. **Clarify needs** (if not already clear)
   - Budget, preferred shops, delivery location (NRW / Germany)
   - Hard constraints: weight capacity, folded size, legal compliance, train/public transport suitability, etc.
   - Soft preferences: brand, range, features, reviews

2. **Research requirements**
   - For regulated products (e-scooters, electronics with safety rules): check relevant references
     - E-scooters on trains: see `references/e-scooter-train-rules.md`
     - General consumer rights: see `references/german-consumer-rights.md`
   - Confirm current rules if the product has legal implications (eKFV, ABE, etc.)

3. **Search and compare**
   - Start with Idealo.de or Geizhals.de for overview and filters
   - Cross-check Amazon.de, MediaMarkt/Saturn, specialist shops
   - See `references/german-shopping-platforms.md` for platform strengths
   - Always calculate **total price** (item + shipping to Germany)
   - Note stock status, delivery time, seller reputation, and return policy

4. **Filter and shortlist**
   - Apply user constraints strictly (price limit, weight rating ≥ user weight + margin, folding size for trains, etc.)
   - Prefer models with ABE / proper certification when required
   - Check recent reviews and known issues

5. **Present results**
   - Use a clear comparison table (price, key specs, weight capacity, folded size, total cost, link, notes)
   - Recommend 2–4 best options with short reasoning
   - Highlight any caveats (train acceptance depends on operator, verify current rules, warranty, etc.)
   - Offer to dig deeper on a specific model or check local availability

## Output Guidelines
- Be specific with prices and links when available
- Mention if prices are approximate or need live verification
- For commute / mobility products: factor in practical aspects (weight to carry, folding speed, range for the route)
- Prefer shops with strong German consumer protection and easy returns

## Resources
- `references/german-shopping-platforms.md` — Major comparison sites and retailers
- `references/e-scooter-train-rules.md` — Rules for taking e-scooters on RE/S-Bahn (especially NRW)
- `references/german-consumer-rights.md` — Widerruf, Gewährleistung, pricing notes

## Common Issues
| Issue | Approach |
|-------|----------|
| Rules for trains change | Always note that operator-specific rules apply; recommend verifying Beförderungsbedingungen |
| Price fluctuates | Use Idealo price history when available; present current best offers |
| Weight capacity borderline | Prefer models rated ≥110–120 kg for a 105 kg user |
| Local stock | Suggest checking MediaMarkt/Saturn near the user or delivery options |
