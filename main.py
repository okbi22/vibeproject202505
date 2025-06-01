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

# 데이터 필터링 및 그래프 생성
if selected_station_1 and selected_station_2:
    # 시간대 컬럼 추출
    time_columns = [col for col in df.columns if '시' in col]

    # 첫 번째 역 데이터 필터링
    data_station_1 = df[
        (df['호선'] == selected_line_1) &
        (df['출발역'] == selected_station_1) &
        (df['상하구분'] == selected_direction)
    ]
    melted_station_1 = data_station_1.melt(id_vars=['출발역'], value_vars=time_columns, var_name='시간', value_name='혼잡도')

    # 두 번째 역 데이터 필터링
    data_station_2 = df[
        (df['호선'] == selected_line_2) &
        (df['출발역'] == selected_station_2) &
        (df['상하구분'] == selected_direction)
    ]
    melted_station_2 = data_station_2.melt(id_vars=['출발역'], value_vars=time_columns, var_name='시간', value_name='혼잡도')

    # 그래프를 나란히 표시하기 위한 컬럼 생성
    col1, col2 = st.columns(2)

    with col1:
        if not melted_station_1.empty:
            fig1 = px.bar(melted_station_1, x='시간', y='혼잡도', color_discrete_sequence=["red"],
                          title=f"{selected_station_1} (🔴) 혼잡도",
                          labels={"혼잡도": "혼잡도 (비율)", "시간": "시간대"})
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.warning(f"⚠️ '{selected_station_1}'의 데이터가 없습니다. CSV 파일을 확인하세요.")

    with col2:
        if not melted_station_2.empty:
            fig2 = px.bar(melted_station_2, x='시간', y='혼잡도', color_discrete_sequence=["blue"],
                          title=f"{selected_station_2} (🔵) 혼잡도",
                          labels={"혼잡도": "혼잡도 (비율)", "시간": "시간대"})
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.warning(f"⚠️ '{selected_station_2}'의 데이터가 없습니다. CSV 파일을 확인하세요.")
else:
    st.warning("⚠️ 두 개의 출발역을 선택하세요!")
