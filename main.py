from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.button import MDFillRoundFlatButton, MDRectangleFlatButton, MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.card import MDCard
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.toast import toast
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import StringProperty, BooleanProperty
from kivy.utils import platform
from kivy.metrics import dp

import os
import time
import subprocess
import urllib.request
import threading
import datetime
import requests
import shutil

# --- CONFIGURATION & PATHS ---
CURRENT_VERSION = "12.0"
REPO_USER = "Attc2834"
REPO_NAME = "ATTC-Project"
VERSION_URL = f"https://raw.githubusercontent.com/{REPO_USER}/{REPO_NAME}/main/version.txt"
UPDATE_CODE_URL = f"https://raw.githubusercontent.com/{REPO_USER}/{REPO_NAME}/main/main.py"

PKG_GLOBAL = "com.tencent.ig"
PKG_KORE = "com.pubg.krmobile"
PKG_VNG = "com.vng.pubgmobile"
PKG_TW = "com.rekoo.pubgm"

if platform == 'android':
    from android.storage import primary_external_storage_path
    from android.permissions import request_permissions, Permission
    from jnius import autoclass

    APP_FOLDER = os.path.dirname(os.path.abspath(__file__))
    RISH_PATH = os.path.join(APP_FOLDER, "rish")
    DEX_PATH = os.path.join(APP_FOLDER, "rish_shizuku.dex")

    USER_DOWNLOAD_DIR = os.path.join(primary_external_storage_path(), "Download")
    EXTERNAL_RISH_SOURCE = os.path.join(USER_DOWNLOAD_DIR, "rish")
    EXTERNAL_DEX_SOURCE = os.path.join(USER_DOWNLOAD_DIR, "rish_shizuku.dex")

    SEARCH_DIR = USER_DOWNLOAD_DIR
    BACKUP_DIR = os.path.join(primary_external_storage_path(), "Attc_Backups")
else:
    SEARCH_DIR = "."
    BACKUP_DIR = "./Backups"
    APP_FOLDER = os.path.dirname(os.path.abspath(__file__))
    RISH_PATH = "./rish"
    DEX_PATH = "./rish_shizuku.dex"
    EXTERNAL_RISH_SOURCE = "./rish_source"
    EXTERNAL_DEX_SOURCE = "./dex_source"

