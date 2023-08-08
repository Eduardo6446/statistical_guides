// declaramos variables para el icono del menu y el navbar

let menu = document.querySelector('#menu-icon');
let nav = document.querySelector('.navlist');

// permite cada vez que se ejecute cambiar de estado la visibilidad del elemento HTML

menu.onclick = () => {
    menu.classList.toggle('bx-x');
    nav.classList.toggle('open');
};

const sr = ScrollReveal({
    distance: '65px',
    duration: 2600,
    delay: 450,
    reset: true
});

sr.reveal('.hero-text',{delay:200, origin:'top'});
sr.reveal('.hero-img',{delay:450, origin:'top'});
sr.reveal('.icons',{delay:500, origin:'left'});