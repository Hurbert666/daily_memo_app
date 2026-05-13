from __future__ import annotations

import calendar
import tkinter as tk
from datetime import date
from tkinter import messagebox

from db import Database, Task


DATE_FORMAT = "%Y-%m-%d"
WEEKDAYS = ("一", "二", "三", "四", "五", "六", "日")
MONTH_NAMES = (
    "",
    "一月",
    "二月",
    "三月",
    "四月",
    "五月",
    "六月",
    "七月",
    "八月",
    "九月",
    "十月",
    "十一月",
    "十二月",
)


class RoundedButton(tk.Canvas):
    def __init__(
        self,
        parent: tk.Misc,
        text: str,
        command,
        *,
        width: int = 88,
        height: int = 36,
        bg: str = "#ffffff",
        fg: str = "#202124",
        hover_bg: str = "#f3f6fb",
        radius: int = 14,
        font: tuple[str, int, str] | tuple[str, int] = ("Microsoft YaHei UI", 10),
    ) -> None:
        super().__init__(
            parent,
            width=width,
            height=height,
            bg=parent.cget("bg"),
            highlightthickness=0,
            cursor="hand2",
        )
        self.command = command
        self.text = text
        self.fill = bg
        self.normal_fill = bg
        self.hover_fill = hover_bg
        self.fg = fg
        self.radius = radius
        self.font = font
        self.draw()
        self.bind("<Button-1>", lambda _event: self.command())
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def draw(self) -> None:
        self.delete("all")
        w = int(self["width"])
        h = int(self["height"])
        self.create_round_rect(1, 1, w - 1, h - 1, self.radius, fill=self.fill, outline="")
        self.create_text(w / 2, h / 2, text=self.text, fill=self.fg, font=self.font)

    def on_enter(self, _event: tk.Event) -> None:
        self.fill = self.hover_fill
        self.draw()

    def on_leave(self, _event: tk.Event) -> None:
        self.fill = self.normal_fill
        self.draw()

    def create_round_rect(self, x1, y1, x2, y2, radius, **kwargs) -> int:
        points = [
            x1 + radius,
            y1,
            x2 - radius,
            y1,
            x2,
            y1,
            x2,
            y1 + radius,
            x2,
            y2 - radius,
            x2,
            y2,
            x2 - radius,
            y2,
            x1 + radius,
            y2,
            x1,
            y2,
            x1,
            y2 - radius,
            x1,
            y1 + radius,
            x1,
            y1,
        ]
        return self.create_polygon(points, smooth=True, **kwargs)


