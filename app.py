import streamlit as st
from score import get_score, get_town_list
import numpy as np
import matplotlib.pyplot as plt
import sqlite3
import pandas as pd
from database import DB_PATH
from hospital import update_hospital_db
import importlib
import score
<<<<<<< HEAD


=======
>>>>>>> 7a09d79bc635037f95f35426ba7d13a620cef84a

plt.rcParams["font.family"] = "Meiryo"

st.set_page_config(page_title='town health checkup', page_icon="🏥")

st.title("まちの健康診断")
st.caption("気になる町の健康診断を行いましょう！（諫早エリア編）")

tab1, tab2, tab3 = st.tabs(["フリーワード検索", "一覧から検索", "情報の更新"])


with tab1:
    st.subheader("🔍フリーワード検索")
    towns_text = st.text_area("✐町名を入力（改行区切り）")

    if st.button("検索"):
        towns = [t.strip() for t in towns_text.splitlines() if t.strip()]
<<<<<<< HEAD

    # ★ 災害スコアを都度計算
        
       

=======
>>>>>>> 7a09d79bc635037f95f35426ba7d13a620cef84a
        for t in towns:
            with st.spinner("🔍検索中"):
                hospital_density = get_score(t, "hospital_score")
                school_density = get_score(t, "school_score")
                crime_density = get_score(t, "crime_score")
                hazard_level = get_score(t, "hazard_score")
                bus_density = get_score(t, "bus_score")

            col1, col2 = st.columns(2)
            
            #左側
            with col1:
                st.markdown(f"### 📋 {t} の住みよさカルテ")
                st.write(f"医療充実度 : {hospital_density:.2f}")
                st.write(f"教育充実度 : {school_density:.2f}")
                st.write(f"治安充実度 : {crime_density:.2f}")
                st.write(f"災害充実度 : {hazard_level:.2f}")
                st.write(f"交通充実度 : {bus_density:.2f}")

            #右側（レーダーチャート）
            with col2:
                labels = ["医療充実度", "教育充実度", "治安充実度", "災害充実度", "交通充実度"]
                values = [hospital_density, school_density, crime_density, hazard_level, bus_density]

                angles = np.linspace(0, 2 * np.pi,len(labels), endpoint=False).tolist()
                values += values[:1]
                angles += angles[:1]

                fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True), facecolor="none")

                #背景を透過
                fig.patch.set_alpha(0)
                ax.set_facecolor("none")

                #レーダーチャート作成
                ax.set_theta_offset(np.pi / 2)
                ax.set_theta_direction(-1)

                ax.plot(angles, values, color="#00BFFF", linewidth=2)
                ax.fill(angles, values, color="#00BFFF", alpha=0.25)
                ax.set_xticks(angles[:-1])
                ax.set_xticklabels(labels)
                ax.set_ylim(0, 100)
                st.pyplot(fig)

            st.write("📋 診断結果")
            st.markdown(f"### {t}は...が充実している町です！")
                        
            st.divider()



    else:
        st.info("町名を入力してください")

with tab2:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM score", conn)
    towns = []

<<<<<<< HEAD
    # ★ 災害スコアを都度計算（一覧検索時に一度だけ）
   

