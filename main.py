import discord
import json
import os
import datetime

from config import DISCORD_BOT_TOKEN

# --- Configuração do Bot ---
intents = discord.Intents.default()
intents.members = True 

bot = discord.Bot(intents=intents)

# Nome do arquivo que vai armazenar os dados dos ninjas
DATA_FILE = "ninjas.json"

# Mapa de Emojis para o comando de resumo
EMOJI_MAP = {
    "katon": "🔥",
    "suiton": "💧",
    "fuuton": "🌪️",
    "doton": "🗿",
    "raiton": "⚡"
}

# --- Funções de Gerenciamento de Dados ---

def carregar_dados():
    """Carrega os dados dos ninjas do arquivo JSON."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

def salvar_dados(dados):
    """Salva os dados dos ninjas no arquivo JSON."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4)

# --- Eventos do Bot ---

@bot.event
async def on_ready():
    """Função que é chamada quando o bot está online e pronto."""
    print(f'Bot conectado como {bot.user}')
    print('Bot online com sistema de múltiplos elementos!')
    print('-' * 20)

# --- NOVO Comando de Elementos ---

@bot.slash_command(name="elementos", description="Registra ou atualiza um ninja com uma lista de elementos.")
async def elementos(
    ctx: discord.ApplicationContext, 
    dados: discord.Option(str, "O primeiro nome é o do ninja, o resto são seus elementos. Ex: Naruto Fuuton Katon")
):
    """Registra um ninja com uma lista de elementos e salva o timestamp."""
    try:
        partes = dados.split()
        if len(partes) < 2:
            await ctx.respond("❗️ **Formato inválido.** Forneça o nome do ninja e pelo menos um elemento.", ephemeral=True)
            return
            
        nome_ninja = partes[0]
        lista_elementos = [elem.lower() for elem in partes[1:]]  # Normaliza para minúsculas
        
        elementos_validos = set(EMOJI_MAP.keys())
        for elem in lista_elementos:
            if elem not in elementos_validos:
                elementos_formatados_validos = ', '.join([e.title() for e in elementos_validos])
                await ctx.respond(f"❗️ **Elemento inválido:** {elem.title()}.\nElementos válidos são: {elementos_formatados_validos}", ephemeral=True)
                return
    except Exception as e:
        await ctx.respond(f"❗️ **Ocorreu um erro ao processar sua entrada:** {e}", ephemeral=True)
        return

    db_ninjas = carregar_dados()
    
    if nome_ninja not in db_ninjas:
        db_ninjas[nome_ninja] = {}
        
    # Pega o timestamp atual
    timestamp = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
    
    # Salva a lista de elementos E o timestamp da atualização
    db_ninjas[nome_ninja]["elementos"] = lista_elementos
    db_ninjas[nome_ninja]["updated_at"] = timestamp
    
    salvar_dados(db_ninjas)

    elementos_formatados = ", ".join([elem.title() for elem in lista_elementos])
    await ctx.respond(f"✅ O ninja **{nome_ninja}** foi registrado/atualizado com os elementos: **{elementos_formatados}**.\n*Última atualização: <t:{timestamp}:R>*")

@bot.slash_command(name="check", description="Verifica os elementos e status de um ninja específico.")
async def check(
    ctx: discord.ApplicationContext,
    nome: discord.Option(str, "O nome do ninja que você quer verificar.")
):
    """Verifica e exibe os dados de um ninja."""
    
    db_ninjas = carregar_dados()
    
    # Verifica se o ninja existe no banco de dados
    if nome not in db_ninjas:
        await ctx.respond(f"❌ Ninja **{nome}** não encontrado no banco de dados.", ephemeral=True)
        return
        
    # Pega os dados do ninja
    info_ninja = db_ninjas[nome]
    
    # Cria o embed da resposta
    embed = discord.Embed(
        title=f"📜 Ficha do Ninja: {nome} 📜",
        color=discord.Color.blue()
    )
    
    # Pega a lista de elementos ou uma lista vazia se não houver
    lista_elementos = info_ninja.get('elementos', [])
    
    if not lista_elementos:
        elementos_str = "Nenhum elemento registrado."
    else:
        # Formata a lista de elementos com emojis
        elementos_formatados = []
        for elem in lista_elementos:
            emoji = EMOJI_MAP.get(elem, "❔")
            elementos_formatados.append(f"{emoji} {elem.title()}")
        elementos_str = "\n".join(elementos_formatados)
        
    embed.add_field(name="🌀 Elementos", value=elementos_str, inline=False)
    
    # Pega o timestamp da última atualização
    timestamp = info_ninja.get('updated_at')
    
    if timestamp:
        # Formata o timestamp para exibição no Discord
        atualizacao_str = f"<t:{timestamp}:F> (<t:{timestamp}:R>)"
        embed.add_field(name="⏳ Última Atualização dos Elementos", value=atualizacao_str, inline=False)
        
    await ctx.respond(embed=embed)

