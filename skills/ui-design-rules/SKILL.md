---
name: ui-design-rules
description: Detailed UI/CSS, colour, motion and usability rules (from saved design reels) to apply when building, restyling or reviewing web or app interfaces - components, pages, themes, palettes, animations, dark mode, forms, OTP/login screens, headers, landing pages. Use for front-end/UI design work only; skip for backend, data or non-UI tasks.
---

# UI design rules

Apply these when writing, restyling or reviewing UI code. Each rule says what to do, why, and how.
Keep to what the task needs: never add effects nobody asked for, and if the project already has a
design system or tokens, follow those over these rules.

---

## 1. CSS craft rules

### 1.1 Nested rounded corners
- **Problem:** when a rounded element sits inside another rounded element, using the same radius for both makes the gap between them look uneven (thick at the corners, thin on the sides).
- **Rule:** inner radius = outer radius - the padding (gap) between them.
- **How:**
  ```css
  .card  { --r: 20px; --pad: 8px; border-radius: var(--r); padding: var(--pad); }
  .card > .inner { border-radius: calc(var(--r) - var(--pad)); }
  ```
- If the result is 0 or negative, use a small radius (2-4px) or a square corner.

### 1.2 Alpha borders instead of solid hex
- **Problem:** a solid hex border (e.g. `#e5e5e5`) only looks right on the one background it was picked for; on tinted, dark or image backgrounds it looks dirty or harsh.
- **Rule:** use semi-transparent black/white borders so they pick up whatever is behind them.
- **How:** light UI `border: 1px solid rgb(0 0 0 / 0.12);` - dark UI `border: 1px solid rgb(255 255 255 / 0.12);`. Tune alpha between 0.06 and 0.16.

### 1.3 Build palettes in OKLCH, not HSL
- **Problem:** human eyes do not perceive brightness evenly across hues. In HSL, yellow at 50% lightness looks far brighter than blue at 50%, so "equal" steps look uneven.
- **Rule:** define colour scales in `oklch(L C H)`; equal L really looks equally light.
- **How:** keep H fixed for one hue's scale, step L evenly (e.g. 0.97, 0.90, 0.80 ... 0.25), and lower C at the very light and very dark ends so colours stay in gamut.
  ```css
  --blue-500: oklch(0.62 0.17 255);
  --blue-100: oklch(0.94 0.04 255);
  ```

### 1.4 Gradients interpolated in OKLCH
- **Problem:** gradients between two vivid, distant colours (e.g. blue to orange) go grey/muddy in the middle in the default sRGB interpolation.
- **Rule:** interpolate in OKLCH so the colour stays vivid all the way.
- **How:** `background: linear-gradient(90deg in oklch, blue, orange);` (works for `radial-` and `conic-` too).

### 1.5 Icon stroke matches text weight
- **Problem:** a thin-line icon next to bold text (or a heavy icon next to light text) looks sloppy and mismatched.
- **Rule:** match the icon's stroke width to the font weight it sits beside.
- **How:** roughly regular (400) text = 1.5px stroke, medium (500) = 1.75px, semibold/bold (600-700) = 2-2.25px at 24px icon size. With Lucide/Feather-style icons set `stroke-width` per context.

### 1.6 Fade carousel / scroller edges with a mask
- **Problem:** horizontally scrolling rows cut off hard at the edge, which looks broken.
- **Rule:** fade both edges to transparent so items softly enter and leave.
- **How:**
  ```css
  .scroller { mask-image: linear-gradient(90deg, transparent, black 15% 85%, transparent); }
  ```

### 1.7 Blur on icon swaps
- **Problem:** swapping one icon for another (play to pause, copy to check, menu to close) with a plain fade looks cheap.
- **Rule:** blur the outgoing icon as it fades out, and bring the new one in from blurred to sharp.
- **How:** animate `opacity` 1 to 0 together with `filter: blur(0)` to `blur(4px)`, plus an optional slight `scale(0.9)`; about 150-200ms.

### 1.8 Depth in dark mode = lighter surfaces
- **Problem:** drop shadows barely show on dark backgrounds, so cards and menus lose their sense of elevation.
- **Rule:** in dark mode, show depth by making raised surfaces lighter, not by adding bigger shadows.
- **How:** base `oklch(0.16 0 0)`, card `oklch(0.20 0 0)`, popover/menu `oklch(0.24 0 0)`; a faint top-light alpha border (1.2) helps too.

