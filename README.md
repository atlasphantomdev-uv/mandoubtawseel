# مندوب توصيل | Mandoub Tawseel — UAE delivery site

Arabic-first, SEO-driven landing site for a UAE courier/delivery business
(**مندوب توصيل** / **مندوب التوصيل**). Built with Hugo 0.168 + Hugo Blox,
deployed to GitHub Pages. Arabic owns the site root; English mirrors it under `/en/`.

- **Live:** <https://atlasphantomdev-uv.github.io/mandoubtawseel/>
- **Build target:** 46 Arabic pages + 13 English pages (48 HTML files incl. 8 hamza alias redirects)
- **Output:** static HTML/CSS/JS, no server, no database, no runtime secrets

---

## Target keywords (evidence-based, not guessed)

Keyword map built from Google Autocomplete (`hl=ar&gl=ae`) and live SERP checks.

| Type | Keywords | Target page |
|---|---|---|
| Core | مندوب توصيل · مندوب التوصيل | `/` |
| Commercial | شركة توصيل · خدمة توصيل · أسعار مندوب التوصيل | `/اسعار-مندوب-التوصيل/` |
| Cities | مندوب توصيل في دبي · أبوظبي · الشارقة · عجمان · رأس الخيمة · الفجيرة · أم القيوين · العين | `/مندوب-توصيل-في-<city>/` |
| Routes | مندوب توصيل من دبي للعين · دبي إلى أبوظبي · الشارقة إلى أبوظبي | `/خطوط-التوصيل/` |
| Services | توصيل طلبات مطاعم · مستندات · سيارات · فوري · نفس اليوم · رخيص · تطبيق | `/خدمات/` |
| Jobs | وظائف مندوب توصيل · انضم كمندوب | `/وظائف-مندوب-توصيل/` |
| Informational | ما هو مندوب التوصيل · كيف أصبح مندوب توصيل | `/مدونة/` |

SERP finding: the generic head term **مندوب توصيل** is held by government
(mohre.gov.ae, tamm.abudhabi) and app-store brands, not small companies. The site
therefore competes on **مندوب التوصيل**, **شركة توصيل**, and city-intent phrases.

---

## Site architecture

```
/                                     Arabic home (ar-ae, RTL)
├── خدمات/                            7 service pages + index
├── مندوب-توصيل-في-<city>/           8 city pages (+ hamza aliases)
├── خطوط-التوصيل/                     inter-emirate routes + 6 route pages
├── اسعار-مندوب-التوصيل/              pricing
├── مناطق-التغطية/                    coverage
├── وظائف-مندوب-توصيل/ + انضم-كمندوب/  jobs + apply
├── مدونة/                            4 informational articles
└── /en/                              English mirror (hreflang reciprocal)
```

Block order per landing page (two dark blocks may never be adjacent):
`hero (dark) → booking panel (light) → service cards → pricing → 7 steps →
testimonials → UAE map → FAQ → CTA (dark)`.

---

## Quick start

```bash
pnpm install            # Tailwind CLI + Pagefind
pnpm dev                # hugo server --disableFastRender → http://localhost:1313
pnpm build              # hugo --minify && pagefind --site public
python3 scripts/seo_check.py   # static SEO assertions over public/
```

Requirements: **Hugo extended 0.168.0** (extended is mandatory — the theme calls
`css.TailwindCSS`), Node ≥ 20, pnpm 10.

---

## Layout of the repo

| Path | What lives there |
|---|---|
| `config/_default/` | `hugo.yaml` (languages, sitemap, security), `languages.yaml`, `menus.yaml`, `params.yaml` (brand, SEO, analytics, verification) |
| `content/ar/`, `content/en/` | Page bundles; landing pages are front-matter block lists |
| `layouts/` | Project overrides of Blox partials (`baseof.html`, `landing_page.html`, `blox/preact-wrapper.html`, `jsonld/main.html`, `site_head.html`, `components/coverage-links.html`) |
| `assets/css/`, `assets/js/` | Design-system CSS and the map block (RTL corrections, sub-path URL resolution) |
| `data/i18n/rtl.yaml` | Locales that render `dir="rtl"` |
| `scripts/seo_check.py` | Post-build indexing assertions (stdlib only) |
| `hugoblox.yaml` | `hugo_version` + `deploy.host` read by CI |

### Non-obvious constraints (do not "fix" these)

- `removePathAccents: false` — otherwise Hugo NFKD-strips the hamza and rewrites
  Arabic filenames (`وظائف` → `وظايف`), breaking every internal link.
- `disableAliases: false` — meta-refresh alias pages are the only redirect
  mechanism GitHub Pages offers for `أبوظبي` vs `ابوظبي`.
- Front-matter URLs are not passed through `relURL` by the theme's JS blocks; the
  base path comes from `data-hbb-relurl` on `<html>` and is applied by
  `assets/js/hbx/blocks/map/component.jsx` + `layouts/_partials/components/coverage-links.html`.
- The hero is a client-rendered Preact block. `layouts/_partials/blox/preact-wrapper.html`
  emits a `<noscript>` copy server-side so crawlers and no-JS readers still get the
  page `<h1>`. Preact replaces it on hydration — one `<h1>` in the live DOM.
- Site search is **disabled** (`hugoblox.search.enable: false`): landing pages are
  Preact block lists, so Pagefind only indexes the 4 static blog articles. Re-enable
  when a server-rendered content section exists.
- `TODO_*` strings are banned from JSON-LD; `layouts/_partials/jsonld/main.html`
  drops any node value that still carries a placeholder.

---

## Deployment

Push to `main` → `.github/workflows/deploy.yml` → reusable `build.yml` →
`actions/upload-pages-artifact` → `actions/deploy-pages`.

