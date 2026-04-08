import tkinter as tk
from tkinter import messagebox, ttk

from database import add_menu_item, delete_menu_item, get_menu_items, get_report_data
from ui_styles import (
    COLORS,
    FONT_LABEL,
    FONT_TEXT,
    apply_text_direction,
    base_button,
    build_sidebar,
    ghost_button,
    is_rtl,
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
                {"text": f"📊  {t('reports', self.controller.language)}", "command": lambda: self.show_view("reports")},
                {"text": f"🧾  {t('menu_management', self.controller.language)}", "command": lambda: self.show_view("menu")},
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
        }

        self.build_reports_view()
        self.build_menu_view()
        self.refresh_texts()

    def rebuild_sidebar(self):
        self.sidebar.destroy()
        self.build_sidebar_panel()
        self.show_view(self.current_view)

    def build_reports_view(self):
        page = self.views["reports"]
        stats = tk.Frame(page, bg=COLORS["bg"])
        stats.pack(fill="x", pady=(0, 10))
        self.stat_total = make_stat_card(stats, "📦", t("total_orders", self.controller.language), "0", COLORS["secondary"])
        self.stat_total.pack(side="left", fill="x", expand=True, padx=4)
        self.stat_active = make_stat_card(stats, "⏳", t("active_orders", self.controller.language), "0", COLORS["warning"])
        self.stat_active.pack(side="left", fill="x", expand=True, padx=4)
        self.stat_top = make_stat_card(stats, "⭐", t("most_ordered_item", self.controller.language), "-", COLORS["success"])
        self.stat_top.pack(side="left", fill="x", expand=True, padx=4)

        report_card = make_card(page, t("summary_report", self.controller.language))
        report_card.pack(fill="both", expand=True)
        self.txt_report = tk.Text(report_card, height=18, font=FONT_TEXT, relief="flat", bg=COLORS["surface"])
        self.txt_report.pack(fill="both", expand=True)

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

    def show_view(self, name):
        self.current_view = name
        set_sidebar_active(self.sidebar_buttons, 0 if name == "reports" else 1)
        for frame in self.views.values():
            frame.pack_forget()
        self.views[name].pack(fill="both", expand=True)
        if name == "reports":
            self.load_report()
        else:
            self.load_menu_items()

    def load_report(self):
        lang = self.controller.language
        report = get_report_data()
        self.stat_total.winfo_children()[1].config(text=str(report["total_orders"]))
        self.stat_active.winfo_children()[1].config(text=str(report["active_orders"]))
        self.stat_top.winfo_children()[1].config(text=str(report["top_item"]))

        self.txt_report.delete("1.0", tk.END)
        text = (
            f"{t('summary_report', lang)}\n"
            f"-----------------------------\n"
            f"{t('queued', lang)}: {report['queued']}\n"
            f"{t('preparing', lang)}: {report['preparing']}\n"
            f"{t('ready', lang)}: {report['ready']}\n"
            f"{t('completed', lang)}: {report['completed']}\n\n"
            f"{t('active_orders', lang)}: {report['active_orders']}\n"
            f"{t('total_orders', lang)}: {report['total_orders']}\n"
            f"{t('most_ordered_item', lang)}: {report['top_item']}\n"
        )
        self.txt_report.insert(tk.END, text)
        apply_text_direction(self.txt_report, lang)

    def load_menu_items(self):
        for row in self.menu_tree.get_children():
            self.menu_tree.delete(row)
        for item in get_menu_items():
            self.menu_tree.insert("", tk.END, values=(item["id"], item["item_name"], item["category"], f"OMR {item['price']:.3f}"))

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

    def on_show(self):
        self.refresh_texts()
        self.rebuild_sidebar()
        if self.current_view == "reports":
            self.load_report()
        else:
            self.load_menu_items()
