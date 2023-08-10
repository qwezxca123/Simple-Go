# 繪圖套件
import matplotlib.pyplot as plt
import numpy as np

# 定義棋盤物件 黑棋:1 白棋:-1 空白:0
class GoBoard:

    # 初始化
    def __init__(self, size=19):

        # 棋盤大小
        self.size = size

        # 棋盤上各位置狀態
        self.board = np.zeros((size, size), dtype=int)

        # 記錄打劫位置
        self.ko_position = None

        # 記錄各方提子數
        self.captured = {1: 0, -1: 0}

        # 定義星位的坐標
        if self.size == 19:
            self.star_positions = [(3, 3), (3, 9), (3, 15),
                                   (9, 3), (9, 9), (9, 15),
                                   (15, 3), (15, 9), (15, 15)]
        else:
            self.star_positions = []

    # 取得鄰近位置座標
    def get_neighbors(self, x, y):
        neighbors = []
        if x > 0:
            neighbors.append((x-1, y))
        if x < self.size - 1:
            neighbors.append((x+1, y))
        if y > 0:
            neighbors.append((x, y-1))
        if y < self.size - 1:
            neighbors.append((x, y+1))
        return neighbors

    # 數氣
    def count_liberties(self, x, y):

        visited = set()       # 紀錄已訪問位置
        group = set()         # 紀錄該棋子所在的群組位置
        stack = [(x, y)]      # 待檢查棋子位置
        liberties = 0         # 氣數

        while stack:

            # 取出一個待檢查位置並記錄位置
            cx, cy = stack.pop()
            visited.add((cx, cy))
            group.add((cx, cy))

            # 查看該棋子相鄰位置狀態
            for nx, ny in self.get_neighbors(cx, cy):

                # 跳過已訪問位置
                if (nx, ny) in visited:
                    continue

                # 若位置為空則氣數+1
                content = self.board[ny, nx]
                if content == 0:
                    liberties += 1

                # 若位置為同色棋子則加入待檢查棋子
                elif content == self.board[y, x]:
                    stack.append((nx, ny))

        # 如果氣為0，返回群組內的所有點，否則只返回氣數
        return liberties, group if liberties == 0 else None

    # 預測落子合法性
    def is_legal_move(self, x, y, color):

        # 超出棋盤的位置不能下
        if not (0 <= x < self.size) or not (0 <= y < self.size):
            return (False, 0)

        # 有子的地方不能下
        if self.board[y, x] != 0:
            return (False, 0)

        # 打劫位置不能下
        if (x, y) == self.ko_position:
            print(self.ko_position)
            print("1")
            return (False, 0)

        # 模擬放置棋子
        self.board[y, x] = color

        # 記錄吃子數
        captured_stones = 0

        # 檢查相鄰位置
        for nx, ny in self.get_neighbors(x, y):

            # 若是敵方棋子
            if self.board[ny, nx] == -color:
              liberties, group = self.count_liberties(nx, ny)

              # 群組氣數為0則整個提掉
              if(liberties == 0):

                # 紀錄提掉的起點座標
                self.ko_position = (nx, ny)
                for gx, gy in group:
                  self.board[gy, gx] = 0
                  captured_stones += 1

        # 若提子數為1且棋子氣數為1,則將其提取棋子位置紀錄為打劫位置
        if captured_stones != 1 or self.count_liberties(x, y)[0] != 1:
            self.ko_position = None

        # 若提子判定後氣數為0則不能下
        if self.count_liberties(x, y) == 0 and captured_stones == 0:

            # 重置模擬落子位置
            self.board[y, x] = 0
            return (False, 0)

        # 重置模擬落子位置
        self.board[y, x] = 0

        # 沒有判定不能下就可以下
        return (True, captured_stones)

    # 落子
    def place_stone(self, x, y, color):

        # 顏色檢查
        if color not in [1, -1]:
            raise ValueError("顏色必須是 1(黑棋) 或 -1(白棋)")

        # 合法性檢查
        else:
          OK, captured_stones = self.is_legal_move(x, y, color)
          if not OK:
            raise ValueError("落子位置非法")

        # 落子
        self.board[y, x] = color

        # 更新提子數
        self.captured[-color] += captured_stones

    def display(self):
        fig, ax = plt.subplots(figsize=(4, 4))

        # 畫底線
        for i in range(self.size):
            ax.axhline(i, color='k', lw=1, zorder=0)
            ax.axvline(i, color='k', lw=1, zorder=0)

        # 畫星位
        for y, x in self.star_positions:
          ax.scatter(x, self.size - 1 - y, s=15, c='black', marker='o', label='Black')

        # 畫棋子
        y, x = np.where(self.board == 1)
        ax.scatter(x, self.size - 1 - y, s=100, c='black', marker='o', label='Black')

        y, x = np.where(self.board == -1)
        ax.scatter(x, self.size - 1 - y, s=100, c='white', marker='o', edgecolors='black', label='White')

        # 設定座標軸範圍以避免超出邊界
        ax.set_xlim([-0.5, self.size - 0.5])
        ax.set_ylim([-0.5, self.size - 0.5])

        # x, y軸比例相同
        ax.set_aspect('equal')

        # 關閉x, y軸刻度
        ax.axis('off')

        plt.show()

    # 判斷勝負
    def determine_territory(self):
        # 初始化領地盤為全0
        territory_board = np.zeros((self.size, self.size), dtype=int)
        
        # 輔助函數，檢查坐標是否在棋盤內
        def is_inside_board(x, y):
            return 0 <= x < self.size and 0 <= y < self.size
        
        # 深度優先搜索，找出連接的空區域
        def dfs(x, y, visited):
            if not is_inside_board(x, y) or (x, y) in visited or self.board[y, x] != 0:
                return set(), set()
            
            visited.add((x, y))
            borders = set()
            neighbors = self.get_neighbors(x, y)
            
            for nx, ny in neighbors:
                if self.board[ny, nx] != 0:
                    borders.add(self.board[ny, nx])
                else:
                    new_borders, new_visited = dfs(nx, ny, visited)
                    borders |= new_borders
                    visited |= new_visited
            
            return borders, visited
        
        # 遍歷棋盤上的每一個位置
        visited_positions = set()
        for y in range(self.size):
            for x in range(self.size):
                if self.board[y, x] == 0 and (x, y) not in visited_positions:
                    borders, visited = dfs(x, y, set())
                    
                    # 根據邊界判定領地
                    if len(borders) == 1:
                        territory_value = list(borders)[0]
                        for vx, vy in visited:
                            territory_board[vy, vx] = territory_value
                    visited_positions |= visited
        
        return territory_board

    # 計算結果並展示
    def display_result(self):
        territory = self.determine_territory()
        black_score = np.sum(territory == 1)
        white_score = np.sum(territory == -1) + 6.5
        print(f"比分: 黑棋：{black_score}，白棋：{white_score}")

        fig, ax = plt.subplots(figsize=(4, 4))

        # 畫底線
        for i in range(self.size):
            ax.axhline(i, color='k', lw=1, zorder=0)
            ax.axvline(i, color='k', lw=1, zorder=0)

        # 畫星位
        for y, x in self.star_positions:
            ax.scatter(x, self.size - 1 - y, s=15, c='black', marker='o', label='Black')

        # 畫棋子
        y, x = np.where(self.board == 1)
        ax.scatter(x, self.size - 1 - y, s=100, c='black', marker='o', label='Black')

        y, x = np.where(self.board == -1)
        ax.scatter(x, self.size - 1 - y, s=100, c='white', marker='o', edgecolors='black', label='White')

        # 畫領地
        y, x = np.where(territory == 1)
        ax.scatter(x, self.size - 1 - y, s=30, c='black', marker='^', label='Black Territory')

        y, x = np.where(territory == -1)
        ax.scatter(x, self.size - 1 - y, s=30, c='white', marker='^', edgecolors='black', label='White Territory')

        # 設定座標軸範圍以避免超出邊界
        ax.set_xlim([-0.5, self.size - 0.5])
        ax.set_ylim([-0.5, self.size - 0.5])

        # x, y軸比例相同
        ax.set_aspect('equal')

        # 關閉x, y軸刻度
        ax.axis('off')

        plt.show()

    # 開始遊戲
    def start_game(self):
        consecutive_passes = 0  # 連續虛手的次數
        current_color = 1  # 黑先，所以設為1

        while consecutive_passes < 2:
            self.display()  # 顯示當前棋盤狀態

            # 根據當前顏色提示玩家
            if current_color == 1:
                print("黑棋回合，請輸入座標(x,y)或'pass'虛手：")
            else:
                print("白棋回合，請輸入座標(x,y)或'pass'虛手：")

            move = input().strip().lower()

            if move == 'pass':
                consecutive_passes += 1
            else:
                try:
                    x, y = map(int, move.split(','))
                    if self.is_legal_move(x, y, current_color)[0]:
                        self.place_stone(x, y, current_color)
                        consecutive_passes = 0  # 重置連續虛手次數
                    else:
                        print("非法落子位置，請重新輸入。")
                        continue
                except ValueError:
                    print("輸入格式錯誤，請重新輸入。")
                    continue

            # 切換玩家
            current_color = -current_color

        # 兩方都選擇虛手，遊戲結束
        print("遊戲結束！")
        self.display_result()  # 顯示結果
