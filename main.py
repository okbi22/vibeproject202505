import streamlit as st
import pandas as pd
import plotly.graph_objs as go
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
import time

# 📁 데이터 로드
df = pd.read_csv("subway_congestion.csv")

# ✅ 앱 상단 제목 꾸미기
st.markdown("""
    <h1 style='text-align: center; color: #1f77b4;'>
        🚇 서울 지하철 혼잡도 비교 대시보드
    </h1>
    <h4 style='text-align: center; color: gray;'>
        지하철 역별 1시간 단위 혼잡도를 시각화하고 지도에서 위치를 확인해보세요!
    </h4>
    <hr>
""", unsafe_allow_html=True)

# ✅ 요일 및 역 선택
st.subheader("📅 요일 및 역 선택")
day_option = st.selectbox("요일을 선택하세요", ["평일", "토요일", "일요일"])
df_filtered = df[(df['요일구분'] == day_option) & (df['상하구분'] == '상선')]

station_list = sorted(df_filtered['출발역'].unique())
station1 = st.selectbox("🔵 첫 번째 역 선택", station_list)
station2 = st.selectbox("🟠 두 번째 역 선택", station_list, index=1)

# ✅ 시간대 컬럼 및 1시간 단위 평균 계산
time_cols_30min = df.columns[6:]
time_pairs = [(time_cols_30min[i], time_cols_30min[i + 1]) for i in range(0, len(time_cols_30min)-1, 2)]
hour_labels = [col1[:col1.find('시') + 1] for col1, _ in time_pairs]

def get_hourly_avg(station_name):
    row = df_filtered[df_filtered['출발역'] == station_name][time_cols_30min].mean()
    return [row[[col1, col2]].mean() for col1, col2 in time_pairs]

hourly_avg1 = get_hourly_avg(station1)
hourly_avg2 = get_hourly_avg(station2)

# ✅ 혼잡도 그래프 시각화
st.markdown("### 📊 혼잡도 비교 그래프")
fig = go.Figure()
fig.add_trace(go.Bar(x=hour_labels, y=hourly_avg1, name=station1, marker_color='royalblue'))
fig.add_trace(go.Bar(x=hour_labels, y=hourly_avg2, name=station2, marker_color='darkorange'))

fig.update_layout(
    barmode='group',
    title=f"🕐 1시간 단위 혼잡도 비교: {station1} vs {station2} ({day_option})",
    xaxis_title="시간대",
    yaxis_title="혼잡도 (%)",
    xaxis_tickangle=0,
    height=600
)
st.plotly_chart(fig)

# ✅ 데이터 설명
st.markdown(f"""
#### 🧾 데이터 설명  
서울교통공사 1-8호선 **30분 단위 평균 혼잡도** 데이터를 바탕으로,  
30분간 지나는 열차들의 혼잡도를 1시간 평균으로 변환해 비교합니다.  
- **정원 대비 승차 인원 비율**을 기준으로 하며,  
- 승객 수 = 좌석 수일 때 혼잡도는 **34%**입니다.

📌 현재 선택 요일: **{day_option}**
""")

# ✅ 지도 시각화 - 지오코딩 사용
st.markdown("---")
st.markdown("### 🗺️ 선택한 역의 지도 위치")

# "역"을 붙인 검색용 이름 생성
station1_name = station1 + "역"
station2_name = station2 + "역"

# 지오코딩 초기화
geolocator = Nominatim(user_agent="subway_locator")

# 위치 검색 함수
@st.cache_data(show_spinner=False)
def get_location(station_name):
    try:
        location = geolocator.geocode(station_name)
        time.sleep(1)  # 요청 간격 지연 (Nominatim 제한)
        return location
    except:
        return None

# 위치 가져오기
location1 = get_location(station1_name)
location2 = get_location(station2_name)

# 지도 중심 설정
map_center = [37.5665, 126.9780]  # 서울 시청 기본
if location1:
    map_center = [location1.latitude, location1.longitude]

# 지도 생성
m = folium.Map(location=map_center, zoom_start=12)

# 마커 추가 함수
def add_marker(location, name, color):
    if location:
        folium.Marker(
            location=[location.latitude, location.longitude],
            popup=name,
            tooltip="📍 " + name,
            icon=folium.Icon(color=color, icon="info-sign")
        ).add_to(m)
    else:
        st.warning(f"⚠️ '{name}'의 위치를 찾을 수 없습니다.")

# 마커 추가
add_marker(location1, station1_name, "blue")
add_marker(location2, station2_name, "orange")

# 지도 출력
st_folium(m, width=700, height=500)