class TaskCard(tk.Canvas):
    def __init__(
        self,
        parent: tk.Misc,
        task: Task,
        open_command,
        drag_start,
        drag_move,
        drag_end,
        *,
        bg: str,
        accent: str,
    ) -> None:
        super().__init__(
            parent,
            height=82,
            bg="#ffffff",
            highlightthickness=0,
            cursor="hand2",
        )
        self.task = task
        self.open_command = open_command
        self.drag_start = drag_start
        self.drag_move = drag_move
        self.drag_end = drag_end
        self.card_bg = bg
        self.accent = accent
        self.press_y = 0
        self.dragging = False
        self.bind("<ButtonPress-1>", self.on_press)
        self.bind("<B1-Motion>", self.on_motion)
        self.bind("<ButtonRelease-1>", self.on_release)
        self.bind("<Configure>", lambda _event: self.draw())
        self.bind("<Enter>", lambda _event: self.configure(bg="#fbfcff"))
        self.bind("<Leave>", lambda _event: self.configure(bg="#ffffff"))

    def on_press(self, event: tk.Event) -> None:
        self.press_y = event.y_root
        self.dragging = False
        self.drag_start(self.task.id)

    def on_motion(self, event: tk.Event) -> None:
        if abs(event.y_root - self.press_y) < 6 and not self.dragging:
            return
        self.dragging = True
        self.drag_move(self.task.id, event.y_root)

    def on_release(self, event: tk.Event) -> None:
        if self.dragging:
            self.drag_end(self.task.id)
            return
        self.open_command(self.task.id)

    def draw(self) -> None:
        self.delete("all")
        width = max(self.winfo_width(), 300)
        fill = "#f2f4f7" if self.task.is_done else self.card_bg
        accent = "#c7cdd8" if self.task.is_done else self.accent
        title_color = "#8a94a6" if self.task.is_done else "#172033"
        text_color = "#a0a8b5" if self.task.is_done else "#667085"
        self.create_round_rect(2, 2, width - 2, 80, 18, fill=fill, outline="")
        self.create_round_rect(2, 2, 9, 80, 18, fill=accent, outline="")
        self.create_text(
            28,
            25,
            text=self.task.title,
            anchor="w",
            fill=title_color,
            font=("Microsoft YaHei UI", 13, "bold"),
        )
        summary = self.task.description if self.task.description else "没有填写具体内容"
        if len(summary) > 42:
            summary = summary[:42] + "..."
        self.create_text(
            28,
            54,
            text=summary,
            anchor="w",
            fill=text_color,
            font=("Microsoft YaHei UI", 9),
        )
        if self.task.is_done:
            self.create_round_rect(
                width - 86,
                22,
                width - 20,
                52,
                13,
                fill="#e5e8ef",
                outline="",
            )
            self.create_text(
                width - 53,
                37,
                text="已完成",
                fill="#7a8599",
                font=("Microsoft YaHei UI", 9, "bold"),
            )

    def create_round_rect(self, x1, y1, x2, y2, radius, **kwargs) -> int:
        points = [
            x1 + radius,
            y1,
            x2 - radius,
            y1,
            x2,
            y1,
            x2,
            y1 + radius,
            x2,
            y2 - radius,
            x2,
            y2,
            x2 - radius,
            y2,
            x1 + radius,
            y2,
            x1,
            y2,
            x1,
            y2 - radius,
            x1,
            y1 + radius,
            x1,
            y1,
        ]
        return self.create_polygon(points, smooth=True, **kwargs)


class CalendarPopup(tk.Toplevel):
    def __init__(self, parent: "DailyMemoApp", selected: date) -> None:
        super().__init__(parent)
        self.parent = parent
        self.selected = selected
        self.view_year = selected.year
        self.view_month = selected.month

        self.overrideredirect(True)
        self.configure(bg="#ffffff")
        self.bind("<Escape>", lambda _event: self.destroy())
        self.build()

        parent.update_idletasks()
        x = parent.date_button.winfo_rootx()
        y = parent.date_button.winfo_rooty() + parent.date_button.winfo_height() + 8
        self.geometry(f"+{x}+{y}")
        self.focus_force()

    def build(self) -> None:
        for child in self.winfo_children():
            child.destroy()

        shell = tk.Frame(self, bg="#ffffff", padx=14, pady=14)
        shell.pack(fill="both", expand=True)

        header = tk.Frame(shell, bg="#ffffff")
        header.pack(fill="x", pady=(0, 10))
        RoundedButton(header, "‹", self.prev_month, width=34, height=30, bg="#eef3ff").pack(side="left")
        tk.Label(
            header,
            text=f"{self.view_year}年 {MONTH_NAMES[self.view_month]}",
            bg="#ffffff",
            fg="#202124",
            font=("Microsoft YaHei UI", 12, "bold"),
        ).pack(side="left", expand=True)
        RoundedButton(header, "›", self.next_month, width=34, height=30, bg="#eef3ff").pack(side="right")

        grid = tk.Frame(shell, bg="#ffffff")
        grid.pack()
        for index, weekday in enumerate(WEEKDAYS):
            tk.Label(
                grid,
                text=weekday,
                width=4,
                bg="#ffffff",
                fg="#7a8599",
                font=("Microsoft YaHei UI", 9),
            ).grid(row=0, column=index, padx=2, pady=(0, 5))

        month = calendar.Calendar(firstweekday=0).monthdatescalendar(self.view_year, self.view_month)
        today = date.today()
        for row_index, week in enumerate(month, start=1):
            for column_index, day in enumerate(week):
                is_current_month = day.month == self.view_month
                bg = "#edf4ff" if day == self.selected else "#ffffff"
                fg = "#2f6fed" if day == self.selected else "#202124"
                if not is_current_month:
                    fg = "#c1c7d0"
                if day == today and day != self.selected:
                    bg = "#f2f7ef"
                    fg = "#2e7d32"
                button = tk.Label(
                    grid,
                    text=str(day.day),
                    width=4,
                    height=2,
                    bg=bg,
                    fg=fg,
                    cursor="hand2",
                    font=("Microsoft YaHei UI", 9, "bold" if day == self.selected else "normal"),
                )
                button.grid(row=row_index, column=column_index, padx=2, pady=2)
                button.bind("<Button-1>", lambda _event, value=day: self.choose(value))

    def prev_month(self) -> None:
        if self.view_month == 1:
            self.view_year -= 1
            self.view_month = 12
        else:
            self.view_month -= 1
        self.build()

    def next_month(self) -> None:
        if self.view_month == 12:
            self.view_year += 1
            self.view_month = 1
        else:
            self.view_month += 1
        self.build()

    def choose(self, value: date) -> None:
        self.parent.change_date(value)
        self.destroy()


