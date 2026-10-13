# ahmadsalehnasution.github.io

Personal portfolio site for Ahmad Saleh — data, BI and AI operations analyst based in Selangor, Malaysia.
Static HTML, plain CSS, no build step. Served by GitHub Pages from `main`.

## Layout

- `index.html` — single-page profile: about, experience, projects, certifications, research, contact
- `case-ai-evaluation.html` — 2026 case study: evaluating AI answers in Indonesian (60 answers, two configurations)
- `case-gold-my-indicators.html` — 2026 case study: SQL + BI analysis of gold versus Malaysian household indicators
- `case-market-brief-agent.html` — 2026 case study: an agent that writes a cited weekly market brief
- `resume.pdf` — the current CV (Data & BI Analyst variant)
- `projects/<slug>/` — the artefacts behind each case study: SQL files, result tables, source provenance, READMEs
- `assets/` — stylesheet, script, favicon
- `dashboard-fifa.html` — earlier Power BI project page
- `about.html`, `cv.html`, `portfolio*.html`, `resume.html`, `contact.html`, `certification.html` — legacy URLs kept as
  redirects to the matching section of `index.html`

## Editing

Edit the HTML directly, commit to `main`, and GitHub Pages rebuilds within about a minute. There is no framework and
no dependency to install; keeping it that way is deliberate.

## Conventions

- Case studies publish their results, **and their limitations**, together. If a number is not measured, the page says
  so rather than estimating.
- Each project states its status honestly: prototype, personal, or running.
- No claim of time saved or revenue gained anywhere it has not been measured.
