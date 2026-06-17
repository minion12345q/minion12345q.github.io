// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const targetId = this.getAttribute('href');
        const targetElement = document.querySelector(targetId);
        
        if(targetElement) {
            window.scrollTo({
                top: targetElement.offsetTop - 70, // offset for navbar
                behavior: 'smooth'
            });
        }
    });
});

// Simple reveal animation on scroll
const observeElements = document.querySelectorAll('.skill-card, .project-card, .achievement-card, .section-title');

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = 1;
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, { threshold: 0.1 });

observeElements.forEach(el => {
    el.style.opacity = 0;
    el.style.transform = 'translateY(20px)';
    el.style.transition = 'all 0.6s ease-out';
    observer.observe(el);
});

// Hamburger menu toggle
const hamburger = document.getElementById('hamburger');
const navLinks = document.querySelector('.nav-links');

if (hamburger && navLinks) {
    hamburger.addEventListener('click', () => {
        hamburger.classList.toggle('active');
        navLinks.classList.toggle('active');
    });

    // Close menu when a link is clicked
    navLinks.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', () => {
            hamburger.classList.remove('active');
            navLinks.classList.remove('active');
        });
    });
}

// Back to top button
const backToTop = document.getElementById('backToTop');

if (backToTop) {
    window.addEventListener('scroll', () => {
        if (window.scrollY > 400) {
            backToTop.classList.add('visible');
        } else {
            backToTop.classList.remove('visible');
        }
    });

    backToTop.addEventListener('click', () => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

// Case study specific effect for El Pollo Diablo (interactive motion-based blackout)
document.addEventListener("DOMContentLoaded", () => {
    const hero = document.querySelector('.theme-pollo .case-study-hero');
    const glitchTitle = document.querySelector('.theme-pollo .case-study-hero .glitch');
    
    if (hero && glitchTitle) {
        let motionTimeout;
        const MOTION_DELAY = 150; // Milliseconds of inactivity before restoring normal screen
        
        const turnOnBlackout = () => {
            if (!hero.classList.contains('blackout')) {
                hero.classList.add('blackout');
            }
        };
        
        const turnOffBlackout = () => {
            if (hero.classList.contains('blackout')) {
                hero.classList.remove('blackout');
            }
        };
        
        const handleMouseMove = () => {
            turnOnBlackout();
            
            // Reset the inactivity timeout
            clearTimeout(motionTimeout);
            motionTimeout = setTimeout(() => {
                // If the mouse stops moving, revert to normal screen
                turnOffBlackout();
            }, MOTION_DELAY);
        };
        
        const handleMouseLeave = () => {
            clearTimeout(motionTimeout);
            turnOffBlackout();
        };
        
        // Listeners for mouse activity on the glitch title
        glitchTitle.addEventListener('mousemove', handleMouseMove);
        glitchTitle.addEventListener('mouseleave', handleMouseLeave);
    }
});
