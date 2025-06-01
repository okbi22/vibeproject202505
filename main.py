import streamlit as st
import pandas as pd
import plotly.graph_objs as go

# 📁 데이터 로드
df = pd.read_csv("subway_congestion.csv")

# 📌 데이터 필터링: 평일 + 상선만 사용
df_filtered = df[(df['요일구분'] == '평일') & (df['상하구분'] == '상선')]

# 🕒 시간대 컬럼 (30분 단위)
time_cols_30min = df.columns[6:]

# 🧮 1시간 단위 평균 열 만들기
time_groups = [(time_cols_30min[i], time_cols_30min[i + 1]) for i in range(0, len(time_cols_30min) - 1, 2)]
hour_labels = [f"{col1[:-2]}" for col1, _ in time_groups]  # "5시", "6시" 등

# 🧪 각 역의 1시간 단위 평균 계산 함수
def get_hourly_avg(row):
    return [row[col1:col2].mean() for col1, col2 in time_groups]

# 🎨 Streamlit UI 구성
st.title("🚇 서울 지하철 역 혼잡도 비교")

st.markdown("""
#### 📊 데이터 설명
서울교통공사 1-8호선 **30분 단위 평균 혼잡도**를 기준으로,  
30분간 지나는 열차들의 평균 혼잡도 (정원 대비 승차 인원 비율)를 나타냅니다.  
승객과 좌석 수가 같을 경우를 **혼잡도 34%**로 간주합니다.  
데이터 구성은 다음과 같습니다:

- 📅 요일구분 (평일, 토요일, 일요일)  
- 🚉 호선, 역번호, 역명  
- ↕️ 상/하선 구분  
- ⏰ 30분 단위 혼잡도 (%)

> *아래 그래프는 1시간 단위로 평균을 낸 데이터를 사용합니다.*
""")

# 🔍 역 선택
station_list = sorted(df_filtered['출발역'].unique())
station1 = st.selectbox("🔵 첫 번째 역 선택", station_list)
station2 = st.selectbox("🟠 두 번째 역 선택", station_list, index=1)

# 📊 선택한 역 데이터 가져오기
data1 = df_filtered[df_filtered['출발역'] == station1][time_cols_30min].mean()
data2 = df_filtered[df_filtered['출발역'] == station2][time_cols_30min].mean()

# ⏱ 1시간 단위 평균 계산
hourly_avg1 = [data1[[col1, col2]].mean() for col1, col2 in time_groups]
hourly_avg2 = [data2[[col1, col2]].mean() for col1, col2 in time_groups]

# 📈 Plotly 그래프 생성
fig = go.Figure()

fig.add_trace(go.Bar(
    x=hour_labels,
    y=hourly_avg1,
    name=station1,
    marker_color='royalblue'
))

fig.add_trace(go.Bar(
    x=hour_labels,
    y=hourly_avg2,
    name=station2,
    marker_color='darkorange'
))

fig.update_layout(
    barmode='group',
    title=f"🕐 1시간 단위 혼잡도 비교: {station1} vs {station2}",
    xaxis_title="시간대",
    yaxis_title="혼잡도 (%)",
    xaxis_tickangle=-45,
    height=600
)

st.plotly_chart(fig)
