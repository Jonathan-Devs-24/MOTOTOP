// web/core/static/core/js/ai_chat.js
document.addEventListener('DOMContentLoaded', () => {
    const toggleBtn = document.getElementById('btnToggleAiChat');
    const closeBtn = document.getElementById('btnCloseAiChat');
    const chatWindow = document.getElementById('aiChatWindow');
    const chatForm = document.getElementById('aiChatForm');
    const chatInput = document.getElementById('aiChatInput');
    const chatMessages = document.getElementById('aiChatMessages');
    const sendBtn = document.getElementById('aiChatSendBtn');

    if (!toggleBtn || !chatWindow || !chatForm) return;

    // Alternar visibilidad al hacer clic en el botón circular
    toggleBtn.addEventListener('click', () => {
        const isHidden = chatWindow.style.display === 'none' || chatWindow.style.display === '';
        if (isHidden) {
            chatWindow.style.display = 'flex';
            chatInput.focus();
            chatMessages.scrollTop = chatMessages.scrollHeight;
        } else {
            chatWindow.style.display = 'none';
        }
    });

    // Cerrar desde la 'X'
    closeBtn.addEventListener('click', () => {
        chatWindow.style.display = 'none';
    });

    // Envío del mensaje
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const prompt = chatInput.value.trim();
        if (!prompt) return;

        // Renderizar mensaje del usuario
        appendMessage(prompt, 'user');
        chatInput.value = '';

        // Indicador de carga
        const loadingDiv = appendMessage('Consultando disponibilidad...', 'bot text-muted fst-italic');
        sendBtn.disabled = true;

        try {
            const csrfToken = getCookie('csrftoken');
            const response = await fetch('/ai-chat/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({ prompt: prompt })
            });

            const data = await response.json();
            loadingDiv.remove();

            if (response.ok && data.respuesta) {
                appendMessage(data.respuesta, 'bot');
            } else {
                appendMessage(data.error || 'Lo siento, no pude obtener respuesta.', 'bot text-danger');
            }
        } catch (err) {
            loadingDiv.remove();
            appendMessage('Error de conexión al consultar el asistente.', 'bot text-danger');
        } finally {
            sendBtn.disabled = false;
            chatInput.focus();
        }
    });

    function appendMessage(text, typeClass) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `ai-msg ai-msg-${typeClass}`;
        msgDiv.textContent = text;
        chatMessages.appendChild(msgDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        return msgDiv;
    }
});

