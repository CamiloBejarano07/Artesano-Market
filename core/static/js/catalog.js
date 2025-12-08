document.addEventListener('DOMContentLoaded', function() {
    // Inicialización del carrusel de categorías
    const carousel = document.querySelector('.carousel');
    const prevButton = document.querySelector('.carousel-nav.prev');
    const nextButton = document.querySelector('.carousel-nav.next');
    
    if (carousel && prevButton && nextButton) {
        const scrollAmount = 200; // Ajusta este valor según el ancho de tus tarjetas

        prevButton.addEventListener('click', () => {
            carousel.scrollBy({
                left: -scrollAmount,
                behavior: 'smooth'
            });
        });

        nextButton.addEventListener('click', () => {
            carousel.scrollBy({
                left: scrollAmount,
                behavior: 'smooth'
            });
        });

        // Detectar cuando el carrusel llega al inicio o al final
        carousel.addEventListener('scroll', () => {
            const isAtStart = carousel.scrollLeft === 0;
            const isAtEnd = carousel.scrollLeft + carousel.clientWidth >= carousel.scrollWidth - 1;

            prevButton.style.opacity = isAtStart ? '0.5' : '1';
            nextButton.style.opacity = isAtEnd ? '0.5' : '1';
        });
    }
    // Inicializar Swiper
    const swiper = new Swiper('.categorias-swiper', {
        slidesPerView: 'auto',
        spaceBetween: 20,
        navigation: {
            nextEl: '.swiper-button-next',
            prevEl: '.swiper-button-prev',
        },
        breakpoints: {
            320: {
                slidesPerView: 2,
            },
            480: {
                slidesPerView: 3,
            },
            768: {
                slidesPerView: 4,
            },
            1024: {
                slidesPerView: 5,
            }
        }
    });

    // Manejo de selección de categorías
    const categoriaPills = document.querySelectorAll('.categoria-pill');
    categoriaPills.forEach(pill => {
        pill.addEventListener('click', function() {
            // Remover clase activa de todos los pills
            categoriaPills.forEach(p => p.classList.remove('active'));
            // Agregar clase activa al pill seleccionado
            this.classList.add('active');
            
            // Aquí puedes agregar la lógica para filtrar productos por categoría
            const categoria = this.dataset.categoria;
            // Implementar filtrado si es necesario
        });
    });
});
