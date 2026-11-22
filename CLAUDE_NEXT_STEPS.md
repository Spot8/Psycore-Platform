# Claude AI — FloSync implementation brief

You are the senior full-stack engineer working on FloSync AI, a multi-tenant SaaS business operations assistant.

## First: inspect, do not assume
1. Read the entire repository and package.json.
2. Preserve the existing Next.js 15 App Router, TypeScript, Supabase SSR authentication, and OpenAI Responses API architecture.
3. Do not replace working files wholesale without explaining why.
4. Do not claim a feature is complete unless you implement and test it.

## Current Phase 2 functionality
- Authenticated AI assistant.
- Supabase organization provisioning and RLS.
- Customer/lead CRUD at `/customers` and `/api/leads`.
- Task CRUD at `/tasks` and `/api/tasks`.
- Workflow registry and workflow-run schema (not an execution engine).

## Build the remaining milestones in this exact sequence

### Phase 3 — workflow engine (safe, auditable)
- Create workflow CRUD screens and APIs.
- Support manual trigger first; later support signed webhook and scheduled triggers.
- Store workflow steps as validated JSON using a strict allowlist of supported actions.
- Add execution worker integration with n8n using a server-only credential and signed requests.
- Add retries, idempotency keys, timeout handling, run logs, and dead-letter/failure state.
- Require explicit owner/admin approval before any external side effect such as sending email, issuing refunds, deleting data, or charging a payment method.
- Never allow the model to supply arbitrary URLs, SQL, shell commands, or unrestricted code to the worker.

### Phase 4 — integrations
- OAuth-based Gmail and Google Calendar connections with least-privilege scopes.
- Encrypt provider tokens at rest; never return tokens to browser clients or model prompts.
- Add disconnect/revoke flows and clear consent screens.
- Do not send email or create calendar events without the user's explicit approval until per-workspace policies are implemented.

### Phase 5 — SaaS billing
- Stripe Checkout and Customer Portal.
- Verify webhook signatures on the server.
- Store customer/subscription IDs and plan status in Supabase.
- Enforce plan entitlements and monthly usage server-side, not in client code.
- Handle checkout completion, renewals, payment failures, cancellation, and subscription changes idempotently.
- Never store card numbers or CVC values.

### Phase 6 — teams and administration
- Workspace member invitations, role management, and revocation.
- Enforce owner/admin/member permissions in every API and RLS policy.
- Audit important actions and offer customer data export/deletion.

### Phase 7 — production readiness
- Rate limiting, abuse protection, request validation, structured logs, error monitoring, backups, retention controls, accessibility, responsive testing, and security review.
- Add privacy policy, terms, AI limitations, support and cancellation pages.
- Add automated tests for cross-tenant isolation and billing webhook behavior.

## Engineering rules
- Use Zod or equivalent validation for every untrusted request body.
- Use authenticated Supabase server clients and RLS. Never trust organization IDs sent by the browser; resolve membership on the server.
- Keep OpenAI, Stripe, n8n, OAuth and Supabase service-role secrets server-only.
- Do not expose secrets through NEXT_PUBLIC variables.
- Do not use the service-role key for ordinary user requests.
- Add tests for authorization, validation, error states and tenant isolation.
- Keep AI as a copilot: propose actions, then require a human approval record before execution.
- Provide complete changed files, migrations, environment variable names, exact setup steps, and test commands after each phase.
- Run `npm run build` and relevant tests. If you cannot run them, say so clearly and list the unverified items.

Start by auditing Phase 2 for correctness and security, then implement Phase 3 only. Do not attempt all phases in one unreviewable code dump.
