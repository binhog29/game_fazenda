from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
import random
import datetime

app = Flask(__name__)
app.secret_key = 'chave_v2_6_mercado_full'

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'fazenda_v2_6.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- DADOS ---
NOMES_FAZENDA = ["Estrela do Norte", "Rio Madeira", "Santa Fé", "Boa Esperança", "Nova Vida", "São João"]
NOMES_SITIO = ["Sítio Recanto", "Sítio Sossego", "Sítio Primavera", "Sítio Beira Rio"]
NOMES_CHACARA = ["Chácara Vovó Ana", "Chácara Bela Vista", "Chácara Paraíso"]

# --- CUSTOS OPERACIONAIS (Adicione ISTO antes de PRECOS_LOJA) ---
CUSTOS = { 
    'limpeza': 500, 'arar': 1200, 'gradear': 800, 'adubacao': 1500, 
    'cerca_arame': 2000, 'cerca_eletrica': 3500, 'cerca_madeira': 5000, 
    'cocho_sal': 600, 'cocho_creep': 1800, 'agua_bebedouro': 2500, 'agua_represa': 12000,
    # Custos de Plantio (Máquina + Mão de obra por lote)
    'plantio_milho': 2500, 'plantio_soja': 3000, 'plantio_arroz': 2800, 
    'plantio_feijao': 2000, 'plantio_algodao': 4000, 'plantio_cana': 3500, 
    'plantio_mandioca': 1500, 'plantio_cafe': 5000, 'plantio_cacau': 6000, 
    'plantio_acai': 4500, 'plantio_cupuacu': 4000, 'plantio_banana': 1800,
    'plantio_abacaxi': 2200, 'plantio_melancia': 1200, 'plantio_pimenta': 3000,
    # Estruturas e Veterinário
    'expandir_celeiro': 5000, 'expandir_silo': 8000, 'expandir_curral': 10000, 
    'vacina': 50, 'inseminacao': 250 
}

# --- CONFIGURAÇÃO DE PREÇOS E ITENS (ATUALIZADO) ---
# --- LISTAS DE PREÇOS (Mapeamento Completo da sua Lista) ---
PRECOS_LOJA = {
    # Insumos (Incluindo Ração e Veneno)
    'sal': 80, 'racao': 120, 'adubo': 150, 'veneno': 200, 'combustivel': 450,
    
    # Grãos e Culturas
    'sem_milho': 200, 'sem_soja': 350, 'sem_arroz': 180, 'sem_feijao': 250,
    'sem_algodao': 400, 'sem_cana': 300, 'sem_mandioca': 150,
    
    # Frutas e Perenes
    'sem_cafe': 500, 'sem_cacau': 600, 'sem_acai': 450, 'sem_cupuacu': 400,
    'sem_banana': 200, 'sem_abacaxi': 250, 'sem_melancia': 120, 'sem_pimenta': 300
}

TABELA_PRECOS = {
    # Pecuária (Gado)
    'nelore': {'filhote': 1200, 'adulto': 3500}, 'angus': {'filhote': 1500, 'adulto': 4000},
    'girolando': {'filhote': 1300, 'adulto': 3800}, 'guzera': {'filhote': 1400, 'adulto': 3900},
    'brahman': {'filhote': 1600, 'adulto': 4200},
    # Pequenos Animais
    'porco': {'filhote': 300, 'adulto': 900}, 'ovelha': {'filhote': 400, 'adulto': 1200},
    'cabra': {'filhote': 350, 'adulto': 1000}, 'cavalo': {'filhote': 2000, 'adulto': 8000},
    # Aves
    'galinha': {'filhote': 20, 'adulto': 50}, 'pato': {'filhote': 25, 'adulto': 60}, 
    'peru': {'filhote': 40, 'adulto': 100},
    # Peixes (Todos da lista)
    'tambaqui': {'filhote': 5, 'adulto': 60}, 'pirarucu': {'filhote': 50, 'adulto': 300},
    'pacu': {'filhote': 4, 'adulto': 50}, 'matrinxa': {'filhote': 6, 'adulto': 70},
    'jaraqui': {'filhote': 3, 'adulto': 40}, 'curimata': {'filhote': 3, 'adulto': 45},
    'surubim': {'filhote': 10, 'adulto': 120}, 'pintado': {'filhote': 12, 'adulto': 130},
    'cachara': {'filhote': 11, 'adulto': 125}, 'tucunare': {'filhote': 8, 'adulto': 90},
    'piau': {'filhote': 4, 'adulto': 40}
}


