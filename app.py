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

# --- CUSTOS OPERACIONAIS ---
CUSTOS = { 
    'limpeza': 500, 'arar': 1200, 'gradear': 800, 'adubacao': 1500, 
    'cerca_arame': 2000, 'cerca_eletrica': 3500, 'cerca_madeira': 5000, 
    'cocho_sal': 600, 'cocho_creep': 1800, 'agua_bebedouro': 2500, 'agua_represa': 12000,
    # Custos de Plantio
    'plantio_milho': 2500, 'plantio_soja': 3000, 'plantio_arroz': 2800, 
    'plantio_feijao': 2000, 'plantio_algodao': 4000, 'plantio_cana': 3500, 
    'plantio_mandioca': 1500, 'plantio_cafe': 5000, 'plantio_cacau': 6000, 
    'plantio_acai': 4500, 'plantio_cupuacu': 4000, 'plantio_banana': 1800,
    'plantio_abacaxi': 2200, 'plantio_melancia': 1200, 'plantio_pimenta': 3000,
    # Estruturas e Veterinário
    'expandir_celeiro': 5000, 'expandir_silo': 8000, 'expandir_curral': 10000, 
    'vacina': 50, 'inseminacao': 250, 'vacina_aftosa': 100,
    'vacina_brucelose': 120,
    'medicamento_geral': 60,
    'suplemento_engorda': 80
}

# --- PREÇOS ---
PRECOS_LOJA = {
    'sal': 80, 'racao': 120, 'adubo': 150, 'veneno': 200, 'combustivel': 450,
    'sem_milho': 200, 'sem_soja': 350, 'sem_arroz': 180, 'sem_feijao': 250,
    'sem_algodao': 400, 'sem_cana': 300, 'sem_mandioca': 150,
    'sem_cafe': 500, 'sem_cacau': 600, 'sem_acai': 450, 'sem_cupuacu': 400,
    'sem_banana': 200, 'sem_abacaxi': 250, 'sem_melancia': 120, 'sem_pimenta': 300,
    'vacina_aftosa': 150,
    'vacina_brucelose': 180,
    'medicamento_geral': 90,
    'suplemento_engorda': 120   
}

PRECOS_VENDA = {
    'milho': 15, 'soja': 22, 'arroz': 18, 'feijao': 25,
    'algodao': 35, 'cana': 12, 'mandioca': 10, 'cafe': 45,
    'cacau': 50, 'acai': 30, 'cupuacu': 28, 'banana': 8,
    'abacaxi': 15, 'melancia': 10, 'pimenta': 20,
    'vacina_aftosa': 100,
    'vacina_brucelose': 120,
    'medicamento_geral': 60,
    'suplemento_engorda': 80
}

# Tabela com TODOS os 23 animais e peixes citados
TABELA_PRECOS = {
    # --- PECUÁRIA ---
    'nelore': {'filhote': 1200, 'adulto': 3850, 'img': 'nelore.png'},
    'angus': {'filhote': 1500, 'adulto': 4400, 'img': 'angus.png'},
    'girolando': {'filhote': 1300, 'adulto': 4180, 'img': 'girolando.png'},
    'guzera': {'filhote': 1400, 'adulto': 4000, 'img': 'guzera.png'},
    'brahman': {'filhote': 1600, 'adulto': 4500, 'img': 'brahman.png'},
    'cavalo': {'filhote': 2500, 'adulto': 8000, 'img': 'cavalo.png'},
    'porco': {'filhote': 350, 'adulto': 990, 'img': 'porco.png'},
    'ovelha': {'filhote': 400, 'adulto': 1100, 'img': 'ovelha.png'},
    'cabra': {'filhote': 380, 'adulto': 1050, 'img': 'cabra.png'},
    'galinha': {'filhote': 25, 'adulto': 60, 'img': 'galinha.png'},
    'pato': {'filhote': 30, 'adulto': 75, 'img': 'pato.png'},
    'peru': {'filhote': 45, 'adulto': 110, 'img': 'peru.png'},
    
    # --- PEIXES (LOTE 3) ---
    'tambaqui': {'filhote': 8, 'adulto': 60, 'img': 'tambaqui.png'},
    'pirarucu': {'filhote': 60, 'adulto': 400, 'img': 'pirarucu.png'},
    'pacu': {'filhote': 6, 'adulto': 55, 'img': 'pacu.png'},
    'matrinxa': {'filhote': 10, 'adulto': 80, 'img': 'matrinxa.png'},
    'jaraqui': {'filhote': 3, 'adulto': 35, 'img': 'jaraqui.png'},
    'curimata': {'filhote': 3, 'adulto': 45, 'img': 'curimata.png'},
    'surubim': {'filhote': 12, 'adulto': 130, 'img': 'surubim.png'},
    'pintado': {'filhote': 15, 'adulto': 150, 'img': 'pintado.png'},
    'cachara': {'filhote': 14, 'adulto': 140, 'img': 'cachara.png'},
    'tucunare': {'filhote': 10, 'adulto': 95, 'img': 'tucunare.png'},
    'piau': {'filhote': 5, 'adulto': 45, 'img': 'piau.png'}
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

class Amizade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    amigo_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    status = db.Column(db.String(20), default='pendente')
    
class ChatMensagem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    remetente_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    destinatario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=True) 
    usuario_nome = db.Column(db.String(50))
    mensagem = db.Column(db.String(200))
    tipo = db.Column(db.String(20), default='global')
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
    
    # Estoques Grãos
    est_milho = db.Column(db.Integer, default=0); est_soja = db.Column(db.Integer, default=0)
    est_arroz = db.Column(db.Integer, default=0); est_feijao = db.Column(db.Integer, default=0)
    est_algodao = db.Column(db.Integer, default=0); est_cana = db.Column(db.Integer, default=0)
    est_mandioca = db.Column(db.Integer, default=0); est_cafe = db.Column(db.Integer, default=0)
    est_cacau = db.Column(db.Integer, default=0); est_acai = db.Column(db.Integer, default=0)
    est_cupuacu = db.Column(db.Integer, default=0); est_banana = db.Column(db.Integer, default=0)
    est_abacaxi = db.Column(db.Integer, default=0); est_melancia = db.Column(db.Integer, default=0)
    est_pimenta = db.Column(db.Integer, default=0)
    # Estoques Insumos
    est_sal = db.Column(db.Integer, default=0); est_racao = db.Column(db.Integer, default=0)
    est_adubo = db.Column(db.Integer, default=0); est_veneno = db.Column(db.Integer, default=0)
    est_combustivel = db.Column(db.Integer, default=0)
    
    est_vacina_aftosa = db.Column(db.Integer, default=0)
    est_vacina_brucelose = db.Column(db.Integer, default=0)
    est_medicamento_geral = db.Column(db.Integer, default=0)
    est_suplemento_engorda = db.Column(db.Integer, default=0)
    lotes = db.relationship('Lote', backref='fazenda', lazy=True)
    
    cap_silo = db.Column(db.Integer, default=500)
    cap_armazem = db.Column(db.Integer, default=200)
    nivel_silo = db.Column(db.Integer, default=1)
    nivel_armazem = db.Column(db.Integer, default=1)
    
    cap_curral = db.Column(db.Integer, default=10) # Capacidade inicial de 10 cabeças
    nivel_curral = db.Column(db.Integer, default=1)
    
    tem_represa_geral = db.Column(db.Boolean, default=False)
    tem_chiqueiro = db.Column(db.Boolean, default=False) # ADICIONADO
    tem_galinheiro = db.Column(db.Boolean, default=False) # ADICIONADO
    
