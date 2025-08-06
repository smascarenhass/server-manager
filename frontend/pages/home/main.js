document.getElementById("menu-toggle").addEventListener("click", function() {
    const navbar = document.getElementById("navbar-vertical");
    const main = document.querySelector("main");
    const header = document.querySelector("header");
    const menuToggle = this;
    
    navbar.classList.toggle("show");
    main.classList.toggle("shifted");
    header.classList.toggle("shifted");
    menuToggle.classList.toggle("active");
    
    // Alternar o texto do botão
    if (menuToggle.classList.contains("active")) {
        menuToggle.textContent = "✕";
    } else {
        menuToggle.textContent = "☰";
    }
});