import json
from datetime import datetime, timezone
import os

KEYS_FILE = 'keys.json'

def desativar_expiradas():
    """Desativa keys que já passaram da data de expiração"""
    
    # Verifica se o arquivo existe
    if not os.path.exists(KEYS_FILE):
        print(f"❌ Arquivo {KEYS_FILE} não encontrado!")
        print(f"📁 Diretório atual: {os.getcwd()}")
        print(f"📁 Arquivos: {os.listdir('.')}")
        return
    
    # Carrega o arquivo
    with open(KEYS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    now = datetime.now(timezone.utc)
    modificado = False
    
    # Verifica cada key
    for key in data.get('keys', []):
        if key.get('active', True) and key.get('expires_at'):
            try:
                # Converte a data de expiração
                expires_at = key['expires_at']
                if expires_at is not None:
                    expires_at = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
                    
                    # Se expirou, desativa
                    if now > expires_at:
                        key['active'] = False
                        key['desativado_em'] = now.isoformat()
                        print(f"🔴 Key desativada: {key['key']}")
                        modificado = True
            except Exception as e:
                print(f"⚠️ Erro ao processar key {key.get('key', 'unknown')}: {e}")
    
    # Salva se houve mudança
    if modificado:
        with open(KEYS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print("✅ Keys atualizadas com sucesso!")
    else:
        print("ℹ️ Nenhuma key expirada encontrada.")

if __name__ == "__main__":
    desativar_expiradas()
