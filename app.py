import sys
import time
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QLabel, QPushButton, QScrollArea, QGroupBox, QHBoxLayout, QSizePolicy, QGridLayout
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFontDatabase, QFont
from PyQt5.QtGui import QFont, QColor
import requests
import subprocess
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QPainter, QLinearGradient

class PlanetPredictionApp(QWidget):
    def __init__(self):
        super().__init__()
        
        # Renk paleti tanımlamaları
        self.DARK_BG = "#121212"
        self.ACCENT_COLOR = "#FF6B35"  # Turuncu
        self.DARK_ACCENT = "#E84E10"   # Koyu turuncu
        self.TEXT_COLOR = "#F5F5F5"    # Beyaz
        self.SECONDARY_BG = "#1E1E1E"  # Biraz daha açık arkaplan
        self.DISABLED_COLOR = "#555555" # Devre dışı rengi
        
        # Ana sayfa gösterimi
        self.current_page = None
    
        font_id = QFontDatabase.addApplicationFont("Poppins-Regular.ttf")
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        font = QFont(font_family)
        self.initUI()
        
    # Gradyan arkaplan
    def paintEvent(self, event):
        painter = QPainter(self)
        # Koyu gradyan arka plan
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor(self.DARK_BG))  # Koyu arkaplan başlangıcı
        gradient.setColorAt(1, QColor("#252525"))  # Biraz daha açık koyu ton
        
        # Gradyanı kullanarak arka planı doldur
        painter.setBrush(gradient)
        painter.setPen(Qt.transparent)  # Kenarlık yok
        painter.drawRect(self.rect())  # Widget'ın tüm alanını doldur

    def initUI(self):
        font_id = QFontDatabase.addApplicationFont("Poppins-Regular.ttf")
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]

        font = QFont(font_family, 10)

        self.setWindowTitle('Crescent')
        self.setGeometry(0, 0, 1200, 900)
        self.setMinimumSize(800, 600)  # Minimum boyut tanımı

        font_id = QFontDatabase.addApplicationFont("Poppins-Regular.ttf")
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        self.font = QFont(font_family, 10)

        # Ekranı ortala
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        window_geometry = self.geometry()
        x = (screen_geometry.width() - window_geometry.width()) // 2
        y = (screen_geometry.height() - window_geometry.height()) // 2
        self.move(x, y)

        # Ana layout
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(20, 20, 20, 20)  # Kenar boşlukları
        self.main_layout.setSpacing(15)  # Öğeler arası boşluk
        
        # Navigasyon butonları için üst panel
        self.nav_layout = QHBoxLayout()
        self.nav_layout.setSpacing(10)  # Butonlar arası boşluk
        self.main_layout.addLayout(self.nav_layout)
        
        self.page_area = QVBoxLayout()
        self.main_layout.addLayout(self.page_area)

        # Sayfaları taşıyacak widget
        self.page_widget = QWidget()
        self.page_layout = QVBoxLayout()
        self.page_widget.setLayout(self.page_layout)
        self.main_layout.addWidget(self.page_widget)
        
        # ML sayfası için sonuç etiketi
        self.result_label = QLabel("")
        
        self.setLayout(self.main_layout)

        self.show_main_menu()  # Uygulama açılınca ANA MENÜ göster
        
    def setup_navigation(self):
        # Navigasyon butonlarını temizle
        while self.nav_layout.count():
            item = self.nav_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        
        # Ana menüde navigasyon butonlarını gösterme
        if self.current_page == 'menu':
            return
        
        # Diğer sayfalarda navigasyonu göster
        nav_button_style = f'padding: 12px 20px; background-color: {self.ACCENT_COLOR}; color: {self.TEXT_COLOR}; border: none; border-radius: 5px; font-weight: bold;'
        disabled_style = f'padding: 12px 20px; background-color: {self.DISABLED_COLOR}; color: {self.TEXT_COLOR}; border: none; border-radius: 5px; font-weight: bold;'
        
        back_button = QPushButton("Ana Menü")
        back_button.setFont(QFont(self.font.family(), 10))
        back_button.setStyleSheet(nav_button_style)
        back_button.setCursor(Qt.PointingHandCursor)  # El imleci
        back_button.clicked.connect(self.show_main_menu)
        self.nav_layout.addWidget(back_button)
        
        # Tüm sayfalarda gösterilecek navigasyon butonları
        # Şu anki sayfa için butonu devre dışı bırak
        merakli_button = QPushButton("Meraklısına")
        merakli_button.setFont(QFont(self.font.family(), 10))
        merakli_button.setStyleSheet(nav_button_style)
        merakli_button.setCursor(Qt.PointingHandCursor)
        merakli_button.clicked.connect(self.show_home_page)
        if self.current_page == 'home':
            merakli_button.setEnabled(False)
            merakli_button.setStyleSheet(disabled_style)
        self.nav_layout.addWidget(merakli_button)
        
        ml_button = QPushButton("ML Sayfası")
        ml_button.setFont(QFont(self.font.family(), 10))
        ml_button.setStyleSheet(nav_button_style)
        ml_button.setCursor(Qt.PointingHandCursor)
        ml_button.clicked.connect(self.show_ml_page)
        if self.current_page == 'ml':
            ml_button.setEnabled(False)
            ml_button.setStyleSheet(disabled_style)
        self.nav_layout.addWidget(ml_button)
        
        sim_button = QPushButton("Simülasyonu Oyna")
        sim_button.setFont(QFont(self.font.family(), 10))
        sim_button.setStyleSheet(nav_button_style)
        sim_button.setCursor(Qt.PointingHandCursor)
        sim_button.clicked.connect(self.run_exe)
        self.nav_layout.addWidget(sim_button)
        
        # Boşluk ekle
        self.nav_layout.addStretch()
        
    def show_main_menu(self):
        self.clear_layout()
        self.current_page = 'menu'
        
        # Navigasyon butonlarını güncelle - Ana menüde gösterme
        self.setup_navigation()

        menu_widget = QWidget()
        menu_layout = QVBoxLayout()
        menu_layout.setAlignment(Qt.AlignCenter)
        menu_layout.setSpacing(30)  # Menü öğeleri arası boşluk

        title = QLabel("Crescent")
        title.setFont(QFont(self.font.family(), 100, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"color: {self.TEXT_COLOR}; margin-bottom: 20px;")

        # Responsive tasarım için buton stilleri
        menu_button_style = f'''
            padding: 20px; 
            background-color: {self.ACCENT_COLOR}; 
            color: {self.TEXT_COLOR}; 
            border: none; 
            border-radius: 12px;
            font-weight: bold;
            min-width: 250px;
            max-width: 400px;
        '''

        play_button = QPushButton("Meraklısına")
        play_button.setFont(QFont(self.font.family(), 16))
        play_button.setStyleSheet(menu_button_style)
        play_button.setCursor(Qt.PointingHandCursor)
        play_button.clicked.connect(self.show_home_page)
        play_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

        ml_button = QPushButton("ML Sayfası")
        ml_button.setFont(QFont(self.font.family(), 16))
        ml_button.setStyleSheet(menu_button_style)
        ml_button.setCursor(Qt.PointingHandCursor)
        ml_button.clicked.connect(self.show_ml_page)
        ml_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        
        sim_button = QPushButton("Simülasyonu Oyna")
        sim_button.setFont(QFont(self.font.family(), 16))
        sim_button.setStyleSheet(menu_button_style)
        sim_button.setCursor(Qt.PointingHandCursor)
        sim_button.clicked.connect(self.run_exe)
        sim_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

        # Butonları içeren container
        button_container = QWidget()
        button_layout = QVBoxLayout(button_container)
        button_layout.setSpacing(15)
        
        button_layout.addWidget(sim_button, alignment=Qt.AlignCenter)
        button_layout.addWidget(ml_button, alignment=Qt.AlignCenter)
        button_layout.addWidget(play_button, alignment=Qt.AlignCenter)

        menu_layout.addWidget(title)
        menu_layout.addSpacing(20)
        menu_layout.addWidget(button_container)

        menu_widget.setLayout(menu_layout)
        self.page_layout.addWidget(menu_widget)
        
    def show_home_page(self):
        if self.current_page == 'home':
            return

        font_id = QFontDatabase.addApplicationFont("Poppins-Regular.ttf")
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        font = QFont(font_family, 14)  # Daha büyük font
    
        self.clear_layout()
        self.current_page = 'home'
        
        # Navigasyon butonlarını güncelle
        self.setup_navigation()
    
        # HTML içerik stilini düzelt - koyu tema için
        home_text = QLabel(f"""
            <h1 style="text-align:center; color:{self.TEXT_COLOR};"><b>MERAKLISINA</b></h1><br>
            <b style="color:{self.TEXT_COLOR};">ICP-OES Teknolojisinin Kimyasal Temeli:</b><br>
            <p style="color:{self.TEXT_COLOR};">ICP-OES, iyonize edilmiş bir plazmanın (çok yüksek sıcaklıkta bir gaz) kullanıldığı analitik bir tekniktir. Bu yöntem, örneklerin bileşimindeki elementlerin konsantrasyonlarını belirlerken, her elementin özgül bir emisyon ışığını yayması ilkesine dayanır. Gezegenden alınan kayaç örnekleri, önce yüksek sıcaklıkta bir plazmaya yerleştirilir, bu sıcaklık yeterince yüksektir ki, kayaçtaki atomlar iyonize olur ve bu iyonlar, kendi belirli dalga boylarında ışık yayar. Bu ışık, dedektörler tarafından ölçülür ve her elementin yoğunluğu, yayılan ışığın yoğunluğu ile doğru orantılıdır.</p><br>

            <b style="color:{self.TEXT_COLOR};">Makine Öğrenmesi ile Kimyasal Verilerin Değerlendirilmesi:</b><br>
            <p style="color:{self.TEXT_COLOR};">Makine öğrenmesi algoritmaları, ICP-OES verilerinin analizi için güçlü bir araçtır. Kayaçlardan elde edilen element yoğunlukları, makine öğrenmesi modeline giriş verisi olarak kullanılıyor. Model, bu kimyasal verileri analiz ederek gezegenin yaşanabilirlik, bilimsel geçerlilik ve madencilik potansiyeli hakkında tahminlerde bulunur. Verilerdeki karmaşık ilişkiler, geleneksel yöntemlerle zor bir şekilde çıkarılabilirken, makine öğrenmesi algoritmaları bu ilişkileri öğrenebilir ve doğru sonuçlar üretiyor.</p><br>

            <b style="color:{self.TEXT_COLOR};">Kimyasal Modelleme ve Gezegenin Bilimsel Geçerliliği:</b><br>
            <p style="color:{self.TEXT_COLOR};">Gezegenin yaşanabilirliği, bilimsel olarak değerlendirilebilecek kimyasal parametrelere dayalıdır. Elementlerin konsantrasyonları, gezegenin atmosferi, sıcaklık düzeni ve su varlığı ile doğrudan ilişkilidir. Örneğin, azot (N) ve oksijen (O) oranları, bir gezegenin atmosferinin kalitesini ve yaşam için uygun olup olmadığını belirlemede kullanılır. Bu kimyasal veriler, Mars'ın yaşam barındırma kapasitesini anlamamıza yardımcı olabilir.</p><br>

            <p style="color:{self.TEXT_COLOR};">Projemiz, Mars&rsquo;tan alınan kayaç örneklerini ICP-OES teknolojisiyle analiz ederek, gezegenin jeolojik yapısını, yaşanabilirlik potansiyelini ve madencilik açısından değerini belirlemeyi amaçlamaktadır. ICP-OES, kayaçlardan alınan element yoğunluklarını ölçerek, bu veriler üzerinden gezegenin kimyasal bileşimini ortaya koyar.</p><br>

            <p style="color:{self.TEXT_COLOR};">Makine öğrenmesi algoritmalarımız, ICP-OES&rsquo;den elde edilen verilerle gezegenin yaşanabilirlik ve bilimsel geçerlilik seviyelerini analiz etmekte kullanılmaktadır. Bu analizler, yüzdelik dilimlere dayalı olarak gezegenin yaşam koşullarını değerlendirir, bu sayede Mars&rsquo;ın madencilik ve bilimsel araştırma potansiyeli hakkında öngörülerde bulunulur. Bu proje, Mars&rsquo;tan alınacak kayaç örnekleri ile elde edilen verilerin, bilimsel olarak mümkün bir şekilde analiz edilebileceğini ve gezegenin potansiyelini anlamak için makine öğrenmesinin güçlü bir araç olabileceğini göstermektedir.</p><br>

            <p style="color:{self.TEXT_COLOR};">Projemiz tamamen açık kaynaklıdır; dilediğiniz gibi kullanabilir, geliştirebilir ve kendi projelerinize ilham kaynağı olarak ekleyebilirsiniz. Katkılarınızı görmekten büyük mutluluk duyarız!</p><br>
            <a href="https://github.com/mertcanyilmaz0/crescent" style="color:{self.ACCENT_COLOR}; font-weight: bold;">Github Linki</a>
        """)

        home_text.setWordWrap(True)
        home_text.setFont(font)
        home_text.setAlignment(Qt.AlignLeft)
        home_text.setOpenExternalLinks(True)
        home_widget = QWidget()
        layout = QVBoxLayout()
    
        # Scroll alanı stilleri
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet(f"""
            QScrollArea {{
                background: transparent;
                border: none;
            }}
            
            QScrollBar:vertical {{
                background: {self.SECONDARY_BG};
                width: 14px;
                border-radius: 7px;
            }}

            QScrollBar::handle:vertical {{
                background: {self.ACCENT_COLOR};
                border-radius: 7px;
                min-height: 30px;
            }}

            QScrollBar::handle:vertical:hover {{
                background: {self.DARK_ACCENT};
            }}

            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                background: none;
                height: 0px;
            }}
            
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}
        """)
        
        container_widget = QWidget()
        container_layout = QVBoxLayout()
        container_layout.setContentsMargins(30, 30, 30, 30)
    
        container_layout.addWidget(home_text)
        container_layout.addStretch()
    
        container_widget.setLayout(container_layout)
        container_widget.setStyleSheet("background-color: transparent;")
        scroll_area.setWidget(container_widget)
    
        layout.addWidget(scroll_area)
    
        home_widget.setLayout(layout)
        self.page_layout.addWidget(home_widget)

    def clear_layout(self):
        while self.page_layout.count():
            item = self.page_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def show_ml_page(self):
        if self.current_page == 'ml':
            return

        self.clear_layout()
        self.current_page = 'ml'

        self.setup_navigation()

        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet(f"""
            QScrollArea {{
                background: transparent;
                border: none;
            }}
            
            QScrollBar:vertical {{
                background: {self.SECONDARY_BG};
                width: 14px;
                border-radius: 7px;
            }}

            QScrollBar::handle:vertical {{
                background: {self.ACCENT_COLOR};
                border-radius: 7px;
                min-height: 30px;
            }}

            QScrollBar::handle:vertical:hover {{
                background: {self.DARK_ACCENT};
            }}

            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                background: none;
                height: 0px;
            }}
            
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}
        """)

        container_widget = QWidget()
        container_layout = QVBoxLayout()
        container_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        # İç widget (responsive genişlik için)
        inner_widget = QWidget()
        inner_layout = QVBoxLayout(inner_widget)
        inner_layout.setContentsMargins(30, 30, 30, 30)
        inner_layout.setSpacing(25)
        inner_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        # Fontlar
        font_id = QFontDatabase.addApplicationFont("Poppins-Regular.ttf")
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        title_font = QFont(font_family, 24, QFont.Bold)
        text_font = QFont(font_family, 14)
        label_font = QFont(font_family, 12)
        input_font = QFont(font_family, 12)
        button_font = QFont(font_family, 16, QFont.Bold)
        result_font = QFont(font_family, 16)

        # Sayfa başlığı
        self.ml_title = QLabel("Makine Öğrenmesi")
        self.ml_title.setFont(title_font)
        self.ml_title.setAlignment(Qt.AlignCenter)
        self.ml_title.setStyleSheet(f"color: {self.TEXT_COLOR}; margin-bottom: 20px;")
        inner_layout.addWidget(self.ml_title)

        # Açıklama metni
        self.ml_text = QLabel("Makine Öğrenmesi'nde RandomForest ve XGBoost algoritmaları kullanılmıştır. Bunun sebebi bu algoritmaların çok fazla verilerde en iyi şekilde yol izlemeleri, modellerin doğruluk oranı minimum %93 seviyesinde ve hata yapma payımız 0.0003 derecesinde neredeyse yok diyebiliriz. Bu makine öğrenmesinin veri tabanında 1500 tane gezegen kullanılmıştır.")
        self.ml_text.setFont(text_font)
        self.ml_text.setAlignment(Qt.AlignLeft)
        self.ml_text.setWordWrap(True)
        self.ml_text.setStyleSheet(f"color: {self.TEXT_COLOR}; padding: 10px;")
        inner_layout.addWidget(self.ml_text)

        # Element inputları
        self.inputs = {}
        elements = ['He', 'Ne', 'Cl', 'Mg', 'Ti', 'Fe', 'Ag', 'Ni', 'Si', 'Cu', 'Mn', 'Pt', 'U', 'Al', 'Ar', 'N', 'Zn', 'P', 'H', 'Ca', 'C', 'Cr', 'S', 'Li', 'Na', 'V']

        elements_group = QGroupBox("Element Yoğunlukları (%)")
        elements_group.setFont(label_font)
        elements_group.setStyleSheet(f"""
            QGroupBox {{
                background-color: {self.SECONDARY_BG}; 
                border-radius: 15px; 
                padding: 20px; 
                color: {self.TEXT_COLOR};
                font-weight: bold;
                margin-top: 15px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 10px;
            }}
        """)
        
        grid_layout = QGridLayout()
        grid_layout.setSpacing(15)
        grid_layout.setContentsMargins(15, 25, 15, 15)

        for i, element in enumerate(elements):
            row = i // 3
            col = i % 3

            label = QLabel(f'{element}:')
            label.setFont(label_font)
            label.setStyleSheet(f"color: {self.TEXT_COLOR};")
            grid_layout.addWidget(label, row, col * 2)

            input_field = QLineEdit(self)
            input_field.setPlaceholderText('0 - 100')
            input_field.setFont(input_font)
            input_field.setStyleSheet(f'''
                border: 1px solid #555; 
                padding: 8px; 
                border-radius: 8px; 
                background-color: {self.DARK_BG};
                color: {self.TEXT_COLOR};
            ''')
            input_field.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            grid_layout.addWidget(input_field, row, col * 2 + 1)
            self.inputs[element] = input_field

        elements_group.setLayout(grid_layout)
        inner_layout.addWidget(elements_group)

        # Sonuç etiketi
        self.result_label = QLabel("Sonuçlar burada görüntülenecek...")
        self.result_label.setFont(result_font)
        self.result_label.setWordWrap(True)
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setMaximumWidth(800)
        self.result_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        self.result_label.setStyleSheet(f"""
            color: {self.TEXT_COLOR}; 
            background-color: {self.SECONDARY_BG}; 
            padding: 20px; 
            border-radius: 15px; 
            margin-top: 20px;
        """)
        inner_layout.addWidget(self.result_label)

        # Tahmin butonu
        predict_button = QPushButton('Tahmin Yap')
        predict_button.setFont(button_font)
        predict_button.setMinimumWidth(200)
        predict_button.setMaximumWidth(300)
        predict_button.clicked.connect(self.predict)
        predict_button.setCursor(Qt.PointingHandCursor)
        predict_button.setStyleSheet(f'''
            background-color: {self.ACCENT_COLOR}; 
            color: {self.TEXT_COLOR}; 
            padding: 15px; 
            border-radius: 12px; 
            margin-top: 25px;
            font-weight: bold;
        ''')
        predict_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        inner_layout.addWidget(predict_button, alignment=Qt.AlignCenter)

        container_layout.addWidget(inner_widget)
        container_widget.setLayout(container_layout)
        container_widget.setStyleSheet("background: transparent;")
        scroll_area.setWidget(container_widget)

        self.page_layout.addWidget(scroll_area)

    def predict(self):
        # Kullanıcının girdiği değerleri al
        input_data = {}
        for element, input_field in self.inputs.items():
            text = input_field.text()
            try:
                value = float(text) if text else 0.0
                # Değer kontrolü
                if value < 0 or value > 100:
                    self.result_label.setText(f"Hata: '{element}' için 0-100 arasında bir değer giriniz.")
                    return
                input_data[element] = value
            except ValueError:
                self.result_label.setText(f"Hata: '{element}' için geçerli bir sayı giriniz.")
                return
        
        try:
            # API isteği gönderme
            response = requests.post('http://127.0.0.1:5000/predict', json=input_data)
            if response.status_code == 200:
                prediction = response.json()
                # Sonuç gösterimi
                result_text = f"""
                <h3 style='text-align:center;'>Tahmin Sonuçları</h3>
                <table style='width:100%; text-align:left; border-spacing:10px;'>
                    <tr>
                        <td><b>Yaşanabilirlik:</b></td>
                        <td>{round(prediction['life_score'] * 100, 2)}%</td>
                    </tr>
                    <tr>
                        <td><b>Bilimsel Geçerlilik:</b></td>
                        <td>{round(prediction['science_score'] * 100, 2)}%</td>
                    </tr>
                    <tr>
                        <td><b>Madencilik Potansiyeli:</b></td>
                        <td>{round(prediction['mining_score'] * 100, 2)}%</td>
                    </tr>
                    <tr>
                        <td><b>Başarı Skoru:</b></td>
                        <td>{round(prediction['success_score'] * 100, 2)}%</td>
                    </tr>
                </table>
                """
                self.result_label.setText(result_text)
            else:
                self.result_label.setText(f'Sunucudan geçerli bir cevap alınamadı. (Hata Kodu: {response.status_code})')
        except Exception as e:
            self.result_label.setText(f'Hata oluştu: {str(e)}. Lütfen sunucunun çalıştığından emin olun.')

    def run_exe(self):
        try:
            subprocess.Popen(["mars_simulation.exe"])  # EXE dosyasının ismi ve yolu
        except Exception as e:
            print(f"Exe çalıştırılırken hata: {e}")
            self.show_error_message(f"Simülasyon başlatılamadı: {str(e)}")
    
    def show_error_message(self, message):
        # Basit hata mesajı gösterimi
        error_dialog = QLabel(message)
        error_dialog.setStyleSheet(f"color: #FF4444; background-color: {self.SECONDARY_BG}")
api_process = subprocess.Popen(["python", "api.py"])
time.sleep(2)  # 2 saniye bekle
if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('crescent.ico'))
    ex = PlanetPredictionApp()
    ex.show()
    sys.exit(app.exec_())
