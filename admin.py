import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import os
import io

try:
    from PIL import Image, ImageTk
except Exception:
    Image = None
    ImageTk = None
    
from database import add_menu_item, delete_menu_item, get_menu_items, get_report_data, get_all_users,get_user_by_id,add_user,update_user,delete_user,reset_user_password

from ui_styles import (
    COLORS,
    FONT_LABEL,
    FONT_TEXT,
    apply_text_direction,
    base_button,
    build_sidebar,
    ghost_button,
    make_card,
    make_stat_card,
    pack_side_for_language,
    set_sidebar_active,
    t,
)


class AdminFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["bg"])
        self.controller = controller
        self.current_view = "reports"
        self.selected_user_id = None
        self.selected_image_path = ""
        self.selected_image_name = ""
        self.selected_image_data = None
        self.user_photo_preview = None
        self.build_layout()
        self.show_view("reports")

    def build_layout(self):
        self.sidebar_container = tk.Frame(self, bg=COLORS["bg"])
        self.sidebar_container.pack(fill="both", expand=True)

        self.content_host = tk.Frame(self.sidebar_container, bg=COLORS["bg"])
        self.content_host.pack(side=pack_side_for_language(self.controller.language, "right"), fill="both", expand=True)

        self.build_sidebar_panel()
        self.build_topbar()
        self.build_views()

    def build_sidebar_panel(self):
        self.sidebar, self.sidebar_buttons = build_sidebar(
            self.sidebar_container,
            self.controller.language,
            t("admin_dashboard", self.controller.language),
            [
            {"text": t("reports", self.controller.language), "icon": "reports", "command": lambda: self.show_view("reports")},
            {"text": t("menu_management", self.controller.language), "icon": "menu", "command": lambda: self.show_view("menu")},
            {"text": t("user_management", self.controller.language), "icon": "users", "command": lambda: self.show_view("users")},
            ],
        )

    def build_topbar(self):
        self.topbar = tk.Frame(self.content_host, bg=COLORS["bg"])
        self.topbar.pack(fill="x", padx=12, pady=(12, 6))

        self.lbl_title = tk.Label(self.topbar, text="", bg=COLORS["bg"], fg=COLORS["text"], font=("Arial", 18, "bold"))
        self.lbl_title.pack(side=pack_side_for_language(self.controller.language, "left"))

        self.btn_logout = ghost_button(self.topbar, "", self.controller.logout, width=12)
        self.btn_logout.pack(side=pack_side_for_language(self.controller.language, "right"))

    def build_views(self):
        self.view_area = tk.Frame(self.content_host, bg=COLORS["bg"])
        self.view_area.pack(fill="both", expand=True, padx=12, pady=10)

        self.views = {
            "reports": tk.Frame(self.view_area, bg=COLORS["bg"]),
            "menu": tk.Frame(self.view_area, bg=COLORS["bg"]),
            "users": tk.Frame(self.view_area, bg=COLORS["bg"]),
        }

        self.build_reports_view()
        self.build_menu_view()
        self.build_users_view()
        self.refresh_texts()

    def rebuild_sidebar(self):
        self.sidebar.destroy()
        self.build_sidebar_panel()
        self.show_view(self.current_view)

    def build_reports_view(self):
        page = self.views["reports"]

        # Top summary cards
        top_stats = tk.Frame(page, bg=COLORS["bg"])
        top_stats.pack(fill="x", pady=(0, 10))

        self.stat_total = make_stat_card(
            top_stats, "📦", t("total_orders", self.controller.language), "0", COLORS["secondary"]
        )
        self.stat_total.pack(side="left", fill="x", expand=True, padx=4)

        self.stat_active = make_stat_card(
            top_stats, "⏳", t("active_orders", self.controller.language), "0", COLORS["warning"]
        )
        self.stat_active.pack(side="left", fill="x", expand=True, padx=4)

        self.stat_top = make_stat_card(
            top_stats, "⭐", t("most_ordered_item", self.controller.language), "-", COLORS["success"]
        )
        self.stat_top.pack(side="left", fill="x", expand=True, padx=4)

        # Main report area
        middle = tk.Frame(page, bg=COLORS["bg"])
        middle.pack(fill="both", expand=True)

        left = make_card(middle, t("summary_report", self.controller.language))
        right = make_card(middle, t("quick_stats", self.controller.language))

        left.pack(side=pack_side_for_language(self.controller.language, "left"), fill="both", expand=True, padx=(0, 6))
        right.pack(side=pack_side_for_language(self.controller.language, "right"), fill="both", expand=False, padx=(6, 0))

        # Left side summary labels
        self.report_summary_box = tk.Frame(left, bg=COLORS["surface"])
        self.report_summary_box.pack(fill="x", pady=(0, 10))

        self.lbl_report_line1 = tk.Label(self.report_summary_box, text="", bg=COLORS["surface"], fg=COLORS["text"], font=("Arial", 12, "bold"))
        self.lbl_report_line1.pack(anchor="w", pady=(0, 6))

        self.lbl_report_line2 = tk.Label(self.report_summary_box, text="", bg=COLORS["surface"], fg=COLORS["text"], font=FONT_LABEL)
        self.lbl_report_line2.pack(anchor="w", pady=2)

        self.lbl_report_line3 = tk.Label(self.report_summary_box, text="", bg=COLORS["surface"], fg=COLORS["text"], font=FONT_LABEL)
        self.lbl_report_line3.pack(anchor="w", pady=2)

        self.lbl_report_line4 = tk.Label(self.report_summary_box, text="", bg=COLORS["surface"], fg=COLORS["text"], font=FONT_LABEL)
        self.lbl_report_line4.pack(anchor="w", pady=2)

        # Report notes text
        self.txt_report = tk.Text(
            left,
            height=10,
            font=FONT_TEXT,
            relief="flat",
            bg=COLORS["surface"],
            wrap="word",
            padx=10,
            pady=10
        )
        self.txt_report.pack(fill="both", expand=True)

        # Right side quick stats as 2x2 grid
        self.quick_grid = tk.Frame(right, bg=COLORS["surface"])
        self.quick_grid.pack(fill="both", expand=True)

        self.quick_grid.grid_columnconfigure(0, weight=1)
        self.quick_grid.grid_columnconfigure(1, weight=1)

        self.stat_queued = make_stat_card(
            self.quick_grid, "🕓", t("queued", self.controller.language), "0", COLORS["muted"]
        )
        self.stat_queued.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)

        self.stat_preparing = make_stat_card(
            self.quick_grid, "⏳", t("preparing", self.controller.language), "0", COLORS["warning"]
        )
        self.stat_preparing.grid(row=0, column=1, sticky="nsew", padx=4, pady=4)

        self.stat_ready = make_stat_card(
            self.quick_grid, "✅", t("ready", self.controller.language), "0", COLORS["success"]
        )
        self.stat_ready.grid(row=1, column=0, sticky="nsew", padx=4, pady=4)

        self.stat_completed = make_stat_card(
            self.quick_grid, "✔", t("completed", self.controller.language), "0", COLORS["primary_2"]
        )
        self.stat_completed.grid(row=1, column=1, sticky="nsew", padx=4, pady=4)

        self.lbl_report_note = tk.Label(
            right,
            text="",
            bg=COLORS["surface"],
            fg=COLORS["muted"],
            font=FONT_LABEL,
            wraplength=300,
            justify="left"
        )
        self.lbl_report_note.pack(fill="x", pady=(10, 0))

    def build_menu_view(self):
        page = self.views["menu"]
        main = tk.Frame(page, bg=COLORS["bg"])
        main.pack(fill="both", expand=True)

        left = make_card(main, t("menu_management", self.controller.language))
        right = make_card(main, t("add_item", self.controller.language))
        left.pack(side=pack_side_for_language(self.controller.language, "left"), fill="both", expand=True, padx=(0, 6))
        right.pack(side=pack_side_for_language(self.controller.language, "right"), fill="both", expand=False, padx=(6, 0))

        self.menu_tree = ttk.Treeview(left, columns=("id", "name", "category", "price"), show="headings", height=16, style="App.Treeview")
        self.menu_tree.pack(fill="both", expand=True)
        self.menu_tree.column("id", width=60, anchor="center")
        self.menu_tree.column("name", width=180, anchor="center")
        self.menu_tree.column("category", width=120, anchor="center")
        self.menu_tree.column("price", width=90, anchor="center")

        self.lbl_item_name = tk.Label(right, text="", bg=COLORS["surface"], font=FONT_LABEL)
        self.lbl_item_name.pack(anchor="w")
        self.entry_item_name = tk.Entry(right, font=FONT_TEXT)
        self.entry_item_name.pack(fill="x", pady=(4, 10))

        self.lbl_category = tk.Label(right, text="", bg=COLORS["surface"], font=FONT_LABEL)
        self.lbl_category.pack(anchor="w")
        self.entry_category = tk.Entry(right, font=FONT_TEXT)
        self.entry_category.pack(fill="x", pady=(4, 10))

        self.lbl_description = tk.Label(right, text="", bg=COLORS["surface"], font=FONT_LABEL)
        self.lbl_description.pack(anchor="w")
        self.entry_description = tk.Entry(right, font=FONT_TEXT)
        self.entry_description.pack(fill="x", pady=(4, 10))

        self.lbl_price = tk.Label(right, text="", bg=COLORS["surface"], font=FONT_LABEL)
        self.lbl_price.pack(anchor="w")
        self.entry_price = tk.Entry(right, font=FONT_TEXT)
        self.entry_price.pack(fill="x", pady=(4, 14))

        self.btn_add = base_button(right, "", self.add_item, bg=COLORS["success"], width=18)
        self.btn_add.pack(fill="x", pady=(0, 8))
        self.btn_delete = base_button(right, "", self.delete_item, bg=COLORS["danger"], width=18)
        self.btn_delete.pack(fill="x", pady=(0, 8))
        self.btn_clear = ghost_button(right, "", self.clear_inputs, width=18)
        self.btn_clear.pack(fill="x")

    
    def build_users_view(self):
        page = self.views["users"]
        main = tk.Frame(page, bg=COLORS["bg"])
        main.pack(fill="both", expand=True)

        left = make_card(main, t("user_accounts", self.controller.language))
        right = make_card(main, t("manage_user", self.controller.language))
        left.pack(side=pack_side_for_language(self.controller.language, "left"), fill="both", expand=True, padx=(0, 6))
        right.pack(side=pack_side_for_language(self.controller.language, "right"), fill="both", expand=False, padx=(6, 0))

        self.users_tree = ttk.Treeview(
            left,
            columns=("id", "username", "role"),
            show="tree headings",
            height=16,
            style="App.Treeview",
        )
        self.users_tree.pack(fill="both", expand=True)

        self.users_tree.heading("#0", text=t("image", self.controller.language))
        self.users_tree.heading("id", text="ID")
        self.users_tree.heading("username", text=t("username", self.controller.language))
        self.users_tree.heading("role", text=t("role", self.controller.language))

        self.users_tree.column("#0", width=70, anchor="center", stretch=False)
        self.users_tree.column("id", width=60, anchor="center")
        self.users_tree.column("username", width=180, anchor="center")
        self.users_tree.column("role", width=140, anchor="center")

        self.users_tree.bind("<<TreeviewSelect>>", self.on_user_selected)

        self.user_row_photos = {}

        self.lbl_user_username = tk.Label(right, text="", bg=COLORS["surface"], font=FONT_LABEL)
        self.lbl_user_username.pack(anchor="w")
        self.entry_user_username = tk.Entry(right, font=FONT_TEXT)
        self.entry_user_username.pack(fill="x", pady=(4, 10))

        self.lbl_user_role = tk.Label(right, text="", bg=COLORS["surface"], font=FONT_LABEL)
        self.lbl_user_role.pack(anchor="w")
        self.combo_user_role = ttk.Combobox(right, state="readonly", font=FONT_TEXT, values=["Customer", "Staff", "Administrator"])
        self.combo_user_role.pack(fill="x", pady=(4, 10))
        self.combo_user_role.set("Customer")

        self.lbl_user_password = tk.Label(right, text="", bg=COLORS["surface"], font=FONT_LABEL)
        self.lbl_user_password.pack(anchor="w")
        self.entry_user_password = tk.Entry(right, font=FONT_TEXT, show="*")
        self.entry_user_password.pack(fill="x", pady=(4, 10))

        self.lbl_user_image = tk.Label(right, text="", bg=COLORS["surface"], font=FONT_LABEL)
        self.lbl_user_image.pack(anchor="w")
        self.image_path_frame = tk.Frame(right, bg=COLORS["surface"])
        self.image_path_frame.pack(fill="x", pady=(4, 10))
        self.entry_user_image = tk.Entry(self.image_path_frame, font=FONT_TEXT)
        self.entry_user_image.pack(side="left", fill="x", expand=True)
        self.btn_browse_image = ghost_button(self.image_path_frame, "", self.choose_user_image, width=10)
        self.btn_browse_image.pack(side="left", padx=(8, 0))

        
        self.image_preview_frame = tk.Frame(
            right,
            bg=COLORS["surface"],
            bd=1,
            relief="solid",
            width=130,
            height=130
        )
        self.image_preview_frame.pack(pady=(0, 10))
        self.image_preview_frame.pack_propagate(False)

        self.image_preview_label = tk.Label(
            self.image_preview_frame,
            text=t("no_image", self.controller.language),
            bg=COLORS["surface"],
            fg=COLORS["muted"],
            compound="center"
        )
        self.image_preview_label.pack(fill="both", expand=True)

        self.btn_user_add = base_button(right, "", self.add_user_action, bg=COLORS["success"], width=18)
        self.btn_user_add.pack(fill="x", pady=(0, 8))
        self.btn_user_update = base_button(right, "", self.update_user_action, bg=COLORS["secondary"], width=18)
        self.btn_user_update.pack(fill="x", pady=(0, 8))
        self.btn_user_delete = base_button(right, "", self.delete_user_action, bg=COLORS["danger"], width=18)
        self.btn_user_delete.pack(fill="x", pady=(0, 8))
        self.btn_user_reset_password = ghost_button(right, "", self.reset_password_action, width=18)
        self.btn_user_reset_password.pack(fill="x", pady=(0, 8))
        self.btn_user_clear = ghost_button(right, "", self.clear_user_inputs, width=18)
        self.btn_user_clear.pack(fill="x")
    
    def show_view(self, name):
        self.current_view = name
        index_map = {"reports": 0, "menu": 1, "users": 2}
        set_sidebar_active(self.sidebar_buttons, index_map.get(name, 0))
        for frame in self.views.values():
            frame.pack_forget()
        self.views[name].pack(fill="both", expand=True)
        if name == "reports":
            self.load_report()
        elif name == "menu":
            self.load_menu_items()
        else:
            self.load_users()

    def load_report(self):
        lang = self.controller.language
        report = get_report_data()

        total_orders = int(report["total_orders"])
        active_orders = int(report["active_orders"])
        queued = int(report["queued"])
        preparing = int(report["preparing"])
        ready = int(report["ready"])
        completed = int(report["completed"])
        top_item = report["top_item"]

        self.stat_total.winfo_children()[1].config(text=str(total_orders))
        self.stat_active.winfo_children()[1].config(text=str(active_orders))
        self.stat_top.winfo_children()[1].config(text=str(top_item))

        self.stat_queued.winfo_children()[1].config(text=str(queued))
        self.stat_preparing.winfo_children()[1].config(text=str(preparing))
        self.stat_ready.winfo_children()[1].config(text=str(ready))
        self.stat_completed.winfo_children()[1].config(text=str(completed))

        # Summary lines
        self.lbl_report_line1.config(
            text=t("summary_report", lang),
            anchor="e" if lang == "ar" else "w",
            justify="right" if lang == "ar" else "left"
        )
        self.lbl_report_line2.config(
            text=f"{t('total_orders', lang)}: {total_orders}",
            anchor="e" if lang == "ar" else "w",
            justify="right" if lang == "ar" else "left"
        )
        self.lbl_report_line3.config(
            text=f"{t('active_orders', lang)}: {active_orders}",
            anchor="e" if lang == "ar" else "w",
            justify="right" if lang == "ar" else "left"
        )
        self.lbl_report_line4.config(
            text=f"{t('most_ordered_item', lang)}: {top_item}",
            anchor="e" if lang == "ar" else "w",
            justify="right" if lang == "ar" else "left"
        )

        # Insight / note
        if total_orders == 0:
            performance_note = "No orders have been recorded yet." if lang == "en" else "لا توجد طلبات مسجلة حتى الآن."
        elif active_orders == 0:
            performance_note = "All current orders are completed." if lang == "en" else "جميع الطلبات الحالية مكتملة."
        elif ready > queued and ready >= preparing:
            performance_note = "Many orders are ready for pickup." if lang == "en" else "هناك عدد كبير من الطلبات الجاهزة للاستلام."
        else:
            performance_note = "Orders are moving normally through the workflow." if lang == "en" else "الطلبات تسير بشكل طبيعي عبر مراحل العمل."

        report_text = (
            f"{t('queued', lang)}: {queued}\n"
            f"{t('preparing', lang)}: {preparing}\n"
            f"{t('ready', lang)}: {ready}\n"
            f"{t('completed', lang)}: {completed}\n\n"
            f"{'Insights' if lang == 'en' else 'ملاحظات'}:\n"
            f"- {performance_note}"
        )

        self.txt_report.delete("1.0", tk.END)
        self.txt_report.insert(tk.END, report_text)
        apply_text_direction(self.txt_report, lang)

        self.lbl_report_note.config(
            text=performance_note,
            anchor="e" if lang == "ar" else "w",
            justify="right" if lang == "ar" else "left"
        )

    def load_menu_items(self):
        for row in self.menu_tree.get_children():
            self.menu_tree.delete(row)
        for item in get_menu_items():
            self.menu_tree.insert("", tk.END, values=(item["id"], item["item_name"], item["category"], f"OMR {item['price']:.3f}"))

    def load_users(self):
        for row in self.users_tree.get_children():
            self.users_tree.delete(row)

        self.user_row_photos = {}

        for user in get_all_users():
            row_image = ""
            image_data = None

            try:
                full_user = get_user_by_id(int(user["id"]))
                image_data = full_user["image_data"] if full_user else None
            except Exception:
                image_data = None

            if image_data and Image is not None and ImageTk is not None:
                try:
                    img = Image.open(io.BytesIO(image_data)).convert("RGBA")
                    img = img.resize((52, 52), Image.LANCZOS)
                    row_image = ImageTk.PhotoImage(img)
                    self.user_row_photos[int(user["id"])] = row_image
                except Exception:
                    row_image = ""

            self.users_tree.insert(
                "",
                tk.END,
                text="",
                image=row_image,
                values=(user["id"], user["username"], user["role"]),
            )
    def add_item(self):
        lang = self.controller.language
        item_name = self.entry_item_name.get().strip()
        category = self.entry_category.get().strip()
        description = self.entry_description.get().strip()
        price_text = self.entry_price.get().strip()

        if not item_name or not category or not description or not price_text:
            messagebox.showwarning(t("warning", lang), t("fill_menu_fields", lang))
            return
        try:
            price = float(price_text)
        except ValueError:
            messagebox.showerror(t("error", lang), t("invalid_price", lang))
            return

        add_menu_item(item_name, category, description, price)
        self.clear_inputs()
        self.load_menu_items()
        messagebox.showinfo(t("success", lang), t("item_added", lang))

    def delete_item(self):
        lang = self.controller.language
        selected = self.menu_tree.selection()
        if not selected:
            messagebox.showwarning(t("warning", lang), t("select_item", lang))
            return
        item_id = int(self.menu_tree.item(selected[0])["values"][0])
        delete_menu_item(item_id)
        self.load_menu_items()
        messagebox.showinfo(t("success", lang), t("item_deleted", lang))

    def clear_inputs(self):
        self.entry_item_name.delete(0, tk.END)
        self.entry_category.delete(0, tk.END)
        self.entry_description.delete(0, tk.END)
        self.entry_price.delete(0, tk.END)


    def choose_user_image(self):
        file_path = filedialog.askopenfilename(
            title=t("select_image", self.controller.language),
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.gif *.bmp"), ("All Files", "*.*")],
        )
        if not file_path:
            return
        self.selected_image_path = file_path
        self.entry_user_image.delete(0, tk.END)
        self.selected_image_name = os.path.basename(file_path)
        self.selected_image_data = self.read_image_bytes(file_path)
        self.entry_user_image.insert(0, self.selected_image_name)
        self.show_user_image_preview(self.selected_image_data, self.selected_image_name)


    def read_image_bytes(self, file_path):
        try:
            with open(file_path, "rb") as f:
                return f.read()
        except Exception:
            return None

    def show_user_image_preview(self, image_data, image_name=""):
        self.user_photo_preview = None
    
        if not image_data:
            self.image_preview_label.config(
                image="",
                text=t("no_image", self.controller.language)
            )
            return
    
        if Image is None or ImageTk is None:
            self.image_preview_label.config(
                image="",
                text=image_name or t("image_available", self.controller.language)
            )
            return
    
        try:
            img = Image.open(io.BytesIO(image_data)).convert("RGBA")
    
            preview_size = (120, 120)
            img.thumbnail(preview_size, Image.LANCZOS)
    
            bg = Image.new("RGBA", preview_size, (255, 255, 255, 0))
            x = (preview_size[0] - img.width) // 2
            y = (preview_size[1] - img.height) // 2
            bg.paste(img, (x, y), img if img.mode == "RGBA" else None)
    
            self.user_photo_preview = ImageTk.PhotoImage(bg)
    
            self.image_preview_label.config(
                image=self.user_photo_preview,
                text=""
            )
        except Exception:
            self.image_preview_label.config(
                image="",
                text=image_name or t("image_available", self.controller.language)
            )
        
    def on_user_selected(self, event=None):
        selected = self.users_tree.selection()
        if not selected:
            return
        values = self.users_tree.item(selected[0])["values"]
        user_id = int(values[0])

        target = get_user_by_id(user_id)
        if target is None:
            return

        self.selected_user_id = user_id
        self.entry_user_username.delete(0, tk.END)
        self.entry_user_username.insert(0, target["username"])
        self.combo_user_role.set(target["role"])
        self.entry_user_password.delete(0, tk.END)
        self.entry_user_image.delete(0, tk.END)
        self.entry_user_image.insert(0, target["image_name"] or "")
        self.selected_image_name = target["image_name"] or ""
        self.selected_image_data = target["image_data"]
        self.show_user_image_preview(self.selected_image_data, self.selected_image_name)

    def add_user_action(self):
        lang = self.controller.language
        username = self.entry_user_username.get().strip()
        role = self.combo_user_role.get().strip()
        password = self.entry_user_password.get().strip()
        image_name = self.entry_user_image.get().strip()

        if not username or not role or not password:
            messagebox.showwarning(t("warning", lang), t("fill_user_fields", lang))
            return

        ok, message = add_user(username, password, role, image_name, self.selected_image_data)
        if not ok:
            messagebox.showerror(t("error", lang), message)
            return

        self.load_users()
        self.clear_user_inputs()
        messagebox.showinfo(t("success", lang), t("user_added", lang))

    def update_user_action(self):
        lang = self.controller.language
        if not self.selected_user_id:
            messagebox.showwarning(t("warning", lang), t("select_user", lang))
            return

        username = self.entry_user_username.get().strip()
        role = self.combo_user_role.get().strip()
        password = self.entry_user_password.get().strip()
        image_name = self.entry_user_image.get().strip()

        if not username or not role:
            messagebox.showwarning(t("warning", lang), t("fill_user_fields_no_password", lang))
            return

        ok, message = update_user(self.selected_user_id, username, role, password,image_name , self.selected_image_data)
        if not ok:
            messagebox.showerror(t("error", lang), message)
            return

        self.load_users()
        messagebox.showinfo(t("success", lang), t("user_updated", lang))

    def delete_user_action(self):
        lang = self.controller.language
        if not self.selected_user_id:
            messagebox.showwarning(t("warning", lang), t("select_user", lang))
            return

        ok, message = delete_user(self.selected_user_id)
        if not ok:
            messagebox.showerror(t("error", lang), message)
            return

        self.load_users()
        self.clear_user_inputs()
        messagebox.showinfo(t("success", lang), t("user_deleted", lang))

    def reset_password_action(self):
        lang = self.controller.language
        if not self.selected_user_id:
            messagebox.showwarning(t("warning", lang), t("select_user", lang))
            return

        new_password = self.entry_user_password.get().strip()
        if not new_password:
            messagebox.showwarning(t("warning", lang), t("enter_new_password", lang))
            return

        ok, message = reset_user_password(self.selected_user_id, new_password)
        if not ok:
            messagebox.showerror(t("error", lang), message)
            return

        self.entry_user_password.delete(0, tk.END)
        messagebox.showinfo(t("success", lang), t("password_reset_success", lang))

    def clear_user_inputs(self):
        self.selected_user_id = None
        self.selected_image_path = ""
        self.selected_image_name = ""
        self.selected_image_data = None
        self.entry_user_username.delete(0, tk.END)
        self.combo_user_role.set("Customer")
        self.entry_user_password.delete(0, tk.END)
        self.entry_user_image.delete(0, tk.END)
        self.users_tree.selection_remove(self.users_tree.selection())
        self.show_user_image_preview(None, "")
        
        
    def refresh_texts(self):
        lang = self.controller.language
        self.lbl_title.config(text=t("admin_dashboard", lang))
        self.btn_logout.config(text=t("logout", lang))

        self.menu_tree.heading("id", text="ID")
        self.menu_tree.heading("name", text=t("item_name", lang))
        self.menu_tree.heading("category", text=t("category", lang))
        self.menu_tree.heading("price", text=t("price", lang))

        self.lbl_item_name.config(text=f"{t('item_name', lang)}:")
        self.lbl_category.config(text=f"{t('category', lang)}:")
        self.lbl_description.config(text=f"{t('description', lang)}:")
        self.lbl_price.config(text=f"{t('price', lang)}:")
        self.btn_add.config(text=t("add_item", lang))
        self.btn_delete.config(text=t("delete_item", lang))
        self.btn_clear.config(text=t("clear", lang))

        self.users_tree.heading("username", text=t("username", lang))
        self.users_tree.heading("role", text=t("role", lang))
        self.users_tree.heading("#0", text=t("image", lang))
        self.lbl_user_username.config(text=f"{t('username', lang)}:")
        self.lbl_user_role.config(text=f"{t('role', lang)}:")
        self.lbl_user_password.config(text=f"{t('password', lang)}:")
        self.lbl_user_image.config(text=f"{t('image', lang)}:")
        self.btn_browse_image.config(text=t("browse", lang))
        self.btn_user_add.config(text=t("add_user", lang))
        self.btn_user_update.config(text=t("update_user", lang))
        self.btn_user_delete.config(text=t("delete_user", lang))
        self.btn_user_reset_password.config(text=t("reset_password", lang))
        self.btn_user_clear.config(text=t("clear", lang))
        self.lbl_report_note.config(
            justify="right" if lang == "ar" else "left",
            anchor="e" if lang == "ar" else "w"
            )

    def on_show(self):
        self.refresh_texts()
        
        self.rebuild_sidebar()
        if self.current_view == "reports":
            self.load_report()
        elif self.current_view == "menu":
            self.load_menu_items()
        else:
            self.load_users()
