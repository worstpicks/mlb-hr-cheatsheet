# Research updates and Netlify

`daily-research.yml` starts at 8 AM America/New_York each day (GitHub may
delay scheduled starts). It builds NBA, NFL, NHL and available NHL cheat
sheets, then makes one commit/push containing the changed output. A no-change
run makes no commit. One sport's failure does not prevent the other sports
from building; partial failures are reported as a failed workflow.

The individual sport workflows retain manual and source-change triggers, but
have no schedules. All four workflows share the `research-publish` concurrency
group. Manual/source-triggered updates and normal website edits may still
produce additional deployments outside the daily update.

The NBA builder ignores the `built` timestamp when comparing content, matching
the existing NHL/NFL behavior. Its timestamp means when the data last changed,
not when it was last checked.

Netlify's `build.ignore` compares the cached commit to the incoming commit.
Changes in `preview/`, `netlify/`, `tools/`, Netlify configuration or supported
Node dependency/runtime configuration allow a build. Other changes alone
(research source, workflows, documentation) skip the website build; generated
research output will trigger it when published. Missing/invalid commit history
and same-commit retries allow a build. If the site gains new build input paths,
add them to `tools/netlify-ignore.mjs`.

This reduces routine daily research publication to at most one push/deploy,
not a global cap on manual deployments or Netlify dashboard retries.
