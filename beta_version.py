import sys
import uuid
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QTextEdit, QTabWidget, QComboBox, QRadioButton, QButtonGroup, QWidget, QApplication
from kokoro import KPipeline
import soundfile as sf
import numpy as np
import re
import os
from PySide6.QtCore import QUrl
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
import generate_srt
import make_movie
import preparescript
import shutil
import get_voices
import time


GLOBAL_TTS_AMERICAN = None
GLOBAL_TTS_BRITISH = None
GLOBAL_TTS_SPANISH = None
GLOBAL_TTS_FRENCH = None
GLOBAL_TTS_HINDI = None
GLOBAL_TTS_ITALIAN = None
GLOBAL_TTS_BRAZILIAN = None
GLOBAL_TTS_JAPANESE = None
GLOBAL_TTS_MANDARIM = None


def html_help_content():
    file_path = 'help.html'
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()
        return html_content
    except FileNotFoundError:
        return "<h1>Error: File not found</h1>"
    except Exception as e:
        return f"<h1>Error: {str(e)}</h1>"

def get_tts_model(accent):
    global GLOBAL_TTS_AMERICAN, GLOBAL_TTS_BRITISH, GLOBAL_TTS_SPANISH
    global GLOBAL_TTS_FRENCH, GLOBAL_TTS_HINDI, GLOBAL_TTS_ITALIAN
    global GLOBAL_TTS_BRAZILIAN, GLOBAL_TTS_JAPANESE, GLOBAL_TTS_MANDARIM
    
    if accent == "American":
        if GLOBAL_TTS_AMERICAN is None:
            print("Carregando modelo TTS para: American")
            GLOBAL_TTS_AMERICAN = KPipeline(lang_code='a', repo_id='hexgrad/Kokoro-82M')
        return GLOBAL_TTS_AMERICAN

    elif accent == "British":
        if GLOBAL_TTS_BRITISH is None:
            print("Carregando modelo TTS para: British")
            GLOBAL_TTS_BRITISH = KPipeline(lang_code='b', repo_id='hexgrad/Kokoro-82M')
        return GLOBAL_TTS_BRITISH

    elif accent == "Spanish":
        if GLOBAL_TTS_SPANISH is None:
            print("Carregando modelo TTS para: Spanish")
            GLOBAL_TTS_SPANISH = KPipeline(lang_code='e', repo_id='hexgrad/Kokoro-82M')
        return GLOBAL_TTS_SPANISH

    elif accent == "French":
        if GLOBAL_TTS_FRENCH is None:
            print("Carregando modelo TTS para: French")
            GLOBAL_TTS_FRENCH = KPipeline(lang_code='f', repo_id='hexgrad/Kokoro-82M')
        return GLOBAL_TTS_FRENCH

    elif accent == "Hindi":
        if GLOBAL_TTS_HINDI is None:
            print("Carregando modelo TTS para: Hindi")
            GLOBAL_TTS_HINDI = KPipeline(lang_code='h', repo_id='hexgrad/Kokoro-82M')
        return GLOBAL_TTS_HINDI

    elif accent == "Italian":
        if GLOBAL_TTS_ITALIAN is None:
            print("Carregando modelo TTS para: Italian")
            GLOBAL_TTS_ITALIAN = KPipeline(lang_code='i', repo_id='hexgrad/Kokoro-82M')
        return GLOBAL_TTS_ITALIAN

    elif accent == "Brazilian":
        if GLOBAL_TTS_BRAZILIAN is None:
            print("Carregando modelo TTS para: Brazilian")
            GLOBAL_TTS_BRAZILIAN = KPipeline(lang_code='p', repo_id='hexgrad/Kokoro-82M')
        return GLOBAL_TTS_BRAZILIAN

    elif accent == "Japanese":
        if GLOBAL_TTS_JAPANESE is None:
            print("Carregando modelo TTS para: Japanese")
            GLOBAL_TTS_JAPANESE = KPipeline(lang_code='j', repo_id='hexgrad/Kokoro-82M')
        return GLOBAL_TTS_JAPANESE

    elif accent == "Mandarin":
        if GLOBAL_TTS_MANDARIM is None:
            print("Carregando modelo TTS para: Mandarin")
            GLOBAL_TTS_MANDARIM = KPipeline(lang_code='z', repo_id='hexgrad/Kokoro-82M')
        return GLOBAL_TTS_MANDARIM

    else:
        raise ValueError(f"Acento desconhecido: {accent}")

