/* ═══════════════════════════════════════════════════════════════
   LEARNIFY LMS — CORE INTERACTIONS
   Terminal typing, Command Palette, Ambient Grid
   ═══════════════════════════════════════════════════════════════ */

(function () {
  'use strict';

  /* ── TERMINAL TYPING EFFECT ────────────────────────────────── */
  function initTypingEffect() {
    const el = document.getElementById('typing-text');
    if (!el) return;

    const fullText = el.getAttribute('data-text') || el.textContent;
    el.textContent = '';
    el.style.visibility = 'visible';

    const cursor = document.createElement('span');
    cursor.className = 'typing-cursor';
    cursor.textContent = '\u2588'; // █
    el.parentNode.appendChild(cursor);

    let i = 0;
    const speed = 32; // ms per character

    function type() {
      if (i < fullText.length) {
        el.textContent += fullText.charAt(i);
        i++;
        setTimeout(type, speed + Math.random() * 20);
      }
    }

    // Small delay before starting
    setTimeout(type, 600);
  }

  /* ── COMMAND PALETTE (Ctrl+K / Cmd+K) ──────────────────────── */
  function initCommandPalette() {
    const overlay = document.getElementById('command-overlay');
    const input = document.getElementById('command-input');
    const body = document.getElementById('command-body');
    if (!overlay || !input) return;

    const items = Array.from(body ? body.querySelectorAll('.command-item') : []);
    let selectedIdx = -1;

    function open() {
      overlay.classList.add('active');
      input.value = '';
      filterItems('');
      selectedIdx = -1;
      setTimeout(() => input.focus(), 50);
    }

    function close() {
      overlay.classList.remove('active');
      input.value = '';
    }

    function filterItems(query) {
      const q = query.toLowerCase().trim();
      items.forEach(item => {
        const text = (item.getAttribute('data-label') || item.textContent).toLowerCase();
        item.style.display = (!q || text.includes(q)) ? '' : 'none';
      });
      selectedIdx = -1;
      clearHighlight();
    }

    function clearHighlight() {
      items.forEach(item => item.classList.remove('selected'));
    }

    function highlight(idx) {
      clearHighlight();
      const visible = items.filter(i => i.style.display !== 'none');
      if (idx >= 0 && idx < visible.length) {
        visible[idx].classList.add('selected');
        visible[idx].scrollIntoView({ block: 'nearest' });
      }
    }

    function navigate(idx) {
      const visible = items.filter(i => i.style.display !== 'none');
      if (idx >= 0 && idx < visible.length) {
        const href = visible[idx].getAttribute('data-href');
        if (href) window.location.href = href;
      }
    }

    // Hotkey listener
    document.addEventListener('keydown', function (e) {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        overlay.classList.contains('active') ? close() : open();
      }
      if (e.key === 'Escape' && overlay.classList.contains('active')) {
        close();
      }
    });

    // Search filtering
    input.addEventListener('input', () => filterItems(input.value));

    // Arrow key navigation & Enter
    input.addEventListener('keydown', function (e) {
      const visible = items.filter(i => i.style.display !== 'none');
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        selectedIdx = Math.min(selectedIdx + 1, visible.length - 1);
        highlight(selectedIdx);
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        selectedIdx = Math.max(selectedIdx - 1, 0);
        highlight(selectedIdx);
      } else if (e.key === 'Enter') {
        e.preventDefault();
        navigate(selectedIdx);
      }
    });

    // Click to navigate
    items.forEach(item => {
      item.addEventListener('click', () => {
        const href = item.getAttribute('data-href');
        if (href) window.location.href = href;
      });
    });

    // Close on overlay background click
    overlay.addEventListener('click', function (e) {
      if (e.target === overlay) close();
    });
  }

  /* ── AMBIENT GRID CANVAS ───────────────────────────────────── */
  function initAmbientGrid() {
    const container = document.getElementById('ambient-grid');
    if (!container) return;

    const canvas = document.createElement('canvas');
    container.appendChild(canvas);
    const ctx = canvas.getContext('2d');

    let w, h;
    const gridSize = 48;
    const dots = [];
    const maxDots = 35;

    function resize() {
      w = canvas.width = window.innerWidth;
      h = canvas.height = window.innerHeight;
    }

    function seedDots() {
      dots.length = 0;
      for (let i = 0; i < maxDots; i++) {
        dots.push({
          x: Math.random() * w,
          y: Math.random() * h,
          vx: (Math.random() - 0.5) * 0.3,
          vy: (Math.random() - 0.5) * 0.3,
          radius: Math.random() * 1.5 + 0.5,
          alpha: Math.random() * 0.4 + 0.1
        });
      }
    }

    function draw() {
      ctx.clearRect(0, 0, w, h);

      // Draw grid
      ctx.strokeStyle = 'rgba(0, 255, 65, 0.04)';
      ctx.lineWidth = 0.5;
      ctx.beginPath();
      for (let x = 0; x < w; x += gridSize) {
        ctx.moveTo(x, 0);
        ctx.lineTo(x, h);
      }
      for (let y = 0; y < h; y += gridSize) {
        ctx.moveTo(0, y);
        ctx.lineTo(w, y);
      }
      ctx.stroke();

      // Draw + move dots
      for (const d of dots) {
        d.x += d.vx;
        d.y += d.vy;
        if (d.x < 0 || d.x > w) d.vx *= -1;
        if (d.y < 0 || d.y > h) d.vy *= -1;

        ctx.beginPath();
        ctx.arc(d.x, d.y, d.radius, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(0, 255, 65, ${d.alpha})`;
        ctx.fill();
      }

      requestAnimationFrame(draw);
    }

    resize();
    seedDots();
    draw();
    window.addEventListener('resize', () => { resize(); seedDots(); });
  }

  /* ── STAGGERED CARD ENTRANCE ───────────────────────────────── */
  function initCardAnimations() {
    const cards = document.querySelectorAll('.course-card, .session-card');
    cards.forEach((card, i) => {
      card.style.opacity = '0';
      card.style.transform = 'translateY(16px)';
      setTimeout(() => {
        card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        card.style.opacity = '1';
        card.style.transform = 'translateY(0)';
      }, 200 + i * 80);
    });
  }

  /* ── BOOT ──────────────────────────────────────────────────── */
  document.addEventListener('DOMContentLoaded', function () {
    initAmbientGrid();
    initTypingEffect();
    initCommandPalette();
    initCardAnimations();
  });
})();
