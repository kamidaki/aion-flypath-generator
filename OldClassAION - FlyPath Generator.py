import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import xml.etree.ElementTree as ET
from datetime import datetime
import os
import shutil
import re
from xml.dom import minidom
import base64
import webbrowser
import io

# Tentar importar PIL, com fallback se não estiver disponível
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("AVISO: Pillow não encontrado. Para exibir o logo, instale com: pip install Pillow")

def convert_image_to_base64(image_path):
    """Função utilitária para converter uma imagem para base64"""
    try:
        with open(image_path, "rb") as img_file:
            img_data = img_file.read()
            return base64.b64encode(img_data).decode('utf-8')
    except Exception as e:
        print(f"Erro ao converter imagem: {e}")
        return None

class FlypathManager:
    def __init__(self, root):
        self.root = root
        self.root.title("OLD CLASS SERVER - Aion Flypath Manager")
        self.root.geometry("1000x700")

        # Variáveis
        self.client_file = tk.StringVar()
        self.emulator_file = tk.StringVar()
        self.seq_counter = 1

        # Tentar carregar o logo
        self.logo_base64 = None
        self.load_logo_from_file()

        # Mapas de world ID para world name (cName)
        self.world_map = {
            # Elyos Cities
            "110010000": "LC1",
            "110020000": "LC2",
            "110070000": "Arena_L_Lobby",

            # Asmodian Cities
            "120010000": "DC1",
            "120020000": "DC2",
            "120080000": "Arena_D_Lobby",

            # Arena Lobbies
            "130090000": "Arena_L_CLobby",
            "140010000": "Arena_D_CLobby",

            # Elyos Zones
            "210010000": "LF1",  # Poeta
            "210020000": "LF2",  # Eltnen
            "210030000": "LF1A",  # Verteron
            "210040000": "LF3",  # Heiron
            "210050000": "LF4",  # Inggison
            "210060000": "LF2A",  # Theobomos
            "210070000": "LF5",  # Cygnea
            "210080000": "LF5_Ship",  # Griffoen
            "210090000": "LDF5_Under_L",  # Idian Depths Light

            # Asmodian Zones
            "220010000": "DF1",  # Ishalgen
            "220020000": "DF2",  # Morheim
            "220030000": "DF1A",  # Altgard
            "220040000": "DF3",  # Beluslan
            "220050000": "DF2A",  # Brusthonin
            "220070000": "DF4",  # Gelkmaros
            "220080000": "DF5",  # Enshar
            "220090000": "DF5_Ship",  # Habrok
            "220100000": "LDF5_Under_D",  # Idian Depths Dark

            # Instance Dungeons (300000000 range)
            "300010000": "IDAbPro",
            "300020000": "IDTest_Dungeon",
            "300030000": "IDAb1_MiniCastle",  # Nochsana Training Camp
            "300040000": "IDLF1",  # Dark Poeta
            "300050000": "IDAbRe_Up_Asteria",  # Asteria Chamber
            "300060000": "IDAbRe_Low_Divine",  # Sulfur Tree Nest
            "300070000": "IDAbRe_Up_Rhoo",  # Chamber of Roah
            "300080000": "IDAbRe_Low_Wciel",  # Left Wing Chamber
            "300090000": "IDAbRe_Low_Eciel",  # Right Wing Chamber
            "300100000": "IDshulackShip",  # Steel Rake
            "300110000": "IDAb1_Dreadgion",  # Dredgion
            "300120000": "IDAbRe_Up3_Dkisas",  # Kysis Chamber
            "300130000": "IDAbRe_Up3_Lamiren",  # Miren Chamber
            "300140000": "IDAbRe_Up3_Crotan",  # Krotan Chamber
            "300150000": "IDTemple_Up",  # Udas Temple
            "300160000": "IDTemple_Low",  # Lower Udas Temple
            "300170000": "IDCatacombs",  # Beshmundir Temple
            "300190000": "IDElim",  # Talocs Hollow
            "300200000": "IDNovice",  # Haramel
            "300210000": "IDDreadgion_02",  # Chantra Dredgion
            "300220000": "IDAbRe_Core",  # Abyssal Splinter
            "300230000": "IDCromede",  # Kromedes Trial
            "300240000": "IDStation",  # Aturam Sky Fortress
            "300250000": "IDF4Re_Drana",  # Esoterrace
            "300280000": "IDYun",  # Rentus Base
            "300290000": "Test_MRT_IDZone",
            "300300000": "IDArena",  # Empyrean Crucible
            "300320000": "IDArena_Solo",  # Crucible Challenge
            "300350000": "IDArena_pvp01",  # Arena of Chaos
            "300360000": "IDArena_pvp02",  # Arena of Discipline
            "300420000": "IDArena_pvp01_T",  # Chaos Training Grounds
            "300430000": "IDArena_pvp02_T",  # Discipline Training Grounds
            "300440000": "IDDreadgion_03",  # Terath Dredgion
            "300450000": "IDArena_Team01",  # Arena of Harmony
            "300460000": "IDshulackShip_Solo",  # Steel Rake Cabin
            "300480000": "IDLDF5RE_Solo",  # Sealed Danuar Mysticarium
            "300510000": "IDTiamat_1",  # Tiamat Stronghold
            "300520000": "IDTiamat_2",  # Dragon Lords Refuge
            "300540000": "IDLDF5b_TD",  # The Eternal Bastion
            "300550000": "IDArena_Glory",  # Arena of Glory
            "300560000": "IDDF2Flying_Event01",  # Shugo Imperial Tomb
            "300570000": "IDArena_Team01_T",  # Harmony Training Grounds
            "300590000": "IDLDF5_Under_01",  # Ophidan Bridge
            "300600000": "IDAbRe_Core_02",  # Unstable Abyssal Splinter
            "300610000": "IDRaksha_solo",  # Raksang Ruins
            "300620000": "IDYun_Hard",  # Occupied Rentus Base
            "300630000": "IDTiamat_2_Hard",  # Anguished Dragon Lords Refuge
            "300700000": "IDUnderpassRe",  # The Hexway
            "300800000": "IDRuneweapon",  # Infinity Shard

            # Instance Dungeons (301000000 range)
            "301100000": "IDArena_Team01_T2",  # Unity Training Grounds
            "301110000": "IDLDF5_Under_Rune",  # Danuar Reliquary
            "301120000": "IDKamar",  # Kamar Battlefield
            "301130000": "IDVritra_Base",  # Sauro Supply Base
            "301140000": "IDLDF5_Under_02",  # Seized Danuar Sanctuary
            "301150000": "IDAsteria_IU_Solo",  # Rumakikis Conspiracy Solo
            "301160000": "IDAsteria_IU_Party",  # Nightmare Circus
            "301200000": "IDAsteria_IU_World",  # The Nightmare Circus
            "301210000": "IDLDF5_Under_01_War",  # Engulfed Ophidan Bridge
            "301220000": "IDF5_TD_War",  # Iron Wall Warfront
            "301230000": "IDLDF5_Under_03",  # Illuminary Obelisk
            "301240000": "IDAbRe_Up3_Dkisas_02",  # Legions Kysis Barracks
            "301250000": "IDAbRe_Up3_Lamiren_02",  # Legions Miren Barracks
            "301260000": "IDAbRe_Up3_Crotan_02",  # Legions Krotan Barracks
            "301270000": "IDLDF4Re_01",  # Linkgate Foundry
            "301280000": "IDAbRe_Up3_Dkisas_02_N",  # Kysis Barracks
            "301290000": "IDAbRe_Up3_Lamiren_02_N",  # Miren Barracks
            "301300000": "IDAbRe_Up3_Crotan_02_N",  # Krotan Barracks
            "301310000": "IDLDF5_Fortress_Re",  # Idgel Dome
            "301320000": "IDLDF5_Under_01_PC",  # Lucky Ophidan Bridge
            "301330000": "IDLDF5_Under_Rune_PC",  # Lucky Danuar Reliquary
            "301340000": "IDLDF4Re_01_Q",  # Linkgate Foundry
            "301360000": "IDLDF5_Under_Rune_H",  # Infernal Danuar Reliquary
            "301370000": "IDLDF5_Under_03_H",  # Infernal Illuminary Obelisk
            "301380000": "IDLDF5_Under_02_E",  # Danuar Sanctuary
            "301390000": "IDSeal",  # Drakenspire Depths
            "301400000": "IDSweep",  # The Shugo Emperors Vault
            "301500000": "IDLegion",  # Stonespear Reach

            # Elyos Instance Dungeons (310000000 range)
            "310010000": "IDAbProL1",  # Karamatis1
            "310020000": "IDAbProL2",  # Karamatis2
            "310030000": "IDAbGateL1",  # Aerdina
            "310040000": "IDAbGateL2",  # Geranaia
            "310050000": "IDLF3Lp",  # Aetherogenetics Lab
            "310060000": "IDLF1B",  # Sliver of Darkness
            "310070000": "IDLF1B_Stigma",  # Sliver of Darkness
            "310080000": "IDLC1_arena",  # Sanctum Underground Arena
            "310090000": "IDLF3_Castle_indratoo",  # Indratu Fortress
            "310100000": "IDLF3_Castle_Lehpar",  # Azoturan Fortress
            "310110000": "IDLF2a_Lab",  # Theobomos Lab
            "310120000": "IDAbProL3",  # Karamatis3

            # Asmodian Instance Dungeons (320000000 range)
            "320010000": "IDAbProD1",  # Ataxiar1
            "320020000": "IDAbProD2",  # Ataxiar2
            "320030000": "IDAbGateD1",  # Bregirun
            "320040000": "IDAbGateD2",  # Nidalber
            "320050000": "IDDF2Flying",  # Sky Temple Interior
            "320060000": "IDDF1B",  # Space of Oblivion
            "320070000": "IDSpace",  # Space of Destiny
            "320080000": "IDDF3_Dragon",  # Draupnir Cave
            "320090000": "IDDC1_arena",  # Triniel Underground Arena
            "320100000": "IDDF2_Dflame",  # Fire Temple
            "320110000": "IDDF3_LP",  # Alquimia Research Center
            "320120000": "IDDC1_Arena_3F",  # Shadow Court Dungeon
            "320130000": "IDDf2a_Adma",  # Adma Stronghold
            "320140000": "IDAbProD3",  # Ataxiar3
            "320150000": "IDDramata_01",  # Padmarashkas Cave

            # Abyss
            "400010000": "Ab1",  # Reshanta
            "400020000": "Gab1_01",  # Belus
            "400030000": "GAb1_Sub",  # Transidium Annex
            "400040000": "Gab1_02",  # Aspida
            "400050000": "Gab1_03",  # Atanatos
            "400060000": "Gab1_04",  # Disillon

            # Prisons
            "510010000": "LF_Prison",
            "520010000": "DF_Prison",

            # Balaurea Zones
            "600010000": "Underpass",  # Silentera Canyon
            "600020000": "LDF4a",  # Sarpan
            "600030000": "LDF4b",  # Tiamaranta
            "600040000": "Tiamat_Down",  # Tiamaranta's Eye
            "600050000": "LDF5a",  # Katalam
            "600060000": "LDF5b",  # Danaria
            "600080000": "IDIU",  # Live Party Concert Hall
            "600090000": "LDF5_Fortress",  # Kaldor
            "600100000": "LDF4_Advance",  # Levinshor

            # Housing
            "700010000": "Housing_LF_personal",  # Oriel
            "700020000": "Housing_LC_legion",  # Elyos Legion Housing
            "710010000": "Housing_DF_personal",  # Pernon
            "710020000": "Housing_DC_legion",  # Asmodian Legion Housing
            "720010000": "housing_idlf_personal",  # Oriel Instance
            "730010000": "housing_iddf_personal",  # Pernon Instance

            # Test Maps
            "900020000": "Test_Basic",
            "900030000": "Test_Server",
            "900100000": "Test_GiantMonster",
            "900110000": "Housing_barrack",
            "900120000": "Test_IDArena",
            "900130000": "IDLDF5RE_test",
            "900140000": "Test_Kgw",
            "900150000": "Test_Basic_Mj",
            "900170000": "test_intro",
            "900180000": "Test_server_art",
            "900190000": "Test_TagMatch",
            "900200000": "test_timeattack",
            "900220000": "System_Basic"
        }

        self.setup_ui()

    def load_logo_from_file(self):
        """Carrega o logo do arquivo especificado"""
        logo_path = r"F:\Servidor Aion\OLD CLASS SERVER\EDIT - CLIENT FILES\FOTOS\LOGO_04.png"
        try:
            if os.path.exists(logo_path):
                self.logo_base64 = convert_image_to_base64(logo_path)
                print("Logo carregado com sucesso!")
            else:
                print(f"Logo não encontrado em: {logo_path}")
                self.create_default_logo()
        except Exception as e:
            print(f"Erro ao carregar logo: {e}")
            self.create_default_logo()

    def create_default_logo(self):
        """Cria um logo padrão se o arquivo não for encontrado"""
        # Logo padrão simples (texto estilizado)
        self.logo_base64 = None

    def open_website(self, url):
        """Abre o site no navegador padrão"""
        webbrowser.open(url)

    def setup_ui(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Frame do logo no topo
        logo_frame = ttk.Frame(main_frame)
        logo_frame.grid(row=0, column=0, columnspan=2, pady=(0, 15))

        # Tentar exibir o logo
        try:
            if self.logo_base64 and PIL_AVAILABLE:
                # Decodificar base64 e criar imagem
                logo_data = base64.b64decode(self.logo_base64)
                logo_image = Image.open(io.BytesIO(logo_data))

                # Redimensionar se necessário (manter proporção)
                logo_width, logo_height = logo_image.size
                max_width = 100
                if logo_width > max_width:
                    ratio = max_width / logo_width
                    new_width = int(logo_width * ratio)
                    new_height = int(logo_height * ratio)
                    logo_image = logo_image.resize((new_width, new_height), Image.Resampling.LANCZOS)

                # Converter para PhotoImage
                self.logo_photo = ImageTk.PhotoImage(logo_image)
                logo_label = ttk.Label(logo_frame, image=self.logo_photo)
                logo_label.pack()
            else:
                # Se não houver logo, mostrar texto estilizado
                title_label = ttk.Label(logo_frame, text="OLD CLASS SERVER",
                                        font=('Arial', 20, 'bold'), foreground='blue')
                title_label.pack()
                subtitle_label = ttk.Label(logo_frame, text="Aion Flypath Manager",
                                           font=('Arial', 12))
                subtitle_label.pack()
        except Exception as e:
            print(f"Erro ao exibir logo: {e}")
            # Fallback para texto
            title_label = ttk.Label(logo_frame, text="OLD CLASS SERVER",
                                    font=('Arial', 16, 'bold'))
            title_label.pack()

        # Configuração de arquivos
        files_frame = ttk.LabelFrame(main_frame, text="Configuração de Arquivos", padding="10")
        files_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        # Cliente XML
        ttk.Label(files_frame, text="Arquivo XML do Cliente:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        ttk.Entry(files_frame, textvariable=self.client_file, width=50).grid(row=0, column=1, padx=(0, 5))
        ttk.Button(files_frame, text="Selecionar", command=self.select_client_file).grid(row=0, column=2)

        # Emulador XML
        ttk.Label(files_frame, text="Arquivo XML do Emulador:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5),
                                                                     pady=(5, 0))
        ttk.Entry(files_frame, textvariable=self.emulator_file, width=50).grid(row=1, column=1, padx=(0, 5),
                                                                               pady=(5, 0))
        ttk.Button(files_frame, text="Selecionar", command=self.select_emulator_file).grid(row=1, column=2, pady=(5, 0))

        # Botões principais
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=2, column=0, columnspan=2, pady=(0, 10))

        ttk.Button(buttons_frame, text="Sincronizar Arquivos", command=self.sync_files).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="Adicionar Novo Flypath", command=self.open_add_flypath_window).pack(
            side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="Criar Apenas SEQ", command=self.open_create_seq_window).pack(side=tk.LEFT)

        # Log area
        log_frame = ttk.LabelFrame(main_frame, text="Log de Operações", padding="10")
        log_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))

        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=80)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # Frame do rodapé com hiperlink
        footer_frame = ttk.Frame(main_frame)
        footer_frame.grid(row=4, column=0, columnspan=2, pady=(10, 0))

        # Texto e hiperlink
        footer_text = ttk.Label(footer_frame, text="Acesse o Site do OLD CLASS: ")
        footer_text.pack(side=tk.LEFT)

        # Link clicável
        link_label = ttk.Label(footer_frame, text="https://aionclassicbrasil.com/",
                               foreground="blue", cursor="hand2")
        link_label.pack(side=tk.LEFT)
        link_label.bind("<Button-1>", lambda e: self.open_website("https://aionclassicbrasil.com/"))

        # Configurar grid weights
        main_frame.rowconfigure(3, weight=1)
        main_frame.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

    def select_client_file(self):
        filename = filedialog.askopenfilename(
            title="Selecionar arquivo XML do Cliente",
            filetypes=[("XML files", "*.xml"), ("All files", "*.*")]
        )
        if filename:
            self.client_file.set(filename)

    def select_emulator_file(self):
        filename = filedialog.askopenfilename(
            title="Selecionar arquivo XML do Emulador",
            filetypes=[("XML files", "*.xml"), ("All files", "*.*")]
        )
        if filename:
            self.emulator_file.set(filename)

    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update()

    def save_log_to_file(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        log_file = os.path.join(script_dir, "flypath_log.txt")

        with open(log_file, "w", encoding="utf-8") as f:
            f.write(self.log_text.get("1.0", tk.END))

        self.log(f"Log salvo em: {log_file}")

    def pretty_print_xml(self, element):
        """Formatar XML com indentação adequada"""
        rough_string = ET.tostring(element, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ", encoding=None)

    def write_formatted_xml(self, tree, filename):
        """Escrever XML formatado com indentação"""
        root = tree.getroot()
        rough_string = ET.tostring(root, encoding='unicode')
        reparsed = minidom.parseString(rough_string)

        # Remover linhas vazias extras
        pretty = reparsed.toprettyxml(indent="  ", encoding=None)
        lines = [line for line in pretty.split('\n') if line.strip()]
        formatted_xml = '\n'.join(lines)

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(formatted_xml)

    def parse_client_xml(self):
        """Parse do arquivo XML do cliente"""
        try:
            tree = ET.parse(self.client_file.get())
            root = tree.getroot()

            paths = {}
            for path_group in root.findall('.//path_group'):
                group_id = path_group.find('group_id').text

                start = path_group.find('start')
                end = path_group.find('end')
                fly_time = path_group.find('fly_time').text
                file_elem = path_group.find('.//file')

                paths[group_id] = {
                    'sx': start.find('x').text,
                    'sy': start.find('y').text,
                    'sz': start.find('z').text,
                    'sworld': start.find('world').text,
                    'ex': end.find('x').text,
                    'ey': end.find('y').text,
                    'ez': end.find('z').text,
                    'eworld': end.find('world').text,
                    'time': fly_time,
                    'file': file_elem.text if file_elem is not None else f"OLDCLASS_BATTLEROYALE_{self.seq_counter:02d}.seq"
                }

            return paths

        except Exception as e:
            self.log(f"Erro ao ler arquivo do cliente: {str(e)}")
            return {}

    def parse_emulator_xml(self):
        """Parse do arquivo XML do emulador"""
        try:
            tree = ET.parse(self.emulator_file.get())
            root = tree.getroot()

            paths = {}
            for flypath in root.findall('.//flypath_location'):
                id_attr = flypath.get('id')
                paths[id_attr] = {
                    'sx': flypath.get('sx'),
                    'sy': flypath.get('sy'),
                    'sz': flypath.get('sz'),
                    'sworld': flypath.get('sworld'),
                    'ex': flypath.get('ex'),
                    'ey': flypath.get('ey'),
                    'ez': flypath.get('ez'),
                    'eworld': flypath.get('eworld'),
                    'time': flypath.get('time')
                }

            return paths, tree, root

        except Exception as e:
            self.log(f"Erro ao ler arquivo do emulador: {str(e)}")
            return {}, None, None

    def world_name_to_id(self, world_name):
        """Converte nome do world para ID (case insensitive)"""
        if not world_name:
            return "210050000"  # Default se world_name for vazio

        world_name_lower = world_name.lower().strip()
        for world_id, name in self.world_map.items():
            if name.lower() == world_name_lower:
                return world_id

        # Log quando não encontrar mapeamento
        self.log(f"⚠️ World name '{world_name}' não encontrado no mapeamento! Usando padrão 210050000")
        return "210050000"  # Default

    def get_world_name_by_id(self, world_id):
        """Retorna o nome do world pelo ID"""
        return self.world_map.get(world_id, 'LF4')

    def add_client_path_group(self, root, client_id, emu_data, today):
        """Adiciona path_group formatado ao arquivo do cliente"""
        # Converter world ID para world name
        sworld_name = self.world_map.get(emu_data['sworld'], 'LF4')
        eworld_name = self.world_map.get(emu_data['eworld'], 'LF4')

        # Adicionar comentário
        comment_text = f" Adicionado {today} "

        # Criar path_group
        path_group = ET.Element('path_group')

        # group_id
        group_id_elem = ET.SubElement(path_group, 'group_id')
        group_id_elem.text = client_id

        # fixed_camera
        fixed_camera = ET.SubElement(path_group, 'fixed_camera')
        fixed_camera.text = "false"

        # path
        path_elem = ET.SubElement(path_group, 'path')
        id_elem = ET.SubElement(path_elem, 'id')
        id_elem.text = "1"
        file_elem = ET.SubElement(path_elem, 'file')
        file_elem.text = f"OLDCLASS_BATTLEROYALE_{self.seq_counter:02d}.seq"
        self.seq_counter += 1

        # start
        start_elem = ET.SubElement(path_group, 'start')
        ET.SubElement(start_elem, 'x').text = emu_data['sx']
        ET.SubElement(start_elem, 'y').text = emu_data['sy']
        ET.SubElement(start_elem, 'z').text = emu_data['sz']
        ET.SubElement(start_elem, 'world').text = sworld_name

        # end
        end_elem = ET.SubElement(path_group, 'end')
        ET.SubElement(end_elem, 'x').text = emu_data['ex']
        ET.SubElement(end_elem, 'y').text = emu_data['ey']
        ET.SubElement(end_elem, 'z').text = emu_data['ez']
        ET.SubElement(end_elem, 'world').text = eworld_name

        # fly_time
        fly_time_elem = ET.SubElement(path_group, 'fly_time')
        fly_time_elem.text = emu_data['time']

        # Adicionar comentário e elemento ao root
        root.append(ET.Comment(comment_text))
        root.append(path_group)

        return file_elem.text

    def sync_files(self):
        """Sincroniza os arquivos entre cliente e emulador"""
        if not self.client_file.get() or not self.emulator_file.get():
            messagebox.showerror("Erro", "Selecione os arquivos do cliente e emulador!")
            return

        self.log("Iniciando sincronização...")

        # Parse dos arquivos
        client_paths = self.parse_client_xml()
        emulator_paths, emu_tree, emu_root = self.parse_emulator_xml()

        if not client_paths or emu_tree is None:
            return

        changes_made = False
        today = datetime.now().strftime("%d.%m.%Y")

        # Verificar diferenças e correções no emulador
        for client_id, client_data in client_paths.items():
            if client_id in emulator_paths:
                emu_data = emulator_paths[client_id]

                # Converter world name para world ID
                sworld_id = self.world_name_to_id(client_data['sworld'])
                eworld_id = self.world_name_to_id(client_data['eworld'])

                # Verificar se dados estão diferentes
                if (emu_data['sx'] != client_data['sx'] or
                        emu_data['sy'] != client_data['sy'] or
                        emu_data['sz'] != client_data['sz'] or
                        emu_data['sworld'] != sworld_id or
                        emu_data['ex'] != client_data['ex'] or
                        emu_data['ey'] != client_data['ey'] or
                        emu_data['ez'] != client_data['ez'] or
                        emu_data['eworld'] != eworld_id or
                        emu_data['time'] != client_data['time']):

                    # Corrigir no emulador
                    for flypath in emu_root.findall('.//flypath_location'):
                        if flypath.get('id') == client_id:
                            flypath.set('sx', client_data['sx'])
                            flypath.set('sy', client_data['sy'])
                            flypath.set('sz', client_data['sz'])
                            flypath.set('sworld', sworld_id)
                            flypath.set('ex', client_data['ex'])
                            flypath.set('ey', client_data['ey'])
                            flypath.set('ez', client_data['ez'])
                            flypath.set('eworld', eworld_id)
                            flypath.set('time', client_data['time'])
                            break

                    self.log(f"ID {client_id}: Dados corrigidos no emulador")
                    changes_made = True

            else:
                # ID não existe no emulador, criar
                sworld_id = self.world_name_to_id(client_data['sworld'])
                eworld_id = self.world_name_to_id(client_data['eworld'])

                # Adicionar comentário
                emu_root.append(ET.Comment(f" Adicionado {today} "))

                # Criar novo elemento
                new_flypath = ET.SubElement(emu_root, 'flypath_location')
                new_flypath.set('id', client_id)
                new_flypath.set('sx', client_data['sx'])
                new_flypath.set('sy', client_data['sy'])
                new_flypath.set('sz', client_data['sz'])
                new_flypath.set('sworld', sworld_id)
                new_flypath.set('ex', client_data['ex'])
                new_flypath.set('ey', client_data['ey'])
                new_flypath.set('ez', client_data['ez'])
                new_flypath.set('eworld', eworld_id)
                new_flypath.set('time', client_data['time'])

                self.log(f"ID {client_id}: Adicionado ao emulador")
                changes_made = True

                # Verificar se arquivo SEQ existe
                self.check_seq_file_exists(client_data['file'])

        # Verificar IDs que existem no emulador mas não no cliente
        client_tree = ET.parse(self.client_file.get())
        client_root = client_tree.getroot()

        for emu_id in emulator_paths.keys():
            if emu_id not in client_paths:
                emu_data = emulator_paths[emu_id]

                # Adicionar path_group ao cliente
                seq_filename = self.add_client_path_group(client_root, emu_id, emu_data, today)

                self.log(f"ID {emu_id}: Adicionado ao cliente")
                changes_made = True

                # Verificar se arquivo SEQ existe
                self.check_seq_file_exists(seq_filename)

        # Salvar alterações
        if changes_made:
            # Backup dos arquivos originais
            shutil.copy2(self.client_file.get(), self.client_file.get() + ".backup")
            shutil.copy2(self.emulator_file.get(), self.emulator_file.get() + ".backup")

            # Salvar arquivos modificados
            self.write_formatted_xml(client_tree, self.client_file.get())
            emu_tree.write(self.emulator_file.get(), encoding='utf-8', xml_declaration=True)

            self.log("Sincronização concluída com sucesso!")
            self.log("Backups criados dos arquivos originais")
        else:
            self.log("Nenhuma alteração necessária")

        self.save_log_to_file()

    def check_seq_file_exists(self, seq_filename):
        """Verifica se o arquivo SEQ existe no diretório do cliente"""
        try:
            client_dir = os.path.dirname(self.client_file.get())
            seq_path = os.path.join(client_dir, seq_filename)

            if os.path.exists(seq_path):
                self.log(f"✓ Arquivo SEQ encontrado: {seq_filename}")
            else:
                self.log(f"⚠ Arquivo SEQ não encontrado: {seq_filename}")
                self.log(f"  Localização esperada: {seq_path}")

        except Exception as e:
            self.log(f"Erro ao verificar arquivo SEQ {seq_filename}: {str(e)}")

    def calculate_trajectory_times(self, start_coords, end_coords, total_time, num_points=10):
        """Calcula tempos de trajetória baseado na distância"""
        import math

        sx, sy, sz = map(float, start_coords)
        ex, ey, ez = map(float, end_coords)
        total_time = float(total_time)

        trajectory_times = []

        for i in range(num_points + 1):
            progress = i / num_points
            # Usar uma curva não linear para distribuir os tempos
            time_progress = progress ** 0.8  # Curva suave
            time_point = time_progress * total_time

            # Calcular posição interpolada
            x = sx + (ex - sx) * progress
            y = sy + (ey - sy) * progress
            z = sz + (ez - sz) * progress

            trajectory_times.append({
                'time': round(time_point, 1),
                'x': round(x, 5),
                'y': round(y, 5),
                'z': round(z, 5)
            })

        return trajectory_times

    def create_seq_file(self, flypath_id, data):
        """Cria arquivo .seq baseado no template com trajetória calculada"""
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            seq_filename = data.get('file', f"OLDCLASS_BATTLEROYALE_{self.seq_counter:02d}.seq")
            seq_path = os.path.join(script_dir, seq_filename)

            # Remover extensão .seq do nome para usar no Name
            seq_name = os.path.splitext(seq_filename)[0]

            # Processar trajetória
            if 'manual_trajectory' in data and data['manual_trajectory']:
                trajectory = sorted(data['manual_trajectory'], key=lambda p: p['time'])
                # Garantir que temos ponto inicial e final
                trajectory.insert(0, {
                    'time': 0.0,
                    'x': float(data['sx']),
                    'y': float(data['sy']),
                    'z': float(data['sz'])
                })
                trajectory.append({
                    'time': float(data['time']),
                    'x': float(data['ex']),
                    'y': float(data['ey']),
                    'z': float(data['ez'])
                })
            else:
                trajectory = self.calculate_trajectory_times(
                    [data['sx'], data['sy'], data['sz']],
                    [data['ex'], data['ey'], data['ez']],
                    data['time']
                )

            total_time = float(data['time'])

            # Gerar Keys para câmera (ParamId="1")
            camera_keys = []
            for i, point in enumerate(trajectory):
                if i == 0:
                    camera_keys.append(
                        f'        <Key ignorePhys="1" tens="0.5" time="{point["time"]}" '
                        f'value="{point["x"]},{point["y"]},{point["z"]}" />'
                    )
                elif i == len(trajectory) - 1:
                    camera_keys.append(
                        f'        <Key ignorePhys="1" tens="1" time="{point["time"]}" '
                        f'value="{point["x"]},{point["y"]},{point["z"]}" />'
                    )
                else:
                    camera_keys.append(
                        f'        <Key time="{point["time"]}" '
                        f'value="{point["x"]},{point["y"]},{point["z"]}" />'
                    )

            # Gerar Keys de rotação da câmera (ParamId="2") - interpolação suave
            camera_rotations = []
            for i, point in enumerate(trajectory):
                # Rotações interpoladas baseadas na posição na trajetória
                progress = i / (len(trajectory) - 1) if len(trajectory) > 1 else 0

                # Rotações que variam suavemente ao longo da trajetória
                if i == 0:
                    camera_rotations.append('        <Key time="0" value="0.8889,-0.0356,-0.4513,0.0701" />')
                elif progress <= 0.2:
                    camera_rotations.append(
                        f'        <Key time="{point["time"]}" value="0.9414,-0.0295,-0.3250,0.0855" />')
                elif progress <= 0.4:
                    camera_rotations.append(
                        f'        <Key time="{point["time"]}" value="0.7775,0.0088,-0.6287,-0.0109" />')
                elif progress <= 0.6:
                    camera_rotations.append(
                        f'        <Key time="{point["time"]}" value="0.9629,0.0107,-0.2668,-0.0387" />')
                elif progress <= 0.8:
                    camera_rotations.append(
                        f'        <Key time="{point["time"]}" value="0.9217,-0.0081,-0.3873,0.0192" />')
                else:
                    camera_rotations.append(
                        f'        <Key time="{point["time"]}" value="0.7459,-0.0209,-0.6653,0.0235" />')

            # Gerar Keys de posição do personagem (ParamId="1" do soloself)
            character_keys = []
            for i, point in enumerate(trajectory):
                if i == 0:
                    character_keys.append(
                        f'        <Key ignorePhys="1" tens="0.5" time="{point["time"]}" '
                        f'value="{point["x"]},{point["y"]},{point["z"]}" />'
                    )
                elif i == len(trajectory) - 1:
                    character_keys.append(
                        f'        <Key ignorePhys="1" tens="0.5" time="{point["time"]}" '
                        f'value="{point["x"]},{point["y"]},{point["z"]}" />'
                    )
                else:
                    character_keys.append(
                        f'        <Key ignorePhys="1" time="{point["time"]}" '
                        f'value="{point["x"]},{point["y"]},{point["z"]}" />'
                    )

            # Gerar Keys de rotação do personagem (ParamId="2" do soloself)
            character_rotations = []
            for i, point in enumerate(trajectory):
                progress = i / (len(trajectory) - 1) if len(trajectory) > 1 else 0

                # Rotações do personagem que variam suavemente
                if i == 0:
                    character_rotations.append(
                        '        <Key time="0" value="0.78648746,0.065623485,-0.046111301,0.61237639" />')
                elif progress <= 0.2:
                    character_rotations.append(
                        f'        <Key time="{point["time"]}" value="0.65647852,0.035936307,-0.04061494,0.75239283" />')
                elif progress <= 0.4:
                    character_rotations.append(
                        f'        <Key time="{point["time"]}" value="0.55345142,0.018595392,-0.045263451,0.83144277" />')
                elif progress <= 0.6:
                    character_rotations.append(
                        f'        <Key time="{point["time"]}" value="0.5147931,0.044739988,-0.066565931,0.85355461" />')
                elif progress <= 0.8:
                    character_rotations.append(
                        f'        <Key time="{point["time"]}" value="0.39219078,0.019033078,-0.065309986,0.91736507" />')
                else:
                    character_rotations.append(
                        f'        <Key time="{point["time"]}" value="0.33336604,-0.051218938,0.0040310188,0.94139653" />')

            # Gerar sons de asa (ParamId="9" e "10") - distribuídos ao longo do tempo
            def generate_wing_sounds(param_id_offset=0):
                sounds = []
                # Intervalos base para sons de asa
                intervals = [0.2, 2.0, 3.8, 10.8, 12.7, 19.3, 21.1, 27.0, 28.9, 30.7, 32.5, 34.5, 36.3]

                # Ajustar intervalos proporcionalmente ao tempo total
                time_ratio = total_time / 60.0  # 60 é o tempo do exemplo
                adjusted_intervals = [interval * time_ratio for interval in intervals]

                # Adicionar mais intervalos se o tempo for maior
                if total_time > 60:
                    additional_sounds = int((total_time - 60) / 5)  # Som a cada 5 segundos extras
                    for i in range(additional_sounds):
                        adjusted_intervals.append(60 * time_ratio + (i + 1) * 5)

                # Filtrar intervalos que excedem o tempo total
                valid_intervals = [t for t in adjusted_intervals if t < total_time - 1]

                for time_val in valid_intervals:
                    sounds.append(
                        f'        <Key desc="" duration="1.241" fadeoutStart="0" fadeoutTime="0" '
                        f'filename="sounds\\cutscene\\path\\path_wing.ogg" InRadius="10" Is3D="1" '
                        f'IsPrivate="0" Loop="0" OutRadius="100" pan="127" Stream="0" '
                        f'time="{time_val:.1f}" volume="255" />'
                    )

                return sounds

            wing_sounds_9 = generate_wing_sounds()

            # Para ParamId="10", usar tempos ligeiramente diferentes
            wing_sounds_10 = []
            intervals_10 = [1.1, 2.8, 4.7, 9.99999, 11.8, 13.7, 20.3, 22.1, 26.1, 27.9, 29.8, 31.7, 33.5, 35.4, 37.2]
            time_ratio = total_time / 60.0
            adjusted_intervals_10 = [interval * time_ratio for interval in intervals_10]

            if total_time > 60:
                additional_sounds = int((total_time - 60) / 5)
                for i in range(additional_sounds):
                    adjusted_intervals_10.append(60 * time_ratio + (i + 1) * 4.5)  # Intervalo ligeiramente diferente

            valid_intervals_10 = [t for t in adjusted_intervals_10 if t < total_time - 1]

            for time_val in valid_intervals_10:
                wing_sounds_10.append(
                    f'        <Key desc="" duration="1.241" fadeoutStart="0" fadeoutTime="0" '
                    f'filename="sounds\\cutscene\\path\\path_wing.ogg" InRadius="10" Is3D="1" '
                    f'IsPrivate="0" Loop="0" OutRadius="100" pan="127" Stream="0" '
                    f'time="{time_val:.1f}" volume="255" />'
                )

            # Gerar animações (ParamId="21") - alternando entre voo e planagem
            animation_keys = []
            animation_keys.append('        <Key anim="FflyF_001" length="0.933333" loop="1" time="0" />')

            # Calcular intervalos para animações baseado no tempo total
            current_time = 5.6 * (total_time / 60.0)  # Proporcional ao exemplo
            animation_type = "glide"  # Começar com glide depois do fly inicial

            while current_time < total_time - 5:  # Deixar buffer no final
                if animation_type == "glide":
                    animation_keys.append(
                        f'        <Key anim="Fglide_001" blend="0.3" length="1.33333" loop="1" time="{current_time:.1f}" />'
                    )
                    current_time += 4.2 * (total_time / 60.0)  # Duração da planagem
                    animation_type = "fly"
                else:
                    animation_keys.append(
                        f'        <Key anim="FflyF_001" blend="0.3" length="0.933333" loop="1" time="{current_time:.1f}" />'
                    )
                    current_time += 3.5 * (total_time / 60.0)  # Duração do voo
                    animation_type = "glide"

            # Adicionar animação final se houver tempo
            if current_time < total_time - 2:
                animation_keys.append(
                    f'        <Key anim="Fglide_001" blend="0.3" length="1.33333" loop="1" time="{current_time:.1f}" />'
                )

            # Template completo do arquivo SEQ
            seq_content = f'''<Sequence EndTime="{total_time}" Flags="0" Name="{seq_name}" StartTime="0" TextFile="" >
         <Nodes>
          <Node GroupName="default" Id="0" Name="Scene" NodeClass="0" Type="2" >
           <Track EndTime="{total_time}" Flags="0" ParamId="8" StartTime="0" >
            <Key node="Cam_01" time="0" />
           </Track>
          </Node>
          <Node EntityClass="CameraSource" EntityClassId="117" FOV="80" GroupName="default" Id="-1098458729" Name="Cam_01" NodeClass="0" Pos="{data['sx']},{data['sy']},{data['sz']}" Rotate="0.75245792,0.037327852,0.033507045,0.65672749" Scale="1,1,1" Type="3" >
           <Track Flags="0" ParamId="1" >
    {chr(10).join(camera_keys)}
           </Track>
           <Track Flags="0" ParamId="2" >
    {chr(10).join(camera_rotations)}
           </Track>
           <Track Flags="0" ParamId="0" >
            <Key time="0" value="80" />
           </Track>
          </Node>
          <Node EntityClass="BasicEntity" EntityClassId="4" GroupName="default" Id="-869699686" Name="soloself" NodeClass="0" ObjectName="objects\\pc\\dm\\mesh\\dm.cgf" Pos="{data['sx']},{data['sy']},{data['sz']}" Rotate="0.76234275,0.0032746301,-0.045539211,0.64556104" Scale="1,1,1" SubMesh01="objects\\pc\\dm\\mesh\\dmpl_r102_body.cgf" SubMesh02="objects\\pc\\dm\\mesh\\dmpl_r102_foot.cgf" SubMesh03="objects\\pc\\dm\\mesh\\dmpl_r102_footshort.cgf" SubMesh04="objects\\pc\\dm\\mesh\\dmpl_r102_hand.cgf" SubMesh05="objects\\pc\\dm\\mesh\\dmpl_r102_handshort.cgf" SubMesh06="objects\\pc\\dm\\mesh\\dmpl_r102_leg.cgf" SubMesh07="objects\\pc\\dm\\mesh\\dmpl_r102_shoulder.cgf" SubMesh08="objects\\pc\\dm\\mesh\\dm001_head.cgf" Type="1" >
           <Track EndTime="{total_time}" Flags="0" ParamId="4" StartTime="0" >
             <Key event="Attach" time="0" to="Wing_bone" what="wing" />
           </Track>
           <Track EndTime="{total_time}" Flags="0" ParamId="7" StartTime="0" >
            <Key fadeTime="0" time="{total_time}" />
           </Track>
           <Track Flags="0" ParamId="1" >
    {chr(10).join(character_keys)}
           </Track>
           <Track Flags="0" ParamId="2" >
    {chr(10).join(character_rotations)}
           </Track>
           <Track EndTime="{total_time}" Flags="0" ParamId="59" StartTime="0" >
            <Key bonename="" scale="1" time="{total_time}" />
           </Track>
           <Track EndTime="{total_time}" Flags="0" ParamId="106" StartTime="0" >
            <Key bonename="Bip01 Spine" effect="sys_pathfly.pathfly.sprite" scale="1" time="0" />
            <Key bonename="" scale="1" time="{total_time}" />
           </Track>
           <Track EndTime="{total_time}" Flags="0" ParamId="9" StartTime="0" >
    {chr(10).join(wing_sounds_9)}
           </Track>
           <Track EndTime="{total_time}" Flags="0" ParamId="10" StartTime="0" >
    {chr(10).join(wing_sounds_10)}
           </Track>
           <Track EndTime="{total_time}" Flags="0" ParamId="21" StartTime="0" >
    {chr(10).join(animation_keys)}
           </Track>
          </Node>
          <Node EntityClass="ParticleEffect" EntityClassId="153" GroupName="default" Id="-288908854" Name="Effect" NodeClass="0" Pos="{data['sx']},{data['sy']},{data['sz']}" Rotate="0.76234269,0.0032746226,-0.0455392,0.64556098" Scale="1,1,1" Type="1" >
           <Track Flags="0" ParamId="1" >
            <Key ignorePhys="1" tens="1" time="0" value="{data['sx']},{data['sy']},{data['sz']}" />
            <Key time="{total_time - 4.0}" value="{data['ex']},{data['ey']},{data['ez']}" />
           </Track>
           <Track Flags="0" ParamId="2" >
            <Key time="0" value="0.76234269,0.0032746226,-0.0455392,0.64556098" />
           </Track>
           <Track EndTime="{total_time}" Flags="0" ParamId="59" StartTime="0" >
            <Key bonename="" effect="skill_healing.healing.hit_fast" scale="3" time="0" />
            <Key bonename="" effect="skill_healing.healing.hit_fast" scale="3" time="{total_time}" />
           </Track>
           <Track EndTime="{total_time}" Flags="0" ParamId="106" StartTime="0" >
            <Key bonename="" effect="skill_healing.healing.hit_party" scale="3" time="0" />
            <Key bonename="" effect="skill_healing.healing.hit_party" scale="3" time="{total_time}" />
           </Track>
          </Node>
         </Nodes>
    </Sequence>'''

            with open(seq_path, 'w', encoding='utf-8') as f:
                f.write(seq_content)

            self.log(f"Arquivo SEQ criado: {seq_filename}")

        except Exception as e:
            self.log(f"Erro ao criar arquivo SEQ para ID {flypath_id}: {str(e)}")
            raise

    def open_add_flypath_window(self):
        """Abre janela para adicionar novo flypath"""
        if not self.client_file.get() or not self.emulator_file.get():
            messagebox.showerror("Erro", "Selecione os arquivos do cliente e emulador primeiro!")
            return

        self.add_window = tk.Toplevel(self.root)
        self.add_window.title("Adicionar Novo Flypath")
        self.add_window.geometry("800x700")  # Aumentado para caber mais pontos
        self.add_window.transient(self.root)
        self.add_window.grab_set()

        # Variáveis para o formulário
        self.new_id = tk.StringVar()
        self.world_id = tk.StringVar(value="210050000")
        self.world_name = tk.StringVar(value="LF4")
        self.fly_time = tk.StringVar(value="60")
        self.start_x = tk.StringVar()
        self.start_y = tk.StringVar()
        self.start_z = tk.StringVar()
        self.end_x = tk.StringVar()
        self.end_y = tk.StringVar()
        self.end_z = tk.StringVar()

        # Frame principal com scrollbar
        main_frame = ttk.Frame(self.add_window)
        main_frame.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Conteúdo dentro do frame rolável
        content_frame = ttk.Frame(scrollable_frame, padding="20")
        content_frame.pack(fill=tk.BOTH, expand=True)

        # ID do Flypath
        row = 0
        ttk.Label(content_frame, text="ID do Flypath:").grid(row=row, column=0, sticky=tk.W, pady=5)
        ttk.Entry(content_frame, textvariable=self.new_id, width=20).grid(row=row, column=1, sticky=tk.W, padx=(10, 0))

        # World ID
        row += 1
        ttk.Label(content_frame, text="World ID:").grid(row=row, column=0, sticky=tk.W, pady=5)
        world_combo = ttk.Combobox(content_frame, textvariable=self.world_id, values=list(self.world_map.keys()),
                                   width=20)
        world_combo.grid(row=row, column=1, sticky=tk.W, padx=(10, 0))
        world_combo.bind('<<ComboboxSelected>>', self.update_world_name)

        # World Name
        row += 1
        ttk.Label(content_frame, text="World Name:").grid(row=row, column=0, sticky=tk.W, pady=5)
        ttk.Entry(content_frame, textvariable=self.world_name, width=20).grid(row=row, column=1, sticky=tk.W,
                                                                              padx=(10, 0))

        # Tempo de voo
        row += 1
        ttk.Label(content_frame, text="Tempo de Voo (segundos):").grid(row=row, column=0, sticky=tk.W, pady=5)
        ttk.Entry(content_frame, textvariable=self.fly_time, width=20).grid(row=row, column=1, sticky=tk.W,
                                                                            padx=(10, 0))

        # Separador
        row += 1
        ttk.Separator(content_frame, orient='horizontal').grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E),
                                                               pady=10)

        # Coordenadas de início
        row += 1
        ttk.Label(content_frame, text="Coordenadas de Início:", font=('TkDefaultFont', 10, 'bold')).grid(
            row=row, column=0, columnspan=2, sticky=tk.W, pady=5)

        row += 1
        ttk.Label(content_frame, text="X:").grid(row=row, column=0, sticky=tk.W, pady=2)
        ttk.Entry(content_frame, textvariable=self.start_x, width=20).grid(row=row, column=1, sticky=tk.W, padx=(10, 0))

        row += 1
        ttk.Label(content_frame, text="Y:").grid(row=row, column=0, sticky=tk.W, pady=2)
        ttk.Entry(content_frame, textvariable=self.start_y, width=20).grid(row=row, column=1, sticky=tk.W, padx=(10, 0))

        row += 1
        ttk.Label(content_frame, text="Z:").grid(row=row, column=0, sticky=tk.W, pady=2)
        ttk.Entry(content_frame, textvariable=self.start_z, width=20).grid(row=row, column=1, sticky=tk.W, padx=(10, 0))

        # Separador
        row += 1
        ttk.Separator(content_frame, orient='horizontal').grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E),
                                                               pady=10)

        # Coordenadas de fim
        row += 1
        ttk.Label(content_frame, text="Coordenadas de Destino:", font=('TkDefaultFont', 10, 'bold')).grid(
            row=row, column=0, columnspan=2, sticky=tk.W, pady=5)

        row += 1
        ttk.Label(content_frame, text="X:").grid(row=row, column=0, sticky=tk.W, pady=2)
        ttk.Entry(content_frame, textvariable=self.end_x, width=20).grid(row=row, column=1, sticky=tk.W, padx=(10, 0))

        row += 1
        ttk.Label(content_frame, text="Y:").grid(row=row, column=0, sticky=tk.W, pady=2)
        ttk.Entry(content_frame, textvariable=self.end_y, width=20).grid(row=row, column=1, sticky=tk.W, padx=(10, 0))

        row += 1
        ttk.Label(content_frame, text="Z:").grid(row=row, column=0, sticky=tk.W, pady=2)
        ttk.Entry(content_frame, textvariable=self.end_z, width=20).grid(row=row, column=1, sticky=tk.W, padx=(10, 0))

        # Separador
        row += 1
        ttk.Separator(content_frame, orient='horizontal').grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E),
                                                               pady=10)

        # Trajetória Intermediária
        row += 1
        ttk.Label(content_frame, text="Pontos de Trajetória (Tempo e Posição):",
                  font=('TkDefaultFont', 10, 'bold')).grid(
            row=row, column=0, columnspan=4, sticky=tk.W, pady=10)

        # Cabeçalho da tabela de trajetória
        row += 1
        ttk.Label(content_frame, text="Tempo").grid(row=row, column=0, padx=5)
        ttk.Label(content_frame, text="X").grid(row=row, column=1, padx=5)
        ttk.Label(content_frame, text="Y").grid(row=row, column=2, padx=5)
        ttk.Label(content_frame, text="Z").grid(row=row, column=3, padx=5)

        self.trajectory_points = []  # Lista para armazenar as entradas de trajetória

        # Adicionar 10 linhas para pontos de trajetória
        for i in range(10):
            row += 1
            time_var = tk.StringVar()
            x_var = tk.StringVar()
            y_var = tk.StringVar()
            z_var = tk.StringVar()
            self.trajectory_points.append((time_var, x_var, y_var, z_var))

            ttk.Entry(content_frame, textvariable=time_var, width=10).grid(row=row, column=0, padx=5, pady=2)
            ttk.Entry(content_frame, textvariable=x_var, width=15).grid(row=row, column=1, padx=5, pady=2)
            ttk.Entry(content_frame, textvariable=y_var, width=15).grid(row=row, column=2, padx=5, pady=2)
            ttk.Entry(content_frame, textvariable=z_var, width=15).grid(row=row, column=3, padx=5, pady=2)

        # Botões
        row += 2
        buttons_frame = ttk.Frame(content_frame)
        buttons_frame.grid(row=row, column=0, columnspan=4, pady=20)

        ttk.Button(buttons_frame, text="Adicionar Flypath", command=self.add_new_flypath).pack(
            side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="Cancelar", command=self.add_window.destroy).pack(side=tk.LEFT)

    def update_world_name(self, event=None):
        """Atualiza o nome do world baseado no ID selecionado"""
        world_id = self.world_id.get()
        if world_id in self.world_map:
            self.world_name.set(self.world_map[world_id])

    def add_new_flypath(self):
        """Adiciona novo flypath aos arquivos"""
        try:
            # Validar campos obrigatórios
            if not all([self.new_id.get(), self.world_id.get(), self.world_name.get(),
                        self.fly_time.get(), self.start_x.get(), self.start_y.get(),
                        self.start_z.get(), self.end_x.get(), self.end_y.get(), self.end_z.get()]):
                messagebox.showerror("Erro", "Todos os campos obrigatórios devem ser preenchidos!")
                return

            # Verificar se ID já existe
            client_paths = self.parse_client_xml()
            emulator_paths, _, _ = self.parse_emulator_xml()

            if self.new_id.get() in client_paths or self.new_id.get() in emulator_paths:
                messagebox.showerror("Erro", f"ID {self.new_id.get()} já existe!")
                return

            # Processar pontos de trajetória
            manual_trajectory = []
            for t_var, x_var, y_var, z_var in self.trajectory_points:
                if (t_var.get().strip() and x_var.get().strip() and
                        y_var.get().strip() and z_var.get().strip()):
                    try:
                        manual_trajectory.append({
                            'time': float(t_var.get()),
                            'x': float(x_var.get()),
                            'y': float(y_var.get()),
                            'z': float(z_var.get())
                        })
                    except ValueError:
                        self.log(
                            f"Valor inválido em ponto de trajetória: {t_var.get()}, {x_var.get()}, {y_var.get()}, {z_var.get()}")
                        continue

            # Ordenar pontos por tempo
            manual_trajectory.sort(key=lambda p: p['time'])

            # Verificar se tempos são válidos
            total_time = float(self.fly_time.get())
            for point in manual_trajectory:
                if point['time'] <= 0 or point['time'] >= total_time:
                    messagebox.showerror("Erro", f"Tempo de trajetória deve estar entre 0 e {total_time}")
                    return


            # Parse dos arquivos
            client_tree = ET.parse(self.client_file.get())
            client_root = client_tree.getroot()

            emulator_tree = ET.parse(self.emulator_file.get())
            emulator_root = emulator_tree.getroot()

            today = datetime.now().strftime("%d.%m.%Y")

            # Adicionar ao cliente com formatação adequada
            seq_filename = f"OLDCLASS_BATTLEROYALE_{self.seq_counter:02d}.seq"

            # Criar path_group formatado
            path_group = ET.Element('path_group')

            group_id_elem = ET.SubElement(path_group, 'group_id')
            group_id_elem.text = self.new_id.get()

            fixed_camera = ET.SubElement(path_group, 'fixed_camera')
            fixed_camera.text = "false"

            path_elem = ET.SubElement(path_group, 'path')
            id_elem = ET.SubElement(path_elem, 'id')
            id_elem.text = "1"
            file_elem = ET.SubElement(path_elem, 'file')
            file_elem.text = seq_filename
            self.seq_counter += 1

            start_elem = ET.SubElement(path_group, 'start')
            ET.SubElement(start_elem, 'x').text = self.start_x.get()
            ET.SubElement(start_elem, 'y').text = self.start_y.get()
            ET.SubElement(start_elem, 'z').text = self.start_z.get()
            ET.SubElement(start_elem, 'world').text = self.world_name.get()

            end_elem = ET.SubElement(path_group, 'end')
            ET.SubElement(end_elem, 'x').text = self.end_x.get()
            ET.SubElement(end_elem, 'y').text = self.end_y.get()
            ET.SubElement(end_elem, 'z').text = self.end_z.get()
            ET.SubElement(end_elem, 'world').text = self.world_name.get()

            fly_time_elem = ET.SubElement(path_group, 'fly_time')
            fly_time_elem.text = self.fly_time.get()

            # Adicionar comentário e path_group ao cliente
            client_root.append(ET.Comment(f" Adicionado {today} "))
            client_root.append(path_group)

            # Adicionar ao emulador
            emulator_root.append(ET.Comment(f" Adicionado {today} "))

            new_flypath = ET.SubElement(emulator_root, 'flypath_location')
            new_flypath.set('id', self.new_id.get())
            new_flypath.set('sx', self.start_x.get())
            new_flypath.set('sy', self.start_y.get())
            new_flypath.set('sz', self.start_z.get())
            new_flypath.set('sworld', self.world_id.get())
            new_flypath.set('ex', self.end_x.get())
            new_flypath.set('ey', self.end_y.get())
            new_flypath.set('ez', self.end_z.get())
            new_flypath.set('eworld', self.world_id.get())
            new_flypath.set('time', self.fly_time.get())

            manual_trajectory = []
            for t_var, x_var, y_var, z_var in self.trajectory_points:
                if t_var.get().strip() and x_var.get().strip() and y_var.get().strip() and z_var.get().strip():
                    manual_trajectory.append({
                        'time': float(t_var.get()),
                        'x': float(x_var.get()),
                        'y': float(y_var.get()),
                        'z': float(z_var.get())
                    })

            seq_data = {
                'sx': self.start_x.get(),
                'sy': self.start_y.get(),
                'sz': self.start_z.get(),
                'sworld': self.world_name.get(),
                'ex': self.end_x.get(),
                'ey': self.end_y.get(),
                'ez': self.end_z.get(),
                'eworld': self.world_name.get(),
                'time': self.fly_time.get(),
                'file': seq_filename,
                'manual_trajectory': manual_trajectory
            }

            self.create_seq_file(self.new_id.get(), seq_data)

            # Salvar arquivos
            self.write_formatted_xml(client_tree, self.client_file.get())
            emulator_tree.write(self.emulator_file.get(), encoding='utf-8', xml_declaration=True)

            self.log(f"Novo flypath ID {self.new_id.get()} adicionado com sucesso!")
            self.log(f"Arquivo SEQ criado: {seq_filename}")

            self.add_window.destroy()
            messagebox.showinfo("Sucesso", "Flypath adicionado com sucesso!")

        except Exception as e:
            self.log(f"Erro ao adicionar flypath: {str(e)}")
            messagebox.showerror("Erro", f"Erro ao adicionar flypath: {str(e)}")

    def open_create_seq_window(self):
        """Abre janela para criar apenas arquivo SEQ"""
        self.seq_window = tk.Toplevel(self.root)
        self.seq_window.title("Criar Arquivo SEQ")
        self.seq_window.geometry("800x700")
        self.seq_window.transient(self.root)
        self.seq_window.grab_set()

        # Variáveis para o formulário
        self.seq_filename = tk.StringVar()
        self.seq_world_name = tk.StringVar(value="LF4")
        self.seq_fly_time = tk.StringVar(value="60")
        self.seq_start_x = tk.StringVar()
        self.seq_start_y = tk.StringVar()
        self.seq_start_z = tk.StringVar()
        self.seq_end_x = tk.StringVar()
        self.seq_end_y = tk.StringVar()
        self.seq_end_z = tk.StringVar()

        # Frame principal com scrollbar
        main_frame = ttk.Frame(self.seq_window)
        main_frame.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Conteúdo dentro do frame rolável
        content_frame = ttk.Frame(scrollable_frame, padding="20")
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Nome do arquivo SEQ
        row = 0
        ttk.Label(content_frame, text="Nome do Arquivo SEQ:").grid(row=row, column=0, sticky=tk.W, pady=5)
        ttk.Entry(content_frame, textvariable=self.seq_filename, width=30).grid(row=row, column=1, sticky=tk.W,
                                                                                padx=(10, 0))
        ttk.Label(content_frame, text="(sem extensão .seq)").grid(row=row, column=2, sticky=tk.W, padx=(5, 0))

        # World Name (para referência visual no SEQ)
        row += 1
        ttk.Label(content_frame, text="World Name (referência):").grid(row=row, column=0, sticky=tk.W, pady=5)
        world_seq_combo = ttk.Combobox(content_frame, textvariable=self.seq_world_name,
                                       values=list(self.world_map.values()), width=20)
        world_seq_combo.grid(row=row, column=1, sticky=tk.W, padx=(10, 0))

        # Tempo de voo
        row += 1
        ttk.Label(content_frame, text="Tempo de Voo (segundos):").grid(row=row, column=0, sticky=tk.W, pady=5)
        ttk.Entry(content_frame, textvariable=self.seq_fly_time, width=20).grid(row=row, column=1, sticky=tk.W,
                                                                                padx=(10, 0))

        # Separador
        row += 1
        ttk.Separator(content_frame, orient='horizontal').grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E),
                                                               pady=10)

        # Coordenadas de início
        row += 1
        ttk.Label(content_frame, text="Coordenadas de Início:", font=('TkDefaultFont', 10, 'bold')).grid(
            row=row, column=0, columnspan=3, sticky=tk.W, pady=5)

        row += 1
        ttk.Label(content_frame, text="X:").grid(row=row, column=0, sticky=tk.W, pady=2)
        ttk.Entry(content_frame, textvariable=self.seq_start_x, width=20).grid(row=row, column=1, sticky=tk.W,
                                                                               padx=(10, 0))

        row += 1
        ttk.Label(content_frame, text="Y:").grid(row=row, column=0, sticky=tk.W, pady=2)
        ttk.Entry(content_frame, textvariable=self.seq_start_y, width=20).grid(row=row, column=1, sticky=tk.W,
                                                                               padx=(10, 0))

        row += 1
        ttk.Label(content_frame, text="Z:").grid(row=row, column=0, sticky=tk.W, pady=2)
        ttk.Entry(content_frame, textvariable=self.seq_start_z, width=20).grid(row=row, column=1, sticky=tk.W,
                                                                               padx=(10, 0))

        # Separador
        row += 1
        ttk.Separator(content_frame, orient='horizontal').grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E),
                                                               pady=10)

        # Coordenadas de fim
        row += 1
        ttk.Label(content_frame, text="Coordenadas de Destino:", font=('TkDefaultFont', 10, 'bold')).grid(
            row=row, column=0, columnspan=3, sticky=tk.W, pady=5)

        row += 1
        ttk.Label(content_frame, text="X:").grid(row=row, column=0, sticky=tk.W, pady=2)
        ttk.Entry(content_frame, textvariable=self.seq_end_x, width=20).grid(row=row, column=1, sticky=tk.W,
                                                                             padx=(10, 0))

        row += 1
        ttk.Label(content_frame, text="Y:").grid(row=row, column=0, sticky=tk.W, pady=2)
        ttk.Entry(content_frame, textvariable=self.seq_end_y, width=20).grid(row=row, column=1, sticky=tk.W,
                                                                             padx=(10, 0))

        row += 1
        ttk.Label(content_frame, text="Z:").grid(row=row, column=0, sticky=tk.W, pady=2)
        ttk.Entry(content_frame, textvariable=self.seq_end_z, width=20).grid(row=row, column=1, sticky=tk.W,
                                                                             padx=(10, 0))

        # Separador
        row += 1
        ttk.Separator(content_frame, orient='horizontal').grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E),
                                                               pady=10)

        # Trajetória Intermediária com explicação melhorada
        row += 1
        ttk.Label(content_frame, text="Pontos de Trajetória Intermediários (Opcional):",
                  font=('TkDefaultFont', 10, 'bold')).grid(
            row=row, column=0, columnspan=4, sticky=tk.W, pady=5)

        # Texto explicativo sobre a trajetória
        row += 1
        help_text = (
            "• Tempo 0: Coordenadas de INÍCIO (automático)\n"
            "• Pontos intermediários: Entre 0.1 e tempo_total-0.1\n"
            "• Tempo final: Coordenadas de DESTINO (automático)\n"
            "• Deixe em branco para trajetória automática"
        )
        help_label = ttk.Label(content_frame, text=help_text,
                               font=('TkDefaultFont', 8), foreground='gray')
        help_label.grid(row=row, column=0, columnspan=4, sticky=tk.W, pady=(0, 10))

        # Cabeçalho da tabela de trajetória
        row += 1
        ttk.Label(content_frame, text="Tempo", font=('TkDefaultFont', 9, 'bold')).grid(row=row, column=0, padx=5)
        ttk.Label(content_frame, text="X", font=('TkDefaultFont', 9, 'bold')).grid(row=row, column=1, padx=5)
        ttk.Label(content_frame, text="Y", font=('TkDefaultFont', 9, 'bold')).grid(row=row, column=2, padx=5)
        ttk.Label(content_frame, text="Z", font=('TkDefaultFont', 9, 'bold')).grid(row=row, column=3, padx=5)

        # Inicializar APENAS UMA VEZ a lista de pontos de trajetória
        self.seq_trajectory_points = []

        # Adicionar 10 linhas para pontos de trajetória
        for i in range(10):
            row += 1
            time_var = tk.StringVar()
            x_var = tk.StringVar()
            y_var = tk.StringVar()
            z_var = tk.StringVar()
            self.seq_trajectory_points.append((time_var, x_var, y_var, z_var))

            # Criar os widgets de entrada
            time_entry = ttk.Entry(content_frame, textvariable=time_var, width=10)
            time_entry.grid(row=row, column=0, padx=5, pady=2)

            x_entry = ttk.Entry(content_frame, textvariable=x_var, width=15)
            x_entry.grid(row=row, column=1, padx=5, pady=2)

            y_entry = ttk.Entry(content_frame, textvariable=y_var, width=15)
            y_entry.grid(row=row, column=2, padx=5, pady=2)

            z_entry = ttk.Entry(content_frame, textvariable=z_var, width=15)
            z_entry.grid(row=row, column=3, padx=5, pady=2)

            # Adicionar placeholder text apenas na primeira linha como exemplo
            if i == 0:
                def add_placeholder(entry, placeholder_text):
                    def on_focus_in(event):
                        if entry.get() == placeholder_text:
                            entry.delete(0, tk.END)
                            entry.config(foreground='black')

                    def on_focus_out(event):
                        if entry.get() == '':
                            entry.insert(0, placeholder_text)
                            entry.config(foreground='gray')

                    entry.insert(0, placeholder_text)
                    entry.config(foreground='gray')
                    entry.bind('<FocusIn>', on_focus_in)
                    entry.bind('<FocusOut>', on_focus_out)

                add_placeholder(time_entry, "ex: 10")
                add_placeholder(x_entry, "ex: 1000.5")
                add_placeholder(y_entry, "ex: 2000.3")
                add_placeholder(z_entry, "ex: 500.0")

        # Botões
        row += 2
        buttons_frame = ttk.Frame(content_frame)
        buttons_frame.grid(row=row, column=0, columnspan=4, pady=20)

        ttk.Button(buttons_frame, text="Criar Arquivo SEQ", command=self.create_standalone_seq).pack(
            side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="Cancelar", command=self.seq_window.destroy).pack(side=tk.LEFT)

    def create_standalone_seq(self):
        """Cria arquivo SEQ standalone sem modificar XMLs"""
        try:
            # Validar campos obrigatórios
            if not all([self.seq_world_name.get(),
                        self.seq_fly_time.get(), self.seq_start_x.get(), self.seq_start_y.get(),
                        self.seq_start_z.get(), self.seq_end_x.get(), self.seq_end_y.get(), self.seq_end_z.get()]):
                messagebox.showerror("Erro", "Todos os campos de coordenadas e tempo devem ser preenchidos!")
                return

            # Debug: Log para verificar se estamos processando os pontos corretamente
            self.log("DEBUG: Processando pontos de trajetória...")

            # Processar pontos de trajetória intermediários
            manual_trajectory = []
            for i, (t_var, x_var, y_var, z_var) in enumerate(self.seq_trajectory_points):
                time_str = t_var.get().strip()
                x_str = x_var.get().strip()
                y_str = y_var.get().strip()
                z_str = z_var.get().strip()

                # Ignorar placeholders
                if (time_str in ["ex: 10", ""] or
                        x_str in ["ex: 1000.5", ""] or
                        y_str in ["ex: 2000.3", ""] or
                        z_str in ["ex: 500.0", ""]):
                    continue

                # Se todos os campos estão preenchidos
                if time_str and x_str and y_str and z_str:
                    try:
                        time_value = float(time_str)
                        x_value = float(x_str)
                        y_value = float(y_str)
                        z_value = float(z_str)

                        manual_trajectory.append({
                            'time': time_value,
                            'x': x_value,
                            'y': y_value,
                            'z': z_value
                        })

                        self.log(
                            f"DEBUG: Ponto {i + 1} adicionado: tempo={time_value}, x={x_value}, y={y_value}, z={z_value}")

                    except ValueError as ve:
                        self.log(f"Valor inválido na linha {i + 1}: {time_str}, {x_str}, {y_str}, {z_str} - Erro: {ve}")
                        messagebox.showerror("Erro",
                                             f"Valores inválidos na linha {i + 1} da trajetória.\nVerifique se todos são números válidos.")
                        return

            # Log do resultado do processamento
            self.log(f"DEBUG: Total de pontos processados: {len(manual_trajectory)}")

            # Ordenar pontos por tempo
            manual_trajectory.sort(key=lambda p: p['time'])

            # Verificar se tempos dos pontos intermediários são válidos
            total_time = float(self.seq_fly_time.get())
            for point in manual_trajectory:
                if point['time'] <= 0 or point['time'] >= total_time:
                    messagebox.showerror("Erro",
                                         f"Pontos de trajetória devem ter tempo entre 0 e {total_time} segundos.\n"
                                         f"Ponto inválido: tempo {point['time']}\n\n"
                                         f"Lembre-se:\n"
                                         f"• Tempo 0: coordenadas de início (automático)\n"
                                         f"• Tempo {total_time}: coordenadas de destino (automático)\n"
                                         f"• Pontos intermediários: entre 0.1 e {total_time - 0.1}")
                    return

            # Preparar nome do arquivo
            base_filename = self.seq_filename.get().strip()
            if not base_filename:
                base_filename = f"CUSTOM_FLYPATH_{self.seq_counter:02d}"
                self.seq_counter += 1

            # Remover extensão .seq se foi fornecida
            if base_filename.lower().endswith('.seq'):
                base_filename = base_filename[:-4]

            seq_filename = f"{base_filename}.seq"

            # Preparar dados para criação do SEQ
            seq_data = {
                'sx': self.seq_start_x.get(),
                'sy': self.seq_start_y.get(),
                'sz': self.seq_start_z.get(),
                'sworld': self.seq_world_name.get(),
                'ex': self.seq_end_x.get(),
                'ey': self.seq_end_y.get(),
                'ez': self.seq_end_z.get(),
                'eworld': self.seq_world_name.get(),
                'time': self.seq_fly_time.get(),
                'file': seq_filename,
                'manual_trajectory': manual_trajectory if manual_trajectory else None
            }

            # Log final antes de criar o arquivo
            if manual_trajectory:
                self.log(f"DEBUG: Criando SEQ com {len(manual_trajectory)} pontos intermediários")
            else:
                self.log("DEBUG: Criando SEQ com trajetória automática")

            # Criar arquivo SEQ usando o método existente
            self.create_seq_file("STANDALONE", seq_data)

            self.log(f"Arquivo SEQ standalone criado: {seq_filename}")
            self.log(f"Localização: {os.path.dirname(os.path.abspath(__file__))}")

            # Log detalhado da trajetória
            self.log(f"Trajetória criada:")
            self.log(
                f"  • Tempo 0: Início X={self.seq_start_x.get()}, Y={self.seq_start_y.get()}, Z={self.seq_start_z.get()}")

            if manual_trajectory:
                self.log(f"  • {len(manual_trajectory)} pontos intermediários:")
                for i, point in enumerate(manual_trajectory, 1):
                    self.log(f"    {i}. Tempo {point['time']}: X={point['x']}, Y={point['y']}, Z={point['z']}")
            else:
                self.log("  • Trajetória automática (sem pontos intermediários)")

            self.log(
                f"  • Tempo {total_time}: Destino X={self.seq_end_x.get()}, Y={self.seq_end_y.get()}, Z={self.seq_end_z.get()}")

            self.seq_window.destroy()
            messagebox.showinfo("Sucesso",
                                f"Arquivo SEQ criado com sucesso!\n\n"
                                f"Arquivo: {seq_filename}\n"
                                f"Localização: {os.path.dirname(os.path.abspath(__file__))}\n\n"
                                f"Trajetória: {'Personalizada' if manual_trajectory else 'Automática'}\n"
                                f"Pontos intermediários: {len(manual_trajectory) if manual_trajectory else 0}")

        except Exception as e:
            self.log(f"Erro ao criar arquivo SEQ standalone: {str(e)}")
            messagebox.showerror("Erro", f"Erro ao criar arquivo SEQ: {str(e)}")

    def update_trajectory_help_text(self):
        """Adiciona texto de ajuda na interface para esclarecer sobre a trajetória"""
        # Este método pode ser chamado na criação da interface para adicionar texto explicativo
        pass

def main():
    root = tk.Tk()
    app = FlypathManager(root)
    root.mainloop()


if __name__ == "__main__":
    main()