def transform_filtered_list_text(text_to_speech):
    text_to_speech = text_to_speech.replace('"', ",").replace("'", "")
    split_regex = r'(?<!\d)[,.;:\n](?!\d)'
    text_parts = re.split(split_regex, text_to_speech)

    filtered_parts = []
    for item in text_parts:
        if item.strip() or item == "\n":
            filtered_parts.append(item)
    text_parts = filtered_parts   

    new_list = []
    for i in range(len(text_parts)):

        part_01 = text_parts[i]

        if len(new_list) == 0:
            new_list.append(part_01)
        
        else:
            last = new_list[-1]

            if last == '.' and part_01 == '.':
                new_list.append(part_01)

            elif (last == '.' and part_01 == '\n') or (last == ',' and part_01 == '\n') or (last == '\n' and part_01 == '\n'):
                new_list.pop()
                new_list.append(part_01)
                
            else:
                new_list.append(part_01)
    return new_list

def make_audio(text_to_speech, output_file,
               speed_value, pause_duration_paragraphs,
               pause_duration_commas, pause_duration_periods,
               accent, alias):
    
    global GLOBAL_TTS_AMERICAN, GLOBAL_TTS_BRITISH, GLOBAL_TTS_SPANISH
    global GLOBAL_TTS_FRENCH, GLOBAL_TTS_HINDI, GLOBAL_TTS_ITALIAN
    global GLOBAL_TTS_BRAZILIAN, GLOBAL_TTS_JAPANESE, GLOBAL_TTS_MANDARIM
    
    tts_model = get_tts_model(accent)

    # Criar dicionário com os tempos de pausa (convertidos para amostras)
    pause_times = {
        ",": int(pause_duration_commas * 24000),
        ";": int(pause_duration_commas * 24000),
        ":": int(pause_duration_commas * 24000),
        ".": int(pause_duration_periods * 24000),
        "\n": int(pause_duration_paragraphs * 24000)
    }

    text_parts = transform_filtered_list_text(text_to_speech)

    audio_clips = []
    for part in text_parts:
        if part in pause_times:
            pause_samples = pause_times[part]
            audio_clips.append(np.zeros(pause_samples, dtype=np.float32))
        else:
            generator = tts_model(part, voice=alias, speed=speed_value)
            for _, _, audio in generator:
                audio_clips.append(audio)

    # Concatenando o áudio final
    final_audio = np.concatenate(audio_clips)
    sf.write(output_file, final_audio, 24000)

class AudioWorker(QThread):

    progress = Signal(str)
    finished = Signal()

    def __init__(self, text_to_speech, 
                 speed_value, pause_duration_paragraphs,
                 pause_duration_commas, pause_duration_periods,
                 accent, alias, id):
    
        super().__init__()
        self.text_to_speech = text_to_speech
        
        self.speed_value = speed_value
        self.pause_duration_paragraphs = pause_duration_paragraphs
        self.pause_duration_commas = pause_duration_commas
        self.pause_duration_periods = pause_duration_periods

        self.accent = accent
        self.alias = alias
        self.id = id

    def run(self):
        output_file = f'audios/temp/{self.id}_{str(uuid.uuid4())}.wav'
        make_audio(
            self.text_to_speech,
            output_file,

            self.speed_value,
            self.pause_duration_paragraphs,
            self.pause_duration_commas,    
            self.pause_duration_periods,

            self.accent,
            self.alias  
        )

        self.finished.emit()

