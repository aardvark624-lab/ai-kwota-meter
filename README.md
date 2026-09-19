# AI Kwota Meter

Foon-vriendelike meter vir **Claude**, **ChatGPT** en **Grok** weeklikse usage.

## Hoe dit werk

- Amptelike apps wys % in Settings → Usage, maar geen openbare API vir Max/Plus/SuperGrok nie.
- Jy stuur die % (of ’n skermskoot) vir MynKonyn / Baas; ons sit dit in `manual_overrides.json`.
- Die meter verdeel die weeklimiet **swaarder oor weekdae** (gewig 1.0) as **naweke** (0.4).
- Wys **% oor vandag** (pacing) en **% oor vir die week**.

## Foon-widget (PWA)

1. Maak die site oop op jou foon.
2. Safari: Deel → Add to Home Screen. Chrome: Kieslys → Install app / Add to Home screen.
3. Die ikoon gedra hom soos ’n app; dit is die “widget”.

## Plaaslike update

```bash
python3 scripts/set_reading.py claude 42
python3 scripts/set_reading.py chatgpt 30
python3 scripts/set_reading.py grok 15
python3 scripts/compute_budgets.py
```

## Note

Voorbeeldgetalle in die repo is net om die UI te wys — vervang met jou regte Settings → Usage %.
