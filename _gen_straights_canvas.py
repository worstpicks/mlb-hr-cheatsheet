import json
from pathlib import Path

d = json.load(open("_straights_0724.json", encoding="utf-8"))

headers = [
    "Status",
    "Batter",
    "vs SP",
    "Game",
    "Split",
    "Risk",
    "Park%",
    "Zone",
    "Form",
    "HR",
    "Near",
    "EV",
    "Score",
    "Odds",
    "Comp",
]
align = [
    "left",
    "left",
    "left",
    "left",
    "right",
    "right",
    "right",
    "right",
    "right",
    "right",
    "right",
    "right",
    "right",
    "left",
    "right",
]


def odds_short(o: str) -> str:
    o = o or ""
    if "prop" in o.lower() and "+" not in o:
        return "prop"
    for part in o.replace("Listed ", "").split():
        if part.startswith("+") or part.startswith("-"):
            digits = part[1:].replace(".", "")
            if digits.isdigit():
                return part
    return o[:20]


def rows_for(items):
    out = []
    tones = []
    for r in items:
        tones.append("success" if r["current"] else None)
        park = r["park"]
        park_s = f"{park:+d}%" if isinstance(park, int) else str(park)
        out.append(
            [
                "CURRENT" if r["current"] else "",
                r["name"],
                r["vs"],
                r["game"],
                f"{r['split']:+.2f}",
                f"{r['risk']:+.2f}",
                park_s,
                str(r["zone"]),
                str(r["form"]),
                str(r["hr"]),
                str(r["near"]),
                str(r["ev"]),
                str(r["score"]),
                odds_short(r["odds"]),
                str(r["comp"]),
            ]
        )
    return out, tones


def emit(items):
    rows, tones = rows_for(items)
    return json.dumps(rows), json.dumps(tones)


o05s_rows, o05s_tones = emit(d["o05_strict"])
o05r_rows, o05r_tones = emit(d["o05_relaxed"])
o15_rows, o15_tones = emit(d["o15"])
o15r_rows, o15r_tones = emit(d["o15_relaxed"])

strict_names = {r["name"] for r in d["o05_strict"]}
extras = [r for r in d["o05_relaxed"] if r["name"] not in strict_names]
ex_rows, ex_tones = emit(extras)

canvas = f"""import {{
  Callout,
  Divider,
  H1,
  H2,
  Stack,
  Stat,
  Table,
  Text,
  Grid,
}} from "cursor/canvas";

const HEADERS = {json.dumps(headers)};
const ALIGN = {json.dumps(align)} as const;

const O05_STRICT_ROWS = {o05s_rows};
const O05_STRICT_TONES = {o05s_tones} as const;

const O05_RELAXED_ROWS = {o05r_rows};
const O05_RELAXED_TONES = {o05r_tones} as const;

const O05_EXTRAS_ROWS = {ex_rows};
const O05_EXTRAS_TONES = {ex_tones} as const;

const O15_ROWS = {o15_rows};
const O15_TONES = {o15_tones} as const;

const O15_RELAXED_ROWS = {o15r_rows};
const O15_RELAXED_TONES = {o15r_tones} as const;

export default function StraightsOptions0724() {{
  return (
    <Stack gap={{24}}>
      <Stack gap={{8}}>
        <H1>7/24 Straights of the Day — full options</H1>
        <Text tone="secondary">
          Source: patch-0724-preview.py pools · zone-fit led · CURRENT = live sheet picks
        </Text>
      </Stack>

      <Grid columns={{2}} gap={{16}}>
        <Stat
          value="Derek Hill"
          label="O0.5 CURRENT · vs Warren · NYY at PHI"
          tone="success"
        />
        <Stat
          value="Joe Mack"
          label="O1.5 CURRENT · vs Marquez · SD at MIA · +820"
          tone="success"
        />
      </Grid>

      <Callout tone="info" title="Column key">
        Split = platoon edge · Risk = pitcher HR risk · Park% = hand park · Zone =
        hr_zone_fit · Form = hr_power_form · Comp = zone+form+split+risk+park
        composite · Odds = listed O0.5 price
      </Callout>

      <Divider />

      <Stack gap={{12}}>
        <H2>O0.5 strict pool ({len(d["o05_strict"])})</H2>
        <Text tone="secondary" size="small">
          Primary O0.5 lane — zone lane OK, positive split, usable attack
        </Text>
        <Table
          headers={{HEADERS}}
          rows={{O05_STRICT_ROWS}}
          columnAlign={{[...ALIGN]}}
          rowTone={{[...O05_STRICT_TONES]}}
          striped
          stickyHeader
        />
      </Stack>

      <Stack gap={{12}}>
        <H2>O0.5 relaxed extras only ({len(extras)})</H2>
        <Text tone="secondary" size="small">
          In relaxed pool but not strict — softer form/zone gates
        </Text>
        <Table
          headers={{HEADERS}}
          rows={{O05_EXTRAS_ROWS}}
          columnAlign={{[...ALIGN]}}
          rowTone={{[...O05_EXTRAS_TONES]}}
          striped
          stickyHeader
        />
      </Stack>

      <Stack gap={{12}}>
        <H2>O0.5 full relaxed pool ({len(d["o05_relaxed"])})</H2>
        <Table
          headers={{HEADERS}}
          rows={{O05_RELAXED_ROWS}}
          columnAlign={{[...ALIGN]}}
          rowTone={{[...O05_RELAXED_TONES]}}
          striped
          stickyHeader
        />
      </Stack>

      <Divider />

      <Stack gap={{12}}>
        <H2>O1.5 multi-HR pool ({len(d["o15"])})</H2>
        <Text tone="secondary" size="small">
          True multi-HR profiles — pair must be a different game than O0.5
        </Text>
        <Table
          headers={{HEADERS}}
          rows={{O15_ROWS}}
          columnAlign={{[...ALIGN]}}
          rowTone={{[...O15_TONES]}}
          striped
          stickyHeader
        />
      </Stack>

      <Stack gap={{12}}>
        <H2>O1.5 relaxed pool ({len(d["o15_relaxed"])})</H2>
        <Text tone="secondary" size="small">
          Adds Valdez vs Boyd (harsh park -23%)
        </Text>
        <Table
          headers={{HEADERS}}
          rows={{O15_RELAXED_ROWS}}
          columnAlign={{[...ALIGN]}}
          rowTone={{[...O15_RELAXED_TONES]}}
          striped
          stickyHeader
        />
      </Stack>
    </Stack>
  );
}}
"""

out = Path(
    r"C:\Users\allmi\.cursor\projects\c-Users-allmi-mlb-hr-cheatsheet-web\canvases\straights-options-0724.canvas.tsx"
)
out.write_text(canvas, encoding="utf-8")
print("wrote", out, "bytes", out.stat().st_size)
