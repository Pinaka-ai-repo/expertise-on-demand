#!/usr/bin/env python3
"""Build the static expert-profile site from extracted content + assets."""
import json, html, os, sys, re

S = os.path.dirname(os.path.abspath(__file__))
OUT = S  # regenerates index.html beside this script

GROUPS = json.load(open(f"{S}/groups.json"))
NETWORKS = json.load(open(f"{S}/networks.json"))

BOOKING = ("https://calendar.google.com/calendar/u/0/appointments/schedules/"
           "AcZssZ0GgIsiCIashTXzVaYEMnjqGcZqlcNsUAxcgStX5fI59_DMN2yX7xCxE-lQ-9yslv1nIuvEFrum")
EMAIL = "information.adept@gmail.com"
PHONE_E164 = "+919740556805"
PHONE_DISP = "+91 97405 56805"
LINKEDIN = "https://www.linkedin.com/in/mohit-sharma-acma-cgma-25764411/"
SITE_URL = "https://www.tonysharma.com/"

e = lambda s: html.escape(s, quote=True)

# ---------------------------------------------------------------- icons
# Lucide-family geometry, normalised to a single 1.6 stroke weight.
def icon(paths, size=20, sw="1.6"):
    return (f'<svg class="ic" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="currentColor" stroke-width="{sw}" stroke-linecap="round" '
            f'stroke-linejoin="round" aria-hidden="true">{paths}</svg>')

IC = {
 "arrow":  '<path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>',
 "mail":   '<rect width="20" height="16" x="2" y="4" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>',
 "shield": '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/>',
 "video":  '<path d="m16 13 5.223 3.482a.5.5 0 0 0 .777-.416V7.87a.5.5 0 0 0-.752-.432L16 10.5"/><rect x="2" y="6" width="14" height="12" rx="2"/>',
 "clip":   '<path d="M10 2v2"/><path d="M14 2v2"/><path d="M16 8a1 1 0 0 1 1 1v8a4 4 0 0 1-4 4H7a4 4 0 0 1-4-4V9a1 1 0 0 1 1-1h4a1 1 0 0 0 1-1V4a2 2 0 1 1 4 0v3a1 1 0 0 0 1 1z"/><path d="M6 2v2"/>',
 "book":   '<path d="M12 7v14"/><path d="M3 18a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h5a4 4 0 0 1 4 4 4 4 0 0 1 4-4h5a1 1 0 0 1 1 1v13a1 1 0 0 1-1 1h-6a3 3 0 0 0-3 3 3 3 0 0 0-3-3z"/>',
 "users":  '<path d="M18 21a8 8 0 0 0-16 0"/><circle cx="10" cy="8" r="5"/><path d="M22 20c0-3.37-2-6.5-4-8a5 5 0 0 0-.45-8.3"/>',
 "mic":    '<path d="M12 8V4H8"/><rect width="16" height="12" x="4" y="8" rx="2"/><path d="M2 14h2"/><path d="M20 14h2"/><path d="M15 13v2"/><path d="M9 13v2"/>',
 "phone":  '<path d="M13.832 16.568a1 1 0 0 0 1.213-.303l.355-.465A2 2 0 0 1 17 15h3a2 2 0 0 1 2 2v3a2 2 0 0 1-2 2A18 18 0 0 1 2 4a2 2 0 0 1 2-2h3a2 2 0 0 1 2 2v3a2 2 0 0 1-.8 1.6l-.468.351a1 1 0 0 0-.292 1.233 14 14 0 0 0 6.392 6.384"/>',
 "chat":   '<path d="M7.9 20A9 9 0 1 0 4 16.1L2 22z"/>',
 "linked": '<path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"/><rect width="4" height="12" x="2" y="9"/><circle cx="4" cy="4" r="2"/>',
 "cal":    '<path d="M8 2v4"/><path d="M16 2v4"/><rect width="18" height="18" x="3" y="4" rx="2"/><path d="M3 10h18"/>',
 "chev":   '<path d="m6 9 6 6 6-6"/>',
 "north":  '<path d="M7 7h10v10"/><path d="M7 17 17 7"/>',
}

FORMATS = [
 ("video", "1:1 calls",             "Phone or video, typically 30–60 minutes, scheduled at short notice."),
 ("clip",  "Due diligence sprints", "Focused vendor, market, or technology diligence against a live deal clock."),
 ("book",  "Long-term advisory",    "Retained support for teams tracking a category or programme over time."),
 ("users", "Moderated panels",      "Multi-expert sessions where I bring the delivery-side perspective."),
 ("mic",   "Speaking",              "Conference sessions and executive roundtables on emerging technology."),
]

STATS = [("1,200", "+", "Consultations delivered"), ("40", "+", "Expert networks"),
         ("25", "+", "Years in consulting"), ("315", "", "Topics advised on")]

