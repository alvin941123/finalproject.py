import tkinter as tk
from tkinter import messagebox
import random

class GomokuGame:
    def __init__(self):
        self.board_size = 15
        self.board = [[0 for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.current_player = 1  # 1為玩家(黑子), 2為AI(白子)
        self.game_over = False
        
        # 創建GUI
        self.root = tk.Tk()
        self.root.title("五子棋 - 人機對戰")
        self.root.resizable(False, False)
        
        # 創建畫布
        self.canvas_size = 600
        self.grid_size = self.canvas_size // (self.board_size + 1)
        self.canvas = tk.Canvas(self.root, width=self.canvas_size, height=self.canvas_size, bg='burlywood')
        self.canvas.pack(pady=10)
        
        # 綁定滑鼠點擊事件
        self.canvas.bind("<Button-1>", self.on_click)
        
        # 創建控制按鈕
        button_frame = tk.Frame(self.root)
        button_frame.pack()
        
        restart_btn = tk.Button(button_frame, text="重新開始", command=self.restart_game, font=("Arial", 12))
        restart_btn.pack(side=tk.LEFT, padx=5)
        
        # 狀態標籤
        self.status_label = tk.Label(self.root, text="黑子先行 - 你的回合", font=("Arial", 14))
        self.status_label.pack(pady=5)
        
        self.draw_board()
    
    def draw_board(self):
        """繪製棋盤"""
        self.canvas.delete("all")
        
        # 繪製棋盤線條
        for i in range(self.board_size):
            x = (i + 1) * self.grid_size
            y1 = self.grid_size
            y2 = self.board_size * self.grid_size
            self.canvas.create_line(x, y1, x, y2, fill="black", width=1)
            
            y = (i + 1) * self.grid_size
            x1 = self.grid_size
            x2 = self.board_size * self.grid_size
            self.canvas.create_line(x1, y, x2, y, fill="black", width=1)
        
        # 繪製天元等標記點
        star_positions = [(3, 3), (3, 11), (7, 7), (11, 3), (11, 11)]
        for row, col in star_positions:
            x = (col + 1) * self.grid_size
            y = (row + 1) * self.grid_size
            self.canvas.create_oval(x-3, y-3, x+3, y+3, fill="black")
        
        # 繪製棋子
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.board[row][col] != 0:
                    x = (col + 1) * self.grid_size
                    y = (row + 1) * self.grid_size
                    radius = self.grid_size // 3
                    
                    if self.board[row][col] == 1:  # 玩家棋子(黑色)
                        self.canvas.create_oval(x-radius, y-radius, x+radius, y+radius, 
                                              fill="black", outline="black")
                    else:  # AI棋子(白色)
                        self.canvas.create_oval(x-radius, y-radius, x+radius, y+radius, 
                                              fill="white", outline="black")
    
    def on_click(self, event):
        """處理滑鼠點擊事件"""
        if self.game_over or self.current_player != 1:
            return
        
        # 計算點擊的格子座標
        col = round(event.x / self.grid_size) - 1
        row = round(event.y / self.grid_size) - 1
        
        # 檢查座標是否有效
        if 0 <= row < self.board_size and 0 <= col < self.board_size:
            if self.board[row][col] == 0:  # 該位置沒有棋子
                self.make_move(row, col, 1)
    
    def make_move(self, row, col, player):
        """下棋"""
        self.board[row][col] = player
        self.draw_board()
        
        # 檢查是否獲勝
        if self.check_winner(row, col, player):
            self.game_over = True
            winner = "你贏了！" if player == 1 else "AI贏了！"
            self.status_label.config(text=winner)
            messagebox.showinfo("遊戲結束", winner)
            return
        
        # 檢查是否平局
        if self.is_board_full():
            self.game_over = True
            self.status_label.config(text="平局！")
            messagebox.showinfo("遊戲結束", "平局！")
            return
        
        # 切換玩家
        self.current_player = 2 if player == 1 else 1
        
        if self.current_player == 1:
            self.status_label.config(text="你的回合")
        else:
            self.status_label.config(text="AI思考中...")
            self.root.after(500, self.ai_move)  # 延遲500ms後AI下棋
    
    def ai_move(self):
        """AI下棋"""
        if self.game_over:
            return
        
        best_row, best_col = self.get_best_move()
        if best_row is not None and best_col is not None:
            self.make_move(best_row, best_col, 2)
    
    def get_best_move(self):
        """獲取AI的最佳移動"""
        # 使用簡單的啟發式算法
        best_score = -1
        best_moves = []
        
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.board[row][col] == 0:
                    score = self.evaluate_position(row, col)
                    if score > best_score:
                        best_score = score
                        best_moves = [(row, col)]
                    elif score == best_score:
                        best_moves.append((row, col))
        
        if best_moves:
            return random.choice(best_moves)
        return None, None
    
    def evaluate_position(self, row, col):
        """評估位置的價值"""
        score = 0
        
        # 檢查四個方向
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        
        for dr, dc in directions:
            # 檢查AI的連子情況
            ai_count = self.count_consecutive(row, col, dr, dc, 2)
            player_count = self.count_consecutive(row, col, dr, dc, 1)
            
            # AI連子得分
            if ai_count >= 4:
                score += 10000  # 能贏
            elif ai_count == 3:
                score += 1000
            elif ai_count == 2:
                score += 100
            elif ai_count == 1:
                score += 10
            
            # 阻擋玩家得分
            if player_count >= 4:
                score += 5000  # 必須阻擋
            elif player_count == 3:
                score += 500
            elif player_count == 2:
                score += 50
        
        # 中心位置加分
        center = self.board_size // 2
        distance_to_center = abs(row - center) + abs(col - center)
        score += (self.board_size - distance_to_center) * 2
        
        return score
    
    def count_consecutive(self, row, col, dr, dc, player):
        """計算指定方向的連續棋子數量"""
        count = 0
        
        # 向一個方向計算
        r, c = row + dr, col + dc
        while 0 <= r < self.board_size and 0 <= c < self.board_size and self.board[r][c] == player:
            count += 1
            r += dr
            c += dc
        
        # 向相反方向計算
        r, c = row - dr, col - dc
        while 0 <= r < self.board_size and 0 <= c < self.board_size and self.board[r][c] == player:
            count += 1
            r -= dr
            c -= dc
        
        return count
    
    def check_winner(self, row, col, player):
        """檢查是否有玩家獲勝"""
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        
        for dr, dc in directions:
            count = 1  # 包含當前下的棋子
            
            # 向一個方向計算
            r, c = row + dr, col + dc
            while 0 <= r < self.board_size and 0 <= c < self.board_size and self.board[r][c] == player:
                count += 1
                r += dr
                c += dc
            
            # 向相反方向計算
            r, c = row - dr, col - dc
            while 0 <= r < self.board_size and 0 <= c < self.board_size and self.board[r][c] == player:
                count += 1
                r -= dr
                c -= dc
            
            if count >= 5:
                return True
        
        return False
    
    def is_board_full(self):
        """檢查棋盤是否已滿"""
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.board[row][col] == 0:
                    return False
        return True
    
    def restart_game(self):
        """重新開始遊戲"""
        self.board = [[0 for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.current_player = 1
        self.game_over = False
        self.status_label.config(text="黑子先行 - 你的回合")
        self.draw_board()
    
    def run(self):
        """運行遊戲"""
        self.root.mainloop()

if __name__ == "__main__":
    game = GomokuGame()
    game.run()