class Lote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fazenda_id = db.Column(db.Integer, db.ForeignKey('fazenda.id'))
    posicao = db.Column(db.Integer); nome = db.Column(db.String(50))
    status = db.Column(db.String(20), default="mato") 
    cultivo = db.Column(db.String(20)); meses_cultivo = db.Column(db.Integer, default=0)
    cerca = db.Column(db.String(20), default="nenhuma"); cocho = db.Column(db.String(20), default="nenhum"); agua = db.Column(db.String(20), default="nenhuma") 
    animais = db.relationship('Animal', backref='lote', lazy=True)
    def para_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'status': self.status if self.status else 'mato'
        }     
    
class Animal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lote_id = db.Column(db.Integer, db.ForeignKey('lote.id'))
    raca = db.Column(db.String(20)); sexo = db.Column(db.String(10)); fase = db.Column(db.String(20)); peso = db.Column(db.Float)
    idade_meses = db.Column(db.Integer); prenha = db.Column(db.Boolean, default=False)
    onde_esta = db.Column(db.String(20), default="pasto"); vacinado = db.Column(db.Boolean, default=False)
    origem = db.Column(db.String(50), default="Leilão")

class Anuncio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vendedor_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    animal_id = db.Column(db.Integer, db.ForeignKey('animal.id'))
    valor = db.Column(db.Float)
    data = db.Column(db.DateTime, default=datetime.datetime.utcnow)
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
    if 'user_id' not in session: 
        return redirect('/login')
    
    # BUSCA O USUÁRIO LOGADO (Essencial para o novo mapa)
    usuario = db.session.get(Usuario, session['user_id'])
    
    if not usuario:
        return redirect('/login')
        
    return render_template('mapa_global.html', user=usuario)

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
    
    # --- MANTIDO IGUAL ---
    gado_curral = Animal.query.join(Lote).filter(Lote.fazenda_id == id, Animal.onde_esta == 'curral').all()
    
    visitante = True
    if user and f.dono_id == user.id:
        visitante = False

    # --- LÓGICA SOCIAL ATUALIZADA ---
    pedidos_pendentes = []
    lista_amigos_final = [] # Criamos uma lista nova para guardar os NOMES
    
    if user:
        # 1. Busca pedidos (Mantido)
        pedidos_pendentes = Amizade.query.filter_by(amigo_id=user.id, status='pendente').all()
        
        # 2. Busca conexões (Mantido)
        conexoes = Amizade.query.filter(
            ((Amizade.usuario_id == user.id) | (Amizade.amigo_id == user.id)) & 
            (Amizade.status == 'aceito')
        ).all()

        # 3. NOVO BLOCO: "Traduz" os IDs para Nomes Reais
        for c in conexoes:
            # Se eu sou o usuario_id, meu amigo é o amigo_id (e vice-versa)
            id_do_amigo = c.amigo_id if c.usuario_id == user.id else c.usuario_id
            
            # Busca os dados desse amigo no banco de Usuários
            amigo_obj = db.session.get(Usuario, id_do_amigo)
            
            if amigo_obj:
                # Adiciona na lista final com ID e NOME para o HTML usar
                lista_amigos_final.append({
                    'id': amigo_obj.id,
                    'nome': amigo_obj.nome
                })

    # No retorno, trocamos 'amigos=meus_amigos' por 'amigos=lista_amigos_final'
    return render_template('gestao_fazenda.html', 
                           fazenda=f, user=user, visitante=visitante, 
                           custos=CUSTOS, gado_curral=gado_curral,
                           pedidos=pedidos_pendentes, 
                           amigos=lista_amigos_final) 
        
