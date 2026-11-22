# CashFlo

A personal finance + social prototype (Dashboard, Money, Investments, Goals, Social, Messages, AI Assistant, Profile), built with React + Vite and charts via Recharts.

## Run it locally

You'll need [Node.js](https://nodejs.org) (v18+) installed.

```bash
npm install
npm run dev
```

Then open the local URL it prints (usually `http://localhost:5173`).

## Build for production

```bash
npm run build
```

This creates a `dist/` folder with the static site.

## Deploy to Netlify

**Option A — drag and drop (fastest, no account setup beyond signup):**
1. Run `npm run build` locally to create the `dist/` folder.
2. Go to [app.netlify.com/drop](https://app.netlify.com/drop) and drag the `dist` folder in.

**Option B — connect a Git repo (auto-deploys on every push):**
1. Push this project to a GitHub/GitLab/Bitbucket repo.
2. In Netlify: **Add new site → Import an existing project**, connect the repo.
3. Build command: `npm run build`, Publish directory: `dist` (already set in `netlify.toml`).

## Important things to know before treating this as a real product

- **Data storage**: this version uses the browser's `localStorage` for persistence, swapped in from the original Claude-artifact version (which used a sandbox-only API). That means data is local to one browser on one device — nothing is synced between users or devices, and clearing browser data erases it. There is no real backend, database, or authentication.
- **AI Assistant**: the assistant tab calls `api.anthropic.com` directly from the browser. That only worked inside the Claude.ai artifact sandbox, which proxies the request. Deployed standalone, this call will fail (no API key, and Anthropic's API isn't meant to be called with an exposed key from client-side code) and will fall back to a friendly error message. To make it actually work, add your own backend or serverless function (e.g. a Netlify Function) that holds a real Anthropic API key server-side and proxies the request — see the comment above `sendAI()` in `src/App.jsx`.
- **Financial data is simulated**: stock/crypto prices, bank account linking (Cash App, Chime, Venmo, Capital One, Amex), and social "friends" are all demo data — there's no live market feed and no real money movement.
- **Not compliance-reviewed**: this hasn't gone through any legal/regulatory review (money transmission, financial privacy law, investment-advice framing, etc.), which a real financial product handling real user data and real money would need before launch.

## Project structure

```
├── index.html
├── package.json
├── vite.config.js
├── netlify.toml
└── src/
    ├── main.jsx     # React entry point
    └── App.jsx      # The whole app
```
