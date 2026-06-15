"""
Builds mosswell-slider-handoff-v4.html — a SAFE COPY whose in-page card matches the
full-homepage reference's EXACT footprint (max-width 720px desktop / 360px mobile,
frame aspect 1280:670 desktop / 390:448 mobile, Before/After labels strip above the
frame, expand icon bottom-RIGHT) while keeping the original Mosswell premium look
(rich gallery hero, serif title, benefit chips). The slider handle is filled BLUE
with a WHITE hand + two chevrons and gives a one-time intro sweep so it visibly
"moves both ways."

Source images come from scripts/capture-comps-v4.js (the rich premium hero cards).
The original build_handoff.py / v2 / v3 and the *-codex.* files are left untouched.
Run:  python scripts/build_handoff_v4.py
"""
import base64, html, pathlib

HERE = pathlib.Path(__file__).parent
ROOT = HERE.parent
SHOTS = ROOT / "screenshots"

def data_uri(name):
    b = (SHOTS / name).read_bytes()
    mime = "image/jpeg" if name.endswith((".jpg", ".jpeg")) else "image/png"
    return f"data:{mime};base64," + base64.b64encode(b).decode("ascii")

imgs = {
    "bd": data_uri("comp-v4-before-desktop.jpg"),   # 1280:670
    "ad": data_uri("comp-v4-after-desktop.jpg"),    # 1280:670
    "bm": data_uri("comp-v4-before-mobile.jpg"),    # 390:448
    "am": data_uri("comp-v4-after-mobile.jpg"),     # 390:448
}

component_src = (ROOT / "components" / "BeforeAfter-v4.jsx").read_text(encoding="utf-8")

usage_snippet = '''import BeforeAfter from '@/components/BeforeAfter';

// ...inside the Mosswell skincare demo-store card, replace the placeholder
// <div className="relative w-full ...">...</div> with:

<BeforeAfter
  beforeSrc="/demos/mosswell-before-card.jpg"
  afterSrc="/demos/mosswell-after-card.jpg"
  beforeSrcMobile="/demos/mosswell-before-card-mobile.jpg"
  afterSrcMobile="/demos/mosswell-after-card-mobile.jpg"
  beforeAlt="Mosswell — original product card"
  afterAlt="Mosswell — AdflowEZ rebuild"
/>'''

comp_esc = html.escape(component_src)
use_esc = html.escape(usage_snippet)

