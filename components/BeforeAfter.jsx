'use client';

/**
 * BeforeAfter — responsive drag-to-compare slider.
 * Matches the Adflowez demo-card look (same classes, #3B7CF4 accent).
 *
 *  • Only the circular HANDLE is draggable (pointer-capture). Clicking the
 *    image does nothing, so on mobile a swipe over the image scrolls the page.
 *  • Responsive: desktop (>=640px) 16:9; mobile (<640px) 4:5 with its own
 *    image set (beforeSrcMobile / afterSrcMobile). Omit the *Mobile props to
 *    fall back to the desktop images.
 *  • Expand button (⤢) opens a large popup with the same slider. Esc / backdrop
 *    / ✕ closes it. Pass expandable={false} to hide the button.
 *
 * Usage (Mosswell skincare before/after):
 *   <BeforeAfter
 *     beforeSrc="/demos/mosswell-before.png"
 *     afterSrc="/demos/mosswell-after.png"
 *     beforeSrcMobile="/demos/mosswell-before-mobile.png"
 *     afterSrcMobile="/demos/mosswell-after-mobile.png"
 *     beforeAlt="Mosswell — original product page"
 *     afterAlt="Mosswell — AdflowEZ rebuild"
 *   />
 *
 * Rename to .tsx for TypeScript (no TS-only syntax).
 */

import { useCallback, useEffect, useRef, useState } from 'react';

function Picture({ desktop, mobile, alt }) {
  return (
    <picture>
      <source media="(min-width: 640px)" srcSet={desktop} />
      <img
        src={mobile || desktop}
        alt={alt}
        draggable={false}
        className="block w-full h-auto"
      />
    </picture>
  );
}

