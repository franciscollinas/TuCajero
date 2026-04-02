import os
import re

# Todos los directorios de tucajero
all_dirs = [
    'tucajero',
    'tucajero/ui',
    'tucajero/services',
    'tucajero/repositories',
    'tucajero/models',
    'tucajero/utils',
    'tucajero/security',
    'tucajero/config',
    'tucajero/database',
    'tucajero/app',
    'tucajero/app/ui',
    'tucajero/app/ui/views',
    'tucajero/app/ui/theme',
    'tucajero/tools',
]

# Patrones de reemplazo - el orden importa
replacements = [
    ('from models.', 'from tucajero.models.'),
    ('from repositories.', 'from tucajero.repositories.'),
    ('from services.', 'from tucajero.services.'),
    ('from ui.', 'from tucajero.ui.'),
    ('from utils.', 'from tucajero.utils.'),
    ('from security.', 'from tucajero.security.'),
    ('from config.', 'from tucajero.config.'),
    ('from database.', 'from tucajero.database.'),
    ('from app.', 'from tucajero.app.'),
    ('from domain.', 'from tucajero.domain.'),
    ('from tools.', 'from tucajero.tools.'),
]

total_files = 0
total_changes = 0

for dir_path in all_dirs:
    if not os.path.exists(dir_path):
        continue
    
    for root, dirs, files in os.walk(dir_path):
        # Skip __pycache__
        if '__pycache__' in root:
            continue
            
        for file in files:
            if not file.endswith('.py'):
                continue
            
            filepath = os.path.join(root, file)
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    original = f.read()
                
                content = original
                
                for old, new in replacements:
                    # Solo reemplazar si no tiene ya 'tucajero.'
                    if f'from {old[5:]}' in content and f'from tucajero.{old[5:]}' not in content:
                        content = content.replace(old, new)
                
                if content != original:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    total_files += 1
                    total_changes += 1
                    print(f'  ✓ {filepath}')
                    
            except Exception as e:
                print(f'  ✗ {filepath}: {e}')

print(f'\n✅ {total_files} archivos actualizados')