@app.route('/api/pasto/<int:lid>')
def get_pasto(lid):
    l = db.session.get(Lote, lid)
    if not l:
        return jsonify({'erro': 'Lote não encontrado'}), 404
    
    animais = []
    for a in l.animais:
        if a.onde_esta == 'pasto':
            animais.append({
                'id': a.id, 
                'tipo': f"{a.raca}", 
                'fase': a.fase, 
                'sexo': a.sexo, 
                'idade': a.idade_meses, 
                'peso': a.peso, 
                'origem': a.origem, 
                'status': "Prenha" if a.prenha else ("Vacinado" if a.vacinado else "PENDENTE")
            })
            
    info_plantio = f"{l.cultivo.capitalize()} (Mês {l.meses_cultivo})" if l.status == 'plantado' else ""
    
    # É essencial que o dicionário retorne todos esses campos para o JS não quebrar
    return jsonify({
        'nome': l.nome, 
        'status': l.status, 
        'cultivo': l.cultivo, 
        'info_plantio': info_plantio, 
        'cerca': l.cerca, 
        'cocho': l.cocho, 
        'agua': l.agua, 
        'animais': animais
    })

@app.route('/comprar_loja', methods=['POST'])
def comprar_loja():
    if 'user_id' not in session:
        return jsonify({'sucesso': False, 'erro': 'Não logado'}) # Troquei mensagem por erro
    
    usuario = db.session.get(Usuario, session['user_id'])
    fazenda = Fazenda.query.filter_by(dono_id=usuario.id).first()
    
    dados = request.get_json()
    item_cod = dados.get('item')
    quantidade = int(dados.get('qtd', 1))
    
    if "sem_" in item_cod:
        total_atual = (fazenda.est_milho + fazenda.est_soja + fazenda.est_cafe + 
                       fazenda.est_arroz + fazenda.est_feijao + fazenda.est_algodao + 
                       fazenda.est_cana + fazenda.est_mandioca + fazenda.est_pimenta +
                       fazenda.est_cacau + fazenda.est_acai + fazenda.est_cupuacu +
                       fazenda.est_banana + fazenda.est_abacaxi + fazenda.est_melancia)

        if total_atual + quantidade > fazenda.cap_silo:
            return jsonify({'sucesso': False, 'erro': f'Silo sem espaço! Limite: {fazenda.cap_silo}kg'})
    else:
         # Lógica do Armazém
         total_insumos = (fazenda.est_sal + fazenda.est_racao + fazenda.est_adubo + 
                         fazenda.est_veneno + fazenda.est_combustivel +
                         fazenda.est_vacina_aftosa + fazenda.est_vacina_brucelose +
                         fazenda.est_medicamento_geral + fazenda.est_suplemento_engorda)
         if total_insumos + quantidade > fazenda.cap_armazem:
            return jsonify({'sucesso': False, 'erro': 'Armazém lotado!'})
         
    preco_unitario = PRECOS_LOJA.get(item_cod)
    if not preco_unitario:
        return jsonify({'sucesso': False, 'erro': f'Item {item_cod} não cadastrado'})
        
    custo_total = preco_unitario * quantidade
    
    if usuario.dinheiro < custo_total:
        return jsonify({'sucesso': False, 'erro': 'Saldo insuficiente'})
    
    nome_base = item_cod.replace('sem_', '')
    nome_coluna = f"est_{nome_base}" 
    
    if hasattr(fazenda, nome_coluna):
        estoque_atual = getattr(fazenda, nome_coluna)
        setattr(fazenda, nome_coluna, estoque_atual + quantidade)
        usuario.dinheiro -= custo_total
        
        # Aqui é o segredo: mudei para 'msg' para o sede.js entender
        db.session.commit()
        return jsonify({
            'sucesso': True, 
            'msg': f'Compra realizada: {quantidade} un!', 
            'novo_saldo': usuario.dinheiro
        })
    else:
        return jsonify({'sucesso': False, 'erro': 'Erro de estoque interno'})

# No seu arquivo app.py
@app.route('/api/lote/melhoria/<int:lote_id>', methods=['POST'])
def melhoria_lote(lote_id):
    if 'user_id' not in session: 
        return jsonify({'sucesso': False, 'erro': 'Sessão expirada. Faça login novamente.'})
    
    user = db.session.get(Usuario, session['user_id'])
    
    # TRAVA DE SEGURANÇA: Se o usuário não existe no banco, para aqui.
    if user is None:
        session.pop('user_id', None) # Limpa a sessão bugada
        return jsonify({'sucesso': False, 'erro': 'Usuário não encontrado. Refaça o login.'})

    lote = db.session.get(Lote, lote_id)
    dados = request.get_json()
    
    # O segredo está em capturar o 'tipo' corretamente
    tipo = dados.get('tipo') 

    try:
        # --- LÓGICA DE INFRAESTRUTURA RESTAURADA ---
        if tipo == 'limpeza':
            if user.dinheiro < 500: return jsonify({'sucesso': False, 'erro': 'Sem saldo'})
            user.dinheiro -= 500
            lote.status = 'livre'
        
        elif tipo == 'arar':
            if user.dinheiro < 1200: return jsonify({'sucesso': False, 'erro': 'Sem saldo'})
            user.dinheiro -= 1200
            lote.status = 'arado'
            lote.cultivo = None

        elif tipo == 'cercar':
            if user.dinheiro < 800: return jsonify({'sucesso': False, 'erro': 'Sem saldo'})
            user.dinheiro -= 800
            lote.status = 'cercado'

        elif tipo == 'infra_pecuaria':
            if user.dinheiro < 1500: return jsonify({'sucesso': False, 'erro': 'Sem saldo'})
            user.dinheiro -= 1500
            lote.status = 'pasto' # Terreno vira PASTO e aceita bois

        elif tipo == 'remover_pasto_arar':
            if len(lote.animais) > 0: return jsonify({'sucesso': False, 'erro': 'Retire os animais'})
            if user.dinheiro < 1000: return jsonify({'sucesso': False, 'erro': 'Sem saldo'})
            user.dinheiro -= 1000
            lote.status = 'arado'

        elif tipo == 'plantar':
            item = dados.get('item')
            lote.status = 'plantado'
            lote.cultivo = item
            lote.meses_cultivo = 0

        db.session.commit()
        return jsonify({'sucesso': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'sucesso': False, 'erro': str(e)})

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
    if 'user_id' not in session: return jsonify({'sucesso': False})
    obj = db.session.get(Fazenda, id) if tipo == 'fazenda' else db.session.get(Lote, id)
    if not obj: return jsonify({'sucesso': False, 'erro': 'Não encontrado'})
    dados = request.get_json()
    if tipo == 'fazenda':
        obj.nome_personalizado = dados.get('nome')
    else:
        obj.nome = dados.get('nome')
    db.session.commit()
    return jsonify({'sucesso': True})