function Slider({
  beforeSrc, afterSrc, beforeSrcMobile, afterSrcMobile,
  beforeAlt = 'Original product page', afterAlt = 'AdflowEZ rebuild', start = 50,
  frameClassName = '', onExpand = null,
}) {
  const [pos, setPos] = useState(start);
  const frameRef = useRef(null);
  const dragging = useRef(false);

  const moveTo = useCallback((clientX) => {
    const el = frameRef.current;
    if (!el) return;
    const r = el.getBoundingClientRect();
    setPos(Math.max(0, Math.min(100, ((clientX - r.left) / r.width) * 100)));
  }, []);

  // Drag handlers live ONLY on the handle.
  const onDown = (e) => { dragging.current = true; e.currentTarget.setPointerCapture?.(e.pointerId); };
  const onMove = (e) => { if (dragging.current) moveTo(e.clientX); };
  const onUp = (e) => { dragging.current = false; e.currentTarget.releasePointerCapture?.(e.pointerId); };
  const onKey = (e) => {
    if (e.key === 'ArrowLeft') setPos((p) => Math.max(0, p - 2));
    else if (e.key === 'ArrowRight') setPos((p) => Math.min(100, p + 2));
    else if (e.key === 'Home') setPos(0);
    else if (e.key === 'End') setPos(100);
  };

  return (
    <div
      ref={frameRef}
      className={`relative w-full overflow-hidden select-none bg-border/30 ${frameClassName}`}
    >
      <style>{`
        @keyframes tolBaPulse{0%{transform:scale(.9);opacity:.7}70%{transform:scale(1.3);opacity:0}100%{opacity:0}}
        .tolBaHandle::before{content:'';position:absolute;inset:-7px;border-radius:9999px;border:2px solid rgba(59,124,244,.55);animation:tolBaPulse 1.8s ease-out infinite;pointer-events:none}
        @media (prefers-reduced-motion: reduce){.tolBaHandle::before{animation:none}}
      `}</style>

      {/* BEFORE underneath */}
      <Picture desktop={beforeSrc} mobile={beforeSrcMobile} alt={beforeAlt} />

      {/* AFTER wipes in from the LEFT: handle far-left = all Before, far-right = all After */}
      <div className="absolute inset-0" style={{ clipPath: `inset(0 ${100 - pos}% 0 0)` }}>
        <Picture desktop={afterSrc} mobile={afterSrcMobile} alt={afterAlt} />
      </div>

      {/* Divider line (visual only) */}
      <div
        className="absolute top-0 bottom-0 w-0.5 bg-white shadow pointer-events-none"
        style={{ left: `${pos}%` }}
      />

      {/* HANDLE — the only draggable element */}
      <div
        role="slider"
        tabIndex={0}
        aria-label="Drag to compare before and after"
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuenow={Math.round(pos)}
        onPointerDown={onDown}
        onPointerMove={onMove}
        onPointerUp={onUp}
        onPointerCancel={onUp}
        onKeyDown={onKey}
        className="tolBaHandle absolute top-1/2 -translate-y-1/2 -translate-x-1/2 w-[50px] h-[50px] rounded-full bg-white shadow-lg flex items-center justify-center cursor-grab active:cursor-grabbing touch-none focus:outline-none focus:ring-2 focus:ring-offset-2"
        style={{ left: `${pos}%`, borderWidth: '2.5px', borderStyle: 'solid', borderColor: '#3B7CF4' }}
      >
        <span className="flex items-center gap-[3px]" style={{ stroke: '#3B7CF4', fill: 'none', strokeWidth: 2, strokeLinecap: 'round', strokeLinejoin: 'round' }}>
          <svg width="7" height="12" viewBox="0 0 10 16"><path d="M8 2 2 8 8 14" /></svg>
          <svg width="13" height="13" viewBox="0 0 24 24">
            <path d="M18 11V6a2 2 0 0 0-2-2v0a2 2 0 0 0-2 2v0" />
            <path d="M14 10V4a2 2 0 0 0-2-2v0a2 2 0 0 0-2 2v2" />
            <path d="M10 10.5V6a2 2 0 0 0-2-2v0a2 2 0 0 0-2 2v8" />
            <path d="M18 8a2 2 0 1 1 4 0v6a8 8 0 0 1-8 8h-2c-2.8 0-4.5-.86-5.99-2.34l-3.6-3.6a2 2 0 0 1 2.83-2.82L7 15" />
          </svg>
          <svg width="7" height="12" viewBox="0 0 10 16"><path d="M2 2 8 8 2 14" /></svg>
        </span>
      </div>

      {/* Corner labels */}
      <div className="absolute top-3 left-3 bg-black/50 text-white text-xs font-semibold px-2.5 py-1 rounded-md pointer-events-none">Before</div>
      <div className="absolute top-3 right-3 text-white text-xs font-semibold px-2.5 py-1 rounded-md pointer-events-none" style={{ background: '#3B7CF4' }}>After</div>

      {/* Expand button */}
      {onExpand && (
        <button
          type="button"
          onClick={onExpand}
          aria-label="Expand"
          className="absolute bottom-3 right-3 w-9 h-9 rounded-lg bg-white/90 backdrop-blur-sm border border-gray-200 shadow flex items-center justify-center hover:bg-white"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#0f172a" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M8 3H3v5M16 3h5v5M3 16v5h5M21 16v5h-5" />
          </svg>
        </button>
      )}
    </div>
  );
}

export default function BeforeAfter(props) {
  const { expandable = true } = props;
  const [open, setOpen] = useState(false);

  useEffect(() => {
    if (!open) return;
    const onEsc = (e) => { if (e.key === 'Escape') setOpen(false); };
    document.addEventListener('keydown', onEsc);
    const prev = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    return () => { document.removeEventListener('keydown', onEsc); document.body.style.overflow = prev; };
  }, [open]);

  const frame = '';   // height comes from the full image (no cropping)

  return (
    <>
      <Slider {...props} frameClassName={frame} onExpand={expandable ? () => setOpen(true) : null} />

      {open && (
        <div
          className="fixed inset-0 z-[1000] bg-black/80 flex items-center justify-center p-4 sm:p-8"
          onClick={() => setOpen(false)}
        >
          <div className="relative w-full max-w-6xl" onClick={(e) => e.stopPropagation()}>
            <button
              type="button"
              onClick={() => setOpen(false)}
              aria-label="Close"
              className="absolute -top-11 right-0 text-white/90 hover:text-white flex items-center gap-1.5 text-sm font-medium"
            >
              Close
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                <path d="M6 6l12 12M18 6L6 18" />
              </svg>
            </button>
            <div className="rounded-xl overflow-hidden shadow-2xl">
              {/* No onExpand here → no expand button inside the popup */}
              <Slider {...props} start={50} frameClassName={frame} />
            </div>
          </div>
        </div>
      )}
    </>
  );
}
