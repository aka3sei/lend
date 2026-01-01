import streamlit as st
import pandas as pd

# ==========================================
# 1. ページ基本設定
# ==========================================
st.set_page_config(page_title="23区 不動産AI分析・決定版", layout="wide")

st.title("🤖 23区別：家賃相場 × 人口動態 AI予測システム")
st.write("最新の2025年相場と、公的統計に基づく2045年までの予測を統合解析します。")

# ==========================================
# 2. 23区マスターデータ（すべて網羅）
# ==========================================
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

# ==========================================
# 3. サイドバー：市場条件・物件収支設定
# ==========================================
st.sidebar.header("🕹️ 市場予測・条件設定")
selected_ward = st.sidebar.selectbox("分析対象の区を選択", list(ward_data.keys()))
room_size = st.sidebar.slider("想定専有面積 (㎡)", 15, 80, 25)
inflation = st.sidebar.slider("AI想定・年間インフレ率 (%)", 0.0, 3.0, 1.2) / 100

st.sidebar.divider()
st.sidebar.header("💰 物件個別収支設定")
prop_price = st.sidebar.number_input("物件購入価格 (万円)", value=3500, step=100)
admin_fee = st.sidebar.number_input("管理費・修繕積立金/月 (円)", value=12000, step=500)
tax_annual = st.sidebar.number_input("固定資産税・都市計画税/年 (円)", value=80000, step=1000)
vacancy_rate = st.sidebar.slider("想定空室リスク (%)", 0, 10, 5) / 100

base = ward_data[selected_ward]

# ==========================================
# 4. AI将来予測ロジック（家賃・人口・世帯数）
# ==========================================
years = [2025, 2030, 2035, 2040, 2045]
sim_list = []

for i, year in enumerate(years):
    t_step = i 
    pop_sim = 100 * (1 + (base['pop_idx'] - 1) * (i/4))
    hh_sim = 100 * (1 + (base['hh_idx'] - 1) * (i/4))
    
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

# ==========================================
# 5. UI表示：マーケット予測セクション
# ==========================================
col1, col2, col3 = st.columns(3)
rent_diff = sim_list[-1]['予測家賃'] - sim_list[0]['予測家賃']

with col1:
    st.metric("現在の相場家賃", f"{int(base['rent_m2'] * room_size):,} 円", f"{base['rent_m2']:,} 円/㎡")
with col2:
    st.metric("2045年 AI予測家賃", f"{sim_list[-1]['予測家賃']:,} 円", f"{rent_diff:,} 円")
with col3:
    st.metric("世帯数指数(2045)", f"{sim_list[-1]['世帯数指数']}", f"{sim_list[-1]['世帯数指数']-100:+.1f}%")

st.divider()

st.subheader(f"📈 {selected_ward}：AI将来予測チャート")
tab1, tab2 = st.tabs(["💴 家賃相場推移", "👥 人口・世帯動態指数"])

with tab1:
    st.line_chart(df_sim["予測家賃"])
    st.caption("▲ 将来の月額家賃予測：世帯需要とインフレ率を統合解析")

with tab2:
    st.line_chart(df_sim[["人口指数", "世帯数指数"]])
    st.caption("▲ 2025年を100とした人口・世帯推移：世帯数（青）が需要の鍵です")

st.divider()

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

# ==========================================
# 6. 収支シミュレーションロジック
# ==========================================
cash_flow_results = []
for row in sim_list:
    gross_revenue = int(row['予測家賃'] * 12 * (1 - vacancy_rate))
    operating_expenses = (admin_fee * 12) + tax_annual
    noi = gross_revenue - operating_expenses
    net_yield = (noi / (prop_price * 10000)) * 100
    
    cash_flow_results.append({
        "年": row['年'],
        "年間純収益": noi,
        "実質利回り": round(net_yield, 2)
    })

df_cf = pd.DataFrame(cash_flow_results).set_index("年")

# ==========================================
# 7. UI表示：物件収支セクション
# ==========================================
st.divider()
st.header("💰 物件収支シミュレーション (NOI分析)")
st.write(f"エリア予測に基づき、この物件を **{prop_price}万円** で購入した場合の収益推移を算出しました。")

c1, c2, c3 = st.columns(3)
with c1:
    initial_yield = ( (sim_list[0]['予測家賃'] * 12) / (prop_price * 10000) ) * 100
    st.metric("初期 表面利回り", f"{initial_yield:.2f} %")
with c2:
    st.metric("初期 実質利回り", f"{cash_flow_results[0]['実質利回り']:.2f} %", "諸経費・空室考慮")
with c3:
    st.metric("20年後の実質利回り", f"{cash_flow_results[-1]['実質利回り']:.2f} %", 
              f"{cash_flow_results[-1]['実質利回り'] - cash_flow_results[0]['実質利回り']:+.2f} %")

st.write("### 📉 20年間の純収益（キャッシュフロー）予測")
st.area_chart(df_cf["年間純収益"])
st.caption("※年間純収益 = (予測家賃 × 12ヶ月 × 稼働率) - 運営費用")

# ==========================================
# 8. 取引ロードマップセクション
# ==========================================
st.divider()
st.header("🗺️ 不動産取引ロードマップ")
mode = st.radio("取引の種別を選択してください", ["売却の流れ", "購入の流れ"], horizontal=True)

if mode == "売却の流れ":
    # 9ステップ
    steps = [
        "1.売買相談", "2.物件調査", "3.査定", "4.媒介契約", 
        "5.インスペクション", "6.広告", "7.契約交渉", 
        "8.重要事項説明", "9.引渡・登記・決済"
    ]
    st.success("🏠 **売却フェーズ:** 公示地価とAI予測に基づき、最適な売り時をアドバイスします。")
else:
    # 10ステップ
    steps = [
        "1.購入相談", "2.資金計画", "3.物件調査", "4.購入申込", 
        "5.契約交渉", "6.媒介契約", "7.重要事項説明", 
        "8.売買契約締結", "9.住宅ローン審査", "10.引渡・登記・決済"
    ]
    st.success("🔑 **購入フェーズ:** 収支シミュレーションを軸に、無理のない資金計画をサポートします。")

# 進捗管理スライダー
current_step = st.select_slider("現在の進捗状況をチェック", options=steps)
progress_percentage = (steps.index(current_step) + 1) / len(steps)
st.progress(progress_percentage)

st.write(f"現在のステップ: **{current_step}**")
st.caption("※不動産取引の一般的な流れです。物件や条件により前後する場合があります。")
