// Configuração da API
const API_CONFIG = {
    BASE_URL: 'http://localhost:8000',
    ENDPOINTS: {
        USERS: '/users',
        HEALTH: '/health'
    }
};

// Função para construir URLs completas
function buildApiUrl(endpoint) {
    return `${API_CONFIG.BASE_URL}${endpoint}`;
}

// Exportar configuração
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { API_CONFIG, buildApiUrl };
} 