# --- KV LANG UI DEFINITION ---
KV = '''
<SectionCard@MDCard>:
    orientation: "vertical"
    padding: dp(15)
    spacing: dp(10)
    size_hint_y: None
    height: self.minimum_height
    radius: [15]
    elevation: 2
    md_bg_color: 0.1, 0.1, 0.1, 1

<SectionHeader@MDLabel>:
    halign: "left"
    theme_text_color: "Custom"
    text_color: app.theme_cls.primary_color
    font_style: "H6"
    bold: True
    size_hint_y: None
    height: self.texture_size[1] + dp(10)

MDScreen:
    MDBoxLayout:
        orientation: 'vertical'
        md_bg_color: 0.05, 0.05, 0.05, 1

        MDTopAppBar:
            title: "ATTC Studio v" + app.version
            elevation: 4
            right_action_items: [["refresh", lambda x: app.check_for_updates()]]
            md_bg_color: 0.8, 0, 0, 1  # Dark Red

        MDScrollView:
            do_scroll_x: False
            MDBoxLayout:
                orientation: 'vertical'
                adaptive_height: True
                padding: dp(15)
                spacing: dp(20)

                # --- UPDATE CARD ---
                MDCard:
                    id: update_card
                    orientation: "vertical"
                    size_hint_y: None
                    height: "0dp"
                    opacity: 0
                    padding: dp(10)
                    md_bg_color: 0, 0.3, 0, 1
                    radius: [10]

                    MDLabel:
                        id: update_label
                        text: "Yeni Güncelleme Mevcut!"
                        halign: "center"
                        theme_text_color: "Custom"
                        text_color: 0, 1, 0, 1
                        bold: True

                    MDFillRoundFlatButton:
                        text: "YÜKLE VE YENİDEN BAŞLAT"
                        pos_hint: {"center_x": .5}
                        md_bg_color: 0, 0.5, 0, 1
                        on_release: app.perform_update()

                # --- TARGET SYSTEM ---
                SectionCard:
                    SectionHeader:
                        text: "Hedef Sistem"

                    MDGridLayout:
                        cols: 2
                        adaptive_height: True
                        spacing: dp(10)

                        MDRectangleFlatButton:
                            text: "🌍 GLOBAL"
                            size_hint_x: 1
                            line_color: 1, 0, 0, 1
                            text_color: 1, 1, 1, 1
                            on_release: app.setup_game(app.PKG_GLOBAL, "GLOBAL")

                        MDRectangleFlatButton:
                            text: "🇰🇷 KORE"
                            size_hint_x: 1
                            line_color: 1, 0, 0, 1
                            text_color: 1, 1, 1, 1
                            on_release: app.setup_game(app.PKG_KORE, "KORE")

                        MDRectangleFlatButton:
                            text: "🇻🇳 VIETNAM"
                            size_hint_x: 1
                            line_color: 1, 0, 0, 1
                            text_color: 1, 1, 1, 1
                            on_release: app.setup_game(app.PKG_VNG, "VIETNAM")

                        MDRectangleFlatButton:
                            text: "🇹🇼 TAIWAN"
                            size_hint_x: 1
                            line_color: 1, 0, 0, 1
                            text_color: 1, 1, 1, 1
                            on_release: app.setup_game(app.PKG_TW, "TAIWAN")

                # --- DATA ANALYSIS ---
                SectionCard:
                    SectionHeader:
                        text: "Veri Analizi & Config"

                    MDBoxLayout:
                        adaptive_height: True
                        spacing: dp(10)

                        MDFillRoundFlatButton:
                            id: btn_scan
                            text: "🔍 TARAMA BAŞLAT"
                            size_hint_x: 0.4
                            disabled: True
                            md_bg_color: 0.6, 0, 0, 1
                            on_release: app.start_scan()

                        MDRectangleFlatButton:
                            id: btn_select_config
                            text: "Config Seçilmedi"
                            size_hint_x: 0.6
                            disabled: True
                            text_color: 1, 1, 1, 1
                            line_color: 0.5, 0.5, 0.5, 1
                            on_release: app.open_menu(self)

                # --- MOD INJECTION ---
                SectionCard:
                    SectionHeader:
                        text: "Mod Enjeksiyon"

                    MDGridLayout:
                        cols: 3
                        adaptive_height: True
                        spacing: dp(5)

                        MDFillRoundFlatButton:
                            id: btn_giris
                            text: "🚀 GİRİŞ"
                            disabled: True
                            size_hint_x: 1
                            md_bg_color: 0.2, 0, 0, 1
                            on_release: app.install_mod("giris", "GİRİŞ")

                        MDFillRoundFlatButton:
                            id: btn_lobi
                            text: "🏠 LOBİ"
                            disabled: True
                            size_hint_x: 1
                            md_bg_color: 0.2, 0, 0, 1
                            on_release: app.install_mod("lobi", "LOBİ")

                        MDFillRoundFlatButton:
                            id: btn_ada
                            text: "🏝️ ADA"
                            disabled: True
                            size_hint_x: 1
                            md_bg_color: 0.2, 0, 0, 1
                            on_release: app.install_mod("ada", "ADA")

                # --- CONTENT MANAGER ---
                SectionCard:
                    SectionHeader:
                        text: "Content Manager"

                    MDFillRoundFlatButton:
                        id: btn_content_install
                        text: "📥 CONTENT'İ HEDEFE AT"
                        disabled: True
                        size_hint_x: 1
                        md_bg_color: 0, 0.5, 0.5, 1
                        on_release: app.install_content()

                    MDBoxLayout:
                        adaptive_height: True
                        spacing: dp(10)

                        MDRectangleFlatButton:
                            id: btn_content_off
                            text: "🔴 Content1 Yap"
                            disabled: True
                            size_hint_x: 0.5
                            text_color: 1, 0.5, 0.5, 1
                            line_color: 1, 0.5, 0.5, 1
                            on_release: app.rename_content_folder("content1")

                        MDRectangleFlatButton:
                            id: btn_content_on
                            text: "🟢 Content Yap"
                            disabled: True
                            size_hint_x: 0.5
                            text_color: 0.5, 1, 0.5, 1
                            line_color: 0.5, 1, 0.5, 1
                            on_release: app.rename_content_folder("content")

                # --- SYSTEM TOOLS ---
                SectionCard:
                    SectionHeader:
                        text: "Sistem Araçları"

                    MDBoxLayout:
                        adaptive_height: True
                        spacing: dp(10)

                        MDFillRoundFlatButton:
                            id: btn_clean
                            text: "🧹 TEMİZLE"
                            size_hint_x: 0.5
                            md_bg_color: 0.8, 0.6, 0, 1
                            on_release: app.cleaner()

                        MDFillRoundFlatButton:
                            id: btn_backup
                            text: "💾 YEDEKLE"
                            size_hint_x: 0.5
                            md_bg_color: 0.7, 0, 0, 1
                            on_release: app.backup()

                # --- LOGS ---
                SectionCard:
                    padding: dp(10)
                    md_bg_color: 0.08, 0.08, 0.08, 1

                    MDLabel:
                        text: "Sistem Logları:"
                        font_style: "Caption"
                        theme_text_color: "Secondary"
                        size_hint_y: None
                        height: dp(20)

                    MDScrollView:
                        size_hint_y: None
                        height: dp(100)
                        do_scroll_x: False

                        MDLabel:
                            text: app.log_text
                            font_style: "Body2"
                            font_size: "11sp"
                            theme_text_color: "Custom"
                            text_color: 0, 1, 0, 1
                            size_hint_y: None
                            height: self.texture_size[1]
'''

