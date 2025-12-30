import streamlit as st
import yfinance as yf
import pandas as pd
import mplfinance as mpf

# Sayfa Ayarı
st.set_page_config(page_title="Borsa Avcısı", layout="wide", page_icon="🦁")

st.title("🦁 Borsa Avcısı: Mobil Versiyon")

# Girişler
col1, col2 = st.columns(2)
with col1:
    hisse = st.text_input("Hisse Kodu (Örn: SASA):", "EUPWR").upper()
with col2:
    periyot = st.selectbox("Zaman:", ["1mo", "3mo", "6mo", "1y"], index=2)

if st.button("Analiz Et 🚀", use_container_width=True):
    try:
        kodu = hisse + ".IS" if not hisse.endswith(".IS") else hisse
        
        with st.spinner('Veriler çekiliyor...'):
            df = yf.Ticker(kodu).history(period=periyot)
            
            if df.empty:
                st.error("Veri bulunamadı!")
            else:
                # Hesaplamalar
                df['SMA20'] = df['Close'].rolling(window=20).mean()
                df['SMA50'] = df['Close'].rolling(window=50).mean()
                
                # RSI
                delta = df['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                df['RSI'] = 100 - (100 / (1 + rs))
                
                # Kartlar
                son_fiyat = df['Close'].iloc[-1]
                son_rsi = df['RSI'].iloc[-1]
                
                c1, c2, c3 = st.columns(3)
                c1.metric("Fiyat", f"{son_fiyat:.2f} TL")
                c2.metric("RSI", f"{son_rsi:.1f}")
                
                trend = "YÜKSELİŞ 🟢" if df['SMA20'].iloc[-1] > df['SMA50'].iloc[-1] else "DÜŞÜŞ 🔴"
                c3.metric("Trend", trend)
                
                # Grafik
                st.subheader("Teknik Grafik")
                apd = [
                    mpf.make_addplot(df['SMA20'], color='green'),
                    mpf.make_addplot(df['SMA50'], color='red'),
                    mpf.make_addplot(df['RSI'], panel=1, color='purple', ylabel='RSI')
                ]
                
                fig, ax = mpf.plot(df, type='candle', style='yahoo', addplot=apd, volume=True, returnfig=True, panel_ratios=(6,2))
                st.pyplot(fig)
                
    except Exception as e:
        st.error(f"Hata: {e}")