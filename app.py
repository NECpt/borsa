import streamlit as st
import yfinance as yf
import pandas as pd
import mplfinance as mpf
import numpy as np
from sklearn.linear_model import LinearRegression
import datetime

# 1. SAYFA AYARLARI
st.set_page_config(
    page_title="Borsa Avcısı: Oracle",
    layout="wide",
    page_icon="🔮",
    initial_sidebar_state="expanded"
)

# 2. YAN MENÜ (SOL PANEL)
st.sidebar.header("🔮 THE ORACLE")
st.sidebar.write("Geleceği tahmin etmeye hazır mısın?")

# Giriş Kutuları
hisse = st.sidebar.text_input("🎯 Hedef Hisse (Örn: SASA):", "THYAO").upper()
periyot = st.sidebar.select_slider(
    "⏳ Analiz Geçmişi:", 
    options=["1mo", "3mo", "6mo", "1y"],
    value="6mo"
)
tahmin_gun = st.sidebar.slider("🔮 Kaç gün sonrasını göreyim?", 3, 30, 7)
hareketli_ort = st.sidebar.toggle("Ortalamaları Göster 📉", value=True)

st.sidebar.markdown("---")
st.sidebar.caption("🚀 Powered by **Yönetici Eren**")

# 3. ANA EKRAN
st.image("https://images.unsplash.com/photo-1642543492481-44e81e3914a7?q=80&w=1200&auto=format&fit=crop", use_column_width=True)
st.title(f"🔮 {hisse} - Kâhin Modu")

# --- YAPAY ZEKA FONKSİYONU ---
def yapay_zeka_tahmini(df, gun_sayisi):
    # Veriyi hazırla (Tarihleri sayıya çevir: 1. gün, 2. gün...)
    df = df.reset_index()
    df['Date_Ordinal'] = df['Date'].apply(lambda x: x.toordinal())
    
    X = df[['Date_Ordinal']]
    y = df['Close']
    
    # Modeli Eğit (Lineer Regresyon)
    model = LinearRegression()
    model.fit(X, y)
    
    # Gelecek tarihleri oluştur
    son_tarih = df['Date'].max()
    gelecek_tarihler = [son_tarih + datetime.timedelta(days=i) for i in range(1, gun_sayisi+1)]
    gelecek_ordinal = np.array([d.toordinal() for d in gelecek_tarihler]).reshape(-1, 1)
    
    # Tahmin Yap
    tahminler = model.predict(gelecek_ordinal)
    
    tahmin_df = pd.DataFrame({
        'Date': gelecek_tarihler,
        'Tahmin': tahminler
    })
    tahmin_df.set_index('Date', inplace=True)
    return tahmin_df, model.coef_[0] # Tahminler ve Eğim (Trend Yönü)

if st.sidebar.button("Küreyi Çalıştır 🔮", type="primary"):
    try:
        kodu = hisse + ".IS" if not hisse.endswith(".IS") else hisse
        
        with st.status("🔮 Oracle uyanıyor...", expanded=True) as status:
            st.write("📡 Piyasa verileri indiriliyor...")
            df = yf.Ticker(kodu).history(period=periyot)
            
            if df.empty:
                status.update(label="Hata! Veri yok.", state="error", expanded=False)
                st.error("💥 Bu hisseyi bulamadım.")
            else:
                # --- KLASİK ANALİZ ---
                st.write("🧠 Teknik indikatörler hesaplanıyor...")
                df['SMA20'] = df['Close'].rolling(window=20).mean()
                df['SMA50'] = df['Close'].rolling(window=50).mean()
                
                # RSI
                delta = df['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                df['RSI'] = 100 - (100 / (1 + rs))

                # --- ORACLE TAHMİNİ ---
                st.write("🔮 Gelecek simülasyonu yapılıyor...")
                tahmin_df, egim = yapay_zeka_tahmini(df, tahmin_gun)
                
                status.update(label="Analiz ve Tahmin Hazır! 🚀", state="complete", expanded=False)

                # --- SONUÇ EKRANI ---
                son_fiyat = df['Close'].iloc[-1]
                tahmin_son_fiyat = tahmin_df['Tahmin'].iloc[-1]
                fark_yuzde = ((tahmin_son_fiyat - son_fiyat) / son_fiyat) * 100
                
                # 1. BÖLÜM: BUGÜNÜN DURUMU
                st.subheader("📊 Mevcut Durum")
                col1, col2, col3 = st.columns(3)
                col1.metric("Anlık Fiyat", f"{son_fiyat:.2f} TL")
                col2.metric("RSI", f"{df['RSI'].iloc[-1]:.1f}")
                
                trend_ikon = "YÜKSELİŞ 🚀" if df['SMA20'].iloc[-1] > df['SMA50'].iloc[-1] else "DÜŞÜŞ 🐻"
                col3.metric("Teknik Trend", trend_ikon)

                # 2. BÖLÜM: ORACLE TAHMİNİ (YENİ!)
                st.markdown("---")
                st.subheader(f"🔮 The Oracle'ın {tahmin_gun} Günlük Kehaneti")
                
                # Tahmin Kartları
                o1, o2 = st.columns(2)
                o1.metric(f"{tahmin_gun} Gün Sonraki Tahmin", f"{tahmin_son_fiyat:.2f} TL", f"%{fark_yuzde:.2f}")
                
                yorum = "YATAY SEYİR ↔️"
                renk = "off"
                if egim > 0.1: 
                    yorum = "GÜÇLÜ YÜKSELİŞ BEKLENTİSİ 🚀"
                    renk = "normal"
                elif egim < -0.1: 
                    yorum = "DÜŞÜŞ RİSKİ 🔻"
                    renk = "inverse"
                
                o2.info(f"**Yapay Zeka Yorumu:**\n{yorum}")

                # 3. BÖLÜM: GRAFİKLER
                tab1, tab2 = st.tabs(["🕯️ Teknik Grafik", "🔮 Gelecek Simülasyonu"])
                
                with tab1:
                    apd = []
                    if hareketli_ort:
                        apd = [
                            mpf.make_addplot(df['SMA20'], color='lime'), 
                            mpf.make_addplot(df['SMA50'], color='fuchsia'),
                        ]
                    fig, ax = mpf.plot(df, type='candle', style='nightclouds', addplot=apd, volume=True, returnfig=True, figsize=(10,6))
                    st.pyplot(fig)
                
                with tab2:
                    st.write("Bu grafik, geçmiş fiyatlar (Mavi) ile Yapay Zeka'nın tahmin çizgisini (Kırmızı Kesik Çizgi) birleştirir.")
                    
                    # Geçmiş ve Geleceği Birleştirip Çizelim
                    chart_data = pd.concat([df[['Close']], tahmin_df.rename(columns={'Tahmin': 'Close'})])
                    
                    # Basit çizgi grafiği ile gösterelim (Streamlit native chart daha interaktif)
                    st.line_chart(chart_data)

    except Exception as e:
        st.error(f"Hata oluştu: {e}")

else:
    st.info("👈 Sol menüden hisse seç ve Küreyi Çalıştır!")