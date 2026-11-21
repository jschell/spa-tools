# Running Start Planner: design decisions and roadmap

Companion to [`running-start-planner.html`](running-start-planner.html) ([live page](https://jschell.github.io/spa-tools/running-start-planner.html)).
This document records what we decided while designing the tool, why, and where the rules came from.
Update it when a decision changes. Add a new row to the decision log instead of rewriting history.

## Purpose

Help a Riverview School District (Cedarcrest High School, Duvall WA) student in Running Start plan two
credentials at once:

1. **The Cedarcrest high school diploma.**
2. **The Bellevue College Associate in Arts & Sciences (AA-DTA) transfer degree.**

The tool should show every option that meets each requirement, make clear what's required and what's optional,
and let the plan be updated quarter by quarter as courses are completed.

## Sources of truth

| Topic | Source | Notes |
|---|---|---|
| HS credit totals | [Cedarcrest 2026–27 course catalog](https://ceb127e6-ce7f-4fb6-a881-d469edc65251.usrfiles.com/ugd/ceb127_e3bfdf274cc64d76851f93b64ac3a4e5.pdf), p. 5–6 | Classes of 2027–2030 table. The [CHS counseling page](https://www.chs.rsd407.org/counseling) points to the catalog and OSPI. |
| State rules: credit conversion, Graduation Pathway, HSBP | [OSPI Class of 2027 graduation toolkit](https://ospi.k12.wa.us/sites/default/files/2026-09/classof2027graduationtoolkit.pdf), p. 12–18 | RCW 28A.230.740, WAC 180-51-050 |
| Running Start → HS subject mapping | [Riverview Running Start course equivalencies](https://6140bf52-cefa-489a-82f8-e9b6a56edce1.filesusr.com/ugd/243013_0c41a1dc3b0d4f6b939995ac7d79394d.pdf) | Also linked from the CHS counseling page |
| AP exam → BC credit | [BC Advanced Placement chart](https://www.bellevuecollege.edu/wp-content/uploads/2024/02/Advanced-Placement-AP-Chart.pdf) (Evaluations Office, Feb 2024) | Transcribed into `AP_CHART` |
| AP exams approved for the Graduation Pathway | OSPI Class of 2027 toolkit, p. 19 | `AP_PATHWAY_ELA`, `AP_PATHWAY_MATH` |
| AA-DTA rules and course lists | [BC AA-DTA worksheet 2025–26](https://www.bellevuecollege.edu/wp-content/uploads/2025/08/AssociateArtsScienceWorksheet_2025-26.pdf) | Course lists are transcribed into the page as `*_SRC` strings |

When a new catalog or worksheet comes out, update the constants at the top of the `<script>` block (`HUM_SRC`, `SS_SRC`,
`NS_SRC`, `MATH_SRC`, `EXTRA_SRC`, `DIV_SRC`, `HS_CATS`, and the equivalency rules in `enrich()`), then add a row below.

## Decision log

| # | Date | Decision | Why / who |
|---|---|---|---|
| 1 | 2026-11-21 | Build as a single-file, client-side HTML tool in this repo | Repo conventions (CLAUDE.md): no build step, works offline, data never leaves the browser |
| 2 | 2026-11-21 | **5 BC quarter credits = 1.0 HS credit** (0.2 HS credit per college credit) | OSPI toolkit p. 18 (RCW 28A.230.740 / WAC 180-51-050) and the Riverview equivalency table both say so. We considered 0.5 and rejected it; the user chose to follow OSPI guidance. |
| 3 | 2026-11-21 | **HS classes are entered as semesters:** 1 semester = 0.5 credit, 2 semesters (a year) = 1.0 | User decision. Matches how Cedarcrest transcripts work, and students count classes rather than credits. |
| 4 | 2026-11-21 | HS requirements follow the Cedarcrest catalog (Classes of 2027–2030): English 4, Math 3, Science 3 (2 lab), World History 1, US History 1, Civics 0.5, social studies elective 0.5, Arts 2 (1 can be PPR), World Language 2 (both can be PPR), Health 0.5, PE 1.5, CTE 1, Electives 4 = 24 | User asked to use OSPI guidance and the CHS counseling page. Every total stays editable so other class years and Personal Pathway Requirement (PPR) choices can be handled. |
| 5 | 2026-11-21 | Non-credit requirements are a checklist: WA State History (default met, since RSD covers it in 7th grade; HIST 214 also counts), financial literacy, HSBP, Graduation Pathway | Catalog p. 5 and OSPI toolkit |
| 6 | 2026-11-21 | The Graduation Pathway (Dual Credit) is **detected automatically**: ≥1.0 HS credit from a 100+ Running Start course credited as English meets ELA, and the same for math. Checkboxes cover other ways (tests, SAT/ACT, AP/IB, CTE sequence). | OSPI toolkit p. 18 |
| 7 | 2026-11-21 | Social studies elective accepts RS **HIST, POLS, ECON, PSYC, GEOG** | **Inference, to verify with a counselor.** The catalog's SS electives are Economics, Global Issues, Law & Business Ethics, Psychology and AP Human Geography; the RS sheet doesn't list an SS elective. |
| 8 | 2026-11-21 | HS lab science counts an RS course as lab only if the BC worksheet marks it **(L)** | Only source that flags labs |
| 9 | 2026-11-21 | Each course counts **once per credential**, but the same course can count for both the HS and the AA | That is the point of dual credit. Within each credential, a local-search optimizer decides placement to minimize unmet requirements, so the student doesn't have to. |
| 10 | 2026-11-21 | Extra HS credits in any subject spill into HS electives | Standard transcript practice |
| 11 | 2026-11-21 | Encode all BC AA rules: 2 subjects per distribution, NS lab, ≤5 performance (*) credits and ≤5 credits of one 100-level language in Humanities, ≤5 MATH/PHIL 120 credits in NS, ≤3 PE activity credits, ≤15 restricted credits, Diversity course, 90 total | BC worksheet |
| 12 | 2026-11-21 | **Requirement map is the primary UI:** one card per requirement, listing *every* qualifying course from both source documents; click to add or remove | User asked for a complete set of options and a selection area. Cards beat a matrix on phones. |
| 13 | 2026-11-21 | Badges: **Required** (specific course or list), **Flexible** (credits any course fills), **✓ Met** (more picks optional). Text like "pick 1 of 4" or "POLS 202 is the only option" is computed live. | User asked to show what's required vs. optional |
| 14 | 2026-11-21 | Chip states: green = counts on this card; dashed blue = in plan but counted elsewhere; plain = not in plan; ✓ completed, ◐ in progress; **2×** = counts for an HS subject and an AA distribution | Makes double-dipping visible at a glance |
| 15 | 2026-11-21 | Course status: Planned → In progress → Completed, edited in the course list. Chip clicks only add or remove *Planned* courses. | "Update as we go" without accidentally deleting finished work |
| 16 | 2026-11-21 | State is saved in `localStorage` **and** the URL hash, so a shared link carries the whole plan | No accounts or servers. A link can be shared with a counselor or parent. |
| 17 | 2026-11-21 | Suggestions and auto-fill use a curated ~60-course catalog, rank by requirements filled, honor simple prerequisites (ENGL 101 → 2xx, language and math sequences), and cap credits per quarter (default 15; Fall, Winter and Spring only) | Running Start funding norms. Not a substitute for placement or advising. |
| 18 | 2026-11-21 | **Mobile and tablet are first-class:** stacked course cards under 640px, 16px inputs (no iOS zoom), larger tap targets on touch screens, a filter bar pinned only within the requirement map, a toast explaining where a tapped course counts (hover tooltips don't exist on touch), and chips that act on pointer-up so a redraw mid-tap can't swallow the tap | User requirement. Tested on emulated iPhone 13 and iPad (portrait and landscape). |
| 19 | 2026-11-21 | Course availability by quarter is a **future goal**. For now each course links to the BC catalog and to ctcLink class search. | See the roadmap below |
| 20 | 2026-11-21 | **AP is split into two things.** The AP *class* counts toward the diploma as Cedarcrest semesters, like any HS class. The AP *exam score* is entered separately (exam + score) and becomes BC courses with status "AP exam credit". | User asked to cover AP. Keeping them separate avoids double-counting HS credit, because the class already earned it. |
| 21 | 2026-11-21 | AP exam credit counts toward the **AA only** (0 HS credit) and is graded "S" | BC AP chart. Exam credit appears on the BC transcript as S and doesn't affect GPA. |
| 22 | 2026-11-21 | Score → course mapping follows the BC chart. Where the chart lists more courses than its credit total covers (e.g. US History 3/4: "HIST 146, 147 = 5 cr"; Statistics: "MATH 130, BA 240 = 5 cr"), the tool awards the first course(s) that fit and shows the chart's note. "Elective" awards become `ELECT 1XX`, and "no BC equivalent" becomes `HUMAN 1XX` / `PHYS 1XX` in the chart's stated distribution. | The chart is ambiguous there; BC Evaluations decides the final course |
| 23 | 2026-11-21 | Enforce **max 15 elective credits with a P/S grade** and **≥30 credits completed at BC** (AP exam credit doesn't count toward the 30) | BC AA-DTA worksheet |
| 24 | 2026-11-21 | Warn when the same course is both AP-awarded and taken at BC, and don't suggest courses already covered by AP | BC chart: "No credit will be given if the same course is taken at BC" |
| 25 | 2026-11-21 | An AP exam score of 3+ on an OSPI-approved ELA or math exam marks that part of the Graduation Pathway as met automatically. The course-based AP route (C+ each term) stays a manual checkbox, since the tool doesn't track HS grades. | OSPI toolkit p. 18–19 |
| 26 | 2026-11-21 | **Cedarcrest classes are entered as a class list** (name, requirement, semesters, grade 9–12, status Completed / In progress / Committed, lab flag for science) instead of one semester total per subject. Requirement cards add the list up and show the in-progress and committed parts separately. The summary says "Complete" only when every contributing HS class and college course is completed, and "On track" when the plan meets everything but some items are still pending. Old per-subject totals are migrated to "Earlier HS classes" rows. | User asked for a place to record what's completed or committed for current HS sessions. Supersedes the input part of #3; 1 semester = 0.5 credit still applies. |

## How it works (implementation notes)

- **Parsing:** `parseCode()` normalizes `ENGL& 101`, `engl 101` and `DRAMA 101` → `ENGL 101` / `DRMA 101`.
- **Course data:** `enrich()` turns a course into the lists of HS categories (`hs`) and AA areas (`aa`) it qualifies for, plus flags: lab, performance, diversity, transferable, restricted.
- **Scoring:** `hsEval()` and `aaEval()` score an assignment as a "deficit" in college-credit units. Missing distribution credits count fully, while missing total and elective credits are down-weighted, so the optimizer and suggestions favor courses that fill specific requirements.
- **Placement:** `optimize()` is a hill climb with single moves and, for the full solve, pair swaps. With ~25–30 courses it runs in milliseconds.
- **Option lists:** `universe()` is every course code named on the BC worksheet or the RS sheet. Requirement cards filter it, and user-entered courses outside it are merged in.

## Known limitations

- IB and Cambridge exam credit aren't modeled yet. BC publishes an IB chart, and OSPI lists approved IB/Cambridge exams, so the same pattern as AP would work.
- AP credit is accepted differently at 4-year universities (BC's chart warns about ENGL& 101 in particular). The tool shows BC's treatment only.

- The tool doesn't check Cedarcrest's math sequence rule (Algebra 1 + Geometry, third credit aligned to the HSBP) or the CADR college-admission columns.
- Credits are assumed to be 5 per course. Edit the course list for exceptions such as PE activity courses.
- Cross-listed BC courses (e.g. PHIL 201 = POLS 201) aren't detected, so don't enter both.
- The BC College Success requirement (FYS 101, etc.) is only shown as advisory; whether it applies to Running Start students is unconfirmed.
- The page is longer than the repo's ~300-line guideline because it carries the full requirement data. Splitting the auto-planner into its own tool is an option.

## Roadmap: course availability by quarter (future goal)

**Goal:** when planning, show which quarters each BC course is actually offered, either historically (e.g. "usually Fall and
Spring") or for the current or upcoming quarter. Then warn when a course is planned in a quarter it doesn't run, and
let auto-fill respect that.

**Findings (2026-11-21):**
- `bellevuecollege.edu/classes/` now redirects to **ctcLink** (the statewide PeopleSoft Campus Solutions system) public class search. The schedule is search-driven per term, with no static per-quarter pages.
- The old per-quarter URLs (e.g. `/classes/Winter2019/CMST`) return a Cloudflare 403 to automated requests.
- There is no documented public JSON API or data feed for ctcLink class sections. The BC WordPress REST API covers web content only.
- A browser-side fetch from GitHub Pages to ctcLink or BC would be blocked by CORS even if an endpoint existed.

**Options, in order:**

1. **Phase 1 (done):** deep links. Each course in the list links to the BC catalog search and to ctcLink class search, and the plan section reminds students to confirm quarters before registering. Zero maintenance, always current, works on phones.
2. **Phase 2 (recommended next):** a curated offerings file, `running-start-offerings.json`, committed next to the page and loaded with a same-origin `fetch()` (the F1 tracker's `f1-tracker-news-cache.json` already follows this pattern). Students, parents or counselors record what they saw in class search each quarter, and history builds up over time. The page would show "Offered: F W Sp" on chips and in the course list, warn on mismatches, and let auto-fill skip quarters where a course didn't run. Proposed schema:

   ```json
   {
     "updated": "2026-11-21",
     "source": "ctcLink class search, observed manually",
     "terms": ["Fall 2025", "Winter 2026", "Spring 2026", "Fall 2026"],
     "offerings": {
       "ENGL 101": { "Fall 2025": 24, "Winter 2026": 22, "Spring 2026": 18, "Fall 2026": 25 },
       "HIST 214": { "Winter 2026": 1, "Spring 2026": 1 }
     }
   }
   ```

   Values are the number of sections, or `0` for "checked, not offered". An empty or missing entry means unknown.
   The page must keep working when the file is absent (offline, or a fork without it).
3. **Phase 3 (only with permission):** automate Phase 2's file with a scheduled GitHub Action that queries ctcLink public class search per term. Before building it, ask Bellevue College / SBCTC ctcLink support whether a public data feed exists or scraping is acceptable under their terms. Respect rate limits, and don't work around Cloudflare protections. If an official feed exists, prefer it.

**Open questions for Phase 2/3:**
- Who maintains the offerings file each quarter: the student, a parent, or a counselor?
- Should the summer quarter be tracked? Running Start generally doesn't fund it, but students sometimes self-pay.
- Should section modality (online, hybrid, in person) and time of day matter for a Running Start schedule that shares days with Cedarcrest?

## Testing checklist

- Opens with no console errors. A plan built with auto-fill reaches "Complete" for both credentials.
- Chip tap adds and removes a course, including right after editing a number field (blur re-render case).
- Phone (390px) and tablet (810px and 1080px) have no horizontal scroll, and chips are ≥40px tall on touch.
- Old share links that used `hsPrior` credits or `hsSem` semesters still load (they're migrated to "Earlier HS classes" rows).
- A Cedarcrest class marked In progress or Committed shows separately on its card, and the summary says "On track" (not "Complete") until it's marked Completed.
- AP: Calculus AB 5 → MATH 151 + 152 (10 cr) and meets the math pathway. English Lang 4 → ENGL 101 and meets ELA. Adding ENGL 101 at BC too shows the no-double-credit warning. More than 15 cr of AP electives is capped at 15.