@app.route('/api/fazenda/expandir_curral', methods=['POST'])
def expandir_curral():
    u = db.session.get(Usuario, session['user_id'])
    f = u.fazendas[0]
    custo = 5000 * f.nivel_curral
    
    if u.dinheiro >= custo:
        u.dinheiro -= custo
        f.cap_curral += 5
        f.nivel_curral += 1
        registrar_transacao(u, f"Expansão Curral Nível {f.nivel_curral}", -custo, "infra")
        db.session.commit()
        return jsonify({'sucesso': True, 'msg': f'Curral expandido para {f.cap_curral} cabeças!'})
    return jsonify({'sucesso': False, 'erro': 'Saldo insuficiente!'})

@app.route('/api/avancar_tempo', methods=['POST'])
def avancar():
    u = db.session.get(Usuario, session['user_id']); u.hora += 1
    if u.hora > 23: u.hora = 0; u.dia += 1
    db.session.commit(); return jsonify({'msg': 'Tempo avançou'})
        
# --- ROTAS DO MERCADO ---
# --- MERCADO ATUALIZADO COM IA ---
@app.route('/mercado')
def ver_mercado():
    if 'user_id' not in session: 
        return redirect('/login')
    
    anuncios_players = Anuncio.query.all()
    
    # BUSCA O USUÁRIO LOGADO
    usuario = db.session.get(Usuario, session['user_id'])
    
    # Vendedores Oficiais (IA) - Agora pegando as chaves da TABELA_PRECOS
    vendedores_ia = []
    
    # O segredo é percorrer todas as chaves da sua tabela de preços
    for raca in TABELA_PRECOS.keys():
        # Preço base adulto com a margem de 10% da IA
        preco_base = TABELA_PRECOS[raca]['adulto']
        
        vendedores_ia.append({
            'id_ia': raca,
            'vendedor_nome': "🚚 Fornecedor Oficial",
            'raca': raca.capitalize(),
            'valor': preco_base * 1.1 
        })
        
    return render_template('mercado.html', 
                           anuncios=anuncios_players, 
                           anuncios_ia=vendedores_ia,
                           TABELA_PRECOS=TABELA_PRECOS,  # ESSENCIAL: Envia para o JS atualizar preços
                           user=usuario)

@app.route('/api/mercado/comprar_v2', methods=['POST'])
def comprar_v2():
    u = db.session.get(Usuario, session['user_id'])
    dados = request.get_json()
    
    id_fazenda = dados.get('fazenda_id')
    local_destino = dados.get('local', 'curral').lower()
    especie_id = dados.get('id', '').lower()
    qtd = int(dados.get('qtd', 1))
    
    # Captura a fase e o sexo enviados pelo JavaScript
    fase_escolhida = dados.get('fase', 'Bezerro').capitalize()
    sexo_escolhido = dados.get('sexo', 'M')
    
    fazenda = next((f for f in u.fazendas if f.id == id_fazenda), u.fazendas[0])

    # --- 1. BLOQUEIOS DE SEGURANÇA (MANTIDOS) ---
    so_curral = ['nelore', 'angus', 'brahman', 'girolando', 'guzera', 'cavalo', 'ovelha', 'cabra']
    peixes = ['tambaqui', 'pirarucu', 'pacu', 'matrinxa', 'jaraqui', 'curimata', 'surubim', 'pintado', 'cachara', 'tucunare', 'piau']

    if especie_id in so_curral and local_destino != 'curral':
        return jsonify({'sucesso': False, 'erro': 'Bovinos e Equinos devem ser entregues no Curral!'})
    if especie_id in peixes and local_destino != 'represa':
        return jsonify({'sucesso': False, 'erro': 'Peixes devem ser entregues diretamente na Represa!'})
    if especie_id == 'porco' and local_destino != 'chiqueiro':
        return jsonify({'sucesso': False, 'erro': 'Suínos devem ser entregues no Chiqueiro!'})
    if especie_id == 'galinha' and local_destino != 'galinheiro':
        return jsonify({'sucesso': False, 'erro': 'Aves devem ser entregues no Galinheiro!'})

    # --- 2. VALIDAÇÃO DE OBRAS (MANTIDO) ---
    if local_destino == 'represa' and not getattr(fazenda, 'tem_represa_geral', False):
        return jsonify({'sucesso': False, 'erro': 'A Represa ainda não foi construída!'})
    if local_destino == 'chiqueiro' and not getattr(fazenda, 'tem_chiqueiro', False):
        return jsonify({'sucesso': False, 'erro': 'O Chiqueiro ainda não foi construído!'})
    if local_destino == 'galinheiro' and not getattr(fazenda, 'tem_galinheiro', False):
        return jsonify({'sucesso': False, 'erro': 'O Galinheiro ainda não foi construído!'})

    # --- 3. FINANCEIRO E PREÇOS (AJUSTADO) ---
    # Agora tentamos pegar o preço exato que veio da tela do mercado
    custo_unitario = dados.get('preco')
    
    # Se o preço não veio no pacote (segurança), usamos a tabela fixa
    if not custo_unitario:
        info_animal = TABELA_PRECOS.get(especie_id, {'adulto': 1000})
        # Se for filhote/bezerro, tenta pegar o preço de filhote da tabela
        chave = 'filhote' if fase_escolhida.lower() in ['filhote', 'bezerro'] else 'adulto'
        custo_unitario = info_animal.get(chave, info_animal['adulto'])

    custo_total = custo_unitario * qtd

    if u.dinheiro < custo_total:
        return jsonify({'sucesso': False, 'erro': f'Saldo insuficiente! Necessário R$ {custo_total}'})

    # --- NOVA TRAVA DE LOTAÇÃO DO TRONCO (MANTIDO) ---
    if local_destino == 'curral':
        animais_no_curral = Animal.query.join(Lote).filter(
            Lote.fazenda_id == fazenda.id, 
            Animal.onde_esta == 'curral'
        ).count()
        capacidade_maxima = getattr(fazenda, 'cap_curral', 10)
        
        if animais_no_curral + qtd > capacidade_maxima:
            return jsonify({
                'sucesso': False, 
                'erro': f'Tronco Lotado! Espaço: {animais_no_curral}/{capacidade_maxima}.'
            })

    # --- EXECUÇÃO DA COMPRA ---
    u.dinheiro -= custo_total
    # Incluímos a fase na descrição para o histórico ficar correto
    registrar_transacao(u, f"Compra Mercado: {qtd}x {especie_id.capitalize()} ({fase_escolhida})", -custo_total, "compra")

    # --- 4. CRIAÇÃO DOS ANIMAIS (AJUSTADO) ---
    for _ in range(qtd):
        # Peso realista: Adulto 18@, Filhote 12@
        peso_inicial = 18.0 if fase_escolhida.lower() == 'adulto' else 12.0

        novo_animal = Animal(
            lote_id=fazenda.lotes[0].id, 
            raca=especie_id.capitalize(), 
            sexo=sexo_escolhido, 
            fase=fase_escolhida, # Usa a fase vinda do mercado
            peso=peso_inicial, 
            onde_esta=local_destino,
            origem="Mercado Logístico"
        )
        db.session.add(novo_animal)
    
    db.session.commit()
    
    return jsonify({
        'sucesso': True, 
        'msg': f'R$ {custo_total} pagos! Carga de {fase_escolhida} entregue!',
        'destino': local_destino.upper()
    })
    
