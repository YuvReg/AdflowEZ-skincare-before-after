"""
Assembles ONE self-contained handoff file: mosswell-slider-handoff.html
- live, responsive before/after slider (desktop 16:9 / mobile 4:5)
- the 4 product-page screenshots embedded as data URIs, each with a Download button
- the React component + usage snippet in copy-to-clipboard boxes
Run:  python scripts/build_handoff.py
(Mirrors the clothing-store deliverable: adflowez-slider/build_handoff.py)
"""
import base64, html, pathlib

HERE = pathlib.Path(__file__).parent          # scripts/
ROOT = HERE.parent                            # repo root
SHOTS = ROOT / "screenshots"

def data_uri(name):
    b = (SHOTS / name).read_bytes()
    mime = "image/jpeg" if name.endswith((".jpg", ".jpeg")) else "image/png"
    return f"data:{mime};base64," + base64.b64encode(b).decode("ascii")

imgs = {
    "bd": data_uri("before-desktop.jpg"),
    "ad": data_uri("after-desktop.jpg"),
    "bm": data_uri("before-mobile.jpg"),
    "am": data_uri("after-mobile.jpg"),
}

component_src = (ROOT / "components" / "BeforeAfter.jsx").read_text(encoding="utf-8")

usage_snippet = '''import BeforeAfter from '@/components/BeforeAfter';

// ...inside the Mosswell skincare demo-store card, replace the placeholder
// <div className="relative w-full aspect-video ...">...</div> with:

<BeforeAfter
  beforeSrc="/demos/mosswell-before.jpg"
  afterSrc="/demos/mosswell-after.jpg"
  beforeSrcMobile="/demos/mosswell-before-mobile.jpg"
  afterSrcMobile="/demos/mosswell-after-mobile.jpg"
  beforeAlt="Mosswell — original product page"
  afterAlt="Mosswell — AdflowEZ rebuild"
/>'''

comp_esc = html.escape(component_src)
use_esc = html.escape(usage_snippet)

