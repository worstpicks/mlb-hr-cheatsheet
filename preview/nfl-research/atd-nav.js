/* Worst Pickz — NFL cheat sheet week picker.
 * The NFL twin of the MLB sheet's Archive row: a dropdown of every week's sheet, read
 * from atd-manifest.json, and a "Current week" button on any sheet that is not this
 * week's. The current week lives at nfl-research/atd.html; past weeks live in
 * nfl-research/archive/. nfl_research/atd_sheet.py keeps the manifest up to date.
 *
 * Each sheet carries <meta name="sheet-week" content="2026-W2"> so it can find itself
 * in the list, and data-root on the nav ("" or "../") so links resolve from either
 * folder.
 */
(function () {
    "use strict";

    var nav = document.getElementById("atdSheetNav");
    if (!nav) return;
    var root = nav.getAttribute("data-root") || "";
    var select = document.getElementById("atdWeekSelect");
    var current = document.getElementById("atdCurrentWeek");
    var status = document.getElementById("atdSheetStatus");
    var meta = document.querySelector('meta[name="sheet-week"]');
    var here = meta ? meta.getAttribute("content") : "";

    var css =
        ".atd-sheetnav{display:flex;flex-wrap:wrap;align-items:center;gap:8px 14px;padding:10px 20px;" +
        "border-bottom:1px solid var(--nrs-border);background:rgba(8,15,28,.55)}" +
        "html.theme-light .atd-sheetnav{background:#fffbeb}" +
        ".atd-sheetnav__title{font-size:.72rem;font-weight:800;letter-spacing:.1em;text-transform:uppercase;color:#fb923c}" +
        "html.theme-light .atd-sheetnav__title{color:#9a3412}" +
        // The label must not shrink narrower than its select: a percentage min-width on the
        // select left the label free to collapse, and the select slid under the button.
        ".atd-sheetnav label{display:inline-flex;align-items:center;gap:8px;flex:0 1 auto;min-width:0;max-width:100%;" +
        "font-size:.74rem;font-weight:700;letter-spacing:.03em;color:var(--nrs-muted)}" +
        ".atd-sheetnav select{box-sizing:border-box;flex:0 1 15rem;width:15rem;min-width:0;max-width:100%;" +
        "padding:7px 10px;min-height:38px;border-radius:10px;" +
        "border:1px solid rgba(251,146,60,.35);background:rgba(15,23,42,.95);color:#f8fafc;font:inherit;" +
        "font-size:.88rem;font-weight:600;cursor:pointer}" +
        "html.theme-light .atd-sheetnav select{background:#fff;color:#1e293b;border-color:rgba(180,83,9,.35)}" +
        ".atd-sheetnav select:disabled{opacity:.55;cursor:not-allowed}" +
        ".atd-current-week{display:inline-flex;align-items:center;flex:0 0 auto;padding:7px 14px;border-radius:10px;" +
        "border:1px solid rgba(74,222,128,.55);background:linear-gradient(135deg,rgba(22,101,52,.95) 0%,rgba(21,128,61,.88) 100%);" +
        "color:#ecfccb;font-size:.82rem;font-weight:800;letter-spacing:.04em;text-decoration:none}" +
        ".atd-current-week[hidden]{display:none}" +
        ".atd-sheetnav__status{font-size:.72rem;font-weight:600;color:var(--nrs-muted)}" +
        ".atd-sheetnav__status.is-past{color:#fdba74}" +
        "html.theme-light .atd-sheetnav__status.is-past{color:#9a3412}";
    var style = document.createElement("style");
    style.textContent = css;
    document.head.appendChild(style);

    function fail() {
        select.disabled = true;
        status.textContent = "Week list unavailable right now.";
    }

    fetch(root + "atd-manifest.json", { cache: "no-store" })
        .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
        .then(function (m) {
            var sheets = (m && m.sheets || []).filter(function (s) { return s && s.key && s.href; });
            if (!sheets.length) return fail();
            sheets.sort(function (a, b) { return (b.season - a.season) || (b.week - a.week); });
            var latest = sheets[0];

            select.innerHTML = "";
            sheets.forEach(function (s) {
                var opt = document.createElement("option");
                opt.value = root + s.href;
                opt.textContent = s.label;
                if (s.key === here) opt.selected = true;
                select.appendChild(opt);
            });

            var onLatest = here === latest.key;
            current.href = root + latest.href;
            current.hidden = onLatest;
            if (!onLatest) {
                status.textContent = "You are viewing an archived week.";
                status.classList.add("is-past");
            }

            select.addEventListener("change", function () {
                if (select.value) window.location.href = select.value;
            });
        })
        .catch(fail);
})();