# ---------------------------------------------------------------- css
CSS = r"""
@font-face{font-family:'Inter';src:url(assets/fonts/inter-latin.woff2) format('woff2');font-weight:100 900;font-display:swap;unicode-range:U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD}
@font-face{font-family:'Inter';src:url(assets/fonts/inter-latin-ext.woff2) format('woff2');font-weight:100 900;font-display:swap;unicode-range:U+0100-02BA,U+02BD-02C5,U+02C7-02CC,U+02CE-02D7,U+02DD-02FF,U+0304,U+0308,U+0329,U+1D00-1DBF,U+1E00-1E9F,U+1EF2-1EFF,U+2020,U+20A0-20AB,U+20AD-20C0,U+2113,U+2C60-2C7F,U+A720-A7FF}
@font-face{font-family:'Syne';src:url(assets/fonts/syne-latin.woff2) format('woff2');font-weight:400 800;font-display:swap;unicode-range:U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD}
@font-face{font-family:'Syne';src:url(assets/fonts/syne-latin-ext.woff2) format('woff2');font-weight:400 800;font-display:swap;unicode-range:U+0100-02BA,U+02BD-02C5,U+02C7-02CC,U+02CE-02D7,U+02DD-02FF,U+0304,U+0308,U+0329,U+1D00-1DBF,U+1E00-1E9F,U+1EF2-1EFF,U+2020,U+20A0-20AB,U+20AD-20C0,U+2113,U+2C60-2C7F,U+A720-A7FF}
@font-face{font-family:'JetBrains Mono';src:url(assets/fonts/jetbrains-mono-latin.woff2) format('woff2');font-weight:400 800;font-display:swap;unicode-range:U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD}
@font-face{font-family:'JetBrains Mono';src:url(assets/fonts/jetbrains-mono-latin-ext.woff2) format('woff2');font-weight:400 800;font-display:swap;unicode-range:U+0100-02BA,U+02BD-02C5,U+02C7-02CC,U+02CE-02D7,U+02DD-02FF,U+0304,U+0308,U+0329,U+1D00-1DBF,U+1E00-1E9F,U+1EF2-1EFF,U+2020,U+20A0-20AB,U+20AD-20C0,U+2113,U+2C60-2C7F,U+A720-A7FF}

:root{
  color-scheme:light dark;
  --sans:'Inter',-apple-system,BlinkMacSystemFont,'SF Pro Text',system-ui,sans-serif;
  --prose:'Syne','Inter',-apple-system,system-ui,sans-serif;
  --mono:'JetBrains Mono',ui-monospace,'SF Mono',Menlo,monospace;

  --wrap:1180px;
  --pad:clamp(20px,5vw,32px);
  --section-y:clamp(56px,7.5vw,96px);
  --s1:8px;--s2:16px;--s3:24px;--s4:32px;--s5:48px;--s6:64px;

  --t-micro:clamp(.6875rem,.66rem + .1vw,.75rem);
  --t-sm:clamp(.8125rem,.79rem + .12vw,.875rem);
  --t-base:clamp(.9375rem,.91rem + .14vw,1rem);
  --t-lead:clamp(1.0625rem,1rem + .32vw,1.1875rem);
  --t-h3:clamp(1.0625rem,1.01rem + .28vw,1.1875rem);
  --t-h2:clamp(1.625rem,1.28rem + 1.5vw,2.375rem);
  --t-stat:clamp(2rem,1.5rem + 2.2vw,2.875rem);
  --t-h1:clamp(2.125rem,1.25rem + 4vw,3.625rem);

  --r-sm:6px;--r-md:10px;--r-lg:14px;--r-xl:18px;
  --ease:cubic-bezier(.22,.61,.36,1);
  --expo:cubic-bezier(.16,1,.3,1);
  --d1:140ms;--d2:240ms;--d3:520ms;

  --bg:#F6F8FB; --band:#FFFFFF; --surface:#FFFFFF; --surface-2:#F1F5FA;
  --panel:#0E1830; --panel-2:#212C42; --panel-ink:#FFFFFF;
  --panel-ink-2:rgba(255,255,255,.74); --panel-ink-3:rgba(255,255,255,.56);
  --panel-line:rgba(255,255,255,.15);
  --ink:#0E1830; --ink-2:#45536B; --ink-3:#5C6A82; --ink-4:#8B99AF;
  --line:rgba(14,24,48,.11); --line-2:rgba(14,24,48,.06); --line-3:rgba(14,24,48,.2);
  --accent:#2E5BEA; --accent-press:#1E45C8; --accent-ink:#FFFFFF;
  --accent-soft:#D9E4FE; --accent-line:#AEC5FB; --accent-panel:#94B2FF;
  --glass:rgba(255,255,255,.72);
  --logo-plate:#FFFFFF; --logo-plate-ring:none;
  --sh-1:0 0 0 .5px rgba(14,24,48,.06),0 1px 2px rgba(14,24,48,.06);
  --sh-2:0 0 0 .5px rgba(14,24,48,.07),0 4px 14px rgba(14,24,48,.08);
  --sh-3:0 0 0 .5px rgba(14,24,48,.08),0 2px 8px rgba(14,24,48,.06),0 16px 38px rgba(14,24,48,.13);
  --scroll-thumb:rgba(14,24,48,.22);
}
@media (prefers-color-scheme:dark){
  :root{
    --bg:#0A0F1E; --band:#0D1426; --surface:#141B31; --surface-2:#1A2340;
    --panel:#161F3A; --panel-2:#202B4C; --panel-ink:#F2F5FB;
    --panel-ink-2:rgba(242,245,251,.74); --panel-ink-3:rgba(242,245,251,.56);
    --panel-line:rgba(255,255,255,.11);
    --ink:#EDF1F8; --ink-2:#AEBACE; --ink-3:#8FA0B8; --ink-4:#6B788F;
    --line:rgba(255,255,255,.1); --line-2:rgba(255,255,255,.06); --line-3:rgba(255,255,255,.2);
    --accent:#7CA0FF; --accent-press:#9DB8FF; --accent-ink:#0A0F1E;
    --accent-soft:rgba(124,160,255,.16); --accent-line:rgba(124,160,255,.4); --accent-panel:#9DB8FF;
    --glass:rgba(13,20,38,.72);
    --logo-plate:#F2F5FA;
    --logo-plate-ring:inset 0 0 0 .5px rgba(14,24,48,.16);
    --sh-1:0 0 0 .5px rgba(0,0,0,.5),0 1px 2px rgba(0,0,0,.4);
    --sh-2:0 0 0 .5px rgba(0,0,0,.55),0 4px 14px rgba(0,0,0,.45);
    --sh-3:0 0 0 .5px rgba(0,0,0,.6),0 2px 8px rgba(0,0,0,.4),0 16px 38px rgba(0,0,0,.5);
    --scroll-thumb:rgba(255,255,255,.22);
  }
}

*,*::before,*::after{box-sizing:border-box}
html{-webkit-text-size-adjust:100%;scroll-behavior:smooth}
@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--sans);
  font-size:var(--t-base);line-height:1.6;font-optical-sizing:auto;
  -webkit-font-smoothing:antialiased;-moz-osx-font-smoothing:grayscale;
  text-rendering:optimizeLegibility;overflow-x:hidden}
h1,h2,h3{margin:0;font-weight:640;letter-spacing:-.022em;text-wrap:balance;line-height:1.12}
p{margin:0}
img,svg{display:block;max-width:100%}
::selection{background:var(--accent-soft);color:var(--ink)}
:focus-visible{outline:2px solid var(--accent);outline-offset:3px;border-radius:var(--r-sm)}
.panel :focus-visible{outline-color:var(--accent-panel)}
*{scrollbar-width:thin;scrollbar-color:var(--scroll-thumb) transparent}
::-webkit-scrollbar{width:11px;height:11px}
::-webkit-scrollbar-thumb{background:var(--scroll-thumb);border-radius:99px;
  border:3px solid transparent;background-clip:content-box}
::-webkit-scrollbar-track{background:transparent}
a{color:var(--accent);text-decoration:none;text-underline-offset:3px;
  text-decoration-thickness:from-font}

.wrap{max-width:var(--wrap);margin-inline:auto;padding-inline:var(--pad)}
.skip{position:absolute;left:var(--pad);top:-100px;z-index:100;background:var(--accent);
  color:var(--accent-ink);padding:10px 16px;border-radius:var(--r-md);font-weight:560;
  transition:top var(--d2) var(--ease)}
.skip:focus{top:12px}
.mono{font-family:var(--mono);font-feature-settings:"tnum" 1}
.lbl{font-family:var(--sans);font-size:var(--t-micro);font-weight:580;
  letter-spacing:.15em;text-transform:uppercase}
.prose{font-family:var(--prose);line-height:1.65;text-wrap:pretty}
.measure{max-width:64ch}

/* ---------- header ---------- */
.hdr{position:sticky;top:0;z-index:50;background:var(--glass);
  -webkit-backdrop-filter:saturate(180%) blur(20px);backdrop-filter:saturate(180%) blur(20px);
  border-bottom:.5px solid transparent;transition:border-color var(--d2) var(--ease),
  box-shadow var(--d2) var(--ease)}
.hdr[data-scrolled]{border-bottom-color:var(--line);box-shadow:0 1px 12px rgba(14,24,48,.05)}
@media (prefers-color-scheme:dark){.hdr[data-scrolled]{box-shadow:0 1px 12px rgba(0,0,0,.4)}}
.hdr-in{display:flex;align-items:center;gap:var(--s3);min-height:60px;padding-block:10px}
.brand{color:var(--ink);display:flex;align-items:baseline;gap:10px;flex-wrap:wrap;
  font-size:1.0625rem;font-weight:620;letter-spacing:-.018em}
.brand-cred{font-family:var(--mono);font-size:var(--t-micro);letter-spacing:.14em;
  color:var(--ink-3);font-weight:400}
.nav{display:flex;align-items:center;gap:clamp(14px,2.4vw,26px);margin-left:auto}
.nav-link{color:var(--ink-2);font-size:var(--t-sm);font-weight:520;position:relative;
  padding-block:4px;white-space:nowrap;transition:color var(--d1) var(--ease)}
.nav-link::after{content:"";position:absolute;left:0;right:0;bottom:0;height:1.5px;
  background:var(--accent);transform:scaleX(0);transform-origin:left;
  transition:transform var(--d2) var(--expo)}
.nav-link:hover{color:var(--ink)}
.nav-link:hover::after{transform:scaleX(1)}
/* Narrow: the section links drop to their own scrollable row instead of disappearing.
   Navigation stays reachable on a phone, and no hamburger is needed for three links. */
@media (max-width:720px){
  .hdr-in{flex-wrap:wrap;row-gap:0;min-height:0;padding-block:7px;gap:12px}
  .brand{flex:1 1 auto;font-size:1rem;flex-wrap:nowrap;min-width:0}
  .cta{order:2;padding:10px 15px}
  .nav{order:3;width:100%;margin-left:0;gap:20px;overflow-x:auto;overscroll-behavior-x:contain;
    padding-block:2px 8px;scrollbar-width:none}
  .nav::-webkit-scrollbar{display:none}
  .nav-link{padding-block:5px}
}
@media (max-width:430px){.brand-cred{display:none}}

/* ---------- buttons ---------- */
.btn{display:inline-flex;align-items:center;justify-content:center;gap:9px;
  font-family:var(--sans);font-size:var(--t-sm);font-weight:560;letter-spacing:-.006em;
  border-radius:var(--r-md);border:.5px solid transparent;cursor:pointer;
  padding:11px 18px;white-space:nowrap;
  transition:background var(--d1) var(--ease),border-color var(--d1) var(--ease),
    box-shadow var(--d1) var(--ease),transform var(--d1) var(--ease),color var(--d1) var(--ease)}
.btn:active{transform:scale(.978)}
.btn-lg{padding:14px 22px;font-size:var(--t-base)}
.btn-pri{background:var(--accent);color:var(--accent-ink);box-shadow:var(--sh-1)}
.btn-pri:hover{background:var(--accent-press);color:var(--accent-ink);box-shadow:var(--sh-2)}
.btn-sec{background:var(--surface);color:var(--ink);border-color:var(--line);box-shadow:var(--sh-1)}
.btn-sec:hover{color:var(--ink);border-color:var(--line-3);box-shadow:var(--sh-2)}
.btn-inv{background:var(--panel-ink);color:var(--panel);box-shadow:var(--sh-1)}
.btn-inv:hover{background:var(--accent-soft);color:var(--panel)}
@media (prefers-color-scheme:dark){.btn-inv:hover{background:var(--accent-press);color:var(--accent-ink)}}
.btn .ic{transition:transform var(--d2) var(--expo)}
.btn:hover .ic{transform:translateX(3px)}

/* ---------- sections ---------- */
.sec{padding-block:var(--section-y);border-bottom:.5px solid var(--line-2)}
.sec-band{background:var(--band)}
.sec-h{font-size:var(--t-h2);letter-spacing:-.026em;max-width:19ch}
.sec-lede{font-family:var(--prose);font-size:var(--t-lead);color:var(--ink-2);
  line-height:1.6;margin-top:var(--s2);max-width:58ch;text-wrap:pretty}

/* ---------- hero ---------- */
.hero{background:var(--band);border-bottom:.5px solid var(--line-2)}
.hero-in{display:grid;grid-template-columns:1.32fr .88fr;gap:clamp(36px,5vw,72px);
  align-items:center;padding-block:clamp(48px,7vw,84px)}
.hero h1{font-size:var(--t-h1);letter-spacing:-.035em;line-height:1.05;max-width:15ch}
.hero-lede{margin-top:var(--s3);font-family:var(--prose);font-size:var(--t-lead);
  color:var(--ink-2);line-height:1.62;max-width:56ch;text-wrap:pretty}
.hero-cta{display:flex;gap:12px;flex-wrap:wrap;margin-top:var(--s5)}
.hero-fig{position:relative;margin:0}
.hero-fig::before{content:"";position:absolute;inset:18px -18px -18px 18px;
  border:1px solid var(--accent-line);border-radius:var(--r-xl);pointer-events:none}
.hero-img{position:relative;width:100%;aspect-ratio:1;object-fit:cover;
  border-radius:var(--r-xl);box-shadow:var(--sh-3);background:var(--surface-2)}
@media (max-width:880px){
  .hero-in{grid-template-columns:1fr;gap:var(--s5)}
  .hero-fig{max-width:340px;order:-1}
  .hero-fig::before{inset:14px -14px -14px 14px}
}

/* ---------- stats ---------- */
.panel{background:var(--panel);color:var(--panel-ink)}
.stats{display:grid;grid-template-columns:repeat(4,1fr)}
.stat{padding:clamp(28px,3.6vw,42px) var(--s4);border-right:.5px solid var(--panel-line)}
.stat:first-child{padding-left:0}
.stat:last-child{border-right:0;padding-right:0}
.stat-n{font-size:var(--t-stat);font-weight:600;letter-spacing:-.03em;line-height:1;
  font-variant-numeric:tabular-nums}
.stat-n span{color:var(--accent-panel)}
.stat-l{margin-top:10px;color:var(--panel-ink-2)}
@media (max-width:760px){
  .stats{grid-template-columns:repeat(2,1fr)}
  .stat{padding:26px 20px;border-bottom:.5px solid var(--panel-line)}
  .stat:nth-child(2n){border-right:0;padding-right:0}
  .stat:nth-child(2n+1){padding-left:0}
  .stat:nth-last-child(-n+2){border-bottom:0}
}

/* ---------- split ---------- */
.split{display:grid;grid-template-columns:.92fr 1.08fr;gap:clamp(32px,5vw,72px)}
@media (max-width:880px){.split{grid-template-columns:1fr;gap:var(--s4)}}
.note{display:flex;gap:13px;padding:18px 20px;background:var(--surface-2);
  border:.5px solid var(--line);border-radius:var(--r-lg);margin-top:var(--s4)}
.note .ic{color:var(--accent);flex:none;margin-top:2px}
.note p{font-family:var(--prose);font-size:var(--t-sm);color:var(--ink-2);line-height:1.6}

/* ---------- marquee ---------- */
.marq{overflow:hidden;-webkit-mask-image:linear-gradient(90deg,transparent,#000 8%,#000 92%,transparent);
  mask-image:linear-gradient(90deg,transparent,#000 8%,#000 92%,transparent)}
.track{display:flex;gap:14px;width:max-content;will-change:transform}
@keyframes marq-l{from{transform:translate3d(0,0,0)}to{transform:translate3d(-33.3333%,0,0)}}
@keyframes marq-r{from{transform:translate3d(-33.3333%,0,0)}to{transform:translate3d(0,0,0)}}
.track-l{animation:marq-l 52s linear infinite}
.track-r{animation:marq-r 58s linear infinite}
.marq:hover .track,.marq:focus-within .track{animation-play-state:paused}
.net{background:var(--surface);border:.5px solid var(--line);border-radius:var(--r-lg);
  padding:16px 20px;display:flex;flex-direction:column;align-items:center;
  justify-content:center;gap:11px;min-width:246px;height:142px;box-shadow:var(--sh-1);
  transition:box-shadow var(--d2) var(--expo),border-color var(--d2) var(--ease),
    transform var(--d2) var(--expo)}
.net:hover{box-shadow:var(--sh-3);border-color:var(--accent-line);transform:translateY(-3px)}
/* Most of these marks ship with an opaque white background baked in, so they get a light
   plate in both themes rather than a filter — inverting would turn them into blank slabs. */
.net-logo{height:80px;width:100%;box-sizing:border-box;padding:6px 14px;display:flex;
  align-items:center;justify-content:center;background:var(--logo-plate);border-radius:10px;
  box-shadow:var(--logo-plate-ring)}
.net-logo img{max-height:100%;width:auto;object-fit:contain}
.net-tag{color:var(--ink-3);white-space:nowrap}
.rule{display:flex;align-items:center;gap:14px;color:var(--ink-3);margin-top:var(--s3)}
.rule::before,.rule::after{content:"";flex:1;height:.5px;background:var(--line)}
@media (prefers-reduced-motion:reduce){
  .track{animation:none!important}
  .marq{overflow-x:auto;-webkit-mask-image:none;mask-image:none;
    scroll-snap-type:x mandatory;padding-bottom:8px}
  .net{scroll-snap-align:center}
}

/* ---------- formats ---------- */
.fmts{display:grid;grid-template-columns:repeat(5,1fr);gap:var(--s3);margin-top:var(--s5)}
.fmt{border-top:1.5px solid var(--ink);padding-top:18px}
.fmt .ic{color:var(--accent)}
.fmt h3{font-size:var(--t-h3);margin:14px 0 7px;letter-spacing:-.016em}
.fmt p{font-family:var(--prose);font-size:var(--t-sm);color:var(--ink-3);line-height:1.55}
@media (max-width:980px){.fmts{grid-template-columns:repeat(2,1fr);gap:var(--s3) var(--s4)}}
@media (max-width:520px){.fmts{grid-template-columns:1fr}}

/* ---------- accordion ---------- */
.acc-top{display:flex;align-items:flex-end;justify-content:space-between;
  gap:var(--s4);flex-wrap:wrap;margin-bottom:var(--s4)}
.acc{background:var(--surface);border:.5px solid var(--line);border-radius:var(--r-xl);
  overflow:hidden;box-shadow:var(--sh-1)}
.acc-item+.acc-item{border-top:.5px solid var(--line-2)}
.acc-btn{width:100%;display:flex;align-items:center;gap:var(--s3);padding:19px 24px;
  background:transparent;border:0;cursor:pointer;text-align:left;color:inherit;
  font-family:var(--sans);transition:background var(--d1) var(--ease)}
.acc-btn:hover{background:var(--surface-2)}
.acc-btn:focus-visible{outline-offset:-3px}
.acc-t{flex:1;font-size:var(--t-h3);font-weight:600;letter-spacing:-.016em;line-height:1.3}
.acc-c{font-family:var(--mono);font-size:var(--t-sm);color:var(--ink-3);
  background:var(--surface-2);border:.5px solid var(--line);border-radius:99px;
  padding:3px 11px;flex:none;font-variant-numeric:tabular-nums}
.acc-btn .ic{color:var(--ink-4);flex:none;transition:transform var(--d2) var(--expo),
  color var(--d1) var(--ease)}
.acc-btn[aria-expanded=true] .ic{transform:rotate(180deg);color:var(--accent)}
.acc-panel{display:grid;grid-template-rows:0fr;transition:grid-template-rows var(--d3) var(--expo)}
.acc-btn[aria-expanded=true]+.acc-panel{grid-template-rows:1fr}
.acc-panel>div{overflow:hidden}
.acc-body{columns:3;column-gap:var(--s5);padding:2px 24px 26px}
@media (max-width:900px){.acc-body{columns:2;column-gap:var(--s4)}}
@media (max-width:600px){.acc-body{columns:1}}
.topic{break-inside:avoid;display:flex;gap:10px;padding:4px 0;font-family:var(--prose);
  font-size:var(--t-sm);color:var(--ink-2);line-height:1.5}
.topic::before{content:"";width:4px;height:4px;border-radius:50%;background:var(--accent-line);
  flex:none;margin-top:8px}
@media (prefers-reduced-motion:reduce){.acc-panel{transition:none}}

/* ---------- contact ---------- */
.contact-in{display:grid;grid-template-columns:1fr 1fr;gap:clamp(32px,5vw,72px);align-items:start}
@media (max-width:880px){.contact-in{grid-template-columns:1fr}}
.contact-h{font-size:var(--t-h2);letter-spacing:-.026em;color:var(--panel-ink);max-width:16ch}
.contact-p{font-family:var(--prose);font-size:var(--t-lead);color:var(--panel-ink-2);
  margin-top:var(--s2);max-width:46ch;line-height:1.6;text-wrap:pretty}
.chan{display:flex;flex-direction:column;border:.5px solid var(--panel-line);
  border-radius:var(--r-xl);overflow:hidden}
.chan a{display:flex;align-items:center;gap:15px;padding:19px 22px;color:var(--panel-ink);
  transition:background var(--d1) var(--ease)}
.chan a+a{border-top:.5px solid var(--panel-line)}
.chan a:hover{background:var(--panel-2);color:var(--panel-ink)}
.chan .ic{color:var(--accent-panel);flex:none}
.chan-k{display:block;color:var(--panel-ink-3);margin-bottom:3px}
.chan-v{display:block;font-size:var(--t-sm);color:var(--panel-ink)}

/* ---------- footer ---------- */
.ft{background:var(--panel);border-top:.5px solid var(--panel-line)}
.ft-in{display:flex;align-items:center;justify-content:space-between;gap:var(--s3);
  flex-wrap:wrap;padding-block:26px}
.ft-name{color:var(--panel-ink);font-weight:520}
.ft-meta{color:var(--panel-ink-3)}

/* ---------- the one authored moment: hero entrance ---------- */
@media (prefers-reduced-motion:no-preference){
  @keyframes rise{from{opacity:0;transform:translate3d(0,14px,0);filter:blur(6px)}
                  to{opacity:1;transform:none;filter:blur(0)}}
  @keyframes settle{from{opacity:0;transform:scale(.975)}to{opacity:1;transform:none}}
  @keyframes draw{from{opacity:0;transform:translate3d(-10px,-10px,0)}to{opacity:1;transform:none}}
  .hero h1,.hero-lede,.hero-cta{animation:rise var(--d3) var(--expo) both}
  .hero-lede{animation-delay:70ms}
  .hero-cta{animation-delay:140ms}
  .hero-img{animation:settle 640ms var(--expo) both;animation-delay:60ms}
  .hero-fig::before{animation:draw 640ms var(--expo) both;animation-delay:200ms}
}

@media print{
  .hdr,.marq,.hero-fig,.skip{display:none!important}
  body{background:#fff;color:#000}
  .panel,.ft{background:#fff!important;color:#000!important}
  .contact-h,.chan a,.chan-v,.ft-name,.stat-n{color:#000!important}
  .acc-panel{grid-template-rows:1fr!important}
  .sec{padding-block:22px;border-bottom:1px solid #ccc}
  a[href^=http]::after{content:" (" attr(href) ")";font-size:9px;color:#555}
}
"""

