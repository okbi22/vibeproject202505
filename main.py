import streamlit as st
import pandas as pd
import plotly.express as px

# 데이터 불러오기 (캐시 유효 시간 1시간 설정)
@st.cache_data(ttl=3600)
def load_data():
    try:
        df = pd.read_csv("subway_congestion.csv")
        return df
    except FileNotFoundError:
        st.error("오류: 'subway_congestion.csv' 파일을 찾을 수 없습니다. 파일이 올바른 위치에 있는지 확인하세요.")
        st.stop() # 파일이 없으면 앱 실행 중단
    except Exception as e:
        st.error(f"오류: CSV 파일을 읽는 중 문제가 발생했습니다. {e}")
        st.stop()

df = load_data()

# UI - 첫 번째 역 선택
st.title("🚇 서울 지하철 혼잡도 비교")
st.subheader("두 개의 역을 선택하여 비교하세요!")

selected_line_1 = st.selectbox("📌 첫 번째 호선을 선택하세요", sorted(df['호선'].unique()), key="line1")
# 선택된 호선에 해당하는 역만 목록으로 제공
stations_on_line_1 = sorted(df[df['호선'] == selected_line_1]['출발역'].unique())
selected_station_1 = st.selectbox("🚉 첫 번째 출발역을 선택하세요", stations_on_line_1, key="station1")

# UI - 두 번째 역 선택
selected_line_2 = st.selectbox("📌 두 번째 호선을 선택하세요", sorted(df['호선'].unique()), key="line2")
# 선택된 호선에 해당하는 역만 목록으로 제공
stations_on_line_2 = sorted(df[df['호선'] == selected_line_2]['출발역'].unique())
selected_station_2 = st.selectbox("🚉 두 번째 출발역을 선택하세요", stations_on_line_2, key="station2")

# 상하선 선택
selected_direction = st.selectbox("🚇 상하선 선택", sorted(df['상하구분'].unique()))

# 데이터 필터링 및 그래프 생성
if selected_station_1 and selected_station_2:
    # 사용자 선택의 유효성 미리 검사 (Selectbox에서 이미 걸러지지만, 만약을 대비)
    if selected_station_1 not in stations_on_line_1:
        st.warning(f"⚠️ 선택하신 첫 번째 역 '{selected_station_1}'은(는) '{selected_line_1}' 호선에 존재하지 않습니다. 다른 역을 선택하세요.")
        st.stop() # 더 이상 진행하지 않음
    if selected_station_2 not in stations_on_line_2:
        st.warning(f"⚠️ 선택하신 두 번째 역 '{selected_station_2}'은(는) '{selected_line_2}' 호선에 존재하지 않습니다. 다른 역을 선택하세요.")
        st.stop() # 더 이상 진행하지 않음

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

    # 필터링된 melted DataFrame에 실제로 두 역의 데이터가 모두 포함되어 있는지 최종 확인
    station_1_exists_in_melted = selected_station_1 in melted['출발역'].unique()
    station_2_exists_in_melted = selected_station_2 in melted['출발역'].unique()

    if station_1_exists_in_melted and station_2_exists_in_melted:
        # 색상 명확히 지정 (첫 번째 역: 빨강, 두 번째 역: 파랑)
        color_map = {selected_station_1: "red", selected_station_2: "blue"}
        
        # 하나의 그래프 안에 막대 나란히 표시
        fig = px.bar(melted, x='시간', y='혼잡도', color='출발역', 
                     barmode="group", # 각 시간대별로 두 역의 막대가 옆으로 나란히 정렬
                     title=f"{selected_station_1} (🔴) vs {selected_station_2} (🔵) 혼잡도 비교",
                     color_discrete_map=color_map,
                     labels={"혼잡도": "혼잡도 (비율)", "시간": "시간대"},
                     hover_data={'호선': False, '출발역': True, '혼잡도': True, '시간': True} # 툴팁 설정
                    )

        st.plotly_chart(fig, use_container_width=True)
    else:
        # 두 역 중 하나라도 최종 필터링된 데이터에 없는 경우 구체적인 경고
        missing_stations = []
        if not station_1_exists_in_melted:
            missing_stations.append(selected_station_1)
        if not station_2_exists_in_melted:
            missing_stations.append(selected_station_2)
        
        st.warning(
            f"⚠️ 선택된 역 중 '{', '.join(missing_stations)}'에 대한 데이터가 없습니다. "
            f"선택하신 호선/상하선 조합에 해당 역의 혼잡도 데이터가 없거나, CSV 파일에 역 이름이 다르게 표기되어 있을 수 있습니다. "
            "CSV 파일을 확인하거나 다른 역을 선택하세요."
        )

else:
    st.warning("⚠️ 두 개의 출발역을 선택하세요!")
