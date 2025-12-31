import streamlit as st
import pandas as pd

# ページ設定
st.set_page_config(page_title="23区 不動産AI分析・決定版", layout="wide")

st.title("🤖 23区別：現在相場 × 人口動態 AI予測システム")
st.write("最新の2025年相場と、公的統計に基づく2045年までの予測を統合解析します。")

# --- 【重要1】23区すべての最新マスターデータ (2025年1月時点の相場) ---
# rent_m2: 平均平米単価(円) / pop_idx: 2045年人口推計比 / hh_idx: 2045年世帯数推計比
ward_data = {
    "千代田区": {"rent_m2": 5400, "pop_idx": 1.22, "hh_idx": 1.25},
    "中央区":   {"rent_m2": 5000, "pop_idx": 1.28, "hh_idx": 1.32},
    "港区":     {"rent_m2": 5800, "pop_idx": 1.18, "hh_idx": 1.22},
    "新宿区":   {"rent_m2": 4400, "pop_idx": 1.05, "hh_idx": 1.09},
    "文京区":   {"rent_m2": 4100, "pop_idx": 1.02, "hh_idx": 1.05},
    "台東区":   {"rent_m2": 3900, "pop_idx": 1.12, "hh_idx": 1.15},
    "墨田区":   {"rent_m2": 3600, "pop_idx": 1.04, "hh_idx": 1.08},
    "江東区":   {"rent_m2": 3700, "pop_idx": 1.14, "hh_idx": 1.17},
    "品川区":   {"rent_m2": 4200, "pop_idx": 1.03, "hh_idx": 1.07},
    "目黒区":   {"rent_m2": 4500, "pop_idx": 1.01, "hh_idx": 1.05},
    "大田区":   {"rent_m2": 3300, "pop_idx": 0.98, "hh_idx": 1.03},
    "世田谷区": {"rent_m2": 3800, "pop_idx": 0.98, "hh_idx": 1.04},
    "渋谷区":   {"rent_m2": 5500, "pop_idx": 1.12, "hh_idx": 1.16},
    "中野区":   {"rent_m2": 4000, "pop_idx": 1.02, "hh_idx": 1.06},
    "杉並区":   {"rent_m2": 3600, "pop_idx": 0.99, "hh_idx": 1.03},
    "豊島区":   {"rent_m2": 4100, "pop_idx": 1.10, "hh_idx": 1.13},
    "北区":     {"rent_m2": 3400, "pop_idx": 1.00, "hh_idx": 1.04},
    "荒川区":   {"rent_m2": 3300, "pop_idx": 1.03, "hh_idx": 1.07},
    "板橋区":   {"rent_m2": 3100, "pop_idx": 0.98, "hh_idx": 1.03},
    "練馬区":   {"rent_m2": 3000, "pop_idx": 0.98, "hh_idx": 1.02},
    "足立区":   {"rent_m2": 2800, "pop_idx": 0.92, "hh_idx": 0.97},
    "葛飾区":   {"rent_m2": 2700, "pop_idx": 0.93, "hh_idx": 0.98},
    "江戸川区": {"rent_m2": 2900, "pop_idx": 0.95, "hh_idx": 1.00}
}

# サイドバー
st.sidebar.header("🕹️ 条件設定")
selected_ward = st.sidebar.selectbox("分析対象の区を選択", list(ward_data.keys()))
room_size = st.sidebar.slider("想定専有面積 (㎡)", 15, 80, 25)
inflation = st.sidebar.slider("AI想定・年間インフレ率 (%)", 0.0, 3.0, 1.2) / 100

base = ward_data[selected_ward]

# --- 【重要2】3要素連動AI将来予測ロジック ---
years = [2025, 2030, 2035, 2040, 2045]
sim_list = []

for i, year in enumerate(years):
    t_step = i # 0, 1, 2, 3, 4 (5年毎)
    
    # 2025年を100とした指数の計算
    pop_sim = 100 * (1 + (base['pop_idx'] - 1) * (i/4))
    hh_sim = 100 * (1 + (base['hh_idx'] - 1) * (i/4))
    
    # 家賃予測AI：世帯数増の寄与 + インフレ複利
    demand_impact = (base['hh_idx'] - 1) * 0.4
    inf_factor = (1 + inflation) ** (t_step * 5)
    
    current_rent_base = base['rent_m2'] * room_size
    future_rent = int(current_rent_base * (1 + demand_impact * (i/4)) * inf_factor)
    
    sim_list.append({
        "年": year,
        "予測家賃": future_rent,
        "人口指数": round(pop_sim, 1),
        "世帯数指数": round(hh_sim, 1)
    })

df_sim = pd.DataFrame(sim_list).set_index("年")

# --- UI表示 ---
col1, col2, col3 = st.columns(3)

# 差額の計算（エラー回避のため事前に定義）
rent_diff = sim_list[-1]['予測家賃'] - sim_list[0]['予測家賃']

with col1:
    st.metric("現在の相場家賃", f"{int(base['rent_m2'] * room_size):,} 円", f"{base['rent_m2']:,} 円/㎡")
with col2:
    st.metric("2045年 AI予測家賃", f"{sim_list[-1]['予測家賃']:,} 円", f"{rent_diff:,} 円")
with col3:
    st.metric("世帯数指数(2045)", f"{sim_list[-1]['世帯数指数']}", f"{sim_list[-1]['世帯数指数']-100:+.1f}%")

st.divider()

# グラフセクション
st.subheader(f"📈 {selected_ward}：AI将来予測チャート")
tab1, tab2 = st.tabs(["💴 家賃相場推移", "👥 人口・世帯動態指数"])

with tab1:
    st.line_chart(df_sim["予測家賃"])
    st.caption("▲ 将来の月額家賃予測：世帯需要とインフレ率を統合解析")

with tab2:
    # 指数グラフが100基準で見えるように表示
    st.line_chart(df_sim[["人口指数", "世帯数指数"]])
    st.caption("▲ 2025年を100とした人口・世帯推移：世帯数（青）が需要の鍵です")

st.divider()

# AI診断
st.subheader("🤖 AI市場診断")
growth_rate = (sim_list[-1]['予測家賃'] / sim_list[0]['予測家賃'] - 1) * 100
st.info(f"AI予測の結果、20年後の家賃は現在より **約 {growth_rate:.1f}% 変動** する見込みです。")

if base['hh_idx'] > 1.15:
    st.success("🔥 **【超有望エリア】** 需要が極めて強く、資産価値の上昇が強く見込めるエリアです。")
elif base['hh_idx'] >= 1.05:
    st.info("✅ **【安定成長エリア】** 人口減少下でも需要が維持され、安定した運用が可能です。")
else:
    st.warning("⚠️ **【選別エリア】** 市場の伸びが緩やかなため、物件の個別スペックが重要になります。")

st.caption("出典：東京都総務局「将来推計人口(令和5年)」、国土交通省「地価公示」を基にAI推計")