from abc import ABC, abstractmethod
import tkinter as tk
import random
import time

class BaseCell(ABC):

    @abstractmethod
    def reveal(self):
        pass

    @abstractmethod
    def is_mine(self):
        pass

class Cell(BaseCell):

    def __init__(self):

        self.__is_mine = False
        self.__is_revealed = False
        self.__is_flagged = False
        self.__neighbor_mines = 0

    def place_mine(self):
        self.__is_mine = True

    def is_mine(self):
        return self.__is_mine

    def reveal(self):
        self.__is_revealed = True

    def is_revealed(self):
        return self.__is_revealed

    def toggle_flag(self):
        self.__is_flagged = not self.__is_flagged

    def is_flagged(self):
        return self.__is_flagged

    def set_neighbor_mines(self, count):
        self.__neighbor_mines = count

    def get_neighbor_mines(self):
        return self.__neighbor_mines

class Board:

    def __init__(self, rows, cols, mines):

        self.rows = rows
        self.cols = cols
        self.mines = mines

        self.grid = [[Cell() for _ in range(cols)] for _ in range(rows)]

        self.mines_placed = False
        self.cells_to_reveal = rows * cols - mines

    def _place_mines_safe(self, safe_r, safe_c):

        safe_zone = set()

        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:

                nr = safe_r + dr
                nc = safe_c + dc

                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    safe_zone.add((nr, nc))

        placed = 0

        while placed < self.mines:

            r = random.randint(0, self.rows - 1)
            c = random.randint(0, self.cols - 1)

            if (r, c) in safe_zone:
                continue

            if not self.grid[r][c].is_mine():

                self.grid[r][c].place_mine()

                placed += 1

        self._calculate_neighbors()

        self.mines_placed = True

    def _calculate_neighbors(self):

        for r in range(self.rows):
            for c in range(self.cols):

                count = 0

                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:

                        nr = r + dr
                        nc = c + dc

                        if 0 <= nr < self.rows and 0 <= nc < self.cols:

                            if self.grid[nr][nc].is_mine():
                                count += 1

                self.grid[r][c].set_neighbor_mines(count)

    def reveal_cell(self, r, c):

        cell = self.grid[r][c]

        if cell.is_flagged():
            return True

        if not self.mines_placed:
            self._place_mines_safe(r, c)

        if cell.is_revealed():
            return True

        cell.reveal()

        if not cell.is_mine():
            self.cells_to_reveal -= 1

        if cell.is_mine():
            return False

        if cell.get_neighbor_mines() == 0:

            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:

                    nr = r + dr
                    nc = c + dc

                    if 0 <= nr < self.rows and 0 <= nc < self.cols:
                        self.reveal_cell(nr, nc)

        return True

    def toggle_flag(self, r, c):

        cell = self.grid[r][c]

        if not cell.is_revealed():
            cell.toggle_flag()

    def check_win(self):

        return self.cells_to_reveal == 0

class GameButton(tk.Button):

    def __init__(self, master, row, col, command):

        super().__init__(
            master,
            width=3,
            height=1,
            font=("Arial", 14, "bold"),
            bg="#3c3f41",
            fg="white",
            activebackground="#5c6164",
            relief=tk.RAISED,
            bd=2,
            command=command
        )

        self.row = row
        self.col = col

