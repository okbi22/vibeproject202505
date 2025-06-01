import streamlit as st
import pandas as pd
import plotly.express as px

# 데이터 불러오기
@st.cache_data
def load_data():
    df = pd.read_csv("subway_congestion.csv")
    return df

df = load_data()

# UI - 첫 번째 역 선택
st.title("🚇 서울 지하철 혼잡도 비교")
st.subheader("두 개의 역을 선택하여 비교하세요!")

selected_line_1 = st.selectbox("📌 첫 번째 호선을 선택하세요", sorted(df['호선'].unique()), key="line1")
selected_station_1 = st.selectbox("🚉 첫 번째 출발역을 선택하세요", sorted(df[df['호선'] == selected_line_1]['출발역'].unique()), key="station1")

# UI - 두 번째 역 선택
selected_line_2 = st.selectbox("📌 두 번째 호선을 선택하세요", sorted(df['호선'].unique()), key="line2")
selected_station_2 = st.selectbox("🚉 두 번째 출발역을 선택하세요", sorted(df[df['호선'] == selected_line_2]['출발역'].unique()), key="station2")

# 상하선 선택
selected_direction = st.selectbox("🚇 상하선 선택", sorted(df['상하구분'].unique()))

# 데이터 필터링
if selected_station_1 and selected_station_2:
    # 두 역의 데이터를 한 번에 필터링
    # SettingWithCopyWarning을 피하기 위해 .copy() 사용
    plot_data = df[
        (((df['호선'] == selected_line_1) & (df['출발역'] == selected_station_1)) |
         ((df['호선'] == selected_line_2) & (df['출발역'] == selected_station_2))) &
        (df['상하구분'] == selected_direction)
    ].copy()

    # 시간대 컬럼 추출
    time_columns = [col for col in df.columns if '시' in col]
    
    # 데이터 변형 (melt)
    melted = plot_data.melt(id_vars=['출발역'], value_vars=time_columns, var_name='시간', value_name='혼잡도')

    # 두 역 모두 데이터가 있는지 확인
    # melted DataFrame에 두 역이 모두 포함되어 있어야 정상적으로 그래프가 그려집니다.
    if not melted.empty and \
       selected_station_1 in melted['출발역'].unique() and \
       selected_station_2 in melted['출발역'].unique():
        
        # 색상 명확히 지정 (첫 번째 역: 빨강, 두 번째 역: 파랑)
        color_map = {selected_station_1: "red", selected_station_2: "blue"}
        
        # 하나의 그래프 안에 막대 나란히 표시
        fig = px.bar(melted, x='시간', y='혼잡도', color='출발역', 
                     barmode="group", # <-- 이 부분이 중요합니다!
                     title=f"{selected_station_1} (🔴) vs {selected_station_2} (🔵) 혼잡도 비교",
                     color_discrete_map=color_map,
                     labels={"혼잡도": "혼잡도 (비율)", "시간": "시간대"},
                     # 툴팁에 호선 정보 추가 (선택 사항)
                     hover_data={'호선': False, '출발역': True, '혼잡도': True, '시간': True}
                    )

        st.plotly_chart(fig, use_container_width=True)
    else:
        # 데이터가 없거나 두 역 중 하나의 데이터가 없는 경우 경고
        missing_stations = []
        if selected_station_1 not in melted['출발역'].unique():
            missing_stations.append(selected_station_1)
        if selected_station_2 not in melted['출발역'].unique():
            missing_stations.append(selected_station_2)
        
        if missing_stations:
            st.warning(f"⚠️ 선택된 역 중 '{', '.join(missing_stations)}'의 데이터가 없습니다. CSV 파일을 확인하거나 다른 역을 선택하세요.")
        else:
            st.warning("⚠️ 선택된 역에 대한 데이터가 없습니다. CSV 파일을 확인하세요.")

else:
    st.warning("⚠️ 두 개의 출발역을 선택하세요!")
