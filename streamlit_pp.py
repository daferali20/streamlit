import streamlit as st
import yfinance as yf
import pandas as pd
import requests
import plotly.graph_objects as go
from datetime import datetime, timedelta
from textblob import TextBlob
import random

#----
if 'telegram_setup' not in st.session_state:
    st.session_state.telegram_setup = {
        'bot_token': '',
        'chat_id': ''
    }

def send_telegram_alert(message: str):
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
        if response.status_code == 200:
            return True
        else:
            st.error(f"❌ فشل الإرسال. الكود: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        st.error(f"❌ حدث خطأ أثناء الإرسال: {e}")
        return False
    #----
# تهيئة الصفحة
st.set_page_config(
    page_title="ProTrade - أداة المضاربة اليومية",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)
 
st.divider()
st.subheader("🚀 تجربة إرسال تنبيه")

sample_message = "🚨 <b>تنبيه تجريبي من بوت الأسهم</b>\nاختبار الاتصال بـ Telegram."

if st.button("📨 إرسال تنبيه تجريبي"):
    if send_telegram_alert(sample_message):
        st.success("✅ تم إرسال التنبيه بنجاح")
    else:
        st.error("❌ فشل في إرسال التنبيه")
        #--- الشريط الجانبي للتلقرام ---
with st.sidebar.expander("⚙️ إعدادات Telegram"):
    new_token = st.text_input("Bot Token", st.session_state.telegram_setup['bot_token'])
    new_chat_id = st.text_input("Chat ID", st.session_state.telegram_setup['chat_id'])

    if st.button("حفظ الإعدادات"):
        st.session_state.telegram_setup.update({
            'bot_token': new_token,
            'chat_id': new_chat_id
        })
        st.success("✅ تم حفظ الإعدادات")

    if st.button("اختبار الإرسال"):
        success = send_telegram_alert("🔔 <b>هذا رسالة اختبار من تطبيق التداول</b>\nتم تكوين الإعدادات بنجاح!")
        if success:
            st.success("📬 تم إرسال الرسالة الاختبارية بنجاح")
        else:
            st.error("❌ فشل إرسال الرسالة")

    #------ لل-----لل ----
# إعداد التطبيق الرئيسي
def main():
    # --- شريط جانبي للمعايير ---
    st.sidebar.header("⚙️ معايير البحث المتقدمة")
    
    with st.sidebar.expander("🔍 فلاتر الأسهم"):
        min_volume = st.number_input("الحد الأدنى لحجم التداول (مليون):", 1, 1000, 5)
        min_change = st.number_input("الحد الأدنى للتغيير اليومي (%):", 0.1, 50.0, 2.0)
        sector = st.selectbox("القطاع:", ["الكل", "تكنولوجيا", "مالية", "رعاية صحية", "طاقة"])
        price_range = st.slider("نطاق السعر ($):", 0.0, 1000.0, (10.0, 500.0))
    
    with st.sidebar.expander("🔔 إعدادات التنبيهات"):
        alert_threshold = st.number_input("حد التنبيه (% تغيير):", 0.1, 20.0, 5.0)
        enable_telegram = st.checkbox("تفعيل تنبيهات التليجرام")
   
    # --- قسم المؤشرات الرئيسية ---
    st.markdown("## 📊 لوحة تحكم المضاربة اليومية")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        sp500 = yf.Ticker("^GSPC")
        sp_change = round(sp500.history(period="1d")['Close'].pct_change().iloc[-1]*100, 2)
        st.metric("S&P 500", f"{sp500.history(period='1d')['Close'].iloc[-1]:.2f}", f"{sp_change}%")
    
    with col2:
        nasdaq = yf.Ticker("^IXIC")
        nasdaq_change = round(nasdaq.history(period="1d")['Close'].pct_change().iloc[-1]*100, 2)
        st.metric("NASDAQ", f"{nasdaq.history(period='1d')['Close'].iloc[-1]:.2f}", f"{nasdaq_change}%")
    
    with col3:
        dow = yf.Ticker("^DJI")
        dow_change = round(dow.history(period="1d")['Close'].pct_change().iloc[-1]*100, 2)
        st.metric("Dow Jones", f"{dow.history(period='1d')['Close'].iloc[-1]:.2f}", f"{dow_change}%")
    
    # --- جلب بيانات الأسهم ---
    @st.cache_data(ttl=300)  # تحديث كل 5 دقائق
    def get_active_stocks():
        tickers = ["AAPL", "TSLA", "AMZN", "META", "GOOG", "MSFT", "NVDA", 
                  "JPM", "BAC", "WFC", "XOM", "CVX", "JNJ", "PFE"]
        data = yf.download(tickers, period="1d")["Volume"]
        df = pd.DataFrame(data.mean(), columns=["Volume"])
        df["% Change"] = [round(x*100, 2) for x in yf.download(tickers, period="1d")["Close"].pct_change().iloc[-1]]
        df["Price"] = [round(x, 2) for x in yf.download(tickers, period="1d")["Close"].iloc[-1]]
        df["Symbol"] = df.index
        
        # تصنيف القطاعات (مثال مبسط)
        sectors = {
            "AAPL": "تكنولوجيا", "TSLA": "تكنولوجيا", "AMZN": "تكنولوجيا",
            "META": "تكنولوجيا", "GOOG": "تكنولوجيا", "MSFT": "تكنولوجيا",
            "NVDA": "تكنولوجيا", "JPM": "مالية", "BAC": "مالية", "WFC": "مالية",
            "XOM": "طاقة", "CVX": "طاقة", "JNJ": "رعاية صحية", "PFE": "رعاية صحية"
        }
        df["Sector"] = df["Symbol"].map(sectors)
        
        return df.reset_index(drop=True)
    
    # --- تصفية وعرض البيانات ---
    df = get_active_stocks()
    
    # تطبيق الفلاتر
    df_filtered = df[
        (df["Volume"] >= min_volume * 1e6) & 
        (df["% Change"].abs() >= min_change) &
        (df["Price"] >= price_range[0]) & 
        (df["Price"] <= price_range[1])
    ]
    
    if sector != "الكل":
        df_filtered = df_filtered[df_filtered["Sector"] == sector]
    
    # --- عرض الأسهم الموصى بها ---
    st.markdown(f"### 📈 أفضل الأسهم للمضاربة اليومية (حجم > {min_volume}M, تغيير > {min_change}%)")
    
    if not df_filtered.empty:
        # تنبيهات للأسهم ذات التغير الكبير
        alert_stocks = df_filtered[df_filtered["% Change"].abs() >= alert_threshold]
        if not alert_stocks.empty:
            for _, row in alert_stocks.iterrows():
                direction = "صعود" if row["% Change"] > 0 else "هبوط"
                st.warning(f"تنبيه! {row['Symbol']} في {direction} قوي ({abs(row['% Change'])}%)")
        
        # عرض البيانات في جدول منظم
        st.dataframe(
            df_filtered.sort_values("% Change", ascending=False),
            column_config={
                "Symbol": "الرمز",
                "Price": st.column_config.NumberColumn("السعر ($)", format="%.2f"),
                "% Change": st.column_config.NumberColumn("التغيير %", format="%.2f"),
                "Volume": st.column_config.NumberColumn("الحجم", format="%.0f"),
                "Sector": "القطاع"
            },
            hide_index=True,
            use_container_width=True
        )
        
        # --- تحليل السهم المحدد ---
        st.markdown("### 📊 تحليل السهم المحدد")
        selected_stock = st.selectbox("اختر سهمًا للتحليل:", df_filtered["Symbol"])
        
        if selected_stock:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # مخطط الشموع اليابانية
                st.markdown("#### 📉 مخطط الشموع اليابانية (5 دقائق)")
                stock_data = yf.download(selected_stock, period="1d", interval="5m")
                
                fig = go.Figure(data=[go.Candlestick(
                    x=stock_data.index,
                    open=stock_data['Open'],
                    high=stock_data['High'],
                    low=stock_data['Low'],
                    close=stock_data['Close']
                )])
                fig.update_layout(
                    xaxis_rangeslider_visible=False,
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # تحليل المشاعر من الأخبار
                st.markdown("#### 🗨️ تحليل مشاعر الأخبار")
                news = get_stock_news(selected_stock)
                if not news.empty:
                    sentiments = [TextBlob(str(headline)).sentiment.polarity for headline in news['headline']]
                    avg_sentiment = sum(sentiments) / len(sentiments)
                    
                    if avg_sentiment > 0.2:
                        st.success(f"مشاعر إيجابية قوية ({avg_sentiment:.2f})")
                    elif avg_sentiment > 0:
                        st.info(f"مشاعر إيجابية ({avg_sentiment:.2f})")
                    elif avg_sentiment < -0.2:
                        st.error(f"مشاعر سلبية قوية ({avg_sentiment:.2f})")
                    else:
                        st.warning(f"مشاعر سلبية ({avg_sentiment:.2f})")
                
            with col2:
                # معلومات السهم الأساسية
                st.markdown("#### ℹ️ معلومات السهم")
                stock_info = yf.Ticker(selected_stock).info
                
                info_cols = st.columns(2)
                info_cols[0].metric("السعر الحالي", f"{stock_info.get('currentPrice', 'N/A')}")
                info_cols[1].metric("PE Ratio", f"{stock_info.get('trailingPE', 'N/A')}")
                
                info_cols[0].metric("52 أسبوع أعلى", f"{stock_info.get('fiftyTwoWeekHigh', 'N/A')}")
                info_cols[1].metric("52 أسبوع أدنى", f"{stock_info.get('fiftyTwoWeekLow', 'N/A')}")
                
                st.metric("القيمة السوقية", f"{stock_info.get('marketCap', 'N/A')/1e9:.2f} مليار")
                
                # المؤشرات الفنية
                st.markdown("#### 📊 المؤشرات الفنية")
                
                # حساب RSI مبسط
                delta = stock_data['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs))
                
                current_rsi = rsi.iloc[-1]
                if current_rsi > 70:
                    st.error(f"RSI: {current_rsi:.2f} (ذروة شراء)")
                elif current_rsi < 30:
                    st.success(f"RSI: {current_rsi:.2f} (ذروة بيع)")
                else:
                    st.info(f"RSI: {current_rsi:.2f} (طبيعي)")
                
                # إشارات تداول
                st.markdown("#### 💡 إشارات تداول")
                
                # إشارة المتوسط المتحرك
                ma_50 = stock_data['Close'].rolling(window=50).mean().iloc[-1]
                ma_200 = stock_data['Close'].rolling(window=200).mean().iloc[-1]
                
                if ma_50 > ma_200:
                    st.success("إشارة شراء: المتوسط 50 يوم فوق المتوسط 200 يوم")
                else:
                    st.error("إشارة بيع: المتوسط 50 يوم تحت المتوسط 200 يوم")
                
                # إشارة حجم التداول
                avg_volume = stock_data['Volume'].mean()
                last_volume = stock_data['Volume'].iloc[-1]
                
                if last_volume > avg_volume * 1.5:
                    st.info("حجم تداول مرتفع: حركة قوية")
        
        # --- قسم الأخبار ---
        st.markdown("### 📰 آخر الأخبار المؤثرة على السوق")
        news_df = get_market_news()
        
        if not news_df.empty:
            for _, news_item in news_df.iterrows():
                with st.expander(f"{news_item['headline']} - {news_item['source']}"):
                    st.write(f"**التاريخ:** {datetime.fromtimestamp(news_item['datetime']).strftime('%Y-%m-%d %H:%M')}")
                    st.write(news_item['summary'] if pd.notna(news_item['summary']) else "لا يوجد ملخص")
                    if pd.notna(news_item['url']):
                        st.markdown(f"[قراءة المزيد]({news_item['url']})")
    else:
        st.warning("لا توجد أسهم مطابقة لمعايير البحث المحددة")
    
    # --- قسم المحفظة ---
    st.markdown("### 💼 متتبع المحفظة")
    
    if 'portfolio' not in st.session_state:
        st.session_state.portfolio = pd.DataFrame(columns=['Stock', 'Shares', 'Entry Price'])
    
    with st.form("portfolio_form"):
        cols = st.columns(4)
        stock = cols[0].text_input("رمز السهم", "AAPL").upper()
        shares = cols[1].number_input("عدد الأسهم", 1, 10000, 1)
        entry_price = cols[2].number_input("سعر الدخول ($)", 0.01, 10000.0, 150.0)
        
        if cols[3].form_submit_button("إضافة إلى المحفظة"):
            new_entry = pd.DataFrame([[stock, shares, entry_price]], 
                                    columns=['Stock', 'Shares', 'Entry Price'])
            st.session_state.portfolio = pd.concat([st.session_state.portfolio, new_entry], ignore_index=True)
    
    if not st.session_state.portfolio.empty:
        # حساب القيمة الحالية
        current_prices = []
        for stock in st.session_state.portfolio['Stock']:
            try:
                price = yf.Ticker(stock).history(period='1d')['Close'].iloc[-1]
                current_prices.append(price)
            except:
                current_prices.append(0)
        
        st.session_state.portfolio['Current Price'] = current_prices
        st.session_state.portfolio['Value'] = st.session_state.portfolio['Shares'] * st.session_state.portfolio['Current Price']
        st.session_state.portfolio['P/L'] = (st.session_state.portfolio['Current Price'] - st.session_state.portfolio['Entry Price']) * st.session_state.portfolio['Shares']
        st.session_state.portfolio['P/L %'] = ((st.session_state.portfolio['Current Price'] / st.session_state.portfolio['Entry Price']) - 1) * 100
        
        st.dataframe(
            st.session_state.portfolio,
            column_config={
                "Stock": "السهم",
                "Shares": "الأسهم",
                "Entry Price": st.column_config.NumberColumn("سعر الدخول", format="%.2f"),
                "Current Price": st.column_config.NumberColumn("السعر الحالي", format="%.2f"),
                "Value": st.column_config.NumberColumn("القيمة", format="%.2f"),
                "P/L": st.column_config.NumberColumn("الربح/الخسارة", format="%.2f"),
                "P/L %": st.column_config.NumberColumn("النسبة %", format="%.2f")
            },
            hide_index=True,
            use_container_width=True
        )
        #----  الاضافة الجديدة ---
         
        #------------------------------------------------------------
        # ملخص المحفظة
        total_value = st.session_state.portfolio['Value'].sum()
        total_pl = st.session_state.portfolio['P/L'].sum()
        total_pl_percent = (total_pl / (total_value - total_pl)) * 100 if (total_value - total_pl) != 0 else 0
        
        cols = st.columns(3)
        cols[0].metric("القيمة الإجمالية", f"${total_value:,.2f}")
        cols[1].metric("إجمالي الربح/الخسارة", f"${total_pl:,.2f}", f"{total_pl_percent:.2f}%")
        
        if cols[2].button("حذف المحفظة"):
            st.session_state.portfolio = pd.DataFrame(columns=['Stock', 'Shares', 'Entry Price'])
            st.rerun()

# --- وظائف مساعدة ---
@st.cache_data(ttl=3600)  # تحديث كل ساعة
def get_market_news():
    try:
        api_key = st.secrets.get("FINNHUB_API_KEY", "d0s84hpr01qkkpltj8j0d0s84hpr01qkkpltj8jg")
        url = f"https://finnhub.io/api/v1/news?category=general&token={api_key}"
        response = requests.get(url).json()
        df = pd.DataFrame(response)[:10]  # عرض آخر 10 أخبار
        return df[['headline', 'source', 'summary', 'url', 'datetime']]
    except:
        return pd.DataFrame()

@st.cache_data(ttl=600)  # تحديث كل 10 دقائق
def get_stock_news(symbol):
    try:
        api_key = st.secrets.get("FINNHUB_API_KEY", "d0s84hpr01qkkpltj8j0d0s84hpr01qkkpltj8jg")
        url = f"https://finnhub.io/api/v1/company-news?symbol={symbol}&from={(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')}&to={datetime.now().strftime('%Y-%m-%d')}&token={api_key}"
        response = requests.get(url).json()
        df = pd.DataFrame(response)[:5]  # عرض آخر 5 أخبار للسهم
        return df[['headline', 'source', 'summary', 'url', 'datetime']]
    except:
        return pd.DataFrame()

if __name__ == "__main__":
    main()
