import re
import pandas as pd
import get_voices

def parse_script_from_text(script_text, character_mapping):
    data = []
    current_character = None
    
    for line in script_text.split("\n"):
        line = line.strip()
        
        # Ignorar linhas vazias
        if not line:
            continue
        
        # Identificar o personagem no início da linha
        match = re.match(r'^(VAR[A-Za-z0-9]+):\s*(.*)', line)
        if match:
            character = match.group(1)
            text = match.group(2)
            
            # Atualizar o personagem atual
            current_character = character
            
            # Obter o nome real do personagem (ex: VARNarrador → Michael)
            real_name = character_mapping.get(character, "Unknown")
            accent, alias = get_voices.get_voice_info(real_name)
            
            # Armazenar dados
            data.append([character, real_name, text, accent, alias])
        
        # Se for continuação do mesmo personagem
        elif current_character:
            real_name = character_mapping.get(current_character, "Unknown")
            accent, alias = get_voices.get_voice_info(real_name)
            data.append([current_character, real_name, line, accent, alias])
    
    # Criar DataFrame
    df = pd.DataFrame(data, columns=["Character", "Real Name", "Line", "Accent", "Voice Alias"])
    return df


# # Exemplo de uso
# script_text = """
# VARNarrador: A manhã estava quente e o mar, selvagem.
# VARPersona03: Sim, mas olha aqueles corais… Se cairmos errado, podemos nos machucar feio.
# VARPersona01: Cara, olha isso! As ondas estão insanas hoje!
# VARNarrador: disse Jake, com os olhos brilhando de excitação.
# VARPersona02: Sim, mas olha aqueles corais… Se cairmos errado, podemos nos machucar feio.
# """

# character_mapping = {
#     "VARNarrador": "Michael",
#     "VARPersona01": "Fernanda",
#     "VARPersona02": "Gabriel",
#     "VARPersona03": "JUlio"
# }

# df_script = parse_script_from_text(script_text, character_mapping)

# # Print results
# print(df_script)
