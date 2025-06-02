import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import matplotlib.pyplot as plt

# CSV 파일 로드 (역 정보)
station_info = pd.read_csv("stationinfo_20250602.csv")

# 혼잡도 예시 데이터 (여기선 임시로 생성. 실제론 외부에서 로드하거나 계산할 수 있음)
# 시간별 혼잡도 더미 데이터 생성
time_slots = [f"{h}:00" for h in range(6, 24)]
dummy_congestion = {
    "station1": [abs(100 - (i * 5) % 100) for i in range(len(time_slots))],
    "station2": [abs(80 - (i * 3) % 80) for i in range(len(time_slots))]
}

# Streamlit UI: 역 선택
st.title("지하철 혼잡도 시각화 및 역 위치 지도 표시")

station_names = station_info["역사명"].unique()
station1 = st.selectbox("역 1 선택", station_names, index=0)
station2 = st.selectbox("역 2 선택", station_names, index=1)

# 혼잡도 그래프 시각화
fig, ax = plt.subplots()
ax.plot(time_slots, dummy_congestion["station1"], label=station1, marker='o')
ax.plot(time_slots, dummy_congestion["station2"], label=station2, marker='s')
ax.set_title("시간대별 혼잡도")
ax.set_xlabel("시간")
ax.set_ylabel("혼잡도 지수")
ax.legend()
st.pyplot(fig)

# 지도 시각화 (Folium)
selected_stations = station_info[station_info["역사명"].isin([station1, station2])]

if not selected_stations.empty:
    center_lat = selected_stations.iloc[0]["역위도"]
    center_lon = selected_stations.iloc[0]["역경도"]
    m = folium.Map(location=[center_lat, center_lon], zoom_start=13)

    # 각 선택된 역 위치에 마커 표시
    for _, row in selected_stations.iterrows():
        folium.Marker(
            location=[row["역위도"], row["역경도"]],
            popup=row["역사명"],
            tooltip=row["역사명"]
        ).add_to(m)

    st.subheader("선택한 역의 위치")
    st_folium(m, width=700, height=500)
else:
    st.warning("선택한 역의 위치 정보를 찾을 수 없습니다.")
