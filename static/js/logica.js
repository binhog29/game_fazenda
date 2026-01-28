// --- VARIÁVEIS GLOBAIS ---
let itemCompraAtual = ''; 

// --- SISTEMA DE ABAS ---
window.onload = function() {
    let lastTab = localStorage.getItem('lastTab') || 'sede';
    ver(lastTab, document.getElementById('tab-' + lastTab));
}

function ver(aba, el) {
    if (!el) return; // Proteção contra erro se o botão não existir
    document.querySelectorAll('.view-section').forEach(v => v.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.getElementById('view-' + aba).classList.add('active');
    el.classList.add('active');
    localStorage.setItem('lastTab', aba);
}

// --- POPUPS E MODAIS ---
function abrirModal(id) { document.getElementById('modal-' + id).style.display = 'flex'; }
function fecharModal(id) { document.getElementById('modal-' + id).style.display = 'none'; }

function showPopup(title, msg, type, callback) {
    document.getElementById('sw-title').innerText = title;
    document.getElementById('sw-text').innerText = msg;
    let actions = document.getElementById('sw-actions');
    
    if (type === 'confirm') {
        actions.innerHTML = `
            <div style="display:flex; gap:10px;">
                <button class="sw-btn" style="background:#ccc; color:#333" onclick="document.getElementById('sw-modal').style.display='none'">Cancelar</button>
                <button class="sw-btn" id="btn-sw-yes">Confirmar</button>
            </div>`;
        document.getElementById('btn-sw-yes').onclick = function() {
            if(callback) callback();
            document.getElementById('sw-modal').style.display = 'none';
        };
    } else {
        actions.innerHTML = `<button class="sw-btn" onclick="document.getElementById('sw-modal').style.display='none'">OK</button>`;
    }
    document.getElementById('sw-modal').style.display = 'flex';
}

// --- FUNÇÕES DA LOJA (Sementes e Insumos) ---
function abrirCompraLoja(item, nome) {
    if (VISITANTE) return;
    itemCompraAtual = item;
    document.getElementById('loja-item-nome').innerText = "Comprar " + nome;
    document.getElementById('loja-qtd').value = 1;
    abrirModal('loja-compra');
}

function confirmarCompraLoja() {
    let qtd = document.getElementById('loja-qtd').value;
    if (qtd < 1) { showPopup("Erro", "Quantidade inválida!", "alert"); return; }

    fetch('/api/loja/comprar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ item: itemCompraAtual, qtd: qtd })
    })
    .then(r => r.json())
    .then(d => {
        if (d.sucesso) {
            showPopup("Sucesso", d.msg, "alert");
            setTimeout(() => location.reload(), 1500);
        } else {
            showPopup("Erro", d.erro, "alert");
        }
    });
}

