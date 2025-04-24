import os
import srt
from datetime import timedelta
import whisper
from pydub import AudioSegment
import uuid

def extrair_numero(nome_arquivo):
    """Extrai o número antes do primeiro underscore (_) para ordenação correta."""
    try:
        return int(nome_arquivo.split("_")[0])
    except ValueError:
        return float("inf")  # Caso não tenha número, joga para o final

def unir_audios_em_ordem():
    pasta_audios = 'audios/temp'
    
    # Obtém a lista de arquivos e ordena corretamente pelo número inicial
    arquivos = sorted(
        [f for f in os.listdir(pasta_audios) if f.endswith((".wav", ".mp3"))],
        key=extrair_numero
    )
    
    if not arquivos:
        print("Nenhum arquivo de áudio encontrado na pasta.")
        return
    
    # Inicializa o áudio final vazio
    audio_final = AudioSegment.empty()
    
    # Concatena os áudios
    for arquivo in arquivos:
        caminho_completo = os.path.join(pasta_audios, arquivo)
        print(caminho_completo)
        audio = AudioSegment.from_file(caminho_completo)
        audio_final += audio

    # Exporta o áudio final
    caminho_saida = f'audios/{str(uuid.uuid4())}.wav'
    audio_final.export(caminho_saida, format="wav")
    print(f"Áudio final exportado para: {caminho_saida}")


def make_subtitle(audio_file, output_srt_file):
    # Verifica se o arquivo de áudio existe
    if not os.path.exists(audio_file):
        print(f"Arquivo {audio_file} não encontrado!")
        return

    # Carrega o modelo do Whisper
    model = whisper.load_model("turbo")

    try:
        # Transcreve o áudio
        result = model.transcribe(audio_file, verbose=False)
        subtitles = []

        # Cria legendas com base nos segmentos
        for i, segment in enumerate(result['segments']):
            start = segment['start']
            end = segment['end']
            text = segment['text'].strip()

            subtitle = srt.Subtitle(
                index=i + 1,
                start=timedelta(seconds=start),
                end=timedelta(seconds=end),
                content=text
            )
            subtitles.append(subtitle)

        # Salvar o arquivo SRT
        with open(output_srt_file, "w", encoding="utf-8") as f:
            f.write(srt.compose(subtitles))

        #print(f"Legendas salvas em: {output_srt_file}")

    except Exception as e:
        print(f"Erro durante a transcrição: {str(e)}")


# audio_file = "audios/40fd9e6f-409c-42c0-94b9-e09c558f332c.wav"
# output_srt_file = f"videos/video_{audio_file.replace('audios/', '').replace(".wav", "")}_TESTE.srt"
# make_subtitle(audio_file, output_srt_file)
#unir_audios_em_ordem()