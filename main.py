import streamlit as st
import pandas as pd
import plotly.graph_objs as go
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
import time

# 📁 데이터 불러오기
df = pd.read_csv("subway_congestion.csv")

# ✅ 앱 제목
st.markdown("""
    <h1 style='text-align: center; color: #1f77b4;'>
        🚇 서울 지하철 혼잡도 비교 대시보드
    </h1>
    <h4 style='text-align: center; color: gray;'>
        지하철 호선과 역을 선택하여 혼잡도를 시각화하고 위치를 확인하세요!
    </h4>
    <hr>
""", unsafe_allow_html=True)

# ✅ 요일 선택
st.subheader("📅 요일 및 지하철 선택")
day_option = st.selectbox("요일을 선택하세요", ["평일", "토요일", "일요일"])

# ✅ 상행선만 필터링
df_filtered = df[(df['요일구분'] == day_option) & (df['상하구분'] == '상선')]

# ✅ 호선 선택
line_list = sorted(df_filtered['호선'].unique())
col1, col2 = st.columns(2)
with col1:
    line1 = st.selectbox("🔵 첫 번째 역 - 호선 선택", line_list)
with col2:
    line2 = st.selectbox("🟠 두 번째 역 - 호선 선택", line_list, index=1 if len(line_list) > 1 else 0)

# ✅ 해당 호선의 역만 필터링
station_list1 = sorted(df_filtered[df_filtered['호선'] == line1]['출발역'].unique())
station_list2 = sorted(df_filtered[df_filtered['호선'] == line2]['출발역'].unique())

with col1:
    station1 = st.selectbox("🔵 첫 번째 역 선택", station_list1)
with col2:
    station2 = st.selectbox("🟠 두 번째 역 선택", station_list2)

# ✅ 시간대 평균 계산
time_cols_30min = df.columns[6:]
time_pairs = [(time_cols_30min[i], time_cols_30min[i + 1]) for i in range(0, len(time_cols_30min)-1, 2)]
hour_labels = [col1[:col1.find('시') + 1] for col1, _ in time_pairs]

def get_hourly_avg(line, station_name):
    row = df_filtered[(df_filtered['호선'] == line) & (df_filtered['출발역'] == station_name)][time_cols_30min].mean()
    return [row[[col1, col2]].mean() for col1, col2 in time_pairs]

hourly_avg1 = get_hourly_avg(line1, station1)
hourly_avg2 = get_hourly_avg(line2, station2)

# ✅ 혼잡도 그래프
st.markdown("### 📊 혼잡도 비교 그래프")
fig = go.Figure()
fig.add_trace(go.Bar(x=hour_labels, y=hourly_avg1, name=f"{line1}호선 {station1}", marker_color='royalblue'))
fig.add_trace(go.Bar(x=hour_labels, y=hourly_avg2, name=f"{line2}호선 {station2}", marker_color='darkorange'))

fig.update_layout(
    barmode='group',
    title=f"🕐 시간대별 혼잡도 비교 ({day_option})",
    xaxis_title="시간대",
    yaxis_title="혼잡도 (%)",
    height=600
)
st.plotly_chart(fig)

# ✅ 지도 시각화
st.markdown("### 🗺️ 역 위치 지도")

station1_name = station1 + "역"
station2_name = station2 + "역"

geolocator = Nominatim(user_agent="subway_locator")

@st.cache_data(show_spinner=False)
def get_location(station_name):
    try:
        location = geolocator.geocode(station_name)
        time.sleep(1)  # 요청 간격 제한 대응
        return location
    except:
        return None

location1 = get_location(station1_name)
location2 = get_location(station2_name)

map_center = [37.5665, 126.9780]  # 서울 중심 기본값
if location1:
    map_center = [location1.latitude, location1.longitude]

m = folium.Map(location=map_center, zoom_start=12)

def add_marker(location, name, color):
    if location:
        folium.Marker(
            location=[location.latitude, location.longitude],
            popup=name,
            tooltip=name,
            icon=folium.Icon(color=color, icon="info-sign")
        ).add_to(m)
    else:
        st.warning(f"⚠️ '{name}'의 위치를 찾을 수 없습니다.")

add_marker(location1, station1_name, "blue")
add_marker(location2, station2_name, "orange")

st_folium(m, width=700, height=500)
