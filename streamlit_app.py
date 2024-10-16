import streamlit as st
from streamlit_autorefresh import st_autorefresh
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

# チャット履歴を削除する関数
def delete_all_messages(conn):
    c = conn.cursor()
    c.execute('DELETE FROM messages')
    conn.commit()

def create_tables(con):
    cc = con.cursor()
    cc.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    con.commit()
 
# テーブルを作成（存在しない場合）
def create_user_table(conn):
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT PRIMARY KEY, password TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS user_data(username TEXT PRIMARY KEY, text_content TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS study_data(username TEXT, date TEXT, study_hours REAL, score INTEGER, subject TEXT)')  # subject列を追加
    c.execute('CREATE TABLE IF NOT EXISTS class_data(username TEXT PRIMARY KEY, class_grade TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS goals(username TEXT PRIMARY KEY, goal TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS projects(username TEXT, project_name TEXT, progress REAL)')
    c.execute('CREATE TABLE IF NOT EXISTS events(username TEXT, date TEXT, description TEXT)')
    conn.commit()
 
# イベントを保存する関数
def save_event(conn, username, date, description):
    c = conn.cursor()
    c.execute('INSERT INTO events(username, date, description) VALUES (?, ?, ?)',
              (username, date, description))
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
    c.execute('INSERT INTO study_data(username, date, study_hours, score, subject) VALUES (?, ?, ?, ?, ?)',
              (username, date, study_hours, score, subject))
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
 
# Excelデータを読み込む関数
def load_timetable(sheet_number):
    df = pd.read_excel('日課表.xlsx', sheet_name=sheet_number)
    return df
 
# クラスに基づいてシート番号を決定する関数
def get_sheet_number(class_grade):
    sheet_mapping = {
        "1.1": 0, "1.2": 1, "1.3": 2, "1.4": 3, "1.5": 4,"1.6": 5, "1.7": 6, "1.8": 7,
        "2.1": 8, "2.2": 9,"2.3": 10, "2.4": 11, "2.5": 12, "2.6": 13, "2.7": 14,"2.3": 10, "2.4": 11, "2.5": 12, "2.6": 13, "2.7": 14,"2.3": 15, "2.8": 16,
        "3.1": 17, "3.2": 18, "3.3": 19, "3.4": 20, "3.5": 21,"3.6": 22, "3.7": 23,"3.8": 24, "3.9": 25,
    }
    return sheet_mapping.get(class_grade, -1)  # -1 は無効なクラスを示す
 
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
    c.execute('INSERT INTO projects(username, project_name, progress) VALUES (?, ?, ?)',
              (username, project_name, project_progress))
    conn.commit()
 
# 既存のプロジェクトを取得する関数
def get_projects(conn, username):
    c = conn.cursor()
    c.execute('SELECT project_name, progress FROM projects WHERE username = ?', (username,))
    return c.fetchall()
 
# プロジェクト進捗を更新する関数
def update_project_progress(conn, username, project_name, new_progress):
    c = conn.cursor()
    c.execute('UPDATE projects SET progress = ? WHERE username = ? AND project_name = ?',
              (new_progress, username, project_name))
    conn.commit()
 
# プロジェクトを削除する関数
def delete_project(conn, username, project_name):
    c = conn.cursor()
    c.execute('DELETE FROM projects WHERE username = ? AND project_name = ?', (username, project_name))
    conn.commit()
 
def main():
    st.title("モチベーション向上")
   
    menu = ["ホーム", "ログイン", "サインアップ","使い方"]
    choice = st.sidebar.selectbox("メニュー", menu)
 
    # データベースに接続
    conn = sqlite3.connect('database.db')
    create_user_table(conn)
 
    if choice == "ホーム":
        st.subheader("ホーム画面")
        st.subheader("左上の矢印を押してください")
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
            tab1, tab2, tab3, tab4, tab5, tab6 ,tab7= st.tabs(["学習データ", "AI","aa" ,"学習ゲーム", "日課表", "予定", "カレンダー"])
 
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
                    if st.button("学習、スコアデータ表示"):
                        st.dataframe(df)
 
                   
                    # マルチセレクトで教科を選択
                    selected_subjects = st.multiselect('教科を選択してください', df['教科'].unique())
 
                 # グラフ表示
                    gurafu = st.selectbox('グラフ', ['学習時間', 'スコア'])
 
                    # figを初期化
                    fig = go.Figure()
 
                    if selected_subjects:
                        filtered_df = df[df['教科'].isin(selected_subjects)]
 
                        for subject in selected_subjects:
                            subject_df = filtered_df[filtered_df['教科'] == subject]
       
                            if gurafu == '学習時間':
                                fig.add_trace(go.Scatter(
                                    x=subject_df['日付'],
                                    y=subject_df['学習時間'],
                                    mode='lines+markers',
                                    name=subject  # 教科名を表示
                                ))
                                fig.update_layout(title='選択された教科の学習時間のグラフ',
                                                xaxis_title='日付',
                                                    yaxis_title='学習時間（時間）')
                            elif gurafu == 'スコア':
                                fig.add_trace(go.Scatter(
                                    x=subject_df['日付'],
                                    y=subject_df['スコア'],
                                    mode='lines+markers',
                                    name=subject  # 教科名を表示
                                ))
                                fig.update_layout(title='選択された教科のスコアのグラフ',
                                                xaxis_title='日付',
                                                yaxis_title='スコア')
 
                        st.plotly_chart(fig)
                    else:
                        st.write("教科が選択されていません。")
 
           
            with tab5:
                st.subheader("日課表")
 
                # クラスをもとに日課表を取得
                sheet_number = get_sheet_number(class_grade_input)
                if sheet_number != -1:
                    timetable = load_timetable(sheet_number)
                    st.dataframe(timetable)
                else:
                    st.warning("無効なクラス/学年が入力されました")
            with tab4:
                st.subheader("学習ゲーム")
                st.text('素因数分解')
                st.link_button("素因数分解", "https://sukepc0824.github.io/factorization/")
                st.text('マスmatics')
                st.link_button("マスmatics", "https://sukepc0824.github.io/masu-matics/")
                st.text('英単語')
                st.link_button("英単語", "https://gatieitanngo-jjmvn8dyjndf9ow9hunxfj.streamlit.app/")
                st.text('歴史')
                st.link_button("歴史", "https://satoudesta31080-cjwty9bid5qndqsqogzjbq.streamlit.app/")
                st.text('四字熟語')
                st.link_button("四字熟語", "https://iqkxbsojo8sg5sddsolvqp.streamlit.app/")
                st.text('地理')
                st.link_button("地理", "https://xquamsmdle8xatfl7df6my.streamlit.app/")
                st.text('生物')
                st.link_button("生物", "https://fobegkereok6v9z6ra2bpb.streamlit.app/")
               
            with tab2:
                if st.button("使い方"):
                    st.text("説明")
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
                    height=400 # 高さを調整
                )
 
               
            with tab6:
                st.subheader("予定メモ")
 
                project_name = st.text_input("予定を入力してください")
                project_progress = st.number_input("進捗 (%)", min_value=0.0, max_value=100.0, step=1.0)
 
                if st.button("予定を追加"):
                    if project_name:
                        save_project(conn, username, project_name, project_progress)
                        st.success(f"予定 '{project_name}' を追加しました！")
                    else:
                        st.warning("予定を入力してください。")
 
                # 既存のプロジェクトを表示
                st.write("### 予定")
                projects = get_projects(conn, username)
                if projects:
                    project_df = pd.DataFrame(projects, columns=["予定", "進捗"])
                    if st.button("データ"):
                        st.dataframe(project_df)
 
                    # 進捗の横棒グラフを表示
                    fig = go.Figure()
                    for project in projects:
                        # 進捗の値を100%スケーリング
                        progress_value = project[1]
                        fig.add_trace(go.Bar(
                            x=[progress_value],  # 進捗
                            y=[project[0]],  # 予定名
                            orientation='h',  # 横棒
                            name=project[0],
                            text=f"{progress_value}%",  # テキストラベル
                            textposition='inside'  # テキストの位置
                        ))
 
                    fig.update_layout(
                        title='プロジェクト進捗 (100%基準)',
                        xaxis_title='進捗 (%)',
                        yaxis_title='予定',
                        xaxis=dict(range=[0, 100]),  # X軸の範囲を0から100に設定
                        barmode='group'
                    )
                    st.plotly_chart(fig)
 
                    # 進捗更新機能
                    project_to_update = st.selectbox("進捗を更新する予定", [p[0] for p in projects])
                    new_progress = st.number_input("新しい進捗 (%)", min_value=0.0, max_value=100.0, step=1.0)
 
                    if st.button("進捗を更新"):
                        update_project_progress(conn, username, project_to_update, new_progress)
                        st.success(f"予定 '{project_to_update}' の進捗を更新しました！")
 
                    # プロジェクト削除機能
                    project_to_delete = st.selectbox("削除するプロジェクト", [p[0] for p in projects])
                    if st.button("削除"):
                        delete_project(conn, username, project_to_delete)
                        st.success(f"予定 '{project_to_delete}' が削除されました！")
                else:
                    st.write("現在、予定はありません。予定があれば追加してください。")
            with tab3:  # Chat Tab
                # データベースに接続
                con = sqlite3.connect('chat.db')
                cc = con.cursor()

                # メッセージテーブルの作成
                cc.execute('''CREATE TABLE IF NOT EXISTS messages
                            (id INTEGER PRIMARY KEY AUTOINCREMENT, user TEXT, message TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
                con.commit()

                # タイトル
                st.title("オープンチャットアプリ")

                # ページのリフレッシュを3秒ごとに設定
                st_autorefresh(interval=3000)  # 3秒ごとにリフレッシュ

                # ユーザーのメッセージ入力
                user_msg = st.text_input("メッセージを入力してください")

                # 送信ボタンを追加
                if st.button("送信"):
                    if user_msg and 'username' in st.session_state:  # ユーザー名が存在するか確認
                        cc.execute("INSERT INTO messages (user, message) VALUES (?, ?)", (st.session_state['username'], user_msg))
                        con.commit()
                        st.success("メッセージが送信されました！")
                    else:
                        st.warning("メッセージが空です。")

                # メッセージの読み込み
                cc.execute("SELECT user, message FROM messages ORDER BY timestamp DESC")
                messages = cc.fetchall()

                # メッセージ表示
                for message in messages:
                    st.write(f"{message[0]}: {message[1]}")  # ユーザー名とメッセージを表示




            with tab7:
                st.subheader("カレンダー")
                selected_date = st.date_input("イベントの日付を選択してください", datetime.now())
                event_description = st.text_input("イベントの説明を入力してください")
 
                # イベントを追加するボタン
                if st.button("イベントを追加"):
                    save_event(conn, username, selected_date.strftime('%Y-%m-%d'), event_description)
                    st.success("イベントが追加されました！")
                # 選択した日のイベントを表示
                st.write(f"### {selected_date.strftime('%Y-%m-%d')} のイベント")
                events = get_events(conn, username, selected_date.strftime('%Y-%m-%d'))
   
                if events:
                    for event in events:
                        st.write(f"- {event[0]}")
                else:
                    st.write("この日にイベントはありません。")
    elif choice == "ログイン":
        st.subheader("ログイン画面です")
        username = st.sidebar.text_input("ユーザー名を入力してください")
        password = st.sidebar.text_input("パスワードを入力してください", type='password')

        if st.sidebar.checkbox("ログイン"):
            result = login_user(conn, username, make_hashes(password))

            if result:
                st.session_state['username'] = username
                st.success("{}さんでログインしました".format(username))
                st.success('ホーム画面に移動して下さい')

                if username == "さとうはお":
                    st.success("こんにちは、佐藤葉緒さん！")

                    if st.button("すべてのユーザーのデータを削除"):
                        delete_all_users(conn)  # チャット履歴を削除する関数を呼び出す
                        st.success("すべてのユーザーのデータが削除されました。")

                    if st.button("すべてのチャット履歴を削除"):
                        delete_all_messages(con)
                        st.success("すべてのチャット履歴が削除されました！")
            else:
                st.warning("ユーザー名かパスワードが間違っています")


 
    elif choice == "サインアップ":
        st.subheader("新しいアカウントを作成します")
        new_user = st.text_input("ユーザー名を入力してください")
        new_password = st.text_input("パスワードを入力してください", type='password')
 
        if st.button("サインアップ"):
            if check_user_exists(conn, new_user):
                st.error("このユーザー名は既に使用されています。別のユーザー名を選んでください。")
            else:
                try:
                    add_user(conn, new_user, make_hashes(new_password))
                    st.success("アカウントの作成に成功しました")
                    st.info("ログイン画面からログインしてください")
                except Exception as e:
                    st.error(f"アカウントの作成に失敗しました: {e}")
    
    if choice == "使い方":
        st.text("d")
 
    # コネクションを閉じる
    conn.close()
 
if __name__ == '__main__':
    main()
    