PRECO_ARROBA = 295.0

# --- MODELOS ---
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(100)); senha_hash = db.Column(db.String(128))
    dinheiro = db.Column(db.Float, default=50000.0)
    dia = db.Column(db.Integer, default=1); mes = db.Column(db.Integer, default=1); ano = db.Column(db.Integer, default=2026)
    hora = db.Column(db.Integer, default=6)
    fazendas = db.relationship('Fazenda', backref='dono', lazy=True)
    transacoes = db.relationship('Transacao', backref='usuario', lazy=True, order_by="desc(Transacao.id)")
    def set_senha(self, s): self.senha_hash = generate_password_hash(s)
    def checar_senha(self, s): return check_password_hash(self.senha_hash, s)
    @property
    def titulo(self): return "👑 Dono do Jogo" if self.nome == "CEO" else ("Iniciante" if self.dinheiro < 100000 else "Fazendeiro")
    @property
    def estacao(self): return "Verão" if self.mes in [12,1,2] else ("Outono" if self.mes in [3,4,5] else ("Inverno" if self.mes in [6,7,8] else "Primavera") )

class ChatMensagem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_nome = db.Column(db.String(50)); mensagem = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class Transacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    descricao = db.Column(db.String(100)); valor = db.Column(db.Float); tipo = db.Column(db.String(20)); data_jogo = db.Column(db.String(20))

