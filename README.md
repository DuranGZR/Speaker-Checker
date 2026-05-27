# 🎙️ Speaker Checker (Konuşmacı Geçmiş Kontrol Sistemi)

Bu proje, bir YouTube kanalındaki geçmiş **tamamlanmış canlı yayınları** YouTube Data API v3 kullanarak çeker, PostgreSQL veritabanına kaydeder ve kullanıcı tarafından girilen isimleri bu videoların başlık ve açıklamaları içinde akıllı bir şekilde arar.

Sistem, ismin geçtiği açıklamayı çevreleyen bağlam satırlarıyla birlikte alıntı olarak sunar ve konuşmacı kalıpları (örn. *"Konuğumuz..."*, *"Konuşmacı..."*) tespit edildiğinde uyarı düzeyini yükselterek hızlıca doğrulama yapmanıza imkan sağlar.

---

## 🛠️ Kurulum ve Çalıştırma

### 1. Bağımlılıkların Yüklenmesi

Sistemde Python 3.8+ yüklü olmalıdır. Proje dizininde bir sanal ortam oluşturup gerekli kütüphaneleri yükleyin:

```bash
# Sanal ortam oluşturma
python -m venv .venv

# Sanal ortamı aktif etme (Windows)
.venv\Scripts\activate

# Sanal ortamı aktif etme (macOS/Linux)
source .venv/bin/activate

# Paketleri kurma
pip install -r requirements.txt
```

### 2. Çevre Değişkenleri (`.env`) Ayarı

Proje kök dizinindeki `.env.example` dosyasının adını `.env` olarak değiştirin ve kendi değerlerinizle doldurun:

```env
# YouTube API Ayarları
YOUTUBE_API_KEY=your_youtube_api_key_here
YOUTUBE_CHANNEL_ID=your_channel_id_here

# PostgreSQL Veritabanı Ayarları
DB_HOST=localhost
DB_PORT=5432
DB_NAME=speaker_checker
DB_USER=postgres
DB_PASSWORD=your_postgres_password_here
```

> 💡 **Önemli:** Arama yapmadan önce PostgreSQL sunucunuzda `speaker_checker` isimli boş bir veritabanı oluşturmuş olmalısınız (`CREATE DATABASE speaker_checker;`). Tablolar, indeksler ve uzantılar uygulama ilk çalıştığında otomatik olarak oluşturulacaktır.

### 3. Uygulamayı Başlatma

Aşağıdaki komutla Streamlit arayüzünü ayağa kaldırabilirsiniz:

```bash
streamlit run app.py
python -m streamlit run app.py
```

Tarayıcınızda otomatik olarak `http://localhost:8501` adresi açılacaktır.

---

## 🔑 YouTube API Key ve Kanal ID Nasıl Alınır?

### 1. YouTube Data API Key Alımı (Adım Adım)

1. **Google Cloud Console'a Giriş Yapın:**
   [Google Cloud Console](https://console.cloud.google.com/) adresine gidin ve Google hesabınızla giriş yapın.

2. **Yeni Proje Oluşturun:**
   Sol üst köşedeki proje seçici menüsünden **"New Project" (Yeni Proje)** butonuna tıklayın. Projenize `Speaker Checker` gibi bir isim verin ve oluşturun.

3. **YouTube API Kitaplığını Etkinleştirin:**
   - Sol menüden veya arama çubuğundan **"APIs & Services" (API'ler ve Servisler) > "Library" (Kitaplık)** bölümüne gidin.
   - Arama çubuğuna **"YouTube Data API v3"** yazın.
   - Çıkan sonuca tıklayın ve **"Enable" (Etkinleştir)** butonuna basın.

4. **API Key Oluşturun:**
   - API etkinleştikten sonra sol menüden **"Credentials" (Kimlik Bilgileri)** sekmesine geçin.
   - Üst tarafta bulunan **"+ Create Credentials" (Kimlik Bilgileri Oluştur)** butonuna tıklayın ve listeden **"API Key" (API Anahtarı)** seçeneğini seçin.
   - Ekranınızda oluşan `AIzaSy...` ile başlayan anahtarı kopyalayın ve `.env` dosyanızdaki `YOUTUBE_API_KEY` alanına yapıştırın.

---

### 2. YouTube Kanal ID (Channel ID) Bulma Yöntemleri

Kanal ID'si `UC` ile başlayan 24 karakterli benzersiz bir kimliktir. Bunu bulmak için 3 pratik yöntem vardır:

#### Yöntem A: Doğrudan Handle Kullanımı (En Kolayı! 🚀)
Geliştirdiğimiz sistem **YouTube Handle (@)** desteğine sahiptir. Bu sayede hiçbir arama yapmadan kanalın kullanıcı adını doğrudan `.env` dosyasına yazabilirsiniz.
* Örnek: `YOUTUBE_CHANNEL_ID=@HuaweiDeveloperGroupsTurkiye` veya `YOUTUBE_CHANNEL_ID=@youtube`

#### Yöntem B: Sayfa Kaynağından Bulma
1. Tarayıcınızda hedef YouTube kanalının ana sayfasına gidin (örn: `https://www.youtube.com/@HuaweiDeveloperGroupsTurkiye`).
2. Sayfada boş bir yere sağ tıklayıp **"View Page Source" (Sayfa Kaynağını Görüntüle)** seçeneğine tıklayın.
3. Açılan kaynak kod sayfasında `Ctrl + F` tuşlarına basarak `channelId` veya `"UC` araması yapın.
4. `"channelId":"UCxxxxxxxxxxxxxxxxxxxx"` şeklinde olan değeri kopyalayıp `.env` dosyasına ekleyin.

#### Yöntem C: Çevrimiçi Araçları Kullanma
1. Kanalın ana sayfa bağlantısını kopyalayın.
2. [CommentPicker YouTube Channel ID Finder](https://commentpicker.com/youtube-channel-id.php) veya [Share連結](https://www.youtube.com/) gibi güvenilir bir çevrimiçi araca kanal linkini yapıştırın.
3. Araç size anında `UC` ile başlayan kanal kimliğini verecektir.

---

## 📂 Dosya Yapısı ve Görevleri

* `app.py`: Siyah/Kırmızı/Beyaz renk şemasına sahip, modern Streamlit kullanıcı arayüzü.
* `youtube_service.py`: YouTube API ile kanal playlistlerini gezen, videoların canlı yayın detaylarını süzüp çeken entegrasyon.
* `db.py`: PostgreSQL bağlantı yönetimi, veritabanı şemasının hazırlanması, GIN indekslerin oluşturulması ve upsert işlemleri.
* `search_service.py`: Arama kelimesini normalize edip veritabanında sorgulayan ve arayüz için eşleşmeleri derleyen koordinatör.
* `excerpt_service.py`: Metin içinde aranan ismin geçtiği satırın 2 satır öncesini ve sonrasını (bağlamını) alan, konuşmacı kalıplarını kontrol eden zeka.
* `normalizer.py`: Türkçe karakterleri (ç->c, ı->i vb.) normalize eden ve arama kalitesini artıran yardımcı modül.
