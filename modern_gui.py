import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import os
import sys
import subprocess
import threading
import re
import glob
import webbrowser
from datetime import datetime
import pandas as pd

# ================= 配置常量 =================
COLORS = {
    "bg_dark": "#2b2b2b",
    "bg_darker": "#1e1e1e",
    "fg_light": "#ffffff",
    "fg_dim": "#a9a9a9",
    "accent": "#00e5ff",  # 霓虹蓝
    "accent_hover": "#00b8cc",
    "success": "#00ff9d", # 霓虹绿
    "warning": "#ffbd2e",
    "danger": "#ff5f5f",
    "input_bg": "#383838",
    "select_bg": "#4a4a4a"
}

FONT_MAIN = ("Microsoft YaHei UI", 10)
FONT_BOLD = ("Microsoft YaHei UI", 10, "bold")
FONT_TITLE = ("Microsoft YaHei UI", 16, "bold")
FONT_MONO = ("Consolas", 9)

CONFIG_PATH = os.path.join("config", "base_config.py")
if not os.path.exists(CONFIG_PATH):
    CONFIG_PATH = "base_config.py"

class ModernCrawlerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("MediaCrawler Pro | 舆情智控终端")
        self.root.geometry("1100x800")
        self.root.configure(bg=COLORS["bg_dark"])
        
        # 状态变量
        self.process = None
        self.is_running = False
        self.keywords_var = tk.StringVar()
        self.platform_var = tk.StringVar(value="xhs")
        self.storage_var = tk.StringVar(value="csv")
        self.status_var = tk.StringVar(value="系统就绪 | 等待指令")
        
        # 数据变量
        self.current_df = None
        
        self._setup_styles()
        self._setup_layout()
        self._load_config()

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure(".", background=COLORS["bg_dark"], foreground=COLORS["fg_light"], font=FONT_MAIN, borderwidth=0)
        
        # Tabs
        style.configure("TNotebook", background=COLORS["bg_darker"], borderwidth=0)
        style.configure("TNotebook.Tab", background=COLORS["bg_dark"], foreground=COLORS["fg_dim"], padding=[15, 8], font=FONT_BOLD)
        style.map("TNotebook.Tab", background=[("selected", COLORS["accent"])], foreground=[("selected", COLORS["bg_darker"])])

        # Treeview (表格)
        style.configure("Treeview", 
            background=COLORS["bg_darker"],
            foreground=COLORS["fg_light"],
            fieldbackground=COLORS["bg_darker"],
            rowheight=30,
            borderwidth=0,
            font=("Microsoft YaHei UI", 9)
        )
        style.configure("Treeview.Heading", 
            background=COLORS["input_bg"],
            foreground=COLORS["accent"],
            font=FONT_BOLD,
            relief="flat",
            padding=5
        )
        style.map("Treeview", background=[("selected", COLORS["accent"])], foreground=[("selected", COLORS["bg_darker"])])

        # Components
        style.configure("Card.TFrame", background=COLORS["bg_darker"], relief="flat")
        style.configure("Title.TLabel", font=FONT_TITLE, foreground=COLORS["accent"], background=COLORS["bg_dark"])
        style.configure("Sub.TLabel", foreground=COLORS["fg_dim"], background=COLORS["bg_darker"])
        style.configure("Info.TLabel", foreground=COLORS["fg_dim"], background=COLORS["bg_dark"], font=("Microsoft YaHei UI", 9))
        
        # Buttons
        style.configure("TButton", background=COLORS["input_bg"], foreground=COLORS["accent"], borderwidth=0, padding=8)
        style.map("TButton", background=[("active", COLORS["bg_dark"]), ("pressed", COLORS["accent"])], foreground=[("pressed", COLORS["bg_darker"])])
        
        style.configure("Accent.TButton", background=COLORS["accent"], foreground=COLORS["bg_darker"], font=FONT_BOLD)
        style.map("Accent.TButton", background=[("active", COLORS["accent_hover"])], foreground=[("active", COLORS["bg_darker"])])

        style.configure("TEntry", fieldbackground=COLORS["input_bg"], foreground=COLORS["fg_light"], insertcolor=COLORS["accent"])
        style.configure("TRadiobutton", background=COLORS["bg_darker"], foreground=COLORS["fg_light"], indicatorcolor=COLORS["input_bg"])

    def _setup_layout(self):
        # Header
        header = tk.Frame(self.root, bg=COLORS["bg_dark"], height=60)
        header.pack(fill=tk.X, padx=20, pady=15)
        ttk.Label(header, text="🛡️ MEDIACRAWLER PRO", style="Title.TLabel").pack(side=tk.LEFT)
        ttk.Label(header, textvariable=self.status_var, foreground=COLORS["success"]).pack(side=tk.RIGHT)

        # Notebook
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Tab 1: Crawler
        crawler_tab = ttk.Frame(notebook)
        notebook.add(crawler_tab, text=" 🚀 智控中心 ")
        self._init_crawler_tab(crawler_tab)

        # Tab 2: Data
        data_tab = ttk.Frame(notebook)
        notebook.add(data_tab, text=" 📋 精简数据 ")
        self._init_data_tab(data_tab)

    def _init_crawler_tab(self, parent):
        left_panel = ttk.Frame(parent, style="Card.TFrame", padding=20)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        
        ttk.Label(left_panel, text="核心配置", style="Sub.TLabel", font=FONT_BOLD).pack(anchor="w", pady=(0, 15))
        
        ttk.Label(left_panel, text="关键词:", style="Sub.TLabel").pack(anchor="w")
        ttk.Entry(left_panel, textvariable=self.keywords_var, width=35).pack(fill=tk.X, pady=(5, 15))
        
        ttk.Label(left_panel, text="平台:", style="Sub.TLabel").pack(anchor="w")
        pf_frame = ttk.Frame(left_panel, style="Card.TFrame")
        pf_frame.pack(fill=tk.X, pady=(5, 15))
        platforms = [("小红书", "xhs"), ("抖音", "dy"), ("快手", "ks"), ("B站", "bili"), ("微博", "wb"), ("知乎", "zhihu")]
        for idx, (lbl, val) in enumerate(platforms):
            ttk.Radiobutton(pf_frame, text=lbl, value=val, variable=self.platform_var).grid(row=idx//3, column=idx%3, sticky="w", padx=5, pady=2)

        ttk.Label(left_panel, text="格式:", style="Sub.TLabel").pack(anchor="w")
        store_frame = ttk.Frame(left_panel, style="Card.TFrame")
        store_frame.pack(fill=tk.X, pady=(5, 20))
        for val in ["csv", "json", "db"]:
            ttk.Radiobutton(store_frame, text=val.upper(), value=val, variable=self.storage_var).pack(side=tk.LEFT, padx=10)

        ttk.Button(left_panel, text="⚙️ 初始化 DB", command=self.init_db).pack(fill=tk.X, pady=5)
        ttk.Button(left_panel, text="📂 打开数据目录", command=self.open_data_folder).pack(fill=tk.X, pady=5)
        
        ttk.Separator(left_panel, orient="horizontal").pack(fill=tk.X, pady=20)
        
        self.btn_start = ttk.Button(left_panel, text="▶ 启动任务", style="Accent.TButton", command=self.start_crawler)
        self.btn_start.pack(fill=tk.X, pady=5)
        
        self.btn_stop = ttk.Button(left_panel, text="⏹ 停止任务", state="disabled", command=self.stop_crawler)
        self.btn_stop.pack(fill=tk.X, pady=5)

        right_panel = ttk.Frame(parent, style="Card.TFrame", padding=1)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        log_header = ttk.Frame(right_panel, style="Card.TFrame", padding=10)
        log_header.pack(fill=tk.X)
        ttk.Label(log_header, text=">_ 系统日志", style="Sub.TLabel").pack(side=tk.LEFT)
        
        self.log_text = scrolledtext.ScrolledText(right_panel, bg="#000000", fg=COLORS["success"], font=FONT_MONO, relief="flat")
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def _init_data_tab(self, parent):
        toolbar = ttk.Frame(parent, style="Card.TFrame", padding=10)
        toolbar.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(toolbar, text="文件:", style="Sub.TLabel").pack(side=tk.LEFT, padx=5)
        self.file_combo = ttk.Combobox(toolbar, width=35, state="readonly")
        self.file_combo.pack(side=tk.LEFT, padx=5)
        self.file_combo.bind("<<ComboboxSelected>>", self._on_file_select)
        
        ttk.Button(toolbar, text="🔄 刷新", command=self._scan_data_files, width=8).pack(side=tk.LEFT, padx=5)
        ttk.Separator(toolbar, orient="vertical").pack(side=tk.LEFT, fill=tk.Y, padx=15)
        ttk.Button(toolbar, text="🔗 打开 aweme_url", style="Accent.TButton", command=self._open_selected_link).pack(side=tk.LEFT, padx=5)
        ttk.Label(toolbar, text="(优先跳转 aweme_url)", style="Info.TLabel").pack(side=tk.LEFT, padx=5)

        table_frame = ttk.Frame(parent, style="Card.TFrame", padding=1)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        tree_scroll_y = ttk.Scrollbar(table_frame)
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        tree_scroll_x = ttk.Scrollbar(table_frame, orient="horizontal")
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.tree = ttk.Treeview(table_frame, 
                                 yscrollcommand=tree_scroll_y.set, 
                                 xscrollcommand=tree_scroll_x.set,
                                 show="headings",
                                 selectmode="browse")
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        tree_scroll_y.config(command=self.tree.yview)
        tree_scroll_x.config(command=self.tree.xview)
        
        self.tree.bind("<Double-1>", self._on_tree_double_click)
        self._scan_data_files()

    # ================= 逻辑功能 =================

    def log(self, msg):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.root.after(0, self._append_log, f"[{timestamp}] {msg}\n")

    def _append_log(self, msg):
        self.log_text.insert(tk.END, msg)
        self.log_text.see(tk.END)

    def _load_config(self):
        try:
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                content = f.read()
                kw = re.search(r'KEYWORDS\s*=\s*["\'](.*?)["\']', content)
                if kw: self.keywords_var.set(kw.group(1))
                plat = re.search(r'PLATFORM\s*=\s*["\'](.*?)["\']', content)
                if plat: self.platform_var.set(plat.group(1))
                store = re.search(r'SAVE_DATA_OPTION\s*=\s*["\'](.*?)["\']', content)
                if store: self.storage_var.set(store.group(1))
            self.log("✅ 配置文件加载成功")
        except Exception as e:
            self.log(f"⚠️ 读取配置失败: {e}")

    def _save_config(self):
        try:
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                content = f.read()
            content = re.sub(r'KEYWORDS\s*=\s*["\'].*?["\']', f'KEYWORDS = "{self.keywords_var.get()}"', content)
            content = re.sub(r'PLATFORM\s*=\s*["\'].*?["\']', f'PLATFORM = "{self.platform_var.get()}"', content)
            content = re.sub(r'SAVE_DATA_OPTION\s*=\s*["\'].*?["\']', f'SAVE_DATA_OPTION = "{self.storage_var.get()}"', content)
            with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            self.log(f"❌ 保存配置失败: {e}")
            return False

    def start_crawler(self):
        if not self.keywords_var.get():
            messagebox.showwarning("提示", "请输入搜索关键词")
            return
        if self._save_config():
            self.is_running = True
            self.btn_start.config(state="disabled")
            self.btn_stop.config(state="normal")
            self.status_var.set(f"🔥 运行中 - {self.platform_var.get()}")
            threading.Thread(target=self._run_process, daemon=True).start()

    def _run_process(self):
        cmd = [sys.executable, "main.py"]
        try:
            self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='gbk' if sys.platform == 'win32' else 'utf-8', errors='replace', bufsize=1)
            for line in self.process.stdout:
                self.log(line.strip())
            self.process.wait()
            self.log("✅ 任务结束")
        except Exception as e:
            self.log(f"❌ 错误: {e}")
        finally:
            self.is_running = False
            self.root.after(0, lambda: [self.btn_start.config(state="normal"), self.btn_stop.config(state="disabled"), self.status_var.set("系统就绪")])

    def stop_crawler(self):
        if self.process and self.is_running:
            self.process.terminate()
            self.log("🛑 正在停止...")

    def open_data_folder(self):
        path = os.path.abspath("data")
        if not os.path.exists(path): os.makedirs(path)
        if sys.platform == 'win32': os.startfile(path)
        else: subprocess.run(['xdg-open', path])

    def init_db(self):
        self.log("初始化数据库...")
        subprocess.Popen([sys.executable, "main.py", "--init_db", "sqlite"])

    # ================= 表格 & 数据过滤 =================
    
    def _scan_data_files(self):
        files = glob.glob("data/**/*.csv", recursive=True)
        files.sort(key=os.path.getmtime, reverse=True)
        self.file_combo['values'] = files
        if files:
            self.file_combo.current(0)
            self._on_file_select(None)
        else:
            self.log("ℹ️ 未找到 CSV 文件")

    def _on_file_select(self, event):
        file_path = self.file_combo.get()
        if not file_path: return
        try:
            self.current_df = pd.read_csv(file_path, encoding='utf-8-sig')
            self.log(f"📂 加载: {os.path.basename(file_path)}")
            self._update_table(self.current_df)
        except Exception as e:
            self.log(f"❌ 读取CSV失败: {e}")

    def _update_table(self, df):
        self.tree.delete(*self.tree.get_children())
        all_columns = list(df.columns)
        
        # 定义需要保留的关键词
        desired_keywords = [
            "id", "user", "nickname", "用户",   
            "ip", "location", "地址",          
            "url", "link", "链接", "aweme", "note", # 明确包含 aweme
            "time", "date", "时间", "日期"      
        ]
        
        # 筛选列
        show_columns = []
        for col in all_columns:
            col_lower = col.lower()
            if any(k in col_lower for k in desired_keywords):
                show_columns.append(col)
        
        if not show_columns: show_columns = all_columns
        self.tree["columns"] = show_columns
        
        for col in show_columns:
            self.tree.heading(col, text=col)
            col_lower = col.lower()
            width = 100
            if "url" in col_lower or "link" in col_lower: width = 250
            elif "time" in col_lower: width = 150
            elif "ip" in col_lower: width = 80
            self.tree.column(col, width=width, anchor="w")
            
        for index, row in df[show_columns].head(1000).iterrows():
            values = [str(item).replace('\n', ' ') for item in row]
            self.tree.insert("", "end", values=values)

    def _on_tree_double_click(self, event):
        self._open_selected_link()

    def _open_selected_link(self):
        """打开链接：优先 aweme_url，其次其他 URL"""
        selected_item = self.tree.selection()
        if not selected_item: return
        
        item = selected_item[0]
        values = self.tree.item(item, "values")
        columns = self.tree["columns"]
        
        target_url = None
        
        # 1. 优先查找 aweme_url (Douyin/TikTok)
        if "aweme_url" in columns:
            idx = columns.index("aweme_url")
            if idx < len(values):
                val = values[idx]
                if str(val).startswith("http"):
                    target_url = val

        # 2. 如果没找到，查找其他常见 URL 字段 (XHS note_url 等)
        if not target_url:
            for priority_col in ["note_url", "detail_url", "video_url", "origin_url"]:
                if priority_col in columns:
                    idx = columns.index(priority_col)
                    if idx < len(values):
                        val = values[idx]
                        if str(val).startswith("http"):
                            target_url = val
                            break
        
        # 3. 还没找到，扫描该行所有数据查找 http
        if not target_url:
            for val in values:
                v = str(val).strip()
                if v.startswith("http"):
                    target_url = v
                    break

        if target_url:
            webbrowser.open(target_url)
            self.log(f"🔗 打开链接: {target_url[:50]}...")
        else:
            messagebox.showinfo("提示", "未找到 aweme_url 或其他有效链接")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ModernCrawlerGUI()
    app.run()