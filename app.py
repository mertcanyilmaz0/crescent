import sys
import time
import random
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QLabel, QPushButton, QScrollArea, QGroupBox, QHBoxLayout, QSizePolicy, QGridLayout
from PyQt5.QtCore import Qt, QSize, QPoint
from PyQt5.QtGui import QFontDatabase, QFont
from PyQt5.QtGui import QFont, QColor
import requests
import subprocess
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QPainter, QLinearGradient

class CustomTitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setFixedHeight(30)  # Özel başlık çubuğunun yüksekliği
        self.setStyleSheet("background-color: #1E1E1E; color: #F5F5F5;")
        self.title_label = QLabel("Crescent", self)
        self.title_label.setStyleSheet("color: #F5F5F5; margin-left: 10px;background-color: transparent;")
        self.close_button = QPushButton("✕", self)
        self.minimize_button = QPushButton("−", self)
        self.maximize_button = QPushButton("□", self)
        self.control_button_style = """
            QPushButton {
                background-color: transparent;
                color: #F5F5F5;
                border: none;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #555555;
            }
        """
        self.close_button.setStyleSheet(self.control_button_style)
        self.minimize_button.setStyleSheet(self.control_button_style)
        self.maximize_button.setStyleSheet(self.control_button_style)
        self.close_button.clicked.connect(self.parent().close)
        self.minimize_button.clicked.connect(self.parent().showMinimized)
        self.maximize_button.clicked.connect(self.toggleMaximized)

        layout = QHBoxLayout(self)
        layout.addWidget(self.title_label)
        layout.addStretch()
        layout.addWidget(self.minimize_button)
        layout.addWidget(self.maximize_button)
        layout.addWidget(self.close_button)
        layout.setContentsMargins(5, 0, 5, 0)

        self.start_pos = None
        self.is_maximized = False

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start_pos = event.globalPos()
            self.window_pos = self.parent().frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self.start_pos:
            delta = QPoint(event.globalPos() - self.start_pos)
            self.parent().move(self.window_pos + delta)

    def mouseReleaseEvent(self, event):
        self.start_pos = None

    def mouseDoubleClickEvent(self, event):
        self.toggleMaximized()

    def toggleMaximized(self):
        if self.is_maximized:
            self.parent().showNormal()
            self.is_maximized = False
            self.maximize_button.setText("□")
        else:
            self.parent().showMaximized()
            self.is_maximized = True
            self.maximize_button.setText("⧉")  # Maximize ikonu

