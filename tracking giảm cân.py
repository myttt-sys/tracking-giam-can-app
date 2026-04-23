import streamlit as st
import pandas as pd
import datetime
import json
import os

st.set_page_config(page_title="Theo Dõi Sức Khỏe", page_icon="🥗", layout="centered")
st.title("🥗 Theo Dõi Ăn Uống & Cân Nặng")

# ─────────────────────────────────────────────
# NHÓM THỰC PHẨM
# ─────────────────────────────────────────────
NHOM_AN = [
    "Tinh bột",
    "Đạm động vật",
    "Đạm thực vật",
    "Rau xanh",
    "Hoa quả",
    "Nước ngọt",
    "Cà phê",
    "Trà sữa",
]

SO_NAM_OPTIONS = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
SO_NAM_LABELS  = ["1/2 nắm", "1 nắm", "1.5 nắm", "2 nắm", "2.5 nắm", "3 nắm"]

# ─────────────────────────────────────────────
# LƯU / ĐỌC DỮ LIỆU
# ─────────────────────────────────────────────
DATA_FILE = "health_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"food_log": {}, "weight_log": {}, "weekly_plans": {}}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

data = load_data()

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab0, tab1, tab2, tab3 = st.tabs([
    "⚙️ Cài khẩu phần theo tuần",
    "🍽️ Nhập đồ ăn hôm nay",
    "⚖️ Nhập cân nặng",
    "📊 Biểu đồ & Lịch sử"
])

# ══════════════════════════════════════════════
# TAB 0: CÀI KHẨU PHẦN
# ══════════════════════════════════════════════
with tab0:
    st.subheader("⚙️ Cài khẩu phần mục tiêu theo tuần")
    st.caption("Tuần 1, Tuần 2... là tuần trong hành trình của bạn.")

    so_tuan = st.number_input("Tuần số", min_value=1, max_value=52, value=1, step=1)
    tuan_key = f"tuan_{so_tuan}"
    plan_hien_tai = data["weekly_plans"].get(tuan_key, {nhom: 1.0 for nhom in NHOM_AN})

    st.markdown(f"**Tuần {so_tuan} — Số nắm cho phép mỗi ngày:**")

    col1, col2 = st.columns(2)
    new_plan = {}

    for i, nhom in enumerate(NHOM_AN):
        col = col1 if i % 2 == 0 else col2
        with col:
            gia_tri_hien = plan_hien_tai.get(nhom, 1.0)
            # Tìm index gần nhất trong options
            idx = min(range(len(SO_NAM_OPTIONS)), key=lambda x: abs(SO_NAM_OPTIONS[x] - gia_tri_hien))
            chon = st.selectbox(
                nhom,
                options=SO_NAM_LABELS,
                index=idx,
                key=f"plan_{tuan_key}_{nhom}"
            )
            new_plan[nhom] = SO_NAM_OPTIONS[SO_NAM_LABELS.index(chon)]

    if st.button("💾 Lưu khẩu phần tuần này"):
        data["weekly_plans"][tuan_key] = new_plan
        save_data(data)
        st.success(f"✅ Đã lưu khẩu phần Tuần {so_tuan}!")

    if data["weekly_plans"]:
        st.markdown("---")
        st.markdown("**📋 Tóm tắt các tuần đã cài:**")
        rows = []
        for k, v in sorted(data["weekly_plans"].items(), key=lambda x: int(x[0].split("_")[1])):
            row = {"Tuần": k.replace("tuan_", "Tuần ")}
            for nhom in NHOM_AN:
                row[nhom] = f"{v.get(nhom, 0)} nắm"
            rows.append(row)
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════
# TAB 1: NHẬP ĐỒ ĂN
# ══════════════════════════════════════════════
with tab1:
    st.subheader("Hôm nay bạn ăn gì?")

    ngay_an = st.date_input("Ngày", value=datetime.date.today(), key="ngay_an")
    ngay_str = str(ngay_an)

    # Chọn tuần thủ công
    danh_sach_tuan = sorted(data["weekly_plans"].keys(), key=lambda x: int(x.split("_")[1])) if data["weekly_plans"] else []
    tuan_options = [f"Tuần {k.split('_')[1]}" for k in danh_sach_tuan]

    if tuan_options:
        tuan_chon = st.selectbox("Bạn đang ở tuần nào?", tuan_options)
        tuan_so = int(tuan_chon.split(" ")[1])
        khau_phan_tuan = data["weekly_plans"][f"tuan_{tuan_so}"]
        st.info(f"📅 Đang dùng khẩu phần **{tuan_chon}** để đánh giá.")
    else:
        tuan_chon = "Tuần 1"
        tuan_so = 1
        khau_phan_tuan = {nhom: 1.0 for nhom in NHOM_AN}
        st.warning("⚠️ Chưa cài khẩu phần. Vào tab **⚙️** để thiết lập trước nhé!")

    st.markdown("---")
    st.markdown("**Nhập số nắm từng nhóm hôm nay:**")

    if "mon_list" not in st.session_state:
        st.session_state.mon_list = {}

    col1, col2 = st.columns(2)
    for i, nhom in enumerate(NHOM_AN):
        col = col1 if i % 2 == 0 else col2
        with col:
            gia_tri = st.session_state.mon_list.get(nhom, 0.0)
            idx = min(range(len(SO_NAM_OPTIONS)), key=lambda x: abs(SO_NAM_OPTIONS[x] - gia_tri)) if gia_tri > 0 else 0
            chon = st.selectbox(
                nhom,
                options=["0 nắm"] + SO_NAM_LABELS,
                index=0 if gia_tri == 0 else idx + 1,
                key=f"nhap_{ngay_str}_{nhom}"
            )
            st.session_state.mon_list[nhom] = 0.0 if chon == "0 nắm" else SO_NAM_OPTIONS[SO_NAM_LABELS.index(chon)]

    # ── ĐÁNH GIÁ ──
    st.markdown("---")
    st.subheader(f"📋 Đánh giá so với kế hoạch {tuan_chon}")

    ket_qua = []
    for nhom in NHOM_AN:
        so_an = st.session_state.mon_list.get(nhom, 0.0)
        muc_tieu = khau_phan_tuan.get(nhom, 0.0)

        if muc_tieu == 0 and so_an == 0:
            continue
        elif muc_tieu == 0 and so_an > 0:
            ket_qua.append(("🔴", nhom, f"Không có trong kế hoạch nhưng ăn {so_an} nắm"))
        elif so_an == 0 and muc_tieu > 0:
            ket_qua.append(("⚠️", nhom, f"Chưa ăn! Mục tiêu {muc_tieu} nắm"))
        elif so_an < muc_tieu:
            ket_qua.append(("⚠️", nhom, f"Thiếu! Ăn {so_an} / mục tiêu {muc_tieu} nắm"))
        elif so_an > muc_tieu:
            ket_qua.append(("🔴", nhom, f"Vượt! Ăn {so_an} / mục tiêu {muc_tieu} nắm"))
        else:
            ket_qua.append(("✅", nhom, f"Đúng mục tiêu ({so_an} nắm) 👍"))

    for icon, nhom, nhan_xet in ket_qua:
        st.write(f"{icon} **{nhom}**: {nhan_xet}")

    loi = [r for r in ket_qua if r[0] in ("⚠️", "🔴")]
    st.markdown("---")
    if not loi:
        st.success("🎉 Hôm nay ăn đúng kế hoạch! Tuyệt vời!")
    elif len(loi) == 1:
        st.warning(f"😐 Gần ổn rồi, chỉ cần điều chỉnh **{loi[0][1]}**!")
    else:
        st.error(f"😬 Cần điều chỉnh {len(loi)} nhóm để đúng kế hoạch.")

    if st.button("💾 Lưu ngày hôm nay"):
        data["food_log"][ngay_str] = {
            "mon_list": st.session_state.mon_list,
            "tuan": tuan_so
        }
        save_data(data)
        st.success("Đã lưu!")
        st.session_state.mon_list = {}
        st.rerun()

