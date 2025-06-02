import streamlit as st
import pandas as pd
import plotly.graph_objs as go
import folium
from streamlit_folium import st_folium
from folium.features import DivIcon

# 📁 데이터 로드
df = pd.read_csv("subway_congestion.csv")
station_info = pd.read_csv("stationinfo_20250602.csv")

# ✅ 앱 상단 제목
st.markdown("""
    <h1 style='text-align: center; color: #1f77b4;'>🚇 서울 지하철 혼잡도 비교 대시보드</h1>
    <h4 style='text-align: center; color: gray;'>지하철 역별 1시간 단위 혼잡도를 시각화합니다.</h4>
    <hr>
""", unsafe_allow_html=True)

# ✅ 요일 선택
st.subheader("📅 요일 및 역 선택")
day_option = st.selectbox("요일을 선택하세요", ["평일", "토요일", "일요일"])
df_filtered = df[(df['요일구분'] == day_option) & (df['상하구분'] == '상선')]

# ✅ 사용자 선택 - 1호선~2호선 포함
st.subheader("🔵 첫 번째 역 선택")
line1_options = ["지하철 1~8호선 중 선택"] + sorted(df_filtered["호선"].unique()) + ["2호선"]
line1 = st.selectbox("1️⃣ 첫 번째 호선을 선택하세요", line1_options, key="line1")

station1_list = sorted(df_filtered[df_filtered["호선"] == line1]["출발역"].unique()) if line1 != "지하철 1~8호선 중 선택" else []
station1 = st.selectbox("📍 첫 번째 역을 선택하세요", ["역명 선택"] + station1_list, key="station1")

# ✅ 사용자 선택 - 2호선 포함
st.subheader("🟠 두 번째 역 선택")
line2_options = ["지하철 1~8호선 중 선택"] + sorted(df_filtered["호선"].unique()) + ["2호선"]
line2 = st.selectbox("2️⃣ 두 번째 호선을 선택하세요", line2_options, key="line2")

station2_list = sorted(df_filtered[df_filtered["호선"] == line2]["출발역"].unique()) if line2 != "지하철 1~8호선 중 선택" else []
station2 = st.selectbox("📍 두 번째 역을 선택하세요", ["역명 선택"] + station2_list, key="station2")

# ✅ 선택한 역이 있을 때만 데이터 가져오기
if station1 != "역명 선택" and station2 != "역명 선택":
    selected_stations = station_info[station_info["역사명"].isin([station1, station2])]
else:
    selected_stations = pd.DataFrame(columns=station_info.columns)  # 빈 데이터프레임 생성

# ✅ 선택한 역 지도 표시
st.markdown("---")
st.markdown("### 🗺️ 선택한 역의 지도 위치")

# 지도 초기화
center = [37.5665, 126.9780]  # 서울 중심
m = folium.Map(location=center, zoom_start=12)

# 마커 및 라벨 표시 함수
def add_marker_with_label(lat, lon, name, color, icon_name):
    folium.Marker(
        location=[lat, lon],
        tooltip=name,
        icon=folium.Icon(color=color, icon=icon_name)
    ).add_to(m)

    folium.map.Marker(
        [lat, lon],
        icon=DivIcon(
            icon_size=(200, 50),
            icon_anchor=(0, 0),
            html=f'<div style="font-size: 16pt; color: {color}; font-weight: bold;">{name}</div>',
        )
    ).add_to(m)

# 선택한 역이 있을 경우 지도에 마커 추가
if not selected_stations.empty:
    for _, row in selected_stations.iterrows():
        name = row["역사명"] + "역"
        lat = row["역위도"]
        lon = row["역경도"]
        color = "royalblue" if row["역사명"] == station1 else "darkorange"
        icon_name = "star" if row["역사명"] == station1 else "cloud"
        add_marker_with_label(lat, lon, name, color, icon_name)

# 지도 출력
st_folium(m, width=800, height=600)