### 1.9 `100dvh` instead of `100vh`
- **Problem:** on mobile Safari (and other mobile browsers) `100vh` ignores the moving address bar, so "full-screen" sections overflow and the bottom gets hidden.
- **Rule:** use dynamic viewport units.
- **How:** `min-height: 100dvh;` (keep a `100vh` line above it as a fallback for very old browsers). Use `svh`/`lvh` if you specifically need the small/large viewport.

### 1.10 `mix-blend-mode: multiply` for product shots
- **Problem:** product photos shot on a white background show an ugly white box on tinted or off-white cards.
- **Rule:** blend the image so the white disappears into the card colour.
- **How:** `img.product { mix-blend-mode: multiply; }` on a light, non-white card. Only for light backgrounds; for dark ones use a transparent PNG/WebP instead.

---

## 2. Colour: one complementary accent

- **Idea:** a palette of two related calm colours looks clean but flat - the eye has nowhere to land. Adding ONE small touch of a colour from the opposite side of the colour wheel tells the eye exactly where to look.
- **Examples from the source:**
  - glacier blue + navy, add a touch of lemon yellow;
  - deep teal + cream (looks cold), add a little orange (now it feels warm, "hot out of the roaster");
  - cream + ink (washed out), add a pop of orchid pink.
- **How:**
  - Pick the base pair (background + text/primary); take its hue and rotate about 180 degrees on the wheel (in OKLCH: H + 180) for the accent.
  - Use the accent sparingly: the main call-to-action, one highlight, a badge, a key number - roughly 5-10% of the screen, never for large areas.
  - Check text-on-accent contrast (WCAG AA 4.5:1 for body text).

---

## 3. "Unslop" an AI-default screen (worked example: OTP / verification code screen)

AI tools tend to produce the same generic look. Clean it up in this order:
1. **Remove AI clichés:** drop the purple/violet gradients and decorative noise. **Auto-submit** the code once the last digit is entered (no extra "Verify" click). Result: it feels trustworthy.
2. **Cut and simplify:** remove extra words (one short heading + one line of help text) and remove borders that are not needed. Result: clean.
3. **Add one premium touch:** a subtle iridescent/soft gradient background, and stronger contrast on the code tiles so each digit box is clearly visible. Result: premium.
4. **Animate states:** animate each digit as it is typed, and give clear visual feedback for every state - focused, filled, verifying, success, error (shake + red tint). Result: satisfying.
5. **Remove work for the user:** let the browser auto-fill the code from the SMS: `<input autocomplete="one-time-code" inputmode="numeric" pattern="[0-9]*">`. Result: the user does not have to type at all.

General version of this checklist for any screen: remove clichés, cut words and borders, add one premium detail, animate states with feedback, then remove any step the user does not need to do.

---

## 4. Motion principles (Disney's 12 principles applied to UI)

- **Squash & stretch:** elements squish slightly on impact and stretch while moving fast, which gives them weight (e.g. a button presses to `scale(0.96)`, a bouncing badge).
- **Anticipation (wind-up):** a small pull back before a big move so the user sees it coming (e.g. a drawer nudges 2-4px the other way before opening). Keep it tiny.
- **Staging (focus):** direct attention to one thing at a time; dim or hold back everything else during the key moment.
- **Pose to pose:** define the key start/end states and let CSS transitions / the browser fill in the frames between.
- **Follow-through:** parts keep moving briefly after the main body stops, then settle (e.g. a spring overshoot, list items arriving a few ms after their container).
- **Slow in & slow out:** never constant (linear) speed; accelerate and decelerate. Use ease-out for entering, ease-in for leaving, or springs.
- **Arcs:** move along curves rather than straight lines where natural (e.g. an item flying into a cart).
- **Secondary action:** a small flourish that supports the main action (e.g. a confetti burst or icon wiggle on success) - never one that competes with it.
- **Snappy timing:** duration sets the feel; keep UI animations under ~300ms (micro-interactions 100-200ms).
- **Exaggeration:** push feedback slightly past realistic so the moment lands (e.g. an error shake, a satisfying check-mark pop).
- **Solid drawing (3D):** give flat things depth and volume - light, shadow, layering, subtle perspective.
- **Staggering:** bring list/grid items in one after another (~30-50ms apart) instead of all at once. Only stagger the first ~5-8 items and show the rest together so the whole entrance stays around 300ms; skip it for frequently used views and under `prefers-reduced-motion`.
- **Interruptible motion:** let users change their mind mid-animation (release a press early, close a menu while it is opening). CSS transitions retarget from the current value, so prefer them over fixed `@keyframes` that must finish; spring libraries (e.g. Motion) also carry over the current velocity. Never block input until an animation ends.
- **Appeal:** the sum of every detail done with care; consistency across all of the above.