HTML = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Mosswell — Before/After slider v4 (matched to the full-homepage frame)</title>
<style>
  :root {{ --blue:#3B7CF4; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:#eef2f7; color:#0f172a;
          font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif; padding:32px 16px; }}
  .wrap {{ max-width:860px; margin:0 auto; }}
  h1 {{ font-size:24px; margin:0 0 4px; }}
  .sub {{ color:#64748b; margin:0 0 28px; }}
  .panel {{ background:#fff; border:1px solid #e2e8f0; border-radius:14px; padding:22px; margin-bottom:22px;
            box-shadow:0 6px 20px rgba(0,0,0,.05); }}
  .panel h2 {{ font-size:15px; text-transform:uppercase; letter-spacing:.06em; color:var(--blue); margin:0 0 14px; }}
  .note {{ font-size:13px; color:#475569; line-height:1.6; }}
  /* on phones, trim side padding so the in-page card runs (near) full width — matches the reference */
  @media(max-width:639px){{
    body {{ padding:20px 8px; }}
    .panel {{ padding:14px; }}
  }}

  /* ---------- in-page PRODUCT CARD (before-expansion view) — footprint matched to the reference ---------- */
  .card {{ border-radius:12px; border:1px solid #e2e8f0; overflow:hidden; max-width:360px; margin:0 auto; }}
  @media(min-width:640px){{ .card {{ max-width:720px; }} }}
  /* Before/After labels live in a strip ABOVE the frame so they never cover the photo */
  .ba__labels {{ display:flex; align-items:center; justify-content:space-between; padding:9px 12px 10px; }}
  .ba__labels .l {{ font-size:12px; font-weight:600; padding:4px 12px; border-radius:6px; color:#fff; letter-spacing:.01em; }}
  .ba__labels .l--before {{ background:rgba(15,23,42,.7); }}
  .ba__labels .l--after  {{ background:var(--blue); }}

  /* frame: mobile 390:448, desktop 1280:670 — each breakpoint loads its own source image at its own aspect */
  .ba {{ position:relative; width:100%; aspect-ratio:390/448; overflow:hidden; background:#fff;
         user-select:none; -webkit-user-select:none; cursor:default; }}
  @media(min-width:640px){{ .ba {{ aspect-ratio:1280/670; }} }}
  .ba__before {{ position:absolute; inset:0; display:block; }}
  /* AFTER wipes in from the LEFT: handle far-left = all Before, far-right = all After. */
  .ba__after {{ position:absolute; inset:0; clip-path:inset(0 50% 0 0); }}
  .ba__after picture {{ position:absolute; inset:0; display:block; }}
  .ba__before img, .ba__after img {{ position:absolute; inset:0; width:100%; height:100%;
         object-fit:cover; object-position:center; display:block; pointer-events:none; }}
  .ba__line {{ position:absolute; top:0; bottom:0; width:2px; background:#fff;
               box-shadow:0 0 4px rgba(0,0,0,.3); left:50%; pointer-events:none; transform:translateX(-50%); }}

  /* NEW handle: filled BLUE, WHITE hand + two chevrons (slides both ways) */
  .ba__handle {{ position:absolute; top:50%; left:50%; transform:translate(-50%,-50%);
                 width:50px; height:50px; border-radius:9999px; background:var(--blue); border:3px solid #fff;
                 box-shadow:0 6px 16px rgba(0,0,0,.32); display:flex; align-items:center; justify-content:center;
                 cursor:grab; touch-action:none; z-index:3; }}
  .ba__handle:active {{ cursor:grabbing; }}
  .ba__handle:focus {{ outline:2px solid var(--blue); outline-offset:2px; }}
  .ba__handle::before {{ content:''; position:absolute; inset:-7px; border-radius:9999px;
                         border:2px solid rgba(255,255,255,.65); animation:tolPulse 1.8s ease-out infinite; pointer-events:none; }}
  @keyframes tolPulse {{ 0%{{transform:scale(.9);opacity:.8}} 70%{{transform:scale(1.35);opacity:0}} 100%{{opacity:0}} }}
  .hrow {{ display:flex; align-items:center; gap:3px; }}
  .hrow svg {{ display:block; fill:none; stroke:#fff; stroke-width:2; stroke-linecap:round; stroke-linejoin:round; }}
  .hhand {{ width:14px; height:14px; }}
  .hchev {{ width:7px; height:12px; }}

  /* one-time intro sweep so it visibly moves both ways; instant once you grab it */
  .ba--demo .ba__after {{ transition:clip-path .55s cubic-bezier(.4,0,.2,1); }}
  .ba--demo .ba__line, .ba--demo .ba__handle {{ transition:left .55s cubic-bezier(.4,0,.2,1); }}

  /* expand button — bottom-RIGHT of the card */
  .ba__expand {{ position:absolute; bottom:12px; right:12px; width:36px; height:36px; border-radius:8px;
                 background:rgba(255,255,255,.9); border:1px solid #e2e8f0; box-shadow:0 2px 6px rgba(0,0,0,.15);
                 display:flex; align-items:center; justify-content:center; cursor:pointer; z-index:4; }}
  .ba__expand:hover {{ background:#fff; }}

  /* ---------- expand modal: same comparison, bigger ---------- */
  .modal {{ position:fixed; inset:0; background:rgba(15,23,42,.85); display:none; align-items:center; justify-content:center;
            padding:14px; z-index:1000; }}
  @media(min-width:640px){{ .modal {{ padding:32px; }} }}
  .modal.open {{ display:flex; }}
  .modal__content {{ position:relative; width:100%; max-width:1100px; }}
  .modal__close {{ position:absolute; top:-38px; right:0; background:none; border:none; color:#fff; font-size:14px;
                   font-weight:600; cursor:pointer; display:flex; align-items:center; gap:6px; }}
  .card2 .card {{ margin:0; max-width:none; width:100%; box-shadow:0 20px 60px rgba(0,0,0,.5); }}
  /* DESKTOP expand: bigger, fits on screen. */
  @media(min-width:640px){{
    .modal__content {{ width:min(1100px, 96vw); max-width:96vw; }}
    .card2 .ba {{ aspect-ratio:1280/670; }}
  }}
  /* MOBILE expand: full-width, edge-to-edge. */
  @media(max-width:639px){{
    .modal {{ padding:0; }}
    .modal__content {{ width:100vw; max-width:100vw; }}
    .card2 .card {{ border-radius:0; }}
    .card2 .ba {{ aspect-ratio:390/448; }}
    .modal__close {{ position:fixed; top:10px; right:12px; background:rgba(15,23,42,.55); padding:6px 10px; border-radius:8px; z-index:5; }}
  }}
  .resizehint {{ text-align:center; font-size:12px; color:#94a3b8; margin-top:10px; }}

  /* ---------- downloads ---------- */
  .grid {{ display:grid; grid-template-columns:repeat(2,1fr); gap:14px; }}
  .dl {{ border:1px solid #e2e8f0; border-radius:10px; padding:10px; text-align:center; background:#fafbfc; }}
  .dl img {{ width:100%; border-radius:6px; border:1px solid #eef2f7; display:block; margin-bottom:8px; }}
  .dl .lbl {{ font-size:12px; color:#475569; margin-bottom:8px; }}
  .btn {{ display:inline-block; background:var(--blue); color:#fff; text-decoration:none; font-size:13px; font-weight:600;
          padding:7px 14px; border-radius:8px; border:none; cursor:pointer; }}
  .btn:hover {{ filter:brightness(1.05); }}

  /* ---------- code boxes ---------- */
  .codewrap {{ position:relative; }}
  .copy {{ position:absolute; top:10px; right:10px; }}
  pre {{ background:#0f172a; color:#e2e8f0; padding:16px; border-radius:10px; overflow:auto; font-size:12.5px; line-height:1.55; margin:0; max-height:420px; }}
  code {{ font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace; }}

  @media (prefers-reduced-motion: reduce){{ .ba__handle::before {{ animation:none; }} }}
</style>
</head>
<body>
<div class="wrap">
  <h1>Mosswell — Before / After slider</h1>
  <p class="sub">Everything's in this one file. Preview it, download the photos, copy the code. Works for desktop and mobile.</p>

  <!-- LIVE PREVIEW -->
  <div class="panel">
    <h2>1 · Live preview (drag it)</h2>
    <div class="card">
      <div class="ba__labels">
        <span class="l l--before">Before</span>
        <span class="l l--after">After</span>
      </div>
      <div class="ba" id="ba">
        <picture class="ba__before">
          <source media="(max-width:639px)" srcset="{imgs['bm']}">
          <img src="{imgs['bd']}" alt="Mosswell original store card">
        </picture>
        <div class="ba__after" id="baAfter">
          <picture>
            <source media="(max-width:639px)" srcset="{imgs['am']}">
            <img src="{imgs['ad']}" alt="Mosswell AdflowEZ rebuild">
          </picture>
        </div>
        <div class="ba__line" id="baLine"></div>
        <div class="ba__handle" id="baHandle" role="slider" tabindex="0"
             aria-label="Drag to compare — slides both ways" aria-valuemin="0" aria-valuemax="100" aria-valuenow="50">
          <span class="hrow">
            <svg class="hchev" viewBox="0 0 10 16"><path d="M8 2 2 8 8 14"/></svg>
            <svg class="hhand" viewBox="0 0 24 24">
              <path d="M18 11V6a2 2 0 0 0-2-2v0a2 2 0 0 0-2 2v0"/>
              <path d="M14 10V4a2 2 0 0 0-2-2v0a2 2 0 0 0-2 2v2"/>
              <path d="M10 10.5V6a2 2 0 0 0-2-2v0a2 2 0 0 0-2 2v8"/>
              <path d="M18 8a2 2 0 1 1 4 0v6a8 8 0 0 1-8 8h-2c-2.8 0-4.5-.86-5.99-2.34l-3.6-3.6a2 2 0 0 1 2.83-2.82L7 15"/>
            </svg>
            <svg class="hchev" viewBox="0 0 10 16"><path d="M2 2 8 8 2 14"/></svg>
          </span>
        </div>
        <button class="ba__expand" id="baExpand" type="button" aria-label="Open a larger view">
          <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="#0f172a" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 3H3v5M16 3h5v5M3 16v5h5M21 16v5h-5"/></svg>
        </button>
      </div>
    </div>
    <p class="resizehint">Drag the blue circle to compare — it slides both ways. Click the expand icon (bottom-right) for a larger view. Narrow the window to see the mobile layout.</p>
  </div>

  <!-- EXPAND POPUP -->
  <div class="modal" id="modal" aria-hidden="true">
    <div class="modal__content">
      <button class="modal__close" id="modalClose" aria-label="Close">Close
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg>
      </button>
      <div class="card2" id="modalBody"></div>
    </div>
  </div>

  <!-- DOWNLOAD IMAGES -->
  <div class="panel">
    <h2>2 · Download the photos</h2>
    <p class="note" style="margin-top:0">Put all four in your project's <code>public/demos/</code> folder. Desktop = 1280:670, Mobile = 390:448.</p>
    <div class="grid">
      <div class="dl"><img src="{imgs['bd']}" alt=""><div class="lbl">Before · desktop 1280:670 (2x)</div><a class="btn" download="mosswell-before-card.jpg" href="{imgs['bd']}">Download</a></div>
      <div class="dl"><img src="{imgs['ad']}" alt=""><div class="lbl">After · desktop 1280:670 (2x)</div><a class="btn" download="mosswell-after-card.jpg" href="{imgs['ad']}">Download</a></div>
      <div class="dl"><img src="{imgs['bm']}" alt=""><div class="lbl">Before · mobile 390:448 (2x)</div><a class="btn" download="mosswell-before-card-mobile.jpg" href="{imgs['bm']}">Download</a></div>
      <div class="dl"><img src="{imgs['am']}" alt=""><div class="lbl">After · mobile 390:448 (2x)</div><a class="btn" download="mosswell-after-card-mobile.jpg" href="{imgs['am']}">Download</a></div>
    </div>
  </div>

  <!-- CODE: COMPONENT -->
  <div class="panel">
    <h2>3 · Copy the component → <code>components/BeforeAfter.jsx</code></h2>
    <div class="codewrap">
      <button class="btn copy" onclick="copyEl('compcode', this)">Copy</button>
      <pre><code id="compcode">{comp_esc}</code></pre>
    </div>
  </div>

  <!-- CODE: USAGE -->
  <div class="panel">
    <h2>4 · Paste this where the Mosswell demo-store placeholder is</h2>
    <div class="codewrap">
      <button class="btn copy" onclick="copyEl('usecode', this)">Copy</button>
      <pre><code id="usecode">{use_esc}</code></pre>
    </div>
    <p class="note">That's it — deploy and the Mosswell demo-store card becomes a real drag-to-compare slider, matched to your existing one.</p>
  </div>
</div>

<script>
function wire(ba) {{
  var after=ba.querySelector('.ba__after'), line=ba.querySelector('.ba__line'),
      handle=ba.querySelector('.ba__handle'), dragging=false;
  function setPos(p){{ p=Math.max(0,Math.min(100,p)); after.style.clipPath='inset(0 '+(100-p)+'% 0 0)'; line.style.left=p+'%'; handle.style.left=p+'%'; handle.setAttribute('aria-valuenow',Math.round(p)); }}
  function fromX(x){{ var r=ba.getBoundingClientRect(); setPos(((x-r.left)/r.width)*100); }}
  handle.addEventListener('pointerdown',function(e){{ dragging=true; handle.setPointerCapture&&handle.setPointerCapture(e.pointerId); }});
  handle.addEventListener('pointermove',function(e){{ if(dragging) fromX(e.clientX); }});
  handle.addEventListener('pointerup',function(e){{ dragging=false; handle.releasePointerCapture&&handle.releasePointerCapture(e.pointerId); }});
  handle.addEventListener('pointercancel',function(){{ dragging=false; }});
  handle.addEventListener('keydown',function(e){{ var n=parseFloat(handle.getAttribute('aria-valuenow'))||50;
    if(e.key==='ArrowLeft')setPos(n-2); else if(e.key==='ArrowRight')setPos(n+2); else if(e.key==='Home')setPos(0); else if(e.key==='End')setPos(100); }});
  return setPos;
}}
var mainBa=document.getElementById('ba');
var mainSetPos=wire(mainBa);

/* one-time intro sweep: demonstrate the handle moves BOTH ways (respects reduced-motion) */
(function introSweep(){{
  if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  var cancelled=false;
  function stop(){{ cancelled=true; mainBa.classList.remove('ba--demo'); }}
  mainBa.addEventListener('pointerdown', stop, {{once:true}});
  setTimeout(function(){{
    if(cancelled) return;
    mainBa.classList.add('ba--demo');
    var steps=[{{p:66,t:0}},{{p:34,t:620}},{{p:50,t:1240}}];
    steps.forEach(function(s){{ setTimeout(function(){{ if(!cancelled) mainSetPos(s.p); }}, s.t); }});
    setTimeout(function(){{ if(!cancelled) mainBa.classList.remove('ba--demo'); }}, 1900);
  }}, 700);
}})();

var modal=document.getElementById('modal'), modalBody=document.getElementById('modalBody');
var lastTrigger=null;
function openModal(){{
  lastTrigger=document.activeElement;
  var clone=document.querySelector('.card').cloneNode(true);
  clone.querySelectorAll('[id]').forEach(function(n){{ n.removeAttribute('id'); }});
  var ex=clone.querySelector('.ba__expand'); if(ex) ex.remove();
  var cba=clone.querySelector('.ba'); cba.classList.remove('ba--demo');
  cba.querySelector('.ba__after').style.clipPath='inset(0 50% 0 0)';
  cba.querySelector('.ba__line').style.left='50%';
  cba.querySelector('.ba__handle').style.left='50%';
  cba.querySelector('.ba__handle').setAttribute('aria-valuenow','50');
  modalBody.innerHTML=''; modalBody.appendChild(clone); wire(cba);
  modal.classList.add('open'); modal.setAttribute('aria-hidden','false'); document.body.style.overflow='hidden';
  document.getElementById('modalClose').focus();
}}
function closeModal(){{ modal.classList.remove('open'); modal.setAttribute('aria-hidden','true'); modalBody.innerHTML=''; document.body.style.overflow='';
  if(lastTrigger&&lastTrigger.focus) lastTrigger.focus(); }}
document.getElementById('baExpand').addEventListener('click', openModal);
document.getElementById('modalClose').addEventListener('click', closeModal);
modal.addEventListener('click', function(e){{ if(e.target===modal) closeModal(); }});
document.addEventListener('keydown', function(e){{ if(e.key==='Escape' && modal.classList.contains('open')) closeModal(); }});

function copyEl(id, btn){{
  var t=document.getElementById(id).innerText;
  navigator.clipboard.writeText(t).then(function(){{ var o=btn.textContent; btn.textContent='Copied!'; setTimeout(function(){{btn.textContent=o;}},1400); }});
}}
</script>
</body>
</html>
"""

out = ROOT / "mosswell-slider-handoff-v4.html"
out.write_text(HTML, encoding="utf-8")
print("wrote", out, "(", round(len(HTML) / 1024), "KB )")
