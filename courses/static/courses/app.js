const searchInput = document.querySelector("#courseSearch");
const filterButtons = document.querySelectorAll(".filter-button");
const courseCards = document.querySelectorAll(".course-card");
const emptyState = document.querySelector("#emptyState");

let activeFilter = "All";

function updateCourses() {
    const query = searchInput.value.trim().toLowerCase();
    let visibleCount = 0;

    courseCards.forEach((card) => {
        const matchesFilter = activeFilter === "All" || card.dataset.category === activeFilter;
        const matchesSearch = card.dataset.search.toLowerCase().includes(query);
        const isVisible = matchesFilter && matchesSearch;

        card.hidden = !isVisible;
        if (isVisible) {
            visibleCount += 1;
        }
    });

    emptyState.hidden = visibleCount > 0;
}

if (searchInput && emptyState) {
    filterButtons.forEach((button) => {
        button.addEventListener("click", () => {
            activeFilter = button.dataset.filter;
            filterButtons.forEach((item) => item.classList.toggle("active", item === button));
            updateCourses();
        });
    });

    searchInput.addEventListener("input", updateCourses);
}


/* ═══════════════════════════════════════════════════════════════════════
   TYPEWRITER EFFECT — Learnify Hero Section
   Smooth typing animation with blinking cursor, cycling through phrases
   ═══════════════════════════════════════════════════════════════════════ */

(function() {
    // Phrases to cycle through
    const phrases = [
        "Python & Django",
        "Web Development",
        "Data Science",
        "JavaScript",
        "Machine Learning",
        "Full Stack Skills",
        "Your Career"
    ];

    const typewriterElement = document.getElementById('typewriter-text');
    if (!typewriterElement) return; // Only run on pages with the hero section

    let phraseIndex = 0;
    let charIndex = 0;
    let isDeleting = false;
    let isPaused = false;

    const TYPING_SPEED = 90;      // ms per character when typing
    const DELETING_SPEED = 50;    // ms per character when deleting
    const PAUSE_AFTER_TYPE = 2200; // ms to wait after typing a phrase
    const PAUSE_AFTER_DELETE = 500; // ms to wait after deleting

    function type() {
        const currentPhrase = phrases[phraseIndex];

        if (isPaused) return; // Don't modify text while paused

        if (!isDeleting) {
            // Typing phase
            typewriterElement.textContent = currentPhrase.substring(0, charIndex + 1);
            charIndex++;

            if (charIndex === currentPhrase.length) {
                // Finished typing — pause then start deleting
                isPaused = true;
                setTimeout(() => {
                    isPaused = false;
                    isDeleting = true;
                    type();
                }, PAUSE_AFTER_TYPE);
                return;
            }

            setTimeout(type, TYPING_SPEED + (Math.random() * 30 - 15));

        } else {
            // Deleting phase
            typewriterElement.textContent = currentPhrase.substring(0, charIndex - 1);
            charIndex--;

            if (charIndex === 0) {
                // Finished deleting — move to next phrase
                isDeleting = false;
                phraseIndex = (phraseIndex + 1) % phrases.length;

                isPaused = true;
                setTimeout(() => {
                    isPaused = false;
                    type();
                }, PAUSE_AFTER_DELETE);
                return;
            }

            setTimeout(type, DELETING_SPEED);
        }
    }

    // Start the typewriter after a brief delay (let page animations begin first)
    setTimeout(type, 600);
})();


/* ═══════════════════════════════════════════════════════════════════════
   HERO SECTION INTERSECTION OBSERVER
   Re-triggers fade-in animations when hero scrolls into view
   ═══════════════════════════════════════════════════════════════════════ */

(function() {
    const heroSection = document.querySelector('.hero-modern');
    if (!heroSection) return;

    const fadeElements = heroSection.querySelectorAll('.fade-in-up');

    // Optional: Add parallax effect on mouse move (desktop only)
    if (window.matchMedia('(hover: hover) and (pointer: fine)').matches) {
        const orbs = heroSection.querySelectorAll('.hero-orb');

        heroSection.addEventListener('mousemove', (e) => {
            const rect = heroSection.getBoundingClientRect();
            const x = (e.clientX - rect.left) / rect.width - 0.5;
            const y = (e.clientY - rect.top) / rect.height - 0.5;

            orbs.forEach((orb, i) => {
                const speed = (i + 1) * 15;
                orb.style.transform = `translate(${x * speed}px, ${y * speed}px)`;
            });
        });
    }
})();
