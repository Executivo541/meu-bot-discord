import os
import random
import threading
import discord
from discord import app_commands
from dotenv import load_dotenv
from flask import Flask # Nova biblioteca para enganar o Render

# --- CONFIGURAÇÃO WEB PARA MANTER O BOT ALIVE ---
app = Flask('')

@app.route('/')
def home():
    return "Bot Atlas Hub está online 24/7!"

def run_web():
    # O Render exige que usemos a porta que eles fornecem ou a 8080 padrão
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def manter_vivo():
    t = threading.Thread(target=run_web)
    t.start()
# ------------------------------------------------

# Carrega o token do arquivo .env
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True 

class Client(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.banco_moedas = {}

    async def on_ready(self):
        print(f'Logado como {self.user}!')
        try:
            synced = await self.tree.sync()
            print(f"Sincronizados {len(synced)} comandos de barra!")
        except Exception as e:
            print(f"Erro ao sincronizar comandos: {e}")

client = Client()

# --- COMANDOS DE UTILIDADE & MODERAÇÃO ---

@client.tree.command(name="ola", description="O bot vai te dar um oi profissional!")
async def ola(interaction: discord.Interaction):
    await interaction.response.send_message(f"Olá, {interaction.user.mention}! Esse é um comando de barra oficial! 🚀")

@client.tree.command(name="ping", description="Mostra o tempo de resposta do bot")
async def ping(interaction: discord.Interaction):
    latencia = round(client.latency * 1000)
    await interaction.response.send_message(f"🏓 Pong! Latência: {latencia}ms")

@client.tree.command(name="avatar", description="Mostra o avatar (foto de perfil) de um usuário")
@app_commands.describe(usuario="Selecione o usuário para ver a foto")
async def avatar(interaction: discord.Interaction, usuario: discord.User = None):
    usuario = usuario or interaction.user
    embed = discord.Embed(title=f"📸 Avatar de {usuario.name}", color=discord.Color.blue())
    embed.set_image(url=usuario.display_avatar.url)
    await interaction.response.send_message(embed=embed)

@client.tree.command(name="serverinfo", description="Mostra informações detalhadas sobre este servidor")
async def serverinfo(interaction: discord.Interaction):
    guild = interaction.guild
    embed = discord.Embed(title=f"📊 Informações de {guild.name}", color=discord.Color.green())
    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
    embed.add_field(name="Dono", value=guild.owner.mention if guild.owner else "Não disponível", inline=True)
    embed.add_field(name="Membros", value=str(guild.member_count), inline=True)
    embed.add_field(name="Criação", value=guild.created_at.strftime("%d/%m/%Y"), inline=True)
    await interaction.response.send_message(embed=embed)

@client.tree.command(name="limpar", description="Apaga um número específico de mensagens no chat")
@app_commands.describe(quantidade="Quantas mensagens você quer apagar?")
async def limpar(interaction: discord.Interaction, quantidade: int):
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message("❌ Você não tem permissão para gerenciar mensagens!", ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True)
    deletadas = await interaction.channel.purge(limit=quantidade)
    await interaction.followup.send(f"🧹 Faxina concluída! {len(deletadas)} mensagens foram apagadas.")

# --- COMANDOS DE INTERAÇÃO & MINIJOGO ---

@client.tree.command(name="userinfo", description="Mostra detalhes e curiosidades sobre a conta de um membro")
@app_commands.describe(membro="Escolha o membro (deixe em branco para ver o seu)")
async def userinfo(interaction: discord.Interaction, membro: discord.Member = None):
    membro = membro or interaction.user
    cargos = [cargo.mention for cargo in membro.roles if cargo.name != "@everyone"]
    lista_cargos = ", ".join(cargos) if cargos else "Nenhum cargo"
    embed = discord.Embed(title=f"👤 Perfil de {membro.name}", color=membro.color)
    embed.set_thumbnail(url=membro.display_avatar.url)
    embed.add_field(name="Tag do Usuário", value=f"`{membro}`", inline=True)
    embed.add_field(name="ID", value=f"`{membro.id}`", inline=True)
    embed.add_field(name="Conta Criada em", value=membro.created_at.strftime("%d/%m/%Y às %H:%M"), inline=False)
    embed.add_field(name="Entrou no Servidor em", value=membro.joined_at.strftime("%d/%m/%Y às %H:%M"), inline=False)
    embed.add_field(name=f"Cargos ({len(cargos)})", value=lista_cargos, inline=False)
    await interaction.response.send_message(embed=embed)

@client.tree.command(name="trabalhar", description="Trabalhe duro para ganhar moedas Atlas!")
async def trabalhar(interaction: discord.Interaction):
    user_id = interaction.user.id
    if user_id not in client.banco_moedas:
        client.banco_moedas[user_id] = 0
    ganho = random.randint(50, 200)
    client.banco_moedas[user_id] += ganho
    respostas_trabalho = [
        f"Você trabalhou como programador e ganhou **{ganho}** moedas! 💻",
        f"Você vendeu coxinha no servidor e lucrou **{ganho}** moedas! 🍗",
        f"Você farmou monstros de madrugada e conseguiu **{ganho}** moedas! ⚔️",
        f"Você ajudou a moderar o chat e ganhou um bônus de **{ganho}** moedas! 🛡️"
    ]
    msg = random.choice(respostas_trabalho)
    await interaction.response.send_message(f"{interaction.user.mention} {msg}\nSaldo atual: **{client.banco_moedas[user_id]}** moedas.")

@client.tree.command(name="carteira", description="Veja quantas moedas você possui no momento")
async def carteira(interaction: discord.Interaction):
    user_id = interaction.user.id
    saldo = client.banco_moedas.get(user_id, 0)
    await interaction.response.send_message(f"💰 {interaction.user.mention}, você tem atualmente **{saldo}** moedas Atlas na sua conta.")

@client.tree.command(name="apostar", description="Aposte suas moedas no cara ou coroa para tentar dobrar!")
@app_commands.describe(opcao="Escolha entre Cara ou Coroa", valor="Quantidade de moedas para apostar")
@app_commands.choices(opcao=[
    app_commands.Choice(name="Cara", value="cara"),
    app_commands.Choice(name="Coroa", value="coroa")
])
async def apostar(interaction: discord.Interaction, opcao: app_commands.Choice[str], valor: int):
    user_id = interaction.user.id
    saldo_atual = client.banco_moedas.get(user_id, 0)
    if valor <= 0:
        await interaction.response.send_message("❌ Você precisa apostar um valor maior que 0!", ephemeral=True)
        return
    if saldo_atual < valor:
        await interaction.response.send_message(f"❌ Você não tem moedas suficientes! Seu saldo é de **{saldo_atual}** moedas.", ephemeral=True)
        return
    resultado_sorteio = random.choice(["cara", "coroa"])
    if opcao.value == resultado_sorteio:
        client.banco_moedas[user_id] += valor
        await interaction.response.send_message(f"🎉 Deu **{resultado_sorteio.upper()}**! Você acertou e ganhou **{valor}** moedas!\nSaldo atual: **{client.banco_moedas[user_id]}** moedas.")
    else:
        client.banco_moedas[user_id] -= valor
        await interaction.response.send_message(f"😭 Deu **{resultado_sorteio.upper()}**... Você errou e perdeu **{valor}** moedas.\nSaldo atual: **{client.banco_moedas[user_id]}** moedas.")

# Liga o servidor web e depois o bot
manter_vivo()
client.run(TOKEN)