import os
import random
import threading
import discord
import datetime
from discord import app_commands
from dotenv import load_dotenv
from flask import Flask

# --- CONFIGURAÇÃO WEB ---
app = Flask('')
@app.route('/')
def home(): return "Bot Atlas Hub está online 24/7!"
def run_web(): app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
def manter_vivo(): threading.Thread(target=run_web).start()

# --- BOT SETUP ---
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

    async def setup_hook(self):
        # Sincroniza os comandos uma única vez ao iniciar
        await self.tree.sync()
        print("Comandos sincronizados!")

    async def on_ready(self):
        print(f'Logado como {self.user}!')

client = Client()

# --- COMANDOS ---
@client.tree.command(name="ola", description="Oi profissional")
async def ola(interaction: discord.Interaction): await interaction.response.send_message(f"Olá, {interaction.user.mention}!")

@client.tree.command(name="ping", description="Latência")
async def ping(interaction: discord.Interaction): await interaction.response.send_message(f"🏓 {round(client.latency * 1000)}ms")

@client.tree.command(name="serverinfo", description="Info do servidor")
async def serverinfo(interaction: discord.Interaction):
    guild = interaction.guild
    embed = discord.Embed(title=f"📊 {guild.name}", color=discord.Color.purple(), timestamp=interaction.created_at)
    embed.add_field(name="Dono", value=guild.owner.mention, inline=True)
    embed.add_field(name="Membros", value=f"{guild.member_count}", inline=True)
    await interaction.response.send_message(embed=embed)

@client.tree.command(name="embed", description="Cria um aviso personalizado")
async def embed(interaction: discord.Interaction, titulo: str, descricao: str):
    embed_msg = discord.Embed(title=titulo, description=descricao, color=discord.Color.blue())
    await interaction.response.send_message(embed=embed_msg)

@client.tree.command(name="limpar", description="Apaga mensagens")
async def limpar(interaction: discord.Interaction, quantidade: int):
    await interaction.response.defer(ephemeral=True)
    deletadas = await interaction.channel.purge(limit=quantidade)
    await interaction.followup.send(f"🧹 {len(deletadas)} apagadas.")

@client.tree.command(name="banir", description="Bane um membro")
async def banir(interaction: discord.Interaction, membro: discord.Member, motivo: str = "Sem motivo"):
    await membro.ban(reason=motivo)
    await interaction.response.send_message(f"🔨 {membro.name} banido.")

@client.tree.command(name="mutar", description="Muta um membro")
async def mutar(interaction: discord.Interaction, membro: discord.Member, minutos: int):
    await membro.timeout(datetime.timedelta(minutes=minutos))
    await interaction.response.send_message(f"🔇 {membro.name} mutado por {minutos} min.")

@client.tree.command(name="trabalhar", description="Ganhe moedas")
async def trabalhar(interaction: discord.Interaction):
    ganho = random.randint(50, 200)
    await interaction.response.send_message(f"💼 Ganhou {ganho} moedas!")

# --- INICIALIZAÇÃO ---
if __name__ == "__main__":
    manter_vivo()
    client.run(TOKEN)
