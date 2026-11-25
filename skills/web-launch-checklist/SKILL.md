---
name: web-launch-checklist
description: Pre-launch safety checklist for websites and apps built quickly with AI - runaway hosting/cloud bills, database access rules (e.g. Supabase RLS), exposed keys, accessibility, SMS/email consent, recursive functions. Use before a public launch or first deploy, sharing a site publicly, or when asked to review a project for security, cost or legal risk, or for edge-case "break-it" tests before release. Skip for normal feature work.
---

# Web launch checklist

Run through this before a site or app goes public, and report each item as OK / FIX (with the exact file and change) / N/A.
Do not change billing settings, sign up for services or rotate keys yourself; tell the user what to do.

## 1. Runaway hosting and cloud bills
- **Risk:** "static" sites are not free if traffic explodes. Hosts that bill per GB of bandwidth can send huge invoices after a traffic spike or DDoS (a widely reported case: a static site on Netlify received a ~$104,500 bandwidth bill after a DDoS in 2024; it was waived only after the story went viral).
- **Check:**
  - Does the host bill per usage (bandwidth, function invocations, build minutes)? Is there a **hard spending cap** or automatic pause, not just an email alert?
  - Large files (videos, images, downloads) served directly from the host? Prefer compressed images and a CDN / object storage with caching.
  - Is DDoS protection / rate limiting on (e.g. Cloudflare in front, platform firewall rules)?
- **Budget alerts only notify, they do not stop spending.** Recommend a real cap or a kill switch where the platform offers one.

## 2. Functions that call themselves (recursion / loops)
- **Risk:** a serverless function, trigger or webhook that ends up calling itself (directly, or by writing to the thing that triggers it) can run millions of times overnight. A widely reported startup case ran up a ~$72,000 cloud bill in about two hours while testing (default autoscaling allowed up to 1,000 instances).
- **Check:** every function/trigger: can its output re-trigger it? Retries with backoff and a max count? Per-function concurrency/instance limits and timeouts set? Loops over paginated APIs have a stop condition?

## 3. Database access rules
- **Risk:** with Supabase (and similar backends) the public "anon" key is in the front-end JavaScript by design. If **Row Level Security (RLS)** is off on a table, anyone with that key can read or change the whole table (e.g. all users).
- **Check:**
  - RLS enabled on **every** table in exposed schemas, with policies that limit rows to the signed-in user (`auth.uid()`), including tables created later by AI or migrations.
  - The `service_role` / admin key is never in front-end code, the repo, or public env vars (`NEXT_PUBLIC_`, `VITE_`, etc.).
  - Views bypass RLS unless created with `security_invoker = true`; RLS on with no policies blocks all access (check the app still works).
  - Newer Supabase projects use "publishable" and "secret" keys: the secret key follows the same rule as `service_role`.
  - Storage buckets: public only if meant to be.
  - Firebase: security rules are not left in test mode (`allow read, write: if true`).

## 4. Exposed secrets and endpoints
- Search the repo and the built output for API keys, tokens and passwords (`.env` committed? keys in client bundles? keys in git history?). Any leaked key must be rotated by the user, not just deleted. List every key the app has ever used; old or unused ones should be revoked (by the user) and the rest given the least access they need.
- API routes: authentication checked on the server for every route that reads or changes private data; no admin/debug routes left open; CORS not `*` for authenticated APIs.
- Before shipping, run Claude Code's `/security-review` on the pending changes. For a deployed site, an external scanner can help, but signing up for one is the user's decision.

## 5. Accessibility (also a legal risk)
- **Risk:** in the US thousands of web-accessibility lawsuits are filed every year (several thousand per year in recent counts), including against small businesses; other countries have similar laws (e.g. the European Accessibility Act).
- **Check (WCAG 2.2 AA basics):**
  - Everything works with the keyboard only: visible focus, logical tab order, no keyboard traps, menus and modals usable with Tab/Enter/Escape.
  - Every meaningful image has `alt` text; decorative images use `alt=""`.
  - Text contrast at least 4.5:1 (3:1 for large text); form fields have labels; buttons/links have accessible names.
  - Page has `lang`, headings in order, and content is not conveyed by colour alone.