@app.route('/api/mercado/vender', methods=['POST'])
def vender_animal():
    u = db.session.get(Usuario, session['user_id']); d = request.json
    ref_animal = db.session.get(Animal, d.get('id_animal'))
    valor = float(d.get('valor'))
    qtd = int(d.get('qtd', 1))

    if ref_animal.lote.fazenda.dono_id != u.id: return jsonify({'erro':'Não autorizado'})

    candidatos = [ref_animal]
    if qtd > 1:
        outros = Animal.query.filter_by(
            lote_id=ref_animal.lote_id, 
            onde_esta='pasto', 
            raca=ref_animal.raca, 
            fase=ref_animal.fase
        ).filter(Animal.id != ref_animal.id).limit(qtd - 1).all()
        candidatos.extend(outros)

    if len(candidatos) < qtd:
        return jsonify({'erro': f'Você só tem {len(candidatos)} animais desse tipo disponíveis para venda.'})

    for boi in candidatos:
        boi.onde_esta = 'venda'
        db.session.add(Anuncio(vendedor_id=u.id, animal_id=boi.id, valor=valor))
    
    db.session.commit()
    return jsonify({'sucesso':True})
        
@app.route('/api/mercado/cancelar', methods=['POST'])
def cancelar_venda_definitivo():
    u = db.session.get(Usuario, session['user_id'])
    dados = request.get_json()
    # Usa o ID que vem do JavaScript para identificar o anúncio
    aid = dados.get('anuncio_id') 

    anuncio = Anuncio.query.get(aid)
    if anuncio and anuncio.vendedor_id == u.id:
        # Se o animal existir, devolvemos ele para o estado normal
        if anuncio.animal:
            anuncio.animal.onde_esta = 'curral'
        db.session.delete(anuncio)
        db.session.commit()
        return jsonify({'sucesso': True})
    return jsonify({'sucesso': False, 'erro': 'Não autorizado'})

@app.route('/expandir_silo')
def expandir_silo():
    user_id = session.get('user_id')
    u = db.session.get(Usuario, user_id)
    f = Fazenda.query.filter_by(dono_id=user_id).first()
    custo = 5000 * f.nivel_silo

    if u.dinheiro >= custo:
        u.dinheiro -= custo
        f.cap_silo += 500
        f.nivel_silo += 1
        registrar_transacao(u, f"Melhoria: Expansão Silo Nível {f.nivel_silo}", -custo, "infra")
        db.session.commit()
        flash(f"Silo expandido! Capacidade: {f.cap_silo}kg", "success")
    else:
        flash(f"Dinheiro insuficiente! Precisa de R$ {custo}", "danger")
    
    return redirect(url_for('ver_fazenda', id=f.id))

@app.route('/colher/<int:lote_id>')
def colher(lote_id):
    lote = db.session.get(Lote, lote_id)
    f = lote.fazenda
    
    colheita_estimada = 100
    total_atual = (f.est_milho + f.est_soja + f.est_cafe + f.est_arroz + f.est_feijao + f.est_algodao + f.est_cana + f.est_mandioca + f.est_pimenta)
    
    if total_atual + colheita_estimada > f.cap_silo:
        flash("Atenção: Silo Lotado! Expanda o silo ou venda produtos para colher.", "warning")
        return redirect(url_for('ver_fazenda', id=f.id))

    if lote.cultivo:
        coluna = f'est_{lote.cultivo}'
        if hasattr(f, coluna):
            setattr(f, coluna, getattr(f, coluna) + colheita_estimada)
    
    lote.cultivo = None
    lote.status = 'arado'
    db.session.commit()
    
    flash(f"Colheita realizada!", "success")
    return redirect(url_for('ver_fazenda', id=f.id))

