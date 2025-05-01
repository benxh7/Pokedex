(function () {
    let lastScroll = 0;
    const navbar = document.querySelector('.navbar');

    // Media query para pantallas pequeñas.
    const isSmallScreen = () => window.innerWidth <= 768;

    window.addEventListener('scroll', () => {
        if (isSmallScreen()) {
            // Nos aseguramos de que este visible
            navbar.classList.remove('hidden');
            return;
        }

        const currentScroll = window.pageYOffset || document.documentElement.scrollTop;

        // Si estamos al tope, siempre mostramos la navbar
        if (currentScroll <= 0) {
            navbar.classList.remove('hidden');
            return;
        }

        // Cuando scrolleamos hacia abajo ocultamos la navbar
        if (currentScroll > lastScroll) {
            navbar.classList.add('hidden');
        }

        // Cuando scrolleamos hacia arriba mostramos la navbar
        else {
            navbar.classList.remove('hidden');
        }

        lastScroll = currentScroll;
    });
})();

/* Animacion para las categorias de la pagina */
const boxes = document.querySelectorAll('.box');

window.addEventListener('scroll', checkBoxes);
checkBoxes();

function checkBoxes() {
    const triggerBottom = window.innerHeight / 5 * 4;
    boxes.forEach((box, idx) => {
        const boxTop = box.getBoundingClientRect().top;

        if (boxTop < triggerBottom) {
            box.classList.add('show');
        } else {
            box.classList.remove('show');
        }
    });
}