## 6. Messaging consent (SMS, WhatsApp, email)
- **Risk:** in the US, marketing texts without prior express written consent can violate the TCPA (mainly autodialed/prerecorded marketing and texts to Do-Not-Call numbers), with statutory damages of $500 per message (up to $1,500 if wilful), so in the worst case a 10,000-text blast could mean millions. Other countries have their own rules (e.g. GDPR/ePrivacy in the EU, the PDPA in Singapore and Malaysia, Indonesia's PDP Law).
- **Check:** waitlist/signup forms collect explicit opt-in (unticked checkbox, clear wording of what they will receive), consent is stored with a timestamp, every message has an easy opt-out, and email follows CAN-SPAM/GDPR basics (sender identity, unsubscribe link). This is general information, not legal advice; the user should confirm the rules for their country.

## 7. Quick final pass
- Privacy policy / cookie notice where required; analytics do not collect more than needed.
- Error pages do not leak stack traces or env values.
- Backups of the database exist and a restore has been tried.
- Mobile layout, page speed (Lighthouse) and broken links checked.

## 8. Think like an attacker (14 common attacks on quickly built apps)
For each item, find where the app handles it and report OK / FIX / N/A. Test only your own app.
- **Script in user input (XSS):** a username or comment like `<script>` must be shown as text. Escape output (frameworks do this by default); avoid `innerHTML` / `dangerouslySetInnerHTML` with user data.
- **Changing an ID in the URL (IDOR):** `/orders/124` must not show someone else's order. Check on the server that the record belongs to the signed-in user.
- **Hidden admin or paid pages:** `/admin`, `/premium` and their API routes need a server-side role or plan check, not just a hidden link.
- **Secrets in the browser:** anything in front-end code or network responses is public (see section 4).
- **Prompt injection:** if the app has an AI feature, users (or pages/files it reads) can write "ignore your instructions". Never give the model secrets or powers the user should not have; check permissions in code, not in the prompt.
- **Making yourself admin at sign-up (mass assignment):** the server must ignore fields like `role` or `isAdmin` sent by the client; allow-list the fields a user may set.
- **Editing the price:** never trust a price, total or discount sent from the browser; look it up on the server.
- **Faking a payment:** mark an order paid only from the payment provider's verified webhook (check the signature, e.g. Stripe's), not from a "success" page redirect.
- **Redeeming a coupon 100 times:** enforce use limits on the server, in a database transaction or with a unique constraint, so parallel requests cannot all pass.
- **Ordering -1 items:** validate quantities and amounts on the server (whole numbers, minimum 1, sensible maximum).
- **Guessing a login code:** rate-limit and lock out after a few wrong one-time codes or passwords; codes should expire.
- **SQL injection:** use parameterised queries or the ORM; never build SQL by joining strings with user input.
- **Exposed `.env` or `.git` folder:** check that `https://yoursite/.env` and `/.git/config` return 404 or 403, and that source maps or backups are not public.
- **Uploading something that isn't a photo:** check type and size on the server, re-encode or reject unexpected files, store uploads outside the web root or in object storage, and never run or serve them as HTML.

