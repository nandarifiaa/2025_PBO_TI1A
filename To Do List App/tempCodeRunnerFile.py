# main.py

import streamlit as st
import datetime
from models.task import Task
from models.task_manager import TaskManager
from utils.file_handler import load_from_file, save_to_file
import pandas as pd
import os

DATA_FILE = 'data/tasks.json'

# Load task manager
manager = TaskManager()
saved_data = load_from_file(DATA_FILE)
manager.load_from_dict(saved_data)

st.set_page_config(page_title="Agenda Harian", layout="wide")
st.markdown("""
    <style>
        .main-title {
            font-size: 2.5rem;
            font-weight: bold;
            color: #4CAF50;
        }
        .stButton>button {
            background-color: #4CAF50;
            color: white;
        }
        .highlight {
            background-color: #333;
            padding: 10px;
            border-radius: 10px;
            color: white;
        }
        .legend {
            display: flex;
            gap: 20px;
            margin: 10px 0;
        }
        .legend span {
            display: flex;
            align-items: center;
            gap: 5px;
            font-size: 16px;
        }
        .task-container {
            background-color: #1e1e1e;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 10px;
        }
    </style>
""", unsafe_allow_html=True)

st.sidebar.title("📌 Menu Agenda")
menu = st.sidebar.radio("Pilih Halaman:", ["Tambah Agenda", "Riwayat Agenda", "Ringkasan"])

if menu == "Tambah Agenda":
    st.markdown("<div class='main-title'>📝 Tambah / Edit Agenda</div>", unsafe_allow_html=True)

    attachment = ""
    attachment_option = st.radio("Jenis Lampiran:", ["URL", "File"], horizontal=True)

    if attachment_option == "URL":
        attachment = st.text_input("Masukkan URL Lampiran", key="lampiran_url")
    elif attachment_option == "File":
        uploaded_file = st.file_uploader("Unggah File dari Komputer", type=["pdf", "png", "jpg", "jpeg", "docx", "txt"], key="lampiran_file")
        if uploaded_file:
            save_path = os.path.join("data", uploaded_file.name)
            with open(save_path, "wb") as f:
                f.write(uploaded_file.read())
            attachment = save_path

    with st.form("form_agenda"):
        col1, col2 = st.columns([2, 1])
        with col1:
            title = st.text_input("Judul Agenda*", key="judul")
            description = st.text_area("Deskripsi", key="deskripsi")
        with col2:
            deadline = st.date_input("Deadline", value=datetime.date.today(), key="deadline")

        submitted = st.form_submit_button("Simpan Agenda")

        if submitted:
            if not title:
                st.warning("Judul wajib diisi.")
            else:
                new_task = Task(title, description, False, str(deadline), attachment)
                manager.add_task(new_task)
                save_to_file(DATA_FILE, manager.to_dict())
                st.success("✅ Agenda berhasil ditambahkan.")

elif menu == "Riwayat Agenda":
    st.markdown("<div class='main-title'>📂 Riwayat Semua Agenda</div>", unsafe_allow_html=True)

    if st.button("🔄 Refresh Riwayat"):
        st.rerun()

    task_data = manager.to_dict()
    if not task_data:
        st.info("Belum ada agenda.")
    else:
        df = pd.DataFrame(task_data)
        df['Deadline'] = pd.to_datetime(df['deadline'], errors='coerce')
        df = df.sort_values(by='Deadline')

        df['Status'] = df['completed'].map(lambda x: 'Selesai' if x else 'Belum')
        df['Indikator'] = df.apply(
            lambda row: '🟢' if row['completed'] else ('🔴' if (row['Deadline'] - datetime.datetime.today()).days <= 3 else '🟡'),
            axis=1
        )

        st.markdown("""
        <div class='legend'>
            <span>🟢 Selesai</span>
            <span>🔴 Mepet Deadline</span>
            <span>🟡 Aman</span>
        </div>
        """, unsafe_allow_html=True)

        for i, row in df.iterrows():
            with st.container():
                cols = st.columns([1, 10, 1])
                with cols[0]:
                    new_status = st.checkbox("", key=f"check_{i}", value=row['completed'])
                    manager.tasks[i].completed = new_status
                with cols[1]:
                    st.markdown(f"<div class='task-container'>", unsafe_allow_html=True)
                    st.markdown(f"**{i + 1}. {row['title']}**")
                    st.write(row['description'])
                    st.write(f"📅 Deadline: {row['Deadline'].date()} | 🏷️ Status: {row['Status']} | {row['Indikator']}")

                    if row['attachment']:
                        if row['attachment'].startswith("http"):
                            st.markdown(f"🔗 [Buka Lampiran URL]({row['attachment']})")
                        elif os.path.exists(row['attachment']):
                            with open(row['attachment'], "rb") as file:
                                st.download_button(label=f"📎 Unduh {os.path.basename(row['attachment'])}", data=file, file_name=os.path.basename(row['attachment']), mime="application/octet-stream")

                    st.markdown("</div>", unsafe_allow_html=True)
                with cols[2]:
                    if st.button("🗑️", key=f"hapus_{i}"):
                        manager.remove_task(i)
                        save_to_file(DATA_FILE, manager.to_dict())
                        st.success("Agenda berhasil dihapus.")
                        st.rerun()

        save_to_file(DATA_FILE, manager.to_dict())

elif menu == "Ringkasan":
    st.markdown("<div class='main-title'>📊 Ringkasan Agenda</div>", unsafe_allow_html=True)
    tasks = manager.to_dict()
    if not tasks:
        st.info("Belum ada data agenda.")
    else:
        df = pd.DataFrame(tasks)
        df['Status'] = df['completed'].map(lambda x: 'Selesai' if x else 'Belum')
        total = len(df)
        selesai = df['Status'].value_counts().get('Selesai', 0)
        belum = df['Status'].value_counts().get('Belum', 0)

        col1, col2, col3 = st.columns(3)
        col1.metric("📋 Total Agenda", total)
        col2.metric("✅ Selesai", selesai)
        col3.metric("⏳ Belum Selesai", belum)

        st.markdown("""<div class='highlight'>Grafik batang menunjukkan jumlah agenda berdasarkan statusnya.</div>""", unsafe_allow_html=True)

        st.bar_chart(df['Status'].value_counts())