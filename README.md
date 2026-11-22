# FloSync AI — SaaS starter

A deployable starting point for a multi-tenant AI business assistant. Includes a Next.js dashboard, Supabase email/password authentication, an authenticated server-side OpenAI Responses API endpoint, and an initial organization/lead/task schema with Row Level Security.

## What works in this starter

- Account creation and sign-in using Supabase Auth.
- One private organization/workspace provisioned for each new user.
- AI assistant chat through the OpenAI Responses API.
- Server-side API key handling (the OpenAI key is never sent to the browser).
- Initial multi-tenant tables for leads, tasks, and usage events, protected with RLS.

## What is not implemented yet

This is an MVP foundation, not a finished commercial SaaS. It does not yet include Stripe checkout/webhooks, a full CRM/task UI, n8n workflow execution, invitation/team management, usage enforcement, audit logs, data export/deletion flows, or production monitoring. Sidebar items marked “SOON” are placeholders. Do not sell it as having those capabilities until built and tested.

## Requirements

- Node.js 20.9+
- An OpenAI API project and API key
- A Supabase project

## Run locally

1. Extract the ZIP and open a terminal in the project folder.
2. Install dependencies:

   ```bash
   npm install
   ```
3. Copy `.env.example` to `.env.local` and fill in:
   - `OPENAI_API_KEY` from the OpenAI Platform
   - `OPENAI_MODEL` (default `gpt-5-mini`; choose a model enabled for your API project)
   - `NEXT_PUBLIC_SUPABASE_URL`
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY` (Supabase project publishable/anon key)
4. In Supabase → SQL Editor, run `supabase/migrations/001_initial_schema.sql`.
5. In Supabase Auth settings, configure your site URL and allowed redirect URLs for local development (`http://localhost:3000`) and your deployed domain.
6. Start the app:

   ```bash
   npm run dev
   ```

7. Open http://localhost:3000 and create an account. If email confirmation is enabled, confirm the email before signing in.

## Deploy to Vercel

1. Push this project to a private GitHub repository.
2. In Vercel, import the repository.
3. Add the four environment variables from `.env.example` in Project Settings → Environment Variables. Do not add secrets to `NEXT_PUBLIC_` variables.
4. Deploy.
5. Add your production domain to Supabase Auth's Site URL and Redirect URLs.
6. Test signup, sign-in, sign-out, and AI chat on the production domain.

## Security checklist before paid launch

- Keep `OPENAI_API_KEY` server-side only. Never prefix it with `NEXT_PUBLIC_`.
- Keep Supabase service-role/secret keys out of the frontend. This starter does not need one.
- Review RLS policies with separate test accounts and verify one workspace cannot access another.
- Add rate limiting, per-plan usage limits, request-size limits, abuse monitoring, and cost alerts.
- Add billing only after Stripe webhook signature verification and subscription state enforcement are implemented server-side.
- Add audit logs and explicit confirmation for external side effects (sending messages, refunds, deleting records, payments).
- Publish Terms, Privacy Policy, cancellation/refund terms, and a clear AI limitations notice.
- Do not connect sensitive health, legal, financial, or employment decision workflows without domain-specific security and compliance review.

## Suggested next milestones

1. CRM and task management screens using the existing RLS-protected tables.
2. Organization settings, team invites, and role-based permissions.
3. Stripe subscriptions + signed webhooks + server-enforced plan entitlements.
4. n8n integration with signed webhooks, allowlisted workflows, retries, and execution logs.
5. Approved AI tools for creating tasks/leads; require human approval before external actions.
6. Usage metering, analytics, observability, backups, and production security review.

## Phase 2: CRM and task management

This update adds:
- `/customers`: create, list, update pipeline status, and delete customer/lead records.
- `/tasks`: create, list, update task status, and delete tasks.
- Authenticated API routes for both modules. Every query is scoped to the signed-in user's workspace and also protected by the original Supabase RLS policies.
- A workflow registry, workflow-run history, and audit-log schema in `supabase/migrations/002_operations_and_automation.sql`. These tables are groundwork only; this release does not execute external automations.

### Apply Phase 2

1. Commit or back up your current project.
2. In Supabase SQL Editor, run `002_operations_and_automation.sql` after migration 001.
3. Replace/add the files from this update in your project.
4. Run `npm install`, then `npm run dev`.
5. Sign in and open `/customers` and `/tasks` from the dashboard.
6. Test with two separate user accounts. Confirm that each account sees only its own workspace data.

### Claude AI instructions

Upload the updated project ZIP to Claude and ask it to review the repository before editing. Use the prompt in `CLAUDE_NEXT_STEPS.md`. Do not paste secret keys into Claude or commit `.env.local`.

### Remaining production milestones

This Phase 2 update does not yet include Stripe billing, team invitations, workflow execution, external integrations, usage enforcement, email notifications, or production-grade rate limiting. Build and test those in later phases before accepting paying customers. The workflow tables are not an execution engine.
