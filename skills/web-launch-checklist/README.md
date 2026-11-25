# web-launch-checklist: what I think it is

A "before you go public" safety check for apps built fast with AI. Claude uses it when you ask for a security, cost or launch review, and reports each item as OK / FIX / N/A.

What's inside, in plain words:
- **Surprise bills (1-2):** usage-billed hosting can send a five- or six-figure invoice after a traffic spike, and a function that triggers itself can loop all night. Set hard caps, not just email alerts.
- **Database rules (3):** with Supabase and similar backends the public key sits in the browser on purpose, so Row Level Security must be on for every table.
- **Leaked secrets (4):** keys in the repo, the client bundle or git history.
- **Accessibility and consent (5-6):** both are legal risks as well as good practice.
- **Think like an attacker (8-9):** about 30 common attacks on quick-built apps: changing an ID in the URL, editing the price in the browser, faking a payment, using a coupon 100 times, account-enumeration, refund-but-keep-premium, email spoofing (SPF/DKIM/DMARC)...
- **Break-it tests (10):** double-tap Pay, airplane mode mid-upload, emoji names, giant text, RTL languages, "Hide My Email".

My take: it isn't a replacement for a real security audit, but it catches the mistakes that keep showing up in rushed apps. Test only apps you own. The legal notes are general information, not legal advice.
