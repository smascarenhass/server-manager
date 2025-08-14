// Função para buscar usuários da API
async function fetchUsers() {
    try {
        const response = await fetch(buildApiUrl(API_CONFIG.ENDPOINTS.USERS));
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const users = await response.json();
        return users;
    } catch (error) {
        console.error('Erro ao buscar usuários:', error);
        throw error;
    }
}

// Função para criar um card de usuário
function createUserCard(user) {
    const card = document.createElement('div');
    card.className = 'user-card';
    
    // Primeira letra do username para o avatar
    const firstLetter = user.username.charAt(0).toUpperCase();
    
    // Status do usuário
    const statusClass = user.has_share ? 'has-share' : 'no-share';
    const statusText = user.has_share ? 'Compartilhamento Ativo' : 'Sem Compartilhamento';
    
    card.innerHTML = `
        <div class="user-header">
            <div class="user-avatar">${firstLetter}</div>
            <div class="user-info">
                <h3>${user.username}</h3>
                <span class="user-status ${statusClass}">${statusText}</span>
            </div>
        </div>
        
        <div class="user-details">
            <p><strong>Nome de usuário:</strong> ${user.username}</p>
            ${user.has_share ? `<p><strong>Caminho do compartilhamento:</strong> ${user.share_path}</p>` : ''}
        </div>
        
        ${user.has_share && user.share_config ? `
            <div class="share-config">
                <h4>Configuração do Compartilhamento</h4>
                ${Object.entries(user.share_config).map(([key, value]) => `
                    <div class="config-item">
                        <span class="config-label">${key}:</span>
                        <span class="config-value">${value}</span>
                    </div>
                `).join('')}
            </div>
        ` : ''}
    `;
    
    return card;
}

// Função para exibir usuários na página
function displayUsers(users) {
    const container = document.getElementById('users-container');
    container.innerHTML = '';
    
    if (users.length === 0) {
        container.innerHTML = '<div class="error">Nenhum usuário encontrado</div>';
        return;
    }
    
    users.forEach(user => {
        const card = createUserCard(user);
        container.appendChild(card);
    });
}

// Função para exibir erro
function displayError(message) {
    const container = document.getElementById('users-container');
    container.innerHTML = `<div class="error">Erro: ${message}</div>`;
}

// Função principal para carregar usuários
async function loadUsers() {
    try {
        const users = await fetchUsers();
        displayUsers(users);
    } catch (error) {
        displayError('Não foi possível carregar os usuários. Verifique se a API está rodando.');
    }
}

// Toggle do menu lateral
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

// Carregar usuários quando a página carregar
document.addEventListener('DOMContentLoaded', loadUsers);


