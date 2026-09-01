/**
 * Render the repository cards on the profile as SVG files in this repo.
 *
 * They used to come from svg.bookmark.style — a third-party renderer fetched
 * fresh on every page view. When it is slow the profile loads with holes in it,
 * when it goes away the profile loses its middle, and either way the look of
 * the page is decided by somebody else's stylesheet rather than the palette
 * everything else here uses.
 *
 * So the cards are built here and committed. `node scripts/build-cards.mjs`
 * reads the live repositories and rewrites assets/cards/*.svg; the weekly
 * workflow runs the same command, so the star counts stay honest without
 * anyone remembering.
 *
 * Needs a token with public repo read: GH_TOKEN or GITHUB_TOKEN.
 */

import { mkdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const USER = "North-web-dev";
const OUT = join(process.cwd(), "assets", "cards");

/** The six the profile leads with, in reading order. */
const FEATURED = [
  "impersonate-http",
  "vfs-monitor",
  "fpcheck",
  "cf-solver",
  "tdata-extract",
  "poolctl",
];

/* The palette the banner established. Kept here rather than in each template
   string so a change of mood is one edit. */
const C = {
  panelTop: "#1c1026",
  panelBottom: "#130a18",
  edge: "#3a1c33",
  beni: "#d9455f",
  gold: "#e6a23c",
  sakura: "#f5a9c1",
  title: "#f6ebf0",
  body: "#c7abbb",
  faint: "#8d7186",
};

const LANG_COLOR = {
  Go: "#00ADD8",
  Python: "#3572A5",
  TypeScript: "#3178c6",
  "C++": "#f34b7d",
  Rust: "#dea584",
  JavaScript: "#f1e05a",
};

const CARD = { w: 560, h: 148, pad: 26 };

function escapeXml(text) {
  return String(text).replace(
    /[<>&'"]/g,
    (c) => ({ "<": "&lt;", ">": "&gt;", "&": "&amp;", "'": "&apos;", '"': "&quot;" })[c],
  );
}

/**
 * Break a description into lines that fit the card.
 *
 * Measured by character width rather than a real font metric: the cards are
 * rendered by GitHub's image proxy with whatever sans it resolves, so an exact
 * measurement would be exact for a font nobody is guaranteed to have. 0.505em
 * per character is the average for this size across the usual system stack,
 * and the card leaves room for the drift.
 */
function wrap(text, maxWidth, fontSize) {
  const perChar = fontSize * 0.505;
  const limit = Math.floor(maxWidth / perChar);
  const words = String(text).split(/\s+/).filter(Boolean);
  const lines = [];
  let line = "";

  for (const word of words) {
    const candidate = line ? `${line} ${word}` : word;
    if (candidate.length <= limit) {
      line = candidate;
      continue;
    }
    if (line) lines.push(line);
    line = word;
  }
  if (line) lines.push(line);
  return lines;
}

function card(repo) {
  const { w, h, pad } = CARD;
  const lang = repo.primaryLanguage?.name ?? null;
  const langColor = lang ? (LANG_COLOR[lang] ?? repo.primaryLanguage?.color ?? C.sakura) : C.faint;

  /* Two lines, and the second one is cut rather than allowed to run into the
     footer row — a card that grows with its description stops being a grid. */
  const wrapped = wrap(repo.description ?? "", w - pad * 2 - 26, 13);
  const lines = wrapped.slice(0, 2);
  if (wrapped.length > 2) lines[1] = `${lines[1].replace(/[,.;:]$/, "")}…`;

  const id = repo.name.replace(/[^a-zA-Z0-9]/g, "");
  const footerY = h - 26;

  return `<svg width="${w}" height="${h}" viewBox="0 0 ${w} ${h}" fill="none"
     xmlns="http://www.w3.org/2000/svg" role="img"
     aria-label="${escapeXml(repo.name)} — ${escapeXml(repo.description ?? "")}"
     font-family="'Segoe UI','Helvetica Neue',system-ui,sans-serif">
  <defs>
    <linearGradient id="bg${id}" x1="0" y1="0" x2="0.4" y2="1">
      <stop offset="0" stop-color="${C.panelTop}"/>
      <stop offset="1" stop-color="${C.panelBottom}"/>
    </linearGradient>
    <radialGradient id="glow${id}" cx="4%" cy="0%" r="70%">
      <stop offset="0" stop-color="${C.beni}" stop-opacity="0.28"/>
      <stop offset="1" stop-color="${C.beni}" stop-opacity="0"/>
    </radialGradient>
    <clipPath id="clip${id}"><rect width="${w}" height="${h}" rx="14"/></clipPath>
  </defs>

  <g clip-path="url(#clip${id})">
    <rect width="${w}" height="${h}" rx="14" fill="url(#bg${id})"/>
    <rect width="${w}" height="${h}" fill="url(#glow${id})"/>
    <!-- beni edge, the same one the section plates carry -->
    <rect width="5" height="${h}" fill="${C.beni}"/>
    <!-- faint horizon line, echoing the banner -->
    <path d="M0 ${h - 46} H${w}" stroke="${C.edge}" stroke-width="1" opacity="0.7"/>
    <g fill="${C.gold}" opacity="0.5">
      <circle cx="${w - 20}" cy="18" r="2"/>
      <circle cx="${w - 32}" cy="28" r="1.4"/>
    </g>
  </g>
  <rect x="0.5" y="0.5" width="${w - 1}" height="${h - 1}" rx="14" fill="none" stroke="${C.edge}"/>

  <text x="${pad}" y="42" font-size="20" font-weight="700" fill="${C.title}">${escapeXml(repo.name)}</text>

  <g font-size="13" fill="${C.body}">
    ${lines
      .map((line, i) => `<text x="${pad}" y="${70 + i * 20}">${escapeXml(line)}</text>`)
      .join("\n    ")}
  </g>

  <g font-size="12.5" font-weight="600">
    ${
      lang
        ? `<circle cx="${pad + 5}" cy="${footerY - 4}" r="5" fill="${langColor}"/>
    <text x="${pad + 18}" y="${footerY}" fill="${C.body}">${escapeXml(lang)}</text>`
        : ""
    }
    <g transform="translate(${lang ? pad + 32 + lang.length * 7.4 : pad}, ${footerY - 11})">
      <path d="M7 0.6 8.9 4.6 13.3 5.2 10.1 8.3 10.9 12.7 7 10.6 3.1 12.7 3.9 8.3 0.7 5.2 5.1 4.6Z"
            fill="${C.gold}" opacity="0.9"/>
      <text x="20" y="11" fill="${C.body}">${repo.stargazerCount}</text>
    </g>
  </g>
</svg>
`;
}

async function main() {
  const token = process.env.GH_TOKEN || process.env.GITHUB_TOKEN;
  if (!token) {
    console.error("Set GH_TOKEN (or GITHUB_TOKEN) to a token that can read public repos.");
    process.exit(1);
  }

  const query = `
    query($user: String!) {
      user(login: $user) {
        repositories(first: 100, privacy: PUBLIC, orderBy: {field: STARGAZERS, direction: DESC}) {
          nodes { name description stargazerCount primaryLanguage { name color } }
        }
      }
    }`;

  const res = await fetch("https://api.github.com/graphql", {
    method: "POST",
    headers: { Authorization: `bearer ${token}`, "Content-Type": "application/json" },
    body: JSON.stringify({ query, variables: { user: USER } }),
  });
  if (!res.ok) throw new Error(`GitHub API ${res.status}: ${await res.text()}`);

  const payload = await res.json();
  if (payload.errors) throw new Error(JSON.stringify(payload.errors));

  const byName = new Map(
    payload.data.user.repositories.nodes.map((repo) => [repo.name, repo]),
  );

  mkdirSync(OUT, { recursive: true });
  for (const name of FEATURED) {
    const repo = byName.get(name);
    if (!repo) {
      /* Loud, not silent: a card that quietly stops being rebuilt is a card
         that shows last year's description forever. */
      console.error(`  ! ${name} is not in the public list — card left as it was`);
      continue;
    }
    writeFileSync(join(OUT, `${name}.svg`), card(repo), "utf8");
    console.log(`  ${name}  ★${repo.stargazerCount}  ${repo.primaryLanguage?.name ?? "—"}`);
  }
  console.log(`cards written to assets/cards/`);
}

await main();
