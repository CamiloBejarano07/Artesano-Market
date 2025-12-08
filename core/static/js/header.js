document.addEventListener('DOMContentLoaded', function() {
    var header = document.getElementById('Header');
    if(!header) return;

    function handleHeaderScroll(){
        var scroll = window.scrollY || window.pageYOffset;
        if(scroll > 10){
            header.style.backgroundColor = 'rgba(0, 0, 0, 0.7)';
        } else {
            header.style.backgroundColor = 'transparent';
        }
    }

    // Estado inicial
    handleHeaderScroll();

    // Escuchar scroll con transición suave definida en CSS
    window.addEventListener('scroll', handleHeaderScroll);
});
