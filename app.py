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

# Daha eğlenceli giriş kutuları
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

# Havalı bir başlık görseli (Banner)
st.image("https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?q=80&w=1200&auto=format&fit=crop", use_column_width=True)
st.title(f"🎢 {hisse} Lunaparkı")

if st.sidebar.button("Analizi Başlat 🔥", type="primary"):
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
