import streamlit as st
import numpy as np
import random
from PIL import Image

# 定数設定
CELL_SIZE = 20
DEFAULT_MAZE_SIZE = 31  # デフォルトの迷路サイズ
DISPLAY_SIZE = 800  # Streamlitでの表示サイズ
MIN_OBSTACLE_COUNT = 2  # 最小障害物数
MAX_OBSTACLE_COUNT = 12  # 最大障害物数
NUM_YELLOW_CELLS = 3  # 黄色にするセルの数

# 障害物の数を決定する関数
def calculate_obstacle_count(size):
    # サイズに応じて障害物の数を調整
    return min(MAX_OBSTACLE_COUNT, max(MIN_OBSTACLE_COUNT, size // 10))

# 迷路生成
def generate_maze(size):
    maze = np.ones((size, size), dtype=int)
    stack = []
    visited = np.zeros((size, size), dtype=bool)
    
    def is_valid(x, y):
        return 0 <= x < size and 0 <= y < size and not visited[x, y]
    
    def carve_path(start_x, start_y):
        stack.append((start_x, start_y))
        maze[start_x, start_y] = 0
        visited[start_x, start_y] = True
        
        while stack:
            x, y = stack[-1]
            neighbors = [(x-2, y), (x+2, y), (x, y-2), (x, y+2)]
            random.shuffle(neighbors)
            
            carved = False
            for nx, ny in neighbors:
                if is_valid(nx, ny):
                    maze[(x + nx) // 2, (y + ny) // 2] = 0
                    maze[nx, ny] = 0
                    visited[nx, ny] = True
                    stack.append((nx, ny))
                    carved = True
                    break
            if not carved:
                stack.pop()
    
    # スタート位置
    start_x, start_y = 1, 1
    carve_path(start_x, start_y)
    
    # ゴール位置
    goal_x, goal_y = size - 2, size - 2
    maze[goal_x, goal_y] = 0
    
    return maze, (start_x, start_y), (goal_x, goal_y)

# 障害物の生成
def generate_obstacles(maze, num_obstacles):
    size = maze.shape[0]
    obstacles = []
    
    for _ in range(num_obstacles):
        while True:
            x = random.randint(1, size - 2)
            y = random.randint(1, size - 2)
            if maze[y, x] == 0 and (x, y) not in obstacles:
                obstacles.append((x, y))
                break
    
    return obstacles

# 障害物の移動
def move_obstacles(obstacles, maze):
    new_obstacles = []
    size = maze.shape[0]
    
    for (x, y) in obstacles:
        direction = random.choice([(0, 1), (1, 0), (0, -1), (-1, 0)])
        new_x = x + direction[0]
        new_y = y + direction[1]
        
        if 0 <= new_x < size and 0 <= new_y < size and maze[new_y, new_x] == 0:
            new_obstacles.append((new_x, new_y))
        else:
            new_obstacles.append((x, y))  # 移動できない場合は元の位置にとどまる
    
    return new_obstacles

# 黄色にするセルの位置を決定する関数
def get_random_yellow_positions(maze, num_positions):
    size = maze.shape[0]
    free_cells = [(x, y) for x in range(size) for y in range(size) if maze[y, x] == 0]
    return random.sample(free_cells, min(num_positions, len(free_cells)))

# 簡単な問題を生成する関数
def generate_problem():
    # 固定の問題と答え
    problem = "1 + 1 = ?"
    answer = 2
    return problem, answer

# 迷路の描画
def draw_maze(maze, player_pos, goal_pos, obstacles, yellow_cells):
    maze_image = np.ones((maze.shape[0], maze.shape[1], 3), dtype=np.uint8) * 255  # 背景は白
    maze_image[maze == 1] = [0, 0, 0]  # 壁を黒で描画
    maze_image[goal_pos[1], goal_pos[0]] = [255, 0, 0]  # ゴールを赤で描画
    maze_image[player_pos[1], player_pos[0]] = [0, 255, 0]  # プレイヤーを緑で描画

    # 2〜3個のセルを黄色に変更
    for (x, y) in yellow_cells:
        maze_image[y, x] = [255, 255, 0]  # 黄色で描画

    for (x, y) in obstacles:
        maze_image[y, x] = [0, 0, 255]  # 障害物を青で描画

    # 画像サイズ調整
    pil_image = Image.fromarray(maze_image)
    pil_image = pil_image.resize((DISPLAY_SIZE, DISPLAY_SIZE), Image.NEAREST)
    
    return pil_image

# Streamlitアプリ
def main():
    st.title("迷路ゲーム")

    # スライダーで迷路サイズを選択
    maze_size = st.slider("迷路のサイズ", min_value=11, max_value=101, step=2, value=DEFAULT_MAZE_SIZE)

    # ステートを使って迷路の位置を保持
    if 'player_pos' not in st.session_state or 'maze_size' not in st.session_state or st.session_state.maze_size != maze_size:
        st.session_state.maze_size = maze_size
        st.session_state.player_pos = [1, 1]
        st.session_state.start_pos = (1, 1)
        st.session_state.maze, st.session_state.start_pos, st.session_state.goal_pos = generate_maze(maze_size)
        num_obstacles = calculate_obstacle_count(maze_size)
        st.session_state.obstacles = generate_obstacles(st.session_state.maze, num_obstacles)
        st.session_state.yellow_cells = get_random_yellow_positions(st.session_state.maze, NUM_YELLOW_CELLS)
        st.session_state.previous_player_pos = list(st.session_state.player_pos)  # プレイヤーの位置を記録
    
    maze = st.session_state.maze
    player_pos = st.session_state.player_pos
    goal_pos = st.session_state.goal_pos
    obstacles = st.session_state.obstacles
    yellow_cells = st.session_state.yellow_cells

    # 黄色のマスに到達したかどうかを確認
    if tuple(player_pos) in yellow_cells:
        # 問題を生成
        problem, answer = generate_problem()
        st.session_state.current_problem = problem
        st.session_state.problem_answer = answer

        # 問題を表示
        user_answer = st.text_input("問題に答えてください:", "")
        if user_answer.isdigit() and int(user_answer) == st.session_state.problem_answer:
            st.write("正解です！")
            st.session_state.yellow_cells.remove(tuple(player_pos))  # 問題が解けたらその黄色マスを消去
            st.session_state.previous_player_pos = list(player_pos)  # 正解した場合もプレイヤー位置を更新
        elif user_answer and int(user_answer) != st.session_state.problem_answer:
            st.write("不正解です。もう一度試してください。")
            st.session_state.player_pos = st.session_state.previous_player_pos  # 不正解の場合、元の位置に戻す
        
        # 正解するまでゲームを一時停止
        if tuple(player_pos) in yellow_cells:
            st.stop()
    
    # 障害物の移動
    st.session_state.obstacles = move_obstacles(st.session_state.obstacles, maze)
    obstacles = st.session_state.obstacles

    # 再生成ボタン
    if st.button("迷路を再生成"):
        st.session_state.player_pos = [1, 1]
        st.session_state.maze, st.session_state.start_pos, st.session_state.goal_pos = generate_maze(maze_size)
        num_obstacles = calculate_obstacle_count(maze_size)
        st.session_state.obstacles = generate_obstacles(st.session_state.maze, num_obstacles)
        st.session_state.yellow_cells = get_random_yellow_positions(st.session_state.maze, NUM_YELLOW_CELLS)
        st.session_state.previous_player_pos = list(st.session_state.player_pos)
    
    # 移動処理
    def move_left():
        if maze[player_pos[1], player_pos[0] - 1] == 0:
            player_pos[0] -= 1
        st.session_state.player_pos = player_pos

    def move_right():
        if maze[player_pos[1], player_pos[0] + 1] == 0:
            player_pos[0] += 1
        st.session_state.player_pos = player_pos

    def move_up():
        if maze[player_pos[1] - 1, player_pos[0]] == 0:
            player_pos[1] -= 1
        st.session_state.player_pos = player_pos

    def move_down():
        if maze[player_pos[1] + 1, player_pos[0]] == 0:
            player_pos[1] += 1
        st.session_state.player_pos = player_pos

    # ボタンの表示
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("左"):
            move_left()
    with col2:
        if st.button("上"):
            move_up()
    with col3:
        if st.button("右"):
            move_right()
    
    with col2:
        if st.button("下"):
            move_down()

    # ゴールに到達したか確認
    if player_pos == list(goal_pos):
        st.write("ゴールに到達しました!")

    # 障害物に触れたか確認
    if tuple(player_pos) in obstacles:
        st.write("ゲームオーバー！障害物に触れました。")
        st.session_state.player_pos = [1, 1]
        st.session_state.maze, st.session_state.start_pos, st.session_state.goal_pos = generate_maze(maze_size)
        num_obstacles = calculate_obstacle_count(maze_size)
        st.session_state.obstacles = generate_obstacles(st.session_state.maze, num_obstacles)
        st.session_state.yellow_cells = get_random_yellow_positions(st.session_state.maze, NUM_YELLOW_CELLS)
        st.session_state.previous_player_pos = list(st.session_state.player_pos)
        return

    # 迷路を描画
    maze_image = draw_maze(maze, player_pos, goal_pos, obstacles, yellow_cells)
    st.image(maze_image, use_column_width=True)

if __name__ == "__main__":
    main()
