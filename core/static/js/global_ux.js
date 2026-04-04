/**
 * VexaLearn Global UX Logic
 * Handles Skeleton Loaders and Toast Notifications
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Skeleton Loader Management
    const skeletons = document.querySelectorAll('.ux-skeleton');
    if (skeletons.length > 0) {
        // Simulate loading for demonstration (in real app, use fetch events)
        setTimeout(() => {
            skeletons.forEach(el => {
                el.classList.remove('ux-skeleton');
                el.classList.add('ux-loaded');
            });
        }, 1500);
    }

    // 2. Toast Management
    window.showToast = (message, type = 'info') => {
        const container = document.getElementById('toast-container');
        if (!container) return;

        const toast = document.createElement('div');
        toast.className = `ux-toast ux-toast-${type}`;
        toast.innerHTML = `
            <div class="ux-toast-content">
                <i class="fas fa-${getIconForType(type)}"></i>
                <span>${message}</span>
            </div>
        `;

        container.appendChild(toast);

        // Auto-remove after 4 seconds
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateY(10px)';
            setTimeout(() => toast.remove(), 300);
        }, 4000);
    };

    function getIconForType(type) {
        switch (type) {
            case 'success': return 'circle-check';
            case 'error': return 'circle-xmark';
            case 'warning': return 'triangle-exclamation';
            default: return 'circle-info';
        }
    }
});
