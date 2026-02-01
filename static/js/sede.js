// static/js/sede.js

// --- 1. FUNÇÕES DE ABRIR/FECHAR MODAIS ---
function abrirModal(id) { 
    document.getElementById(id).style.display = "flex"; 
}
function fecharModal(id) { 
    document.getElementById(id).style.display = 'none'; 
}
function fecharSeClicarFora(event, id) { 
    if (event.target.id === id) fecharModal(id); 
}

// --- 2. REABERTURA AUTOMÁTICA (FIM DO TELETRANSPORTE) ---
window.addEventListener('load', function() {
    const modalParaAbrir = localStorage.getItem('reabrirModal');
    if (modalParaAbrir) {
        abrirModal(modalParaAbrir);
        localStorage.removeItem('reabrirModal'); 
    }
});

// --- 3. SISTEMA DE VENDAS ---
function prepararVenda(codigo, nome, estoqueMax) {
    // 1. Preenche os dados no modal de confirmação
    document.getElementById('cod-item-final').value = codigo;
    document.getElementById('titulo-venda-final').innerText = "Vender " + nome;
    document.getElementById('estoque-venda-final').innerText = estoqueMax + " kg";
    
    // 2. Define o preço unitário
    const preco = PRECOS[codigo] || 0;
    document.getElementById('preco-venda-final').innerText = preco.toFixed(2);
    
    // 3. Configura o campo de quantidade
    const input = document.getElementById('input-venda-final');
    input.max = estoqueMax; 
    input.value = 1; 
    
    // 4. Calcula o valor inicial e abre o modal
    calcularTotalFinal(); 
    document.getElementById('modal-venda-final').style.display = 'flex';
}


function calcularTotalFinal() {
    const precoUnitario = parseFloat(document.getElementById('preco-venda-final').innerText);
    let qtd = parseInt(document.getElementById('input-venda-final').value);
    
    if (isNaN(qtd) || qtd < 1) qtd = 0;
    
    const total = (qtd * precoUnitario).toFixed(2);
    document.getElementById('total-venda-final').innerText = total;
}

function fecharVenda() { 
    document.getElementById('modal-venda-final').style.display = 'none'; 
}

function confirmarVendaFinal() {
    const item = document.getElementById('cod-item-final').value;
    const qtd = document.getElementById('input-venda-final').value;
    
    // Lista de insumos para o JS saber para onde enviar
    const listaInsumos = ['sal', 'racao', 'adubo', 'veneno', 'combustivel'];
    
    // Define a rota correta baseada no item
    let rota = '/api/vender_produto'; 
    if (listaInsumos.includes(item)) {
        rota = '/api/vender_insumo';
    }

    fetch(rota, { 
        method: 'POST', 
        headers: {'Content-Type': 'application/json'}, 
        body: JSON.stringify({ item: item, qtd: qtd }) 
    })
    .then(r => r.json())
    .then(d => { 
        if (d.sucesso) {
            fecharVenda(); 
            // O 'true' garante que o modal (Silo ou Armazém) reabra sozinho
            mostrarAviso("Sucesso! 💰", d.msg, true);
        } else { 
            mostrarAviso("Erro 🚫", d.erro); 
        } 
    });
}

// --- 4. AVISOS E RECARREGAMENTO INTELIGENTE (FIM DO FANTASMA) ---
// Versão com o alinhamento corrigido para facilitar sua leitura
function mostrarAviso(titulo, mensagem, recarregar=false) {
    document.getElementById('titulo-aviso').innerText = titulo;
    document.getElementById('texto-aviso').innerText = mensagem;
    document.getElementById('modal-aviso').style.display = 'flex';
    
    document.querySelector('#modal-aviso button').onclick = function() {
        document.getElementById('modal-aviso').style.display = 'none';
        
        if (recarregar) {
            // Verifica qual estava aberto para reabrir após o reload
            if (document.getElementById('modal-silo').style.display === 'flex') {
                localStorage.setItem('reabrirModal', 'modal-silo');
            } 
            else if (document.getElementById('modal-armazem').style.display === 'flex') {
                localStorage.setItem('reabrirModal', 'modal-armazem');
            } 
            else if (document.getElementById('modal-curral').style.display === 'flex') {
                localStorage.setItem('reabrirModal', 'modal-curral');
            }
            
            location.reload();
        }
    };
}

