import streamlit as st
import yfinance as yf
import pandas as pd
import mplfinance as mpf

# 1. SAYFA AYARLARI
st.set_page_config(
    page_title="Borsa Avcısı Arcade",
    layout="wide",
    page_icon="🦁",
    initial_sidebar_state="expanded"
)

# 2. YAN MENÜ (SOL PANEL)
st.sidebar.header("🎮 Kontrol Kulesi")
st.sidebar.write("Hisseni seç ve oyuna başla!")

# Giriş Kutuları
hisse = st.sidebar.text_input("🎯 Hedef Hisse (Örn: SASA):", "EUPWR").upper()
periyot = st.sidebar.select_slider(
    "⏳ Zaman Makinesi:", 
    options=["1mo", "3mo", "6mo", "1y", "2y"],
    value="6mo"
)
hareketli_ort = st.sidebar.toggle("Ortalamaları Göster 📉", value=True)

st.sidebar.markdown("---")
st.sidebar.caption("🚀 Powered by **Yönetici Eren**")

# 3. ANA EKRAN (SAĞ TARAF)

# Başlık Görseli - 3 sütunlu layout (1, 2, 1 oranında)
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?q=80&w=1200&auto=format&fit=crop", use_column_width=True)
    
st.title(f"🎢 {hisse} Lunaparkı")

if st.sidebar.button("Analizi Başlat 🔥", type="primary"):
    # --- TRY BLOĞU BAŞLIYOR (Hata koruması) ---
    try:
        kodu = hisse + ".IS" if not hisse.endswith(".IS") else hisse
        
        # Eğlenceli yükleme ekranı
        with st.status("Veriler yükleniyor...", expanded=True) as status:
            st.write("📡 Uyduyla bağlantı kuruluyor...")
            df = yf.Ticker(kodu).history(period=periyot)
            st.write("🧠 Yapay zeka hesaplama yapıyor...")
            
            if df.empty:
                status.update(label="Hata! Veri yok.", state="error", expanded=False)
                st.error("💥псt! Bu hisseyi bulamadık. Kodunu kontrol et.")
            else:
                # --- HESAPLAMALAR ---
                df['SMA20'] = df['Close'].rolling(window=20).mean()
                df['SMA50'] = df['Close'].rolling(window=50).mean()
                
                delta = df['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                df['RSI'] = 100 - (100 / (1 + rs))

                status.update(label="Analiz Hazır! 🚀", state="complete", expanded=False)

                # --- KARTLAR (METRICS) ---
                son_fiyat = df['Close'].iloc[-1]
                onceki_fiyat = df['Close'].iloc[-2]
                degisim = son_fiyat - onceki_fiyat
                son_rsi = df['RSI'].iloc[-1]
                
                st.markdown("### 🎫 Anlık Durum Bileti")
                col1, col2, col3 = st.columns(3)
                
                col1.metric("💰 Fiyat", f"{son_fiyat:.2f} TL", f"{degisim:.2f} TL")
                col2.metric("🌡️ RSI Motor Sıcaklığı", f"{son_rsi:.1f}", delta_color="off")
                
                trend_yonu = "YÜKSELİŞ 🚀" if df['SMA20'].iloc[-1] > df['SMA50'].iloc[-1] else "DÜŞÜŞ 🐻"
                col3.metric("🎢 Trend Yönü", trend_yonu)
                
                # --- RENKLİ ROBOT YORUMU ---
                st.markdown("---")
                st.subheader("🤖 Robotun Tavsiyesi")
                
                if son_rsi < 30:
                    st.success("💎 **FIRSAT ALARMI!** Hisse çok ucuzladı (Aşırı Satım). Tepki yükselişi gelebilir!")
                elif son_rsi > 70:
                    st.error("🔥 **DİKKAT!** Motor çok ısındı (Aşırı Alım). Kâr satışı gelebilir, dikkatli ol.")
                else:
                    st.info("✅ **NORMAL SEYİR.** Trendi takip etmeye devam et. Aşırı bir durum yok.")

                # --- GRAFİK ---
                st.markdown("---")
                st.subheader("🎡 Teknik Grafik")
                
                apd = []
                if hareketli_ort:
                    apd = [
                        mpf.make_addplot(df['SMA20'], color='lime', width=1.5), 
                        mpf.make_addplot(df['SMA50'], color='fuchsia', width=1.5), 
                        mpf.make_addplot(df['RSI'], panel=1, color='cyan', ylabel='RSI') 
                    ]
                
                fig, ax = mpf.plot(
                    df, 
                    type='candle', 
                    style='nightclouds', 
                    addplot=apd, 
                    volume=True, 
                    returnfig=True, 
                    panel_ratios=(6,2),
                    figsize=(10,7)
                )
                st.pyplot(fig)

    # --- KRİTİK KISIM: KOPAN PARÇA BURASIYDI ---
    except Exception as e:
        st.error(f"Bir şeyler ters gitti: {e}")

else:
    st.info("👈 Sol taraftan bir hisse seç ve 'Analizi Başlat' butonuna bas!")
