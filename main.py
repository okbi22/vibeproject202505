import streamlit as st
import pandas as pd
import plotly.graph_objs as go
import folium
from streamlit_folium import st_folium

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

# ✅ 좌표 사전 정의 (필요한 역만 추가)
station_coords = {
    "청량리": [37.5802, 127.0464],
    "강남": [37.4979, 127.0276],
    "서울역": [37.5547, 126.9706],
    "홍대입구": [37.5572, 126.9245],
    "신도림": [37.5088, 126.8910],
    "건대입구": [37.5405, 127.0697],
    "삼각지": [37.5345, 126.9736],
    # 필요한 역 추가하세요
}

# ✅ 지도 시각화
st.markdown("---")
st.markdown("### 🗺️ 선택한 역의 지도 위치")
center = [37.5665, 126.9780]
m = folium.Map(location=center, zoom_start=12)

for station in [station1, station2]:
    if station in station_coords:
        lat, lon = station_coords[station]
        folium.Marker(
            location=[lat, lon],
            popup=f"{station}역",
            tooltip="📍 " + station,
            icon=folium.Icon(color="blue" if station == station1 else "orange")
        ).add_to(m)
    else:
        st.warning(f"⚠️ '{station}' 역의 좌표 정보가 없습니다. station_coords 딕셔너리에 추가해주세요.")

st_folium(m, width=700, height=500)
