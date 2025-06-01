import streamlit as st
import folium
from geopy.geocoders import Nominatim
from streamlit_folium import st_folium

# 📍 지오코더 설정
geolocator = Nominatim(user_agent="subway-map")

# 🏙️ 역명 입력 받기
station_name = st.text_input("🔍 역명을 입력하세요 (예: 청량리)")

if station_name:
    location = geolocator.geocode(station_name + "역, 서울")

    if location:
        # 🗺️ 지도 생성
        m = folium.Map(location=[location.latitude, location.longitude], zoom_start=16)
        folium.Marker(
            [location.latitude, location.longitude],
            popup=f"{station_name}역",
            tooltip="📍 클릭하면 위치 표시"
        ).add_to(m)

        st.markdown(f"### 🧭 {station_name}역 위치")
        st_folium(m, width=700, height=500)
    else:
        st.error("❌ 역의 위치를 찾을 수 없습니다. 정확한 역명을 입력해주세요.")
