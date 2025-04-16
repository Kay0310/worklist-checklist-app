
import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="작업목록표 입력 시스템", layout="wide")
st.title("📝 작업목록표 입력 시스템")

# 공통 정보 먼저 입력
with st.form("common_info"):
    col1, col2 = st.columns(2)
    with col1:
        team = st.text_input("소속 / 팀 / 과")
        group_name = st.text_input("반 이름")
        user_name = st.text_input("작성자 이름")
    with col2:
        contact = st.text_input("작성자 연락처")
        workplace = st.text_input("작업장 이름")
        total_workers = st.number_input("반별 근로자 수", min_value=1, step=1)
    start_button = st.form_submit_button("작업목록 입력 시작하기")

# 단위작업공정 여러 개 입력
if start_button:
    st.info("예시: '절단작업' / '포장작업' 등 실제 수행되는 작업명을 입력하세요.")

    task_units = []
    num_units = st.number_input("단위작업 개수", min_value=1, step=1, value=1)
    for i in range(int(num_units)):
        with st.expander(f"단위작업 {i+1} 입력"):
            with st.form(f"worklist_form_{i}"):
                task_unit = st.text_input("단위작업명", key=f"task_unit_{i}")
                unit_workers = st.number_input("작업 근로자 수", min_value=1, step=1, key=f"unit_workers_{i}")
                worker_names = st.text_area("작업 근로자 이름 (쉼표로 구분)", key=f"worker_names_{i}")
                work_type = st.radio("작업형태", ["주전", "교대"], key=f"work_type_{i}")
                work_hours = st.text_input("1일 작업시간 (예: 8시간)", key=f"work_hours_{i}")

                st.text_area("📄 단위작업 내용 설명", key=f"task_desc_{i}")

                risk_factors = st.multiselect("근골격계 유해위험요인", ["자세", "중량물"], key=f"risk_factors_{i}")

                # 자세 관련
                if "자세" in risk_factors:
                    st.markdown("**🧍 자세 관련 정보**")
                    shoulder_time = st.text_input("어깨 위로 팔이 올라가는 자세 - 작업시간", key=f"shoulder_time_{i}")
                    twist_time = st.text_input("몸통이 비틀리는 자세 - 작업시간", key=f"twist_time_{i}")
                    squat_time = st.text_input("쪼그려 앉는 자세 - 작업시간", key=f"squat_time_{i}")
                    repeat_total = st.text_input("반복작업 - 하루 작업시간", key=f"repeat_total_{i}")
                    repeat_heavy = st.text_input("반복작업 (4.5kg 이상) - 분당 작업횟수", key=f"repeat_heavy_{i}")

                # 중량물 관련
                tools = []
                materials = []
                if "중량물" in risk_factors:
                    st.markdown("**📦 중량물 관련 정보**")
                    num_tools = st.number_input("수공구 수", min_value=0, step=1, key=f"num_tools_{i}")
                    for j in range(int(num_tools)):
                        cols = st.columns(4)
                        tool_name = cols[0].text_input(f"수공구명 {j+1}", key=f"tool_name_{i}_{j}")
                        tool_purpose = cols[1].text_input(f"용도 {j+1}", key=f"tool_purpose_{i}_{j}")
                        tool_weight = cols[2].number_input(f"무게(kg) {j+1}", min_value=0.0, step=0.1, key=f"tool_weight_{i}_{j}")
                        tool_freq = cols[3].text_input(f"1일 작업 횟수/시간 {j+1}", key=f"tool_freq_{i}_{j}")
                        tools.append((tool_name, tool_purpose, tool_weight, tool_freq))

                    num_weights = st.number_input("중량물 수", min_value=0, step=1, key=f"num_weights_{i}")
                    for j in range(int(num_weights)):
                        cols = st.columns(3)
                        mat_name = cols[0].text_input(f"중량물명 {j+1}", key=f"mat_name_{i}_{j}")
                        mat_weight = cols[1].number_input(f"중량물 무게(kg) {j+1}", min_value=0.0, step=0.1, key=f"mat_weight_{i}_{j}")
                        mat_freq = cols[2].text_input(f"1일 작업 횟수 {j+1}", key=f"mat_freq_{i}_{j}")
                        materials.append((mat_name, mat_weight, mat_freq))

                ppe = st.multiselect("근골격계 관련 착용 보호구", ["무릎보호대", "손목보호대", "허리보호대", "각반", "기타"], key=f"ppe_{i}")

                submitted = st.form_submit_button("저장하기")
                if submitted:
                    task_units.append({
                        "소속": team,
                        "반": group_name,
                        "단위작업명": task_unit,
                        "작업자 수": unit_workers,
                        "작업자 이름": worker_names,
                        "작업형태": work_type,
                        "1일 작업시간": work_hours,
                        "자세": {
                            "어깨": shoulder_time if "자세" in risk_factors else "",
                            "몸통": twist_time if "자세" in risk_factors else "",
                            "쪼그림": squat_time if "자세" in risk_factors else "",
                            "반복전체": repeat_total if "자세" in risk_factors else "",
                            "반복무거운": repeat_heavy if "자세" in risk_factors else ""
                        },
                        "도구": tools,
                        "중량물": materials,
                        "보호구": ppe
                    })

    if task_units:
        output = io.BytesIO()
        rows = []
        for unit in task_units:
            base_row = {
                "소속": unit["소속"],
                "반": unit["반"],
                "단위작업명": unit["단위작업명"],
                "작업자 수": unit["작업자 수"],
                "작업자 이름": unit["작업자 이름"],
                "작업형태": unit["작업형태"],
                "1일 작업시간": unit["1일 작업시간"],
                "자세_어깨": unit["자세"].get("어깨"),
                "자세_몸통": unit["자세"].get("몸통"),
                "자세_쪼그림": unit["자세"].get("쪼그림"),
                "자세_반복전체": unit["자세"].get("반복전체"),
                "자세_반복무거운": unit["자세"].get("반복무거운"),
                "보호구": ", ".join(unit["보호구"])
            }
            for tool in unit["도구"]:
                rows.append({**base_row, "구분": "수공구", "명칭": tool[0], "용도": tool[1], "무게(kg)": tool[2], "작업횟수/시간": tool[3]})
            for mat in unit["중량물"]:
                rows.append({**base_row, "구분": "중량물", "명칭": mat[0], "용도": "-", "무게(kg)": mat[1], "작업횟수/시간": mat[2]})
            if not unit["도구"] and not unit["중량물"]:
                rows.append(base_row)

        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            pd.DataFrame(rows).to_excel(writer, index=False, sheet_name='작업목록')

        st.download_button(
            label="📥 작업목록표 다운로드",
            data=output.getvalue(),
            file_name=f"작업목록표_{group_name}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
