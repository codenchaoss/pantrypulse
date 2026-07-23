import os
import glob

provider_files = glob.glob('app/llm/providers/*_provider.py')
for file in provider_files:
    with open(file, 'r') as f:
        content = f.read()
    
    new_content = content.replace('timeout=2.5', 'timeout=5.0')
    
    with open(file, 'w') as f:
        f.write(new_content)
    
print('Updated timeout in all providers.')
