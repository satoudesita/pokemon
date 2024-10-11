import streamlit as st
import sqlite3
import hashlib
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import streamlit.components.v1 as components

# パスワードをハッシュ化する関数
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# ハッシュ化されたパスワードをチェックする関数
def check_hashes(password, hashed_text):
    return make_hashes(password) == hashed_text

# テーブルを作成（存在しない場合）
def create_user_table(conn):
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT PRIMARY KEY, password TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS user_data(username TEXT PRIMARY KEY, text_content TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS study_data(username TEXT, date TEXT, study_hours REAL, score INTEGER, subject TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS class_data(username TEXT PRIMARY KEY, class_grade TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS goals(username TEXT PRIMARY KEY, goal TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS projects(username TEXT, project_name TEXT, progress REAL)')
    c.execute('CREATE TABLE IF NOT EXISTS events(username TEXT, date TEXT, description TEXT)')
    conn.commit()

# イベントを保存する関数
def save_event(conn, username, date, description):
    c = conn.cursor()
    c.execute('INSERT INTO events(username, date, description) VALUES (?, ?, ?)', (username, date, description))
    conn.commit()

# イベントデータを取得する関数
def get_events(conn, username, date):
    c = conn.cursor()
    c.execute('SELECT description FROM events WHERE username = ? AND date = ?', (username, date))
    return c.fetchall()

# 新しいユーザーを追加する関数
def add_user(conn, username, password):
    c = conn.cursor()
    c.execute('INSERT INTO userstable(username, password) VALUES (?, ?)', (username, password))
    conn.commit()

# クラスデータを追加または更新する関数
def update_class_data(conn, username, class_grade):
    c = conn.cursor()
    c.execute('DELETE FROM class_data WHERE username = ?', (username,))
    c.execute('INSERT INTO class_data(username, class_grade) VALUES (?, ?)', (username, class_grade))
    conn.commit()

# ユーザー名の存在を確認する関数
def check_user_exists(conn, username):
    c = conn.cursor()
    c.execute('SELECT * FROM userstable WHERE username = ?', (username,))
    return c.fetchone() is not None

# ユーザーをログインさせる関数
def login_user(conn, username, password):
    c = conn.cursor()
    c.execute('SELECT * FROM userstable WHERE username = ? AND password = ?', (username, password))
    return c.fetchall()

# 学習データを保存する関数
def save_study_data(conn, username, date, study_hours, score, subject):
    c = conn.cursor()
    c.execute('INSERT INTO study_data(username, date, study_hours, score, subject) VALUES (?, ?, ?, ?, ?)', (username, date, study_hours, score, subject))
    conn.commit()

# ユーザーの学習データを取得する関数
def get_study_data(conn, username):
    c = conn.cursor()
    c.execute('SELECT date, study_hours, score, subject FROM study_data WHERE username = ?', (username,))
    return c.fetchall()

# クラスデータを取得する関数
def get_class_data(conn, username):
    c = conn.cursor()
    c.execute('SELECT class_grade FROM class_data WHERE username = ?', (username,))
    data = c.fetchone()
    return data[0] if data else ""

# クラス学年に応じたメッセージを取得する関数
def get_class_message(class_grade):
    messages = {
        "1.1": "あ", "1.2": "い", "1.3": "う", "1.4": "え", "1.5": "お",
        "1.6": "か", "1.7": "き", "1.8": "く", "1.9": "け", "2.0": "こ",
        "2.1": "さ", "2.2": "し", "2.3": "す", "2.4": "せ", "2.5": "そ",
        "2.6": "た", "2.7": "ち", "2.8": "つ", "2.9": "て", "3.0": "と",
        "3.1": "な", "3.2": "に", "3.3": "ぬ", "3.4": "ね", "3.5": "の",
        "3.6": "は", "3.7": "ひ", "3.8": "ふ", "3.9": "へ",
    }
    return messages.get(class_grade, "不明な学年")

# 目標を保存する関数
def save_goal(conn, username, goal):
    c = conn.cursor()
    c.execute('REPLACE INTO goals(username, goal) VALUES (?, ?)', (username, goal))
    conn.commit()

# 指定したユーザーのデータを削除する関数
def delete_user_data(conn, username):
    c = conn.cursor()
    c.execute('DELETE FROM study_data WHERE username = ?', (username,))
    c.execute('DELETE FROM class_data WHERE username = ?', (username,))
    c.execute('DELETE FROM user_data WHERE username = ?', (username,))
    c.execute('DELETE FROM goals WHERE username = ?', (username,))
    c.execute('DELETE FROM projects WHERE username = ?', (username,))
    conn.commit()

# すべてのユーザーのデータを削除する関数
def delete_all_users(conn):
    c = conn.cursor()
    c.execute('DELETE FROM userstable')
    c.execute('DELETE FROM study_data')
    c.execute('DELETE FROM class_data')
    c.execute('DELETE FROM user_data')
    c.execute('DELETE FROM goals')
    c.execute('DELETE FROM projects')
    conn.commit()

# プロジェクトを保存する関数
def save_project(conn, username, project_name, project_progress):
    c = conn.cursor()
    c.execute('INSERT INTO projects(username, project_name, progress) VALUES (?, ?, ?)', (username, project_name, project_progress))
    conn.commit()

# 既存のプロジェクトを取得する関数
def get_projects(conn, username):
    c = conn.cursor()
    c.execute('SELECT project_name, progress FROM projects WHERE username = ?', (username,))
    return c.fetchall()

# プロジェクト進捗を更新する関数
def update_project_progress(conn, username, project_name, new_progress):
    c = conn.cursor()
    c.execute('UPDATE projects SET progress = ? WHERE username = ? AND project_name = ?', (new_progress, username, project_name))
    conn.commit()

# プロジェクトを削除する関数
def delete_project(conn, username, project_name):
    c = conn.cursor()
    c.execute('DELETE FROM projects WHERE username = ? AND project_name = ?', (username, project_name))
    conn.commit()

def main():
    st.title("ログイン機能テスト")
   
    menu = ["ホーム", "ログイン", "サインアップ"]
    choice = st.sidebar.selectbox("メニュー", menu)

    # データベースに接続
    conn = sqlite3.connect('database.db')
    create_user_table(conn)

    if choice == "ホーム":
        st.subheader("ホーム画面です")
        if 'username' in st.session_state:
            username = st.session_state['username']
            st.write(f"ようこそ、{username}さん！")
 
            class_grade = get_class_data(conn, username)
            class_grade_input = st.sidebar.text_input("クラス/学年を入力してください（例１年１組→1.1）", value=class_grade)
 
            if st.sidebar.button("クラス/学年を変更"):
                if class_grade_input:
                    update_class_data(conn, username, class_grade_input)
                    st.sidebar.success('クラス/学年が変更されました！')
                else:
                    st.sidebar.warning('クラス/学年を入力してください。')
 
            # タブによる学習データ、日課表、学習ゲーム、AIの表示
            tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["学習データ", "日課表", "学習ゲーム", "AI", "予定", "カレンダー"])
 
            with tab1:
                # 学習データ入力フォーム
                with st.form(key='study_form'):
                    date = st.date_input('学習日', value=datetime.now())
                    study_hours = st.number_input('学習時間（時間）', min_value=0.0, step=0.5)
                    score = st.number_input('テストのスコア', min_value=0, max_value=100, step=1)
                    subject = st.selectbox('教科', ['数学', '英語', '理科', '社会', '国語'])
                    submit_button = st.form_submit_button(label='学習データを保存')
                    if submit_button:
                        save_study_data(conn, username, date, study_hours, score, subject)
                        st.success('学習データが保存されました！')

                # 学習データの表示
                study_data = get_study_data(conn, username)
                if study_data:
                    df = pd.DataFrame(study_data, columns=['日付', '学習時間', 'スコア', '教科'])
                    st.dataframe(df)
                    # グラフ表示
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=df['日付'], y=df['学習時間'], mode='lines+markers', name='学習時間'))
                    fig.add_trace(go.Scatter(x=df['日付'], y=df['スコア'], mode='lines+markers', name='スコア'))
                    fig.update_layout(title='学習データのグラフ', xaxis_title='日付', yaxis_title='値')
                    st.plotly_chart(fig)
                else:
                    st.write("学習データがありません。")

            with tab2:
                # 日課表機能の実装
                st.write("日課表の機能を実装予定です。")

            with tab3:
                # 学習ゲーム機能の実装
                st.write("学習ゲームの機能を実装予定です。")

            with tab4:
                # AI機能の実装
                st.write("AIの機能を実装予定です。")

            with tab5:
                # 予定管理
                st.subheader("予定の管理")
                date_input = st.date_input('予定日', value=datetime.now())
                description_input = st.text_input("予定内容")
                if st.button("予定を保存"):
                    save_event(conn, username, date_input, description_input)
                    st.success("予定が保存されました。")

                # 予定の表示
                events = get_events(conn, username, date_input)
                if events:
                    st.write("予定:")
                    for event in events:
                        st.write(event[0])
                else:
                    st.write("この日の予定はありません。")

            with tab6:
                # カレンダー機能の実装
                st.write("カレンダーの機能を実装予定です。")

            # Chatbase チャットボットを埋め込む
            components.html(
                """
                <script>
                    window.embeddedChatbotConfig = {
                        chatbotId: "uZHqK1b61C7QU9eF1MmxO",
                        domain: "www.chatbase.co"
                    }
                </script>
                <script
                    src="https://www.chatbase.co/embed.min.js"
                    chatbotId="uZHqK1b61C7QU9eF1MmxO"
                    domain="www.chatbase.co"
                    defer>
                </script>
                """,
                height=500  # 高さを調整
            )

        else:
            st.warning("ログインしてください。")

    elif choice == "ログイン":
        st.subheader("ログイン")
        username = st.text_input("ユーザー名")
        password = st.text_input("パスワード", type='password')
        if st.button("ログイン"):
            if login_user(conn, username, make_hashes(password)):
                st.session_state['username'] = username
                st.success(f"ようこそ、{username}さん！")
                st.experimental_rerun()
            else:
                st.error("ユーザー名またはパスワードが間違っています。")

    elif choice == "サインアップ":
        st.subheader("サインアップ")
        new_username = st.text_input("新しいユーザー名")
        new_password = st.text_input("新しいパスワード", type='password')
        if st.button("サインアップ"):
            if check_user_exists(conn, new_username):
                st.error("このユーザー名はすでに使用されています。")
            else:
                add_user(conn, new_username, make_hashes(new_password))
                st.success("アカウントが作成されました！ログインしてください。")

    # コネクションを閉じる
    conn.close()

if __name__ == '__main__':
    main()