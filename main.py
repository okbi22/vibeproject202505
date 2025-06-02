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
df_filtered = df[df['요일구분'] == day_option]

# ✅ 사용자 선택 - 역1
st.subheader("🔵 첫 번째 역 선택")
line1_options = ["1~8호선 중 선택"] + sorted(df_filtered["호선"].unique())
line1 = st.selectbox("1️⃣ 첫 번째 호선을 선택하세요", line1_options, key="line1")

station1_list = sorted(df_filtered[df_filtered["호선"] == line1]["출발역"].unique()) if line1 != "1~8호선 중 선택" else []
station1 = st.selectbox("📍 첫 번째 역을 선택하세요", ["역명 선택"] + station1_list, key="station1")

# ✅ 사용자 선택 - 역2
st.subheader("🟠 두 번째 역 선택")
line2_options = ["1~8호선 중 선택"] + sorted(df_filtered["호선"].unique())
line2 = st.selectbox("2️⃣ 두 번째 호선을 선택하세요", line2_options, key="line2")

station2_list = sorted(df_filtered[df_filtered["호선"] == line2]["출발역"].unique()) if line2 != "1~8호선 중 선택" else []
station2 = st.selectbox("📍 두 번째 역을 선택하세요", ["역명 선택"] + station2_list, key="station2")

# ✅ 시간대 평균 계산
time_cols = df.columns[6:]
hour_labels = [col[:col.find('시') + 1] for col in time_cols]

def get_hourly_avg(line, station):
    if station == "역명 선택":
        return [0] * len(hour_labels)
    row = df_filtered[(df_filtered["호선"] == line) & (df_filtered["출발역"] == station)][time_cols].mean()
    return list(row)

hourly_avg1 = get_hourly_avg(line1, station1)
hourly_avg2 = get_hourly_avg(line2, station2)

# ✅ 혼잡도 그래프
st.markdown("### 📊 혼잡도 비교 그래프")
fig = go.Figure()
fig.add_trace(go.Bar(x=hour_labels, y=hourly_avg1, name=f"{line1}호선 {station1}" if station1 != "역명 선택" else "역 선택 필요", marker_color='royalblue'))
fig.add_trace(go.Bar(x=hour_labels, y=hourly_avg2, name=f"{line2}호선 {station2}" if station2 != "역명 선택" else "역 선택 필요", marker_color='darkorange'))
fig.update_layout(
    barmode='group',
    title=f"🕐 1시간 단위 혼잡도 비교" if station1 != "역명 선택" and station2 != "역명 선택" else "역을 선택하세요",
    xaxis_title="시간대",
    yaxis_title="혼잡도 (%)",
    xaxis_tickangle=0,
    height=600
)
st.plotly_chart(fig)

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
            icon_size=(len(name) * 12, 30),  # 글자 길이에 따라 배경 크기 조정
            icon_anchor=(0, 0),
            html=f'<div style="display: inline-block; font-size: 14pt; color: {color}; font-weight: bold; '
                 f'background-color: white; padding: 5px 10px; border-radius: 8px; border: 1px solid black; '
                 f'white-space: nowrap;">{name}</div>',
        )
    ).add_to(m)



# 선택한 역이 있을 경우 지도에 마커 추가
if station1 != "역명 선택" and station2 != "역명 선택":
    selected_stations = station_info[station_info["역사명"].isin([station1, station2])]

    if not selected_stations.empty:  # 두 개의 역을 올바르게 가져왔는지 확인
        for _, row in selected_stations.iterrows():
            name = row["역사명"] + "역"
            lat = row["역위도"]
            lon = row["역경도"]
            color = "royalblue" if row["역사명"] == station1 else "darkorange"
            icon_name = "star" if row["역사명"] == station1 else "cloud"
            add_marker_with_label(lat, lon, name, color, icon_name)

# 지도 출력
st_folium(m, width=800, height=600)