class MinesweeperGUI:

    def __init__(self, root):

        self.root = root
        self.root.title("Minesweeper")
        self.root.configure(bg="#1e1e1e")

        self.game_over = False

        self.number_colors = {
            1: "blue",
            2: "green",
            3: "red",
            4: "dark blue",
            5: "dark red",
            6: "turquoise",
            7: "black",
            8: "gray"
        }

        self.top_frame = tk.Frame(root, bg="#1e1e1e")
        self.top_frame.pack(pady=10)

        self.title_label = tk.Label(
            self.top_frame,
            text="MINESWEEPER",
            font=("Arial", 20, "bold"),
            fg="white",
            bg="#1e1e1e"
        )

        self.title_label.pack()

        self.info_frame = tk.Frame(root, bg="#1e1e1e")
        self.info_frame.pack(pady=5)

        self.mine_counter_label = tk.Label(
            self.info_frame,
            text="Mines Left: 10",
            font=("Arial", 14, "bold"),
            fg="#ffd54f",
            bg="#1e1e1e"
        )

        self.mine_counter_label.grid(row=0, column=0, padx=20)

        self.timer_label = tk.Label(
            self.info_frame,
            text="Time: 00:00",
            font=("Arial", 14, "bold"),
            fg="#4fc3f7",
            bg="#1e1e1e"
        )

        self.timer_label.grid(row=0, column=1, padx=20)

        self.difficulty_frame = tk.Frame(root, bg="#1e1e1e")
        self.difficulty_frame.pack(pady=5)

        tk.Button(
            self.difficulty_frame,
            text="Easy",
            width=10,
            bg="#4caf50",
            fg="white",
            command=lambda: self.start_new_game(8, 8, 10)
        ).grid(row=0, column=0, padx=5)

        tk.Button(
            self.difficulty_frame,
            text="Medium",
            width=10,
            bg="#ff9800",
            fg="white",
            command=lambda: self.start_new_game(12, 12, 20)
        ).grid(row=0, column=1, padx=5)

        tk.Button(
            self.difficulty_frame,
            text="Hard",
            width=10,
            bg="#f44336",
            fg="white",
            command=lambda: self.start_new_game(16, 16, 40)
        ).grid(row=0, column=2, padx=5)

        self.board_frame = tk.Frame(root, bg="#1e1e1e")
        self.board_frame.pack(pady=10)

        self.buttons = []

        self.current_settings = (8, 8, 10)

        self.start_new_game(*self.current_settings)

    def start_timer(self):

        self.start_time = time.time()

        self.timer_running = True

        self.update_timer()

    def update_timer(self):

        if self.timer_running and not self.game_over:

            elapsed = int(time.time() - self.start_time)

            minutes = elapsed // 60
            seconds = elapsed % 60

            self.timer_label.config(
                text=f"Time: {minutes:02}:{seconds:02}"
            )

            self.root.after(1000, self.update_timer)

    def start_new_game(self, rows, cols, mines):

        self.current_settings = (rows, cols, mines)

        self.game_over = False

        self.flags_used = 0

        self.first_click = True

        self.timer_running = False

        self.timer_label.config(text="Time: 00:00")

        for widget in self.board_frame.winfo_children():
            widget.destroy()

        self.rows = rows
        self.cols = cols

        self.board = Board(rows, cols, mines)

        self.buttons = [[None for _ in range(cols)] for _ in range(rows)]

        self.create_buttons()

        self.update_mine_counter()

    def create_buttons(self):

        for r in range(self.rows):
            for c in range(self.cols):

                btn = GameButton(
                    self.board_frame,
                    r,
                    c,
                    lambda r=r, c=c: self.left_click(r, c)
                )

                btn.bind(
                    "<Button-3>",
                    lambda event, r=r, c=c: self.right_click(r, c)
                )

                btn.grid(row=r, column=c, padx=1, pady=1)

                self.buttons[r][c] = btn

    def left_click(self, r, c):

        if self.game_over:
            return

        if self.first_click:

            self.first_click = False

            self.start_timer()

        alive = self.board.reveal_cell(r, c)

        self.update_buttons()

        if not alive:

            self.game_over = True

            self.timer_running = False

            self.show_mines()

            self.disable_buttons()

            self.show_end_screen("GAME OVER", "#d32f2f")

            return

        if self.board.check_win():

            self.game_over = True

            self.timer_running = False

            self.show_mines()

            self.disable_buttons()

            self.show_end_screen("YOU WIN!", "#4caf50")

    def right_click(self, r, c):

        if self.game_over:
            return

        cell = self.board.grid[r][c]

        was_flagged = cell.is_flagged()

        self.board.toggle_flag(r, c)

        if was_flagged:
            self.flags_used -= 1
        else:
            self.flags_used += 1

        self.update_mine_counter()

        self.update_buttons()

    def update_buttons(self):

        for r in range(self.rows):
            for c in range(self.cols):

                cell = self.board.grid[r][c]

                btn = self.buttons[r][c]

                if cell.is_flagged():


                    btn.config(
                        text="⚑",
                        bg="#ffd54f",
                        fg="black"
                    )

                elif not cell.is_revealed():

                    btn.config(
                        text="",
                        bg="#3c3f41",
                        relief=tk.RAISED
                    )

                elif cell.is_mine():

                    btn.config(
                        text="💣",
                        bg="#d32f2f",
                        fg="white",
                        relief=tk.SUNKEN
                    )

                else:

                    count = cell.get_neighbor_mines()

                    color = self.number_colors.get(count, "black")

                    if count == 0:

                        btn.config(
                            text="",
                            bg="#bdbdbd",
                            relief=tk.SUNKEN
                        )

                    else:

                        btn.config(
                            text=str(count),
                            fg=color,
                            bg="#d6d6d6",
                            relief=tk.SUNKEN
                        )

    def update_mine_counter(self):

        remaining = self.board.mines - self.flags_used

        self.mine_counter_label.config(
            text=f"Mines Left: {remaining}"
        )

    def show_mines(self):

        for r in range(self.rows):
            for c in range(self.cols):

                if self.board.grid[r][c].is_mine():

                    self.buttons[r][c].config(
                        text="💣",
                        bg="#d32f2f",
                        fg="white"
                    )

    def disable_buttons(self):

        for row in self.buttons:
            for btn in row:
                btn.config(state=tk.DISABLED)

    def show_end_screen(self, text, color):

        self.end_frame = tk.Frame(
            self.root,
            bg="#1e1e1e",
            bd=3,
            relief=tk.RIDGE
        )

        self.end_frame.place(
            relx=0.5,
            rely=0.5,
            anchor="center"
        )

        label = tk.Label(
            self.end_frame,
            text=text,
            font=("Arial", 22, "bold"),
            fg=color,
            bg="#1e1e1e"
        )

        label.pack(padx=30, pady=20)

        button_frame = tk.Frame(
            self.end_frame,
            bg="#1e1e1e"
        )

        button_frame.pack(pady=10)

        restart_btn = tk.Button(
            button_frame,
            text="Restart",
            width=12,
            bg="#4caf50",
            fg="white",
            font=("Arial", 11, "bold"),
            command=self.restart_game
        )

        restart_btn.grid(row=0, column=0, padx=10)

        close_btn = tk.Button(
            button_frame,
            text="Close",
            width=12,
            bg="#d32f2f",
            fg="white",
            font=("Arial", 11, "bold"),
            command=self.root.destroy
        )

        close_btn.grid(row=0, column=1, padx=10)

    def restart_game(self):

        self.end_frame.destroy()

        rows, cols, mines = self.current_settings

        self.start_new_game(rows, cols, mines)

if __name__ == "__main__":

    root = tk.Tk()

    app = MinesweeperGUI(root)

    root.mainloop()