(function () {
    let lastScroll = 0;
    const navbar = document.querySelector('.navbar');

    window.addEventListener('scroll', () => {
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