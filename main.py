import discord
import json
import os

from config import DISCORD_BOT_TOKEN

# --- Configuração do Bot ---
intents = discord.Intents.default()
intents.members = True 

bot = discord.Bot(intents=intents)

# Nome do arquivo que vai armazenar os dados dos ninjas
DATA_FILE = "ninjas.json"

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
    print('Bot online e com todas as funcionalidades prontas!')
    print('-' * 20)

# --- Comandos de Elemento (LÓGICA ATUALIZADA) ---

async def registrar_elemento(ctx: discord.ApplicationContext, nome: str, elemento: str, emoji: str):
    """
    Função auxiliar para registrar um elemento.
    CRIA o ninja se ele não existir, ou ATUALIZA se ele já existir.
    """
    dados = carregar_dados()
    
    # Garante que o ninja exista no dicionário (padrão "get or create")
    if nome not in dados:
        dados[nome] = {}
        
    # Adiciona ou atualiza as informações do elemento
    dados[nome]['elemento'] = elemento
    dados[nome]['emoji'] = emoji
    
    salvar_dados(dados)
    await ctx.respond(f"{emoji} O ninja **{nome}** agora possui o elemento **{elemento}**!")

@bot.slash_command(name="katon", description="🔥 Registra um nome de ninja com o elemento Fogo.")
async def katon(ctx: discord.ApplicationContext, nome: discord.Option(str, "Digite o nome do ninja a ser registrado.")):
    await registrar_elemento(ctx, nome, "Katon", "🔥")

@bot.slash_command(name="suiton", description="💧 Registra um nome de ninja com o elemento Água.")
async def suiton(ctx: discord.ApplicationContext, nome: discord.Option(str, "Digite o nome do ninja a ser registrado.")):
    await registrar_elemento(ctx, nome, "Suiton", "💧")

@bot.slash_command(name="fuuton", description="🌪️ Registra um nome de ninja com o elemento Vento.")
async def fuuton(ctx: discord.ApplicationContext, nome: discord.Option(str, "Digite o nome do ninja a ser registrado.")):
    await registrar_elemento(ctx, nome, "Fuuton", "🌪️")

@bot.slash_command(name="doton", description="🗿 Registra um nome de ninja com o elemento Terra.")
async def doton(ctx: discord.ApplicationContext, nome: discord.Option(str, "Digite o nome do ninja a ser registrado.")):
    await registrar_elemento(ctx, nome, "Doton", "🗿")

@bot.slash_command(name="raiton", description="⚡ Registra um nome de ninja com o elemento Raio.")
async def raiton(ctx: discord.ApplicationContext, nome: discord.Option(str, "Digite o nome do ninja a ser registrado.")):
    await registrar_elemento(ctx, nome, "Raiton", "⚡")

# --- Comandos de Selo (LÓGICA ATUALIZADA) ---

async def atualizar_selo(ctx: discord.ApplicationContext, nome: str, status_selo: bool):
    """
    Função auxiliar para aplicar ou remover o debuff de selo.
    CRIA o ninja se ele não existir, ou ATUALIZA se ele já existir.
    """
    dados = carregar_dados()
    
    # Garante que o ninja exista no dicionário (padrão "get or create")
    if nome not in dados:
        dados[nome] = {}
        
    # Adiciona ou atualiza o status do selo
    dados[nome]['debuff_de_selo'] = status_selo
    salvar_dados(dados)
    
    if status_selo:
        await ctx.respond(f"🔒 O ninja **{nome}** agora está **com** o debuff de selo.")
    else:
        await ctx.respond(f"🔓 O ninja **{nome}** agora está **sem** o debuff de selo.")

@bot.slash_command(name="selo", description="🔒 Aplica o debuff de selo em um ninja (cria o ninja se não existir).")
async def selo(ctx: discord.ApplicationContext, nome: discord.Option(str, "O nome do ninja que receberá o debuff.")):
    await atualizar_selo(ctx, nome, True)

@bot.slash_command(name="semselo", description="🔓 Remove o debuff de selo de um ninja (cria o ninja se não existir).")
async def semselo(ctx: discord.ApplicationContext, nome: discord.Option(str, "O nome do ninja que terá o debuff removido.")):
    await atualizar_selo(ctx, nome, False)

# --- Comando de Resumo Simplificado (sem alterações) ---

@bot.slash_command(name="resumo", description="📋 Mostra um resumo da contagem de ninjas por status.")
async def resumo(ctx: discord.ApplicationContext):
    ninjas = carregar_dados()
    if not ninjas:
        await ctx.respond("Nenhum ninja foi registrado ainda.")
        return

    contagem_elementos = {}
    ninjas_selados = 0
    ninjas_sem_selo = 0

    for info in ninjas.values():
        elemento = info.get('elemento', 'Sem Elemento')
        emoji = info.get('emoji', '❔')
        if elemento not in contagem_elementos:
            contagem_elementos[elemento] = {'count': 0, 'emoji': emoji}
        contagem_elementos[elemento]['count'] += 1
        
        if info.get('debuff_de_selo', False):
            ninjas_selados += 1
        else:
            ninjas_sem_selo += 1

    embed = discord.Embed(
        title="📊 Resumo de Status dos Ninjas 📊",
        description="Contagem total de ninjas por elemento e status de selo.",
        color=discord.Color.from_rgb(70, 130, 180)
    )

    resumo_elementos_str = ""
    for elemento, data in sorted(contagem_elementos.items()):
        resumo_elementos_str += f"{data['emoji']} **{elemento}**: {data['count']}\n"
    if resumo_elementos_str:
        embed.add_field(name="Contagem por Elemento", value=resumo_elementos_str, inline=True)
    
    resumo_selos_str = f"🔒 **Com debuff de Selo:** {ninjas_selados}\n🔓 **Sem debuff de Selo:** {ninjas_sem_selo}"
    embed.add_field(name="Status de Selo", value=resumo_selos_str, inline=True)

    embed.set_footer(text=f"Total de {len(ninjas)} ninjas cadastrados.")
    await ctx.respond(embed=embed)

# --- Comando de Rotação (sem alterações) ---

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