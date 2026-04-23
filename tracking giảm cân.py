import streamlit as st
import pandas as pd
import datetime
import json
import os

st.set_page_config(page_title="Theo Dõi Sức Khỏe", page_icon="🥗", layout="centered")
st.title("🥗 Theo Dõi Ăn Uống & Cân Nặng")

# ─────────────────────────────────────────────
# NHÓM THỰC PHẨM + ĐƠN VỊ RIÊNG
# ─────────────────────────────────────────────
NHOM_AN = [
    {"key": "tinh_bot",     "label": "Tinh bột",      "don_vi": "nắm"},
    {"key": "dam_dong_vat", "label": "Đạm động vật",  "don_vi": "nắm"},
    {"key": "dam_thuc_vat", "label": "Đạm thực vật",  "don_vi": "nắm"},
    {"key": "rau_xanh",     "label": "Rau xanh",       "don_vi": "nắm"},
    {"key": "hoa_qua",      "label": "Hoa quả",        "don_vi": "nắm"},
    {"key": "nuoc_ngot",    "label": "Nước ngọt",      "don_vi": "lon"},
    {"key": "ca_phe",       "label": "Cà phê",         "don_vi": "cốc"},
    {"key": "tra_sua",      "label": "Trà sữa",        "don_vi": "cốc"},
    {"key": "nuoc",         "label": "Nước lọc",       "don_vi": "lít"},
]

def get_options(don_vi):
    if don_vi == "nắm":
        return [0, 0.5, 1, 1.5, 2, 2.5, 3]
    elif don_vi == "lon":
        return [0, 1, 2, 3]
    elif don_vi == "cốc":
        return [0, 1, 2, 3, 4]
    elif don_vi == "lít":
        return [0, 0.5, 1, 1.5, 2, 2.5, 3]
    return [0, 1, 2, 3]

