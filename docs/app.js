/* =====================================================================
   Godot 4 · 2.5D 8-bit guide — reading UX
   ---------------------------------------------------------------------
   No dependencies, no network. Everything degrades to a plain readable
   document if this file fails to load.

   IMPORTANT: the highlighter only wraps existing characters in <span>.
   It reads textContent and re-emits every character HTML-escaped, so no
   GDScript is ever altered — copy always yields the original source.
   ===================================================================== */
(function () {
  "use strict";

  var $ = function (sel, root) { return (root || document).querySelector(sel); };
  var $$ = function (sel, root) {
    return Array.prototype.slice.call((root || document).querySelectorAll(sel));
  };
  // matchMedia is missing in a few embedded/older webviews — never let a
  // media query take the whole script down.
  var mq = function (q) {
    return !!(window.matchMedia && window.matchMedia(q).matches);
  };

  /* ------------------------------------------------------------- theme */
  var STORE_KEY = "g25d-theme";

  function applyTheme(mode) {
    document.documentElement.setAttribute("data-theme", mode);
    $$("[data-theme-toggle]").forEach(function (btn) {
      btn.setAttribute("aria-pressed", mode === "light" ? "true" : "false");
      var lbl = $(".themebtn__txt", btn);
      if (lbl) lbl.textContent = mode === "light" ? "Tối" : "Sáng";
      btn.setAttribute("aria-label", mode === "light" ? "Chuyển sang nền tối" : "Chuyển sang nền sáng");
    });
  }

  function currentTheme() {
    var set = document.documentElement.getAttribute("data-theme");
    if (set) return set;
    return mq("(prefers-color-scheme: light)") ? "light" : "dark";
  }

  applyTheme(currentTheme());

  $$("[data-theme-toggle]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var next = currentTheme() === "light" ? "dark" : "light";
      applyTheme(next);
      try { localStorage.setItem(STORE_KEY, next); } catch (e) { /* private mode */ }
    });
  });

  /* -------------------------------------------------------- copy button */
  $$(".code").forEach(function (fig) {
    var btn = $(".code__copy", fig);
    var code = $("code", fig);
    if (!btn || !code) return;

    btn.addEventListener("click", function () {
      var text = code.getAttribute("data-raw");
      if (text === null) text = code.textContent;

      var done = function (ok) {
        var txt = $(".code__copy-txt", btn) || btn;
        txt.textContent = ok ? "Đã copy" : "Lỗi";
        btn.classList.toggle("is-done", ok);
        setTimeout(function () {
          txt.textContent = "Copy";
          btn.classList.remove("is-done");
        }, 1600);
      };

      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(function () { done(true); }, function () { fallback(text, done); });
      } else {
        fallback(text, done);
      }
    });
  });

  function fallback(text, done) {
    var ta = document.createElement("textarea");
    ta.value = text;
    ta.setAttribute("readonly", "");
    ta.style.position = "fixed";
    ta.style.top = "-1000px";
    document.body.appendChild(ta);
    ta.select();
    var ok = false;
    try { ok = document.execCommand("copy"); } catch (e) { ok = false; }
    document.body.removeChild(ta);
    done(ok);
  }

  /* --------------------------------------------------- syntax highlight */
  var GD_KEYWORDS = ("func var const enum signal class class_name extends static "
    + "if elif else for while match break continue pass return await "
    + "and or not in is as await yield self super new "
    + "true false null void int float bool String StringName NodePath "
    + "Vector2 Vector2i Vector3 Vector3i Rect2 Transform3D Basis Color "
    + "Array Dictionary PackedStringArray PackedInt32Array Callable Signal "
    + "breakpoint assert preload load print push_error push_warning").split(" ");

  var SH_KEYWORDS = ("if then elif else fi for in do done while case esac function "
    + "return export local echo cd mkdir rm cp mv ls cat set unset source exit").split(" ");

  var RULES = {
    gdscript: [
      ["tk-com", /#[^\n]*/],
      ["tk-str", /"""[\s\S]*?"""|"(?:\\.|[^"\\\n])*"|'(?:\\.|[^'\\\n])*'/],
      ["tk-ann", /@[A-Za-z_]\w*/],
      ["tk-num", /\b(?:0x[0-9a-fA-F_]+|\d[\d_]*(?:\.\d[\d_]*)?(?:e[+-]?\d+)?)\b/],
      ["tk-kw", new RegExp("\\b(?:" + GD_KEYWORDS.join("|") + ")\\b")],
      ["tk-fn", /\b[A-Za-z_]\w*(?=\s*\()/]
    ],
    bash: [
      ["tk-com", /#[^\n]*/],
      ["tk-str", /"(?:\\.|[^"\\])*"|'[^']*'/],
      ["tk-num", /\s(?:--?[A-Za-z][\w-]*)/],
      ["tk-kw", new RegExp("\\b(?:" + SH_KEYWORDS.join("|") + ")\\b")],
      ["tk-fn", /\$\{?\w+\}?/]
    ],
    json: [
      ["tk-fn", /"(?:\\.|[^"\\])*"(?=\s*:)/],
      ["tk-str", /"(?:\\.|[^"\\])*"/],
      ["tk-kw", /\b(?:true|false|null)\b/],
      ["tk-num", /-?\b\d+(?:\.\d+)?(?:e[+-]?\d+)?\b/]
    ],
    gitignore: [
      ["tk-com", /#[^\n]*/]
    ]
  };

  function esc(s) {
    return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }

  function highlight(src, rules) {
    // Single left-to-right pass: at each position, take the earliest match
    // among all rules. Guarantees no token is re-scanned inside another.
    var master = new RegExp(
      rules.map(function (r) { return "(" + r[1].source + ")"; }).join("|"),
      "g"
    );
    var out = "";
    var last = 0;
    var m;
    while ((m = master.exec(src)) !== null) {
      if (m[0] === "") { master.lastIndex++; continue; }
      var which = -1;
      for (var i = 1; i < m.length; i++) {
        if (m[i] !== undefined) { which = i - 1; break; }
      }
      out += esc(src.slice(last, m.index));
      if (which < 0) {
        out += esc(m[0]);
      } else {
        // keep any leading whitespace the rule captured outside the span
        var raw = m[0];
        var lead = raw.match(/^\s*/)[0];
        out += esc(lead) + '<span class="' + rules[which][0] + '">' + esc(raw.slice(lead.length)) + "</span>";
      }
      last = m.index + m[0].length;
    }
    out += esc(src.slice(last));
    return out;
  }

  $$(".code code").forEach(function (code) {
    var lang = (code.className.match(/lang-(\w+)/) || [])[1];
    var rules = RULES[lang === "sh" ? "bash" : lang];
    // stash the pristine source so Copy is never affected by highlighting
    code.setAttribute("data-raw", code.textContent);
    if (!rules) return;
    try {
      var html = highlight(code.textContent, rules);
      // paranoia: markup must not change the visible characters
      var probe = document.createElement("div");
      probe.innerHTML = html;
      if (probe.textContent === code.textContent) code.innerHTML = html;
    } catch (e) { /* leave the plain block alone */ }
  });

  /* ------------------------------------------------------- TOC + drawer */
  var toc = $("#tocPanel");
  var tocToggle = $("#tocToggle");
  var scrim = $("#scrim");

  function closeDrawer() {
    if (!toc) return;
    toc.classList.remove("is-open");
    document.body.classList.remove("is-locked");
    if (scrim) scrim.hidden = true;
    if (tocToggle) tocToggle.setAttribute("aria-expanded", "false");
  }

  function openDrawer() {
    if (!toc) return;
    toc.classList.add("is-open");
    document.body.classList.add("is-locked");
    if (scrim) scrim.hidden = false;
    if (tocToggle) tocToggle.setAttribute("aria-expanded", "true");
  }

  if (tocToggle) {
    tocToggle.addEventListener("click", function () {
      if (toc.classList.contains("is-open")) closeDrawer(); else openDrawer();
    });
  }
  if (scrim) scrim.addEventListener("click", closeDrawer);
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") closeDrawer();
  });
  if (toc) {
    toc.addEventListener("click", function (e) {
      if (e.target.closest("a")) closeDrawer();
    });
  }

  /* ----------------------------------------- scroll-spy + progress + top */
  var links = toc ? $$(".toc__item > a", toc) : [];
  var targets = links
    .map(function (a) {
      var el = document.getElementById(decodeURIComponent(a.hash.slice(1)));
      return el ? { el: el, li: a.parentNode } : null;
    })
    .filter(Boolean);

  var bar = $("#progressBar");
  var toTop = $("#toTop");
  var active = null;
  var queued = false;

  function measure() {
    queued = false;
    var offset = 96;

    if (targets.length) {
      var found = targets[0];
      for (var i = 0; i < targets.length; i++) {
        if (targets[i].el.getBoundingClientRect().top - offset <= 0) found = targets[i];
        else break;
      }
      if (found !== active) {
        if (active) active.li.classList.remove("is-active");
        found.li.classList.add("is-active");
        active = found;
        if (toc && mq("(min-width: 1024px)")) {
          var lb = found.li.getBoundingClientRect();
          var tb = toc.getBoundingClientRect();
          if (lb.top < tb.top || lb.bottom > tb.bottom) {
            toc.scrollTop += lb.top - tb.top - tb.height / 3;
          }
        }
      }
    }

    if (bar) {
      var doc = document.documentElement;
      var max = doc.scrollHeight - doc.clientHeight;
      var pct = max > 0 ? Math.min(1, Math.max(0, window.scrollY / max)) : 0;
      bar.style.width = (pct * 100).toFixed(2) + "%";
    }

    if (toTop) toTop.classList.toggle("is-visible", window.scrollY > 700);
  }

  function onScroll() {
    if (!queued) { queued = true; requestAnimationFrame(measure); }
  }

  window.addEventListener("scroll", onScroll, { passive: true });
  window.addEventListener("resize", onScroll);
  measure();

  if (toTop) {
    toTop.addEventListener("click", function () {
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }
})();