// --- PASTO E MANEJO ---
function abrirPasto(id) {
    loteAtual = id;
    abrirModal('pasto');
    document.getElementById('buy-form').style.display = 'none';
    
    if (VISITANTE) {
        document.getElementById('p-actions').innerHTML = "<p>Modo Visitante</p>";
        document.getElementById('p-gado-list').innerHTML = "";
        return;
    }

    fetch(`/api/pasto/${id}`)
    .then(r => r.json())
    .then(d => {
        document.getElementById('p-nome').innerText = d.nome;
        let h = "";
        
        // Lógica de botões do pasto
        if (d.status == 'plantado') {
            h += `<div style="background:#e8f5e9; padding:10px; border:1px solid green; border-radius:10px; text-align:center; margin-bottom:10px;">
                    <b>${d.info_plantio}</b>
                  </div>`;
            h += btn('infra', 'gradear', '🚜 Colher/Gradear', CUSTOS.gradear);
        } else if (d.status == 'mato') {
            h += btn('infra', 'limpeza', '🚜 Limpar Mato', CUSTOS.limpeza);
        } else {
            if (d.agua == 'nenhuma') h += btn('infra', 'agua', '🌊 Represa', CUSTOS.agua_represa);
            if (d.cerca == 'nenhuma') h += btn('infra', 'cerca', '🚧 Cerca', CUSTOS.cerca_arame);
            if (d.cocho == 'nenhum') h += btn('infra', 'cocho', '📦 Cocho', CUSTOS.cocho_sal);

            if (d.status == 'limpo') {
                h += btn('infra', 'arar', '🚜 Arar Terra', CUSTOS.arar);
                h += `<button class="btn-small" style="background:#e3f2fd; color:#1565c0; border:1px solid #2196f3; margin-top:5px;" onclick="document.getElementById('buy-form').style.display='block'">🐂 Comprar Gado</button>`;
            } else if (d.status == 'arado') {
                h += `<div style="font-weight:bold; margin-top:5px;">PLANTIO:</div>
                      <div style="display:grid; grid-template-columns:1fr 1fr; gap:5px;">
                        <button class="btn-small" style="background:#ffb74d" onclick="acao('infra','plantar','milho')">🌽 Milho</button>
                        <button class="btn-small" style="background:#81c784" onclick="acao('infra','plantar','soja')">🌿 Soja</button>
                        <button class="btn-small" style="background:#e0e0e0; color:#333;" onclick="acao('infra','plantar','arroz')">🍚 Arroz</button>
                        <button class="btn-small" style="background:#a1887f" onclick="acao('infra','plantar','feijao')">🫘 Feijão</button>
                        <button class="btn-small" style="background:#6d4c41; grid-column:span 2" onclick="acao('infra','plantar','cafe')">☕ Café</button>
                        <button class="btn-small" style="background:#aed581; color:#33691e; grid-column:span 2" onclick="acao('infra','plantar','capim')">🌱 Plantar Capim</button>
                      </div>`;
            }
        }
        
        // Lista de animais
        let g = "";
        if (d.animais) {
            d.animais.forEach(a => {
                            // CÓDIGO NOVO: Verifica se está à venda
            let botaoManejo = '';
            let statusTexto = a.status;

            if (a.onde_esta === 'venda') {
                statusTexto = '<span style="color:orange; font-weight:bold;">À VENDA 💰</span>';
                botaoManejo = '<small>No Mercado</small>';
            } else {
                botaoManejo = `<button class="btn-small" style="width:auto; background:#eee; color:#333;" onclick="manejo('mover_para_curral',${a.id})">🏠</button>`;
            }

            g += `<div class="animal-row">
                    <div class="animal-info">
                        <b>${a.tipo}</b> <small>${a.fase} | ${a.peso}@</small><br>
                        <span style="font-size:10px;">${statusTexto}</span>
                    </div>
                    ${botaoManejo}
                  </div>`;

            });
        }
        document.getElementById('p-actions').innerHTML = h;
        document.getElementById('p-gado-list').innerHTML = g;
    });
}

// Botão auxiliar
function btn(t, s, l, c) { return `<div class="act-btn" onclick="acao('${t}','${s}')"><span>${l}</span> <b>$${c||'??'}</b></div>`; }

// Executar Ação
function acao(t, s, i = null) {
    showPopup('Confirmar', 'Realizar investimento?', 'confirm', () => {
        fetch(`/api/lote/melhoria/${loteAtual}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ acao: t, tipo: s, item: i })
        }).then(r => r.json()).then(d => {
            if (d.sucesso) location.reload();
            else showPopup("Erro", d.erro, "alert");
        });
    });
}

// --- FUNÇÃO CORRIGIDA DE COMPRA DE GADO ---
function confirmarCompraGado() {
    let raca = document.getElementById('b-raca').value;
    let sexo = document.getElementById('b-sexo').value;
    let fase = document.getElementById('b-fase').value;
    let qtd = document.getElementById('b-qtd').value;

    fetch(`/api/lote/melhoria/${loteAtual}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ acao: 'comprar_gado', raca: raca, sexo: sexo, fase: fase, qtd: qtd })
    }).then(r => r.json()).then(d => {
        if (d.sucesso) location.reload();
        else showPopup("Erro", d.erro, "alert");
    });
}

// --- FUNÇÕES GERAIS ---
function abrirCurral() { abrirModal('curral'); }

function verGTA(id, r, s, i, p, o, v) {
    animalAtual = id;
    document.getElementById('gta-raca').innerText = r;
    document.getElementById('gta-sexo').innerText = s;
    document.getElementById('gta-idade').innerText = i;
    document.getElementById('gta-peso').innerText = p;
    document.getElementById('gta-origem').innerText = o;
    document.getElementById('gta-vacina').innerHTML = v ? '<span class="pill-ok">EM DIA</span>' : '<span class="pill-warn">PENDENTE</span>';
    document.getElementById('modal-gta').style.display = 'flex';
}

