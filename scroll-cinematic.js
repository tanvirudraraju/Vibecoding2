/* Vastra — scroll-cinematic engine
 * Canvas image-sequence scrub: the frame drawn to each sticky <canvas> is
 * chosen by that section's scroll progress. A rAF lerp smooths progress so
 * scrubbing feels inertial without hijacking native scroll.
 * Config lives in SCRUB_SECTIONS at the bottom of index.html.
 */
(function () {
  "use strict";

  var DPR = Math.min(window.devicePixelRatio || 1, 2);
  var LERP = 0.14; // smoothing factor for scrub inertia

  function buildSection(cfg) {
    var section = document.querySelector(cfg.section);
    if (!section) return null; // engine skips missing sections
    var canvas = section.querySelector("canvas");
    var ctx = canvas.getContext("2d");
    var st = {
      cfg: cfg, section: section, canvas: canvas, ctx: ctx,
      frames: new Array(cfg.frameCount), loaded: 0,
      progress: 0, target: 0, drawnFrame: -1, ready: false
    };

    for (var i = 0; i < cfg.frameCount; i++) {
      (function (idx) {
        var img = new Image();
        img.onload = function () {
          st.frames[idx] = img;
          st.loaded++;
          if (idx === 0) { st.ready = true; draw(st, 0); }
          if (st.loaded === cfg.frameCount) section.classList.add("frames-ready");
        };
        img.onerror = function () { st.loaded++; };
        img.src = cfg.framePath(idx);
      })(i);
    }

    window.addEventListener("resize", function () { size(st); draw(st, st.drawnFrame, true); });
    size(st);
    return st;
  }

  function size(st) {
    var w = st.canvas.clientWidth, h = st.canvas.clientHeight;
    st.canvas.width = Math.round(w * DPR);
    st.canvas.height = Math.round(h * DPR);
  }

  function draw(st, frameIdx, force) {
    if (frameIdx < 0) return;
    var img = st.frames[frameIdx] || st.frames[st.drawnFrame >= 0 ? st.drawnFrame : 0];
    if (!img) return;
    if (frameIdx === st.drawnFrame && !force) return;
    st.drawnFrame = frameIdx;

    var cw = st.canvas.width, ch = st.canvas.height;
    var scale = Math.max(cw / img.width, ch / img.height); // cover fit
    var dw = img.width * scale, dh = img.height * scale;
    st.ctx.fillStyle = st.cfg.bg || "#1f120a";
    st.ctx.fillRect(0, 0, cw, ch);
    st.ctx.drawImage(img, (cw - dw) / 2, (ch - dh) / 2, dw, dh);
  }

  function sectionProgress(el) {
    var rect = el.getBoundingClientRect();
    var span = rect.height - window.innerHeight;
    if (span <= 0) return 0;
    return Math.min(1, Math.max(0, -rect.top / span));
  }

  function updateOverlay(section, p) {
    var lines = section.querySelectorAll("[data-in]");
    for (var i = 0; i < lines.length; i++) {
      var el = lines[i];
      var a = parseFloat(el.dataset.in), b = parseFloat(el.dataset.out);
      var fadeSpan = Math.min(0.08, (b - a) / 3);
      var o = 0;
      if (p >= a && p <= b) {
        var fadeIn = a <= 0 ? 1 : (p - a) / fadeSpan;   // first line: visible on load
        var fadeOut = b >= 1 ? 1 : (b - p) / fadeSpan;  // last line: holds to the end
        o = Math.min(fadeIn, fadeOut, 1);
      }
      el.style.opacity = o.toFixed(3);
      el.style.transform = "translateY(" + ((1 - o) * 24).toFixed(1) + "px)";
      el.style.pointerEvents = o > 0.4 ? "" : "none"; // hidden cards must not eat clicks
    }
  }

  // Scroll-reveal for regular content sections
  function initReveals() {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add("revealed"); io.unobserve(e.target); }
      });
    }, { threshold: 0.18 });
    document.querySelectorAll(".reveal").forEach(function (el) { io.observe(el); });
  }

  function start() {
    var states = (window.SCRUB_SECTIONS || []).map(buildSection).filter(Boolean);
    initReveals();

    var nav = document.querySelector(".nav");
    function loop() {
      states.forEach(function (st) {
        st.target = sectionProgress(st.section);
        st.progress += (st.target - st.progress) * LERP;
        if (Math.abs(st.target - st.progress) < 0.0005) st.progress = st.target;
        if (st.ready) {
          var idx = Math.min(st.cfg.frameCount - 1,
            Math.max(0, Math.round(st.progress * (st.cfg.frameCount - 1))));
          draw(st, idx);
        }
        updateOverlay(st.section, st.progress);
      });
      if (nav) nav.classList.toggle("scrolled", window.scrollY > 40);
      requestAnimationFrame(loop);
    }
    requestAnimationFrame(loop);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start);
  } else {
    start();
  }
})();
