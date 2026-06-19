import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.graph_objects as go
from datetime import date
import urllib.request
import json as _json
import streamlit.components.v1 as components
import locale
import folium
from streamlit_folium import st_folium
try:
    locale.setlocale(locale.LC_TIME, 'vi_VN.UTF-8')
except:
    pass

st.set_page_config(page_title="StreamWave Rain", page_icon="🌧️", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
*{box-sizing:border-box;margin:0;padding:0;}
html,body,[class*="css"],.stApp{font-family:'Inter',sans-serif;color:#1a1a1a;font-size:15px;}
#MainMenu,footer,header{visibility:hidden;}
.block-container{padding:0 !important;max-width:100% !important;}
::-webkit-scrollbar{width:5px;} ::-webkit-scrollbar-track{background:#f5eed8;} ::-webkit-scrollbar-thumb{background:#e0c870;border-radius:4px;}

/* NỀN */
.stApp{
    background:
        radial-gradient(circle at 10% 10%, rgba(255,180,50,0.50) 0%, transparent 40%),
        radial-gradient(circle at 90% 20%, rgba(255,120,40,0.38) 0%, transparent 40%),
        radial-gradient(circle at 30% 90%, rgba(255,210,70,0.45) 0%, transparent 45%),
        radial-gradient(circle at 80% 80%, rgba(255,160,60,0.38) 0%, transparent 40%),
        #fdf8f0 !important;
    background-attachment:fixed !important;
}

/* STREAMLIT WRAPPERS — transparent để glassmorphism hoạt động */
.stMarkdown,.element-container,
[data-testid="stVerticalBlock"],
[data-testid="stVerticalBlockBorderWrapper"],
[data-testid="column"],
[data-testid="stColumn"]>div,
[data-testid="stColumn"]>div>div,
section.main>div,.main>div{background:transparent !important;}

/* HEADER */
.app-header{background:linear-gradient(135deg,#ffffff 0%,#fff8e7 100%);border-bottom:2px solid #f0d890;padding:14px 28px;display:flex;align-items:center;justify-content:space-between;box-shadow:0 4px 24px rgba(200,160,40,0.10);}
.app-title{font-family:'Space Grotesk',sans-serif;font-size:2.1rem;font-weight:700;color:#b8860b;letter-spacing:-0.02em;}
.app-subtitle{font-size:1.1rem;font-weight:500;color:#6b5510;margin-top:2px;}
.app-meta{font-size:1.05rem;color:#6b5510;text-align:right;}

/* RISK CARD */
.risk-card{border-radius:16px;padding:22px;margin-bottom:14px;background:rgba(255,255,255,0.35) !important;backdrop-filter:blur(24px) saturate(200%) !important;-webkit-backdrop-filter:blur(24px) saturate(200%) !important;border:1px solid rgba(255,255,255,0.75) !important;box-shadow:0 8px 32px rgba(180,130,20,0.15),0 2px 8px rgba(180,130,20,0.10) !important;transition:all 0.3s ease;}
.risk-card.danger {background:rgba(255,230,235,0.35) !important;backdrop-filter:blur(24px) saturate(200%) !important;-webkit-backdrop-filter:blur(24px) saturate(200%) !important;border-color:rgba(240,128,152,0.7) !important;}
.risk-card.warning{background:rgba(255,245,215,0.35) !important;backdrop-filter:blur(24px) saturate(200%) !important;-webkit-backdrop-filter:blur(24px) saturate(200%) !important;border-color:rgba(244,176,96,0.7) !important;}
.risk-card.safe   {background:rgba(230,255,238,0.35) !important;backdrop-filter:blur(24px) saturate(200%) !important;-webkit-backdrop-filter:blur(24px) saturate(200%) !important;border-color:rgba(112,208,160,0.7) !important;}

/* PROB / STATION */
.prob-number{font-family:'Space Grotesk',sans-serif;font-size:5.2rem;font-weight:700;line-height:1;margin:8px 0 4px;}
.prob-danger{color:#c03050;} .prob-warning{color:#c07000;} .prob-safe{color:#207050;}
.station-name{font-family:'Space Grotesk',sans-serif;font-size:1.9rem;font-weight:600;color:#1a1a1a;}
.station-province{font-size:1.2rem;color:#2d2d2d;margin-top:2px;}

/* BADGES */
.alert-badge{display:inline-block;padding:8px 20px;border-radius:20px;font-size:1.05rem;font-weight:600;letter-spacing:0.04em;text-transform:uppercase;margin-top:8px;}
.badge-danger{background:#fde0e8;color:#a02040;border:1px solid #f08098;}
.badge-warning{background:#fef0d8;color:#a06000;border:1px solid #f4b060;}
.badge-safe{background:#d8f4e8;color:#186040;border:1px solid #70d0a0;}

/* GROUND TRUTH */
.ground-truth{background:rgba(248,244,232,0.7);border-radius:10px;padding:14px 18px;font-size:1.2rem;display:flex;justify-content:space-between;align-items:center;border:1px solid #e8dfc0;}
.gt-label{color:#1a1a1a;font-weight:500;font-size:1.2rem;}
.gt-correct{color:#186040;font-weight:600;font-size:1.2rem;}
.gt-wrong{color:#a02040;font-weight:600;font-size:1.2rem;}
.gt-unknown{color:#555555;font-style:italic;font-size:1.2rem;}

/* FEATURE ROW */
.feat-section-title{font-size:1.05rem;font-weight:700;color:#6b5510;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:8px;}
.feature-row{display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid #e8dfc0;font-size:1.05rem;gap:8px;}
.feature-name{color:#1a1a1a;font-size:1.05rem;font-weight:600;flex:1;}
.feature-desc{color:#3d3d3d;font-size:0.95rem;display:block;}
.feature-bar-wrap{width:70px;background:#e8dfc0;border-radius:4px;height:5px;flex-shrink:0;}
.feature-bar{height:5px;border-radius:4px;background:#d4a017;}
.feature-value{color:#1a1a1a;font-weight:600;font-family:'Space Grotesk',monospace;font-size:1.1rem;flex-shrink:0;}

/* WEATHER PANEL */
.weather-panel{width:100%;height:100px;border-radius:14px;overflow:hidden;margin-bottom:14px;position:relative;}

/* SUMMARY BOX */
.summary-box{background:rgba(255,250,235,0.40) !important;backdrop-filter:blur(20px) saturate(180%) !important;-webkit-backdrop-filter:blur(20px) saturate(180%) !important;border-radius:14px;padding:18px 22px;border:1.5px solid rgba(232,223,192,0.8);margin-top:16px;box-shadow:0 8px 32px rgba(180,130,20,0.14),0 2px 8px rgba(180,130,20,0.08) !important;}
.summary-title{font-size:1.15rem;font-weight:700;color:#6b5510;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:12px;}
.sum-table{width:100%;border-collapse:collapse;font-size:1.15rem;}
.sum-table th{padding:9px 13px;text-align:left;color:#1a1a1a;font-weight:700;font-size:1.15rem;background:rgba(245,238,216,0.8);border-bottom:2px solid #e8dfc0;}
.sum-table td{padding:8px 13px;border-bottom:1px solid #f0e8c8;color:#1a1a1a;font-size:1.15rem;}
.sum-table td:last-child{color:#1a1a1a;font-size:1.15rem;font-weight:600;}
.sum-table tr:last-child td{border-bottom:none;}
.sum-dot{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:7px;vertical-align:middle;}
.sum-stat{text-align:center;}
.sum-num{font-family:'Space Grotesk',sans-serif;font-size:2.4rem;font-weight:700;}
.sum-lbl{font-size:1.15rem;color:#1a1a1a;margin-top:2px;font-weight:600;}
.summary-lbl{font-size:1.15rem;font-weight:600;color:#1a1a1a;}
.sum-grid{display:flex;gap:24px;margin-bottom:16px;}

/* MAP BORDER */
.map-border-wrap{border:2px solid #f0d890;border-radius:16px;overflow:hidden;padding:0;backdrop-filter:blur(4px);-webkit-backdrop-filter:blur(4px);box-shadow:0 8px 32px rgba(200,160,40,0.12);}

/* CALENDAR */
[data-baseweb="calendar"]{font-family:'Inter',sans-serif !important;}
[data-baseweb="calendar"] [data-testid="month-header"]{font-size:0.85rem !important;}

/* DATE INPUT */
div[data-testid="stDateInput"] input{background:#fdf8f0 !important;border:1.5px solid #e0c890 !important;color:#1a1a1a !important;border-radius:10px !important;}

/* ===== RADIO BUTTON — 1 BLOCK DUY NHẤT ===== */
div[data-testid="stRadio"] label {
    background:#fffdf5 !important;
    border:2px solid #d4a017 !important;
    border-radius:20px !important;
    padding:8px 20px !important;
    margin-right:8px !important;
    cursor:pointer !important;
}
div[data-testid="stRadio"] label * {
    color:#1a1a1a !important;
    font-weight:700 !important;
    font-size:1.15rem !important;
    opacity:1 !important;
}
div[data-testid="stRadio"] label:has(input:checked) {
    background:#d4a017 !important;
    border-color:#d4a017 !important;
}
div[data-testid="stRadio"] label:has(input:checked) * {
    color:#ffffff !important;
}
div[data-testid="stRadio"] label:hover:not(:has(input:checked)) {
    background:#fff0b0 !important;
}
div[data-testid="stRadio"] > div {
    display:flex !important;
    flex-direction:row !important;
    gap:8px !important;
    flex-wrap:wrap !important;
}
div[data-testid="stRadio"] input { display:none !important; }

/* ===== SELECTBOX — 1 BLOCK DUY NHẤT ===== */
div[data-testid="stSelectbox"] > div > div {
    background:#fffdf5 !important;
    border:2px solid #e0c890 !important;
    border-radius:10px !important;
}
div[data-testid="stSelectbox"] * {
    color:#1a1a1a !important;
    font-size:1.15rem !important;
}
div[data-baseweb="select"] > div {
    background:#fffdf5 !important;
    color:#1a1a1a !important;
}
ul[data-testid="stSelectboxVirtualDropdown"],
div[data-baseweb="popover"],
div[data-baseweb="menu"] {
    background:#fffdf5 !important;
    border:1px solid #e8dfc0 !important;
}
ul[data-testid="stSelectboxVirtualDropdown"] li,
div[data-baseweb="popover"] li,
div[data-baseweb="menu"] li {
    color:#1a1a1a !important;
    font-size:1.15rem !important;
    background:#fffdf5 !important;
}
ul[data-testid="stSelectboxVirtualDropdown"] li:hover,
div[data-baseweb="popover"] li:hover,
div[data-baseweb="menu"] li:hover {
    background:#fff0c0 !important;
}
</style>
""", unsafe_allow_html=True)

STATION_INFO = {
    "48820099999": {"name":"Nội Bài",     "province":"Hà Nội",         "region":"Bắc",   "lat":21.221192,"lon":105.807178},
    "48823099999": {"name":"Nam Định",     "province":"Nam Định",        "region":"Bắc",   "lat":20.433333,"lon":106.150000},
    "48826099999": {"name":"Phù Liễn",     "province":"Hải Phòng",       "region":"Bắc",   "lat":20.800000,"lon":106.633333},
    "48831099999": {"name":"Thái Nguyên",  "province":"Thái Nguyên",     "region":"Bắc",   "lat":21.600000,"lon":105.833333},
    "48840099999": {"name":"Thanh Hoá",    "province":"Thanh Hoá",       "region":"Trung", "lat":19.750000,"lon":105.783333},
    "48845099999": {"name":"Vinh",         "province":"Nghệ An",         "region":"Trung", "lat":18.736725,"lon":105.670881},
    "48848099999": {"name":"Đồng Hới",     "province":"Quảng Bình",      "region":"Trung", "lat":17.483333,"lon":106.600000},
    "48852099999": {"name":"Phú Bài",      "province":"Thừa Thiên Huế", "region":"Trung", "lat":16.401500,"lon":107.702614},
    "48863099999": {"name":"Quảng Ngãi",   "province":"Quảng Ngãi",      "region":"Trung", "lat":15.133333,"lon":108.783333},
    "48866099999": {"name":"Pleiku",       "province":"Gia Lai",         "region":"Trung", "lat":14.004522,"lon":108.017158},
    "48870099999": {"name":"Quy Nhơn",     "province":"Bình Định",       "region":"Trung", "lat":13.766667,"lon":109.216667},
    "48894099999": {"name":"Nhà Bè",       "province":"TP. Hồ Chí Minh","region":"Nam",   "lat":10.650000,"lon":106.716667},
    "48900099999": {"name":"Tân Sơn Nhất", "province":"TP. Hồ Chí Minh","region":"Nam",   "lat":10.818797,"lon":106.651856},
    "48907099999": {"name":"Rạch Giá",     "province":"Kiên Giang",      "region":"Nam",   "lat":10.000000,"lon":105.083333},
    "48914099999": {"name":"Cà Mau",       "province":"Cà Mau",          "region":"Nam",   "lat": 9.183333,"lon":105.150000},
}

FEATURE_COLS = joblib.load("model_catboost.pkl").feature_names_

FEATURE_META = {
    'prcp_gsod_mm_lag1':("Lượng mưa trạm hôm qua (mm)","Mưa thực đo ngày t-1 — tín hiệu trực tiếp nhất"),
    'prcp_gsod_mm_lag2':("Lượng mưa trạm 2 ngày trước (mm)","Mưa thực đo ngày t-2"),
    'prcp_gsod_mm_lag3':("Lượng mưa trạm 3 ngày trước (mm)","Mưa thực đo ngày t-3"),
    'prcp_gsod_mm_lag7':("Lượng mưa trạm 7 ngày trước (mm)","Mưa thực đo ngày t-7"),
    'prcp_gsod_mm_roll3_sum':("Tổng mưa trạm 3 ngày (mm)","Lượng mưa tích lũy ngắn hạn"),
    'prcp_gsod_mm_roll7_sum':("Tổng mưa trạm 7 ngày (mm)","Lượng mưa tích lũy 1 tuần"),
    'prcp_gsod_mm_roll14_sum':("Tổng mưa trạm 14 ngày (mm)","Lượng mưa tích lũy 2 tuần"),
    'prcp_gsod_mm_roll30_sum':("Tổng mưa trạm 30 ngày (mm)","Lượng mưa tích lũy 1 tháng"),
    'precipitation_sum_lag1':("Mưa Open-Meteo hôm qua (mm)","Dự báo số trị từ Open-Meteo ngày t-1"),
    'precipitation_sum_lag3':("Mưa Open-Meteo 3 ngày trước","Dự báo số trị từ Open-Meteo ngày t-3"),
    'precipitation_sum_lag7':("Mưa Open-Meteo 7 ngày trước","Dự báo số trị từ Open-Meteo ngày t-7"),
    'precipitation_sum_roll3_sum':("Tổng mưa OM 3 ngày (mm)","Mưa Open-Meteo tích lũy 3 ngày"),
    'precipitation_sum_roll7_sum':("Tổng mưa OM 7 ngày (mm)","Mưa Open-Meteo tích lũy 1 tuần"),
    'precipitation_sum_roll14_sum':("Tổng mưa OM 14 ngày (mm)","Mưa Open-Meteo tích lũy 2 tuần"),
    'relative_humidity_2m_mean_lag1':("Độ ẩm không khí hôm qua (%)","Độ ẩm tương đối 2m — cao→dễ mưa"),
    'relative_humidity_2m_mean_lag3':("Độ ẩm không khí 3 ngày trước (%)","Độ ẩm tương đối 2m ngày t-3"),
    'relative_humidity_2m_mean_roll3_mean':("Độ ẩm TB 3 ngày (%)","Trung bình độ ẩm 3 ngày gần nhất"),
    'relative_humidity_2m_mean_roll7_mean':("Độ ẩm TB 7 ngày (%)","Trung bình độ ẩm 1 tuần"),
    'dew_point_2m_mean_lag1':("Điểm sương hôm qua (°C)","Gần nhiệt độ→không khí bão hòa hơi nước"),
    'pressure_msl_mean_lag1':("Áp suất khí quyển hôm qua (hPa)","Giảm mạnh→hệ thống thấp áp, dễ mưa lớn"),
    'pressure_msl_mean_roll7_std':("Biến động áp suất 7 ngày","Dao động lớn→thời tiết không ổn định"),
    'cloud_cover_mean_lag1':("Mây che phủ hôm qua (%)","100%→trời mây dày, tiền đề mưa"),
    'cloud_cover_mean_roll3_mean':("Mây che phủ TB 3 ngày (%)","Mây liên tục→tích tụ ẩm"),
    'cloud_cover_mean_roll7_mean':("Mây che phủ TB 7 ngày (%)","Xu hướng mây che phủ 1 tuần"),
    'temperature_2m_mean_lag1':("Nhiệt độ TB hôm qua (°C)","Nhiệt độ không khí 2m ngày t-1"),
    'temperature_2m_min_lag1':("Nhiệt độ tối thấp hôm qua (°C)","Đêm mát→ngưng tụ hơi nước nhiều hơn"),
    'temperature_2m_mean_roll7_std':("Biến động nhiệt độ 7 ngày","Dao động lớn→front lạnh/nóng đang hoạt động"),
    'soil_moisture_0_to_7cm_mean_roll7_mean':("Độ ẩm đất mặt TB 7 ngày","Đất bão hòa→mưa thêm dễ gây ngập/lũ"),
    'wind_gusts_10m_max_roll3_max':("Gió giật tối đa 3 ngày (km/h)","Gió mạnh→đối lưu mạnh, dễ mưa giông"),
    'wet_spell_length':("Số ngày mưa liên tiếp trước đó","Chuỗi mưa dài→đất bão hòa, tăng rủi ro lũ"),
    'coast_distance_km':("Khoảng cách đến bờ biển (km)","Gần biển→hơi ẩm dồi dào hơn"),
    'enso_mei_current':("Chỉ số ENSO hiện tại","Dương=El Niño (khô), Âm=La Niña (ẩm/mưa)"),
    'enso_mei_3m_lag':("Chỉ số ENSO 3 tháng trước","ENSO có độ trễ ảnh hưởng mưa ~3 tháng"),
    'enso_phase':("Pha ENSO","el_nino / la_nina / neutral"),
    'is_monsoon':("Mùa gió mùa","1=đang trong mùa gió mùa hoạt động"),
    'day_of_year':("Ngày thứ trong năm","Tháng 9–11 là cao điểm lũ miền Trung"),
    'year':("Năm",""),
    'month_sin':("Mùa vụ (sin)","Mã hóa tuần hoàn tháng trong năm"),
    'month_cos':("Mùa vụ (cos)","Mã hóa tuần hoàn tháng trong năm"),
    'doy_sin':("Chu kỳ ngày (sin)","Mã hóa tuần hoàn ngày trong năm"),
    'doy_cos':("Chu kỳ ngày (cos)","Mã hóa tuần hoàn ngày trong năm"),
    'koppen_Am':("Khí hậu nhiệt đới gió mùa","Köppen Am — mưa nhiều quanh năm"),
    'koppen_Aw':("Khí hậu nhiệt đới xavan","Köppen Aw — mùa khô rõ rệt"),
    'koppen_Cwa':("Khí hậu cận nhiệt đới","Köppen Cwa — mùa đông khô, hè nóng"),
    'STATION':("Mã trạm khí tượng",""),
    'LATITUDE':("Vĩ độ (°N)","Vị trí địa lý — ảnh hưởng đặc trưng khí hậu vùng"),
    'LONGITUDE':("Kinh độ (°E)","Vị trí địa lý"),
    'ELEVATION':("Độ cao (m)","Cao hơn→nhiệt độ thấp hơn, mưa địa hình"),
    'season_label_mua_kho_bac':("Mùa khô miền Bắc","1=đang trong mùa khô miền Bắc"),
    'season_label_mua_kho_nam':("Mùa khô miền Nam","1=đang trong mùa khô miền Nam"),
    'season_label_mua_kho_trung':("Mùa khô miền Trung","1=đang trong mùa khô miền Trung"),
    'season_label_mua_mua_bac':("Mùa mưa miền Bắc","1=đang trong mùa mưa miền Bắc"),
    'season_label_mua_mua_nam':("Mùa mưa miền Nam","1=đang trong mùa mưa miền Nam"),
    'season_label_mua_mua_trung':("Mùa mưa miền Trung","1=đang trong mùa mưa miền Trung"),
}

THRESHOLD = 0.54

@st.cache_resource
def load_model():
    return joblib.load("model_catboost.pkl")

@st.cache_resource
def load_province_geojson():
    try:
        url = "https://geodata.ucdavis.edu/gadm/gadm4.1/json/gadm41_VNM_1.json"
        with urllib.request.urlopen(url, timeout=15) as r:
            return _json.load(r)
    except:
        return None

@st.cache_data
def load_data():
    df = pd.read_csv("test_final.csv")
    df['DATE'] = pd.to_datetime(df['DATE'])
    df = df.sort_values(['STATION','DATE']).reset_index(drop=True)
    if 'wet_spell_length' not in df.columns:
        rain = df['prcp_gsod_mm_lag1'].fillna(0).gt(0.1)
        not_rain_cs = (~rain).groupby(df['STATION']).cumsum()
        df['wet_spell_length'] = rain.groupby([df['STATION'],not_rain_cs]).cumsum().astype(int)
    return df

@st.cache_data
def get_predictions_for_date(date_str):
    df = load_data()
    model = load_model()
    day_df = df[df['DATE']==date_str].copy()
    if day_df.empty: return {}
    results = {}
    for _,row in day_df.iterrows():
        sid = str(int(row['STATION']))
        try:
            X = row[FEATURE_COLS].to_frame().T
            prob = float(model.predict_proba(X)[0][1])
        except: prob = 0.0
        results[sid] = {
            'prob': prob,
            'rain_binary': row.get('rain_binary', np.nan),
            'target_reliable': bool(row.get('target_reliable', False)),
            'row': row
        }
    return results

def get_level(prob):
    if prob >= THRESHOLD: return "danger"
    if prob >= 0.30: return "warning"
    return "safe"

def get_color(prob):
    return {"danger":"#d03050","warning":"#d08000","safe":"#207050"}[get_level(prob)]

def get_map_color(prob):
    return {"danger":"#e83060","warning":"#f09020","safe":"#30c070"}[get_level(prob)]

# Weather animation HTML
def weather_html(level):
    if level == "danger":
        bg = "linear-gradient(180deg,#6080a0 0%,#405878 100%)"
        label = "⛈️&nbsp; MƯA LỚN — NGUY HIỂM"
        label_color = "rgba(255,230,240,0.95)"
        script = """
var drops=[];for(var i=0;i<90;i++)drops.push({x:Math.random()*W,y:Math.random()*H,s:Math.random()*1.5+0.8,sp:Math.random()*5+7,op:Math.random()*0.6+0.3,len:Math.random()*10+8});
function draw(){ctx.clearRect(0,0,W,H);drops.forEach(function(d){ctx.strokeStyle='rgba(180,215,255,'+d.op+')';ctx.lineWidth=d.s*0.6;ctx.beginPath();ctx.moveTo(d.x,d.y);ctx.lineTo(d.x+d.len*0.4,d.y+d.len);ctx.stroke();d.y+=d.sp;d.x+=d.sp*0.3;if(d.y>H){d.y=-d.len;d.x=Math.random()*W;}});requestAnimationFrame(draw);}
"""
    elif level == "warning":
        bg = "linear-gradient(180deg,#b0a080 0%,#907858 100%)"
        label = "🌦️&nbsp; MƯA VỪA — CẢNH BÁO"
        label_color = "rgba(255,240,200,0.95)"
        script = """
var drops=[];for(var i=0;i<40;i++)drops.push({x:Math.random()*W,y:Math.random()*H,s:Math.random()*1.2+0.6,sp:Math.random()*3+4,op:Math.random()*0.4+0.2,len:Math.random()*7+5});
function draw(){ctx.clearRect(0,0,W,H);drops.forEach(function(d){ctx.strokeStyle='rgba(200,220,255,'+d.op+')';ctx.lineWidth=d.s*0.5;ctx.beginPath();ctx.moveTo(d.x,d.y);ctx.lineTo(d.x+d.len*0.3,d.y+d.len);ctx.stroke();d.y+=d.sp;d.x+=d.sp*0.2;if(d.y>H){d.y=-d.len;d.x=Math.random()*W;}});requestAnimationFrame(draw);}
"""
    else:
        bg = "linear-gradient(180deg,#60b0e8 0%,#f0c840 100%)"
        label = "☀️&nbsp; TRỜI NẮNG — AN TOÀN"
        label_color = "rgba(80,40,0,0.9)"
        script = """
var angle=0;
function draw(){ctx.clearRect(0,0,W,H);var cx=60,cy=H/2,r=24;ctx.save();ctx.translate(cx,cy);ctx.rotate(angle);for(var i=0;i<12;i++){var a=i*Math.PI/6;ctx.strokeStyle='rgba(255,210,0,0.7)';ctx.lineWidth=2.5;ctx.beginPath();ctx.moveTo(Math.cos(a)*(r+6),Math.sin(a)*(r+6));ctx.lineTo(Math.cos(a)*(r+18),Math.sin(a)*(r+18));ctx.stroke();}ctx.restore();var g=ctx.createRadialGradient(cx,cy,0,cx,cy,r);g.addColorStop(0,'rgba(255,240,100,0.95)');g.addColorStop(1,'rgba(255,190,0,0.8)');ctx.fillStyle=g;ctx.beginPath();ctx.arc(cx,cy,r,0,Math.PI*2);ctx.fill();angle+=0.01;requestAnimationFrame(draw);}
"""
    uid = f"wc_{level}"
    return f"""<!DOCTYPE html><html><head>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@700&display=swap" rel="stylesheet">
<style>*{{margin:0;padding:0;box-sizing:border-box;}}</style>
</head><body style="margin:0;padding:0;overflow:hidden;">
<div style="width:100%;height:100px;border-radius:14px;overflow:hidden;position:relative;background:{bg};">
  <canvas id="{uid}" style="position:absolute;inset:0;width:100%;height:100%;"></canvas>
  <div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-family:'Space Grotesk',sans-serif;font-size:1.3rem;font-weight:700;color:{label_color};letter-spacing:0.05em;text-shadow:0 2px 6px rgba(0,0,0,0.3);">{label}</div>
</div>
<script>(function(){{var c=document.getElementById('{uid}');if(!c)return;var ctx=c.getContext('2d');var W=c.offsetWidth||400,H=100;c.width=W;c.height=H;{script}draw();}})();</script>
</body></html>"""

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
  <div>
    <div class="app-title">🌧️ StreamWave Rain</div>
    <div class="app-subtitle">Hệ thống dự báo mưa cực đoan · 15 trạm quan trắc · Việt Nam 2024</div>
  </div>
  <div class="app-meta">Mô hình: CatBoost · Ngưỡng cảnh báo: 54% · AUC-PR: 0.336<br>Dữ liệu: GSOD + Open-Meteo · Tập kiểm tra: 2024</div>
</div>""", unsafe_allow_html=True)

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

VIETNAMESE_MONTHS = ["Tháng 1","Tháng 2","Tháng 3","Tháng 4","Tháng 5","Tháng 6",
                     "Tháng 7","Tháng 8","Tháng 9","Tháng 10","Tháng 11","Tháng 12"]

col_date, col_info = st.columns([4,6])
with col_date:
    c1, c2, c3 = st.columns([1, 1.4, 1])
    with c1:
        sel_day = st.selectbox("Ngày", options=list(range(1,32)),
            index=20, label_visibility="collapsed", key="day_sel")
    with c2:
        sel_month_idx = st.selectbox("Tháng", options=list(range(12)),
            index=8, format_func=lambda x: VIETNAMESE_MONTHS[x],
            label_visibility="collapsed", key="month_sel")
    with c3:
        sel_year = st.selectbox("Năm", options=[2024],
            index=0, label_visibility="collapsed", key="year_sel")
    try:
        selected_date = date(sel_year, sel_month_idx + 1, sel_day)
        if selected_date < date(2024, 1, 8):  selected_date = date(2024, 1, 8)
        if selected_date > date(2024, 12, 31): selected_date = date(2024, 12, 31)
    except ValueError:
        selected_date = date(2024, 9, 21)
with col_info:
    st.markdown(f"<div style='padding:9px 4px;font-size:0.95rem;color:#6b5510;'>08/01/2024 – 31/12/2024 &nbsp;·&nbsp; <b style='color:#c0306a;'>Đang xem: {selected_date.strftime('%d/%m/%Y')}</b></div>", unsafe_allow_html=True)

st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

date_str = selected_date.strftime('%Y-%m-%d')
with st.spinner("Đang tính toán dự báo..."):
    predictions = get_predictions_for_date(date_str)

if 'sel_sid' not in st.session_state:
    st.session_state.sel_sid = "48852099999"

# ── MAP + PANEL ───────────────────────────────────────────────────────────────
map_col, panel_col = st.columns([6,4], gap="small")

with map_col:
    region_tab = st.radio("Vùng", ["Tất cả","Miền Bắc","Miền Trung","Miền Nam"],
        horizontal=True, label_visibility="collapsed", key="rr")
    zoom_lf = {"Tất cả":(16.0,107.5,5),"Miền Bắc":(21.0,106.0,7),"Miền Trung":(16.0,107.5,6),"Miền Nam":(10.5,106.0,7)}[region_tab]
    rf = {"Tất cả":["Bắc","Trung","Nam"],"Miền Bắc":["Bắc"],"Miền Trung":["Trung"],"Miền Nam":["Nam"]}[region_tab]

    # ── XÂY DỰNG FOLIUM MAP ──────────────────────────────────────────
    m = folium.Map(
        location=[zoom_lf[0], zoom_lf[1]],
        zoom_start=zoom_lf[2],
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}",
        attr="Tiles © Esri",
        control_scale=False,
        zoom_control=True,
    )

    # CSS animation cho mưa/nắng — inject 1 lần vào map root
    ANIM_CSS = """
    <style>
    @keyframes rain-fall {
      0%  { transform: translateY(-10px) scaleY(0.5); opacity:0.9; }
      100%{ transform: translateY(28px)  scaleY(1.2); opacity:0;   }
    }
    @keyframes sun-pulse {
      0%,100%{ box-shadow:0 0 4px 2px rgba(255,220,0,0.5); }
      50%    { box-shadow:0 0 10px 5px rgba(255,220,0,0.2); }
    }
    @keyframes sel-ring {
      0%  { transform:scale(1);   opacity:0.7; }
      100%{ transform:scale(2.2); opacity:0;   }
    }
    .rain-drop{ position:absolute; width:2px; border-radius:2px;
                background:rgba(100,160,255,0.75);
                animation: rain-fall linear infinite; }
    .sun-dot  { position:absolute; border-radius:50%;
                background:rgba(255,215,0,0.85);
                animation: sun-pulse 2s ease-in-out infinite; }
    .sel-ring { position:absolute; border-radius:50%; border:2px solid currentColor;
                animation: sel-ring 1.4s ease-out infinite; }
    </style>
    """
    m.get_root().html.add_child(folium.Element(ANIM_CSS))

    # Province highlight
    province_geojson = load_province_geojson()
    if province_geojson:
        sel_prov_key = STATION_INFO[st.session_state.sel_sid]['province'].replace(' ', '')
        prob_sel_p = predictions.get(st.session_state.sel_sid, {}).get('prob', 0.0)
        lv_sel_p = get_level(prob_sel_p)
        prov_fill = {"danger":"#dc3232","warning":"#dc9000","safe":"#30b870"}[lv_sel_p]

        def make_style(key, fill):
            def _s(feat):
                if feat['properties']['NAME_1'] == key:
                    return {'fillColor':fill,'fillOpacity':0.22,'color':'#966050','weight':1.5}
                return {'fillColor':'transparent','fillOpacity':0,'color':'transparent','weight':0}
            return _s

        folium.GeoJson(
            province_geojson,
            style_function=make_style(sel_prov_key, prov_fill),
            name='provinces',
        ).add_to(m)

    # Markers mỗi trạm
    for sid, info in STATION_INFO.items():
        if info['region'] not in rf: continue
        pred  = predictions.get(sid, {})
        prob  = pred.get('prob', 0.0)
        lv    = get_level(prob)
        is_sel = (sid == st.session_state.sel_sid)
        c_map = {"danger":"#e83060","warning":"#f09020","safe":"#30c070"}
        fill_c = c_map[lv]
        radius = 11 if is_sel else 7
        tip_icon = "🔴" if lv=="danger" else "🟡" if lv=="warning" else "🟢"

        # Vòng tròn chính
        folium.CircleMarker(
            location=[info['lat'], info['lon']],
            radius=radius,
            color='white', weight=2 if is_sel else 1,
            fill=True, fill_color=fill_c, fill_opacity=0.92,
            tooltip=folium.Tooltip(
                f"<b style='font-size:13px'>{info['name']}</b><br>"
                f"<span style='color:#3d3d3d'>{info['province']}</span><br>"
                f"Xác suất: <b style='color:{fill_c}'>{prob*100:.1f}%</b> {tip_icon}",
                sticky=True
            ),
        ).add_to(m)

        # Pulse ring cho trạm đang chọn
        if is_sel:
            ring_html = (
                f'<div style="width:32px;height:32px;transform:translate(-16px,-16px);position:relative;">'
                f'<div class="sel-ring" style="inset:0;color:{fill_c};"></div>'
                f'</div>'
            )
            folium.Marker(
                location=[info['lat'], info['lon']],
                icon=folium.DivIcon(html=ring_html, icon_size=(0,0), icon_anchor=(0,0)),
            ).add_to(m)

        # Rain animation — danger/warning
        if lv in ("danger", "warning"):
            n_drops = 10 if lv == "danger" else 5
            drops_html = ""
            for i in range(n_drops):
                lft   = 3 + (i * 5) % 44
                dly   = round((i * 0.13) % 1.0, 2)
                dur   = round(0.55 if lv=="danger" else 0.85, 2)
                h_px  = 9 + (i % 3) * 3
                drops_html += (
                    f'<div class="rain-drop" style="left:{lft}px;height:{h_px}px;'
                    f'animation-duration:{dur}s;animation-delay:{dly}s;"></div>'
                )
            rain_div = (
                f'<div style="position:relative;width:50px;height:36px;'
                f'transform:translate(-25px,-42px);pointer-events:none;">'
                f'{drops_html}</div>'
            )
            folium.Marker(
                location=[info['lat'], info['lon']],
                icon=folium.DivIcon(html=rain_div, icon_size=(0,0), icon_anchor=(0,0)),
            ).add_to(m)

        # Sun animation — safe
        else:
            sun_div = (
                '<div style="width:12px;height:12px;transform:translate(-6px,-6px);'
                'pointer-events:none;">'
                '<div class="sun-dot" style="inset:0;width:12px;height:12px;"></div>'
                '</div>'
            )
            folium.Marker(
                location=[info['lat'], info['lon']],
                icon=folium.DivIcon(html=sun_div, icon_size=(0,0), icon_anchor=(0,0)),
            ).add_to(m)

        # Tên trạm
        folium.Marker(
            location=[info['lat'], info['lon']],
            icon=folium.DivIcon(
                html=f'<div style="font-family:Inter,sans-serif;font-size:9px;'
                     f'color:#4a2030;white-space:nowrap;'
                     f'transform:translate(14px,-5px);pointer-events:none;">'
                     f'{info["name"]}</div>',
                icon_size=(90,14), icon_anchor=(0,7),
            ),
        ).add_to(m)

    # ── HOÀNG SA & TRƯỜNG SA (bắt buộc — chủ quyền lãnh thổ) ──────────
    for ilabel, ilat, ilon, ipopup in [
        ("Hoàng Sa", 16.5, 112.0, "Quần đảo Hoàng Sa — Việt Nam"),
        ("Trường Sa",  8.8, 111.9, "Quần đảo Trường Sa — Việt Nam"),
    ]:
        # Vòng tròn đánh dấu vị trí quần đảo
        folium.CircleMarker(
            location=[ilat, ilon],
            radius=7,
            color="#c0306a", weight=2,
            fill=True, fill_color="#e8306a", fill_opacity=0.5,
            tooltip=folium.Tooltip(
                f"<b style='color:#c0306a'>{ilabel}</b><br>"
                f"<span style='font-size:11px;color:#555'>{ipopup}</span>",
                sticky=True,
            ),
            popup=folium.Popup(ipopup, max_width=220),
        ).add_to(m)
        # Nhãn text nổi bật bên cạnh
        folium.Marker(
            location=[ilat, ilon],
            icon=folium.DivIcon(
                html=(
                    f'<div style="font-family:Inter,sans-serif;font-size:11px;font-weight:700;'
                    f'color:#c0306a;white-space:nowrap;'
                    f'background:rgba(255,255,255,0.90);padding:2px 7px;'
                    f'border-radius:8px;border:1.5px solid #f0a0c8;'
                    f'box-shadow:0 2px 6px rgba(200,80,120,0.18);'
                    f'transform:translate(12px,-8px);">'
                    f'🇻🇳 {ilabel}</div>'
                ),
                icon_size=(100, 22),
                icon_anchor=(0, 11),
            ),
        ).add_to(m)

    # Render
    st.markdown('<div class="map-border-wrap">', unsafe_allow_html=True)
    map_result = st_folium(m, height=540, use_container_width=True,
                           key=f"fmap_{region_tab}",
                           returned_objects=["last_object_clicked"])
    st.markdown('</div>', unsafe_allow_html=True)

    # Xử lý click
    if map_result:
        clicked = map_result.get('last_object_clicked')
        if clicked:
            clat = clicked.get('lat')
            clng = clicked.get('lng')
            if clat is not None and clng is not None:
                candidates = [(sid, info) for sid, info in STATION_INFO.items()
                              if info['region'] in rf]
                if candidates:
                    new_sid = min(candidates,
                        key=lambda x: (x[1]['lat']-clat)**2 + (x[1]['lon']-clng)**2
                    )[0]
                    if new_sid != st.session_state.sel_sid:
                        st.session_state.sel_sid = new_sid
                        st.rerun()

    st.markdown("""<div style='display:flex;gap:18px;padding:7px 4px;font-size:1.15rem;color:#1a1a1a;font-weight:500;'>
        <span><span style='color:#e83060;'>●</span> Nguy hiểm (≥54%)</span>
        <span><span style='color:#f09020;'>●</span> Cảnh báo (30–54%)</span>
        <span><span style='color:#30c070;'>●</span> An toàn (&lt;30%)</span>
        <span style='margin-left:auto;color:#6b5510;'>Bấm vào trạm để xem chi tiết</span>
    </div>""", unsafe_allow_html=True)
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    active = {sid:f"{info['name']} · {info['province']}" for sid,info in STATION_INFO.items() if info['region'] in rf}
    sel_keys = list(active.keys())
    cur_idx = sel_keys.index(st.session_state.sel_sid) if st.session_state.sel_sid in sel_keys else 0
    chosen = st.selectbox("Chọn trạm:",options=sel_keys,format_func=lambda x:active[x],index=cur_idx,key="ss2")
    if chosen != st.session_state.sel_sid:
        st.session_state.sel_sid = chosen; st.rerun()

with panel_col:
    sid = st.session_state.sel_sid
    info = STATION_INFO[sid]
    pred = predictions.get(sid,{})
    prob = pred.get('prob',0.0)
    rain_binary = pred.get('rain_binary',np.nan)
    target_reliable = pred.get('target_reliable',False)
    level = get_level(prob)
    row_data = pred.get('row',None)

    components.html(weather_html(level), height=110)

    badge_text = "⚠️ NGUY HIỂM — MƯA CỰC ĐOAN" if level=="danger" else "⚡ CẢNH BÁO — MƯA VỪA" if level=="warning" else "✅ AN TOÀN"
    st.markdown(f"""<div class="risk-card {level}">
        <div class="station-name">{info['name']}</div>
        <div class="station-province">📍 {info['province']} &nbsp;·&nbsp; {selected_date.strftime('%d/%m/%Y')}</div>
        <div class="prob-{level} prob-number">{prob*100:.1f}<span style='font-size:1.4rem;'>%</span></div>
        <div style='color:#3d3d3d;font-size:0.92rem;margin-bottom:8px;'>xác suất mưa cực đoan (ngưỡng: 54%)</div>
        <span class="alert-badge badge-{level}">{badge_text}</span>
    </div>""", unsafe_allow_html=True)

    if target_reliable and not (isinstance(rain_binary,float) and np.isnan(rain_binary)):
        actual = int(float(rain_binary))
        predicted = 1 if prob>=THRESHOLD else 0
        is_correct = (actual==predicted)
        actual_text = "🌧️ Thực tế: Có mưa cực đoan" if actual==1 else "☀️ Thực tế: Không mưa"
        st.markdown(f"""<div class="ground-truth">
            <span class="gt-label">{actual_text}</span>
            <span class="{'gt-correct' if is_correct else 'gt-wrong'}">{'✓ Dự báo đúng' if is_correct else '✗ Dự báo sai'}</span>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""<div class="ground-truth"><span class="gt-label">Nhãn thực tế</span><span class="gt-unknown">Không đủ tin cậy</span></div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="feat-section-title">📊 Tín hiệu quan trọng nhất</div>', unsafe_allow_html=True)

    if row_data is not None:
        try:
            model = load_model()
            importances = model.get_feature_importance()
            feat_imp = dict(zip(FEATURE_COLS,importances))
            top_feats = sorted(feat_imp.items(),key=lambda x:x[1],reverse=True)[:10]
            max_imp = top_feats[0][1] if top_feats else 1
            html = '<div style="background:rgba(255,255,255,0.7);border-radius:10px;padding:10px 14px;border:1px solid #f0d8e4;">'
            for feat_name,imp in top_feats:
                meta = FEATURE_META.get(feat_name,(feat_name,""))
                label,desc = meta
                try:
                    val = row_data[feat_name]
                    val_str = f"{float(val):.2f}" if not (isinstance(val,float) and np.isnan(val)) else "—"
                except: val_str = "—"
                bar_pct = int(imp/max_imp*100)
                html += f"""<div class="feature-row">
                    <div class="feature-name" style="flex:1;min-width:0;">
                        <span style="display:block;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" title="{label}">{label}</span>
                        {f'<span class="feature-desc">{desc}</span>' if desc else ''}
                    </div>
                    <div class="feature-bar-wrap"><div class="feature-bar" style="width:{bar_pct}%;"></div></div>
                    <span class="feature-value">{val_str}</span>
                </div>"""
            html += "</div>"
            st.markdown(html, unsafe_allow_html=True)
        except Exception as e:
            st.info(f"Không thể tải tín hiệu: {e}")

# ── BẢNG TỔNG QUAN DƯỚI MAP (full width) ────────────────────────────────────
if predictions:
    danger_list = sorted([(sid,STATION_INFO[sid]['name'],p.get('prob',0)) for sid,p in predictions.items() if get_level(p.get('prob',0))=="danger" and sid in STATION_INFO],key=lambda x:-x[2])
    warning_list= sorted([(sid,STATION_INFO[sid]['name'],p.get('prob',0)) for sid,p in predictions.items() if get_level(p.get('prob',0))=="warning" and sid in STATION_INFO],key=lambda x:-x[2])
    safe_list   = sorted([(sid,STATION_INFO[sid]['name'],p.get('prob',0)) for sid,p in predictions.items() if get_level(p.get('prob',0))=="safe" and sid in STATION_INFO],key=lambda x:-x[2])

    rows_html = ""
    for items,dot_color,lv_label in [(danger_list,"#e83060","Nguy hiểm"),(warning_list,"#f09020","Cảnh báo"),(safe_list,"#30c070","An toàn")]:
        for _,name,pv in items:
            rows_html += f"""<tr>
                <td style="padding:8px 14px;border-bottom:1px solid #f8e0ee;">
                    <span class="sum-dot" style="background:{dot_color};"></span>{name}
                </td>
                <td style="padding:8px 14px;text-align:right;font-weight:700;color:{dot_color};border-bottom:1px solid #f8e0ee;">{pv*100:.1f}%</td>
                <td style="padding:8px 14px;font-size:1.0rem;color:#1a1a1a;font-weight:600;border-bottom:1px solid #f8e0ee;">{lv_label}</td>
            </tr>"""

    st.markdown(f"""
    <div class="summary-box">
        <div class="summary-title">📋 Tổng quan toàn quốc ngày {selected_date.strftime('%d/%m/%Y')}</div>
        <div class="sum-grid">
            <div class="sum-stat"><div class="sum-num" style="color:#c03050;">{len(danger_list)}</div><div class="sum-lbl">Nguy hiểm</div></div>
            <div class="sum-stat"><div class="sum-num" style="color:#c07000;">{len(warning_list)}</div><div class="sum-lbl">Cảnh báo</div></div>
            <div class="sum-stat"><div class="sum-num" style="color:#207050;">{len(safe_list)}</div><div class="sum-lbl">An toàn</div></div>
            <div class="sum-stat"><div class="sum-num" style="color:#c0306a;">{len(predictions)}</div><div class="sum-lbl">Tổng trạm</div></div>
        </div>
        <table class="sum-table">
            <thead><tr><th>Trạm khí tượng</th><th style="text-align:right;">Xác suất mưa cực đoan</th><th>Mức độ</th></tr></thead>
            <tbody>{rows_html}</tbody>
        </table>
    </div>""", unsafe_allow_html=True)
