# ================================================================
# EVIL EYES KEY SYSTEM (VERSÃO CORRIGIDA)
# ================================================================

import discord
from discord.ext import commands
import json
import os
import random
import string
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS
import threading

# ================================================================
# CONFIGURAÇÃO
# ================================================================

TOKEN = 'MTUyMjI1MDkwNjQyMTI5NzI1Mg.Gbb2PQ.yujSH0PKAmqoUzmAq1217O0KJvOAUhUNsWpBME'  # COLOQUE SEU TOKEN AQUI
KEYS_FILE = 'keys.json'
PORT = 3000

# ================================================================
# BANCO DE DADOS
# ================================================================

def load_keys():
    try:
        with open(KEYS_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_keys(keys):
    with open(KEYS_FILE, 'w') as f:
        json.dump(keys, f, indent=2)

def generate_key():
    chars = string.ascii_uppercase + string.digits
    key = 'EYE-'
    for i in range(3):
        for j in range(4):
            key += random.choice(chars)
        if i < 2:
            key += '-'
    return key

# ================================================================
# DISCORD BOT
# ================================================================

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'🤖 Bot {bot.user} conectado!')

@bot.command(name='gerar')
@commands.has_permissions(administrator=True)
async def gerar(ctx, usuario: discord.Member, dias: int):
    if dias < 1 or dias > 365:
        await ctx.send('❌ Dias inválidos. (1 a 365)')
        return

    keys = load_keys()
    key = generate_key()
    now = datetime.now()
    expires = now + timedelta(days=dias)

    keys[key] = {
        'discordId': usuario.id,
        'userName': usuario.name,
        'createdBy': ctx.author.name,
        'createdAt': now.isoformat(),
        'expiresAt': expires.isoformat(),
        'status': 'active'
    }

    save_keys(keys)

    embed = discord.Embed(
        title='🔑 Key Gerada!',
        description=f'`{key}`',
        color=0x00ff41
    )
    embed.add_field(name='👤 Usuário', value=usuario.name, inline=True)
    embed.add_field(name='⏰ Validade', value=f'{dias} dias', inline=True)

    await ctx.send(embed=embed)
    await ctx.send(f'🔐 **Key:** `{key}`')

@bot.command(name='keys')
@commands.has_permissions(administrator=True)
async def listar_keys(ctx):
    keys = load_keys()
    ativas = {k: v for k, v in keys.items() if v.get('status') == 'active'}

    if not ativas:
        await ctx.send('📭 Nenhuma Key ativa.')
        return

    lista = '🔑 **Keys Ativas:**\n\n'
    for key, data in ativas.items():
        expires = datetime.fromisoformat(data['expiresAt'])
        days_left = (expires - datetime.now()).days
        lista += f'`{key}` → {data["userName"]} ({days_left} dias restantes)\n'

    await ctx.send(lista)

@bot.command(name='revogar')
@commands.has_permissions(administrator=True)
async def revogar(ctx, key: str):
    keys = load_keys()
    if key not in keys:
        await ctx.send('❌ Key não encontrada.')
        return

    keys[key]['status'] = 'revoked'
    save_keys(keys)
    await ctx.send(f'✅ Key `{key}` revogada.')

@bot.command(name='status')
async def verificar_status(ctx, key: str):
    keys = load_keys()
    if key not in keys:
        await ctx.send('❌ Key não encontrada.')
        return

    data = keys[key]
    expires = datetime.fromisoformat(data['expiresAt'])
    now = datetime.now()
    is_valid = data['status'] == 'active' and expires > now

    embed = discord.Embed(
        title='✅ Válida' if is_valid else '❌ Inválida',
        color=0x00ff41 if is_valid else 0xff4444
    )
    embed.add_field(name='🔑 Key', value=f'`{key}`')
    embed.add_field(name='👤 Usuário', value=data['userName'], inline=True)
    embed.add_field(name='📅 Expira', value=expires.strftime('%d/%m/%Y %H:%M'), inline=True)
    embed.add_field(name='📌 Status', value=data['status'], inline=True)

    await ctx.send(embed=embed)

@bot.command(name='ajuda')
async def ajuda(ctx):
    embed = discord.Embed(
        title='🤖 Evil Eyes - Key System',
        description='Comandos disponíveis:',
        color=0x00ff41
    )
    embed.add_field(name='!gerar @usuario dias', value='Gera uma Key', inline=False)
    embed.add_field(name='!keys', value='Lista Keys ativas', inline=False)
    embed.add_field(name='!revogar KEY', value='Revoga uma Key', inline=False)
    embed.add_field(name='!status KEY', value='Verifica status', inline=False)

    await ctx.send(embed=embed)

# ================================================================
# API FLASK (CORRIGIDA)
# ================================================================

app = Flask(__name__)
CORS(app, origins='*')  # Libera CORS para qualquer origem

@app.route('/')
def home():
    return 'Evil Eyes API rodando! ✅'

@app.route('/verify', methods=['POST'])
def verify_key():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'valid': False, 'message': 'Requisição inválida'})

        key = data.get('key')
        if not key:
            return jsonify({'valid': False, 'message': 'Key não fornecida'})

        keys = load_keys()
        if key not in keys:
            return jsonify({'valid': False, 'message': 'Key não encontrada'})

        info = keys[key]
        expires = datetime.fromisoformat(info['expiresAt'])
        now = datetime.now()

        if info['status'] != 'active':
            return jsonify({'valid': False, 'message': 'Key revogada'})

        if expires < now:
            return jsonify({'valid': False, 'message': 'Key expirada'})

        days_left = (expires - now).days

        return jsonify({
            'valid': True,
            'user': info['userName'],
            'expiresAt': info['expiresAt'],
            'daysLeft': days_left
        })

    except Exception as e:
        return jsonify({'valid': False, 'message': f'Erro: {str(e)}'})

def run_flask():
    app.run(host='0.0.0.0', port=PORT, debug=False)

# ================================================================
# INICIA TUDO
# ================================================================

if __name__ == '__main__':
    # Inicia a API em uma thread separada
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    print(f'🌐 API rodando na porta {PORT}')  # <<< LINHA IMPORTANTE
    bot.run(TOKEN)