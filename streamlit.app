import streamlit as st
import yfinance as yf
import pandas as pd
import requests

# عنوان التطبيق
st.title("🤑 أداة المضاربة اليومية في الأسهم الأمريكية")

# شريط جانبي لإدخال المعايير
st.sidebar.header("🔍 معايير البحث")
min_volume = st.sidebar.number_input("الحد الأدنى لحجم التداول (مليون):", 1, 100, 5)
min_change = st.sidebar.number_input("الحد الأدنى للتغيير اليومي (%):", 1, 20, 5)

# جلب البيانات من Yahoo Finance (مثال: أكثر الأسهم نشاطًا)
@st.cache_data
def get_active_stocks():
    url = "https://finance.yahoo.com/most-active"
    tables = pd.read_html(url)
    df = tables[0]
    return df

# تصفية النتائج حسب المعايير
df = get_active_stocks()
df_filtered = df[
    (df["Volume"] >= min_volume * 1e6) & 
    (df["% Change"].abs() >= min_change)
]

# عرض النتائج
st.subheader(f"📈 أفضل الأسهم للمضاربة اليومية (حجم > {min_volume}M, تغيير > {min_change}%)")
st.dataframe(df_filtered)

# إظهار مخطط سريع للسهم المختار
selected_stock = st.selectbox("اختر سهمًا لرسم مخططه:", df_filtered["Symbol"])
if selected_stock:
    stock_data = yf.download(selected_stock, period="1d", interval="5m")
    st.line_chart(stock_data["Close"])

# قسم الأخبار (باستخدام Finnhub API - يحتاج API Key)
api_key = "your_finnhub_api_key"  # استبدله بمفتاحك
@st.cache_data
def get_news():
    url = f"https://finnhub.io/api/v1/news?category=general&token={api_key}"
    response = requests.get(url).json()
    return pd.DataFrame(response)[:5]  # عرض آخر 5 أخبار

st.subheader("📰 آخر الأخبار المؤثرة على السوق")
news_df = get_news()
st.dataframe(news_df[["headline", "source"]])