class SubtitleWorker(QThread):
    progress = Signal(str)
    finished = Signal()

    def __init__(self, latest_audio):
        super().__init__()
        self.latest_audio = latest_audio

    def run(self):

        latest_audio_name = self.latest_audio.replace('audios/', '').replace('.wav', '')
        folder = f"videos/{latest_audio_name}"
        if not os.path.exists(folder):
            os.makedirs(folder)
        
        output_srt_file = f"videos/{latest_audio_name}/{latest_audio_name}.srt"
        self.progress.emit("Starting generate subtitles")
        try:
            if self.latest_audio is not None:
                generate_srt.make_subtitle(self.latest_audio, output_srt_file)
            else:
                self.progress.emit("No audio file found.")
        except Exception as e:
            self.progress.emit(f"Error: {str(e)}")

        self.progress.emit(f"Subtitles save on: {output_srt_file}")
        self.finished.emit()

class VideoWorker(QThread):
    progress = Signal(str)
    finished = Signal()

    def __init__(self, latest_audio):
        super().__init__()
        self.latest_audio = latest_audio

    def run(self):
        latest_audio_name = self.latest_audio.replace('audios/', '').replace('.wav', '')
        
        folder = f"videos/{latest_audio_name}"
        if not os.path.exists(folder):
            os.makedirs(folder)

        srt_file = f"{folder}/{latest_audio_name}.srt"
        output_video_file = f"{folder}/{latest_audio_name}.mp4"

        try:
            if self.latest_audio is not None:
                make_movie.create_black_background_video(self.latest_audio, srt_file, output_video_file)
                self.progress.emit(f"Video saved on: {output_video_file}")
            else:
                self.progress.emit("No audio file found.")
        except Exception as e:
            self.progress.emit(f"Error: {str(e)}")
        
        self.finished.emit()

