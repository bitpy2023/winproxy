# proxy_frontend.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import math
import time
import asyncio
from proxy_backend import ProxyBackend
from datetime import datetime
import os

class ModernProxyFrontend:
    def __init__(self):
        self.backend = ProxyBackend()
        self.version = "2.1.0"
        self.setup_ui()
        
        
        # متغیرهای وضعیت جدید
        self.testing_active = False
        self.current_proxy = None
        
    def setup_ui(self):
        # ایجاد پنجره اصلی با طراحی مدرن
        self.root = tk.Tk()
        self.root.title(f"🌐 ProxyMaster Pro v{self.version}")
        self.root.geometry("1200x800")
        self.root.configure(bg='#0f0f23')
        self.root.minsize(1000, 700)
        
        # متغیرهای وضعیت
        self.is_connected = False
        self.current_filters = {}
        
        # پالت رنگ مدرن
        self.setup_colors()
        
        # استایل‌های سفارشی
        self.setup_styles()
        
        # ایجاد لایه‌های UI
        self.setup_sidebar()
        self.setup_main_content()
        self.setup_status_bar()
        
        # لود اولیه
        self.load_initial_proxies()
        
        # بایند کردن کلیدهای میانبر
        self.setup_keyboard_shortcuts()
        
    def setup_colors(self):
        """پالت رنگ مدرن"""
        self.colors = {
            'primary': '#6366f1',
            'primary_light': '#818cf8',
            'primary_dark': '#4f46e5',
            'success': '#10b981',
            'success_light': '#34d399',
            'danger': '#ef4444',
            'danger_light': '#f87171',
            'warning': '#f59e0b',
            'warning_light': '#fbbf24',
            'dark_bg': '#0f0f23',
            'dark_card': '#1e1e3f',
            'darker_card': '#161632',
            'light_bg': '#2a2a4a',
            'text_primary': '#f8fafc',
            'text_secondary': '#cbd5e1',
            'text_muted': '#64748b',
            'border': '#334155',
            'accent_purple': '#8b5cf6',
            'accent_blue': '#3b82f6',
            'accent_green': '#22c55e',
            'ping_good': '#10b981',
            'ping_medium': '#f59e0b',
            'ping_bad': '#ef4444',
            'anonymity_elite': '#10b981',
            'anonymity_anonymous': '#f59e0b',
            'anonymity_transparent': '#ef4444'
        }
        
    def setup_styles(self):
        """تنظیم استایل‌های سفارشی"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # استایل Treeview
        style.configure("Modern.Treeview",
                       background=self.colors['dark_card'],
                       foreground=self.colors['text_primary'],
                       fieldbackground=self.colors['dark_card'],
                       borderwidth=0,
                       rowheight=32)
        
        style.configure("Modern.Treeview.Heading",
                       background=self.colors['primary'],
                       foreground=self.colors['text_primary'],
                       relief='flat',
                       font=('Segoe UI', 10, 'bold'))
        
        style.map("Modern.Treeview",
                 background=[('selected', self.colors['primary_dark'])],
                 foreground=[('selected', self.colors['text_primary'])])
        
        # استایل Progressbar
        style.configure("Modern.Horizontal.TProgressbar",
                       background=self.colors['primary'],
                       troughcolor=self.colors['dark_card'],
                       borderwidth=0,
                       lightcolor=self.colors['primary_light'],
                       darkcolor=self.colors['primary_dark'])
        
    def setup_sidebar(self):
        """سایدبار مدرن"""
        self.sidebar = tk.Frame(self.root, bg=self.colors['darker_card'], width=300)
        self.sidebar.pack(side='left', fill='y', padx=0, pady=0)
        self.sidebar.pack_propagate(False)
        
        # لوگو و عنوان
        logo_frame = tk.Frame(self.sidebar, bg=self.colors['darker_card'], height=120)
        logo_frame.pack(fill='x', pady=(20, 10))
        logo_frame.pack_propagate(False)
        
        tk.Label(logo_frame, text="🌐", font=('Segoe UI', 32),
                bg=self.colors['darker_card'], fg=self.colors['primary']).pack(pady=(10, 0))
        
        tk.Label(logo_frame, text="ProxyMaster", font=('Segoe UI', 20, 'bold'),
                bg=self.colors['darker_card'], fg=self.colors['text_primary']).pack()
        
        tk.Label(logo_frame, text="PRO", font=('Segoe UI', 12, 'bold'),
                bg=self.colors['darker_card'], fg=self.colors['accent_purple']).pack()
        
        # منوی اصلی
        self.setup_sidebar_menu()
        
        # تنظیمات سریع
        self.setup_quick_settings()
        
        # آمار سریع
        self.setup_quick_stats()
        
    def setup_sidebar_menu(self):
        """منوی سایدبار"""
        menu_frame = tk.Frame(self.sidebar, bg=self.colors['darker_card'])
        menu_frame.pack(fill='x', padx=20, pady=20)
        
        menu_items = [
            ("📂 Load Proxies", self.load_proxies),
            ("📋 Import Clipboard", self.import_from_clipboard),
            ("➕ Add Proxy", self.add_proxy_dialog),
            ("🚀 Start Test", self.start_test),
            ("⏹️ Stop Test", self.stop_test),
            ("💾 Export Results", self.export_results),
            ("🔄 Refresh Status", self.update_connection_status),
            ("🧹 Clear All", self.clear_all_data),
            ("ℹ️ About", self.show_about),
        ]
        
        for text, command in menu_items:
            btn = self.create_modern_button(menu_frame, text, command, 
                                          self.colors['dark_card'], 
                                          self.colors['primary'])
            btn.pack(fill='x', pady=4)
            
    def setup_quick_settings(self):
        """تنظیمات سریع در سایدبار"""
        settings_frame = tk.Frame(self.sidebar, bg=self.colors['darker_card'])
        settings_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(settings_frame, text="⚙️ Quick Settings", font=('Segoe UI', 12, 'bold'),
                bg=self.colors['darker_card'], fg=self.colors['text_primary']).pack(anchor='w', pady=(0, 10))
        
        # تنظیمات صدا
        self.sound_var = tk.BooleanVar(value=self.backend.settings['enable_sound'])
        sound_cb = tk.Checkbutton(settings_frame, text="Enable Sound", 
                                 variable=self.sound_var,
                                 command=self.toggle_sound,
                                 bg=self.colors['darker_card'],
                                 fg=self.colors['text_primary'],
                                 selectcolor=self.colors['dark_card'],
                                 activebackground=self.colors['darker_card'],
                                 activeforeground=self.colors['text_primary'])
        sound_cb.pack(anchor='w', pady=2)
        
        # تنظیمات HTTPS
        self.https_var = tk.BooleanVar(value=self.backend.settings['test_https'])
        https_cb = tk.Checkbutton(settings_frame, text="Test HTTPS", 
                                 variable=self.https_var,
                                 command=self.toggle_https,
                                 bg=self.colors['darker_card'],
                                 fg=self.colors['text_primary'],
                                 selectcolor=self.colors['dark_card'],
                                 activebackground=self.colors['darker_card'],
                                 activeforeground=self.colors['text_primary'])
        https_cb.pack(anchor='w', pady=2)
        
    def setup_quick_stats(self):
        """آمار سریع در سایدبار"""
        stats_frame = tk.Frame(self.sidebar, bg=self.colors['darker_card'])
        stats_frame.pack(side='bottom', fill='x', padx=20, pady=20)
        
        tk.Label(stats_frame, text="📊 Quick Stats", font=('Segoe UI', 12, 'bold'),
                bg=self.colors['darker_card'], fg=self.colors['text_primary']).pack(anchor='w', pady=(0, 10))
        
        self.quick_stats = {
            'total': self.create_stat_item(stats_frame, "Total Proxies", "0"),
            'active': self.create_stat_item(stats_frame, "Active", "0"),
            'success_rate': self.create_stat_item(stats_frame, "Success Rate", "0%"),
            'best_ping': self.create_stat_item(stats_frame, "Best Ping", "- ms"),
            'best_http': self.create_stat_item(stats_frame, "Best HTTP", "- ms")
        }
        
        # وضعیت پروکسی فعلی
        self.current_proxy_label = tk.Label(stats_frame, text="🔴 No Proxy Set", 
                                          font=('Segoe UI', 10),
                                          bg=self.colors['darker_card'],
                                          fg=self.colors['text_muted'])
        self.current_proxy_label.pack(anchor='w', pady=(10, 0))
        
    def create_stat_item(self, parent, label, value):
        """ایجاد آیتم آمار"""
        frame = tk.Frame(parent, bg=self.colors['darker_card'])
        frame.pack(fill='x', pady=6)
        
        tk.Label(frame, text=label, font=('Segoe UI', 9),
                bg=self.colors['darker_card'], fg=self.colors['text_secondary']).pack(anchor='w')
        
        value_label = tk.Label(frame, text=value, font=('Segoe UI', 11, 'bold'),
                             bg=self.colors['darker_card'], fg=self.colors['primary'])
        value_label.pack(anchor='w')
        
        return value_label
        
    def setup_main_content(self):
        """محتوای اصلی"""
        main_frame = tk.Frame(self.root, bg=self.colors['dark_bg'])
        main_frame.pack(side='right', fill='both', expand=True, padx=20, pady=20)
        
        # هدر اصلی
        self.setup_main_header(main_frame)
        
        # کارت‌های وضعیت
        self.setup_status_cards(main_frame)
        
        # دکمه GO مرکزی
        self.setup_go_section(main_frame)
        
        # فیلترهای سریع
        self.setup_quick_filters(main_frame)
        
        # نتایج
        self.setup_results_section(main_frame)
        
    def setup_main_header(self, parent):
        """هدر اصلی"""
        header_frame = tk.Frame(parent, bg=self.colors['dark_bg'], height=80)
        header_frame.pack(fill='x', pady=(0, 20))
        header_frame.pack_propagate(False)
        
        # عنوان و وضعیت
        title_frame = tk.Frame(header_frame, bg=self.colors['dark_bg'])
        title_frame.pack(side='left', fill='y')
        
        tk.Label(title_frame, text="Proxy Dashboard", font=('Segoe UI', 24, 'bold'),
                bg=self.colors['dark_bg'], fg=self.colors['text_primary']).pack(anchor='w')
        
        self.connection_status = tk.Label(title_frame, text="● Checking connection...", 
                                        font=('Segoe UI', 11),
                                        fg=self.colors['text_muted'],
                                        bg=self.colors['dark_bg'])
        self.connection_status.pack(anchor='w', pady=(5, 0))
        
        # دکمه‌های عمل سریع
        action_frame = tk.Frame(header_frame, bg=self.colors['dark_bg'])
        action_frame.pack(side='right', fill='y')
        
        self.create_modern_button(action_frame, "🚫 Disable Proxy", 
                                self.disable_proxy, 
                                self.colors['danger'], 
                                self.colors['danger_light'], small=True).pack(side='left', padx=5)
        
        self.create_modern_button(action_frame, "⚡ Auto Set Best", 
                                self.auto_set_best_proxy, 
                                self.colors['success'], 
                                self.colors['success_light'], small=True).pack(side='left', padx=5)
        
        self.create_modern_button(action_frame, "🧹 Clear Results", 
                                self.clear_results, 
                                self.colors['warning'], 
                                self.colors['warning_light'], small=True).pack(side='left', padx=5)
        
    def setup_status_cards(self, parent):
        """کارت‌های وضعیت"""
        cards_frame = tk.Frame(parent, bg=self.colors['dark_bg'])
        cards_frame.pack(fill='x', pady=(0, 20))
        
        cards_data = [
            {"title": "🌐 Connection", "value": "Checking...", "color": self.colors['primary'], "key": "connection"},
            {"title": "⚡ Performance", "value": "Ready", "color": self.colors['success'], "key": "performance"},
            {"title": "🛡️ Security", "value": "Protected", "color": self.colors['accent_purple'], "key": "security"},
            {"title": "📈 Efficiency", "value": "Optimal", "color": self.colors['accent_blue'], "key": "efficiency"}
        ]
        
        self.status_cards = {}
        for i, data in enumerate(cards_data):
            card_dict = self.create_status_card(cards_frame, data)
            card_dict['frame'].pack(side='left', fill='x', expand=True, padx=(0, 15) if i < len(cards_data)-1 else (0, 0))
            self.status_cards[data['key']] = card_dict

    def create_status_card(self, parent, data):
        """ایجاد کارت وضعیت"""
        card = tk.Frame(parent, bg=self.colors['dark_card'], relief='flat', 
                    bd=1, highlightbackground=self.colors['border'],
                    highlightthickness=1)
        card.configure(width=200, height=100)
        
        title_label = tk.Label(card, text=data["title"], font=('Segoe UI', 12, 'bold'),
                bg=self.colors['dark_card'], fg=self.colors['text_secondary'])
        title_label.pack(anchor='w', pady=(15, 5), padx=15)
        
        value_label = tk.Label(card, text=data["value"], font=('Segoe UI', 16, 'bold'),
                            bg=self.colors['dark_card'], fg=data["color"])
        value_label.pack(anchor='w', padx=15)
        
        # نوار پیشرفت کوچک
        progress_frame = tk.Frame(card, bg=self.colors['dark_card'], height=4)
        progress_frame.pack(fill='x', side='bottom', pady=(10, 0))
        progress_frame.pack_propagate(False)
        
        progress_bar = tk.Frame(progress_frame, bg=data["color"], height=4)
        progress_bar.pack(fill='x', padx=15)
        
        return {
            'frame': card,
            'value_label': value_label,
            'progress_bar': progress_bar
        }        
    def setup_go_section(self, parent):
        """بخش دکمه GO"""
        go_frame = tk.Frame(parent, bg=self.colors['dark_bg'])
        go_frame.pack(fill='x', pady=30)
        
        # دایره GO مدرن
        self.go_canvas = tk.Canvas(go_frame, width=200, height=200, 
                                  bg=self.colors['dark_bg'], highlightthickness=0)
        self.go_canvas.pack()
        
        # ایجاد افکت گرادیان دایره‌ای
        self.create_modern_go_circle()
        
        # متن وضعیت
        self.go_status = tk.Label(go_frame, text="Click for Smart Connect", 
                                font=('Segoe UI', 12),
                                fg=self.colors['text_muted'],
                                bg=self.colors['dark_bg'])
        self.go_status.pack(pady=10)
        
    def create_modern_go_circle(self):
        """ایجاد دایره GO مدرن"""
        # دایره بیرونی با گرادیان
        self.outer_circle = self.go_canvas.create_oval(10, 10, 190, 190, 
                                                     outline=self.colors['primary'],
                                                     width=3, fill=self.colors['dark_card'])
        
        # دایره داخلی
        self.inner_circle = self.go_canvas.create_oval(30, 30, 170, 170, 
                                                     outline=self.colors['primary_light'],
                                                     width=2, fill=self.colors['dark_card'])
        
        # متن GO
        self.go_text = self.go_canvas.create_text(100, 100, text="GO", 
                                                font=('Segoe UI', 28, 'bold'),
                                                fill=self.colors['primary'])
        
        # افکت‌های بصری
        self.create_circle_effects()
        
        # بایند کردن کلیک - فقط برای اتصال هوشمند
        self.go_canvas.tag_bind(self.outer_circle, "<Button-1>", self.smart_connect)
        self.go_canvas.tag_bind(self.inner_circle, "<Button-1>", self.smart_connect)
        self.go_canvas.tag_bind(self.go_text, "<Button-1>", self.smart_connect)
        
    def create_circle_effects(self):
        """ایجاد افکت‌های بصری برای دایره"""
        # نقاط درخشان
        for i in range(8):
            angle = i * 45
            rad = angle * 3.14159 / 180
            x = 100 + 80 * math.cos(rad)
            y = 100 + 80 * math.sin(rad)
            
            self.go_canvas.create_oval(x-2, y-2, x+2, y+2, 
                                     fill=self.colors['primary_light'],
                                     outline="", tags="glow_points")
        
    def setup_quick_filters(self, parent):
        """فیلترهای سریع"""
        filters_frame = tk.Frame(parent, bg=self.colors['dark_bg'])
        filters_frame.pack(fill='x', pady=(0, 15))
        
        tk.Label(filters_frame, text="🔍 Quick Filters:", 
                font=('Segoe UI', 11, 'bold'),
                fg=self.colors['text_primary'],
                bg=self.colors['dark_bg']).pack(side='left', padx=(0, 10))
        
        # فیلتر Active Only
        self.active_filter_var = tk.BooleanVar()
        active_cb = tk.Checkbutton(filters_frame, text="Active Only",
                                  variable=self.active_filter_var,
                                  command=self.apply_filters,
                                  bg=self.colors['dark_bg'],
                                  fg=self.colors['text_primary'],
                                  selectcolor=self.colors['dark_card'],
                                  activebackground=self.colors['dark_bg'],
                                  activeforeground=self.colors['text_primary'])
        active_cb.pack(side='left', padx=5)
        
        # فیلتر پینگ
        tk.Label(filters_frame, text="Max Ping:",
                font=('Segoe UI', 9),
                fg=self.colors['text_muted'],
                bg=self.colors['dark_bg']).pack(side='left', padx=(10, 5))
        
        self.ping_filter_var = tk.StringVar(value="")
        ping_combo = ttk.Combobox(filters_frame, textvariable=self.ping_filter_var,
                                 values=['', '100', '200', '300', '500'],
                                 state='readonly', width=8)
        ping_combo.pack(side='left', padx=5)
        ping_combo.bind('<<ComboboxSelected>>', self.apply_filters)
        
        # دکمه پاک کردن فیلترها
        self.create_modern_button(filters_frame, "Clear Filters", 
                                self.clear_filters,
                                self.colors['dark_card'],
                                self.colors['primary_light'], small=True).pack(side='left', padx=10)
        
    def setup_results_section(self, parent):
        """بخش نتایج"""
        results_frame = tk.Frame(parent, bg=self.colors['dark_bg'])
        results_frame.pack(fill='both', expand=True)
        
        # هدر نتایج
        results_header = tk.Frame(results_frame, bg=self.colors['dark_bg'])
        results_header.pack(fill='x', pady=(0, 15))
        
        tk.Label(results_header, text="📋 Test Results", 
                font=('Segoe UI', 16, 'bold'),
                fg=self.colors['text_primary'],
                bg=self.colors['dark_bg']).pack(side='left')
        
        # کنترل‌های فیلتر و سورت
        control_frame = tk.Frame(results_header, bg=self.colors['dark_bg'])
        control_frame.pack(side='right')
        
        tk.Label(control_frame, text="Sort by:", font=('Segoe UI', 10),
                fg=self.colors['text_muted'], bg=self.colors['dark_bg']).pack(side='left', padx=5)
        
        self.sort_var = tk.StringVar(value='http_time')
        sort_combo = ttk.Combobox(control_frame, textvariable=self.sort_var,
                                 values=['ping', 'http_time', 'status', 'proxy', 'country'], 
                                 state='readonly', width=12)
        sort_combo.pack(side='left', padx=5)
        sort_combo.bind('<<ComboboxSelected>>', self.sort_results)
        
        # جدول نتایج
        self.setup_results_table(results_frame)
        
    def setup_results_table(self, parent):
        """جدول نتایج مدرن"""
        table_container = tk.Frame(parent, bg=self.colors['dark_bg'])
        table_container.pack(fill='both', expand=True)
        
        # ایجاد Treeview با استایل مدرن
        columns = ('#', 'Proxy', 'Country', 'Ping', 'HTTP Time', 'Anonymity', 'Status')
        self.results_tree = ttk.Treeview(table_container, columns=columns, 
                                       show='headings', height=12, style="Modern.Treeview")
        
        # تنظیم ستون‌ها
        column_config = {
            '#': {'width': 50, 'anchor': 'center'},
            'Proxy': {'width': 200, 'anchor': 'w'},
            'Country': {'width': 120, 'anchor': 'center'},
            'Ping': {'width': 80, 'anchor': 'center'},
            'HTTP Time': {'width': 100, 'anchor': 'center'},
            'Anonymity': {'width': 100, 'anchor': 'center'},
            'Status': {'width': 100, 'anchor': 'center'}
        }
        
        for col in columns:
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, **column_config[col])
        
        # اسکرول بارهای مدرن
        v_scrollbar = ttk.Scrollbar(table_container, orient="vertical", 
                                  command=self.results_tree.yview)
        h_scrollbar = ttk.Scrollbar(table_container, orient="horizontal", 
                                  command=self.results_tree.xview)
        
        self.results_tree.configure(yscrollcommand=v_scrollbar.set, 
                                  xscrollcommand=h_scrollbar.set)
        
        # قرارگیری در grid
        self.results_tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        table_container.grid_rowconfigure(0, weight=1)
        table_container.grid_columnconfigure(0, weight=1)
        
        # منوی راست‌کلیک
        self.setup_context_menu()
        
    def setup_context_menu(self):
        """منوی راست‌کلیک برای جدول"""
        self.context_menu = tk.Menu(self.root, tearoff=0, bg=self.colors['dark_card'], fg=self.colors['text_primary'])
        self.context_menu.add_command(label="📋 Copy Proxy", command=self.copy_selected_proxy)
        self.context_menu.add_command(label="📋 Copy IP Only", command=self.copy_selected_ip)
        self.context_menu.add_command(label="🔧 Set as System Proxy", command=self.set_selected_proxy)
        self.context_menu.add_command(label="🔄 Test Again", command=self.retest_selected_proxy)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="✅ Select All Working", command=self.select_all_working)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="🗑️ Remove from List", command=self.remove_selected_proxy)
        
        self.results_tree.bind("<Button-3>", self.show_context_menu)
        self.results_tree.bind('<Double-1>', self.on_proxy_double_click)
        
    def setup_status_bar(self):
        """نوار وضعیت پایین"""
        self.status_bar = tk.Frame(self.root, bg=self.colors['darker_card'], height=40)
        self.status_bar.pack(side='bottom', fill='x', padx=0, pady=0)
        self.status_bar.pack_propagate(False)
        
        # نوار پیشرفت
        self.progress_frame = tk.Frame(self.status_bar, bg=self.colors['darker_card'])
        self.progress_frame.pack(fill='x', padx=20, pady=8)
        
        self.progress_label = tk.Label(self.progress_frame, text="Ready to start testing", 
                                      font=('Segoe UI', 9),
                                      fg=self.colors['text_muted'],
                                      bg=self.colors['darker_card'])
        self.progress_label.pack(side='left')
        
        self.progress_bar = ttk.Progressbar(self.progress_frame, mode='determinate',
                                          style="Modern.Horizontal.TProgressbar")
        self.progress_bar.pack(side='right', fill='x', expand=True, padx=(10, 0))
        
        # شمارنده تست زنده
        self.live_counter = tk.Label(self.progress_frame, text="", 
                                   font=('Segoe UI', 9),
                                   fg=self.colors['primary'],
                                   bg=self.colors['darker_card'])
        self.live_counter.pack(side='right', padx=(10, 0))
        
        # مخفی کردن در حالت عادی
        self.hide_progress_bar()
        
    def setup_keyboard_shortcuts(self):
        """تنظیم میانبرهای کیبورد"""
        self.root.bind('<F5>', lambda e: self.start_test())
        self.root.bind('<Delete>', lambda e: self.remove_selected_proxy())
        self.root.bind('<Control-a>', lambda e: self.select_all_working())
        self.root.bind('<Control-c>', lambda e: self.copy_selected_proxy())
        
    def create_modern_button(self, parent, text, command, bg_color, hover_color, small=False):
        """ایجاد دکمه مدرن"""
        btn = tk.Button(parent, text=text, command=command,
                       bg=bg_color, fg=self.colors['text_primary'],
                       font=('Segoe UI', 10 if not small else 9),
                       relief='flat', border=0, cursor='hand2',
                       padx=20 if not small else 15, pady=10 if not small else 8)
        
        # افکت hover
        def on_enter(e):
            btn.configure(bg=hover_color)
            
        def on_leave(e):
            btn.configure(bg=bg_color)
            
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        
        return btn
        
    def update_go_animation(self, status):
        """آپدیت انیمیشن دکمه GO"""
        colors = {
            'testing': (self.colors['warning'], self.colors['warning_light']),
            'connected': (self.colors['success'], self.colors['success_light']),
            'disconnected': (self.colors['danger'], self.colors['danger_light']),
            'ready': (self.colors['primary'], self.colors['primary_light'])
        }
        
        primary_color, secondary_color = colors.get(status, (self.colors['primary'], self.colors['primary_light']))
        
        self.go_canvas.itemconfig(self.outer_circle, outline=primary_color)
        self.go_canvas.itemconfig(self.inner_circle, outline=secondary_color)
        self.go_canvas.itemconfig(self.go_text, fill=primary_color)
        
        # آپدیت متن وضعیت
        status_texts = {
            'testing': "Testing proxies...",
            'connected': f"Connected via {self.current_proxy}" if self.current_proxy else "Connected",
            'disconnected': "Proxy disabled",
            'ready': "Click for Smart Connect"
        }
        self.go_status.config(text=status_texts.get(status, "Ready"))
        
    def show_progress_bar(self):
        """نمایش نوار پیشرفت"""
        self.progress_frame.pack(fill='x', padx=20, pady=8)
        
    def hide_progress_bar(self):
        """مخفی کردن نوار پیشرفت"""
        self.progress_frame.pack_forget()
        
    def update_connection_status(self):
        """آپدیت وضعیت اتصال"""
        def check_status():
            is_connected, status_text = self.backend.get_connection_status()
            self.root.after(0, lambda: self.update_status_display(is_connected, status_text))
        
        threading.Thread(target=check_status, daemon=True).start()
        
    def update_status_display(self, is_connected, status_text):
        """آپدیت نمایش وضعیت"""
        self.is_connected = is_connected
        status_color = self.colors['success'] if is_connected else self.colors['danger']
        status_icon = "●" if is_connected else "○"
        
        self.connection_status.config(
            text=f"{status_icon} {status_text}",
            fg=status_color
        )
        
        # آپدیت کارت وضعیت اتصال
        if 'connection' in self.status_cards:
            card = self.status_cards['connection']
            card['value_label'].config(
                text="Connected" if is_connected else "Disconnected",
                fg=status_color
            )
        
    def load_initial_proxies(self):
        """لود اولیه پروکسی‌ها"""
        success, message = self.backend.load_proxies_from_file()
        if success and "loaded" in message.lower():
            self.update_quick_stats()
        
    def load_proxies(self):
        """لود پروکسی‌ها از فایل"""
        filename = filedialog.askopenfilename(
            title="Select Proxy List File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            success, message = self.backend.load_proxies_from_file(filename)
            if success:
                self.show_notification("Success", message, "success")
                self.update_quick_stats()
            else:
                self.show_notification("Error", message, "error")
                
    def import_from_clipboard(self):
        """ایمپورت از کلیپ‌بورد"""
        success, message = self.backend.import_from_clipboard()
        if success:
            self.show_notification("Success", message, "success")
            self.update_quick_stats()
        else:
            self.show_notification("Error", message, "error")
                
    def add_proxy_dialog(self):
        """دیالوگ اضافه کردن پروکسی مدرن"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Proxy")
        dialog.geometry("400x200")
        dialog.configure(bg=self.colors['dark_card'])
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # center the dialog
        dialog.geometry(f"+{self.root.winfo_x()+200}+{self.root.winfo_y()+200}")
        
        tk.Label(dialog, text="Add New Proxy", font=('Segoe UI', 16, 'bold'),
                fg=self.colors['text_primary'], bg=self.colors['dark_card']).pack(pady=20)
        
        tk.Label(dialog, text="Enter proxy address (IP:PORT or host:PORT):", font=('Segoe UI', 11),
                fg=self.colors['text_secondary'], bg=self.colors['dark_card']).pack(pady=10)
        
        entry_frame = tk.Frame(dialog, bg=self.colors['dark_card'])
        entry_frame.pack(pady=10)
        
        entry = tk.Entry(entry_frame, font=('Segoe UI', 12), width=25, 
                        bg=self.colors['light_bg'], fg=self.colors['text_primary'],
                        insertbackground=self.colors['text_primary'],
                        relief='flat', bd=2, highlightbackground=self.colors['border'],
                        highlightthickness=1)
        entry.pack(padx=10, pady=5)
        entry.focus()
        
        def add_proxy():
            proxy = entry.get().strip()
            if proxy:
                success, message = self.backend.add_proxy_manual(proxy)
                if success:
                    self.show_notification("Success", message, "success")
                    self.update_quick_stats()
                    dialog.destroy()
                else:
                    self.show_notification("Error", message, "error")
        
        btn_frame = tk.Frame(dialog, bg=self.colors['dark_card'])
        btn_frame.pack(pady=20)
        
        self.create_modern_button(btn_frame, "Add Proxy", add_proxy, 
                                self.colors['success'], self.colors['success_light']).pack(side='left', padx=10)
        
        self.create_modern_button(btn_frame, "Cancel", dialog.destroy, 
                                self.colors['danger'], self.colors['danger_light']).pack(side='left', padx=10)
        
        dialog.bind('<Return>', lambda e: add_proxy())
        dialog.bind('<Escape>', lambda e: dialog.destroy())
        
    def start_test(self, event=None):
        """شروع تست"""
        if self.testing_active:
            self.show_notification("Info", "Test is already in progress", "info")
            return
            
        if not self.backend.proxy_list:
            self.show_notification("Error", "No proxies loaded. Please load proxies first.", "error")
            return
            
        self.testing_active = True
        self.update_go_animation('testing')
        self.show_progress_bar()
        self.progress_bar['value'] = 0
        
        # پاک کردن نتایج قبلی
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        # ریست کردن نتایج قبلی در بک‌اند
        self.backend.test_results.clear()
        
        # اجرای تست در thread جداگانه
        def run_async_test():
            try:
                # ایجاد event loop جدید
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                async def run_test():
                    return await self.backend.run_full_test_async(
                        progress_callback=self.update_progress,
                        result_callback=self.add_result_to_table
                    )
                
                result = loop.run_until_complete(run_test())
                
                # بستن صحیح event loop
                loop.stop()
                loop.close()
                
                # ارسال نتیجه به UI thread
                self.root.after(0, lambda: self.test_completed(result))
                
            except Exception as e:
                self.root.after(0, lambda: self.test_completed((False, {"error": str(e)})))
        
        threading.Thread(target=run_async_test, daemon=True).start()
            
    def stop_test(self):
        """توقف تست"""
        if self.testing_active:
            self.backend.stop_testing()
            self.testing_active = False
            self.update_go_animation('ready')
            self.hide_progress_bar()
            self.live_counter.config(text="")
            self.show_notification("Info", "Test stopped", "info")

    def smart_connect(self, event=None):
        """اتصال هوشمند - بهترین پروکسی را پیدا کرده و متصل می‌شود"""
        best_proxy = self.backend.get_smart_best_proxy()
        
        if not best_proxy:
            self.update_go_animation('disconnected')
            self.show_notification("Error", "No active proxy found. Please run a test first.", "error")
            return
        
        # ست کردن بهترین پروکسی
        success, message = self.backend.set_windows_proxy(best_proxy)
        if success:
            self.current_proxy = best_proxy
            self.update_go_animation('connected')
            self.update_current_proxy_display()
            
            # پیدا کردن اطلاعات کشور برای نمایش
            country_info = "Unknown"
            for result in self.backend.test_results:
                if result.proxy == best_proxy and result.country != "Unknown":
                    country_info = result.country
                    break
            
            self.show_notification("Success", f"Connected to: {best_proxy} ({country_info})", "success")
        else:
            self.show_notification("Error", message, "error")

    def update_progress(self, current, total):
        """آپدیت نوار پیشرفت"""
        def update_ui():
            try:
                percent = (current / total) * 100
                self.progress_bar['value'] = percent
                self.progress_label.config(text=f"Testing {current}/{total} proxies")
                self.live_counter.config(text=f"Testing {current}/{total}")
            except:
                pass  # جلوگیری از خطا اگر ویجت از بین رفته باشد
        
        self.root.after(0, update_ui)

    def add_result_to_table(self, result):
        """اضافه کردن نتیجه به جدول"""
        def add_to_ui():
            try:
                # تعیین آیکون وضعیت و رنگ
                if result.get('status') == 'Active':
                    status_icon = "✅"
                    status_color = self.colors['success']
                else:
                    status_icon = "❌"
                    status_color = self.colors['danger']
                
                # تعیین رنگ پینگ
                ping = result.get('ping', 0)
                if ping < 120:
                    ping_color = self.colors['ping_good']
                elif ping < 350:
                    ping_color = self.colors['ping_medium']
                else:
                    ping_color = self.colors['ping_bad']
                
                # تعیین رنگ anonymity
                anonymity = result.get('anonymity', 'Unknown')
                if anonymity == 'Elite':
                    anonymity_color = self.colors['anonymity_elite']
                elif anonymity == 'Anonymous':
                    anonymity_color = self.colors['anonymity_anonymous']
                else:
                    anonymity_color = self.colors['anonymity_transparent']
                
                # اضافه کردن به جدول
                item_id = self.results_tree.insert('', 'end', values=(
                    len(self.backend.test_results),
                    result.get('proxy', ''),
                    self.get_country_flag(result.get('country_code', 'XX')) + " " + result.get('country', 'Unknown'),
                    f"{ping}ms",
                    f"{result.get('http_time', 0)}ms",
                    result.get('anonymity', 'Unknown'),
                    f"{status_icon} {result.get('status', 'Unknown')}"
                ))
                
                # اسکرول به آخر
                self.results_tree.see(item_id)
                
            except Exception as e:
                print(f"Error adding result to table: {e}")
        
        self.root.after(0, add_to_ui)

    def get_country_flag(self, country_code: str) -> str:
        """دریافت پرچم کشور بر اساس کد"""
        flag_emojis = {
            'US': '🇺🇸', 'GB': '🇬🇧', 'DE': '🇩🇪', 'FR': '🇫🇷', 'JP': '🇯🇵',
            'CN': '🇨🇳', 'RU': '🇷🇺', 'BR': '🇧🇷', 'IN': '🇮🇳', 'IR': '🇮🇷',
            'TR': '🇹🇷', 'CA': '🇨🇦', 'AU': '🇦🇺', 'NL': '🇳🇱', 'SE': '🇸🇪',
            'IT': '🇮🇹', 'ES': '🇪🇸', 'KR': '🇰🇷', 'SA': '🇸🇦', 'AE': '🇦🇪'
        }
        return flag_emojis.get(country_code.upper(), '🌐')
        
    def test_completed(self, result):
        """پایان تست"""
        self.testing_active = False
        self.update_go_animation('ready')
        self.hide_progress_bar()
        self.live_counter.config(text="")
        
        success, stats = result
        
        if success and stats:
            self.update_quick_stats()
            
            # آپدیت کارت‌های وضعیت
            self.update_status_cards_with_stats(stats)
            
            # سورت خودکار بر اساس http_time
            self.sort_var.set('http_time')
            self.sort_results()
            
            # ذخیره خودکار پروکسی‌های سالم
            if stats.get('active', 0) > 0:
                save_success, save_message = self.backend.save_working_proxies()
                if save_success:
                    notification_text = (f"Test completed!\n"
                                    f"Active: {stats.get('active', 0)}/{stats.get('total', 0)}\n"
                                    f"Best HTTP Time: {stats.get('best_http_time', 0)}ms")
                    self.show_notification("Test Complete", notification_text, "success")
        else:
            error_msg = stats.get('error', 'Unknown error') if isinstance(stats, dict) else 'Test failed'
            self.show_notification("Error", f"Proxy testing failed: {error_msg}", "error")

    def update_status_cards_with_stats(self, stats):
        """آپدیت کارت‌های وضعیت با آمار جدید"""
        if not stats:
            return
            
        if 'performance' in self.status_cards:
            performance_card = self.status_cards['performance']
            if stats.get('active', 0) > 0:
                performance_text = f"{stats.get('best_http_time', 0)}ms Best"
                performance_card['value_label'].config(text=performance_text)
        
        if 'efficiency' in self.status_cards:
            efficiency_card = self.status_cards['efficiency']
            efficiency_text = f"{stats.get('success_rate', 0):.1f}% Success"
            efficiency_card['value_label'].config(text=efficiency_text)
            
        if 'security' in self.status_cards:
            security_card = self.status_cards['security']
            active_count = stats.get('active', 0)
            if active_count > 10:
                security_text = "Excellent"
            elif active_count > 3:
                security_text = "Good"
            else:
                security_text = "Basic"
            security_card['value_label'].config(text=security_text)
            
    def disable_proxy(self):
        """غیرفعال کردن پروکسی"""
        success, message = self.backend.disable_windows_proxy()
        if success:
            self.current_proxy = None
            self.update_go_animation('disconnected')
            self.update_current_proxy_display()
            self.show_notification("Success", message, "success")
        else:
            self.show_notification("Error", message, "error")
            
    def auto_set_best_proxy(self):
        """تنظیم اتوماتیک بهترین پروکسی"""
        if not self.backend.best_proxy:
            self.show_notification("Error", "No best proxy available. Run a test first.", "error")
            return
            
        success, message = self.backend.set_windows_proxy(self.backend.best_proxy)
        if success:
            self.current_proxy = self.backend.best_proxy
            self.update_go_animation('connected')
            self.update_current_proxy_display()
            # آپدیت کارت Performance
            self.update_status_cards_with_stats(self.backend.get_stats())
            self.show_notification("Success", message, "success")
        else:
            self.show_notification("Error", message, "error")
            
    def update_current_proxy_display(self):
        """آپدیت نمایش پروکسی فعلی"""
        if self.current_proxy:
            self.current_proxy_label.config(
                text=f"🟢 {self.current_proxy}",
                fg=self.colors['success']
            )
        else:
            self.current_proxy_label.config(
                text="🔴 No Proxy Set",
                fg=self.colors['text_muted']
            )
            
    def on_proxy_double_click(self, event):
        """دابل کلیک روی پروکسی برای تنظیم"""
        item = self.results_tree.selection()
        if item:
            values = self.results_tree.item(item, 'values')
            proxy = values[1]  # ستون Proxy
            
            success, message = self.backend.set_windows_proxy(proxy)
            if success:
                self.current_proxy = proxy
                self.update_go_animation('connected')
                self.update_current_proxy_display()
                self.show_notification("Success", f"Proxy set: {proxy}", "success")
            else:
                self.show_notification("Error", message, "error")
                
    def show_context_menu(self, event):
        """نمایش منوی راست‌کلیک"""
        item = self.results_tree.identify_row(event.y)
        if item:
            self.results_tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
                
    def copy_selected_proxy(self):
        """کپی کردن پروکسی انتخاب شده"""
        item = self.results_tree.selection()
        if item:
            values = self.results_tree.item(item, 'values')
            proxy = values[1]  # ستون Proxy
            self.root.clipboard_clear()
            self.root.clipboard_append(proxy)
            self.show_notification("Success", f"Copied: {proxy}", "success")
            
    def copy_selected_ip(self):
        """کپی کردن فقط IP پروکسی انتخاب شده"""
        item = self.results_tree.selection()
        if item:
            values = self.results_tree.item(item, 'values')
            proxy = values[1]  # ستون Proxy
            ip = proxy.split(':')[0]
            self.root.clipboard_clear()
            self.root.clipboard_append(ip)
            self.show_notification("Success", f"Copied IP: {ip}", "success")
            
    def set_selected_proxy(self):
        """تنظیم پروکسی انتخاب شده"""
        self.on_proxy_double_click(None)
        
    def retest_selected_proxy(self):
        """تست مجدد پروکسی انتخاب شده"""
        item = self.results_tree.selection()
        if item:
            values = self.results_tree.item(item, 'values')
            proxy = values[1]  # ستون Proxy
            
            def test_single():
                result = self.backend.test_single_proxy(proxy)
                self.root.after(0, lambda: self.update_single_proxy_result(proxy, result))
            
            threading.Thread(target=test_single, daemon=True).start()
            self.show_notification("Info", f"Testing {proxy}...", "info")
            
    def update_single_proxy_result(self, proxy: str, result):
        """آپدیت نتیجه تست تک پروکسی"""
        # حذف ردیف قدیمی
        for item in self.results_tree.get_children():
            if self.results_tree.item(item, 'values')[1] == proxy:
                self.results_tree.delete(item)
                break
        
        # اضافه کردن نتیجه جدید
        self.add_result_to_table(result.to_dict())
        self.update_quick_stats()
        self.show_notification("Success", f"Retested: {proxy}", "success")
        
    def select_all_working(self):
        """انتخاب تمام پروکسی‌های فعال"""
        for item in self.results_tree.get_children():
            values = self.results_tree.item(item, 'values')
            if "✅ Active" in values[-1]:  # ستون Status
                self.results_tree.selection_add(item)
                
    def remove_selected_proxy(self):
        """حذف پروکسی انتخاب شده از لیست"""
        items = self.results_tree.selection()
        if items:
            for item in items:
                values = self.results_tree.item(item, 'values')
                proxy = values[1]  # ستون Proxy
                
                if proxy in self.backend.proxy_list:
                    self.backend.proxy_list.remove(proxy)
                self.results_tree.delete(item)
            
            self.update_quick_stats()
            self.show_notification("Success", f"Removed {len(items)} proxies", "success")
                
    def apply_filters(self, event=None):
        """اعمال فیلترها"""
        filters = {}
        
        if self.active_filter_var.get():
            filters['active_only'] = True
            
        if self.ping_filter_var.get():
            filters['max_ping'] = int(self.ping_filter_var.get())
            
        self.current_filters = filters
        self.refresh_results_table()
        
    def clear_filters(self):
        """پاک کردن فیلترها"""
        self.active_filter_var.set(False)
        self.ping_filter_var.set('')
        self.current_filters = {}
        self.refresh_results_table()
        
    def refresh_results_table(self):
        """تازه‌سازی جدول نتایج با فیلترها"""
        # پاک کردن جدول
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        # گرفتن نتایج فیلتر شده
        if self.current_filters:
            filtered_results = self.backend.get_filtered_results(self.current_filters)
        else:
            filtered_results = [r.to_dict() for r in self.backend.test_results]
        
        # پر کردن مجدد
        for i, result in enumerate(filtered_results, 1):
            self.add_result_to_table(result)
                
    def sort_results(self, event=None):
        """سورت کردن نتایج"""
        sort_by = self.sort_var.get()
        sorted_results = self.backend.get_sorted_results(sort_by)
        
        # پاک کردن جدول
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        # پر کردن مجدد
        for i, result in enumerate(sorted_results, 1):
            status_icon = "✅" if result['status'] == 'Active' else "❌"
            self.results_tree.insert('', 'end', values=(
                i, 
                result['proxy'], 
                self.get_country_flag(result.get('country_code', 'XX')) + " " + result.get('country', 'Unknown'),
                f"{result['ping']}ms", 
                f"{result['http_time']}ms", 
                result.get('anonymity', 'Unknown'),
                f"{status_icon} {result['status']}"
            ))
            
    def clear_results(self):
        """پاک کردن نتایج"""
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        self.backend.test_results.clear()
        self.update_quick_stats()
        self.show_notification("Info", "Results cleared", "info")
        
    def clear_all_data(self):
        """پاک کردن همه داده‌ها"""
        self.backend.clear_all()
        self.clear_results()
        self.update_quick_stats()
        self.show_notification("Info", "All data cleared", "info")
        
    def export_results(self):
        """اکسپورت نتایج"""
        success, message = self.backend.export_results_json()
        if success:
            self.show_notification("Success", message, "success")
        else:
            self.show_notification("Error", message, "error")
            
    def update_quick_stats(self):
        """آپدیت آمار سریع"""
        stats = self.backend.get_stats()
        
        total = stats.get('total_proxies', 0)
        active = stats.get('active_proxies', 0)
        success_rate = stats.get('success_rate', 0)
        best_ping = stats.get('best_ping', 0)
        best_http = stats.get('best_http_time', 0)
        
        # آپدیت آمار سریع
        self.quick_stats['total'].config(text=str(total))
        self.quick_stats['active'].config(text=str(active))
        self.quick_stats['success_rate'].config(text=f"{success_rate:.1f}%")
        self.quick_stats['best_ping'].config(text=f"{best_ping} ms" if best_ping > 0 else "- ms")
        self.quick_stats['best_http'].config(text=f"{best_http} ms" if best_http > 0 else "- ms")
        
    def toggle_sound(self):
        """تغییر وضعیت صدا"""
        self.backend.update_settings({'enable_sound': self.sound_var.get()})
        
    def toggle_https(self):
        """تغییر وضعیت تست HTTPS"""
        self.backend.update_settings({'test_https': self.https_var.get()})
        
    def show_about(self):
        """نمایش صفحه درباره"""
        about_text = f"""🌐 ProxyMaster Pro v{self.version}

A powerful proxy testing and management tool

✨ Features:
• Fast async proxy testing
• Country detection with flags
• Anonymity level detection  
• Real-time statistics
• One-click proxy setup
• Advanced filtering
• Export capabilities

📧 Contact: Your Contact Info
🔗 Telegram: Your Telegram

Thank you for using ProxyMaster Pro!"""
        
        messagebox.showinfo("About ProxyMaster Pro", about_text, parent=self.root)
        
    def show_notification(self, title, message, type_="info"):
        """نمایش نوتیفیکیشن مدرن"""
        # رنگ‌های مختلف برای انواع نوتیفیکیشن
        colors = {
            'success': self.colors['success'],
            'error': self.colors['danger'],
            'warning': self.colors['warning'],
            'info': self.colors['primary']
        }
        
        bg_color = colors.get(type_, self.colors['primary'])
        
        # ایجاد پنجره نوتیفیکیشن
        notification = tk.Toplevel(self.root)
        notification.overrideredirect(True)
        notification.configure(bg=bg_color)
        notification.attributes('-topmost', True)
        
        # موقعیت‌یابی
        x = self.root.winfo_x() + self.root.winfo_width() - 350
        y = self.root.winfo_y() + 50
        notification.geometry(f"300x80+{x}+{y}")
        
        # محتوای نوتیفیکیشن
        title_label = tk.Label(notification, text=title, font=('Segoe UI', 12, 'bold'),
                              bg=bg_color, fg=self.colors['text_primary'])
        title_label.pack(anchor='w', padx=15, pady=(10, 0))
        
        message_label = tk.Label(notification, text=message, font=('Segoe UI', 10),
                                bg=bg_color, fg=self.colors['text_primary'], justify='left')
        message_label.pack(anchor='w', padx=15, pady=(5, 15))
        
        # محو شدن خودکار
        def fade_out():
            for i in range(100, 0, -10):
                try:
                    notification.attributes('-alpha', i/100)
                    notification.update()
                    notification.after(50)
                except:
                    break
            notification.destroy()
        
        notification.after(3000, fade_out)
        
    def run(self):
        """اجرای برنامه"""
        # شروع چک کردن وضعیت اتصال
        self.update_connection_status()
        
        # اجرای حلقه اصلی
        self.root.mainloop()

if __name__ == "__main__":
    try:
        import requests
    except ImportError:
        print("Please install requests: pip install requests")
        exit(1)
        
    app = ModernProxyFrontend()
    app.run()