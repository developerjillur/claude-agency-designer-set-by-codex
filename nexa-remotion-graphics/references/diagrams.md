# Diagrams: flows, timelines, trees

A diagram in a video is a story told in order: each box arrives when the story gets to it, and the connector that
leads to it draws first. The eye follows the drawing line.

## 1. Flow diagrams (kit `FlowDiagram`)

**Choreography (built in).** Nodes are ordered along the flow (left to right, or top to bottom), then across it.
The first node arrives at the start; a node with incoming connectors arrives when the last of them finishes
drawing; a connector starts drawing once its source node has mostly arrived (60% of the node's entrance); nodes with
nothing leading to them follow the previous one after `stagger` frames; connectors that point back (loops,
rollbacks) draw once both ends are on screen. With 14 f nodes and 18 f connectors, a 5-step chain takes about 4 s.

**Placement.**
- Automatic layers: a node sits one layer after the latest node pointing to it; nodes in a layer are centred
  against the tallest layer. Good for pipelines and branching processes.
- Grid: `col` and `row` (fractions allowed) when you want a specific shape (a diamond of parallel steps, a loop).
- Free: `x` and `y` as shares of the box (0 to 1) for maps of systems.
- `direction` 'right' (16:9) or 'down' (9:16, `'auto'` picks by the frame).

**Routing.** `'curve'` (a cubic S between facing sides: the friendly default), `'elbow'` (right angles with rounded
corners: technical diagrams, pipelines, org charts), `'straight'` (sparse networks). A connector to a node behind it
(a loop, a rollback) leaves from the far side and runs round outside every node between its ends, with rounded
corners (below the diagram for 'right' flows, to the right for 'down' flows).

**Emphasis.** `highlight` rings nodes in the accent and turns connectors between two highlighted nodes accent (the
happy path). `tone: 'accent'` makes one node solid (the goal, the product); `tone: 'outline'` a ruled box (external
systems). Labels on connectors (`label`) are small pills at the middle that arrive after the connector. Dashed
connectors (`dashed`) for optional or failure paths. `pulse` sends dots along drawn connectors (data moving); use it
in tech explainers, not in calm corporate pieces.

**Content.** 2 to 3 words per node, an optional `sub` line, an optional icon (drawn on after the box lands). 6 to 8
nodes per frame; split bigger systems into two scenes or zoom with the motion kit's `Camera`.

## 2. Timelines (kit `Timeline`)

- The line draws through time with an arrow head riding its tip (time goes on); each event's dot pops when the tip
  reaches it, then its date and title rise (3 f later).
- `at` on every event makes spacing true to time (a gap of four years looks like four years); leave it out for
  even spacing when only the order matters.
- Horizontal: events alternate above and below the line when they are closer than about 300 px; one line of text
  per title, a short detail line. Vertical (9:16 default): text to the right of the line.
- One highlighted event (a filled dot with a halo, the title in the accent): the one the voice lands on.
- Budget: 20 f of line per event (at least 50 f), then hold 1.5 s.
- Long histories: split into eras, or move a `Camera` along a wide timeline.

## 3. Trees and org charts (kit `OrgChart`)

- Parent links in, positions out: leaves take even slots in depth-first order, each parent sits centred over its
  first and last child, rows by depth; connectors are elbows through a bus line half way between rows.
- Keep 2 to 4 levels and 8 leaves per frame; show deeper trees in two scenes (the top, then one branch).
- `tone: 'accent'` for the root or the person being introduced; `highlight` for the branch the voice talks about.

## 4. Building other diagrams from the kit's parts

| Diagram | Parts |
|---|---|
| Venn (2 or 3 sets) | circles from `circlePath` with 40% opacity fills, drawn on in `'together'` mode, labels as `ChartLabel`; the overlap label arrives last |
| Cycle (a loop of 4 to 6 steps) | nodes on a circle (`x`, `y` from angle), `route="curve"`, the last edge back to the first |
| Funnel | trapezoids from `polyPath`, stacked and growing from the top, values with `formatValue`, conversion arrows between |
| Before and after | two columns, `HandMark kind="cross"` on the old, `kind="check"` on the new |
| Mind map | a centre node, `bendPath` connectors drawn outward with a 4 f stagger, labels at the ends |
| Map of a system | `FlowDiagram` with `x`/`y`, `tone: 'outline'` for outside services, `pulse` on live connections |
| Step list | `IconBadge` + text rows arriving with the motion kit's `Stagger`, a `DrawnPath` line joining the badges |

## 5. Rules

- Arrive in reading order; one thing moving at a time; a connector always draws before the node it leads to.
- Keep labels horizontal (never along a curve); connector labels short (one or two words).
- Colour carries meaning: the accent for the path that matters, grey for the rest, the theme's negative for failure
  paths.
- A diagram holds at least 2 s after its last node lands; longer if it has more than 5 nodes (reading time).