## 9. More attacks: accounts, payments, data and email
Same rule: test only your own app, report OK / FIX / N/A.
- **"Is this email registered?" (account enumeration):** login and password-reset give the same message and similar response for known and unknown emails ("If an account exists, we sent a link"). Sign-up can only do this if it confirms by email first; otherwise rate-limit it (below).
- **Reset link sent to the wrong address:** the reset endpoint accepts exactly one email (reject arrays or extra fields) and sends only to the address already stored on the account. A real bug of this kind (GitLab CVE-2023-7028) delivered reset emails to an attacker's unverified address.
- **Old reset links:** reset tokens are single-use, expire after a short time, and stop working once the password changes.
- **Still logged in elsewhere after a password change:** changing or resetting the password ends the user's other sessions and refresh tokens (offer "log out of all devices").
- **Refund but keep premium:** remove access when the store or payment provider reports a refund, revocation or chargeback (Apple App Store Server Notifications `REFUND` and `REVOKE`, Google Play Voided Purchases API, Stripe `charge.refunded`, `charge.dispute.created`, `customer.subscription.deleted`). The server's record is the source of truth, never a client-side `premium: true` flag.
- **Whole-table API responses:** endpoints like `/api/users` must not return every user or fields the caller doesn't need (emails, phones, hashes). Return only what the signed-in user may see, with pagination and a field allow-list.
- **"Deleted" data still returned:** soft-deleted records (`deleted: true`) must not be sent to the client, including through search indexes, caches and exports. Hard-delete or wipe content when the user expects it gone.
- **The AI feature reads other users' data:** an in-app assistant may only fetch what the current user may see. Scope its tools and queries by user ID in code (see prompt injection in section 8).
- **Location in uploaded photos:** strip EXIF metadata (GPS, device) from user photos, or re-encode them on the server, before storing or showing them.
- **Public storage bucket:** private user files are served with short-lived signed URLs or an access check, and the bucket cannot be listed (see section 3).
- **Huge uploads:** besides the server checks in section 8, set a size limit at the storage/proxy level too.
- **Thousands of fake sign-ups:** rate-limit sign-up and reset by IP and account (like login codes in section 8), require email verification, and add bot protection where abuse is likely.
- **Fake emails "from" your domain:** set up SPF, DKIM and DMARC for every sending domain. Since 2024 Gmail and Yahoo require SPF or DKIM from all senders, and SPF, DKIM, DMARC and one-click unsubscribe from bulk senders (about 5,000+ messages a day to Gmail). DMARC `p=none` only reports; move to `quarantine` or `reject` once reports are clean. Tell the user which DNS records to add; don't change DNS yourself.
- **Copying your code from the browser:** front-end code is always public and source maps only make it readable. Don't publish production source maps, and keep secrets and business rules on the server (see sections 4 and 7).

## 10. Break-it tests before launch (edge cases)
Try these on real devices or the browser's device tools. Fix anything that crashes, double-charges, loses data or looks broken.
- **Navigation and timing:** press Back during checkout or payment; quit halfway through onboarding and come back; tap Sign up / Pay twice quickly (the second tap must not create a duplicate: disable the button and use an idempotency key, see ui-design-rules section 9).
- **Odd input:** emoji in the name, a 5,000-word bio, an empty email, a password that is only a space. Validate on the server and set max lengths. Trim emails and names, but never trim or change passwords: allow spaces and enforce a minimum length instead (current NIST guidance).
- **Network:** airplane mode in the middle of an upload; slow 3G (throttling in dev tools). Show a clear error and allow retry without losing what the user typed.
- **Display:** rotate the phone; very large text (WCAG 1.4.4: web text resizable to 200% without losing content or function; on native apps test Dynamic Type / font scale); dark mode; foldable and very narrow or wide screens.
- **Device settings:** deny every permission (camera, location, notifications) and check the app still works or explains why; change the time zone (dates, streaks and "today" use the user's zone, stored as UTC); switch to a right-to-left language such as Arabic (layout mirrors with `dir="rtl"` and logical CSS properties).
- **Accounts:** sign in with Apple using "Hide My Email": register your sending domain/addresses in Apple's Private Email Relay settings or mail to `@privaterelay.appleid.com` is dropped, link the account to Apple's stable user ID (`sub`) rather than the email, and save the name on the first sign-in (Apple sends it only once). Delete the account and sign up again with the same email: old data must not reappear and a soft-deleted row must not block the new sign-up. Log in on two phones at once.

Sources: idea from saved reels by adilet.fndr ("your vibe-coded app can cost $100,000") and Miles Tech (scan your site for exposed keys before sharing) and Arshan Adili (attacker checklist, section 8; checked against OWASP Top 10 A01 and the OWASP API Security Top 10); checked against Supabase RLS docs, FCC/TCPA guidance and WCAG 2.2. Case figures are as publicly reported. Sections 9-10 from reels by Ryan Naghibzadeh and Arshan Adili (Nov 2026), checked against the OWASP Forgot Password, Authentication and Session Management cheat sheets, CVE-2023-7028, Apple App Store Server Notifications, Google Play Voided Purchases, Google email sender guidelines and WCAG 1.4.4. Wording is original.
