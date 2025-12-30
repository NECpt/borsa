import streamlit as st
import yfinance as yf
import pandas as pd
import mplfinance as mpf

# 1. SAYFA AYARLARI (Geniş Ekran)
st.set_page_config(
    page_title="Borsa Avcısı Pro",
    layout="wide",
    page_icon="🦁",
    initial_sidebar_state="expanded"
)

# 2. YAN MENÜ (SOL PANEL) - GİRİŞLER BURADA
st.sidebar.header("🦁 Kontrol Paneli")
st.sidebar.info("Hisse kodunu ve ayarları buradan seçebilirsin.")

hisse = st.sidebar.text_input("Hisse Kodu (Örn: THYAO):", "EUPWR").upper()
periyot = st.sidebar.select_slider(
    "Zaman Aralığı:", 
    options=["1mo", "3mo", "6mo", "1y", "2y"],
    value="6mo"
)
hareketli_ort = st.sidebar.checkbox("Ortalamaları Göster", value=True)

st.sidebar.markdown("---")
st.sidebar.write("Developed by **Eren**")

# 3. ANA EKRAN (SAĞ TARAF)
st.title(f"📊 {hisse} Analiz Raporu")

# Verileri Çekme Butonu (Sidebar'da değil ana ekranda da olabilir)
if st.sidebar.button("Analizi Başlat 🚀", type="primary"):
    try:
        # Kodun sonuna .IS ekleme kontrolü
        kodu = hisse + ".IS" if not hisse.endswith(".IS") else hisse
        
        with st.spinner(f'{kodu} verileri getiriliyor...'):
            # Veri İndirme
            df = yf.Ticker(kodu).history(period=periyot)
            
            if df.empty:
                st.error("Veri bulunamadı! Hisse kodunu kontrol et.")
            else:
                # --- HESAPLAMALAR ---
                df['SMA20'] = df['Close'].rolling(window=20).mean()
                df['SMA50'] = df['Close'].rolling(window=50).mean()
                
                # RSI Hesabı
                delta = df['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                df['RSI'] = 100 - (100 / (1 + rs))

                # --- ÜST BİLGİ KARTLARI (YAN YANA 4 SÜTUN) ---
                son_fiyat = df['Close'].iloc[-1]
                onceki_fiyat = df['Close'].iloc[-2]
                degisim = son_fiyat - onceki_fiyat
                son_rsi = df['RSI'].iloc[-1]
                
                col1, col2, col3, col4 = st.columns(4)
                
                col1.metric("Anlık Fiyat", f"{son_fiyat:.2f} TL", f"{degisim:.2f} TL")
                
                col2.metric("RSI (Güç)", f"{son_rsi:.1f}", delta_color="off")
                
                # Trend Durumu
                trend_yonu = "YÜKSELİŞ 🟢" if df['SMA20'].iloc[-1] > df['SMA50'].iloc[-1] else "DÜŞÜŞ 🔴"
                col3.metric("Trend Yönü", trend_yonu)
                
                # Robot Yorumu
                durum = "NÖTR"
                if son_rsi < 30: durum = "ALIM FIRSATI 💎"
                elif son_rsi > 70: durum = "SATIŞ RİSKİ 🔥"
                col4.metric("Robot Görüşü", durum)
                
                st.markdown("---")

                # --- SEKMELER (TABS) ---
                tab1, tab2 = st.tabs(["📈 Teknik Grafik", "📋 Veri Tablosu"])
                
                with tab1:
                    # Grafik Ayarları
                    apd = []
                    if hareketli_ort:
                        apd = [
                            mpf.make_addplot(df['SMA20'], color='green', width=1.5),
                            mpf.make_addplot(df['SMA50'], color='red', width=1.5),
                            mpf.make_addplot(df['RSI'], panel=1, color='purple', ylabel='RSI')
                        ]
                    
                    fig, ax = mpf.plot(
                        df, 
                        type='candle', 
                        style='yahoo', 
                        addplot=apd, 
                        volume=True, 
                        returnfig=True, 
                        panel_ratios=(6,2),
                        figsize=(10,6),
                        title=f"{hisse} Fiyat Hareketleri"
                    )
                    st.pyplot(fig)
                
                with tab2:
                    st.dataframe(df.sort_index(ascending=False), use_container_width=True)

    except Exception as e:
        st.error(f"Bir hata oluştu: {e}")

else:
    st.info("👈 Analize başlamak için sol menüden hisse seç ve butona bas.")