# --- Comando de Resumo (Adaptado para a nova estrutura) ---

@bot.slash_command(name="resumo", description="📋 Mostra um resumo da contagem de ninjas por status.")
async def resumo(ctx: discord.ApplicationContext):
    ninjas = carregar_dados()
    if not ninjas:
        await ctx.respond("Nenhum ninja foi registrado ainda.")
        return

    contagem_elementos = {}

    for info in ninjas.values():
        # Loop através da LISTA de elementos de cada ninja
        for elemento in info.get('elementos', []): # .get com [] para ninjas sem elemento
            if elemento not in contagem_elementos:
                # Busca o emoji no mapa que criamos no topo do arquivo
                emoji = EMOJI_MAP.get(elemento, '❔')
                contagem_elementos[elemento] = {'count': 0, 'emoji': emoji}
            contagem_elementos[elemento]['count'] += 1

    embed = discord.Embed(
        title="📊 Resumo de Status dos Ninjas 📊",
        description="Contagem total de ninjas e ocorrências de elementos.",
        color=discord.Color.from_rgb(70, 130, 180)
    )

    resumo_elementos_str = ""
    if not contagem_elementos:
        resumo_elementos_str = "Nenhum elemento registrado."
    else:
        for elemento, data in sorted(contagem_elementos.items()):
            resumo_elementos_str += f"{data['emoji']} **{elemento.title()}**: {data['count']}\n"
    
    embed.add_field(name="Ocorrências de Elementos", value=resumo_elementos_str, inline=True)

    embed.set_footer(text=f"Total de {len(ninjas)} ninjas cadastrados.")
    await ctx.respond(embed=embed)


# --- Comando de Rotação  ---

@bot.slash_command(name="rotacao", description="Calcula o dano de uma rotação golpe a golpe para derrotar um inimigo.")
async def rotacao(
    ctx: discord.ApplicationContext, 
    dados: discord.Option(str, "Danos da rotação e, por último, a vida do inimigo. Ex: 100 50 200 1500")
):
    try:
        numeros = [int(n) for n in dados.split()]
        if len(numeros) < 2:
            await ctx.respond("❗️ **Formato inválido.**", ephemeral=True)
            return
        danos_individuais = numeros[:-1]
        hp_inicial = numeros[-1]
        dano_por_rotacao = sum(danos_individuais)
    except ValueError:
        await ctx.respond("❗️ **Erro.** Por favor, insira apenas números.", ephemeral=True)
        return

    if dano_por_rotacao <= 0:
        await ctx.respond(f"🤔 O inimigo nunca será derrotado.", ephemeral=True)
        return
    if hp_inicial <= 0:
        await ctx.respond("✅ O inimigo já foi derrotado!", ephemeral=True)
        return

    hp_atual = hp_inicial
    contagem_rotacoes = 0
    log_batalha = []
    continuar_batalha = True
    while continuar_batalha:
        contagem_rotacoes += 1
        log_batalha.append(f"**🌀 Iniciando Rotação {contagem_rotacoes}**")
        for i, dano in enumerate(danos_individuais):
            hp_antes_do_golpe = hp_atual
            hp_atual -= dano
            hp_final_do_golpe = max(0, hp_atual)
            log_batalha.append(f" ┕ 🗡️ Golpe {i+1} ({dano} dano): {hp_antes_do_golpe} HP ➔ **{hp_final_do_golpe} HP**")
            if hp_atual <= 0:
                continuar_batalha = False
                break
    
    embed = discord.Embed(title="⚔️ Simulação de Dano (Golpe a Golpe) ⚔️", color=discord.Color.gold())
    embed.add_field(name="📊 Dados Iniciais", value=f"**HP do Inimigo:** {hp_inicial}\n**Dano Total por Rotação:** {dano_por_rotacao}", inline=False)
    embed.add_field(name="🏁 Resultado Final", value=f"O inimigo foi derrotado na **Rotação {contagem_rotacoes}**.", inline=False)
    
    log_parcial = ""
    titulo_campo = "📜 Log da Batalha 📜"
    for linha in log_batalha:
        linha_formatada = linha + "\n"
        if len(log_parcial) + len(linha_formatada) > 1024:
            embed.add_field(name=titulo_campo, value=f"```\n{log_parcial}```", inline=False)
            log_parcial = ""
            titulo_campo = "📜 Log da Batalha (continuação) 📜"
        log_parcial += linha_formatada
    if log_parcial:
        embed.add_field(name=titulo_campo, value=f"```\n{log_parcial}```", inline=False)
        
    await ctx.respond(embed=embed)


# --- Execução do Bot ---
try:
    bot.run(DISCORD_BOT_TOKEN)
except discord.errors.LoginFailure:
    print("ERRO: Token inválido. Verifique se o token no código está correto.")
except Exception as e:
    print(f"Ocorreu um erro ao tentar iniciar o bot: {e}")