// --- FUNÇÕES PARA VENDA DE INSUMOS (ARMAZÉM) ---

function prepararVendaInsumo(codigo, nome, estoqueMax) {
    // 1. Preenche os dados no modal de confirmação (reutilizamos o mesmo modal do Silo)
    document.getElementById('cod-item-final').value = codigo;
    document.getElementById('titulo-venda-final').innerText = "Vender " + nome;
    document.getElementById('estoque-venda-final').innerText = estoqueMax + " un";
    
    // 2. Tabela de Preços dos Insumos
    const PRECOS_INSUMOS = {
        'sal': 50,
        'racao': 80,
        'adubo': 120,
        'veneno': 150,
        'combustivel': 200,
        'vacina_aftosa': 100,      // Adicionado
        'vacina_brucelose': 120,   // Adicionado
        'medicamento_geral': 60,   // Adicionado
        'suplemento_engorda': 80   // Adicionado
    };
    
    const preco = PRECOS_INSUMOS[codigo] || 0;
    document.getElementById('preco-venda-final').innerText = preco.toFixed(2);
    
    // 3. Configura o campo de quantidade
    const input = document.getElementById('input-venda-final');
    input.max = estoqueMax; 
    input.value = 1; 
    
    // 4. Atualiza o cálculo e abre o modal
    calcularTotalFinal(); 
    document.getElementById('modal-venda-final').style.display = 'flex';

    // 5. IMPORTANTE: Alterar o comando do botão "Confirmar" para usar a rota de insumos
    document.querySelector('#modal-venda-final .btn-confirmar').onclick = function() {
        confirmarVendaInsumo(codigo);
    };
}

function confirmarVendaInsumo(item) {
    const qtd = document.getElementById('input-venda-final').value;
    
    fetch('/api/vender_insumo', { 
        method: 'POST', 
        headers: {'Content-Type': 'application/json'}, 
        body: JSON.stringify({ item: item, qtd: qtd }) 
    })
    .then(r => r.json())
    .then(d => { 
        if (d.sucesso) {
            fecharVenda(); 
            // O 'true' faz o "post-it" para reabrir o Armazém após recarregar
            mostrarAviso("Sucesso! 💰", d.msg, true);
        } else { 
            mostrarAviso("Erro 🚫", d.erro); 
        } 
    });
}
function prepararCompra(codigo, nome, precoUnitario) {
    document.getElementById('cod-item-compra').value = codigo;
    document.getElementById('titulo-compra-final').innerText = "Comprar " + nome;
    document.getElementById('preco-compra-final').innerText = precoUnitario.toFixed(2);
    
    const input = document.getElementById('input-compra-final');
    input.value = 1;
    
    calcularTotalCompra();
    document.getElementById('modal-compra-final').style.display = 'flex';
}

function calcularTotalCompra() {
    const preco = parseFloat(document.getElementById('preco-compra-final').innerText);
    let qtd = parseInt(document.getElementById('input-compra-final').value);
    
    if (isNaN(qtd) || qtd < 1) qtd = 0;
    
    const total = (qtd * preco).toFixed(2);
    document.getElementById('total-compra-final').innerText = total;
}

function confirmarCompraFinal() {
    const item = document.getElementById('cod-item-compra').value;
    const qtd = document.getElementById('input-compra-final').value;

    fetch('/comprar_loja', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ item: item, qtd: qtd })
    })
    .then(r => r.json())
    .then(d => {
        if (d.sucesso) {
            fecharModal('modal-compra-final');
            // O 'true' recarrega a página para atualizar seu dinheiro e estoque
            mostrarAviso("Sucesso! 🛒", d.msg, true);
        } else {
            mostrarAviso("Erro 🚫", d.erro);
        }
    });
}
