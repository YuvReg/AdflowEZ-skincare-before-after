(function () {
  const state = {
    mode: window.matchMedia("(max-width: 760px)").matches ? "mobile" : "desktop",
    position: 50,
    lastFocus: null,
  };

  const sources = {
    desktop: {
      before: "screenshots/before-desktop.png",
      after: "screenshots/after-desktop.png",
      label: "Desktop comparison",
    },
    mobile: {
      before: "screenshots/before-mobile.png",
      after: "screenshots/after-mobile.png",
      label: "Mobile comparison",
    },
  };

  const stages = [
    document.querySelector("[data-comparison]"),
    document.querySelector("[data-comparison-modal]"),
  ].filter(Boolean);
  const modeButtons = Array.from(document.querySelectorAll("[data-mode]"));
  const modeLabel = document.querySelector("[data-mode-label]");
  const positionLabel = document.querySelector("[data-position-label]");
  const modal = document.querySelector("[data-modal]");
  const expandButton = document.querySelector("[data-expand]");
  const closeButton = document.querySelector("[data-close]");

  function clamp(value) {
    return Math.max(0, Math.min(100, Math.round(value)));
  }

  function setPosition(value) {
    state.position = clamp(value);
    stages.forEach((stage) => {
      stage.style.setProperty("--position", `${state.position}%`);
      const range = stage.querySelector(".comparison-range");
      if (range) {
        range.value = String(state.position);
        range.setAttribute("aria-valuetext", `${state.position}% reveal`);
      }
    });
    if (positionLabel) {
      positionLabel.textContent = `Slider at ${state.position}%`;
    }
  }

  function setMode(mode) {
    state.mode = mode;
    const selected = sources[state.mode];
    stages.forEach((stage) => {
      stage.classList.toggle("is-mobile", state.mode === "mobile");
      stage.querySelector(".comparison-before").src = selected.before;
      stage.querySelector(".comparison-after").src = selected.after;
    });
    modeButtons.forEach((button) => {
      button.setAttribute("aria-pressed", String(button.dataset.mode === state.mode));
    });
    if (modeLabel) {
      modeLabel.textContent = selected.label;
    }
  }

  function positionFromEvent(stage, event) {
    const rect = stage.getBoundingClientRect();
    return ((event.clientX - rect.left) / rect.width) * 100;
  }

  function bindStage(stage) {
    const range = stage.querySelector(".comparison-range");
    range.addEventListener("input", () => setPosition(Number(range.value)));

    stage.addEventListener("pointerdown", (event) => {
      stage.setPointerCapture(event.pointerId);
      setPosition(positionFromEvent(stage, event));
    });

    stage.addEventListener("pointermove", (event) => {
      if (stage.hasPointerCapture(event.pointerId)) {
        setPosition(positionFromEvent(stage, event));
      }
    });

    stage.addEventListener("pointerup", (event) => {
      if (stage.hasPointerCapture(event.pointerId)) {
        stage.releasePointerCapture(event.pointerId);
      }
    });

    stage.addEventListener("pointercancel", (event) => {
      if (stage.hasPointerCapture(event.pointerId)) {
        stage.releasePointerCapture(event.pointerId);
      }
    });

    range.addEventListener("keydown", (event) => {
      const keys = {
        ArrowLeft: -5,
        ArrowDown: -5,
        ArrowRight: 5,
        ArrowUp: 5,
        PageDown: -10,
        PageUp: 10,
      };
      if (event.key === "Home") {
        event.preventDefault();
        setPosition(0);
      } else if (event.key === "End") {
        event.preventDefault();
        setPosition(100);
      } else if (Object.prototype.hasOwnProperty.call(keys, event.key)) {
        event.preventDefault();
        setPosition(state.position + keys[event.key]);
      }
    });
  }

  function openModal() {
    state.lastFocus = document.activeElement;
    modal.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";
    closeButton.focus();
  }

  function closeModal() {
    modal.setAttribute("aria-hidden", "true");
    document.body.style.overflow = "";
    if (state.lastFocus && typeof state.lastFocus.focus === "function") {
      state.lastFocus.focus();
    }
  }

  function trapFocus(event) {
    if (modal.getAttribute("aria-hidden") === "true" || event.key !== "Tab") {
      return;
    }
    const focusable = Array.from(
      modal.querySelectorAll('button, input, [href], [tabindex]:not([tabindex="-1"])')
    ).filter((element) => !element.disabled);
    const first = focusable[0];
    const last = focusable[focusable.length - 1];
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  }

  stages.forEach(bindStage);
  modeButtons.forEach((button) => {
    button.addEventListener("click", () => setMode(button.dataset.mode));
  });
  expandButton.addEventListener("click", openModal);
  closeButton.addEventListener("click", closeModal);
  modal.addEventListener("click", (event) => {
    if (event.target === modal) {
      closeModal();
    }
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && modal.getAttribute("aria-hidden") === "false") {
      closeModal();
    }
    trapFocus(event);
  });

  setMode(state.mode);
  setPosition(state.position);
})();
