# `denmark` — schema parity patch (HIGH priority)

_Source: Stage 7e audit 2026-05-22 UTC · KB §49.11_

## Findings

`substations[0].markov` missing `p_crit_20yr`, `p_critical_20yr`,
`steady_state`. Note: synonym group `(p_crit_20yr, p_critical_20yr)`
exists in the audit — Denmark is missing **both**, so the synonym
can't save it. This is a real gap.

## Why this matters

Denmark's substation pages would show a blank 20-year risk forecast
+ no Markov steady-state distribution. The 20-year horizon drives
the long-tail risk widget visible on every substation popover and
on intelligence.html's "Section G — Markov forecast".

## Patch

In `scoring-dk/publish.py`, find the substation loop that builds the
`markov` dict. Currently emits something like:

```python
"markov": {
    "risk_score":     risk_score,
    "corrosion_class": corr_class,
    "ettc_years":     ettc,
    "p_crit_10yr":    p10,
    # MISSING:
    # "p_crit_20yr":  p20,
    # "p_critical_20yr": p20,   # alias (LV convention)
    # "steady_state": ss_vec,
},
```

Add the three missing fields. The Markov pipeline likely already
computes them — they're just not being exported. The values come
from the same Markov transition matrix that produces `p_crit_10yr`:

```python
# In the Markov-chain computation block:
P10  = markov_p_critical(transition_matrix, initial_state, horizon=10)
P20  = markov_p_critical(transition_matrix, initial_state, horizon=20)
SS   = markov_steady_state(transition_matrix)  # length-4 vector

"markov": {
    "risk_score":      risk_score,
    "corrosion_class": corr_class,
    "ettc_years":      ettc,
    "p_crit_10yr":     P10,           # FR-style name (current)
    "p_critical_10yr": P10,           # LV-style alias (KB §49.11 standard)
    "p_crit_20yr":     P20,
    "p_critical_20yr": P20,           # alias
    "steady_state":    list(SS),      # JSON-serialisable
},
```

The double-emission (FR-style + LV-style alias) maintains backwards
compatibility with any dashboard JS that currently reads either form.

## Verification

```
python3 scoring-dk/score-country.py
python3 -c "
import json
d = json.load(open('denmark/ssi-data.json'))
sub = d['substations'][0] if isinstance(d['substations'], list) else next(iter(d['substations'].values()))
mk  = sub['markov']
for k in ['p_crit_20yr', 'p_critical_20yr', 'steady_state']:
    assert k in mk, f'still missing: {k}'
    print(f'{k}: {mk[k]}')
"
```

Then trigger the audit:

```
gh workflow run runtime-audit.yml \
    -R ikengassiindex/ikengassiindex.github.io \
    -f countries=denmark -f always_send=true
```

Expected next-run result: denmark shows ✓ clean.
