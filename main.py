import streamlit as st
import pandas as pd
import plotly.graph_objs as go

# 데이터 로드
df = pd.read_csv("subway_congestion.csv")

# 평일, 상선 데이터만 사용
df_filtered = df[(df['요일구분'] == '평일') & (df['상하구분'] == '상선')]

# 시간대 컬럼 추출
time_columns = df.columns[6:]

# Streamlit UI
st.title("지하철 역 혼잡도 비교")

# 역 선택
station_list = df_filtered['출발역'].unique()
station1 = st.selectbox("첫 번째 역 선택", station_list)
station2 = st.selectbox("두 번째 역 선택", station_list, index=1)

# 선택된 역의 데이터 추출
data1 = df_filtered[df_filtered['출발역'] == station1][time_columns].mean()
data2 = df_filtered[df_filtered['출발역'] == station2][time_columns].mean()

# Plotly 그래프 생성
fig = go.Figure()

fig.add_trace(go.Bar(
    x=time_columns,
    y=data1,
    name=station1,
    marker_color='blue'
))

fig.add_trace(go.Bar(
    x=time_columns,
    y=data2,
    name=station2,
    marker_color='orange'
))

fig.update_layout(
    barmode='group',
    title=f"{station1} vs {station2} 시간대별 혼잡도 비교",
    xaxis_title="시간대",
    yaxis_title="혼잡도 수치",
    xaxis_tickangle=-45,
    height=600
)

st.plotly_chart(fig)
