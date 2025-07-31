const form = document.querySelector('.login-form');
const submit = document.getElementById('submit');

const accounts = {
    'username': '123',	
    'password': '123'
};

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
    
    // Limpa os campos de input
    document.getElementById('username').value = '';
    document.getElementById('password').value = '';
    
    if (username === accounts.username && password === accounts.password) {
        // Redireciona para a página home após o login
        window.location.href = '../home/index.html';
       
    } else {
        alert('Usuário ou senha inválidos');
        window.location.reload();
    }
});

form.addEventListener("keypress", (e) => {
    if (e.key === 'Enter') {
        e.preventDefault();
        submit.click();
    }
})