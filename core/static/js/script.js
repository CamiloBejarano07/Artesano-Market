//header efecto
var header = document.getElementById('Header')

window.addEventListener('scroll', ()=>{
    var scroll = window.scrollY
    if(scroll>10){
        header.style.backgroundColor = 'rgba(0, 0, 0, 0.7)'
    } else {
        header.style.backgroundColor = 'transparent'
    }
})

// carrusel de imagenes
document.addEventListener("DOMContentLoaded", () => {
    var splide = new Splide('.splide', {
        type   : 'loop',
        perPage: 3,
        perMove: 1,
        autoplay: true,
        interval: 3000,
        breakpoints: {
            768: {
                perPage: 2,
            },
            480: {
                perPage: 1,
            },
        },
    });

    splide.mount();
});
