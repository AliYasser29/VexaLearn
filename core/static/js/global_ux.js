/**
 * VexaLearn Global Interaction Layer
 * Adds subtle reveal animations, skeleton handling, and toast notifications.
 */

document.addEventListener('DOMContentLoaded', () => {
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    function enhanceRevealAnimations() {
        const revealTargets = document.querySelectorAll(
            '.vx-reveal, .ux-card, .card, .course-item, .notif-item, section, .dashboard-shell, .dashboard-hero'
        );

        revealTargets.forEach((node, index) => {
            if (!node.classList.contains('vx-reveal')) {
                node.classList.add('vx-reveal');
            }
            node.style.transitionDelay = `${Math.min(index * 40, 280)}ms`;
        });

        if (prefersReducedMotion || !('IntersectionObserver' in window)) {
            revealTargets.forEach((node) => node.classList.add('is-visible'));
            return;
        }

        const observer = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('is-visible');
                        observer.unobserve(entry.target);
                    }
                });
            },
            { threshold: 0.16, rootMargin: '0px 0px -10% 0px' }
        );

        revealTargets.forEach((node) => observer.observe(node));
    }

    function finalizeSkeletons() {
        const skeletons = document.querySelectorAll('.ux-skeleton');
        if (!skeletons.length) {
            return;
        }

        window.setTimeout(() => {
            skeletons.forEach((el) => {
                el.classList.remove('ux-skeleton');
                el.classList.add('ux-loaded');
            });
        }, 1200);
    }

    function getIconForType(type) {
        switch (type) {
            case 'success':
                return 'circle-check';
            case 'error':
                return 'circle-xmark';
            case 'warning':
                return 'triangle-exclamation';
            default:
                return 'circle-info';
        }
    }

    window.showToast = (message, type = 'info') => {
        const container = document.getElementById('ux-toast-container');
        if (!container || !message) {
            return;
        }

        const toast = document.createElement('div');
        toast.className = `ux-toast ux-toast-${type}`;
        toast.innerHTML = `
            <div class="ux-toast-content">
                <i class="fas fa-${getIconForType(type)}" aria-hidden="true"></i>
                <span>${message}</span>
            </div>
        `;

        container.appendChild(toast);

        window.setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateY(8px)';
            window.setTimeout(() => toast.remove(), 220);
        }, 3600);
    };

    enhanceRevealAnimations();
    finalizeSkeletons();
});