# --- ROTA DE VENDA SEGURA ---
@app.route('/api/vender_produto', methods=['POST'])
def vender_produto():
    if 'user_id' not in session: return jsonify({'sucesso': False, 'erro': 'Login necessário'})
    dados = request.get_json()
    item = dados.get('item')
    qtd_venda = int(dados.get('qtd'))
    
    u = db.session.get(Usuario, session['user_id'])
    f = Fazenda.query.filter_by(dono_id=u.id).first()
    
    preco_unitario = PRECOS_VENDA.get(item)
    coluna_estoque = f"est_{item}"
    
    if hasattr(f, coluna_estoque):
        estoque_atual = getattr(f, coluna_estoque)
        if estoque_atual >= qtd_venda:
            setattr(f, coluna_estoque, estoque_atual - qtd_venda)
            valor_venda = qtd_venda * preco_unitario
            u.dinheiro += valor_venda
            
            registrar_transacao(u, f"Venda: {qtd_venda}kg de {item}", valor_venda, "venda")
            db.session.commit()
            # Salva no banco de dados
            
            flash(f"Venda realizada: {qtd_venda}kg de {item}!", "success")
            return jsonify({'sucesso': True, 'msg': 'Venda realizada!'})
    return jsonify({'sucesso': False, 'erro': 'Erro no estoque'})

# --- ROTA DE PEDIR AMIZADE ---
@app.route('/pedir_amizade/<int:amigo_id>')
def pedir_amizade(amigo_id):
    if 'user_id' not in session: return redirect(url_for('login'))
    
    usuario_atual = session['user_id']
    if usuario_atual == amigo_id: return redirect(url_for('index'))

    existe = Amizade.query.filter_by(usuario_id=usuario_atual, amigo_id=amigo_id).first()
    if not existe:
        novo_pedido = Amizade(usuario_id=usuario_atual, amigo_id=amigo_id, status='pendente')
        db.session.add(novo_pedido)
        db.session.commit()
    
    return redirect(request.referrer or url_for('index'))

# --- ROTA API CHAT (CORRETA E ÚNICA) ---
@app.route('/api/chat', methods=['GET', 'POST'])
def chat():
    user_id = session.get('user_id')
    if not user_id: 
        return jsonify({'erro': 'Não logado'}), 401
    
    # 1. ENVIO DE MENSAGEM (POST)
    if request.method == 'POST':
        u = db.session.get(Usuario, user_id)
        dados = request.get_json()
        
        tipo_msg = dados.get('tipo', 'global')
        dest_id = dados.get('destinatario_id')

        if tipo_msg == 'privado' and not dest_id:
            tipo_msg = 'global'

        nova_msg = ChatMensagem(
            remetente_id=u.id,
            usuario_nome=u.nome,
            mensagem=dados.get('mensagem'),
            tipo=tipo_msg,
            destinatario_id=dest_id
        )
        db.session.add(nova_msg)
        db.session.commit()
        return jsonify({'sucesso': True})
    
    # 2. LEITURA DE MENSAGENS (GET)
    mensagens = ChatMensagem.query.filter(
        (ChatMensagem.tipo == 'global') | 
        (ChatMensagem.remetente_id == user_id) | 
        (ChatMensagem.destinatario_id == user_id)
    ).order_by(ChatMensagem.timestamp.desc()).limit(30).all()
    
    return jsonify([{
        'nome': m.usuario_nome, 
        'texto': m.mensagem, 
        'tipo': m.tipo,
        'remetente_id': m.remetente_id,
        'destinatario_id': m.destinatario_id
    } for m in mensagens])
    
@app.route('/aceitar_amizade/<int:id>')
def aceitar_amizade(id):
    pedido = db.session.get(Amizade, id)
    if pedido and session.get('user_id') == pedido.amigo_id:
        pedido.status = 'aceito'
        db.session.commit()
    return redirect(request.referrer or url_for('index'))

@app.route('/recusar_amizade/<int:id>')
def recusar_amizade(id):
    pedido = db.session.get(Amizade, id)
    if pedido and session.get('user_id') == pedido.amigo_id:
        db.session.delete(pedido)
        db.session.commit()
    return redirect(request.referrer or url_for('index'))
    
# --- NOVAS ROTAS DE MANEJO DO CURRAL ---
@app.route('/api/animal/manejo_curral', methods=['POST'])
def manejo_curral():
    if 'user_id' not in session: return jsonify({'erro': 'Login necessário'})
    u = db.session.get(Usuario, session['user_id'])
    f = u.fazendas[0]
    dados = request.json
    animal = db.session.get(Animal, dados.get('animal_id'))
    acao = dados.get('acao') 

    if not animal: return jsonify({'erro': 'Animal não encontrado!'})

    if acao == 'aftosa':
        if animal.vacinado: return jsonify({'erro': 'Já vacinado!'})
        if f.est_vacina_aftosa < 1: return jsonify({'erro': 'Sem Vacina Aftosa!'})
        f.est_vacina_aftosa -= 1
        animal.vacinado = True
        msg = "💉 Vacina Aftosa aplicada!"

    elif acao == 'brucelose':
        if f.est_vacina_brucelose < 1: return jsonify({'erro': 'Sem Vacina Brucelose!'})
        f.est_vacina_brucelose -= 1
        msg = "💉 Vacina Brucelose aplicada!"

    elif acao == 'suplemento':
        if f.est_suplemento_engorda < 1: return jsonify({'erro': 'Sem Suplemento!'})
        f.est_suplemento_engorda -= 1
        animal.peso += 0.5 # Realismo: Ganho de peso pelo manejo
        msg = "🌽 Suplemento aplicado! +0.5@"

    db.session.commit()
    return jsonify({'sucesso': True, 'msg': msg})