# ---------------------------------------------------------------- html
def net_card(n, dup):
    slug = n["logo"].split("/")[-1].replace(".png", "")
    alt = "" if dup else f'{n["name"]} logo'
    return (f'<div class="net">'
            f'<span class="net-logo"><img src="assets/logos/{slug}.webp" alt="{e(alt)}" '
            f'loading="lazy" decoding="async" style="height:{n["h"]}px"></span>'
            f'<span class="net-tag lbl">{e(n["tag"])}</span></div>')

def marquee(items, direction, label):
    # Three copies make the -33.33% loop seamless; only the first is exposed to AT.
    real = "".join(net_card(n, False) for n in items)
    dupe = "".join(net_card(n, True) for n in items) * 2
    return (f'<div class="marq" role="group" aria-label="{e(label)}">'
            f'<div class="track track-{direction}">{real}'
            f'<span aria-hidden="true" style="display:contents">{dupe}</span>'
            f'</div></div>')

def accordion():
    out = []
    for i, (title, topics) in enumerate(GROUPS):
        tid = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
        body = "".join(f'<span class="topic">{e(t)}</span>' for t in topics)
        out.append(
            f'<div class="acc-item">'
            f'<button class="acc-btn" type="button" aria-expanded="false" aria-controls="p-{tid}" id="b-{tid}">'
            f'<span class="acc-t">{e(title)}</span>'
            f'<span class="acc-c">{len(topics)}</span>{icon(IC["chev"], 18, "1.9")}</button>'
            f'<div class="acc-panel" id="p-{tid}" role="region" aria-labelledby="b-{tid}">'
            f'<div><div class="acc-body">{body}</div></div></div></div>')
    return "".join(out)

