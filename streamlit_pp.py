# app.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
import random
import yfinance as yf
# إعداد الصفحة
st.set_page_config(page_title="أداة المضاربة اليومية", layout="wide")

# بيانات وهمية للسوق الأمريكي (يجب لاحقًا ربطها ببيانات حقيقية)
def load_market_data():
    return {
        "S&P 500": {"value": 4200.50, "change": +0.52},
        "NASDAQ": {"value": 13500.25, "change": -0.36},
        "Dow Jones": {"value": 34000.75, "change": +0.25}
    }

# إنشاء بيانات وهمية للأسهم
def load_stock_data_real(symbols):
    data = []
    for symbol in symbols:
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            hist = stock.history(period="2d")  # اليوم الحالي واليوم السابق

            if hist.shape[0] < 2:
                continue

            current_price = hist['Close'].iloc[-1]
            previous_close = hist['Close'].iloc[-2]
            volume = hist['Volume'].iloc[-1]
            change = round((current_price - previous_close) / previous_close * 100, 2)

            data.append({
                "Symbol": symbol,
                "Current Price": round(current_price, 2),
                "Previous Close": round(previous_close, 2),
                "Volume": int(volume),
                "Change %": change,
                "Volatility": round(abs(current_price - previous_close), 2),  # تبسيط للتقلب
                "Sentiment": 0  # مؤقتًا 0 - يمكن استبداله بتحليل مشاعر لاحقًا
            })

        except Exception as e:
            print(f"خطأ في السهم {symbol}: {e}")
    return pd.DataFrame(data)


# تحليل معنويات السوق البسيط
def analyze_market_sentiment(df):
    avg_sentiment = df['Sentiment'].mean()
    if avg_sentiment > 0.3:
        return "🟢 معنويات السوق إيجابية"
    elif avg_sentiment < -0.3:
        return "🔴 معنويات السوق سلبية"
    else:
        return "🟡 معنويات السوق محايدة"

# تصفية الأسهم بناءً على معايير المستخدم
def filter_stocks(df, min_volume, min_change, price_min, price_max):
    return df[
        (df["Volume"] >= min_volume) &
        (df["Change %"] >= min_change) &
        (df["Current Price"] >= price_min) &
        (df["Current Price"] <= price_max)
    ]

# عرض المؤشرات الرئيسية
def display_market_overview(market_data):
    st.subheader("🧭 نظرة على السوق")
    cols = st.columns(len(market_data))
    for i, (index, data) in enumerate(market_data.items()):
        change_color = "green" if data["change"] >= 0 else "red"
        cols[i].metric(index, f'{data["value"]}', f'{data["change"]}%', delta_color="inverse")

# الرسم البياني للسعر
def display_chart(stock):
    fig = px.line(
        x=[datetime.now().replace(hour=i) for i in range(10, 16)],
        y=np.random.normal(loc=stock["Current Price"], scale=stock["Volatility"], size=6),
        labels={"x": "الوقت", "y": "السعر"},
        title=f"🔹 الرسم البياني لسهم {stock['Symbol']}"
    )
    st.plotly_chart(fig, use_container_width=True)

# دالة رئيسية واحدة لكل التطبيق
def main():
    st.title("📊 أداة المضاربة اليومية الذكية")
    st.markdown("أداة تساعدك على فلترة الأسهم وتحليلها بسرعة باستخدام الذكاء الاصطناعي وبيانات السوق الحية.")

    # عرض نظرة على السوق
    market_data = load_market_data()
    display_market_overview(market_data)

    # الشريط الجانبي للفلاتر
    st.sidebar.header("⚙️ إعدادات الفلترة")
    min_volume = st.sidebar.slider("أدنى حجم تداول", 10000, 1000000, 50000, step=10000)
    min_change = st.sidebar.slider("أدنى نسبة تغيير إيجابية", 0.0, 10.0, 1.0, step=0.1)
    price_range = st.sidebar.slider("نطاق السعر", 10.0, 500.0, (50.0, 200.0))

    # تحميل بيانات الأسهم وتطبيق الفلترة
    df = load_stock_data()
    filtered_df = filter_stocks(df, min_volume, min_change, price_range[0], price_range[1])

    # عرض معنويات السوق
    sentiment_result = analyze_market_sentiment(filtered_df)
    st.subheader("🧠 تحليل معنويات السوق")
    st.info(sentiment_result)

    # عرض الأسهم المفلترة
    st.subheader("📈 الأسهم المفلترة")
    st.dataframe(filtered_df, use_container_width=True)

    # اختيار سهم لعرض تفاصيله
    st.subheader("🔍 تحليل سهم محدد")
    selected_symbol = st.selectbox("اختر سهمًا لتحليله", filtered_df["Symbol"])
    selected_stock = filtered_df[filtered_df["Symbol"] == selected_symbol].iloc[0]
    st.write(f"تفاصيل السهم: **{selected_symbol}**")
    st.write(f"السعر الحالي: {selected_stock['Current Price']}$")
    st.write(f"النسبة المئوية للتغيير: {selected_stock['Change %']}%")
    st.write(f"حجم التداول: {selected_stock['Volume']}")
    st.write(f"التقلب: {selected_stock['Volatility']}")
    st.write(f"المعنويات: {round(selected_stock['Sentiment'], 2)}")

    # عرض الرسم البياني
    display_chart(selected_stock)

    # قسم المحفظة (قيد التطوير)
    st.subheader("💼 محفظتك")
    st.markdown("🚧 سيتم قريبًا تمكين إضافة الأسهم للمراقبة أو البيع والشراء.")

# تشغيل التطبيق
if __name__ == "__main__":
    main()