function venderFrigorifico() {
    showPopup('Vender', 'Confirmar venda?', 'confirm', () => {
        manejo('vender_frigorifico', animalAtual);
    });
}

function manejo(a, id) {
    fetch('/api/manejo', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ acao: a, id: id })
    }).then(r => r.json()).then(d => {
        if (d.sucesso) { showPopup('Sucesso', d.msg, 'alert'); setTimeout(() => location.reload(), 1000); }
        else showPopup('Erro', d.erro, 'alert');
    });
}

function renomearPasto() {
    if (VISITANTE) return;
    let n = prompt("Novo nome do pasto:");
    if (n) fetch(`/api/renomear/pasto/${loteAtual}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nome: n })
    }).then(() => location.reload());
}

function renomearFazenda(id) {
    if (VISITANTE) return;
    let n = prompt("Novo nome da fazenda:");
    if (n) fetch(`/api/renomear/fazenda/${id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nome: n })
    }).then(() => location.reload());
}

function expandir(t) {
    if (VISITANTE) return;
    showPopup("Expandir", `Melhorar ${t}?`, "confirm", () => {
        fetch('/api/expandir_sede', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ tipo: t })
        }).then(r => r.json()).then(d => {
            if (d.sucesso) location.reload(); else showPopup("Erro", d.erro, "alert");
        });
    });
}

function avancarTempo() {
    showPopup("Dormir", "Avançar dia?", "confirm", () => {
        fetch('/api/avancar_tempo', { method: 'POST' }).then(() => location.reload());
    });
}

// --- CHAT ---
function toggleChat() {
    let c = document.getElementById('chat-win');
    c.style.display = c.style.display === 'flex' ? 'none' : 'flex';
    if (c.style.display === 'flex') loadChat();
}

function sendChat() {
    let m = document.getElementById('chat-in').value;
    if (!m) return;
    fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ msg: m })
    }).then(() => {
        document.getElementById('chat-in').value = '';
        loadChat();
    });
}

function loadChat() {
    fetch('/api/chat').then(r => r.json()).then(d => {
        let h = '';
        d.forEach(m => {
            h += `<div style="margin-bottom:5px; background:white; padding:5px; border-radius:5px; box-shadow:0 1px 2px rgba(0,0,0,0.1);">
                    <b style="color:#0288d1">${m.user}:</b> ${m.msg}
                  </div>`;
        });
        document.getElementById('chat-list').innerHTML = h;
    });
}

setInterval(() => {
    if (document.getElementById('chat-win') && document.getElementById('chat-win').style.display === 'flex') loadChat();
}, 3000);

// --- FUNÇÕES DE VENDA (NOVO) ---
function abrirModalVenda() {
    // Fecha o GTA e abre a Venda
    document.getElementById('modal-gta').style.display = 'none';
    document.getElementById('venda-valor').value = '';
    document.getElementById('venda-qtd').value = '1';
    document.getElementById('modal-venda').style.display = 'flex';
}

function confirmarVenda() {
    let valor = document.getElementById('venda-valor').value;
    let qtd = document.getElementById('venda-qtd').value;
    
    if (!valor || valor <= 0) { showPopup("Erro", "Digite um valor válido!", "alert"); return; }
    if (qtd < 1) { showPopup("Erro", "Quantidade mínima é 1", "alert"); return; }

    fetch('/api/mercado/vender', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            id_animal: animalAtual, // Variável global que já guarda o boi clicado
            valor: valor,
            qtd: qtd
        })
    })
    .then(r => r.json())
    .then(d => {
        if (d.sucesso) {
            showPopup("Sucesso", "Anúncio publicado!", "alert");
            setTimeout(() => location.reload(), 1500);
        } else {
            showPopup("Erro", d.erro, "alert");
        }
    });
}

function abrirModal(id) {
    var modal = document.getElementById(id);
    if (modal) {
        modal.style.display = 'flex';
    } else {
        console.error("Não achei o modal com o ID: " + id);
    }
}

function fecharModal(id) {
    const modal = document.getElementById(id);
    if (modal) {
        modal.style.display = 'none';
    }
}