class TtsApp(QWidget):

    def __init__(self):
        super().__init__()

        # Tamanho da janela e título
        self.setWindowTitle("TTS StoryTeller")
        self.resize(800, 800)
        
        # Layout principal com abas
        self.tabs = QTabWidget(self)
        
        # Aba "Geração de Cards"
        self.generation_tab = QWidget()
        self.generation_layout = QVBoxLayout()
        self.setup_generation_tab()
        self.generation_tab.setLayout(self.generation_layout)
        
        # Aba "Ajuda"
        self.help_tab = QWidget()
        self.help_layout = QVBoxLayout()
        self.setup_help_tab()
        self.help_tab.setLayout(self.help_layout)

        # Layout final da janela
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)

        # Add tabs
        self.tabs.addTab(self.generation_tab, "TTS Engine")
        self.tabs.addTab(self.help_tab, "Help")

        # Inicializar o player de áudio
        self.audio_output_dir = "audios"
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)

    def setup_generation_tab(self):
        # Adicionar um espaço superior
        self.generation_layout.addSpacing(20)
        voices_avaible = get_voices.get_avaible_voices()

        # Inputs de configuração do Narrador
        space_between_persona = 20
        
        # Narrador
        layout_narrador = QHBoxLayout()
        label_narrador = QLabel("Narrador:")
        self.var_narrator = QComboBox(self)
        self.var_narrator.addItems(voices_avaible)
        layout_narrador.addWidget(label_narrador)
        layout_narrador.addWidget(self.var_narrator)
        self.generation_layout.addLayout(layout_narrador)

        layout_narrador_inputs = QHBoxLayout()
        layout_narrador_inputs.addWidget(QLabel("Speed:"))
        self.speed_narrador = QLineEdit(self)
        self.speed_narrador.setText("1.0")
        layout_narrador_inputs.addWidget(self.speed_narrador)

        layout_narrador_inputs.addWidget(QLabel("Paragraph:"))
        self.pause_paragraphs_narrador = QLineEdit(self)
        self.pause_paragraphs_narrador.setText("1.2")
        layout_narrador_inputs.addWidget(self.pause_paragraphs_narrador)

        layout_narrador_inputs.addWidget(QLabel("Comma:"))
        self.pause_commas_narrador = QLineEdit(self)
        self.pause_commas_narrador.setText("0.8")
        layout_narrador_inputs.addWidget(self.pause_commas_narrador)

        layout_narrador_inputs.addWidget(QLabel("Period:"))
        self.pause_periods_narrador = QLineEdit(self)
        self.pause_periods_narrador.setText("1")
        layout_narrador_inputs.addWidget(self.pause_periods_narrador)

        self.generation_layout.addLayout(layout_narrador_inputs)
        self.generation_layout.addSpacing(space_between_persona)

        # Inputs de configuração da Persona 01
        layout_persona_01 = QHBoxLayout()
        label_persona_01 = QLabel("Persona 01:")
        self.var_persona_01 = QComboBox(self)
        self.var_persona_01.addItems(voices_avaible)
        layout_persona_01.addWidget(label_persona_01)
        layout_persona_01.addWidget(self.var_persona_01)
        self.generation_layout.addLayout(layout_persona_01)

        layout_persona01_inputs = QHBoxLayout()
        layout_persona01_inputs.addWidget(QLabel("Speed:"))
        self.speed_persona01 = QLineEdit(self)
        self.speed_persona01.setText("1.0")
        layout_persona01_inputs.addWidget(self.speed_persona01)

        layout_persona01_inputs.addWidget(QLabel("Paragraph:"))
        self.pause_paragraphs_persona01 = QLineEdit(self)
        self.pause_paragraphs_persona01.setText("1.2")
        layout_persona01_inputs.addWidget(self.pause_paragraphs_persona01)

        layout_persona01_inputs.addWidget(QLabel("Comma:"))
        self.pause_commas_persona01 = QLineEdit(self)
        self.pause_commas_persona01.setText("0.8")
        layout_persona01_inputs.addWidget(self.pause_commas_persona01)

        layout_persona01_inputs.addWidget(QLabel("Period:"))
        self.pause_periods_persona01 = QLineEdit(self)
        self.pause_periods_persona01.setText("1")
        layout_persona01_inputs.addWidget(self.pause_periods_persona01)

        self.generation_layout.addLayout(layout_persona01_inputs)
        self.generation_layout.addSpacing(space_between_persona)
        
        # Inputs de configuração da Persona 02
        layout_persona_02 = QHBoxLayout()
        label_persona_02 = QLabel("Persona 02:")
        self.var_persona_02 = QComboBox(self)
        self.var_persona_02.addItems(voices_avaible)
        layout_persona_02.addWidget(label_persona_02)
        layout_persona_02.addWidget(self.var_persona_02)
        self.generation_layout.addLayout(layout_persona_02)
        
        layout_persona02_inputs = QHBoxLayout()
        layout_persona02_inputs.addWidget(QLabel("Speed:"))
        self.speed_persona02 = QLineEdit(self)
        self.speed_persona02.setText("1.0")
        layout_persona02_inputs.addWidget(self.speed_persona02)

        layout_persona02_inputs.addWidget(QLabel("Paragraph:"))
        self.pause_paragraphs_persona02 = QLineEdit(self)
        self.pause_paragraphs_persona02.setText("1.2")
        layout_persona02_inputs.addWidget(self.pause_paragraphs_persona02)

        layout_persona02_inputs.addWidget(QLabel("Comma:"))
        self.pause_commas_persona02 = QLineEdit(self)
        self.pause_commas_persona02.setText("0.8")
        layout_persona02_inputs.addWidget(self.pause_commas_persona02)

        layout_persona02_inputs.addWidget(QLabel("Period:"))
        self.pause_periods_persona02 = QLineEdit(self)
        self.pause_periods_persona02.setText("1")
        layout_persona02_inputs.addWidget(self.pause_periods_persona02)

        self.generation_layout.addLayout(layout_persona02_inputs)
        self.generation_layout.addSpacing(space_between_persona)

        # Inputs de configuração da Persona 03
        layout_persona_03 = QHBoxLayout()
        label_persona_03 = QLabel("Persona 03:")
        self.var_persona_03 = QComboBox(self)
        self.var_persona_03.addItems(voices_avaible)
        layout_persona_03.addWidget(label_persona_03)
        layout_persona_03.addWidget(self.var_persona_03)
        self.generation_layout.addLayout(layout_persona_03)

        layout_persona03_inputs = QHBoxLayout()
        layout_persona03_inputs.addWidget(QLabel("Speed:"))
        self.speed_persona03 = QLineEdit(self)
        self.speed_persona03.setText("1.0")
        layout_persona03_inputs.addWidget(self.speed_persona03)

        layout_persona03_inputs.addWidget(QLabel("Paragraph:"))
        self.pause_paragraphs_persona03 = QLineEdit(self)
        self.pause_paragraphs_persona03.setText("1.2")
        layout_persona03_inputs.addWidget(self.pause_paragraphs_persona03)

        layout_persona03_inputs.addWidget(QLabel("Comma:"))
        self.pause_commas_persona03 = QLineEdit(self)
        self.pause_commas_persona03.setText("0.8")
        layout_persona03_inputs.addWidget(self.pause_commas_persona03)

        layout_persona03_inputs.addWidget(QLabel("Period:"))
        self.pause_periods_persona03 = QLineEdit(self)
        self.pause_periods_persona03.setText("1")
        layout_persona03_inputs.addWidget(self.pause_periods_persona03)

        self.generation_layout.addLayout(layout_persona03_inputs)
        self.generation_layout.addSpacing(space_between_persona)
        
        # Campo de entrada de texto
        self.text_input_label = QLabel("Enter your text:")
        self.text_input = QTextEdit(self) 
        self.text_input.setPlaceholderText("Type or paste your text here...")
        self.text_input.setMinimumHeight(150)
        
        self.generation_layout.addWidget(self.text_input_label)
        self.generation_layout.addWidget(self.text_input)

        # Campo de Log/Feedback
        self.log_output = QTextEdit(self)
        self.log_output.setReadOnly(True)
        self.log_output.setStyleSheet("background-color: #f5f5f5; padding: 10px; font-family: Arial; font-size: 12px; color: #333333;")
        self.log_output.setMaximumHeight(80) 
        self.generation_layout.addWidget(self.log_output)

        self.generate_audio_button = QPushButton("Generate Audio", self)
        self.generate_audio_button.clicked.connect(self.generate_audio)

        self.clear_button_logs = QPushButton("Clear Logs", self)
        self.clear_button_logs.clicked.connect(self.clear_logs)

        self.play_audio_button = QPushButton("Play Latest Audio", self)
        self.play_audio_button.clicked.connect(self.play_latest_audio)

        self.generate_subtitles_button = QPushButton("Subtitle Generation for latest Audio", self)
        self.generate_subtitles_button.clicked.connect(self.genenare_subtitles)
        
        self.generate_video_button = QPushButton("Video Generation for latest Audio", self)
        self.generate_video_button.clicked.connect(self.genenare_video)

        # Layout para os botões
        button_layout = QVBoxLayout()
        button_layout.addWidget(self.generate_audio_button)
        button_layout.addWidget(self.clear_button_logs)
        button_layout.addWidget(self.play_audio_button)
        button_layout.addWidget(self.generate_subtitles_button)
        button_layout.addWidget(self.generate_video_button)

        self.generation_layout.addLayout(button_layout)
        
    def genenare_subtitles(self):
        self.generate_subtitles_button.setEnabled(False)
        latest_audio = self.get_latest_file()
        self.subtitle_worker = SubtitleWorker(latest_audio)
        self.subtitle_worker.progress.connect(self.log_output.append)
        self.subtitle_worker.finished.connect(lambda: self.generate_subtitles_button.setEnabled(True))
        self.subtitle_worker.start()
    
    def genenare_video(self):
        try:
            latest_audio = self.get_latest_file()
            if latest_audio != None:

                folder = f"videos/{str(latest_audio.replace('audios/', '').replace(".wav", ""))}"

                if not os.path.exists(folder):
                    os.makedirs(folder)
                    return None
    
                srt_file = f"{folder}/{latest_audio.replace('audios/', '').replace(".wav", "")}.srt"

                if not os.path.exists(srt_file):
                    self.log_output.append("Generating the srt file firts...")
                    self.genenare_subtitles()
                else:
                    self.generate_video_button.setEnabled(False)
                    latest_audio = self.get_latest_file()
                    self.video_worker = VideoWorker(latest_audio)
                    self.video_worker.progress.connect(self.log_output.append)
                    self.video_worker.finished.connect(lambda: self.generate_video_button.setEnabled(True))
                    self.video_worker.start()
            
        except Exception as e:
            self.log_output.append(f"Error: {e}")

    def generate_audio(self):

        self.audio_already_merged = False 
        pasta ='audios/temp'
        try:
            shutil.rmtree(pasta)
        except:
            pass
    
        os.mkdir(pasta)
        time.sleep(2)
        

        # Desabilita o botão para evitar múltiplas execuções
        self.generate_audio_button.setEnabled(False)  
        script_text = self.text_input.toPlainText()
        
        narrador = self.var_narrator.currentText().split(' ', 1)[1]
        persona01 = self.var_persona_01.currentText().split(' ', 1)[1]
        persona02 = self.var_persona_02.currentText().split(' ', 1)[1]
        persona03 = self.var_persona_03.currentText().split(' ', 1)[1]
    
        personas_settings = {
            narrador: {
                "speed": float(self.speed_narrador.text()),
                "pause_paragraphs": float(self.pause_paragraphs_narrador.text()),
                "pause_commas": float(self.pause_commas_narrador.text()),
                "pause_periods": float(self.pause_periods_narrador.text())
            },
            persona01: {
                "speed": float(self.speed_persona01.text()),
                "pause_paragraphs": float(self.pause_paragraphs_persona01.text()),
                "pause_commas": float(self.pause_commas_persona01.text()),
                "pause_periods": float(self.pause_periods_persona01.text())
            },
            persona02: {
                "speed": float(self.speed_persona02.text()),
                "pause_paragraphs": float(self.pause_paragraphs_persona02.text()),
                "pause_commas": float(self.pause_commas_persona02.text()),
                "pause_periods": float(self.pause_periods_persona02.text())
            },
            persona03: {
                "speed": float(self.speed_persona03.text()),
                "pause_paragraphs": float(self.pause_paragraphs_persona03.text()),
                "pause_commas": float(self.pause_commas_persona03.text()),
                "pause_periods": float(self.pause_periods_persona03.text())
            }
        }

        character_mapping = {
            "VARNarrator": narrador,
            "VARPersona01": persona01,
            "VARPersona02": persona02,
            "VARPersona03": persona03
        }
        self.df_script = preparescript.parse_script_from_text(script_text, character_mapping)
        print(self.df_script)

        
        # Atualizando modelos necessários para esse dataframe
        self.atualizar_modelos()
        self.log_output.append("Starting genarate audios...")

        self.audio_workers = [] 
        id = 1
        for index, row in self.df_script.iterrows():
            character = row['Character']
            text = row['Line']
            accent = row['Accent']
            alias = row['Voice Alias']

            settings = personas_settings.get(character, {
                "speed": 1.0,
                "pause_paragraphs": 1,
                "pause_commas": 0.3,
                "pause_periods": 0.7
            })

            speed_value = settings["speed"]
            pause_duration_paragraphs = settings["pause_paragraphs"]
            pause_duration_commas = settings["pause_commas"]
            pause_duration_periods = settings["pause_periods"]

            worker = AudioWorker(
                text,
                speed_value,
                pause_duration_paragraphs,
                pause_duration_commas,      
                pause_duration_periods,
                accent,
                alias,
                id
            )
            worker.finished.connect(lambda: self.check_all_workers_finished()) 
            self.audio_workers.append(worker)
            worker.start()
            id += 1
        
    def check_all_workers_finished(self):
        """
        Verifica se todas as threads de áudio (workers) terminaram.
        Se sim, habilita o botão e chama a função que une os áudios.
        """
        
        # Verifica se TODAS as threads terminaram
        todas_finalizadas = all(worker.isFinished() for worker in self.audio_workers)

        # Só executa se todas finalizaram E ainda não foi feito o merge
        if todas_finalizadas and not self.audio_already_merged:
            self.audio_already_merged = True 
            self.generate_audio_button.setEnabled(True) 
            generate_srt.unir_audios_em_ordem()

            audio_path = self.get_latest_file()
            self.log_output.append(f"Work Finished! Audio save on: {audio_path}")

    def atualizar_modelos(self):

        global GLOBAL_TTS_AMERICAN, GLOBAL_TTS_BRITISH, GLOBAL_TTS_SPANISH
        global GLOBAL_TTS_FRENCH, GLOBAL_TTS_HINDI, GLOBAL_TTS_ITALIAN
        global GLOBAL_TTS_BRAZILIAN, GLOBAL_TTS_JAPANESE, GLOBAL_TTS_MANDARIM
        
        list_accent = []
        for index, row in self.df_script.iterrows():
        
            accent = row['Accent']

            if accent not in list_accent:
                list_accent.append(accent)
                
                if accent == "American":
                    if GLOBAL_TTS_AMERICAN is None:
                        GLOBAL_TTS_AMERICAN = KPipeline(lang_code='a', repo_id='hexgrad/Kokoro-82M')

                elif accent == "British":
                    if GLOBAL_TTS_BRITISH is None:
                        GLOBAL_TTS_BRITISH = KPipeline(lang_code='b', repo_id='hexgrad/Kokoro-82M')

                elif accent == "Spanish":
                    if GLOBAL_TTS_SPANISH is None:
                        GLOBAL_TTS_SPANISH = KPipeline(lang_code='e', repo_id='hexgrad/Kokoro-82M')

                elif accent == "French":
                    if GLOBAL_TTS_FRENCH is None:
                        GLOBAL_TTS_FRENCH = KPipeline(lang_code='f', repo_id='hexgrad/Kokoro-82M')

                elif accent == "Hindi":
                    if GLOBAL_TTS_HINDI is None:
                        GLOBAL_TTS_HINDI = KPipeline(lang_code='h', repo_id='hexgrad/Kokoro-82M')

                elif accent == "Italian":
                    if GLOBAL_TTS_ITALIAN is None:
                        GLOBAL_TTS_ITALIAN = KPipeline(lang_code='i', repo_id='hexgrad/Kokoro-82M')
        
                elif accent == "Brazilian":
                    if GLOBAL_TTS_BRAZILIAN is None:
                        GLOBAL_TTS_BRAZILIAN = KPipeline(lang_code='p', repo_id='hexgrad/Kokoro-82M')

                elif accent == "Japanese":
                    if GLOBAL_TTS_JAPANESE is None:
                        GLOBAL_TTS_JAPANESE = KPipeline(lang_code='j', repo_id='hexgrad/Kokoro-82M')
                elif accent == "Mandarin":
                    if GLOBAL_TTS_MANDARIM is None:
                        GLOBAL_TTS_MANDARIM = KPipeline(lang_code='z', repo_id='hexgrad/Kokoro-82M')
                else:
                    raise ValueError(f"Acento desconhecido: {accent}")
                
                self.log_output.append(f"Loading tts model: {accent}" )

    def clear_logs(self):
        self.log_output.clear()

    def setup_help_tab(self):
        self.help_text = QTextEdit(self)
        self.help_text.setReadOnly(True) 
        self.help_text.setAlignment(Qt.AlignLeft)
        help_content = html_help_content()
        self.help_text.setHtml(help_content)
        self.help_layout.addWidget(self.help_text)
    
    def get_latest_file(self):
        """Retorna o caminho do arquivo de áudio mais recente."""
        try:
            # Criar diretório se não existir
            if not os.path.exists(self.audio_output_dir):
                os.makedirs(self.audio_output_dir)
                return None

            # Lista todos os arquivos de áudio do diretório (MP3 e WAV)
            files = [os.path.join(self.audio_output_dir, f) for f in os.listdir(self.audio_output_dir)
                     if f.endswith(('.mp3', '.wav')) and os.path.isfile(os.path.join(self.audio_output_dir, f))]

            if not files:
                return None

            # Retorna o arquivo mais recente
            return max(files, key=os.path.getmtime)

        except Exception as e:
            self.log_output.append(f"Error accessing directory: {e}")
            return None

    def play_latest_audio(self):
        """Busca e toca o arquivo de áudio mais recente."""
        latest_audio = self.get_latest_file()

        if latest_audio:
            self.log_output.append(f"Playing: {latest_audio}")

            # Configura o player
            self.player.setSource(QUrl.fromLocalFile(latest_audio))
            self.audio_output.setVolume(50)  # Define o volume
            self.player.play()
            
            self.log_output.append("Playback started.")
        else:
            self.log_output.append("No audio file found.")

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = TtsApp()
    window.show()

    sys.exit(app.exec())

