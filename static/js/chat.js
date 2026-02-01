// static/js/chat.js

let chatIntervalo = null; 

function atualizarChat() {
    fetch('/api/chat')
    .then(response => response.json())
    .then(listaMensagens => {
        const divLista = document.getElementById('mensagens-lista');
        const chatAbertoId = document.getElementById('destinatario_id').value;
        const chatEstaVisivel = document.getElementById('janela-chat').style.display === 'block';
        divLista.innerHTML = ""; 
        let temNovaMensagem = false;

        listaMensagens.reverse().forEach(msg => {
            let mostrar = false;
            if (chatAbertoId === "" && msg.tipo === 'global') mostrar = true;
            else if (msg.tipo === 'privado') {
                 if ((msg.remetente_id == MEU_ID && msg.destinatario_id == chatAbertoId) ||
                     (msg.remetente_id == chatAbertoId && msg.destinatario_id == MEU_ID)) {
                     mostrar = true;
                 }
            }
            if (mostrar) {
                const p = document.createElement('p');
                p.style.margin = "5px 0"; p.style.padding = "8px"; p.style.borderRadius = "8px"; p.style.fontSize = "13px"; p.style.maxWidth = "85%"; p.style.wordWrap = "break-word";
                if (msg.remetente_id == MEU_ID) {
                    p.style.background = "#dcedc8"; p.style.textAlign = "right"; p.style.marginLeft = "auto";
                    p.innerHTML = `<span style="color: #333;">${msg.texto}</span>`;
                } else {
                    p.style.background = "#fff"; p.style.textAlign = "left"; p.style.marginRight = "auto"; p.style.border = "1px solid #eee";
                    p.innerHTML = `<strong style="color: #2e7d32; font-size:11px;">${msg.nome}</strong><br>${msg.texto}`;
                    temNovaMensagem = true;
                }
                divLista.appendChild(p);
            }
        });
        divLista.scrollTop = divLista.scrollHeight;

        if (temNovaMensagem && !chatEstaVisivel) {
            let btn = document.getElementById('btn-social-alerta');
            if (btn) {
                btn.style.background = "#FF5722";
                btn.innerText = "NOVA MENSAGEM! 🔔";
            }
        }
    });
}

function resetarAlerta() {
    let btn = document.getElementById('btn-social-alerta');
    if (btn) {
        btn.style.background = "#673AB7";
        btn.innerText = "SOCIAL & CHAT 💬";
    }
}

function abrirChat(id, nome) {
    resetarAlerta();
    document.getElementById('janela-chat').style.display = 'block';
    document.getElementById('chat-titulo').innerText = "Chat com " + nome;
    document.getElementById('destinatario_id').value = id;
    if (chatIntervalo) clearInterval(chatIntervalo);
    chatIntervalo = setInterval(atualizarChat, 2000);
    atualizarChat();
}

function abrirChatGlobal() {
    resetarAlerta();
    fecharModal('modal-social');
    document.getElementById('janela-chat').style.display = 'block';
    document.getElementById('chat-titulo').innerText = "Chat Global 🌎";
    document.getElementById('destinatario_id').value = ""; 
    if (chatIntervalo) clearInterval(chatIntervalo);
    chatIntervalo = setInterval(atualizarChat, 2000);
    atualizarChat();
}

function enviarMensagem(e) {
    e.preventDefault();
    const texto = document.getElementById('msg-input').value;
    const dest = document.getElementById('destinatario_id').value;
    if (!texto.trim()) return;
    fetch('/api/chat', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ mensagem: texto, destinatario_id: dest ? dest : null, tipo: dest ? 'privado' : 'global' })
    })
    .then(r => r.json()).then(d => {
        if (d.sucesso) { document.getElementById('msg-input').value = ''; atualizarChat(); }
    });
}