@app.route('/api/animal/vender_frigorifico', methods=['POST'])
def vender_frigorifico():
    if 'user_id' not in session: 
        return jsonify({'sucesso': False, 'erro': 'Sessão expirada'})
    
    # Busca o usuário e o animal
    u = db.session.get(Usuario, session['user_id'])
    animal_id = request.json.get('id')
    animal = db.session.get(Animal, animal_id)
    
    if not animal:
        return jsonify({'sucesso': False, 'erro': 'Animal não encontrado no curral!'})
    
    # LÓGICA DE REALISMO: Preço baseado no peso atual (engorda valendo a pena!)
    preco_arroba = 285.00 # Você pode mudar esse valor conforme o mercado
    valor_venda = animal.peso * preco_arroba
    
    try:
        # Adiciona o dinheiro ao usuário
        u.dinheiro += valor_venda
        
        # Opcional: Registrar no seu histórico financeiro se você tiver essa função
        # registrar_transacao(u, f"Venda Frigorífico: {animal.raca}", valor_venda, "venda")
        
        # Remove o animal do banco de dados (ele foi pro abate/venda)
        db.session.delete(animal)
        db.session.commit()
        
        return jsonify({
            'sucesso': True, 
            'msg': f'Vendido com sucesso! R$ {valor_venda:,.2f} adicionados à conta.'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'sucesso': False, 'erro': f'Erro ao processar venda: {str(e)}'})

@app.route('/api/animal/mover', methods=['POST'])
def mover_animal_novo():
    if 'user_id' not in session: 
        return jsonify({'sucesso': False, 'erro': 'Login necessário'})
    
    dados = request.get_json()
    animal = db.session.get(Animal, dados.get('animal_id'))
    lote = db.session.get(Lote, dados.get('lote_id'))
    
    if not animal:
        return jsonify({'sucesso': False, 'erro': 'Animal não encontrado!'})

    # --- NOVIDADE: REALISMO DE MANEJO ---
    # Se o animal não estiver vacinado, ele não pode sair para o pasto
    if not animal.vacinado:
        return jsonify({
            'sucesso': False, 
            'erro': f'Manejo Pendente! O animal #{animal.id} precisa ser vacinado antes de ser enviado ao pasto.'
        })

    if not lote or lote.status != 'pasto':
        return jsonify({'sucesso': False, 'erro': 'Este lote não é um pasto pronto!'})

    try:
        animal.lote_id = lote.id
        animal.onde_esta = 'pasto'
        db.session.commit()
        
        # Adicionamos a 'msg' para o seu sede.js mostrar o aviso de sucesso
        return jsonify({
            'sucesso': True, 
            'msg': f'Animal #{animal.id} movido com sucesso para o pasto!'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'sucesso': False, 'erro': f'Erro ao mover: {str(e)}'})

@app.route('/expandir_armazem')
def expandir_armazem():
    user_id = session.get('user_id')
    u = db.session.get(Usuario, user_id)
    f = Fazenda.query.filter_by(dono_id=user_id).first()
    custo = 2500 # Preço que já aparece no seu botão

    if u.dinheiro >= custo:
        u.dinheiro -= custo
        f.cap_armazem += 300 # Aumenta a capacidade
        f.nivel_armazem += 1
        # Registra a saída no financeiro
        registrar_transacao(u, f"Melhoria: Expansão Armazém Nível {f.nivel_armazem}", -custo, "infra")
        db.session.commit()
        flash(f"Armazém expandido! Nova Capacidade: {f.cap_armazem} un", "success")
    else:
        flash(f"Dinheiro insuficiente! Precisa de R$ {custo}", "danger")
    
    return redirect(url_for('ver_fazenda', id=f.id))

@app.route('/api/vender_insumo', methods=['POST'])
def vender_insumo():
    if 'user_id' not in session: return jsonify({'sucesso': False, 'erro': 'Login necessário'})
    dados = request.get_json()
    item = dados.get('item')
    qtd_venda = int(dados.get('qtd'))
    
    u = db.session.get(Usuario, session['user_id'])
    f = Fazenda.query.filter_by(dono_id=u.id).first()
    
    # Realismo: Venda de insumo paga metade do preço de compra da loja
    precos_venda_insumo = {'sal': 40, 'racao': 60, 'adubo': 75, 'veneno': 100, 'combustivel': 225}
    preco_unitario = precos_venda_insumo.get(item, 0)
    coluna_estoque = f"est_{item}"
    
    if hasattr(f, coluna_estoque):
        estoque_atual = getattr(f, coluna_estoque)
        if estoque_atual >= qtd_venda:
            setattr(f, coluna_estoque, estoque_atual - qtd_venda)
            valor_recebido = qtd_venda * preco_unitario
            u.dinheiro += valor_recebido
            # Registra a entrada no financeiro
            registrar_transacao(u, f"Venda Insumo: {qtd_venda} un de {item}", valor_recebido, "venda")
            db.session.commit()
            flash(f"Venda de insumo realizada! +R$ {valor_recebido}", "success")
            return jsonify({'sucesso': True, 'msg': 'Venda realizada!'})
    return jsonify({'sucesso': False, 'erro': 'Erro no estoque'})

@app.route('/api/animal/vender_lote_curral', methods=['POST'])
def vender_lote_curral():
    u = db.session.get(Usuario, session['user_id'])
    dados = request.get_json()
    raca_alvo = dados.get('raca')
    quantidade = int(dados.get('quantidade', 1))
    fazenda_id = dados.get('fazenda_id')

    # Busca animais daquela raça que estão especificamente no curral dessa fazenda
    animais = Animal.query.join(Lote).filter(
        Lote.fazenda_id == fazenda_id,
        Animal.raca == raca_alvo,
        Animal.onde_esta == 'curral'
    ).limit(quantidade).all()

    if len(animais) < quantidade:
        return jsonify({'sucesso': False, 'erro': f'Você só possui {len(animais)} animais desta raça no curral.'})

    valor_total = 0
    for a in animais:
        valor_venda = a.peso * 285.00 # Preço fixo do frigorífico
        valor_total += valor_venda
        db.session.delete(a)

    u.dinheiro += valor_total
    registrar_transacao(u, f"Venda Lote Curral: {quantidade}x {raca_alvo}", valor_total, "venda")
    db.session.commit()

    return jsonify({'sucesso': True, 'msg': f'Lote vendido! R$ {valor_total:,.2f} creditados.'})

