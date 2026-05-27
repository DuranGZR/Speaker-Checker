import streamlit as st
import datetime
import html

# Attempt to import database and service modules
try:
    from db import init_db, count_live_videos
    from youtube_service import sync_youtube_live_videos
    from search_service import search_name_in_live_videos
    from excerpt_service import highlight_name_in_text
    db_import_success = True
except ImportError as err:
    db_import_success = False
    db_import_error = str(err)

# Page Configuration
st.set_page_config(
    page_title="Konuşmacı Geçmiş Kontrol Sistemi",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for Black, Bordeaux, White Theme (No Glows, Matte Solid Colors)
custom_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');

/* Global Background and Typography */
.stApp {
    background-color: #0d0d0d !important;
    font-family: 'Outfit', sans-serif;
    color: #ffffff;
}

.block-container {
    max-width: 1180px;
    padding-top: 5rem;
    padding-left: 2rem;
    padding-right: 2rem;
}

h1, h2, h3, h4, h5, h6 {
    font-family: 'Outfit', sans-serif !important;
    font-weight: 700 !important;
    color: #ffffff !important;
}

h1 {
    font-size: clamp(2rem, 4vw, 2.6rem) !important;
    line-height: 1.1 !important;
    margin-bottom: 0.5rem !important;
}

.sub-title {
    color: #b3b3b3;
    font-size: 1.05rem;
    margin-bottom: 1.5rem;
    max-width: 760px;
}

/* Tab styling override to match Bordeaux theme */
div[data-testid="stTabBar"] button {
    font-size: 1.05rem !important;
    font-weight: 600 !important;
    color: #b3b3b3 !important;
}

div[data-testid="stTabBar"] button[aria-selected="true"] {
    color: #ffffff !important;
    border-bottom: 3px solid #800020 !important;
}

/* Custom Buttons (st.button, st.form_submit_button) */
div.stButton > button, div.stFormSubmitButton > button {
    background-color: #800020 !important;
    color: #ffffff !important;
    border: 1px solid #a61c38 !important;
    border-radius: 6px !important;
    padding: 10px 24px !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    transition: background-color 0.2s ease !important;
    width: 100%;
    min-height: 44px;
}

div.stButton > button:hover, div.stFormSubmitButton > button:hover {
    background-color: #990026 !important;
    border-color: #c22746 !important;
}

/* Input Fields styling */
.stTextInput>div>div>input {
    background-color: #161616 !important;
    color: #ffffff !important;
    border: 1px solid #333333 !important;
    border-radius: 6px !important;
    padding: 12px !important;
    font-size: 1.1rem !important;
    transition: border-color 0.2s ease !important;
}

.stTextInput>div>div>input:focus {
    border-color: #800020 !important;
    box-shadow: none !important;
}

.stTextInput label {
    color: #d8d8d8 !important;
}

div[data-testid="stForm"] {
    background: #161616;
    border: 1px solid #262626;
    border-radius: 8px;
    padding: 20px;
}

/* Custom Metric Card */
.metric-card {
    background: #161616;
    border: 1px solid #262626;
    border-left: 5px solid #800020;
    border-radius: 8px;
    padding: 20px;
    text-align: center;
    max-width: 300px;
    margin-bottom: 20px;
}

.metric-val {
    font-size: 2.8rem;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 5px;
}

.metric-lbl {
    font-size: 0.85rem;
    color: #a6a6a6;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-weight: 600;
}

/* Custom Result Card */
.result-card {
    background: #161616;
    border-left: 5px solid #800020;
    border-top: 1px solid #262626;
    border-right: 1px solid #262626;
    border-bottom: 1px solid #262626;
    border-radius: 0 8px 8px 0;
    padding: 25px;
    margin-bottom: 25px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
}

.result-grid {
    display: grid;
    grid-template-columns: minmax(220px, 320px) minmax(0, 1fr);
    gap: 24px;
    align-items: start;
}

.result-thumb {
    width: 100%;
    aspect-ratio: 16 / 9;
    object-fit: cover;
    border-radius: 6px;
    border: 1px solid #262626;
    background: #0d0d0d;
}

.result-thumb-placeholder {
    width: 100%;
    aspect-ratio: 16 / 9;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 6px;
    border: 1px solid #262626;
    background: #121212;
    color: #8c8c8c;
    font-weight: 600;
}

.result-title {
    margin: 0 0 12px;
    font-size: clamp(1.2rem, 2vw, 1.6rem);
    line-height: 1.25;
    overflow-wrap: anywhere;
}

.result-meta {
    color: #a6a6a6;
    font-size: 0.95rem;
    margin-bottom: 14px;
}

.badge-strong {
    background-color: rgba(128, 0, 32, 0.15);
    color: #ff6680;
    border: 1px solid rgba(128, 0, 32, 0.4);
    padding: 5px 12px;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 700;
    display: inline-block;
    margin-bottom: 12px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.badge-normal {
    background-color: #262626;
    color: #dcdcdc;
    border: 1px solid #333333;
    padding: 5px 12px;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 700;
    display: inline-block;
    margin-bottom: 12px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.excerpt-box {
    background-color: #0d0d0d;
    border: 1px solid #262626;
    border-radius: 6px;
    padding: 16px;
    font-family: 'Courier New', Courier, monospace;
    font-size: 0.95rem;
    color: #e0e0e0;
    white-space: pre-wrap;
    margin: 15px 0;
    line-height: 1.6;
    overflow-wrap: anywhere;
}

.description-title {
    color: #ffffff;
    font-weight: 700;
    margin: 18px 0 8px;
}

.description-details {
    margin-top: 15px;
    border: 1px solid #262626;
    border-radius: 6px;
    background: #0d0d0d;
    overflow: hidden;
}

.description-details > summary {
    min-height: 44px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    color: #ffffff;
    font-weight: 700;
    cursor: pointer;
    list-style: none;
    padding: 12px 16px;
    background: #161616;
    user-select: none;
}

.description-details > summary::-webkit-details-marker {
    display: none;
}

.description-details > summary::after {
    content: "▼ Göster";
    color: #ff6680;
    font-size: 0.85rem;
}

.description-details[open] > summary::after {
    content: "▲ Gizle";
}

.description-box {
    background-color: #090909;
    border-top: 1px solid #262626;
    padding: 16px;
    color: #e9e9e9;
    font-size: 0.95rem;
    line-height: 1.7;
    white-space: pre-wrap;
    overflow-wrap: anywhere;
    max-height: 350px;
    overflow-y: auto;
}

.watch-link {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-height: 44px;
    margin-top: 18px;
    padding: 10px 18px;
    border-radius: 6px;
    background: #800020;
    border: 1px solid #a61c38;
    color: #ffffff !important;
    text-decoration: none !important;
    font-weight: 700;
    transition: background-color 0.2s ease;
}

.watch-link:hover {
    background: #990026;
}

@media (max-width: 768px) {
    .block-container {
        padding-left: 0.75rem !important;
        padding-right: 0.75rem !important;
        padding-top: 4.5rem !important;
    }

    .result-grid {
        grid-template-columns: 1fr !important;
        gap: 12px !important;
    }
    
    .result-thumb {
        max-width: 100% !important;
        margin: 0 auto !important;
        border-radius: 6px !important;
    }

    .result-card {
        padding: 12px 14px !important;
        border-left: 4px solid #800020 !important;
        border-radius: 8px !important;
        margin-bottom: 16px !important;
    }

    .result-title {
        font-size: 1.15rem !important;
        line-height: 1.35 !important;
        margin-top: 6px !important;
        margin-bottom: 8px !important;
    }

    .result-meta {
        font-size: 0.82rem !important;
        margin-bottom: 8px !important;
    }

    .badge-strong, .badge-normal {
        padding: 4px 10px !important;
        font-size: 0.7rem !important;
        margin-bottom: 8px !important;
    }

    .description-title {
        font-size: 0.85rem !important;
        margin: 12px 0 4px !important;
    }

    .excerpt-box {
        font-size: 0.82rem !important;
        padding: 10px 12px !important;
        margin: 8px 0 !important;
        line-height: 1.5 !important;
    }

    .description-details {
        margin-top: 10px !important;
    }

    .description-details > summary {
        min-height: 38px !important;
        padding: 8px 12px !important;
        font-size: 0.82rem !important;
    }

    .description-box {
        font-size: 0.82rem !important;
        padding: 10px 12px !important;
        max-height: 200px !important;
    }

    .watch-link {
        width: 100% !important;
        margin-top: 12px !important;
        font-size: 0.88rem !important;
        min-height: 40px !important;
        padding: 8px 16px !important;
        border-radius: 6px !important;
    }
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# Verify Imports
if not db_import_success:
    st.error("🚨 Kütüphane Yükleme Hatası!")
    st.markdown(f"""
    Bağımlı Python dosyaları bulunamadı: `{db_import_error}`
    
    Lütfen projenin kök dizininde tüm dosyaların (`db.py`, `youtube_service.py`, `search_service.py`, `normalizer.py`, `excerpt_service.py`) mevcut olduğunu doğrulayın.
    """)
    st.stop()

# Initialize Database on Startup
db_ready = False
try:
    init_db()
    db_ready = True
except Exception as e:
    db_ready = False
    db_error_msg = str(e)

# Main Application Layout
st.markdown("<h1>🎙️ Konuşmacı Geçmiş Kontrol Sistemi</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>YouTube canlı yayın açıklamalarında otomatik konuşmacı ve isim tarama sistemi (MVP)</p>", unsafe_allow_html=True)

# Database Error Notice
if not db_ready:
    st.error("🚨 Veritabanı Bağlantı Hatası!")
    st.markdown(f"""
    PostgreSQL veritabanına bağlantı sağlanamadı.
    
    **Hata Detayı:** `{db_error_msg}`
    
    **Çözüm Adımları:**
    1. PostgreSQL sunucunuzun çalışır durumda (açık) olduğundan emin olun.
    2. `.env` dosyasındaki veritabanı kullanıcı adı (`DB_USER`), şifre (`DB_PASSWORD`), sunucu (`DB_HOST`) ve port (`DB_PORT`) bilgilerini kontrol edin.
    3. Belirtilen veritabanının PostgreSQL'de oluşturulduğundan emin olun:
       ```sql
       CREATE DATABASE speaker_checker;
       ```
    """)
    st.stop()

# TABBED INTERFACE (Solve Mobile view issue by removing sidebar)
tab_search, tab_admin = st.tabs(["🔍 Konuşmacı Ara", "⚙️ Yönetici Paneli"])

# TAB 1: Search
with tab_search:
    st.subheader("🔍 İsim Arama & Doğrulama")
    st.write("Geçmiş canlı yayınlarda aramak istediğiniz kişinin adını ve soyadını yazın.")

    # Form to trigger search with Enter or Button click
    with st.form("search_form"):
        search_name = st.text_input(
            "Aranacak Kişi Adı",
            placeholder="Örn: Gamze Akman Acar",
            label_visibility="collapsed"
        )
        submit_search = st.form_submit_button("Canlı Yayınlarda Ara")

    if submit_search:
        clean_name = search_name.strip()
        if not clean_name:
            st.warning("Lütfen arama yapmak için bir isim girin.")
        else:
            results_data = search_name_in_live_videos(clean_name)
            
            st.markdown(f"#### **Arama Sonuçları**")
            st.write(f"'{clean_name}' ismi için **{results_data['result_count']}** eşleşen canlı yayın bulundu.")
            
            if results_data['result_count'] == 0:
                st.info("Bu isim kayıtlı canlı yayın başlıklarında veya açıklamalarında bulunamadı. Lütfen ismi farklı kombinasyonlarla (örn. sadece soyadı veya sadece ön adı) aramayı deneyin.")
            else:
                for item in results_data['results']:
                    badge_class = "badge-strong" if item['match_type'] == "STRONG_SPEAKER_PATTERN" else "badge-normal"
                    badge_text = "🔥 Konuşmacı Olabilir (Kalıp Eşleşti)" if item['match_type'] == "STRONG_SPEAKER_PATTERN" else "📝 İsim Açıklamada Geçiyor"
                    title = html.escape(item["title"])
                    date_value = item['actual_start_time'].strftime('%d %B %Y, %H:%M') if isinstance(item['actual_start_time'], datetime.datetime) else item['actual_start_time']
                    date_text = html.escape(str(date_value or "Tarih bilgisi yok"))
                    video_url = html.escape(item["video_url"], quote=True)
                    excerpt = html.escape(item["matched_excerpt"]).replace("\n", "<br>")
                    description_text = item.get("description") or item.get("raw_text") or "Açıklama bulunamadı."
                    full_description = highlight_name_in_text(description_text, clean_name)

                    if item["thumbnail_url"]:
                        thumbnail_html = f'<img class="result-thumb" src="{html.escape(item["thumbnail_url"], quote=True)}" alt="{title} kapak görseli">'
                    else:
                        thumbnail_html = '<div class="result-thumb-placeholder">Görsel yok</div>'

                    st.markdown(f"""
                    <article class="result-card">
                        <div class="result-grid">
                            <div>{thumbnail_html}</div>
                            <div>
                                <div class="{badge_class}">{badge_text}</div>
                                <h3 class="result-title">{title}</h3>
                                <div class="result-meta">📅 <b>Yayın Tarihi:</b> {date_text}</div>
                                <div class="description-title">Eşleşen bölüm</div>
                                <div class="excerpt-box">{excerpt}</div>
                                <details class="description-details">
                                    <summary>Yayın açıklamasının tamamı</summary>
                                    <div class="description-box">{full_description}</div>
                                </details>
                                <a class="watch-link" href="{video_url}" target="_blank" rel="noopener noreferrer">📺 YouTube'da İzle / Aç</a>
                            </div>
                        </div>
                    </article>
                    """, unsafe_allow_html=True)

# TAB 2: Admin Panel
with tab_admin:
    st.subheader("⚙️ Yönetici Paneli")
    st.write("Verileri YouTube API üzerinden tazelemek ve durum takibi yapmak için burayı kullanın.")
    
    # Custom HTML Metric Card
    live_count = count_live_videos()
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-val">{live_count}</div>
        <div class="metric-lbl">Kayıtlı Canlı Yayın</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Sync Button
    st.markdown("#### Veri Güncelleme")
    st.write("YouTube kanalındaki en son canlı yayın kayıtlarını senkronize edin:")
    sync_clicked = st.button("🔄 YouTube Canlı Yayınlarını Güncelle")
    
    if sync_clicked:
        with st.spinner("Canlı yayınlar çekiliyor... Bu işlem kanal boyutuna göre biraz sürebilir..."):
            try:
                sync_result = sync_youtube_live_videos()
                st.success("Senkronizasyon Başarıyla Tamamlandı!")
                st.balloons()
                # Display statistics
                st.markdown(f"""
                - **Taranan Video:** {sync_result['total_video_count']}
                - **Eklenen/Güncellenen Canlı Yayın:** {sync_result['live_saved_count']}
                - **Atlanan Normal Video:** {sync_result['skipped_non_live_count']}
                """)
                # Force rerun to update metric
                st.rerun()
            except Exception as sync_err:
                st.error(f"Güncelleme sırasında hata oluştu: {sync_err}")
                st.info("İpucu: YOUTUBE_API_KEY ve YOUTUBE_CHANNEL_ID değerlerinizin .env dosyasında doğru şekilde tanımlandığından emin olun.")