```
config job      reads deploy.host from hugoblox.yaml (github-pages | netlify | vercel | cloudflare | none)
build job       pnpm install → hugo --minify --baseURL <pages url> → pagefind → upload artifact
deploy job      actions/deploy-pages, environment: github-pages
```

Pages must be set to **Source = GitHub Actions** (not "Deploy from a branch").
This repo is already configured that way (`build_type: workflow`), verified via
`gh api repos/atlasphantomdev-uv/mandoubtawseel/pages`.

```bash
# Re-check / re-apply the Pages source
gh api repos/atlasphantomdev-uv/mandoubtawseel/pages --jq .build_type
gh api -X PUT repos/atlasphantomdev-uv/mandoubtawseel/pages -f build_type=workflow
```

`netlify.toml` is kept as an alternative target (`deploy.host: netlify`).

---

## Business data

All `TODO_*` placeholders are gone. These values are now wired:

| Fact | Value | Where |
|---|---|---|
| WhatsApp (all CTAs) | `+971 52 789 0094` → `https://wa.me/971527890094` | every hero, pricing tier, FAQ, CTA, jobs block |
| Phone (`tel:` link) | `+971527890094` | `contact-info` blocks, `hugoblox.seo.location.phone`, JSON-LD `telephone` |
| Brand | `Mandoub Tawseel` (EN) / Arabic page titles carry مندوب توصيل | `params.yaml → identity.name`, `languages.yaml → title` |
| Service base | دبي، الإمارات العربية المتحدة / Dubai, UAE | `contact-info` blocks, JSON-LD `PostalAddress` (city/region/country only, no street) |
| Hours | يوميًا 8:00 صباحًا – 11:00 مساءً / Daily 8:00–23:00 | `contact-info` blocks |
| Pricing | Tier 1 = 15 AED (client-approved); tiers 2–3 show their `price_note` instead of a number | pricing blocks, JSON-LD `priceRange: AED 15+` |
| Earnings, transit times | Qualitative only ("حسب عدد الطلبات والمسافة") | jobs pages, route pages |

Generated defaults to review before spending on ads: brand name, service base
(no street address), opening hours, and the tier-2/3 price notes. Change them in
`config/_default/params.yaml` + the page front matter; nothing else needs touching.

Two deliberate omissions:

- **No testimonials.** The brief allows no invented customer reviews, so the block
  was removed from all 19 landing pages. Add it back with real reviews only.
- **No booking form.** No form endpoint exists, so `show_form: false` everywhere and
  the panel funnels to WhatsApp. To enable: set `show_form: true` and `form_action`
  to a real endpoint (Formspree etc.) in the `contact-info` blocks.

Re-check for regenerated placeholders any time with:

```bash
grep -rho "TODO_[A-Z_]*" content config | sort | uniq -c   # expect no output
```

---

## Indexing playbook

### Already automated

- Self-referencing `canonical` on every page (`layouts/_partials/site_head.html`).
- Reciprocal `hreflang` (`ar-ae`, `en-us`) + `x-default` → Arabic root.
- `sitemap.xml` index → `/ar/sitemap.xml` (34 URLs) and `/en/sitemap.xml` (6 URLs).
- `robots.txt` allows all and advertises the sitemap.
- JSON-LD `@graph`: `WebSite`, `LocalBusiness`, `Service`, `WebPage`,
  `BreadcrumbList`, `FAQPage`, `BlogPosting`.
- Taxonomies with no content disabled (`disableKinds: [taxonomy]`) so no thin
  `/tags/` pages get indexed.
- Skip link, RTL-correct tracking/line-height, keyboard-reachable coverage links.

### Operator steps (one time, after deploying with real data)

1. **Google Search Console** — add the URL-prefix property
   `https://atlasphantomdev-uv.github.io/mandoubtawseel/`, verify with the HTML tag
   value in `params.yaml → hugoblox.verification.google`, then submit
   `https://atlasphantomdev-uv.github.io/mandoubtawseel/sitemap.xml`.
2. **Bing Webmaster Tools** — import from GSC (`hugoblox.verification.bing`).
   Bing powers DuckDuckGo and ChatGPT search.
3. **IndexNow — already automated.** `static/5bf46cfe551b44f7bd2570708a76b4ed.txt`
   is the key; the deploy job pings IndexNow for the 16 priority URLs after every
   successful Pages deploy. Rotate by replacing that file (name must equal its
   content) — no workflow edit needed, the step globs `static/*.txt`.
4. **Analytics** — `params.yaml → hugoblox.analytics.google.measurement_id` (GA4).
   Nothing loads until an ID is set.
5. **Google Business Profile** — for a local courier the map pack outranks organic;
   the address/phone in `hugoblox.seo.location` must match the profile exactly.
6. **Reviews** — only real, attributable ones. Empty is better than invented; the
   testimonials block should be removed until they exist.

### Why the sub-path URL is a limit

`github.io/…/mandoubtawseel/` cannot win Arabic brand queries the way a domain can.
Moving to a custom domain is a `static/CNAME` + `baseURL` change plus DNS; canonicals,
sitemap and hreflang follow automatically from `baseURL`/`configure-pages`.

---

## Verification

```bash
hugo --minify                 # 0 errors, 0 warnings
python3 scripts/seo_check.py  # 0 errors; warnings should be empty
```

`seo_check.py` asserts, per built page: exactly one `<h1>`, a canonical, a meta
description, parseable JSON-LD with no `TODO_`, and reciprocal `hreflang`.
Exit code 1 means an indexing regression — do not deploy over it.

---

## License

Code: MIT (`LICENSE.md`). Content and business copy belong to the site owner.
