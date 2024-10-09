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
    conn.commit()

# 新しいユーザーを追加する関数
def add_user(conn, username, password):
    c = conn.cursor()
    c.execute('INSERT INTO userstable(username, password) VALUES (?, ?)', (username, password))
    conn.commit()

# クラスデータを追加する関数
def add_class_data(conn, username, class_grade):
    c = conn.cursor()
    c.execute('INSERT OR REPLACE INTO class_data(username, class_grade) VALUES (?, ?)', (username, class_grade))
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

# ユーザーのすべてのデータを削除する関数
def delete_user_data(conn, username):
    c = conn.cursor()
    c.execute('DELETE FROM study_data WHERE username = ?', (username,))
    c.execute('DELETE FROM class_data WHERE username = ?', (username,))
    c.execute('DELETE FROM user_data WHERE username = ?', (username,))
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

            # クラスや学年の入力フォーム
            class_grade = get_class_data(conn, username)  # データベースからクラスを取得
            class_grade_input = st.sidebar.text_input("クラス/学年を入力してください", value=class_grade)
            
            if st.sidebar.button("クラス/学年を変更"):
                if class_grade_input:
                    add_class_data(conn, username, class_grade_input)
                    st.sidebar.success('クラス/学年が変更されました！')
                else:
                    st.sidebar.warning('クラス/学年を入力してください。')

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

                # 現在のユーザーのすべてのデータ削除ボタン
                if st.button("すべてのデータを削除"):
                    delete_user_data(conn, username)
                    st.success("すべてのデータが削除されました。")
            else:
                st.write('データがまだ入力されていません。')
        else:
            st.warning("ログインしていません。")

    elif choice == "ログイン":
        st.subheader("ログイン画面です")

        username = st.sidebar.text_input("ユーザー名を入力してください")
        password = st.sidebar.text_input("パスワードを入力してください", type='password')

        if st.sidebar.checkbox("ログイン"):
            result = login_user(conn, username, make_hashes(password))

            if result:
                st.session_state['username'] = username
                st.success("{}さんでログインしました".format(username))
                
                # 特定のユーザー名に対するメッセージ
                if username == "佐藤葉緒":
                    st.success("こんにちは、佐藤葉緒さん！特別なメッセージをお届けします。")
            else:
                st.warning("ユーザー名かパスワードが間違っています")

    elif choice == "サインアップ":
        st.subheader("新しいアカウントを作成します")
        new_user = st.text_input("ユーザー名を入力してください")
        new_password = st.text_input("パスワードを入力してください", type='password')

        if st.button("サインアップ"):
            # ユーザー名がすでに存在するか確認
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
