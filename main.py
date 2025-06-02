import streamlit as st
import pandas as pd
import plotly.graph_objs as go
import folium
from streamlit_folium import st_folium
from folium.features import DivIcon

# 📁 혼잡도 데이터 및 역 위치 데이터 로드
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

# ✅ 사용자 선택 - 역1
st.subheader("🔵 첫 번째 역 선택")
line1 = st.selectbox("1️⃣ 첫 번째 호선을 선택하세요", sorted(df_filtered["호선"].unique()), key="line1")
station1_list = sorted(df_filtered[df_filtered["호선"] == line1]["출발역"].unique())
station1 = st.selectbox("📍 첫 번째 역을 선택하세요", [""] + station1_list, key="station1")  # 초기값을 빈 값으로 설정

# ✅ 사용자 선택 - 역2
st.subheader("🟠 두 번째 역 선택")
line2 = st.selectbox("2️⃣ 두 번째 호선을 선택하세요", sorted(df_filtered["호선"].unique()), index=1, key="line2")
station2_list = sorted(df_filtered[df_filtered["호선"] == line2]["출발역"].unique())
station2 = st.selectbox("📍 두 번째 역을 선택하세요", [""] + station2_list, key="station2")  # 초기값을 빈 값으로 설정

# ✅ 시간대 평균 계산
time_cols_30min = df.columns[6:]
time_pairs = [(time_cols_30min[i], time_cols_30min[i + 1]) for i in range(0, len(time_cols_30min)-1, 2)]
hour_labels = [col1[:col1.find('시') + 1] for col1, _ in time_pairs]

def get_hourly_avg(line, station):
    if station == "":
        return [0] * len(hour_labels)  # 역이 선택되지 않으면 빈 데이터를 반환
    row = df_filtered[(df_filtered["호선"] == line) & (df_filtered["출발역"] == station)][time_cols_30min].mean()
    return [row[[col1, col2]].mean() for col1, col2 in time_pairs]

hourly_avg1 = get_hourly_avg(line1, station1)
hourly_avg2 = get_hourly_avg(line2, station2)

# ✅ 혼잡도 그래프
st.markdown("### 📊 혼잡도 비교 그래프")
fig = go.Figure()
fig.add_trace(go.Bar(x=hour_labels, y=hourly_avg1, name=f"{line1}호선 {station1}" if station1 else "역 선택 필요", marker_color='royalblue'))
fig.add_trace(go.Bar(x=hour_labels, y=hourly_avg2, name=f"{line2}호선 {station2}" if station2 else "역 선택 필요", marker_color='darkorange'))
fig.update_layout(
    barmode='group',
    title=f"🕐 1시간 단위 혼잡도 비교" if station1 and station2 else "역을 선택하세요",
    xaxis_title="시간대",
    yaxis_title="혼잡도 (%)",
    xaxis_tickangle=0,
    height=600
)
st.plotly_chart(fig)

# ✅ 선택된 역 지도에 마커 표시
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

# 역이 선택된 경우 지도에 마커 추가
if station1 and station2:
    selected_stations = station_info[station_info["역사명"].isin([station1, station2])]
    for _, row in selected_stations.iterrows():
        name = row["역사명"] + "역"
        lat = row["역위도"]
        lon = row["역경도"]
        color = "royalblue" if row["역사명"] == station1 else "darkorange"
        icon_name = "star" if row["역사명"] == station1 else "cloud"
        add_marker_with_label(lat, lon, name, color, icon_name)

# 지도 출력
st_folium(m, width=800, height=600)
