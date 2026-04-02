import os
import re

# Directorios a procesar
dirs_to_fix = [
    'tucajero/services',
    'tucajero/repositories', 
    'tucajero/ui',
    'tucajero/utils',
    'tucajero/security',
    'tucajero/config',
    'tucajero/app',
]

# Patrones de reemplazo
replacements = [
    (r'from models\.', 'from tucajero.models.'),
    (r'from repositories\.', 'from tucajero.repositories.'),
    (r'from services\.', 'from tucajero.services.'),
    (r'from ui\.', 'from tucajero.ui.'),
    (r'from utils\.', 'from tucajero.utils.'),
    (r'from security\.', 'from tucajero.security.'),
    (r'from config\.', 'from tucajero.config.'),
    (r'from database\.', 'from tucajero.database.'),
    (r'from app\.', 'from tucajero.app.'),
    (r'from domain\.', 'from tucajero.domain.'),
]

total_files = 0
total_replacements = 0

for dir_path in dirs_to_fix:
    full_dir = os.path.join('tucajero', dir_path)
    if not os.path.exists(full_dir):
        continue
        
    for root, dirs, files in os.walk(full_dir):
        for file in files:
            if not file.endswith('.py'):
                continue
            
            filepath = os.path.join(root, file)
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original = content
                
                for pattern, replacement in replacements:
                    content = re.sub(pattern, replacement, content)
                
                if content != original:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    total_files += 1
                    changes = (original.count('from models.') - content.count('from models.')) + \
                              (original.count('from repositories.') - content.count('from tucajero.repositories.')) + \
                              (original.count('from services.') - content.count('from tucajero.services.')) + \
                              (original.count('from ui.') - content.count('from tucajero.ui.')) + \
                              (original.count('from utils.') - content.count('from tucajero.utils.')) + \
                              (original.count('from security.') - content.count('from tucajero.security.')) + \
                              (original.count('from config.') - content.count('from tucajero.config.'))
                    total_replacements += changes
                    print(f'  ✓ {filepath}')
                    
            except Exception as e:
                print(f'  ✗ {filepath}: {e}')

print(f'\n✅ {total_files} archivos actualizados, {total_replacements} imports corregidos')
