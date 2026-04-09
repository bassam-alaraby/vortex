    const hamburger = document.getElementById('hamburger');
    const navLinks = document.querySelector('.nav-links');

    hamburger.addEventListener('click', () => {
        navLinks.classList.toggle('open');
        hamburger.querySelector('i').classList.toggle('ri-menu-line');
        hamburger.querySelector('i').classList.toggle('ri-close-line');
    });