class AttcStudioApp(MDApp):
    version = StringProperty(CURRENT_VERSION)
    log_text = StringProperty("Sistem Başlatıldı...\n")

    selected_config_path = StringProperty("")
    target_base_path = StringProperty("")
    menu = None

    # Package Constants
    PKG_GLOBAL = PKG_GLOBAL
    PKG_KORE = PKG_KORE
    PKG_VNG = PKG_VNG
    PKG_TW = PKG_TW

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Red"
        self.theme_cls.accent_palette = "Red"
        # Optional: Set material_style="M3" if using newer KivyMD versions that support it well
        # self.theme_cls.material_style = "M3"
        return Builder.load_string(KV)

    def on_start(self):
        self.request_all_permissions()
        self.check_files()
        self.check_for_updates()

    # --- LOGGING ---
    def write_log(self, msg):
        timestamp = time.strftime('%H:%M')
        Clock.schedule_once(lambda dt: self._update_log(f"> [{timestamp}] {msg}"))

    def _update_log(self, new_line):
        self.log_text += new_line + "\n"

    # --- PERMISSIONS & FILE SETUP ---
    def request_all_permissions(self):
        """Requests necessary permissions for Android."""
        if platform == 'android':
            try:
                # 1. SHIZUKU PERMISSION
                self.write_log("🔑 Shizuku İzni İsteniyor...")
                request_permissions([
                    Permission.WRITE_EXTERNAL_STORAGE,
                    Permission.READ_EXTERNAL_STORAGE,
                    "moe.shizuku.manager.permission.API_V23"
                ])

                # 2. MANAGE ALL FILES PERMISSION (Android 11+)
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                Environment = autoclass('android.os.Environment')
                Intent = autoclass('android.content.Intent')
                Settings = autoclass('android.provider.Settings')
                Uri = autoclass('android.net.Uri')

                if not Environment.isExternalStorageManager():
                    intent = Intent()
                    intent.setAction(Settings.ACTION_MANAGE_APP_ALL_FILES_ACCESS_PERMISSION)
                    uri = Uri.fromParts("package", PythonActivity.mActivity.getPackageName(), None)
                    intent.setData(uri)
                    PythonActivity.mActivity.startActivity(intent)
                    toast("Lütfen DOSYA Erişim İznini Verin!")
                else:
                    self.write_log("✅ Dosya İzni Tamam.")
            except Exception as e:
                self.write_log(f"❌ İzin Hatası: {e}")

    def check_files(self):
        """Checks for 'rish' and 'dex' files, copies them if missing."""
        rish_ok = False
        dex_ok = False

        # Rish Check
        if os.path.exists(RISH_PATH) and os.path.getsize(RISH_PATH) > 500:
            rish_ok = True
        else:
            try: os.remove(RISH_PATH)
            except: pass

        # Dex Check
        if os.path.exists(DEX_PATH) and os.path.getsize(DEX_PATH) > 500:
            dex_ok = True
        else:
            try: os.remove(DEX_PATH)
            except: pass

        if rish_ok and dex_ok:
             try:
                 os.chmod(RISH_PATH, 0o755) # Execution permission
                 self.write_log("✅ Sistem Dosyaları Hazır.")
             except: pass
        else:
            # Try copying from Download folder
            self.copy_files_from_download()

    def copy_files_from_download(self):
        """Copies required files from the user's Download folder."""
        self.write_log(f"📂 'Download' klasöründe dosyalar aranıyor...")

        found_count = 0

        # 1. Copy Rish
        if os.path.exists(EXTERNAL_RISH_SOURCE):
            try:
                shutil.copyfile(EXTERNAL_RISH_SOURCE, RISH_PATH)
                os.chmod(RISH_PATH, 0o755)
                found_count += 1
                self.write_log("✅ 'rish' kopyalandı.")
            except Exception as e:
                self.write_log(f"❌ Rish Kopyalama Hatası: {e}")
        else:
             self.write_log("❌ 'rish' dosyası bulunamadı!")

        # 2. Copy Dex
        if os.path.exists(EXTERNAL_DEX_SOURCE):
            try:
                shutil.copyfile(EXTERNAL_DEX_SOURCE, DEX_PATH)
                found_count += 1
                self.write_log("✅ 'rish_shizuku.dex' kopyalandı.")
            except Exception as e:
                 self.write_log(f"❌ Dex Kopyalama Hatası: {e}")
        else:
             self.write_log("❌ 'rish_shizuku.dex' dosyası bulunamadı!")

        if found_count == 2:
            toast("Dosyalar Başarıyla Yüklendi!")
        else:
            self.write_log("⚠️ EKSİK DOSYA VAR!")
            self.write_log("Lütfen 'rish' ve 'rish_shizuku.dex' dosyalarını")
            self.write_log("telefonunuzun 'Download' klasörüne atın.")

    def run_cmd(self, cmd):
        """Executes a shell command using rish (Shizuku)."""
        pkg_name = "com.attc.attcstudio" # Must match package name in buildozer.spec
        full_cmd = f"export RISH_APPLICATION_ID={pkg_name} && sh {RISH_PATH} -c '{cmd}' 2>&1"

        try:
            res = subprocess.run(full_cmd, shell=True, capture_output=True, text=True)
            return res.returncode, res.stdout
        except Exception as e:
            return -1, str(e)

    # --- UI LOGIC ---
    def setup_game(self, pkg, name):
        """Sets the target game package and enables relevant buttons."""
        self.target_base_path = f"/storage/emulated/0/Android/data/{pkg}"

        # Enable buttons
        self.root.ids.btn_scan.disabled = False
        self.root.ids.btn_clean.disabled = False
        self.root.ids.btn_backup.disabled = False

        self.write_log(f"🎯 Hedef: {name}")
        toast(f"Hedef: {name}")

    def start_scan(self):
        """Starts scanning for config folders in a thread."""
        self.root.ids.btn_scan.text = "⏳ Taranıyor..."
        threading.Thread(target=self._scan_thread).start()

    def _scan_thread(self):
        found = []
        try:
            for root, dirs, files in os.walk(SEARCH_DIR):
                dname = os.path.basename(root)
                if "attc" in dname.lower():
                    found.append({"text": dname, "path": root})
        except Exception as e:
            self.write_log(f"❌ Tarama Hatası: {e}")

        Clock.schedule_once(lambda dt: self._scan_finished(found))

    def _scan_finished(self, found):
        if found:
            self.root.ids.btn_scan.text = f"✅ {len(found)} KLASÖR"
            self.root.ids.btn_scan.md_bg_color = (0, 0.6, 0, 1)
            self.root.ids.btn_select_config.disabled = False
            self.root.ids.btn_select_config.text = "Seçim Yapınız"

            menu_items = [
                {
                    "text": item["text"],
                    "viewclass": "OneLineListItem",
                    "on_release": lambda x=item: self.set_config(x),
                } for item in found
            ]
            self.menu = MDDropdownMenu(caller=self.root.ids.btn_select_config, items=menu_items, width_mult=4)
            self.write_log(f"📂 {len(found)} adet bulundu.")
        else:
            self.root.ids.btn_scan.text = "❌ YOK"
            self.root.ids.btn_scan.md_bg_color = (0.6, 0, 0, 1)
            self.write_log("❌ Klasör bulunamadı.")

    def open_menu(self, button):
        if self.menu:
            self.menu.open()

    def set_config(self, item):
        self.selected_config_path = item["path"]
        self.root.ids.btn_select_config.text = item["text"]
        self.menu.dismiss()
        self.analyze_config(self.selected_config_path)

    def analyze_config(self, path):
        """Analyzes the selected config folder to enable available mods."""
        ids = self.root.ids

        # Reset buttons
        ids.btn_giris.disabled = True
        ids.btn_lobi.disabled = True
        ids.btn_ada.disabled = True
        ids.btn_content_install.disabled = True
        ids.btn_content_off.disabled = True
        ids.btn_content_on.disabled = True

        has_giris, has_lobi, has_ada, has_content = False, False, False, False

        try:
            items = os.listdir(path)
            for item in items:
                name_low = item.lower()
                if "giris" in name_low: has_giris = True
                if "lobi" in name_low: has_lobi = True
                if "ada" in name_low: has_ada = True
                if name_low in ["content", "content1"]: has_content = True
        except Exception as e:
            self.write_log(f"❌ Analiz Hatası: {e}")

        # Enable buttons based on findings
        if has_giris: ids.btn_giris.disabled = False
        if has_lobi: ids.btn_lobi.disabled = False
        if has_ada: ids.btn_ada.disabled = False

        if has_content:
            ids.btn_content_install.disabled = False
            ids.btn_content_off.disabled = False
            ids.btn_content_on.disabled = False
            self.write_log("✅ Content algılandı.")

    # --- ACTION HANDLERS ---
    def install_mod(self, key, name):
        if not self.selected_config_path: return
        self.write_log(f"⏳ {name} yükleniyor...")
        threading.Thread(target=self._install_worker, args=(key, name)).start()

    def _install_worker(self, key, name):
        target_src = None
        for item in os.listdir(self.selected_config_path):
            if key in item.lower():
                target_src = os.path.join(self.selected_config_path, item)
                break

        if target_src:
            dst_files = os.path.join(self.target_base_path, "files")
            src_path = target_src

            # If the source is a directory containing 'files', use that inner 'files'
            if os.path.isdir(target_src) and "files" in os.listdir(target_src):
                src_path = os.path.join(target_src, "files")

            # Construct copy command
            cmd = f"cp -rf \"{src_path}/.\" \"{dst_files}/\"" if os.path.isdir(src_path) else f"cp -rf \"{src_path}\" \"{dst_files}/\""

            code, out = self.run_cmd(cmd)
            if code == 0:
                self.run_cmd(f"chmod -R 777 \"{dst_files}\"")
                self.write_log(f"✅ {name} BAŞARILI!")
                Clock.schedule_once(lambda dt: toast(f"{name} Kuruldu"))
            else:
                self.write_log(f"❌ Hata: {out}")
        else:
            self.write_log(f"⚠️ Dosya bulunamadı: {key}")

    def install_content(self):
        self.write_log("⏳ Content kuruluyor...")
        threading.Thread(target=self._content_worker).start()

    def _content_worker(self):
        src_content = None
        for item in os.listdir(self.selected_config_path):
            if item.lower() in ["content", "content1"]:
                src_content = os.path.join(self.selected_config_path, item)
                break

        if src_content:
            dst_base = os.path.join(self.target_base_path, "files/UE4Game/ShadowTrackerExtra/ShadowTrackerExtra")
            self.run_cmd(f"rm -rf \"{dst_base}/content\"")
            self.run_cmd(f"rm -rf \"{dst_base}/content1\"")

            code, out = self.run_cmd(f"cp -rf \"{src_content}\" \"{dst_base}/\"")
            if code == 0:
                self.write_log("✅ Content Kuruldu.")
            else:
                self.write_log(f"❌ Hata: {out}")

    def rename_content_folder(self, new_name):
        self.write_log(f"🔄 İsim değiştiriliyor -> {new_name}")
        threading.Thread(target=self._rename_worker, args=(new_name,)).start()

    def _rename_worker(self, target_name):
        base_path = os.path.join(self.target_base_path, "files/UE4Game/ShadowTrackerExtra/ShadowTrackerExtra")
        current_content = os.path.join(base_path, "content")
        current_content1 = os.path.join(base_path, "content1")

        cmd = ""
        if target_name == "content1":
            cmd = f"mv \"{current_content}\" \"{current_content1}\""
        elif target_name == "content":
            cmd = f"mv \"{current_content1}\" \"{current_content}\""

        code, out = self.run_cmd(cmd)
        if code == 0:
            self.write_log(f"✅ Klasör: {target_name}")
        else:
            self.write_log("⚠️ İşlem başarısız.")

    def cleaner(self):
        self.write_log("🧹 Temizlik başladı...")
        threading.Thread(target=self._cleaner_worker).start()

    def _cleaner_worker(self):
        base = os.path.join(self.target_base_path, "files/UE4Game/ShadowTrackerExtra/ShadowTrackerExtra/Saved/Paks")
        targets = ["ODPaks", "puffer_temp", "game_patch_4.2.0.20753.pak", "game_patch_4.2.0.20763.pak"]

        for t in targets:
            self.run_cmd(f"rm -rf \"{os.path.join(base, t)}\"")

        self.write_log("✨ Temizlik Bitti.")

    def backup(self):
        self.write_log("📦 Yedekleme başladı...")
        threading.Thread(target=self._backup_worker).start()

    def _backup_worker(self):
        src = os.path.join(self.target_base_path, "files/UE4Game/ShadowTrackerExtra/ShadowTrackerExtra/Saved")
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        dst = os.path.join(BACKUP_DIR, f"Backup_{ts}")

        self.run_cmd(f"mkdir -p \"{BACKUP_DIR}\"")
        self.run_cmd(f"cp -rf \"{src}\" \"{dst}\"")

        self.write_log(f"✅ Yedek Alındı.")

    # --- UPDATE SYSTEM ---
    def check_for_updates(self):
        threading.Thread(target=self._update_check_thread).start()

    def _update_check_thread(self):
        try:
            with urllib.request.urlopen(VERSION_URL) as response:
                remote_version = response.read().decode('utf-8').strip()

            if remote_version != CURRENT_VERSION:
                Clock.schedule_once(lambda dt: self._show_update_card(remote_version))
            else:
                self.write_log(f"✅ Sürüm Güncel (v{CURRENT_VERSION})")
        except:
            pass

    def _show_update_card(self, new_ver):
        self.root.ids.update_card.height = "100dp"
        self.root.ids.update_card.opacity = 1
        self.root.ids.update_label.text = f"YENİ SÜRÜM: v{new_ver}"
        self.write_log(f"🔥 GÜNCELLEME VAR: v{new_ver}")

    def perform_update(self):
        self.write_log("⏳ İndiriliyor...")
        threading.Thread(target=self._download_update).start()

    def _download_update(self):
        try:
            response = requests.get(UPDATE_CODE_URL)
            with open("update_tmp.py", "wb") as f:
                f.write(response.content)

            current_file = os.path.abspath(__file__)
            os.replace("update_tmp.py", current_file)

            self.write_log("✅ GÜNCELLEME BİTTİ. YENİDEN BAŞLATIN.")
            time.sleep(2)
            os._exit(0)
        except Exception as e:
            self.write_log(f"❌ Hata: {e}")

if __name__ == "__main__":
    AttcStudioApp().run()