# ══════════════════════════════════════════════
# TAB 2: NHẬP CÂN NẶNG
# ══════════════════════════════════════════════
with tab2:
    st.subheader("Nhập cân nặng hôm nay")

    ngay_cn = st.date_input("Ngày", value=datetime.date.today(), key="ngay_cn")
    can_nang = st.number_input("Cân nặng (kg)", min_value=30.0, max_value=200.0, value=60.0, step=0.1)

    if st.button("💾 Lưu cân nặng"):
        data["weight_log"][str(ngay_cn)] = can_nang
        save_data(data)
        st.success(f"Đã lưu: {ngay_cn} → {can_nang} kg")

    if data["weight_log"]:
        st.markdown("---")
        st.markdown("**Lịch sử cân nặng:**")
        df_w = pd.DataFrame(
            [(k, v) for k, v in sorted(data["weight_log"].items())],
            columns=["Ngày", "Cân nặng (kg)"]
        )
        st.dataframe(df_w, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════
# TAB 3: BIỂU ĐỒ
# ══════════════════════════════════════════════
with tab3:
    st.subheader("📊 Biểu đồ cân nặng theo thời gian")

    if len(data["weight_log"]) >= 2:
        df_w = pd.DataFrame(
            [(k, v) for k, v in sorted(data["weight_log"].items())],
            columns=["Ngày", "Cân nặng (kg)"]
        )
        df_w["Ngày"] = pd.to_datetime(df_w["Ngày"])
        df_w = df_w.set_index("Ngày")
        st.line_chart(df_w)

        dau = df_w["Cân nặng (kg)"].iloc[0]
        cuoi = df_w["Cân nặng (kg)"].iloc[-1]
        chenh = cuoi - dau
        if chenh < 0:
            st.success(f"📉 Bạn đã giảm **{abs(chenh):.1f} kg** kể từ lần đầu ghi nhận!")
        elif chenh > 0:
            st.warning(f"📈 Bạn đã tăng **{chenh:.1f} kg** kể từ lần đầu ghi nhận.")
        else:
            st.info("⚖️ Cân nặng ổn định.")
    else:
        st.info("Nhập ít nhất 2 ngày cân nặng để xem biểu đồ nhé!")

    st.markdown("---")
    st.subheader("🍽️ Lịch sử ăn uống theo tuần")

    if data["food_log"]:
        # Hiển thị bảng lịch sử
        rows = []
        for ngay, v in sorted(data["food_log"].items()):
            row = {"Ngày": ngay, "Tuần": f"Tuần {v.get('tuan', '?')}"}
            if isinstance(v.get("mon_list"), dict):
                for nhom in NHOM_AN:
                    row[nhom] = f"{v['mon_list'].get(nhom, 0)} nắm"
            rows.append(row)
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.info("Chưa có dữ liệu đồ ăn nào được lưu.")
