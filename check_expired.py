import json
from datetime import datetime, timezone
import os

KEYS_FILE = 'keys.json'

def desativar_expiradas():
    # Verifica se o arquivo existe
    if not os.path.exists(KEYS_FILE):
        print(f"❌ Arquivo {KEYS_FILE} não encontrado")
        return
    
    with open(KEYS_FILE, 'r') as f:
        data = json.load(f)
    
    now = datetime.now(timezone.utc)
    modificado = False
    
    for key in data['keys']:
        if key.get('active', True) and key.get('expires_at'):
            try:
                expires_at = datetime.fromisoformat(key['expires_at'].replace('Z', '+00:00'))
                if now > expires_at:
                    key['active'] = False
                    key['desativado_em'] = now.isoformat()
                    print(f"🔴 Key desativada: {key['key']} (expirada em {key['expires_at']})")
                    modificado = True
            except Exception as e:
                print(f"⚠️ Erro ao processar key {key.get('key', 'unknown')}: {e}")
    
    if modificado:
        with open(KEYS_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        print("✅ Keys atualizadas com sucesso!")
    else:
        print("ℹ️ Nenhuma key expirada encontrada.")

if __name__ == "__main__":
    desativar_expiradas()