class PlanetPredictionApp(QWidget):
    def __init__(self):
        super().__init__()
        self.DARK_BG = "#121212"
        self.ACCENT_COLOR = "#B33C1A"
        self.DARK_ACCENT ="#80280F"
        self.TEXT_COLOR = "#F5F5F5"
        self.SECONDARY_BG = "#1E1E1E"
        self.DISABLED_COLOR = "#555555"
        
        self.current_page = None
    
        font_id = QFontDatabase.addApplicationFont("Poppins-Regular.ttf")
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        font = QFont(font_family)
        self.initUI()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor(self.DARK_BG))
        gradient.setColorAt(1, QColor("#252525"))
        painter.setBrush(gradient)
        painter.setPen(Qt.transparent)
        painter.drawRect(self.rect())

    def initUI(self):
        font_id = QFontDatabase.addApplicationFont("Poppins-Regular.ttf")
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        self.font = QFont(font_family, 10)

        self.setWindowTitle('Crescent')
        self.setGeometry(0, 0, 1000, 800)
        self.setMinimumSize(800, 600)
        
        # Frameless window için bayrak ekle
        self.setWindowFlags(Qt.FramelessWindowHint)

        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        window_geometry = self.geometry()
        x = (screen_geometry.width() - window_geometry.width()) // 2
        y = (screen_geometry.height() - window_geometry.height()) // 2
        self.move(x, y)

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)  # Kenar boşlukları
        self.main_layout.setSpacing(0)  # Öğeler arası boşluk
        
        # Özel başlık çubuğunu ekle
        self.title_bar = CustomTitleBar(self)
        self.main_layout.addWidget(self.title_bar)
        
        self.nav_layout = QHBoxLayout()
        self.nav_layout.setSpacing(10)
        self.main_layout.addLayout(self.nav_layout)
        
        self.page_area = QVBoxLayout()
        self.main_layout.addLayout(self.page_area)

        self.page_widget = QWidget()
        self.page_layout = QVBoxLayout()
        self.page_widget.setLayout(self.page_layout)
        self.main_layout.addWidget(self.page_widget)
        
        self.result_label = QLabel("")
        
        self.setLayout(self.main_layout)

        self.show_main_menu()
        self.showMaximized()  # Görev çubuğunu gizlemeden ekranı kapla
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

    <b style="color:{self.TEXT_COLOR};">ICP-OES Teknolojisinin Kimyasal ve Spektroskopik Temelleri:</b><br>
    <p style="color:{self.TEXT_COLOR};">
    ICP-OES (Inductively Coupled Plasma Optical Emission Spectrometry), çok elementli, yüksek hassasiyetli analizler yapabilen bir atomik spektroskopi tekniğidir. Bu yöntemde, numuneler önce sıvı hâline getirilir ve ardından aerosol hâline dönüştürülerek argon gazı taşıyıcılığında yüksek sıcaklıklı plazma torcuna yönlendirilir. Plazma yaklaşık 6000-10000 K sıcaklığa sahiptir ve bu enerji, atomları iyonlaştırarak uyarılmış hâle getirir. Uyarılmış atom ve iyonlar temel hâllerine dönerken kendilerine özgü elektromanyetik ışınımlar (emisyonlar) yayar. Bu ışınımlar optik sistemler ve fotodedektörlerle analiz edilerek her bir elementin dalga boyu ve yoğunluğu belirlenir. Böylece, numunedeki her elementin konsantrasyonu yüksek doğrulukla hesaplanabilir. ICP-OES, özellikle jeolojik, çevresel ve uzay araştırmalarında yaygın olarak kullanılmaktadır çünkü hem çok düşük tespit sınırlarına sahiptir hem de çok sayıda elementi aynı anda analiz etme kapasitesine olanak tanır.</p><br>

    <b style="color:{self.TEXT_COLOR};">Makine Öğrenmesi Yaklaşımları ile Kimyasal Verilerin Modellemesi:</b><br>
    <p style="color:{self.TEXT_COLOR};">
    ICP-OES cihazı ile elde edilen yüksek boyutlu element yoğunluk verileri, istatistiksel analizlerin ötesine geçerek, karmaşık örüntülerin keşfi için makine öğrenmesi algoritmalarıyla işlenmektedir. Bu projede, Random Forest ve XGBoost gibi denetimli öğrenme algoritmaları kullanılmıştır. Random Forest, çok sayıda karar ağacının rastgele alt örneklemlemeyle birleştirilmesiyle oluşturulan bir topluluk (ensemble) yöntemidir. Bu yapı, aşırı öğrenme (overfitting) riskini azaltırken genel doğruluk oranını artırır. XGBoost ise gradyan artırmalı karar ağaçlarını optimize eden, yüksek performanslı bir algoritmadır ve özellikle küçük ama karmaşık veri kümelerinde son derece etkilidir. Her iki algoritma da bu projede, ICP-OES analizinden elde edilen sayısal veriler üzerinden gezegenin yaşanabilirlik potansiyelini, bilimsel geçerliliğini ve madencilik açısından ekonomik değerini tahmin etmek için eğitilmiştir. Modellerin doğruluk oranı %93’ün üzerinde, ortalama hata oranı ise 0.0003 seviyesindedir.</p><br>

    <b style="color:{self.TEXT_COLOR};">Gezegensel Yaşanabilirliğin Kimyasal Parametrelerle Değerlendirilmesi:</b><br>
    <p style="color:{self.TEXT_COLOR};">
    Bir gezegenin yaşama elverişliliği, yüzey ve atmosfer bileşiminin biyolojik süreçleri destekleyip desteklemediğine bağlı olarak kimyasal düzeyde değerlendirilebilir. ICP-OES ile ölçülen azot (N), oksijen (O), karbon (C), fosfor (P), sülfür (S), hidrojen (H), demir (Fe), magnezyum (Mg) ve potasyum (K) gibi temel elementlerin oranları, biyolojik süreçlerin sürdürülebilirliği ve fotosentetik canlılık potansiyelinin değerlendirilmesi açısından önemlidir. Örneğin; oksijen ve azot oranları, atmosferik stabilitenin yanı sıra oksijen solunumuna dayalı yaşamın sürdürülebilirliğini gösterirken; fosfor ve karbon, hücresel yapıların inşasında ve enerji metabolizmasında merkezi rol oynar. Bu elementlerin ideal aralıkta bulunması, gezegenin yaşanabilirliğine yönelik pozitif bir gösterge olarak değerlendirilir.</p><br>

    <p style="color:{self.TEXT_COLOR};">
    Projemizde, Mars’tan alınmış örnek veriler kullanılarak ICP-OES analizi yapılmakta ve makine öğrenmesiyle elde edilen çıktılar, gezegenin yaşanabilirlik, bilimsel öneme sahiplik ve ekonomik kaynak potansiyeli açısından sistematik olarak değerlendirilmektedir. Bu değerlendirme, kimyasal kompozisyon ile jeofiziksel koşullar arasındaki ilişkiyi temel alarak yapılır. Özellikle yaşam destekleyici elementlerin varlığı, düşük toksisite gösteren mineral yoğunluğu ve işlenebilir maden rezervlerine dair ipuçları bu analizlerde belirleyici rol oynamaktadır.</p><br>

    <p style="color:{self.TEXT_COLOR};">
    Makine öğrenmesi modelleri, bu elementel verileri istatistiksel olarak sınıflandırarak gezegenin potansiyelini yüzdelik oranlarla ifade etmektedir. Örneğin, analiz edilen 1500 gezegen arasında, Mars’a benzer örneklerde %71,95 oranında yaşanabilirlik potansiyeli tespit edilmiştir. Bu sayede hem bilimsel keşif hem de potansiyel uzay madenciliği operasyonları için hedeflenen bölgeler daha akılcı ve veri odaklı bir şekilde belirlenebilmektedir.</p><br>

    <p style="color:{self.TEXT_COLOR};">
    Projemiz, açık kaynaklı bir yapıda geliştirilmiş olup, bilimsel araştırmalarda yeniden kullanım ve özelleştirme için uygundur. Araştırmacılar, geliştiriciler veya eğitimciler, projeyi inceleyerek katkıda bulunabilir, farklı gezegenler için yeni modeller türetebilir ya da veri kümesini genişleterek daha genel geçer sonuçlar elde edebilir. Bilimsel iş birliğini teşvik eden bu yaklaşım, gezegen keşiflerinde yapay zekânın nasıl entegre edilebileceğine dair güçlü bir örnek sunmaktadır.</p><br>

    <a href="https://github.com/mertcanyilmaz0/crescent" style="color:{self.ACCENT_COLOR}; font-weight: bold;">GitHub Proje Linki</a>