HTML = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Mosswell — Before/After slider (everything in one file)</title>
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
  ol.steps {{ margin:0; padding-left:20px; font-size:14px; line-height:1.8; }}
  ol.steps code {{ background:#f1f5f9; padding:1px 6px; border-radius:4px; font-size:12.5px; }}

  /* ---------- the live slider (shows the FULL product view, no cropping) ---------- */
  .card {{ border-radius:12px; border:1px solid #e2e8f0; overflow:hidden; max-width:560px; margin:0 auto; }}
  .ba {{ position:relative; width:100%; user-select:none; -webkit-user-select:none; cursor:default; background:#fff; }}
  .ba__before {{ display:block; }}
  .ba__before img {{ display:block; width:100%; height:auto; pointer-events:none; }}
  /* AFTER wipes in from the LEFT: handle far-left = all Before, far-right = all After. */
  .ba__after {{ position:absolute; inset:0; clip-path:inset(0 50% 0 0); }}
  .ba__after img {{ display:block; width:100%; height:auto; pointer-events:none; }}
  .ba__line {{ position:absolute; top:0; bottom:0; width:2px; background:#fff;
               box-shadow:0 0 4px rgba(0,0,0,.3); left:50%; pointer-events:none; transform:translateX(-50%); }}
  .ba__handle {{ position:absolute; top:50%; left:50%; transform:translate(-50%,-50%);
                 width:50px; height:50px; border-radius:9999px; background:#fff; border:2.5px solid var(--blue);
                 box-shadow:0 6px 16px rgba(0,0,0,.28); display:flex; align-items:center; justify-content:center; cursor:grab; touch-action:none; }}
  .ba__handle:active {{ cursor:grabbing; }}
  .ba__handle:focus {{ outline:2px solid var(--blue); outline-offset:2px; }}
  .ba__handle::before {{ content:''; position:absolute; inset:-7px; border-radius:9999px; border:2px solid rgba(59,124,244,.55); animation:tolPulse 1.8s ease-out infinite; pointer-events:none; }}
  @keyframes tolPulse {{ 0%{{transform:scale(.9);opacity:.7}} 70%{{transform:scale(1.3);opacity:0}} 100%{{opacity:0}} }}
  /* handle glyph: left chevron + hand + right chevron (signals drag left/right) */
  .hrow {{ display:flex; align-items:center; gap:3px; }}
  .hrow svg {{ display:block; fill:none; stroke:var(--blue); stroke-width:2; stroke-linecap:round; stroke-linejoin:round; }}
  .hhand {{ width:13px; height:13px; }}
  .hchev {{ width:7px; height:12px; }}
  .ba__tag {{ position:absolute; top:12px; font-size:12px; font-weight:600; padding:4px 10px; border-radius:6px; color:#fff; pointer-events:none; }}
  .ba__tag--before {{ left:12px; background:rgba(0,0,0,.5); }}
  .ba__tag--after  {{ right:12px; background:var(--blue); }}
  .ba__hint {{ position:absolute; bottom:12px; left:50%; transform:translateX(-50%);
               font-size:12px; color:#475569; background:rgba(255,255,255,.9); backdrop-filter:blur(4px);
               padding:6px 12px; border-radius:9999px; border:1px solid #e2e8f0; pointer-events:none; white-space:nowrap; }}
  .ba__expand {{ position:absolute; bottom:12px; right:12px; width:36px; height:36px; border-radius:8px;
                 background:rgba(255,255,255,.9); border:1px solid #e2e8f0; box-shadow:0 2px 6px rgba(0,0,0,.15);
                 display:flex; align-items:center; justify-content:center; cursor:pointer; }}
  .ba__expand:hover {{ background:#fff; }}
  .modal {{ position:fixed; inset:0; background:rgba(0,0,0,.8); display:none; align-items:center; justify-content:center; padding:24px; z-index:1000; }}
  .modal.open {{ display:flex; }}
  .modal__content {{ position:relative; width:100%; max-width:1200px; }}
  .modal__close {{ position:absolute; top:-40px; right:0; background:none; border:none; color:#fff; font-size:14px;
                   font-weight:600; cursor:pointer; display:flex; align-items:center; gap:6px; }}
  .card2 {{ border-radius:12px; overflow:auto; max-height:88vh; box-shadow:0 20px 60px rgba(0,0,0,.5); }}
  /* DESKTOP expand: scale the whole comparison to fit the screen height — no scrolling.
     (Mobile keeps the scroll-in-frame behaviour above, untouched.) */
  @media(min-width:640px){{
    .modal__content {{ width:auto; max-width:96vw; }}
    .card2 {{ overflow:hidden; max-height:none; width:max-content; margin:0 auto; }}
    .card2 .ba {{ display:inline-block; width:auto; }}
    .card2 .ba__before img {{ width:auto; height:auto; max-height:90vh; max-width:96vw; }}
  }}
  /* MOBILE expand: full-screen, edge-to-edge — the in-page card already fills
     most of the width, so this is the largest a phone can show the comparison. */
  @media(max-width:639px){{
    .modal {{ padding:0; }}
    .modal__content {{ width:100vw; max-width:100vw; }}
    .card2 {{ overflow:hidden; max-height:100vh; border-radius:0; width:100vw; }}
    .card2 .ba__before img {{ width:100vw; height:auto; }}
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
      <div class="ba" id="ba">
        <picture class="ba__before">
          <img src="{imgs['bd']}" alt="Mosswell original product page">
        </picture>
        <div class="ba__after" id="baAfter">
          <picture>
            <img src="{imgs['ad']}" alt="Mosswell AdflowEZ rebuild">
          </picture>
        </div>
        <div class="ba__line" id="baLine"></div>
        <div class="ba__handle" id="baHandle" role="slider" tabindex="0"
             aria-label="Drag to compare" aria-valuemin="0" aria-valuemax="100" aria-valuenow="50">
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
        <div class="ba__tag ba__tag--before">Before</div>
        <div class="ba__tag ba__tag--after">After</div>
      </div>
    </div>
    <div style="text-align:center;margin-top:12px">
      <button class="btn" id="baExpand" aria-label="Open a larger view"
              style="display:inline-flex;align-items:center;gap:8px;background:#fffdf8;color:#0f172a;border:1px solid #e2e8f0">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 3H3v5M16 3h5v5M3 16v5h5M21 16v5h-5"/></svg>
        View larger
      </button>
    </div>
    <p class="resizehint">Drag the blue circle to compare (only the circle moves it). Narrow the window to see the mobile layout.</p>
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
    <p class="note" style="margin-top:0">Put all four in your project's <code>public/demos/</code> folder. Desktop = 16:9 product page, Mobile = phone product page.</p>
    <div class="grid">
      <div class="dl"><img src="{imgs['bd']}" alt=""><div class="lbl">Before · desktop (2x)</div><a class="btn" download="mosswell-before.jpg" href="{imgs['bd']}">Download</a></div>
      <div class="dl"><img src="{imgs['ad']}" alt=""><div class="lbl">After · desktop (2x)</div><a class="btn" download="mosswell-after.jpg" href="{imgs['ad']}">Download</a></div>
      <div class="dl"><img src="{imgs['bm']}" alt=""><div class="lbl">Before · mobile (2x)</div><a class="btn" download="mosswell-before-mobile.jpg" href="{imgs['bm']}">Download</a></div>
      <div class="dl"><img src="{imgs['am']}" alt=""><div class="lbl">After · mobile (2x)</div><a class="btn" download="mosswell-after-mobile.jpg" href="{imgs['am']}">Download</a></div>
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
// Handle-ONLY drag: the listeners live on the circle, not the image.
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
}}
wire(document.getElementById('ba'));

// Expand -> clone the slider into a larger popup.
var modal=document.getElementById('modal'), modalBody=document.getElementById('modalBody');
var lastTrigger=null;
function openModal(){{
  lastTrigger=document.activeElement;
  var clone=document.getElementById('ba').cloneNode(true);
  clone.removeAttribute('id');
  var ex=clone.querySelector('.ba__expand'); if(ex) ex.remove();
  clone.querySelector('.ba__after').style.clipPath='inset(0 50% 0 0)';
  clone.querySelector('.ba__line').style.left='50%';
  clone.querySelector('.ba__handle').style.left='50%';
  clone.querySelector('.ba__handle').setAttribute('aria-valuenow','50');
  modalBody.innerHTML=''; modalBody.appendChild(clone); wire(clone);
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

out = ROOT / "mosswell-slider-handoff.html"
out.write_text(HTML, encoding="utf-8")
print("wrote", out, "(", round(len(HTML) / 1024), "KB )")