CHANNELS = [
    ("mail",  f"mailto:{EMAIL}",              "Email",      EMAIL, False),
    ("phone", f"tel:{PHONE_E164}",            "Phone",      PHONE_DISP, False),
    ("chat",  f"https://wa.me/{PHONE_E164.lstrip('+')}", "WhatsApp", "Message me directly", True),
    ("linked", LINKEDIN,                      "LinkedIn",   "mohit-sharma-acma-cgma", True),
    ("cal",    BOOKING,                       "Scheduling", "Pick a time on my calendar", True),
]

def channels():
    out = []
    for k, href, label, val, ext in CHANNELS:
        a = ' target="_blank" rel="noopener"' if ext else ""
        out.append(f'<a href="{e(href)}"{a}>{icon(IC[k], 19, "1.7")}<span>'
                   f'<span class="chan-k lbl">{e(label)}</span>'
                   f'<span class="chan-v">{e(val)}</span></span></a>')
    return "".join(out)

DESC = ("Mohit Sharma (ACMA, CGMA) is an emerging-technologies specialist and enterprise "
        "architect with 25+ years in consulting and 1,200+ expert-network consultations "
        "across 315 topics.")

JSONLD = json.dumps({
    "@context": "https://schema.org", "@type": "Person",
    "name": "Mohit Sharma", "honorificSuffix": "ACMA, CGMA",
    "jobTitle": "Expert Network Advisor",
    "description": DESC, "url": SITE_URL,
    "image": SITE_URL + "assets/headshot.webp",
    "email": f"mailto:{EMAIL}", "telephone": PHONE_E164,
    "address": {"@type": "PostalAddress", "addressLocality": "Bengaluru", "addressCountry": "IN"},
    "sameAs": [LINKEDIN],
    "knowsAbout": [g[0] for g in GROUPS],
    "alumniOf": [{"@type": "Organization", "name": n} for n in
                 ("Accenture", "IBM", "Capgemini", "Genpact")],
}, separators=(",", ":"))

