import subprocess
import os
from pathlib import Path

def make_commit():
    try:
        # Determina a pasta atual utilizando o caminho da linha de comando ou diretório atual.
        current_dir = os.getcwd() if '.' not in sys.argv else Path(sys.argv[1].lstrip('/\\').split(os.sep)[0])
        
        # Identifica todos os ficheiros e diretórios que foram modificados recentemente (última modificação).
        modified_files = [str(p) for p in Path(current_dir).rglob('*') if p.is_file() and p.stat().st_mtime > 0]
        tracked_dirs = [str(p) for p in Path(current_dir).iterdir() if (not p.name.startswith('.') or '.git' not in str(p)) and p.is_dir()]
        
        # Combina as modificações rastreadas pelo Git com os ficheiros modificados recentemente.
        all_to_commit = set(modified_files + [f for d in tracked_dirs if d.name != '.'])
        
        # Verifica se existem alterações a serem adicionadas ao commit e realiza o commit se necessário.
        if list(all_to_commit):
            result = subprocess.run([
                'git', 'add', *[p for p in Path('.').rglob('*') if not (Path(p).is_dir() or str(p) == '.')]
            ], capture_output=True)
            commit_message = "Código atualizado e pronto para o push"
        else:
            commit_message = ""
        
        subprocess.run([
            'git', 'commit', f' -m', commit_message,
            '-m', 'Auto commit das alterações recentes'
        ], check=False)
    except Exception as e:
        print(f"Erro ao executar o comando git: {e}")