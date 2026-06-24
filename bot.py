import os
import random
import threading
import discord
from discord import app_commands
from dotenv import load_dotenv
from flask import Flask

# --- CONFIGURAÇÃO WEB PARA MANTER O BOT ALIVE ---
app = Flask('')

@app.route('/')
def home():
    return "Bot Atlas Hub está online 24/7!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def manter_vivo():
    t = threading.Thread(target=run_web)
    t.start()

# --- CONFIGURAÇÃO DO BOT ---
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

# --- COMANDOS DE UTILIDADE ---

@client.tree.command(name="ola", description="O bot vai te dar um oi profissional!")
async def ola(interaction: discord.Interaction):
    await interaction.response.send_message(f"Olá, {interaction.user.mention}! Estou operacional e pronto para ajudar! 🚀")

@client.tree.command(name="ping", description="Mostra a latência do bot")
async def ping(interaction: discord.Interaction):
    latencia = round(client.latency * 1000)
    await interaction.response.send_message(f"🏓 Pong! Latência atual: {latencia}ms")

@client.tree.command(name="serverinfo", description="Mostra informações detalhadas do servidor")
async def serverinfo(interaction: discord.Interaction):
    guild = interaction.guild
    embed = discord.Embed(title=f"📊 Informações: {guild.name}", color=discord.Color.purple(), timestamp=interaction.created_at)
    embed.set_author(name=interaction.user.name, icon_url=interaction.user.display_avatar.url)
    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
    embed.add_field(name="👑 Dono", value=guild.owner.mention, inline=True)
    embed.add_field(name="👥 Membros", value=f"{guild.member_count}", inline=True)
    embed.add_field(name="📅 Criado em", value=guild.created_at.strftime("%d/%m/%Y"), inline=False)
    embed.set_footer(text="Atlas Hub | Sistema de Monitoramento")
    await interaction.response.send_message(embed=embed)

@client.tree.command(name="userinfo", description="Perfil de um membro")
async def userinfo(interaction: discord.Interaction, membro: discord.Member = None):
    membro = membro or interaction.user
    embed = discord.Embed(title=f"👤 Perfil de {membro.name}", color=membro.color, timestamp=interaction.created_at)
    embed.set_thumbnail(url=membro.display_avatar.url)
    embed.add_field(name="ID", value=f"`{membro.id}`", inline=True)
    embed.add_field(name="Entrou em", value=membro.joined_at.strftime("%d/%m/%Y"), inline=True)
    embed.set_footer(text="Atlas Hub | Dados de Usuário")
    await interaction.response.send_message(embed=embed)

# --- COMANDOS DE ECONOMIA ---

@client.tree.command(name="trabalhar", description="Ganhe moedas Atlas!")
async def trabalhar(interaction: discord.Interaction):
    user_id = interaction.user.id
    if user_id not in client.banco_moedas: client.banco_moedas[user_id] = 0
    ganho = random.randint(50, 200)
    client.banco_moedas[user_id] += ganho
    await interaction.response.send_message(f"💼 Você trabalhou e ganhou **{ganho}** moedas! Saldo: **{client.banco_moedas[user_id]}**.")

# --- INICIALIZAÇÃO ---
manter_vivo()
client.run(TOKEN)