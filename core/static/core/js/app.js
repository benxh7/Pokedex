const slides = document.querySelectorAll('.slide');
const dots = document.querySelectorAll('.dot');
let currentSlide = 0;
const slideInterval = 15000; // 15 segundos
let autoSlide;

function showSlide(index) {
    // Actualizamos cada slide
    slides.forEach((slide, i) => {
        slide.classList.toggle('active', i === index);
    });
    // Actualizamos los botones (dots)
    dots.forEach((dot, i) => {
        dot.classList.toggle('active', i === index);
    });
    currentSlide = index;

    // Reiniciamos el temporizador del slider
    clearInterval(autoSlide);
    autoSlide = setInterval(nextSlide, slideInterval);
}

function nextSlide() {
    let nextIndex = (currentSlide + 1) % slides.length;
    showSlide(nextIndex);
}

function prevSlide() {
    let prevIndex = (currentSlide - 1 + slides.length) % slides.length;
    showSlide(prevIndex);
}

// Inicializamos el slider y el temporizador automático
showSlide(currentSlide);
autoSlide = setInterval(nextSlide, slideInterval);

// Cambio de slide al hacer clic en los puntos (dots)
dots.forEach(dot => {
    dot.addEventListener('click', () => {
        const index = parseInt(dot.getAttribute('data-index'));
        showSlide(index);
    });
});

// Navegación con flechas
const prevButton = document.querySelector('.prev');
const nextButton = document.querySelector('.next');

prevButton.addEventListener('click', () => {
    prevSlide();
});

nextButton.addEventListener('click', () => {
    nextSlide();
});