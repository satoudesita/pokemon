import streamlit as st
import sqlite3
import hashlib
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

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
    c.execute('CREATE TABLE IF NOT EXISTS study_data(username TEXT, date TEXT, study_hours REAL, score INTEGER)')
    c.execute('CREATE TABLE IF NOT EXISTS class_data(username TEXT PRIMARY KEY, class_grade TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS goals(username TEXT PRIMARY KEY, goal TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS projects(username TEXT, project_name TEXT, progress REAL)')
    c.execute('CREATE TABLE IF NOT EXISTS events(username TEXT, date TEXT, description TEXT)')  # 追加
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
def save_study_data(conn, username, date, study_hours, score):
    c = conn.cursor()
    c.execute('INSERT INTO study_data(username, date, study_hours, score) VALUES (?, ?, ?, ?)',
              (username, date, study_hours, score))
    conn.commit()

# ユーザーの学習データを取得する関数
def get_study_data(conn, username):
    c = conn.cursor()
    c.execute('SELECT date, study_hours, score FROM study_data WHERE username = ?', (username,))
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
            tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["学習データ", "日課表", "学習ゲーム", "AI", "予定","カレンダー"])

            with tab1:
                # 学習データ入力フォーム
                with st.form(key='study_form'):
                    date = st.date_input('学習日', value=datetime.now())
                    study_hours = st.number_input('学習時間（時間）', min_value=0.0, step=0.5)
                    score = st.number_input('テストのスコア', min_value=0, max_value=100, step=1)
                    submit_button = st.form_submit_button(label='データを保存')

                # データの保存処理
                if submit_button:
                    save_study_data(conn, username, date.strftime('%Y-%m-%d'), study_hours, score)
                    st.success('データが保存されました！')

                # 保存されたデータの表示
                study_data = get_study_data(conn, username)
                if study_data:
                    df = pd.DataFrame(study_data, columns=['Date', 'Study Hours', 'Score'])
                    st.write('### 現在の学習データ')
                    st.dataframe(df)

                    # グラフ描画のオプション
                    st.write('### グラフ表示')
                    plot_type = st.selectbox('表示するグラフを選択してください', ['学習時間', 'スコア'])

                    # グラフ描画
                    fig, ax = plt.subplots()
                    if plot_type == '学習時間':
                        ax.plot(df['Date'], df['Study Hours'], marker='o')
                        ax.set_title('日別学習時間の推移')
                        ax.set_xlabel('日付')
                        ax.set_ylabel('学習時間（時間）')
                    elif plot_type == 'スコア':
                        ax.plot(df['Date'], df['Score'], marker='o', color='orange')
                        ax.set_title('日別スコアの推移')
                        ax.set_xlabel('日付')
                        ax.set_ylabel('スコア')
                    st.pyplot(fig)
                else:
                    st.write('データがまだ入力されていません。')

            with tab2:
                class_message = get_class_message(class_grade_input)
                st.write(f"日課表: {class_message}")

            with tab3:
                st.subheader("学習ゲーム")
                st.text('素因数分解')
                st.link_button("素因数分解", "https://shoblog.iiyan.net/")
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
                
            with tab4:
                st.link_button('a', "https://chatgpt.com/")
                
            with tab5:
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
                    st.dataframe(project_df)

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
            with tab6:
                with tab6:
                    st.subheader("カレンダーイベント管理")
    
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
                        delete_all_users(conn)
                        st.success("すべてのユーザーのデータが削除されました。")
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

    # コネクションを閉じる
    conn.close()

if __name__ == '__main__':
    main()