class Fazenda(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dono_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    x = db.Column(db.Integer); y = db.Column(db.Integer)
    nome_tipo = db.Column(db.String(50)); nome_personalizado = db.Column(db.String(50))
    tamanho_lotes = db.Column(db.Integer); hectares = db.Column(db.Float)
    preco = db.Column(db.Integer); cor_mapa = db.Column(db.String(20))
    nivel_curral = db.Column(db.Integer, default=1); nivel_celeiro = db.Column(db.Integer, default=1); nivel_silo = db.Column(db.Integer, default=1)
    tem_represa_geral = db.Column(db.Boolean, default=False)
    
        # --- ESTOQUE DE SEMENTES E MUDAS ---
    est_milho = db.Column(db.Integer, default=0); est_soja = db.Column(db.Integer, default=0)
    est_arroz = db.Column(db.Integer, default=0); est_feijao = db.Column(db.Integer, default=0)
    est_algodao = db.Column(db.Integer, default=0); est_cana = db.Column(db.Integer, default=0)
    est_mandioca = db.Column(db.Integer, default=0); est_cafe = db.Column(db.Integer, default=0)
    est_cacau = db.Column(db.Integer, default=0); est_acai = db.Column(db.Integer, default=0)
    est_cupuacu = db.Column(db.Integer, default=0); est_banana = db.Column(db.Integer, default=0)
    est_abacaxi = db.Column(db.Integer, default=0); est_melancia = db.Column(db.Integer, default=0)
    est_pimenta = db.Column(db.Integer, default=0)

    # --- ESTOQUE DE INSUMOS (Aqui estão Veneno e Ração) ---
    est_sal = db.Column(db.Integer, default=0); est_racao = db.Column(db.Integer, default=0)
    est_adubo = db.Column(db.Integer, default=0); est_veneno = db.Column(db.Integer, default=0)
    est_combustivel = db.Column(db.Integer, default=0)

    lotes = db.relationship('Lote', backref='fazenda', lazy=True)
    
    # Adicione estas linhas exatamente assim:
    cap_silo = db.Column(db.Integer, default=500)
    cap_armazem = db.Column(db.Integer, default=200)
    nivel_silo = db.Column(db.Integer, default=1)
    nivel_armazem = db.Column(db.Integer, default=1)

    
class Lote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fazenda_id = db.Column(db.Integer, db.ForeignKey('fazenda.id'))
    posicao = db.Column(db.Integer); nome = db.Column(db.String(50))
    status = db.Column(db.String(20), default="mato") 
    cultivo = db.Column(db.String(20)); meses_cultivo = db.Column(db.Integer, default=0)
    cerca = db.Column(db.String(20), default="nenhuma"); cocho = db.Column(db.String(20), default="nenhum"); agua = db.Column(db.String(20), default="nenhuma") 
    animais = db.relationship('Animal', backref='lote', lazy=True)

class Animal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lote_id = db.Column(db.Integer, db.ForeignKey('lote.id'))
    raca = db.Column(db.String(20)); sexo = db.Column(db.String(10)); fase = db.Column(db.String(20)); peso = db.Column(db.Float)
    idade_meses = db.Column(db.Integer); prenha = db.Column(db.Boolean, default=False)
    onde_esta = db.Column(db.String(20), default="pasto"); vacinado = db.Column(db.Boolean, default=False)
    origem = db.Column(db.String(50), default="Leilão")

# --- NOVO: CLASSE ANÚNCIO (O que faltava) ---
class Anuncio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vendedor_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    animal_id = db.Column(db.Integer, db.ForeignKey('animal.id'))
    valor = db.Column(db.Float)
    data = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    # Relacionamentos
    vendedor = db.relationship('Usuario', backref='anuncios')
    animal = db.relationship('Animal', backref='anuncio', uselist=False)

def registrar_transacao(u, d, v, t): db.session.add(Transacao(usuario_id=u.id, descricao=d, valor=v, tipo=t, data_jogo=f"{u.dia}/{u.mes}/{u.ano}"))

def criar_mundo():
    db.create_all()
    if Fazenda.query.count() == 0:
        tipos = [{'n':'Chácara', 's':2, 'h':5, 'p':5000, 'l':NOMES_CHACARA}, {'n':'Sítio', 's':4, 'h':20, 'p':25000, 'l':NOMES_SITIO}, {'n':'Fazenda', 's':9, 'h':100, 'p':100000, 'l':NOMES_FAZENDA}]
        for x in range(8):
            for y in range(8):
                t = random.choices(tipos, weights=[40, 40, 20], k=1)[0]
                db.session.add(Fazenda(x=x, y=y, nome_tipo=t['n'], nome_personalizado=random.choice(t['l'])+f" {x}{y}", tamanho_lotes=t['s'], hectares=t['h'], preco=t['p']))
        db.session.commit()

# --- ROTAS ---
@app.route('/')
def index():
    if 'user_id' not in session: return redirect('/login')
    return render_template('mapa_global.html', user=db.session.get(Usuario, session['user_id']))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        acao = request.form.get('acao'); nome = request.form.get('nome'); senha = request.form.get('senha')
        if acao == 'registro':
            if Usuario.query.filter_by(nome=nome).first(): return render_template('login.html', msg="Existe!")
            u = Usuario(nome=nome, email=request.form.get('email'), dinheiro=100000000.0 if nome == "CEO" else 50000.0); u.set_senha(senha)
            db.session.add(u); db.session.commit(); registrar_transacao(u, "Início", u.dinheiro, "entrada"); session['user_id'] = u.id; return redirect('/')
        elif acao == 'login':
            u = Usuario.query.filter_by(nome=nome).first()
            if u and u.checar_senha(senha): session['user_id'] = u.id; return redirect('/')
    return render_template('login.html')

@app.route('/logout')
def logout(): session.pop('user_id', None); return redirect('/login')

@app.route('/perfil')
def perfil(): return render_template('perfil.html', user=db.session.get(Usuario, session['user_id']))

@app.route('/financeiro')
def financeiro():
    if 'user_id' not in session: return redirect('/login')
    u = db.session.get(Usuario, session['user_id'])
    e = sum(t.valor for t in u.transacoes if t.valor > 0); s = sum(t.valor for t in u.transacoes if t.valor < 0)
    return render_template('financeiro.html', user=u, entradas=e, saidas=s, saldo=u.dinheiro)

@app.route('/api/mapa_global')
def get_mapa(): return jsonify([{'id':f.id, 'nome':f.nome_personalizado, 'tipo':f.nome_tipo, 'x':f.x, 'y':f.y, 'preco':f.preco, 'dono':f.dono.nome if f.dono else None, 'e_minha':f.dono_id==session.get('user_id'), 'hec':f.hectares} for f in Fazenda.query.all()])

@app.route('/api/comprar_fazenda/<int:fid>', methods=['POST'])
def comprar(fid):
    u = db.session.get(Usuario, session['user_id']); f = db.session.get(Fazenda, fid)
    if u.dinheiro >= f.preco:
        u.dinheiro -= f.preco; f.dono_id = u.id
        for i in range(f.tamanho_lotes): db.session.add(Lote(fazenda_id=f.id, posicao=i, nome=f"Pasto {i+1}"))
        db.session.commit(); return jsonify({'sucesso':True})
    return jsonify({'erro':'Sem saldo'})

@app.route('/fazenda/<int:id>')
def ver_fazenda(id):
    f = db.session.get(Fazenda, id)
    user_id = session.get('user_id')
    user = db.session.get(Usuario, user_id) if user_id else None
    
    # Busca animais que estão no curral desta fazenda
    gado_curral = Animal.query.join(Lote).filter(Lote.fazenda_id == id, Animal.onde_esta == 'curral').all()
    
    # CORREÇÃO: Usar dono_id em vez de usuario_id
    visitante = True
    if user and f.dono_id == user.id:
        visitante = False

    return render_template('gestao_fazenda.html', 
                           fazenda=f, user=user, visitante=visitante, 
                           custos=CUSTOS, gado_curral=gado_curral)
@app.route('/api/pasto/<int:lid>')
def get_pasto(lid):
    l = db.session.get(Lote, lid); animais = []
    for a in l.animais:
        if a.onde_esta == 'pasto':
            animais.append({'id':a.id, 'tipo':f"{a.raca}", 'fase': a.fase, 'sexo': a.sexo, 'idade': a.idade_meses, 'peso':a.peso, 'origem': a.origem, 'status': "Prenha" if a.prenha else ("Vacinado" if a.vacinado else "PENDENTE")})
    info_plantio = f"{l.cultivo.capitalize()} (Mês {l.meses_cultivo})" if l.status == 'plantado' else ""
    return jsonify({'nome':l.nome, 'status':l.status, 'cultivo':l.cultivo, 'info_plantio': info_plantio, 'cerca':l.cerca, 'cocho':l.cocho, 'agua':l.agua, 'animais':animais})

# --- ROTA DE COMPRA ATUALIZADA (Substitui a antiga /api/loja/comprar) ---
@app.route('/comprar_loja', methods=['POST'])
def comprar_loja():
    # Verifica se está logado
    if 'user_id' not in session:
        return jsonify({'sucesso': False, 'mensagem': 'Não logado'})
    
    # Pega dados do banco
    usuario = db.session.get(Usuario, session['user_id'])
    fazenda = Fazenda.query.filter_by(dono_id=usuario.id).first()
    
    # Pega dados do pedido
    dados = request.get_json()
    item_cod = dados.get('item')           # Ex: 'sem_milho' ou 'veneno'
    quantidade = int(dados.get('qtd', 1))
    
    # 1. Verifica preço e existência
    preco_unitario = PRECOS_LOJA.get(item_cod)
    if not preco_unitario:
        return jsonify({'sucesso': False, 'mensagem': f'Item {item_cod} não cadastrado'})
    
    custo_total = preco_unitario * quantidade
    
    # 2. Verifica saldo
    if usuario.dinheiro < custo_total:
        return jsonify({'sucesso': False, 'mensagem': 'Saldo insuficiente'})
    
    # 3. Lógica Inteligente: Descobre qual coluna do banco usar
    # Se for semente (sem_milho), tira o 'sem_' -> fica 'est_milho'
    # Se for insumo (veneno), usa direto -> fica 'est_veneno'
    nome_base = item_cod.replace('sem_', '')
    nome_coluna = f"est_{nome_base}" 
    
    # Verifica se a "gaveta" existe na Fazenda
    if hasattr(fazenda, nome_coluna):
        # Pega valor atual e soma
        estoque_atual = getattr(fazenda, nome_coluna)
        setattr(fazenda, nome_coluna, estoque_atual + quantidade)
        
        # Paga e Salva
        usuario.dinheiro -= custo_total
        db.session.commit()
        return jsonify({'sucesso': True, 'novo_saldo': usuario.dinheiro})
    else:
        print(f"ERRO: Coluna {nome_coluna} não existe no banco!")
        return jsonify({'sucesso': False, 'mensagem': 'Erro de estoque interno'})

@app.route('/api/lote/melhoria/<int:lid>', methods=['POST'])
def melhoria(lid):
    l = db.session.get(Lote, lid); u = db.session.get(Usuario, session['user_id']); d = request.json; acao = d.get('acao')
    if l.fazenda.dono_id != u.id: return jsonify({'erro': 'Visitante!'})
    if acao == 'infra':
        tipo = d.get('tipo'); item = d.get('item'); custo = CUSTOS.get(f"{tipo}_{item}" if item else tipo, 0)
        if u.dinheiro < custo: return jsonify({'erro':'Saldo insuficiente'})
        u.dinheiro -= custo
        if tipo == 'arar': l.status = 'arado'
        elif tipo == 'plantar': l.cultivo = item; l.status='plantado'; l.meses_cultivo = 0
        elif tipo == 'limpeza': l.status = 'limpo'
        elif tipo == 'cerca': l.cerca = item;
        elif tipo == 'cocho': l.cocho = item;
        elif tipo == 'agua': l.agua = item;
        elif tipo == 'gradear': l.status = 'limpo'; l.cultivo = None
        registrar_transacao(u, f"Infra {tipo}", -custo, "infra")
    elif acao == 'comprar_gado':
        qtd = int(d.get('qtd')); fase = d.get('fase'); custo = TABELA_PRECOS[d.get('raca')][fase] * qtd
        if u.dinheiro >= custo:
            u.dinheiro -= custo; idade = 8 if fase == 'filhote' else 36; peso = 6.0 if fase == 'filhote' else 16.0
            for _ in range(qtd): db.session.add(Animal(lote_id=l.id, raca=d.get('raca'), sexo=d.get('sexo'), fase=fase.capitalize(), peso=peso, idade_meses=idade, onde_esta='pasto'))
            registrar_transacao(u, "Compra Gado", -custo, "compra")
        else: return jsonify({'erro':'Sem saldo'})
    db.session.commit(); return jsonify({'sucesso':True})

@app.route('/api/manejo', methods=['POST'])
def manejo():
    u = db.session.get(Usuario, session['user_id']); d = request.json; acao = d.get('acao'); a = db.session.get(Animal, d.get('id'))
    if acao == 'mover_para_curral': a.onde_esta = 'curral'
    elif acao == 'soltar_pasto': a.onde_esta = 'pasto'
    elif acao == 'vacinar': 
        if u.dinheiro >= 50: u.dinheiro-=50; a.vacinado=True
    elif acao == 'vender_frigorifico': v = a.peso * PRECO_ARROBA; u.dinheiro+=v; db.session.delete(a)
    db.session.commit(); return jsonify({'sucesso':True, 'msg':'OK'})

@app.route('/api/renomear/<tipo>/<int:id>', methods=['POST'])
def renomear(tipo, id):
    obj = db.session.get(Fazenda, id) if tipo == 'fazenda' else db.session.get(Lote, id)
    if tipo == 'fazenda': obj.nome_personalizado = request.json.get('nome')
    else: obj.nome = request.json.get('nome')
    db.session.commit(); return jsonify({'sucesso':True})

@app.route('/api/avancar_tempo', methods=['POST'])
def avancar():
    u = db.session.get(Usuario, session['user_id']); u.hora += 1
    if u.hora > 23: u.hora = 0; u.dia += 1
    db.session.commit(); return jsonify({'msg': 'Tempo avançou'})

@app.route('/api/chat', methods=['GET', 'POST'])
def chat():
    if request.method == 'POST':
        u = db.session.get(Usuario, session['user_id']); msg = ChatMensagem(usuario_nome=u.nome, mensagem=request.json.get('msg')); db.session.add(msg); db.session.commit()
        return jsonify({'sucesso':True})
    msgs = ChatMensagem.query.order_by(ChatMensagem.id.desc()).limit(20).all()
    return jsonify([{'user':m.usuario_nome, 'msg':m.mensagem} for m in msgs[::-1]])

# --- ROTAS DO MERCADO (NOVAS) ---
@app.route('/mercado')
def ver_mercado():
    if 'user_id' not in session: return redirect('/login')
    anuncios = Anuncio.query.all()
    return render_template('mercado.html', anuncios=anuncios, user=db.session.get(Usuario, session['user_id']))
    

@app.route('/api/mercado/vender', methods=['POST'])
def vender_animal():
    u = db.session.get(Usuario, session['user_id']); d = request.json
    
    # Recebe o ID de um animal (como referência) e a Quantidade desejada
    ref_animal = db.session.get(Animal, d.get('id_animal'))
    valor = float(d.get('valor'))
    qtd = int(d.get('qtd', 1)) # Se não informar, vende só 1

    if ref_animal.lote.fazenda.dono_id != u.id: return jsonify({'erro':'Não autorizado'})

    # Busca animais disponíveis (Mesmo pasto, mesma raça, mesma fase)
    # Primeiro inclui o próprio animal clicado
    candidatos = [ref_animal]
    
    if qtd > 1:
        # Busca outros iguais no mesmo pasto
        outros = Animal.query.filter_by(
            lote_id=ref_animal.lote_id, 
            onde_esta='pasto', 
            raca=ref_animal.raca, 
            fase=ref_animal.fase
        ).filter(Animal.id != ref_animal.id).limit(qtd - 1).all()
        candidatos.extend(outros)

    # Verifica se tem a quantidade pedida
    if len(candidatos) < qtd:
        return jsonify({'erro': f'Você só tem {len(candidatos)} animais desse tipo disponíveis para venda.'})

    # Cria os anúncios
    for boi in candidatos:
        boi.onde_esta = 'venda'
        db.session.add(Anuncio(vendedor_id=u.id, animal_id=boi.id, valor=valor))
    
    db.session.commit()
    return jsonify({'sucesso':True})


@app.route('/api/mercado/comprar/<int:aid>', methods=['POST'])
def comprar_animal(aid):
    comprador = db.session.get(Usuario, session['user_id']); anuncio = db.session.get(Anuncio, aid)
    if not anuncio: return jsonify({'erro':'Anúncio inexistente'})
    if comprador.dinheiro < anuncio.valor: return jsonify({'erro':'Saldo insuficiente'})
    
    vendedor = anuncio.vendedor; animal = anuncio.animal
    comprador.dinheiro -= anuncio.valor; vendedor.dinheiro += anuncio.valor
    
    pasto_destino = comprador.fazendas[0].lotes[0] 
    animal.lote_id = pasto_destino.id; animal.onde_esta = 'pasto'
    
    db.session.delete(anuncio)
    registrar_transacao(comprador, f"Comprou {animal.raca}", -anuncio.valor, "mercado")
    registrar_transacao(vendedor, f"Vendeu {animal.raca}", anuncio.valor, "mercado")
    db.session.commit(); return jsonify({'sucesso':True})

@app.route('/api/mercado/cancelar/<int:aid>', methods=['POST'])
def cancelar_anuncio(aid):
    u = db.session.get(Usuario, session['user_id']); anuncio = db.session.get(Anuncio, aid)
    if anuncio.vendedor_id == u.id:
        anuncio.animal.onde_esta = 'pasto'; db.session.delete(anuncio); db.session.commit()
        return jsonify({'sucesso':True})
    return jsonify({'erro':'Erro'})

# --- ROTA DE EXPANSÃO (Sede) ---
@app.route('/expandir_silo')
def expandir_silo():
    user_id = session.get('user_id')
    u = db.session.get(Usuario, user_id)
    f = Fazenda.query.filter_by(dono_id=user_id).first()
    
    custo = 5000 * f.nivel_silo

    # CORREÇÃO: Checar o dinheiro no USUÁRIO (u), não na fazenda
    if u.dinheiro >= custo:
        u.dinheiro -= custo
        f.cap_silo += 500
        f.nivel_silo += 1
        db.session.commit()
        flash(f"Silo expandido! Capacidade: {f.cap_silo}kg", "success")
    else:
        flash(f"Dinheiro insuficiente! Precisa de R$ {custo}", "danger")
    
    return redirect(url_for('ver_fazenda', id=f.id))

# --- ROTA DE COLHEITA (Pastos) ---
@app.route('/colher/<int:lote_id>')
def colher(lote_id):
    lote = db.session.get(Lote, lote_id)
    f = lote.fazenda
    
    colheita_estimada = 100
    total_atual = (f.est_milho + f.est_soja + f.est_cafe + f.est_arroz + f.est_feijao + f.est_algodao + f.est_cana + f.est_mandioca + f.est_pimenta)

    if total_atual + colheita_estimada > f.cap_silo:
        flash("Silo Lotado!", "warning")
        return redirect(url_for('ver_fazenda', id=f.id))

    if lote.cultivo:
        # Adiciona ao estoque dinamicamente baseado no que estava plantado
        coluna = f'est_{lote.cultivo}'
        if hasattr(f, coluna):
            setattr(f, coluna, getattr(f, coluna) + colheita_estimada)
    
    lote.cultivo = None
    lote.status = 'limpo'
    db.session.commit()
    flash(f"Colheita realizada!", "success")
    return redirect(url_for('ver_fazenda', id=f.id))

@app.route('/vender_grao/<tipo>')
def vender_grao(tipo):
    user_id = session.get('user_id')
    u = db.session.get(Usuario, user_id)
    # CORREÇÃO: Buscar por dono_id
    f = Fazenda.query.filter_by(dono_id=user_id).first()
    
    if not f: f = Fazenda.query.first()
    
    # Lógica de Preços
    precos = {'milho': 2, 'soja': 5, 'cafe': 12, 'arroz': 3, 'feijao': 4, 'algodao': 6, 'cana': 1, 'mandioca': 2, 'pimenta': 15}
    valor_unidade = precos.get(tipo, 1)
    
    qtd = getattr(f, f'est_{tipo}')
    if qtd > 0:
        lucro = qtd * valor_unidade
        u.dinheiro += lucro
        setattr(f, f'est_{tipo}', 0)
        db.session.commit()
        flash(f"Venda realizada! +R$ {lucro}", "success")

    return redirect(url_for('ver_fazenda', id=f.id))
if __name__ == '__main__':
    with app.app_context(): criar_mundo()
    app.run(debug=True, host='0.0.0.0', port=5000)
