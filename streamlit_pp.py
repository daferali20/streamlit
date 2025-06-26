import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from datetime import datetime, timedelta
from textblob import TextBlob
import plotly.graph_objects as go

# ---------- إعدادات أساسية ----------
st.set_page_config(page_title="ProTrade - أداة المضاربة اليومية", page_icon="📈", layout="wide")

# ---------- إعدادات Telegram ----------
DEFAULT_BOT_TOKEN = "1079128294:AAHre_zWJNLLEBG1toniBDYbX5AKa6EokgM"
DEFAULT_CHAT_ID = "@D_Option"
#TELEGRAM_BOT_TOKEN="1079128294:AAHre_zWJNLLEBG1toniBDYbX5AKa6EokgM"
#TELEGRAM_CHAT_ID="@D_Option"

if 'telegram_setup' not in st.session_state:
    st.session_state.telegram_setup = {
        'bot_token': DEFAULT_BOT_TOKEN,
        'chat_id': DEFAULT_CHAT_ID
    }

def send_telegram_alert(message: str) -> bool:
    """إرسال تنبيه إلى Telegram"""
    try:
        bot_token = st.session_state.telegram_setup["bot_token"]
        chat_id = st.session_state.telegram_setup["chat_id"]

        if not bot_token or not chat_id:
            st.warning("⚠️ لم يتم ضبط إعدادات Telegram بعد.")
            return False

        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML"
        }

        response = requests.post(url, json=payload)
        return response.status_code == 200

    except Exception as e:
        st.error(f"❌ خطأ في الإرسال إلى Telegram: {e}")
        return False

# ---------- إعداد الشريط الجانبي ----------
with st.sidebar.expander("⚙️ إعدادات Telegram"):
    new_token = st.text_input("Bot Token", st.session_state.telegram_setup['bot_token'])
    new_chat_id = st.text_input("Chat ID", st.session_state.telegram_setup['chat_id'])

    if st.button("💾 حفظ الإعدادات"):
        st.session_state.telegram_setup['bot_token'] = new_token
        st.session_state.telegram_setup['chat_id'] = new_chat_id
        st.success("✅ تم حفظ إعدادات Telegram")

    if st.button("📨 إرسال رسالة اختبار"):
        if send_telegram_alert("🔔 <b>رسالة اختبار من تطبيق المضاربة</b>\nتم إعداد Telegram بنجاح."):
            st.success("✅ تم إرسال الرسالة الاختبارية")
        else:
            st.error("❌ فشل إرسال الرسالة")

# ---------- مدخلات المستخدم ----------
st.sidebar.header("🔍 فلاتر البحث")
min_volume = st.sidebar.number_input("الحد الأدنى لحجم التداول (مليون):", 1, 1000, 5)
min_change = st.sidebar.number_input("الحد الأدنى للتغير اليومي (%):", 0.1, 50.0, 2.0)
price_range = st.sidebar.slider("نطاق السعر ($):", 0.0, 1000.0, (10.0, 500.0))
enable_telegram = st.sidebar.checkbox("✅ تفعيل إرسال تنبيه Telegram يوميًا 5 مساء")

# ---------- تحميل بيانات الأسهم ----------
@st.cache_data(ttl=300)
def get_active_stocks():
    tickers = ["AAPL", "TSLA", "AMZN", "META", "GOOG", "MSFT", "NVDA", "JPM", "BAC", "WFC", "XOM", "CVX", "JNJ", "PFE"]
    prices = yf.download(tickers, period="1d")
    
    df = pd.DataFrame({
        "Symbol": tickers,
        "Price": [round(prices["Close"][t].iloc[-1], 2) for t in tickers],
        "% Change": [round(prices["Close"][t].pct_change().iloc[-1]*100, 2) for t in tickers],
        "Volume": [int(prices["Volume"][t].iloc[-1]) for t in tickers]
    })

    sectors = {
        "AAPL": "تكنولوجيا", "TSLA": "تكنولوجيا", "AMZN": "تكنولوجيا",
        "META": "تكنولوجيا", "GOOG": "تكنولوجيا", "MSFT": "تكنولوجيا",
        "NVDA": "تكنولوجيا", "JPM": "مالية", "BAC": "مالية", "WFC": "مالية",
        "XOM": "طاقة", "CVX": "طاقة", "JNJ": "رعاية صحية", "PFE": "رعاية صحية"
    }
    df["Sector"] = df["Symbol"].map(sectors)
    return df

df = get_active_stocks()

# ---------- تصفية البيانات حسب الفلاتر ----------
df_filtered = df[
    (df["Volume"] >= min_volume * 1e6) &
    (df["% Change"].abs() >= min_change) &
    (df["Price"] >= price_range[0]) &
    (df["Price"] <= price_range[1])
]

# ---------- إرسال التنبيه تلقائيًا الساعة 5 مساء ----------
top_gainers = df_filtered[df_filtered["% Change"] > 0].sort_values("% Change", ascending=False).head(5)
current_hour = datetime.now().hour
today_key = f"telegram_sent_{datetime.now().date()}"

if enable_telegram and current_hour == 17 and not st.session_state.get(today_key, False) and not top_gainers.empty:
    # ----------- محتوى الرسالة المعدل ----------- #
    message = "<b>📈 تنبيه يومي - أفضل الأسهم ارتفاعًا:</b>\n\n"
    for _, row in top_gainers.iterrows():
        message += f"🔹 <b>{row['Symbol']}</b>: {row['% Change']}% ⬆️ | السعر: ${row['Price']}\n"
    message += "\n🔔 المصدر: تطبيق المضاربة ProTrade"

    if send_telegram_alert(message):
        st.success("✅ تم إرسال تنبيه Telegram اليومي")
        st.session_state[today_key] = True
    else:
        st.error("❌ فشل إرسال تنبيه Telegram")

# ---------- عرض جدول الأسهم ----------
st.markdown(f"## 📊 قائمة الأسهم بعد الفلترة")
if df_filtered.empty:
    st.warning("⚠️ لا توجد نتائج مطابقة للفلاتر المحددة")
else:
    st.dataframe(
        df_filtered.sort_values("% Change", ascending=False),
        column_config={
            "Symbol": "الرمز",
            "Price": st.column_config.NumberColumn("السعر ($)", format="%.2f"),
            "% Change": st.column_config.NumberColumn("التغيير %", format="%.2f"),
            "Volume": st.column_config.NumberColumn("الحجم", format="%.0f"),
            "Sector": "القطاع"
        },
        use_container_width=True,
        hide_index=True
    )
