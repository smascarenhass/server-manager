console.log('teste');

const usernameInput = document.getElementById('username');
const passwordInput = document.getElementById('password');

const submitButton = document.getElementById('submit');

// Função para verificar se o botão deve estar habilitado ou desabilitado
function checkButtonState() {
    const usernameValue = usernameInput.value.trim();
    const passwordValue = passwordInput.value.trim();
    if (usernameValue === '' || passwordValue === '') {
        submitButton.disabled = true;
        submitButton.style.opacity = '0.5';
        submitButton.style.cursor = 'not-allowed';
    } else {
        submitButton.disabled = false;
        submitButton.style.opacity = '1';
        submitButton.style.cursor = 'pointer';
    }
}

// Verificar estado inicial do botão
checkButtonState();

// Adicionar listener para verificar mudanças no campo de usuário
usernameInput.addEventListener('input', checkButtonState);
passwordInput.addEventListener('input', checkButtonState);


const accounts = {
    'username': '123',	
    'password': '123'
};

// Previne o comportamento padrão do formulário e faz o login ao submeter
submitButton.addEventListener("click", (e) => {
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