stats_html = "".join(
    f'<div class="stat"><div class="stat-n">{n}<span>{s}</span></div>'
    f'<div class="stat-l lbl">{e(l)}</div></div>' for n, s, l in STATS)

fmts_html = "".join(
    f'<div class="fmt">{icon(IC[k], 21)}<h3>{e(t)}</h3><p>{e(d)}</p></div>'
    for k, t, d in FORMATS)

HTML = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>Mohit Sharma — Expert Network Advisor</title>
<meta name="description" content="{e(DESC)}">
<link rel="canonical" href="{SITE_URL}">
<meta name="theme-color" content="#FFFFFF" media="(prefers-color-scheme:light)">
<meta name="theme-color" content="#0A0F1E" media="(prefers-color-scheme:dark)">
<meta property="og:type" content="profile">
<meta property="og:title" content="Mohit Sharma — Expert Network Advisor">
<meta property="og:description" content="{e(DESC)}">
<meta property="og:url" content="{SITE_URL}">
<meta property="og:image" content="{SITE_URL}assets/og.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="assets/apple-touch-icon.png">
<link rel="preload" as="font" type="font/woff2" href="assets/fonts/inter-latin.woff2" crossorigin>
<link rel="preload" as="image" href="assets/headshot.webp" fetchpriority="high">
<style>{CSS}</style>
<script type="application/ld+json">{JSONLD}</script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>