---

## 5. UX laws

- **Fitts's law:** bigger, closer targets are faster to hit. Put primary actions large and near where the user's pointer/thumb already is.
- **Bigger hit areas:** the clickable area can be larger than the visible element; use padding or a pseudo-element to make tap targets at least 44x44px.
- **Hick's law:** more choices = slower decisions. Cut options, use sensible defaults, and reveal advanced options progressively.
- **Miller's law:** people hold about 7 (+/-2) items in mind at once; chunk information (phone numbers in groups, menus in sections).
- **Doherty threshold:** respond within ~400ms or it feels slow; if work takes longer, show instant feedback, optimistic UI or a progress indicator.
- **Postel's law:** be liberal in what you accept (messy input: spaces, dashes, different date formats) and strict/clean in what you output.
- **Jakob's law:** people spend most of their time in other apps and expect yours to work the same way; follow familiar patterns (logo top-left links home, cart top-right, standard icons).
- **Frequency of use:** the more often something is used, the less it should animate - daily actions should be instant; save delight animations for rare moments.
- **Von Restorff (isolation) effect:** the one item that looks different gets noticed and remembered. Reserve it for the single primary action (see sections 2 and 7), and make it differ by more than colour alone (weight, size, shape) for accessibility.
- **Peak-end rule:** people judge an experience mostly by its most intense moment (good or bad) and by its end. Polish success states and the last step of flows, and make error recovery gentle.

---

## 6. Interaction animation details

Small motion fixes that make UI feel responsive. Honour `prefers-reduced-motion` (turn shakes, slides and springs into an instant change or a plain fade).

- **Entrances:** start from `scale(0.97)` + `opacity: 0`, never from `scale(0)` (growing from nothing feels abrupt). For popovers/menus set `transform-origin` to the trigger, or to the click/tap point for things that grow from a press (origin awareness) - never an arbitrary centre.
- **Pressed buttons:** shrink slightly while pressed so the tap is felt: `button { transition: scale 150ms ease-out; } button:active { scale: 0.97; }` (same 0.96-0.97 range as section 4).
- **Wrong input (e.g. password):** shake the field as well as turning it red, so the error is obvious even to someone not looking at the colour: keyframes on `translateX` 0, -10, 10, -6, 6, -3, 0px over ~360ms (error feedback may run a little over the ~300ms guideline).
- **Steppers / multi-step forms:** slide the next step in from the direction of travel (forward = from the right, back = from the left; mirror for RTL layouts) instead of crossfading.
- **Accordions / `height: auto`:** `:root { interpolate-size: allow-keywords; }` lets `height` (and other sizes) transition to and from `auto`/`max-content`. Not Baseline yet (check MDN/caniuse), so treat it as progressive enhancement: without it the panel just opens instantly. `calc-size(auto)` is the per-property alternative; `<details>` also needs `::details-content` styled to animate.
- **Moving things:** prefer `transform` and `opacity`; avoid animating `top`/`left`/`width`/`height` for movement, because they trigger layout and repaint every frame. Size transitions like accordions are the accepted exception; keep them short.
- **Theme switches:** disable transitions while switching so every colour transition does not fire at once:
  ```css
  .theme-switching, .theme-switching *, .theme-switching *::before, .theme-switching *::after { transition: none !important; }
  ```
  Add the class to the root, change the theme, force a reflow (e.g. `getComputedStyle(document.body).opacity`), then remove the class in the next `requestAnimationFrame`/`setTimeout`.
