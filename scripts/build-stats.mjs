/**
 * Render the stats panel as an SVG in this repo.
 *
 * The profile used to embed two cards from a github-readme-stats instance on
 * somebody's Vercel account. That instance ran out of GitHub API quota, so what
 * the profile actually displayed was two white boxes reading "Something went
 * wrong! … Please add an env variable called PAT_1 with your github token in
 * vercel" — an error message about someone else's deployment, sitting in the
 * middle of the page, in the one place a visitor looks for evidence.
 *
 * Built here instead: the numbers come from the GitHub API with this account's
 * own token, the palette is the one the rest of the page uses, and the weekly
 * workflow keeps it current. Nothing to rate-limit and nothing to go down.
 *
 * Needs a token with public repo read: GH_TOKEN or GITHUB_TOKEN.
 */

import { mkdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const USER = "North-web-dev";
const OUT = join(process.cwd(), "assets");

const C = {
  panelTop: "#1c1026",
  panelBottom: "#120a17",
  edge: "#3a1c33",
  beni: "#d9455f",
  gold: "#e6a23c",
  sakura: "#f5a9c1",
  title: "#f6ebf0",
  body: "#c7abbb",
  faint: "#8d7186",
};

/* GitHub's own language colours for the ones that actually appear here; the
   API supplies the rest. Pinned so the bar keeps its palette even if a
   language's official colour changes under it. */
const LANG_COLOR = {
  Go: "#00ADD8",
  Python: "#3572A5",
  TypeScript: "#3178c6",
  JavaScript: "#f1e05a",
  "C++": "#f34b7d",
  Rust: "#dea584",
  HTML: "#e34c26",
  CSS: "#563d7c",
  Shell: "#89e051",
};

const QUERY = `
  query($user: String!) {
    user(login: $user) {
      followers { totalCount }
      contributionsCollection {
        contributionCalendar { totalContributions }
      }
      repositories(first: 100, ownerAffiliations: OWNER, isFork: false) {
        totalCount
        nodes {
          isPrivate
          stargazerCount
          languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
            edges { size node { name color } }
          }
        }
      }
    }
  }`;

function escapeXml(text) {
  return String(text).replace(
    /[<>&'"]/g,
    (c) => ({ "<": "&lt;", ">": "&gt;", "&": "&amp;", "'": "&apos;", '"': "&quot;" })[c],
  );
}

function statRow(x, y, label, value, accent) {
  return `<g transform="translate(${x},${y})">
      <rect width="4" height="34" rx="2" fill="${accent}"/>
      <text x="18" y="16" font-size="24" font-weight="700" fill="${C.title}">${escapeXml(value)}</text>
      <text x="18" y="31" font-size="11.5" font-weight="600" letter-spacing="1.6" fill="${C.faint}">${escapeXml(label)}</text>
    </g>`;
}

function panel(data) {
  const repos = data.repositories.nodes;
  const stars = repos.reduce((sum, r) => sum + r.stargazerCount, 0);
  const publicRepos = repos.filter((r) => !r.isPrivate).length;
  const contributions = data.contributionsCollection.contributionCalendar.totalContributions;
  const followers = data.followers.totalCount;

  const W = 1000;
  const H = 230;
  const barX = 452;
  const barW = W - barX - 40;
  const barY = 92;

  /* Bytes per language across every repository this account owns, private
     included — the shape of the work, not the shape of the public half. */
  const bytes = new Map();
  for (const repo of repos) {
    for (const edge of repo.languages.edges) {
      const name = edge.node.name;
      bytes.set(name, (bytes.get(name) ?? 0) + edge.size);
      if (!LANG_COLOR[name] && edge.node.color) LANG_COLOR[name] = edge.node.color;
    }
  }
  const total = [...bytes.values()].reduce((a, b) => a + b, 0) || 1;
  const top = [...bytes.entries()].sort((a, b) => b[1] - a[1]).slice(0, 6);


  let cursor = barX;
  const drawn = top
    .map(([name, size]) => {
      const width = Math.max(3, (size / total) * barW);
      const seg = `<rect x="${cursor.toFixed(1)}" y="${barY}" width="${width.toFixed(1)}" height="14" fill="${LANG_COLOR[name] ?? C.sakura}"/>`;
      cursor += width;
      return seg;
    });

  /* Everything past the top six, so the bar reaches its own right edge
     instead of stopping short with a rounded cap over nothing. */
  const rest = barX + barW - cursor;
  if (rest > 0.5) {
    drawn.push(
      `<rect x="${cursor.toFixed(1)}" y="${barY}" width="${rest.toFixed(1)}" height="14" fill="${C.faint}" opacity="0.5"/>`,
    );
  }
  const segments = drawn.join("\n      ");

  const legend = top
    .map(([name, size], i) => {
      const col = i % 2;
      const row = Math.floor(i / 2);
      const x = barX + col * 176;
      const y = barY + 44 + row * 26;
      const share = ((size / total) * 100).toFixed(1);
      return `<g transform="translate(${x},${y})">
        <circle cx="6" cy="-4" r="5" fill="${LANG_COLOR[name] ?? C.sakura}"/>
        <text x="20" y="0" font-size="12.5" font-weight="600" fill="${C.body}">${escapeXml(name)}</text>
        <text x="126" y="0" font-size="12" fill="${C.faint}">${share}%</text>
      </g>`;
    })
    .join("\n      ");

  return `<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" fill="none" xmlns="http://www.w3.org/2000/svg"
     role="img" aria-label="${stars} stars across ${data.repositories.totalCount} repositories, ${contributions} contributions in the last year, ${followers} followers"
     font-family="'Segoe UI','Helvetica Neue',system-ui,sans-serif">
  <defs>
    <linearGradient id="sbg" x1="0" y1="0" x2="0.35" y2="1">
      <stop offset="0" stop-color="${C.panelTop}"/><stop offset="1" stop-color="${C.panelBottom}"/>
    </linearGradient>
    <radialGradient id="sglow" cx="6%" cy="0%" r="60%">
      <stop offset="0" stop-color="${C.beni}" stop-opacity="0.22"/><stop offset="1" stop-color="${C.beni}" stop-opacity="0"/>
    </radialGradient>
    <clipPath id="sclip"><rect width="${W}" height="${H}" rx="16"/></clipPath>
    <clipPath id="sbar"><rect x="${barX}" y="${barY}" width="${barW}" height="14" rx="7"/></clipPath>
  </defs>

  <g clip-path="url(#sclip)">
    <rect width="${W}" height="${H}" rx="16" fill="url(#sbg)"/>
    <rect width="${W}" height="${H}" fill="url(#sglow)"/>
    <text x="${W - 26}" y="${H - 18}" text-anchor="end" font-size="96" font-weight="700" fill="${C.sakura}" opacity="0.05">記録</text>
    <rect width="5" height="${H}" fill="${C.beni}"/>
  </g>
  <rect x="0.5" y="0.5" width="${W - 1}" height="${H - 1}" rx="16" fill="none" stroke="${C.edge}"/>

  <text x="40" y="44" font-size="13" font-weight="700" letter-spacing="3" fill="${C.sakura}" opacity="0.85">RECORD</text>

  ${statRow(40, 72, "STARS EARNED", String(stars), C.gold)}
  ${statRow(230, 72, "REPOSITORIES", String(data.repositories.totalCount), C.beni)}
  ${statRow(40, 140, "CONTRIBUTIONS · 1Y", String(contributions), C.sakura)}
  ${statRow(230, 140, "FOLLOWERS", String(followers), C.gold)}

  <line x1="420" y1="40" x2="420" y2="${H - 40}" stroke="${C.edge}"/>

  <text x="${barX}" y="${barY - 18}" font-size="13" font-weight="700" letter-spacing="3" fill="${C.sakura}" opacity="0.85">LANGUAGES</text>
  <text x="${barX + barW}" y="${barY - 18}" text-anchor="end" font-size="11" fill="${C.faint}">by bytes · private repos included</text>
  <g clip-path="url(#sbar)">
    ${segments}
  </g>
  <rect x="${barX}" y="${barY}" width="${barW}" height="14" rx="7" fill="none" stroke="${C.edge}"/>

  <g>
    ${legend}
  </g>
</svg>
`;
}

async function main() {
  const token = process.env.GH_TOKEN || process.env.GITHUB_TOKEN;
  if (!token) {
    console.error("Set GH_TOKEN (or GITHUB_TOKEN) to a token that can read this account.");
    process.exit(1);
  }

  const res = await fetch("https://api.github.com/graphql", {
    method: "POST",
    headers: { Authorization: `bearer ${token}`, "Content-Type": "application/json" },
    body: JSON.stringify({ query: QUERY, variables: { user: USER } }),
  });
  if (!res.ok) throw new Error(`GitHub API ${res.status}: ${await res.text()}`);

  const payload = await res.json();
  if (payload.errors) throw new Error(JSON.stringify(payload.errors));

  mkdirSync(OUT, { recursive: true });
  writeFileSync(join(OUT, "stats.svg"), panel(payload.data.user), "utf8");
  console.log("stats.svg written");
}

await main();