<header class="hdr" id="top">
  <div class="wrap hdr-in">
    <a class="brand" href="#top">Mohit Sharma <span class="brand-cred">ACMA · CGMA</span></a>
    <nav class="nav" aria-label="Primary">
      <a class="nav-link" href="#background">Background</a>
      <a class="nav-link" href="#networks">Networks</a>
      <a class="nav-link" href="#expertise">Expertise</a>
    </nav>
    <a class="btn btn-pri cta" href="{BOOKING}" target="_blank" rel="noopener">Book a call</a>
  </div>
</header>

<main id="main">

  <section class="hero">
    <div class="wrap hero-in">
      <div>
        <h1>Emerging technology, explained by someone who has delivered it.</h1>
        <p class="hero-lede">I'm an emerging-technologies specialist with an enterprise
          architecture background and more than 25 years in consulting. I've completed
          1,200+ consultations with market-leading expert networks — helping investors,
          strategy teams, and operators get to a clear answer quickly.</p>
        <div class="hero-cta">
          <a class="btn btn-pri btn-lg" href="{BOOKING}" target="_blank" rel="noopener">
            Schedule a consultation{icon(IC["arrow"], 17, "1.9")}</a>
          <a class="btn btn-sec btn-lg" href="mailto:{EMAIL}">{icon(IC["mail"], 17, "1.7")}Email me</a>
        </div>
      </div>
      <figure class="hero-fig">
        <img class="hero-img" src="assets/headshot.webp" width="800" height="800"
             alt="Mohit Sharma" fetchpriority="high" decoding="async">
      </figure>
    </div>
  </section>

  <section class="panel" aria-label="Track record">
    <div class="wrap"><div class="stats">{stats_html}</div></div>
  </section>

  <section class="sec sec-band" id="background" style="scroll-margin-top:72px">
    <div class="wrap split">
      <h2 class="sec-h">Twenty-five years on the delivery side of enterprise technology.</h2>
      <div>
        <p class="prose measure" style="font-size:var(--t-lead);color:var(--ink-2)">I've worked
          globally across industries and sectors with Fortune 100 clients, at firms including
          <strong style="color:var(--ink);font-weight:620">Accenture</strong>,
          <strong style="color:var(--ink);font-weight:620">IBM</strong>,
          <strong style="color:var(--ink);font-weight:620">Capgemini</strong>, and
          <strong style="color:var(--ink);font-weight:620">Genpact</strong> — evaluating,
          designing, and delivering transformation solutions for genuinely complex use cases.</p>
        <p class="prose measure" style="font-size:var(--t-lead);color:var(--ink-2);margin-top:var(--s3)">
          That means I can speak to a category from three angles at once: what the technology
          actually does, how buyers evaluate and procure it, and what happens after the contract
          is signed. It's a useful vantage point when you're sizing a market, diligencing a
          vendor, or testing a thesis.</p>
        <div class="note">{icon(IC["shield"], 19, "1.7")}<p>No employer-confidentiality
          restrictions and no public-company exposure restrictions. I complete every network's
          compliance training and work strictly within its guidelines.</p></div>
      </div>
    </div>
  </section>

  <section class="sec" id="networks" style="scroll-margin-top:72px">
    <div class="wrap">
      <h2 class="sec-h">Trusted by the networks your clients already use.</h2>
      <p class="sec-lede">I'm an active, compliance-cleared expert with 40+ networks worldwide.
        Those I work with most often:</p>
    </div>
    <div style="padding-block:var(--s4) 12px">
      {marquee(NETWORKS[:7], "l", "Expert networks, part 1")}
    </div>
    <div style="padding-bottom:var(--s3)">
      {marquee(NETWORKS[7:], "r", "Expert networks, part 2")}
    </div>
    <div class="wrap"><p class="rule lbl">+ 27 further networks worldwide</p></div>
  </section>

  <section class="sec sec-band" id="formats">
    <div class="wrap">
      <h2 class="sec-h">Formats I take on.</h2>
      <div class="fmts">{fmts_html}</div>
    </div>
  </section>

  <section class="sec" id="expertise" style="scroll-margin-top:72px">
    <div class="wrap">
      <div class="acc-top">
        <div>
          <h2 class="sec-h">315 topics across 15 domains.</h2>
          <p class="sec-lede">If a project touches any of these, I can almost certainly help —
            or tell you honestly that I can't. Open a domain to see the full list.</p>
        </div>
        <button class="btn btn-sec" type="button" id="toggle-all" aria-pressed="false">Expand all</button>
      </div>
      <div class="acc">{accordion()}</div>
    </div>
  </section>

  <section class="panel" id="contact" style="scroll-margin-top:72px">
    <div class="wrap contact-in" style="padding-block:var(--section-y)">
      <div>
        <h2 class="contact-h">Have a project that fits? Let's talk.</h2>
        <p class="contact-p">Coordinators and recruiters — send the brief and I'll confirm fit
          the same day. I'm based in India (IST) and regularly take calls across US and
          European hours.</p>
        <a class="btn btn-inv btn-lg" href="{BOOKING}" target="_blank" rel="noopener"
           style="margin-top:var(--s4)">Book a 30-minute slot{icon(IC["north"], 16, "1.9")}</a>
      </div>
      <div class="chan">{channels()}</div>
    </div>
  </section>

