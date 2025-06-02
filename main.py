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
            html=f'<div style="font-size: 16pt; color: {color}; font-weight: bold; background-color: white; padding: 3px; border-radius: 5px;' \
                 f'border: 1px solid black;' \
                 f'">{name}</div>',
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