""")
#        home_text = QLabel(f"""
#            <h1 style="text-align:center; color:{self.TEXT_COLOR};"><b>MERAKLISINA</b></h1><br>
#            <b style="color:{self.TEXT_COLOR};">ICP-OES Teknolojisinin Kimyasal Temeli:</b><br>
#            <p style="color:{self.TEXT_COLOR};">ICP-OES, iyonize edilmiş bir plazmanın (çok yüksek sıcaklıkta bir gaz) kullanıldığı analitik bir tekniktir. Bu yöntem, #örneklerin bileşimindeki elementlerin konsantrasyonlarını belirlerken, her elementin özgül bir emisyon ışığını yayması ilkesine dayanır. Gezegenden alınan kayaç #örnekleri, önce yüksek sıcaklıkta bir plazmaya yerleştirilir, bu sıcaklık yeterince yüksektir ki, kayaçtaki atomlar iyonize olur ve bu iyonlar, kendi belirli #dalga boylarında ışık yayar. Bu ışık, dedektörler tarafından ölçülür ve her elementin yoğunluğu, yayılan ışığın yoğunluğu ile doğru orantılıdır.</p><br>
#
#            <b style="color:{self.TEXT_COLOR};">Makine Öğrenmesi ile Kimyasal Verilerin Değerlendirilmesi:</b><br>
#            <p style="color:{self.TEXT_COLOR};">Makine öğrenmesi algoritmaları, ICP-OES verilerinin analizi için güçlü bir araçtır. Kayaçlardan elde edilen element #yoğunlukları, makine öğrenmesi modeline giriş verisi olarak kullanılıyor. Model, bu kimyasal verileri analiz ederek gezegenin yaşanabilirlik, bilimsel #geçerlilik ve madencilik potansiyeli hakkında tahminlerde bulunur. Verilerdeki karmaşık ilişkiler, geleneksel yöntemlerle zor bir şekilde çıkarılabilirken, #makine öğrenmesi algoritmaları bu ilişkileri öğrenebilir ve doğru sonuçlar üretiyor.</p><br>
#
#            <b style="color:{self.TEXT_COLOR};">Kimyasal Modelleme ve Gezegenin Bilimsel Geçerliliği:</b><br>
#            <p style="color:{self.TEXT_COLOR};">Gezegenin yaşanabilirliği, bilimsel olarak değerlendirilebilecek kimyasal parametrelere dayalıdır. Elementlerin #konsantrasyonları, gezegenin atmosferi, sıcaklık düzeni ve su varlığı ile doğrudan ilişkilidir. Örneğin, azot (N) ve oksijen (O) oranları, bir gezegenin #atmosferinin kalitesini ve yaşam için uygun olup olmadığını belirlemede kullanılır. Bu kimyasal veriler, Mars'ın yaşam barındırma kapasitesini anlamamıza #yardımcı olabilir.</p><br>
#
#            <p style="color:{self.TEXT_COLOR};">Projemiz, Mars&rsquo;tan alınan kayaç örneklerini ICP-OES teknolojisiyle analiz ederek, gezegenin jeolojik yapısını, #yaşanabilirlik potansiyelini ve madencilik açısından değerini belirlemeyi amaçlamaktadır. ICP-OES, kayaçlardan alınan element yoğunluklarını ölçerek, bu veriler #üzerinden gezegenin kimyasal bileşimini ortaya koyar.</p><br>
#
#            <p style="color:{self.TEXT_COLOR};">Makine öğrenmesi algoritmalarımız, ICP-OES&rsquo;den elde edilen verilerle gezegenin yaşanabilirlik ve bilimsel geçerlilik #seviyelerini analiz etmekte kullanılmaktadır. Bu analizler, yüzdelik dilimlere dayalı olarak gezegenin yaşam koşullarını değerlendirir, bu sayede Mars&rsquo;ın #madencilik ve bilimsel araştırma potansiyeli hakkında öngörülerde bulunulur. Bu proje, Mars&rsquo;tan alınacak kayaç örnekleri ile elde edilen verilerin, #bilimsel olarak mümkün bir şekilde analiz edilebileceğini ve gezegenin potansiyelini anlamak için makine öğrenmesinin güçlü bir araç olabileceğini #göstermektedir.</p><br>
#
#            <p style="color:{self.TEXT_COLOR};">Projemiz tamamen açık kaynaklıdır; dilediğiniz gibi kullanabilir, geliştirebilir ve kendi projelerinize ilham kaynağı olarak #ekleyebilirsiniz. Katkılarınızı görmekten büyük mutluluk duyarız!</p><br>
#            <a href="https://github.com/mertcanyilmaz0/crescent" style="color:{self.ACCENT_COLOR}; font-weight: bold;">Github Linki</a>
#        """)

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

        inner_widget = QWidget()
        inner_layout = QVBoxLayout(inner_widget)
        inner_layout.setContentsMargins(30, 30, 30, 30)
        inner_layout.setSpacing(25)
        inner_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        
        container_layout.addWidget(inner_widget)
        container_widget.setLayout(container_layout)
        container_widget.setStyleSheet("background: transparent;")
        
        self.page_layout.addWidget(scroll_area)

        scroll_area.setWidget(container_widget)
        font_id = QFontDatabase.addApplicationFont("Poppins-Regular.ttf")
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        title_font = QFont(font_family, 24, QFont.Bold)
        text_font = QFont(font_family, 14)
        label_font = QFont(font_family, 12)
        input_font = QFont(font_family, 12)
        button_font = QFont(font_family, 16, QFont.Bold)
        result_font = QFont(font_family, 16)

        self.ml_title = QLabel("Makine Öğrenmesi")
        self.ml_title.setFont(title_font)
        self.ml_title.setAlignment(Qt.AlignCenter)
        self.ml_title.setStyleSheet(f"color: {self.TEXT_COLOR}; margin-bottom: 20px;")
        inner_layout.addWidget(self.ml_title)

        self.ml_text = QLabel("Makine öğrenmesi sürecinde Random Forest ve XGBoost algoritmaları kullanılmıştır. Bu algoritmalar, büyük veri kümelerinde yüksek doğrulukla çalıştıkları ve etkili karar mekanizmaları sundukları için tercih edilmiştir. Geliştirilen modellerin doğruluk oranı %93'ün üzerindedir ve hata payı yaklaşık 0.0003 gibi oldukça düşük bir seviyededir. Modelin eğitildiği veri tabanı, 1500 farklı gezegene ait verileri içermektedir. Yapılan analizler sonucunda, bir gezegenin en yüksek başarı potansiyeli %71,95 olarak hesaplanmıştır.")
        self.ml_text.setFont(text_font)
        self.ml_text.setAlignment(Qt.AlignLeft)
        self.ml_text.setWordWrap(True)
        self.ml_text.setStyleSheet(f"color: {self.TEXT_COLOR}; padding: 10px;")
        inner_layout.addWidget(self.ml_text)

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

        # Rastgele sayı butonu
        random_button = QPushButton("Rastgele Değerler")
        random_button.setFont(button_font)
        random_button.setMinimumWidth(200)
        random_button.setMaximumWidth(300)
        random_button.clicked.connect(self.fill_random_inputs)
        random_button.setCursor(Qt.PointingHandCursor)
        random_button.setStyleSheet(f'''
            background-color: {self.ACCENT_COLOR}; 
            color: {self.TEXT_COLOR}; 
            padding: 15px; 
            border-radius: 12px; 
            margin-top: 25px;
            font-weight: bold;
        ''')
        random_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        inner_layout.addWidget(random_button, alignment=Qt.AlignCenter)

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
#        inner_layout.addWidget(self.result_label)
        inner_layout.addWidget(self.result_label, alignment=Qt.AlignHCenter)
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
        scroll_area.setWidget(container_widget)

        self.page_layout.addWidget(scroll_area)
        container_widget.repaint()
    def fill_random_inputs(self):
        for element, input_field in self.inputs.items():
            random_value = random.randint(1, 100)
            input_field.setText(str(random_value))
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