def format_label(val, don_vi):
    if val == 0:
        return f"0 {don_vi} (không)"
    if don_vi == "nắm" and val == 0.5:
        return "1/2 nắm"
    if don_vi == "lít" and val == 0.5:
        return "0.5 lít"
    return f"{val} {don_vi}"

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
    plan_hien_tai = data["weekly_plans"].get(tuan_key, {n["key"]: 1.0 for n in NHOM_AN})

    st.markdown(f"**Tuần {so_tuan} — Mục tiêu mỗi ngày:**")

    col1, col2 = st.columns(2)
    new_plan = {}

    for i, nhom in enumerate(NHOM_AN):
        col = col1 if i % 2 == 0 else col2
        with col:
            options = get_options(nhom["don_vi"])
            labels = [format_label(o, nhom["don_vi"]) for o in options]
            gia_tri_hien = plan_hien_tai.get(nhom["key"], 0)
            idx = min(range(len(options)), key=lambda x: abs(options[x] - gia_tri_hien))
            chon = st.selectbox(
                nhom["label"],
                options=labels,
                index=idx,
                key=f"plan_{tuan_key}_{nhom['key']}"
            )
            new_plan[nhom["key"]] = options[labels.index(chon)]

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
                row[nhom["label"]] = format_label(v.get(nhom["key"], 0), nhom["don_vi"])
            rows.append(row)
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════
# TAB 1: NHẬP ĐỒ ĂN
# ══════════════════════════════════════════════
with tab1:
    st.subheader("Hôm nay bạn ăn gì?")

    ngay_an = st.date_input("Ngày", value=datetime.date.today(), key="ngay_an")
    ngay_str = str(ngay_an)

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
        khau_phan_tuan = {n["key"]: 1.0 for n in NHOM_AN}
        st.warning("⚠️ Chưa cài khẩu phần. Vào tab **⚙️** để thiết lập trước nhé!")

    if "food_input" not in st.session_state:
        st.session_state.food_input = {n["key"]: {"ten": "", "so_luong": 0.0} for n in NHOM_AN}

    st.markdown("---")
    st.markdown("**Nhập thực phẩm hôm nay:**")

    for nhom in NHOM_AN:
        st.markdown(f"**{nhom['label']}**")
        col1, col2 = st.columns([2, 1])
        with col1:
            ten = st.text_input(
                "Tên",
                value=st.session_state.food_input[nhom["key"]]["ten"],
                placeholder=f"Tên {nhom['label'].lower()}...",
                key=f"ten_{ngay_str}_{nhom['key']}",
                label_visibility="collapsed"
            )
            st.session_state.food_input[nhom["key"]]["ten"] = ten
        with col2:
            options = get_options(nhom["don_vi"])
            labels = [format_label(o, nhom["don_vi"]) for o in options]
            so_luong_hien = st.session_state.food_input[nhom["key"]]["so_luong"]
            idx = min(range(len(options)), key=lambda x: abs(options[x] - so_luong_hien))
            chon = st.selectbox(
                "Số lượng",
                options=labels,
                index=idx,
                key=f"luong_{ngay_str}_{nhom['key']}",
                label_visibility="collapsed"
            )
            st.session_state.food_input[nhom["key"]]["so_luong"] = options[labels.index(chon)]

    # ── ĐÁNH GIÁ ──
    st.markdown("---")
    st.subheader(f"📋 Đánh giá so với kế hoạch {tuan_chon}")

    ket_qua = []
    for nhom in NHOM_AN:
        so_an = st.session_state.food_input[nhom["key"]]["so_luong"]
        ten = st.session_state.food_input[nhom["key"]]["ten"]
        muc_tieu = khau_phan_tuan.get(nhom["key"], 0.0)
        ten_hien = f"{nhom['label']}" + (f" ({ten})" if ten else "")
        dv = nhom["don_vi"]

        if muc_tieu == 0 and so_an == 0:
            continue
        elif muc_tieu == 0 and so_an > 0:
            ket_qua.append(("🔴", ten_hien, f"Ngoài kế hoạch — {format_label(so_an, dv)}"))
        elif so_an == 0 and muc_tieu > 0:
            ket_qua.append(("⚠️", ten_hien, f"Chưa dùng! Mục tiêu {format_label(muc_tieu, dv)}"))
        elif so_an < muc_tieu:
            ket_qua.append(("⚠️", ten_hien, f"Thiếu! {format_label(so_an, dv)} / mục tiêu {format_label(muc_tieu, dv)}"))
        elif so_an > muc_tieu:
            ket_qua.append(("🔴", ten_hien, f"Vượt! {format_label(so_an, dv)} / mục tiêu {format_label(muc_tieu, dv)}"))
        else:
            ket_qua.append(("✅", ten_hien, f"Đúng mục tiêu — {format_label(so_an, dv)} 👍"))

    for icon, ten, nhan_xet in ket_qua:
        st.write(f"{icon} **{ten}**: {nhan_xet}")

    loi = [r for r in ket_qua if r[0] in ("⚠️", "🔴")]
    st.markdown("---")
    if not loi:
        st.success("🎉 Hôm nay đúng kế hoạch! Tuyệt vời!")
    elif len(loi) == 1:
        st.warning(f"😐 Gần ổn rồi, chỉ cần điều chỉnh **{loi[0][1].split('(')[0].strip()}**!")
    else:
        st.error(f"😬 Cần điều chỉnh {len(loi)} nhóm để đúng kế hoạch.")

    if st.button("💾 Lưu hôm nay"):
        data["food_log"][ngay_str] = {
            "chi_tiet": {n["key"]: st.session_state.food_input[n["key"]] for n in NHOM_AN},
            "tuan": tuan_so
        }
        save_data(data)
        st.success("Đã lưu!")
        st.session_state.food_input = {n["key"]: {"ten": "", "so_luong": 0.0} for n in NHOM_AN}
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
    st.subheader("🍽️ Lịch sử ăn uống")

    if data["food_log"]:
        rows = []
        for ngay, v in sorted(data["food_log"].items()):
            row = {"Ngày": ngay, "Tuần": f"Tuần {v.get('tuan', '?')}"}
            chi_tiet = v.get("chi_tiet", {})
            for nhom in NHOM_AN:
                info = chi_tiet.get(nhom["key"], {})
                ten = info.get("ten", "")
                so = info.get("so_luong", 0)
                row[nhom["label"]] = f"{ten} ({format_label(so, nhom['don_vi'])})" if ten else format_label(so, nhom["don_vi"])
            rows.append(row)
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.info("Chưa có dữ liệu đồ ăn nào được lưu.")
