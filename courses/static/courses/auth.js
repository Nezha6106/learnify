(function () {
  'use strict';

  function syncTerminalValues(root) {
    const fields = root.querySelectorAll('.terminal-field');
    fields.forEach((field) => {
      const input = field.querySelector('input, select');
      if (!input) return;

      function update() {
        field.classList.toggle('has-value', Boolean(input.value));
      }

      update();
      input.addEventListener('input', update);
      input.addEventListener('change', update);
    });
  }

  function initPasswordMeter(root) {
    const password = root.querySelector('#id_password1');
    const confirm = root.querySelector('#id_password2');
    const fill = root.querySelector('#password-fill');
    const status = root.querySelector('#password-status');
    const percent = root.querySelector('#password-percent');
    const matchStatus = root.querySelector('#password-match-status');

    if (!password || !fill || !status || !percent) return;

    function scorePassword(value) {
      let score = 0;
      if (value.length > 0) score += 8;
      if (value.length >= 8) score += 24;
      if (value.length >= 12) score += 12;
      if (/[a-z]/.test(value)) score += 12;
      if (/[A-Z]/.test(value)) score += 16;
      if (/[0-9]/.test(value)) score += 14;
      if (/[^A-Za-z0-9]/.test(value)) score += 14;
      return Math.min(score, 100);
    }

    function setMeter() {
      const score = scorePassword(password.value);
      fill.className = 'password-meter-fill';
      fill.style.width = score + '%';
      percent.textContent = score + '%';
      fill.style.background = '';
      fill.style.boxShadow = '';

      status.className = '';
      if (score === 0) {
        status.textContent = 'STRENGTH: VOID';
        fill.style.background = 'transparent';
        fill.style.boxShadow = 'none';
      } else if (score < 45) {
        status.textContent = 'STRENGTH: VULNERABLE';
        status.classList.add('strength-low');
        fill.classList.add('strength-low');
      } else if (score < 82) {
        status.textContent = 'STRENGTH: CHARGING';
        status.classList.add('strength-medium');
        fill.classList.add('strength-medium');
      } else {
        status.textContent = 'STRENGTH: SECURE';
        status.classList.add('strength-high');
        fill.classList.add('strength-high');
      }
    }

    function setMatchStatus() {
      if (!confirm || !matchStatus) return;

      matchStatus.classList.remove('is-valid');
      if (!confirm.value) {
        matchStatus.textContent = '';
        confirm.setCustomValidity('');
        return;
      }

      if (confirm.value === password.value) {
        matchStatus.textContent = '[OK] KEYS_SYNCHRONIZED';
        matchStatus.classList.add('is-valid');
        confirm.setCustomValidity('');
      } else {
        matchStatus.textContent = '[WARN] KEY_MISMATCH';
        confirm.setCustomValidity('Passwords do not match.');
      }
    }

    password.addEventListener('input', function () {
      setMeter();
      setMatchStatus();
    });

    if (confirm) {
      confirm.addEventListener('input', setMatchStatus);
    }

    setMeter();
    setMatchStatus();
  }

  function initStepForm(root) {
    const form = root.querySelector('.auth-step-form');
    if (!form) return;

    const steps = Array.from(form.querySelectorAll('.auth-step'));
    const nodes = Array.from(form.querySelectorAll('.auth-progress-node'));
    const prev = form.querySelector('[data-step-prev]');
    const next = form.querySelector('[data-step-next]');
    const submit = form.querySelector('[data-step-submit]');
    let index = 0;

    function render() {
      steps.forEach((step, stepIndex) => {
        step.classList.toggle('active', stepIndex === index);
      });

      nodes.forEach((node, nodeIndex) => {
        node.classList.toggle('active', nodeIndex === index);
        node.classList.toggle('complete', nodeIndex < index);
      });

      if (prev) prev.hidden = index === 0;
      if (next) next.hidden = index === steps.length - 1;
      if (submit) submit.hidden = index !== steps.length - 1;
    }

    function currentFields() {
      return Array.from(steps[index].querySelectorAll('input, select, textarea'));
    }

    function canAdvance() {
      return currentFields().every((field) => {
        if (field.checkValidity()) return true;
        field.reportValidity();
        return false;
      });
    }

    if (next) {
      next.addEventListener('click', function () {
        if (!canAdvance()) return;
        index = Math.min(index + 1, steps.length - 1);
        render();
      });
    }

    if (prev) {
      prev.addEventListener('click', function () {
        index = Math.max(index - 1, 0);
        render();
      });
    }

    form.addEventListener('submit', function (event) {
      if (canAdvance()) return;
      event.preventDefault();
    });

    render();
  }

  document.addEventListener('DOMContentLoaded', function () {
    syncTerminalValues(document);
    initPasswordMeter(document);
    initStepForm(document);
  });
})();