</main>

<footer class="ft">
  <div class="wrap ft-in">
    <span class="ft-name">Mohit Sharma · ACMA, CGMA</span>
    <span class="ft-meta lbl">Expert network advisor · Bengaluru, India</span>
  </div>
</footer>

<script>
(function(){{
  // Toggling one attribute is cheap and reads no layout, so it runs straight off the
  // scroll event. A rAF throttle would add nothing and would stall in a hidden tab.
  var hdr=document.querySelector('.hdr');
  function sync(){{ hdr.toggleAttribute('data-scrolled', window.scrollY>4); }}
  addEventListener('scroll',sync,{{passive:true}});
  addEventListener('pageshow',sync);
  sync();

  var btns=[].slice.call(document.querySelectorAll('.acc-btn')),
      all=document.getElementById('toggle-all');
  function open(b,v){{ b.setAttribute('aria-expanded',String(v)); }}
  function refresh(){{
    var every=btns.every(function(b){{ return b.getAttribute('aria-expanded')==='true'; }});
    all.textContent=every?'Collapse all':'Expand all';
    all.setAttribute('aria-pressed',String(every));
  }}
  btns.forEach(function(b){{
    b.addEventListener('click',function(){{
      open(b,b.getAttribute('aria-expanded')!=='true'); refresh();
    }});
  }});
  all.addEventListener('click',function(){{
    var v=all.getAttribute('aria-pressed')!=='true';
    btns.forEach(function(b){{ open(b,v); }}); refresh();
  }});
}})();
</script>
</body>
</html>
"""

os.makedirs(OUT, exist_ok=True)
open(f"{OUT}/index.html", "w", encoding="utf-8").write(HTML)
open(f"{OUT}/.nojekyll", "w").close()
print("wrote index.html:", round(len(HTML.encode()) / 1024, 1), "KB")
