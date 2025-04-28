import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QLabel, QPushButton, QScrollArea, QGroupBox, QHBoxLayout, QSizePolicy
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFontDatabase, QFont
from PyQt5.QtGui import QFont, QColor
import requests
import subprocess
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QPainter, QLinearGradient

class PlanetPredictionApp(QWidget):
    def __init__(self):
        super().__init__()

        # Ana sayfa gösterimi
        self.current_page = None
    

        font_id = QFontDatabase.addApplicationFont("Poppins-Regular.ttf")
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        font = QFont(font_family)
        self.initUI()
        # Linear Gradient (yatay bir geçiş)
    def paintEvent(self, event):
        painter = QPainter(self)
        # Linear Gradient (yatay geçiş)
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor("#FE7743"))  # Başlangıç rengi
        gradient.setColorAt(1, QColor("#273F4F"))  # Bitiş rengi

        # Gradyanı kullanarak arka planı doldur
        painter.setBrush(gradient)
        painter.setPen(Qt.transparent)  # Kenarlık yok
        painter.drawRect(self.rect())  # Widget'ın tüm alanını doldur
        # UI elemanlarını oluştur

    def initUI(self):
        self.setWindowTitle('Crescent')
        self.setGeometry(0, 0, 1500, 900)
        font_id = QFontDatabase.addApplicationFont("Poppins-Regular.ttf")
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]

        # Yeni fontu ayarlama
        font = QFont(font_family, 10)  # Fontu 16 piksel olarak ayarlıyoruz
        # Ekranın ortasında konumlandır
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        window_geometry = self.geometry()
        x = (screen_geometry.width() - window_geometry.width()) // 2
        y = (screen_geometry.height() - window_geometry.height()) // 2
        self.move(x, y)

        # Ana layout
        self.main_layout = QVBoxLayout()  # Artık bunu self.main_layout yapıyoruz

        # Üst butonlar
        button_layout = QHBoxLayout()

        self.ml_button = QPushButton('ML Sayfası', self)
        self.ml_button.clicked.connect(self.show_ml_page)
        self.ml_button.setFont(font)
        button_layout.addWidget(self.ml_button)

        self.home_button = QPushButton('Ana Sayfa', self)
        self.home_button.clicked.connect(self.show_home_page)
        self.home_button.setFont(font)
        button_layout.addWidget(self.home_button)

        self.exe_button = QPushButton('Simülasyonu Oyna', self)
        self.exe_button.clicked.connect(self.run_exe)
        self.exe_button.setFont(font)
        button_layout.addWidget(self.exe_button)

        self.main_layout.addLayout(button_layout)

        # Sayfaların geleceği alan
        self.page_area = QVBoxLayout()
        self.main_layout.addLayout(self.page_area)

        # Şimdi önemli kısım:
        self.page_widget = QWidget()   # <- Sayfaları tutacak görünür bir widget
        self.page_layout = QVBoxLayout()  # <- Sayfalar burada yer değiştirecek
        self.page_widget.setLayout(self.page_layout)
        self.main_layout.addWidget(self.page_widget)  # <- Görünür olanı ekledik!

        self.setLayout(self.main_layout)

        self.show_home_page()
    def show_home_page(self):
        if self.current_page == 'home':
            return

        font_id = QFontDatabase.addApplicationFont("Poppins-Regular.ttf")
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        font = QFont(font_family, 16)
    
        self.clear_layout()
        self.current_page = 'home'
    
        home_text = QLabel("""
                           <h1><b>HOŞGELDİNİZ</b></h1><br>
<b>ICP-OES Teknolojisinin Kimyasal Temeli:</b><br>
ICP-OES, iyonize edilmiş bir plazmanın (çok yüksek sıcaklıkta bir gaz) kullanıldığı analitik bir tekniktir. Bu yöntem, örneklerin bileşimindeki elementlerin konsantrasyonlarını belirlerken, her elementin özgül bir emisyon ışığını yayması ilkesine dayanır. Gezegenden alınan kayaç örnekleri, önce yüksek sıcaklıkta bir plazmaya yerleştirilir, bu sıcaklık yeterince yüksektir ki, kayaçtaki atomlar iyonize olur ve bu iyonlar, kendi belirli dalga boylarında ışık yayar. Bu ışık, dedektörler tarafından ölçülür ve her elementin yoğunluğu, yayılan ışığın yoğunluğu ile doğru orantılıdır.<br><br>

<b>Makine Öğrenmesi ile Kimyasal Verilerin Değerlendirilmesi:</b><br>
Makine öğrenmesi algoritmaları, ICP-OES verilerinin analizi için güçlü bir araçtır. Kayaçlardan elde edilen element yoğunlukları, makine öğrenmesi modeline giriş verisi olarak kullanılıyor. Model, bu kimyasal verileri analiz ederek gezegenin yaşanabilirlik, bilimsel geçerlilik ve madencilik potansiyeli hakkında tahminlerde bulunur. Verilerdeki karmaşık ilişkiler, geleneksel yöntemlerle zor bir şekilde çıkarılabilirken, makine öğrenmesi algoritmaları bu ilişkileri öğrenebilir ve doğru sonuçlar üretiyor.<br><br>

<b>Kimyasal Modelleme ve Gezegenin Bilimsel Geçerliliği:</b><br>
Gezegenin yaşanabilirliği, bilimsel olarak değerlendirilebilecek kimyasal parametrelere dayalıdır. Elementlerin konsantrasyonları, gezegenin atmosferi, sıcaklık düzeni ve su varlığı ile doğrudan ilişkilidir. Örneğin, azot (N) ve oksijen (O) oranları, bir gezegenin atmosferinin kalitesini ve yaşam için uygun olup olmadığını belirlemede kullanılır. Bu kimyasal veriler, Mars’ın yaşam barındırma kapasitesini anlamamıza yardımcı olabilir.<br><br>

Projemiz, Mars&rsquo;tan alınan kayaç örneklerini ICP-OES teknolojisiyle analiz ederek, gezegenin jeolojik yapısını, yaşanabilirlik potansiyelini ve madencilik açısından değerini belirlemeyi amaçlamaktadır. ICP-OES, kayaçlardan alınan element yoğunluklarını ölçerek, bu veriler üzerinden gezegenin kimyasal bileşimini ortaya koyar.<br><br>

Makine öğrenmesi algoritmalarımız, ICP-OES&rsquo;den elde edilen verilerle gezegenin yaşanabilirlik ve bilimsel geçerlilik seviyelerini analiz etmekte kullanılmaktadır. Bu analizler, yüzdelik dilimlere dayalı olarak gezegenin yaşam koşullarını değerlendirir, bu sayede Mars&rsquo;ın madencilik ve bilimsel araştırma potansiyeli hakkında öngörülerde bulunulur. Bu proje, Mars&rsquo;tan alınacak kayaç örnekleri ile elde edilen verilerin, bilimsel olarak mümkün bir şekilde analiz edilebileceğini ve gezegenin potansiyelini anlamak için makine öğrenmesinin güçlü bir araç olabileceğini göstermektedir.<br><br>

Projemiz tamamen açık kaynaklıdır; dilediğiniz gibi kullanabilir, geliştirebilir ve kendi projelerinize ilham kaynağı olarak ekleyebilirsiniz. Katkılarınızı görmekten büyük mutluluk duyarız!<br>
<a href="https://github.com/mertcanyilmaz0/crescent">Github Linki</a>
""")

        self.setStyleSheet("background-color: rgba(0, 0, 0, 0);border:none;text-align:start;")
        home_text.setWordWrap(True)
        home_text.setFont(font)
        home_text.setAlignment(Qt.AlignLeft)
        home_text.setOpenExternalLinks(True)
        home_widget = QWidget()
        layout = QVBoxLayout()
    
        # Scroll alanı ekleme
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollBar:vertical {
                background: #f1f1f1;
                width: 12px;
                border-radius: 6px;
            }

            QScrollBar::handle:vertical {
                background: #FE7743;
                border-radius: 6px;
            }

            QScrollBar::handle:vertical:hover {
                background: #555;
            }

            QScrollBar::add-line:vertical {
                background: #f1f1f1;
                height: 20px;
            }

            QScrollBar::sub-line:vertical {
                background: #273F4F;
                height: 20px;
            }
        """)
        container_widget = QWidget()
        container_layout = QVBoxLayout()
    
        container_layout.addStretch()
        container_layout.addWidget(home_text)
        container_layout.addStretch()
    
        container_widget.setLayout(container_layout)
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

        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollBar:vertical {
                background: #f1f1f1;
                width: 12px;
                border-radius: 6px;
            }

            QScrollBar::handle:vertical {
                background: #FE7743;
                border-radius: 6px;
            }

            QScrollBar::handle:vertical:hover {
                background: #555;
            }

            QScrollBar::add-line:vertical {
                background: #f1f1f1;
                height: 20px;
            }

            QScrollBar::sub-line:vertical {
                background: #273F4F;
                height: 20px;
            }
        """)
        container_widget = QWidget()
        container_layout = QVBoxLayout()

        self.inputs = {}
        elements = ['He', 'Ne', 'Cl', 'Mg', 'Ti', 'Fe', 'Ag', 'Ni', 'Si', 'Cu', 'Mn', 'Pt', 'U', 'Al', 'Ar', 'N', 'Zn', 'P', 'H', 'Ca', 'C', 'Cr', 'S', 'Li', 'Na', 'V']

        font_id = QFontDatabase.addApplicationFont("Poppins-Regular.ttf")
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]

        # Yeni fontu ayarlama
        font = QFont(font_family, 12)  # Fontu 16 piksel olarak ayarlıyoruz

        for element in elements:
            label = QLabel(f'{element} Yoğunluğu (%):')
            label.setFont(font)
            container_layout.addWidget(label)
            input_field = QLineEdit(self)
            input_field.setPlaceholderText('0 - 100 arasında bir değer girin')
            input_field.setFont(QFont('Arial', 10))
            input_field.setStyleSheet('border: 1px solid #ccc; padding: 5px; border-radius: 5px;')
            container_layout.addWidget(input_field)
            self.inputs[element] = input_field

        self.result_label = QLabel('Tahmin Sonuçları: ')
        self.result_label.setFont(QFont('Arial', 12))
        self.result_label.setStyleSheet('color: black;padding:0 10 0 10;')
        container_layout.addWidget(self.result_label)

        self.predict_button = QPushButton('Tahmin Yap', self)
        self.predict_button.setFont(QFont('Arial', 12))
        self.predict_button.setStyleSheet('background-color: #273F4F; color: white; border: none; padding: 10px; border-radius: 5px;')
        self.predict_button.clicked.connect(self.predict)
        container_layout.addWidget(self.predict_button)

        container_widget.setLayout(container_layout)
        scroll_area.setWidget(container_widget)

        self.page_layout.addWidget(scroll_area)

    def predict(self):
        # Kullanıcı inputlarını al
        user_input = {}
        for element, input_field in self.inputs.items():
            try:
                value = float(input_field.text())
                if 0 <= value <= 100:  # 0-100 arasında bir değer kontrolü
                    user_input[element] = value / 100  # 0-100 arasındaki değeri 0-1 arasına dönüştür
                else:
                    raise ValueError
            except ValueError:
                self.result_label.setText("Hata: Lütfen 0-100 arasında geçerli bir sayı girin.")
                return

        # API'ye POST isteği gönder
        url = 'http://127.0.0.1:5000/predict'
        response = requests.post(url, json=user_input)

        # Sonuçları al ve etiketleri güncelle
        if response.status_code == 200:
            results = response.json()
            result_text = f"🌱 Yaşanabilirlik: %{results['life_score'] * 100:.2f}\n"
            result_text += f"🔬 Bilimsel ilgi: %{results['science_score'] * 100:.2f}\n"
            result_text += f"⛏️ Madencilik: %{results['mining_score'] * 100:.2f}\n"
            result_text += f"✅ Genel başarı: %{results['success_score'] * 100:.2f}"
            self.result_label.setText(result_text)
        else:
            self.result_label.setText("API isteği başarısız oldu.")

    def run_exe(self):
        # EXE dosyasını çalıştır
        exe_path = 'path/to/your/exe/file.exe'  # EXE dosyasının yolu
        subprocess.run([exe_path])

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('crescent.ico'))
    ex = PlanetPredictionApp()
    ex.show()
    sys.exit(app.exec_())

 