=======
>>>>>>> 7a09d79bc635037f95f35426ba7d13a620cef84a
    area_order = [
        "諫早地域",
        "多良見地域",
        "森山地域",
        "飯盛地域",
        "高来地域",
        "小長井地域"
    ]
    #areaごとに塊を作りその中でチェックボックス作成
    for area in area_order:
        with st.expander(area):
            area_towns = df[
                df["town_area_name"] == area
            ]["town_name"].tolist()

            #選択肢に町名を入れる
            cols = st.columns(4)
            for i, town in enumerate(area_towns):
                with cols[i%4]:
                    if st.checkbox(town, key=f"town_{town}"):
                        towns.append(town)


    #以下tab1と同じ(編集してます)
    results =[]

    sort_type = st.selectbox(
        "条件を選んで並び替え",
        [
            "医療充実度",
            "教育充実度",
            "治安充実度",
            "災害充実度",
            "交通充実度"
        ]
    )

    sort_map = {
        "医療充実度": "hospital",
        "教育充実度": "school",
        "治安充実度": "crime",
        "災害充実度": "hazard",
        "交通充実度": "bus"
    }

    for t in towns:
        with st.spinner("🔍検索中"):
            hospital_density = get_score(t, "hospital_score")
            school_density = get_score(t, "school_score")
            crime_density = get_score(t, "crime_score")
            hazard_level = get_score(t, "hazard_score")
            bus_density = get_score(t, "bus_score")

            results.append({
                "town": t,
                "hospital": hospital_density,
                "school": school_density,
                "crime": crime_density,
                "hazard": hazard_level,
                "bus":bus_density
            })

    results.sort(key=lambda x: x[sort_map[sort_type]], reverse=True)

    for r in results:
        t = r["town"]
        hospital_density = r["hospital"]
        school_density = r["school"]
        crime_density = r["crime"]
        hazard_level = r["hazard"]
        bus_density = r["bus"]

        scores ={
            "医療環境": hospital_density,
            "教育環境": school_density,
            "治安": crime_density,
            "災害への安全性": hazard_level,
            "交通環境": bus_density
        }
        good_points = [
            name for name, score in scores.items()
            if score > 60
        ]
        weak_points = [
            name for name, score in scores.items()
            if score < 40
        ]

        st.markdown(f"#### 📋 {t} の住みよさカルテ")
    
        col1, col2 = st.columns(2)

        with col1:
            if hospital_density > 60:
                st.markdown(f"##### 医療充実度： <span style='color:#FF9800'>{hospital_density:.2f}</span>", unsafe_allow_html=True)
            elif hospital_density < 60:
                st.markdown(f"##### 医療充実度： <span style='color:#00BFFF'>{hospital_density:.2f}</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"##### 医療充実度： {hospital_density:.2f}")

            if school_density > 60:
                st.markdown(f"##### 教育充実度： <span style='color:#FF9800'>{school_density:.2f}</span>", unsafe_allow_html=True)
            elif school_density < 60:
                st.markdown(f"##### 教育充実度： <span style='color:#00BFFF'>{school_density:.2f}</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"##### 教育充実度： {school_density:.2f}")

            if crime_density > 60:
                st.markdown(f"##### 治安充実度： <span style='color:#FF9800'>{crime_density:.2f}</span>", unsafe_allow_html=True)
            elif crime_density < 60:
                st.markdown(f"##### 治安充実度： <span style='color:#00BFFF'>{crime_density:.2f}</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"##### 治安充実度： {crime_density:.2f}")

            if hazard_level > 60:
                st.markdown(f"##### 災害充実度： <span style='color:#FF9800'>{hazard_level:.2f}</span>", unsafe_allow_html=True)
            elif hazard_level < 60:
                st.markdown(f"##### 災害充実度： <span style='color:#00BFFF'>{hazard_level:.2f}</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"##### 災害充実度： {hazard_level:.2f}")

            if bus_density > 60:
                st.markdown(f"##### 交通充実度： <span style='color:#FF9800'>{bus_density:.2f}</span>", unsafe_allow_html=True)
            elif bus_density < 60:
                st.markdown(f"##### 交通充実度： <span style='color:#00BFFF'>{bus_density:.2f}</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"##### 交通充実度： {bus_density:.2f}")

        with col2:
            labels = ["医療充実度", "教育充実度", "治安充実度", "災害充実度", "交通充実度"]
            values = [hospital_density, school_density, crime_density, hazard_level, bus_density]

            angles = np.linspace(0, 2 * np.pi,len(labels), endpoint=False).tolist()
            values += values[:1]
            angles += angles[:1]

            fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True), facecolor="none")

            fig.patch.set_alpha(0)
            ax.set_facecolor("none")

            ax.set_theta_offset(np.pi / 2)
            ax.set_theta_direction(-1)

            ax.plot(angles, values, color="#00BFFF", linewidth=2)
            ax.fill(angles, values, color="#00BFFF", alpha=0.25)
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(labels)
            ax.set_ylim(0, 100)
            st.pyplot(fig)

        if good_points or weak_points:
            st.write("📋 診断結果")

        if good_points:
            perfect = "と".join(good_points)
            st.markdown(f"### {t}は<span style='color:#FF9800'>{perfect}</span>が充実している町です！", unsafe_allow_html=True)

        if weak_points:
            more = "と".join(weak_points)
            st.markdown(f"### {t}は<span style='color:#00BFFF'>{more}</span>が弱点です！", unsafe_allow_html=True)

        st.divider()

with tab3:
    st.subheader("❔情報の更新")

    if st.button("病院情報を更新"):
        with st.spinner("病院情報を更新中"):
            update_hospital_db()
            #score.pyを再度読み込み、最新のDBからdfを作り直す
            importlib.reload(score)
        st.success("病院情報更新完了です")