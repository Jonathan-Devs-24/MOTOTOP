// web/core/static/core/js/home.js
document.addEventListener("DOMContentLoaded", function () {
    const cards = document.querySelectorAll(".card");

    cards.forEach(card => {
        // Aplicamos la transición suave de opacidad, transform y sombra a todas las tarjetas
        card.style.transition = "transform 0.25s ease, box-shadow 0.25s ease, opacity 0.25s ease";

        // Evento cuando el cursor entra a una tarjeta específica
        card.addEventListener("mouseenter", function () {
            // 1. Elevamos la tarjeta actual
            this.style.transform = "translateY(-6px)";
            this.style.boxShadow = "0 10px 20px rgba(0, 0, 0, 0.15)";
            this.style.opacity = "1";

            // 2. Apagamos LEVEMENTE el resto de los productos
            cards.forEach(otherCard => {
                if (otherCard !== this) {
                    otherCard.style.opacity = "0.65"; // Leve atenuado (podés probar 0.7 si querés menos o 0.5 si querés más)
                }
            });
        });

        // Evento cuando el cursor sale de la tarjeta
        card.addEventListener("mouseleave", function () {
            // Restauramos todas las tarjetas a la normalidad
            cards.forEach(c => {
                c.style.transform = "translateY(0px)";
                c.style.boxShadow = "";
                c.style.opacity = "1";
            });
        });
    });
});