- **Tooltips:** delay only the first tooltip (~400-600ms); while one is open, or just after one closed, show the next instantly.
- **Flicks and drags:** on release, hand off to a spring that keeps the release velocity instead of a fixed-duration transition, which feels mechanical. E.g. Motion: `animate(y, 0, { type: "spring", duration: 0.5, bounce: 0, velocity })` where `y` is a MotionValue and velocity is in units per second. Drag libraries with built-in momentum (e.g. Motion's `drag` + `dragTransition`) already do this.
- **Carousels / scroll ends:** past either end, add resistance that grows the further the user pulls (rubber band), then spring back.

## 7. Visual hierarchy: one big, a few medium, rest small

- **Problem:** when many elements share the same size and colour strength, the design looks messy and the eye has no starting point.
- **Rule:** make ONE element the hero, one or two supporting elements medium, and keep everything else quiet.
- **How:** vary size first, then colour intensity/weight (hero large and full contrast; supporting medium; the rest smaller and in a muted colour), while still meeting WCAG AA contrast (4.5:1 body text, 3:1 large text). Combine with the single accent from section 2 on the hero or the main call-to-action.

## 8. Page patterns: headers, landing pages, timing

### 8.1 Header that hides on scroll down and returns on scroll up
- **Problem:** a header pinned to the top takes space on every scroll position, covering part of product photos, reviews and prices. A header that simply scrolls away is worse: shoppers lose menu, search and cart.
- **Rule:** on long pages (especially product and shop pages), hide the header while the user scrolls down and bring it back as soon as they scroll up.
- **Evidence (as reported in the reel, not independently verified):** kitchenware brand Joseph Joseph tested fixed vs scroll-away vs hide-and-return. Hide-and-return reportedly raised purchases ~6% and revenue per visitor ~15.5% (a 19-day desktop/tablet test reported by the testing vendor); the header that just disappeared reportedly lost (the reel claims -15% add-to-basket). Treat as one case study, not a law.
- **How:**
  - Track scroll direction with a small threshold (ignore moves under ~5-10px) and toggle a class: `header.is-hidden { transform: translateY(-100%); }` with `transition: transform 200-250ms ease-out` (it must come back quickly, well under half a second).
  - Always show it at the very top of the page, when a menu/search inside it is open or focused, and when keyboard focus moves into it.
  - Use `position: sticky; top: 0;` so the layout does not jump; under `prefers-reduced-motion` toggle without the slide.

### 8.2 Bold "one-accent" landing page recipe
A popular trend for professional-looking landing pages. Steps from the reel:
1. **Make the subject huge:** the person or product is blown up so it extends beyond the frame/section edges. Clip the overflow on the section (`overflow-x: clip`) so it never causes horizontal scrolling on mobile.
2. **Use physical textures** (paper, concrete, glass, fabric) for backgrounds instead of flat colours or digital gradients. Keep texture images light (compressed WebP/AVIF) so the page stays fast.
3. **Three colours only:** start with two base colours, one neutral and one coloured, one dark and one light; they are the background and the typography. Then take the coloured one and rotate at least ~120 degrees on the colour wheel (up to the full ~180 degrees of section 2) for the accent.
4. **Use the accent sparingly:** only on the subject, one highlighted word, or the main button.
- This is a style, not a default: use it for marketing/hero pages, not for dense app screens or where a brand palette already exists.

### 8.3 How long motion should take (page level)
- Too slow and the visitor waits for the site to finish "showing off"; too fast and they cannot see where things came from. Good motion is over just as you notice it.
- **Rule of thumb:** a press/tap response takes a blink (~100-150ms); a reveal (section, card, image coming in) stays under a second (typically 300-700ms); a full hero scene or page-level sequence can take just over a second, and only once (never on every visit or for frequently used views).
- The <300ms guideline in section 4 is for interface controls; longer durations are only for one-off, page-level reveals.

---

## 9. Polish details that make an app feel finished
Pick the ones that fit the product; do not add all of them by default. Check browser support for the newer CSS ones.

**Perceived speed**
- **Skeleton screens:** while content loads, show grey blocks shaped like the final layout instead of a spinner, so the page does not jump when data arrives.
- **Optimistic updates:** for likely-to-succeed actions (like, save, toggle), update the UI at once and roll back with an error message if the server fails. Do not do this for payments or anything hard to undo.
- **Stale-while-revalidate:** show cached data immediately and refresh it in the background (the HTTP `Cache-Control: stale-while-revalidate` directive, or data libraries such as SWR / TanStack Query).
- **Prefetch / prerender likely next pages:** e.g. on hover or with the Speculation Rules API (Chromium only; other browsers ignore it safely).
- **Blurred image placeholders:** show a tiny blurred preview (e.g. BlurHash or a low-quality image) with fixed width/height so images fade in without layout shift.

**Speed for power users**
- **Command menu (Cmd/Ctrl+K):** a searchable list of pages and actions, fully keyboard-usable.
- **Shortcut hints:** show the keyboard shortcut next to menu items or in tooltips so users can learn it.
- **Undo instead of "Are you sure?":** for reversible actions (delete, archive), do it at once and show a toast with an Undo button for a few seconds (soft-delete, or delay the real delete until the toast closes). Keep confirmation dialogs for truly destructive actions.

**Motion and touch**
- **View transitions:** use the View Transitions API for smooth page/state changes (same-document transitions work in all major browsers since late 2025; cross-document ones are not in Firefox yet; respect `prefers-reduced-motion`).
- **Interruptible animations:** see section 4.
- **Swipe-to-dismiss sheets** on mobile, with a visible close button as well (not everyone swipes).
- **Predictive back (Android):** in Android apps, support the system back-gesture preview so users see where back will go.
- **Bigger hit areas ("hit slop"):** see section 5 (at least 44x44px tap targets).
- **Safe triangle for hover menus:** when a submenu opens beside a menu, keep it open while the pointer moves diagonally toward it (the pattern Amazon's mega menu made famous). Many menu libraries (e.g. Radix) already do this; otherwise a short close delay helps.

**Device and form details**
- **Safe-area insets:** on phones with notches/home bars, pad fixed headers, footers and bottom bars with `env(safe-area-inset-*)` (needs `viewport-fit=cover` in the viewport meta tag).
- **One-time-code autofill:** see section 3 (`autocomplete="one-time-code"`).

**Typography and shape**
- **Tabular numbers:** use `font-variant-numeric: tabular-nums` for prices, timers, tables and counters so digits do not jiggle as they change (the font must include tabular figures).
- **Balanced headlines:** `text-wrap: balance` on headings (not body text) avoids one lonely word on the last line. Supported in Chrome/Edge 114+, Firefox 121+, Safari 17.5+; Chrome only balances short blocks (about 6 lines).
- **Smooth ("continuous") corners:** Apple-style squircle corners look softer than plain `border-radius`. CSS `corner-shape: squircle` is new and not supported everywhere; it only changes corners that already have a `border-radius` (shipped in Chrome 139; not yet in Firefox/Safari), so treat it as progressive enhancement.

**Reliability**
- **Idempotency keys:** send a unique key with requests that create things (orders, payments) so a double-click or retry does not create duplicates. Make the key once per user action and reuse it on retries. Stripe accepts an `Idempotency-Key` header; on your own endpoints, store the key and return the first result for repeats.

---

## How to use this skill
- When building or restyling UI, apply the relevant rules without listing them; mention a rule only when it explains a non-obvious choice.
- When reviewing UI, check it against sections 1-9 and report concrete fixes (selector + change).
- Respect accessibility: honour `prefers-reduced-motion` (turn off non-essential motion), keep WCAG AA contrast, keep focus states visible.

Sources: summarised from four saved Instagram reels by charles.unemployed (design rules, complementary accent, OTP-screen "unslop" demo, animation and UX laws; the laws list credits userinterface.wiki and Disney's animation principles), plus reels by Charles Liu (interaction animation details) and Maxwell Gomes (visual hierarchy), and bendoescareer (staggering, origin awareness, interruptible motion, Von Restorff, peak-end; checked against Laws of UX and NN/g), plus levilayernn (hide-on-scroll header case study), Anthony Alexander (one-accent landing pages) and theglidestudio (motion timing), and Aidan Murphy (20 polish details, section 9; checked against MDN, Chrome/web.dev, Stripe and Android docs). Wording is original.
