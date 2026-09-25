# Evals

`scenarios.json` holds real-world briefs with observable pass conditions. Run them after any change to the kit or the
skills that could change results:

1. Start a fresh Claude Code session per scenario and give its brief to the `remotion-director` agent, with a new
   project folder.
2. When it delivers, give only the rendered file, the platform and the audience to the `remotion-reviewer` agent.
3. Mark the scenario passed when every `done_when` item is true on the file, `nrk.py qa` passes and the reviewer has no
   high or medium finding. Record the render time and the number of review rounds.

Compare the numbers before and after a change. A change that fixes one scenario and breaks another is not done.
