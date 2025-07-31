const form = document.querySelector('.login-form');
const submit = document.getElementById('submit');

// Previne o comportamento padrão do formulário e faz o login ao submeter
submit.addEventListener("click", (e) => {
    e.preventDefault();
    const users = [];
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    users.push(
        {
            'username': username, 
            'password': password 
        }
    );//juntando o usuário e a senha em um array
    console.log(users);
    
    // Limpa os campos de input
    document.getElementById('username').value = '';
    document.getElementById('password').value = '';
});

form.addEventListener("keypress", (e) => {
    if (e.key === 'Enter') {
        e.preventDefault();
        submit.click();
    }
})