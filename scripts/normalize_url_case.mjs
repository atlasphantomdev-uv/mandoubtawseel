#!/usr/bin/env node
/**
 * Normalize percent-escape hex digits to uppercase in the built HTML.
 *
 * Why this exists (measured 2026-11-18 against production and GSC):
 *   Hugo's `relURL` / `relLangURL` lowercase the percent-encoded path, while
 *   `.Permalink` (used by <link rel=canonical>, hreflang, JSON-LD and the
 *   sitemap) emits uppercase. On this site every Arabic slug is percent-encoded,
 *   so the same page was reachable as two distinct URL strings:
 *
 *     nav link    /mandoubtawseel/%d8%ae%d8%af%d9%85%d8%a7%d8%aa/
 *     canonical   /mandoubtawseel/%D8%AE%D8%AF%D9%85%D8%A7%D8%AA/
 *
 *   GitHub Pages is case-sensitive, so both resolve to a 200. Google merged each
 *   pair into the canonical (uppercase) URL but kept crawling the lowercase twin:
 *   a site audit of 60 crawled pages reported 32 as "canonicalized to another
 *   URL", i.e. over half the crawl budget produced no addressable page.
 *
 *   RFC 3986 §2.1 makes the hex digits case-insensitive, so uppercasing them is
 *   semantically a no-op — it only removes the duplicate URL strings. Doing it
 *   here, once, on the finished output, covers every producer (local partials
 *   and upstream Hugo Blox module templates alike) instead of chasing each
 *   relLangURL call site.
 *
 * Usage:
 *   node scripts/normalize_url_case.mjs [dir]          rewrite in place
 *   node scripts/normalize_url_case.mjs [dir] --check  exit 1 if any remain
 */

import { existsSync, readdirSync, readFileSync, statSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const args = process.argv.slice(2);
const check = args.includes("--check");
const root = args.find((a) => !a.startsWith("--")) || "public";

if (!existsSync(root)) {
  console.error(`ERROR: build directory not found: ${root} — run "hugo" first`);
  process.exit(1);
}

const ESCAPE = /%[0-9a-fA-F]{2}/g;
// Only escapes carrying a lowercase hex letter need work: "%85" is already
// canonical, and treating it as lowercase made the --check gate useless.
const needsUpper = (m) => m !== m.toUpperCase();

function* htmlFiles(dir) {
  for (const entry of readdirSync(dir)) {
    const full = join(dir, entry);
    const st = statSync(full);
    if (st.isDirectory()) yield* htmlFiles(full);
    else if (entry.endsWith(".html")) yield full;
  }
}

let files = 0;
const offenders = [];

for (const file of htmlFiles(root)) {
  const html = readFileSync(file, "utf8");
  const matches = (html.match(ESCAPE) || []).filter(needsUpper);
  if (!matches.length) continue;
  files += 1;
  offenders.push(`${file} (${matches.length})`);
  if (!check) writeFileSync(file, html.replace(ESCAPE, (m) => m.toUpperCase()));
}

if (check) {
  if (files > 0) {
    console.error(
      `ERROR: ${files} built HTML file(s) still contain lowercase percent-escapes:\n` +
        offenders.slice(0, 10).map((o) => `  ${o}`).join("\n"),
    );
    process.exit(1);
  }
  console.log("OK: no lowercase percent-escapes in built HTML");
} else {
  console.log(
    `normalize_url_case: uppercased escapes in ${files} file(s) under ${root}/`,
  );
}