@app.route('/api/mercado/anunciar', methods=['POST'])
def anunciar_leilao():
    if 'user_id' not in session:
        return jsonify({'sucesso': False, 'erro': 'Sessão expirada'})
    
    u = db.session.get(Usuario, session['user_id'])
    dados = request.get_json()
    
    # Capturamos todos os dados enviados pelo JavaScript
    animal_id = dados.get('animal_id') # Pode ser o ID real ou 0 para Lote
    raca = dados.get('raca')
    preco = float(dados.get('preco', 0))
    quantidade = int(dados.get('quantidade', 1))
    
    # Identificamos a fazenda ativa (usando a primeira do usuário por padrão)
    fazenda_id = u.fazendas[0].id

    # --- LÓGICA DE SELEÇÃO DE ANIMAIS ---
    if animal_id and animal_id != 0:
        # VENDA INDIVIDUAL: Busca o animal específico pelo ID
        animal_alvo = Animal.query.get(animal_id)
        if not animal_alvo or animal_alvo.onde_esta != 'curral':
            return jsonify({'sucesso': False, 'erro': 'Animal não encontrado no tronco!'})
        animais_disponiveis = [animal_alvo]
        quantidade = 1 # Força quantidade 1 para venda individual
    else:
        # VENDA EM LOTE: Busca pela raça dentro do curral da fazenda
        animais_disponiveis = Animal.query.join(Lote).filter(
            Lote.fazenda_id == fazenda_id,
            Animal.raca == raca.capitalize() if raca else None,
            Animal.onde_esta == 'curral'
        ).limit(quantidade).all()
    
    # --- VALIDAÇÕES ---
    if len(animais_disponiveis) < quantidade:
        return jsonify({'sucesso': False, 'erro': f'Quantidade insuficiente! Você só tem {len(animais_disponiveis)} disponíveis.'})
    
    if preco <= 0:
        return jsonify({'sucesso': False, 'erro': 'O preço deve ser maior que zero!'})

    # --- EXECUÇÃO DO ANÚNCIO ---
    try:
        for animal in animais_disponiveis:
            animal.onde_esta = 'venda' # Remove do curral para o estado de "venda"
            novo_anuncio = Anuncio(
                vendedor_id=u.id,
                animal_id=animal.id,
                valor=preco
            )
            db.session.add(novo_anuncio)
        
        db.session.commit()
        return jsonify({'sucesso': True, 'msg': f'{len(animais_disponiveis)}x {raca} anunciados no Mercado Global!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'sucesso': False, 'erro': f'Erro no banco: {str(e)}'})

@app.route('/api/mercado/comprar_leilao', methods=['POST'])
def comprar_leilao():
    if 'user_id' not in session:
        return jsonify({'sucesso': False, 'erro': 'Sessão expirada'})
    
    comprador = db.session.get(Usuario, session['user_id'])
    dados = request.get_json()
    
    anuncio_id = dados.get('anuncio_id')
    qtd_desejada = int(dados.get('quantidade', 1))
    id_fazenda_destino = dados.get('fazenda_id') # Recebe a fazenda escolhida no modal

    # 1. Busca o anúncio e valida se ainda existe
    anuncio = Anuncio.query.get(anuncio_id)
    if not anuncio or getattr(anuncio, 'vendido', False):
        return jsonify({'sucesso': False, 'erro': 'Este animal já foi vendido ou o anúncio expirou.'})

    vendedor = db.session.get(Usuario, anuncio.vendedor_id)
    valor_total = anuncio.valor * qtd_desejada

    # 2. Valida o saldo do comprador
    if comprador.dinheiro < valor_total:
        return jsonify({'sucesso': False, 'erro': f'Saldo insuficiente! Você precisa de R$ {valor_total:,.2f}'})

    # 3. TRANSFERÊNCIA FINANCEIRA
    comprador.dinheiro -= valor_total
    vendedor.dinheiro += valor_total

    # 4. REGISTRO NO FINANCEIRO (Para aparecer no Fluxo de Caixa)
    registrar_transacao(comprador, f"Compra Leilão: {anuncio.animal.raca}", -valor_total, "compra")
    registrar_transacao(vendedor, f"Venda Leilão: {anuncio.animal.raca}", valor_total, "venda")

    # 5. TRANSFERÊNCIA DO ANIMAL PARA O COMPRADOR
    # Busca o primeiro lote da fazenda que o comprador escolheu
    fazenda_destino = next((f for f in comprador.fazendas if f.id == id_fazenda_destino), comprador.fazendas[0])
    
    animal = anuncio.animal
    animal.lote_id = fazenda_destino.lotes[0].id # Muda o dono do animal
    animal.onde_esta = 'curral' # Coloca o animal no curral do novo dono
    
    # Marca o anúncio como vendido para ele sumir do mercado
    db.session.delete(anuncio) 
    
    db.session.commit()
    return jsonify({
        'sucesso': True, 
        'msg': f'Sucesso! R$ {valor_total:,.2f} pagos. O animal já está no seu curral!'
    })

# --- ADICIONE ISSO PARA MATAR O FANTASMA NO PYTHON ---
@app.after_request
def add_header(response):
    # Proíbe o navegador de guardar versões antigas da página (mata o fantasma)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response
if __name__ == '__main__':
    with app.app_context(): criar_mundo()
    app.run(debug=True, host='0.0.0.0', port=5000)
