# crawler_gui.py
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import subprocess
import threading
import sys
import os
import re
from datetime import datetime

# ================= 配置区域 =================
# 请确认你的 base_config.py 路径
# 如果在 config 文件夹下：
CONFIG_FILE_PATH = os.path.join("config", "base_config.py")
# 如果在根目录下，请取消下面这行的注释：
# CONFIG_FILE_PATH = "base_config.py"
# ===========================================

class MediaCrawlerGUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("眭昕之达摩克利斯神剑-舆情检测3.0版本")
        self.window.geometry("850x700")
        
        # 进程控制
        self.process = None
        self.is_running = False
        
        self.setup_ui()
        
        # 启动时读取配置文件，同步界面状态
        self.load_current_config()
        
    def setup_ui(self):
        """设置用户界面"""
        # 1. 标题
        title_frame = ttk.Frame(self.window, padding="10")
        title_frame.pack(fill=tk.X)
        
        title_label = ttk.Label(
            title_frame,
            text="🎬 眭昕之达摩克利斯神剑-舆情检测3.0版本",
            font=("Microsoft YaHei", 14, "bold")
        )
        title_label.pack(side=tk.LEFT)
        
        # 2. 爬虫配置区域
        config_frame = ttk.LabelFrame(self.window, text="参数设置", padding="15")
        config_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # --- 关键词设置 ---
        ttk.Label(config_frame, text="搜索关键词:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.keywords_var = tk.StringVar()
        self.keywords_entry = ttk.Entry(config_frame, textvariable=self.keywords_var, width=50)
        self.keywords_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Label(config_frame, text="(英文逗号分隔)").grid(row=0, column=2, sticky=tk.W)
        
        # --- 平台选择 (点击这里会自动修改 config) ---
        ttk.Label(config_frame, text="目标平台:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.platform_var = tk.StringVar(value="xhs")
        
        platforms = [
            ("小红书(xhs)", "xhs"), 
            ("抖音(dy)", "dy"), 
            ("快手(ks)", "ks"),
            ("B站(bili)", "bili"), 
            ("微博(wb)", "wb"), 
            ("贴吧(tieba)", "tieba"), 
            ("知乎(zhihu)", "zhihu")
        ]
        
        platform_frame = ttk.Frame(config_frame)
        platform_frame.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5, columnspan=2)
        
        for i, (name, value) in enumerate(platforms):
            ttk.Radiobutton(
                platform_frame,
                text=name,
                value=value,
                variable=self.platform_var
            ).pack(side=tk.LEFT, padx=2)
        
        # 3. 数据存储选项
        ttk.Label(config_frame, text="存储方式:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.storage_var = tk.StringVar(value="csv")
        
        storage_frame = ttk.Frame(config_frame)
        storage_frame.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5, columnspan=2)
        
        for text, value in [("JSON", "json"), ("Excel", "excel"), ("数据库(DB)", "db")]:
            ttk.Radiobutton(
                storage_frame,
                text=text,
                value=value,
                variable=self.storage_var,
                command=self.on_storage_change
            ).pack(side=tk.LEFT, padx=5)
        
        # 4. 词云开关
        self.wordcloud_var = tk.BooleanVar(value=False)
        self.wordcloud_check = ttk.Checkbutton(
            config_frame,
            text="生成词云 (仅JSON)",
            variable=self.wordcloud_var,
            state="normal"
        )
        self.wordcloud_check.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        
        # 5. 数据库工具栏
        db_frame = ttk.Frame(config_frame)
        db_frame.grid(row=4, column=1, sticky=tk.W, padx=5, pady=5, columnspan=2)
        ttk.Button(db_frame, text="初始化 SQLite", command=self.init_sqlite_db).pack(side=tk.LEFT, padx=2)
        ttk.Button(db_frame, text="初始化 MySQL", command=self.init_mysql_db).pack(side=tk.LEFT, padx=2)
        
        # 6. 核心控制区
        control_frame = ttk.Frame(self.window)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.start_btn = ttk.Button(
            control_frame,
            text="✅ 保存配置并启动",
            command=self.start_crawler,
            style="Accent.TButton",
            width=20
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(
            control_frame,
            text="⛔ 停止",
            command=self.stop_crawler,
            state=tk.DISABLED,
            width=10
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        # --- 新增：打开数据目录按钮 ---
        self.open_dir_btn = ttk.Button(
            control_frame,
            text="📂 打开数据目录",
            command=self.open_data_folder,
            width=15
        )
        self.open_dir_btn.pack(side=tk.LEFT, padx=5)
        # ---------------------------
        
        self.progress = ttk.Progressbar(control_frame, mode='indeterminate', length=200)
        self.progress.pack(side=tk.LEFT, padx=20)
        
        # 7. 日志区
        log_frame = ttk.LabelFrame(self.window, text="实时日志", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=12, font=("Consolas", 9))
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # 8. 状态栏
        self.status_var = tk.StringVar(value="系统就绪")
        ttk.Label(self.window, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W).pack(side=tk.BOTTOM, fill=tk.X)

    def load_current_config(self):
        """启动时读取 base_config.py 的内容并显示在界面上"""
        if not os.path.exists(CONFIG_FILE_PATH):
            self.log(f"⚠️ 未找到配置文件: {CONFIG_FILE_PATH}")
            return

        try:
            with open(CONFIG_FILE_PATH, 'r', encoding='utf-8') as f:
                content = f.read()
                
                kw_match = re.search(r'KEYWORDS\s*=\s*["\'](.*?)["\']', content)
                if kw_match:
                    self.keywords_var.set(kw_match.group(1))
                    
                plat_match = re.search(r'PLATFORM\s*=\s*["\'](.*?)["\']', content)
                if plat_match:
                    current_plat = plat_match.group(1)
                    if any(current_plat == p[1] for p in [
                        ("xhs", "xhs"), ("dy", "dy"), ("ks", "ks"),
                        ("bili", "bili"), ("wb", "wb"), ("tieba", "tieba"), ("zhihu", "zhihu")
                    ]):
                        self.platform_var.set(current_plat)
                        
                store_match = re.search(r'SAVE_DATA_OPTION\s*=\s*["\'](.*?)["\']', content)
                if store_match:
                    self.storage_var.set(store_match.group(1))
                    
            self.log("✅ 已加载当前配置")
            
        except Exception as e:
            self.log(f"❌ 读取配置失败: {e}")

    def update_config_file(self):
        """将界面的设置写入 base_config.py"""
        if not os.path.exists(CONFIG_FILE_PATH):
            messagebox.showerror("错误", f"找不到配置文件: {CONFIG_FILE_PATH}")
            return False

        keywords = self.keywords_var.get().strip()
        platform = self.platform_var.get()
        storage = self.storage_var.get()
        
        if not keywords:
            messagebox.showwarning("警告", "请输入搜索关键词！")
            return False

        try:
            with open(CONFIG_FILE_PATH, 'r', encoding='utf-8') as f:
                content = f.read()
            
            content = re.sub(
                r'KEYWORDS\s*=\s*["\'].*?["\']', 
                f'KEYWORDS = "{keywords}"', 
                content
            )
            content = re.sub(
                r'PLATFORM\s*=\s*["\'].*?["\']', 
                f'PLATFORM = "{platform}"', 
                content
            )
            content = re.sub(
                r'SAVE_DATA_OPTION\s*=\s*["\'].*?["\']', 
                f'SAVE_DATA_OPTION = "{storage}"', 
                content
            )
            
            with open(CONFIG_FILE_PATH, 'w', encoding='utf-8') as f:
                f.write(content)
                
            self.log(f"📝 配置已更新 -> 平台: [{platform}] | 关键词: [{keywords}]")
            return True
            
        except Exception as e:
            self.log(f"❌ 更新配置文件失败: {str(e)}")
            return False

    def start_crawler(self):
        if self.is_running:
            return
        
        if not self.update_config_file():
            return

        self.is_running = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.progress.start()
        self.status_var.set(f"正在 {self.platform_var.get()} 爬取中...")
        
        thread = threading.Thread(target=self.run_crawler_thread, daemon=True)
        thread.start()

    def run_crawler_thread(self):
        try:
            cmd = [sys.executable, "main.py"]
            self.log(f"🚀 启动命令: {' '.join(cmd)}")
            
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                encoding='gbk', 
                errors='replace',
                bufsize=1,
                universal_newlines=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )
            
            for line in iter(self.process.stdout.readline, ''):
                if line:
                    self.log(line.strip())
            
            self.process.wait()
            
            if self.process.returncode == 0:
                self.log("✅ 爬虫任务完成！")
                self.status_var.set("任务完成")
            else:
                self.log(f"⚠️ 爬虫结束，代码: {self.process.returncode}")
                self.status_var.set("任务中断")
        
        except Exception as e:
            self.log(f"❌ 运行异常: {str(e)}")
        finally:
            self.window.after(0, self.on_crawler_finished)

    def stop_crawler(self):
        if self.process and self.is_running:
            self.log("🛑 正在停止...")
            self.process.terminate()
            self.is_running = False

    def on_crawler_finished(self):
        self.is_running = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.progress.stop()

    # --- 新增功能：打开数据文件夹 ---
    def open_data_folder(self):
        """打开根目录下的 data 文件夹"""
        data_path = os.path.join(os.getcwd(), "data")
        
        # 如果不存在，尝试创建
        if not os.path.exists(data_path):
            try:
                os.makedirs(data_path)
                self.log(f"已创建新目录: {data_path}")
            except Exception as e:
                self.log(f"❌ 创建目录失败: {e}")
                messagebox.showerror("错误", f"无法创建目录: {data_path}")
                return

        # 根据操作系统打开文件夹
        try:
            if sys.platform == 'win32':
                os.startfile(data_path)
            elif sys.platform == 'darwin':
                subprocess.run(['open', data_path])
            else:
                subprocess.run(['xdg-open', data_path])
            self.log("📂 已打开数据文件夹")
        except Exception as e:
            self.log(f"❌ 无法打开文件夹: {e}")
    # ----------------------------

    def on_storage_change(self):
        if self.storage_var.get() == "json":
            self.wordcloud_check.config(state="normal")
        else:
            self.wordcloud_var.set(False)
            self.wordcloud_check.config(state="disabled")

    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.window.after(0, self._update_log, f"[{timestamp}] {message}\n")
    
    def _update_log(self, message):
        self.log_text.insert(tk.END, message)
        self.log_text.see(tk.END)

    def init_sqlite_db(self):
        self.log("初始化 SQLite...")
        self.run_command([sys.executable, "main.py", "--init_db", "sqlite"])

    def init_mysql_db(self):
        self.log("初始化 MySQL...")
        self.run_command([sys.executable, "main.py", "--init_db", "mysql"])

    def run_command(self, cmd):
        def run():
            try:
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True, 
                    encoding='gbk', 
                    errors='replace'
                )
                self.log(result.stdout)
                if result.stderr: self.log(f"ERR: {result.stderr}")
            except Exception as e:
                self.log(f"❌ CMD错: {str(e)}")
        threading.Thread(target=run, daemon=True).start()

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = MediaCrawlerGUI()
    app.run()