class TaskEditor(tk.Toplevel):
    def __init__(self, parent: "DailyMemoApp", task: Task | None = None) -> None:
        super().__init__(parent)
        self.parent = parent
        self.task = task
        self.result: str | None = None

        self.title("编辑代办" if task else "新建代办")
        self.configure(bg="#f8fafc")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.title_var = tk.StringVar(value=task.title if task else "")
        self.build()
        self.bind("<Escape>", lambda _event: self.destroy())
        self.update_idletasks()
        x = parent.winfo_rootx() + max(80, (parent.winfo_width() - self.winfo_width()) // 2)
        y = parent.winfo_rooty() + max(60, (parent.winfo_height() - self.winfo_height()) // 2)
        self.geometry(f"+{x}+{y}")

    def build(self) -> None:
        card = tk.Frame(self, bg="#ffffff", padx=22, pady=18)
        card.pack(fill="both", expand=True, padx=18, pady=18)
        card.columnconfigure(0, weight=1)

        topbar = tk.Frame(card, bg="#ffffff")
        topbar.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        if self.task:
            RoundedButton(
                topbar,
                "🗑",
                self.delete_task,
                width=42,
                height=34,
                bg="#fff0f0",
                hover_bg="#ffe1e1",
                fg="#d93025",
                font=("Segoe UI Emoji", 13),
            ).pack(side="left")
            RoundedButton(
                topbar,
                "✓",
                self.finish_task,
                width=42,
                height=34,
                bg="#edf8ef",
                hover_bg="#dff3e3",
                fg="#20883d",
                font=("Microsoft YaHei UI", 14, "bold"),
            ).pack(side="right")

        tk.Label(
            card,
            text="标题",
            bg="#ffffff",
            fg="#566076",
            font=("Microsoft YaHei UI", 10, "bold"),
        ).grid(row=1, column=0, sticky="w")
        title_entry = tk.Entry(
            card,
            textvariable=self.title_var,
            width=42,
            relief="flat",
            bg="#f2f5f9",
            fg="#202124",
            insertbackground="#2f6fed",
            font=("Microsoft YaHei UI", 12),
        )
        title_entry.grid(row=2, column=0, sticky="ew", ipady=10, pady=(6, 16))

        tk.Label(
            card,
            text="具体内容（选填）",
            bg="#ffffff",
            fg="#566076",
            font=("Microsoft YaHei UI", 10, "bold"),
        ).grid(row=3, column=0, sticky="w")
        self.description_text = tk.Text(
            card,
            width=42,
            height=8,
            wrap="word",
            relief="flat",
            bg="#f2f5f9",
            fg="#202124",
            insertbackground="#2f6fed",
            padx=12,
            pady=10,
            font=("Microsoft YaHei UI", 11),
        )
        self.description_text.grid(row=4, column=0, sticky="ew", pady=(6, 18))
        if self.task:
            self.description_text.insert("1.0", self.task.description)

        actions = tk.Frame(card, bg="#ffffff")
        actions.grid(row=5, column=0, sticky="e")
        RoundedButton(actions, "取消", self.destroy, width=76, height=36, bg="#f0f2f5").pack(side="left", padx=(0, 8))
        RoundedButton(actions, "保存", self.save_task, width=88, height=36, bg="#2f6fed", hover_bg="#245fd4", fg="#ffffff").pack(side="left")
        title_entry.focus_set()

    def save_task(self) -> None:
        title = self.title_var.get().strip()
        if not title:
            messagebox.showwarning("缺少标题", "请输入代办标题。", parent=self)
            return

        data = {
            "title": title,
            "description": self.description_text.get("1.0", "end").strip(),
            "priority": "中",
            "due_time": "",
        }
        if self.task:
            self.parent.db.update_task(self.task.id, **data)
        else:
            self.parent.db.add_task(self.parent.current_date_text, **data)
        self.result = "saved"
        self.destroy()

    def delete_task(self) -> None:
        if not self.task:
            return
        self.parent.db.delete_task(self.task.id)
        self.result = "deleted"
        self.destroy()

    def finish_task(self) -> None:
        if not self.task:
            return
        self.parent.db.set_task_done(self.task.id, True)
        self.result = "done"
        self.destroy()


class DailyMemoApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.db = Database()
        self.current_date = date.today()
        self.calendar_popup: CalendarPopup | None = None
        self.task_cards: dict[int, TaskCard] = {}
        self.tasks: list[Task] = []
        self.drag_task_id: int | None = None

        self.title("每日备忘录与任务管理")
        self.geometry("920x680")
        self.minsize(760, 560)
        self.configure(bg="#eef2f7")
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.build_ui()
        self.load_tasks()

    @property
    def current_date_text(self) -> str:
        return self.current_date.strftime(DATE_FORMAT)

    def build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        header = tk.Frame(self, bg="#eef2f7", padx=26, pady=22)
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(1, weight=1)

        brand = tk.Frame(header, bg="#eef2f7")
        brand.grid(row=0, column=0, sticky="w")
        tk.Label(
            brand,
            text="✦",
            bg="#eef2f7",
            fg="#ffb020",
            font=("Microsoft YaHei UI", 20, "bold"),
        ).pack(side="left", padx=(0, 8))
        tk.Label(
            brand,
            text="每日任务",
            bg="#eef2f7",
            fg="#172033",
            font=("Microsoft YaHei UI", 22, "bold"),
        ).pack(side="left")

        self.date_button = tk.Frame(header, bg="#ffffff", cursor="hand2", padx=16, pady=9)
        self.date_button.grid(row=0, column=2, sticky="e")
        self.date_button.bind("<Button-1>", lambda _event: self.toggle_calendar())
        tk.Label(
            self.date_button,
            text="📅",
            bg="#ffffff",
            fg="#2f6fed",
            font=("Segoe UI Emoji", 14),
            cursor="hand2",
        ).pack(side="left", padx=(0, 8))
        self.date_label = tk.Label(
            self.date_button,
            text=self.display_date(),
            bg="#ffffff",
            fg="#202124",
            font=("Microsoft YaHei UI", 12, "bold"),
            cursor="hand2",
        )
        self.date_label.pack(side="left")
        for child in self.date_button.winfo_children():
            child.bind("<Button-1>", lambda _event: self.toggle_calendar())

        content = tk.Frame(self, bg="#eef2f7", padx=26, pady=0)
        content.grid(row=1, column=0, sticky="nsew")
        content.columnconfigure(0, weight=1)
        content.rowconfigure(1, weight=1)

        section_header = tk.Frame(content, bg="#eef2f7")
        section_header.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        section_header.columnconfigure(0, weight=1)
        tk.Label(
            section_header,
            text="待完成任务",
            bg="#eef2f7",
            fg="#172033",
            font=("Microsoft YaHei UI", 17, "bold"),
        ).grid(row=0, column=0, sticky="w")
        self.count_label = tk.Label(
            section_header,
            text="",
            bg="#eef2f7",
            fg="#6b7485",
            font=("Microsoft YaHei UI", 10),
        )
        self.count_label.grid(row=0, column=1, sticky="e")

        self.task_area = tk.Frame(content, bg="#ffffff")
        self.task_area.grid(row=1, column=0, sticky="nsew")
        self.task_area.columnconfigure(0, weight=1)
        self.task_area.rowconfigure(0, weight=1)

        self.canvas = tk.Canvas(self.task_area, bg="#ffffff", highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew", padx=(0, 2), pady=2)
        self.scrollbar = tk.Scrollbar(self.task_area, orient="vertical", command=self.canvas.yview)
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.cards_frame = tk.Frame(self.canvas, bg="#ffffff", padx=22, pady=22)
        self.cards_window = self.canvas.create_window((0, 0), window=self.cards_frame, anchor="nw")
        self.cards_frame.columnconfigure(0, weight=1)

        self.canvas.bind("<Configure>", self.on_canvas_resize)
        self.cards_frame.bind("<Configure>", self.update_scroll_region)
        self.canvas.bind("<Button-1>", self.on_empty_area_click)
        self.cards_frame.bind("<Button-1>", self.on_empty_area_click)
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)

        footer = tk.Frame(self, bg="#eef2f7", padx=26, pady=0)
        footer.grid(row=2, column=0, sticky="ew")
        self.status_label = tk.Label(
            footer,
            text="点击空白区域即可新增代办",
            bg="#eef2f7",
            fg="#7a8599",
            font=("Microsoft YaHei UI", 9),
        )
        self.status_label.pack(side="left")

    def display_date(self) -> str:
        today = date.today()
        prefix = "今天 · " if self.current_date == today else ""
        return f"{prefix}{self.current_date.year}年{self.current_date.month}月{self.current_date.day}日"

    def load_tasks(self) -> None:
        for child in self.cards_frame.winfo_children():
            child.destroy()
        self.task_cards.clear()

        tasks = self.db.list_tasks(self.current_date_text)
        self.tasks = tasks
        self.date_label.configure(text=self.display_date())
        done_count = sum(1 for task in tasks if task.is_done)
        pending_count = len(tasks) - done_count
        self.count_label.configure(text=f"{pending_count} 个待办 · {done_count} 个已完成")

        if not tasks:
            self.render_empty_state()
        else:
            for index, task in enumerate(tasks):
                self.render_task_card(task, index)

        self.update_idletasks()
        self.update_scroll_region()

    def render_empty_state(self) -> None:
        empty = tk.Frame(self.cards_frame, bg="#ffffff", cursor="hand2")
        empty.grid(row=0, column=0, sticky="nsew", pady=80)
        empty.columnconfigure(0, weight=1)
        tk.Label(
            empty,
            text="☁",
            bg="#ffffff",
            fg="#c7d2e5",
            font=("Microsoft YaHei UI", 48),
            cursor="hand2",
        ).grid(row=0, column=0)
        tk.Label(
            empty,
            text="今日还没有代办任务",
            bg="#ffffff",
            fg="#7a8599",
            font=("Microsoft YaHei UI", 15, "bold"),
            cursor="hand2",
        ).grid(row=1, column=0, pady=(4, 8))
        tk.Label(
            empty,
            text="点击这里新建一个任务",
            bg="#ffffff",
            fg="#9aa4b2",
            font=("Microsoft YaHei UI", 10),
            cursor="hand2",
        ).grid(row=2, column=0)
        empty.bind("<Button-1>", lambda _event: self.open_new_task())
        for child in empty.winfo_children():
            child.bind("<Button-1>", lambda _event: self.open_new_task())

    def render_task_card(self, task: Task, index: int) -> None:
        palette = [
            ("#fff5e6", "#ffb020"),
            ("#eef7ff", "#2f6fed"),
            ("#f0f8ef", "#35a852"),
            ("#f7f0ff", "#8e5cf7"),
        ]
        bg, accent = palette[index % len(palette)]
        card = TaskCard(
            self.cards_frame,
            task,
            self.open_existing_task,
            self.begin_drag,
            self.drag_task,
            self.finish_drag,
            bg=bg,
            accent=accent,
        )
        card.grid(row=index, column=0, sticky="ew", pady=(0, 12))
        self.task_cards[task.id] = card

    def begin_drag(self, task_id: int) -> None:
        self.drag_task_id = task_id
        card = self.task_cards.get(task_id)
        if card:
            card.configure(cursor="fleur")

    def drag_task(self, task_id: int, y_root: int) -> None:
        if self.drag_task_id != task_id or len(self.tasks) < 2:
            return

        current_index = next(
            (index for index, task in enumerate(self.tasks) if task.id == task_id),
            None,
        )
        if current_index is None:
            return

        target_index = 0
        for index, task in enumerate(self.tasks):
            card = self.task_cards.get(task.id)
            if not card:
                continue
            middle_y = card.winfo_rooty() + card.winfo_height() / 2
            if y_root > middle_y:
                target_index = index

        if target_index == current_index:
            return

        task = self.tasks.pop(current_index)
        self.tasks.insert(target_index, task)
        self.regrid_task_cards()

    def finish_drag(self, task_id: int) -> None:
        card = self.task_cards.get(task_id)
        if card:
            card.configure(cursor="hand2")
        self.drag_task_id = None
        self.db.reorder_tasks(self.current_date_text, [task.id for task in self.tasks])
        self.status_label.configure(text="代办顺序已更新")

    def regrid_task_cards(self) -> None:
        for index, task in enumerate(self.tasks):
            card = self.task_cards.get(task.id)
            if card:
                card.grid_configure(row=index)
        self.update_scroll_region()

    def on_canvas_resize(self, event: tk.Event) -> None:
        self.canvas.itemconfigure(self.cards_window, width=event.width)

    def update_scroll_region(self, _event: tk.Event | None = None) -> None:
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_mousewheel(self, event: tk.Event) -> None:
        if self.canvas.winfo_containing(event.x_root, event.y_root):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def on_empty_area_click(self, event: tk.Event) -> None:
        widget = event.widget
        if widget in self.task_cards.values():
            return
        if isinstance(widget, tk.Label) and widget.master in self.task_cards.values():
            return
        self.open_new_task()

    def open_new_task(self) -> None:
        editor = TaskEditor(self)
        self.wait_window(editor)
        if editor.result:
            self.load_tasks()
            self.status_label.configure(text="代办已保存")

    def open_existing_task(self, task_id: int) -> None:
        task = self.db.get_task(task_id)
        if not task:
            self.load_tasks()
            return
        editor = TaskEditor(self, task)
        self.wait_window(editor)
        if editor.result:
            self.load_tasks()
            self.status_label.configure(text="代办已更新")

    def toggle_calendar(self) -> None:
        if self.calendar_popup and self.calendar_popup.winfo_exists():
            self.calendar_popup.destroy()
            self.calendar_popup = None
            return
        self.calendar_popup = CalendarPopup(self, self.current_date)

    def change_date(self, new_date: date) -> None:
        self.current_date = new_date
        self.load_tasks()
        self.status_label.configure(text=f"已切换到 {self.current_date_text}")

    def on_close(self) -> None:
        self.db.close()
        self.destroy()
