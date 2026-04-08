import tkinter as tk
from tkinter import messagebox, ttk

from database import get_all_orders, update_order_status
from ui_styles import (
    COLORS,
    FONT_LABEL,
    FONT_TEXT,
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


class StaffFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["bg"])
        self.controller = controller
        self.current_view = "orders"
        self.order_cache = []

        self.build_layout()
        self.show_view("orders")

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
            t("staff_dashboard", self.controller.language),
            [
                {"text": f"📋  {t('orders', self.controller.language)}", "command": lambda: self.show_view("orders")},
                {"text": f"🚦  {t('queue_control', self.controller.language)}", "command": lambda: self.show_view("queue")},
            ],
        )

    def build_topbar(self):
        self.topbar = tk.Frame(self.content_host, bg=COLORS["bg"])
        self.topbar.pack(fill="x", padx=12, pady=(12, 6))

        self.lbl_title = tk.Label(self.topbar, text="", bg=COLORS["bg"], fg=COLORS["text"], font=("Arial", 18, "bold"))
        self.lbl_title.pack(side=pack_side_for_language(self.controller.language, "left"))

        self.btn_logout = ghost_button(self.topbar, "", self.controller.logout, width=12)
        self.btn_logout.pack(side=pack_side_for_language(self.controller.language, "right"))

        self.lbl_hint = tk.Label(self.content_host, text="", bg=COLORS["bg"], fg=COLORS["muted"], font=FONT_LABEL)
        self.lbl_hint.pack(fill="x", padx=14)

    def build_views(self):
        self.view_area = tk.Frame(self.content_host, bg=COLORS["bg"])
        self.view_area.pack(fill="both", expand=True, padx=12, pady=10)

        self.views = {
            "orders": tk.Frame(self.view_area, bg=COLORS["bg"]),
            "queue": tk.Frame(self.view_area, bg=COLORS["bg"]),
        }

        self.build_orders_view()
        self.build_queue_view()
        self.refresh_texts()

    def rebuild_sidebar(self):
        self.sidebar.destroy()
        self.build_sidebar_panel()
        self.show_view(self.current_view)

    def build_orders_view(self):
        page = self.views["orders"]
        stats = tk.Frame(page, bg=COLORS["bg"])
        stats.pack(fill="x", pady=(0, 10))
        self.stat_total = make_stat_card(stats, "📦", t("total_orders", self.controller.language), "0", COLORS["secondary"])
        self.stat_total.pack(side="left", fill="x", expand=True, padx=4)
        self.stat_active = make_stat_card(stats, "⏳", t("active_orders", self.controller.language), "0", COLORS["warning"])
        self.stat_active.pack(side="left", fill="x", expand=True, padx=4)

        card = make_card(page, t("orders", self.controller.language))
        card.pack(fill="both", expand=True)

        self.orders_tree = ttk.Treeview(card, columns=("id", "customer", "items", "total", "status", "queue", "created"), show="headings", height=18, style="App.Treeview")
        self.orders_tree.pack(fill="both", expand=True)
        widths = {"id": 60, "customer": 120, "items": 270, "total": 90, "status": 110, "queue": 70, "created": 160}
        for col, w in widths.items():
            self.orders_tree.column(col, width=w, anchor="center")

    def build_queue_view(self):
        page = self.views["queue"]
        main = tk.Frame(page, bg=COLORS["bg"])
        main.pack(fill="both", expand=True)

        left = make_card(main, t("queue_control", self.controller.language))
        right = make_card(main, t("summary", self.controller.language))
        left.pack(side=pack_side_for_language(self.controller.language, "left"), fill="both", expand=True, padx=(0, 6))
        right.pack(side=pack_side_for_language(self.controller.language, "right"), fill="both", expand=False, padx=(6, 0))

        self.queue_tree = ttk.Treeview(left, columns=("id", "customer", "status", "queue"), show="headings", height=16, style="App.Treeview")
        self.queue_tree.pack(fill="both", expand=True)
        self.queue_tree.column("id", width=60, anchor="center")
        self.queue_tree.column("customer", width=140, anchor="center")
        self.queue_tree.column("status", width=120, anchor="center")
        self.queue_tree.column("queue", width=80, anchor="center")

        self.lbl_queue_help = tk.Label(right, text="", bg=COLORS["surface"], font=FONT_TEXT, wraplength=260)
        self.lbl_queue_help.pack(fill="x", pady=(0, 14))

        self.btn_refresh = base_button(right, "", self.load_orders, bg=COLORS["secondary"], width=18)
        self.btn_refresh.pack(fill="x", pady=(0, 8))
        self.btn_queued = base_button(right, "", lambda: self.update_selected_status("Queued"), bg=COLORS["muted"], width=18)
        self.btn_queued.pack(fill="x", pady=4)
        self.btn_preparing = base_button(right, "", lambda: self.update_selected_status("Preparing"), bg=COLORS["warning"], width=18)
        self.btn_preparing.pack(fill="x", pady=4)
        self.btn_ready = base_button(right, "", lambda: self.update_selected_status("Ready"), bg=COLORS["success"], width=18)
        self.btn_ready.pack(fill="x", pady=4)
        self.btn_completed = base_button(right, "", lambda: self.update_selected_status("Completed"), bg=COLORS["primary_2"], width=18)
        self.btn_completed.pack(fill="x", pady=4)

    def show_view(self, name):
        self.current_view = name
        set_sidebar_active(self.sidebar_buttons, 0 if name == "orders" else 1)
        for frame in self.views.values():
            frame.pack_forget()
        self.views[name].pack(fill="both", expand=True)
        self.load_orders()

    def load_orders(self):
        self.order_cache = get_all_orders()
        for tree in [self.orders_tree, self.queue_tree]:
            for row in tree.get_children():
                tree.delete(row)

        total_orders = len(self.order_cache)
        active_orders = 0
        for order in self.order_cache:
            if order["status"] in ("Queued", "Preparing", "Ready"):
                active_orders += 1
            self.orders_tree.insert(
                "",
                tk.END,
                values=(
                    order["id"],
                    order["customer"],
                    order["items_summary"],
                    f"OMR {order['total_price']:.3f}",
                    order["status"],
                    order["queue_position"],
                    order["created_at"],
                ),
            )
            self.queue_tree.insert(
                "",
                tk.END,
                values=(order["id"], order["customer"], order["status"], order["queue_position"]),
            )

        self.stat_total.winfo_children()[1].config(text=str(total_orders))
        self.stat_active.winfo_children()[1].config(text=str(active_orders))

    def update_selected_status(self, new_status):
        lang = self.controller.language
        selected = self.queue_tree.selection()
        if not selected:
            messagebox.showwarning(t("warning", lang), t("select_order", lang))
            return
        order_id = int(self.queue_tree.item(selected[0])["values"][0])
        update_order_status(order_id, new_status)
        self.load_orders()
        messagebox.showinfo(t("success", lang), t("status_updated", lang))

    def refresh_texts(self):
        lang = self.controller.language
        self.lbl_title.config(text=t("staff_dashboard", lang))
        self.lbl_hint.config(text=t("team_hint", lang), justify="right" if is_rtl(lang) else "left", anchor="e" if is_rtl(lang) else "w")
        self.btn_logout.config(text=t("logout", lang))

        self.orders_tree.heading("id", text="ID")
        self.orders_tree.heading("customer", text=t("customer", lang))
        self.orders_tree.heading("items", text=t("order_items", lang))
        self.orders_tree.heading("total", text=t("total_price", lang))
        self.orders_tree.heading("status", text=t("order_status", lang))
        self.orders_tree.heading("queue", text=t("queue_position", lang))
        self.orders_tree.heading("created", text=t("created_at", lang))

        self.queue_tree.heading("id", text="ID")
        self.queue_tree.heading("customer", text=t("customer", lang))
        self.queue_tree.heading("status", text=t("order_status", lang))
        self.queue_tree.heading("queue", text=t("queue_position", lang))

        self.lbl_queue_help.config(text=t("team_hint", lang), justify="right" if is_rtl(lang) else "left", anchor="e" if is_rtl(lang) else "w")
        self.btn_refresh.config(text=t("refresh", lang))
        self.btn_queued.config(text=t("queued", lang))
        self.btn_preparing.config(text=t("preparing", lang))
        self.btn_ready.config(text=t("ready", lang))
        self.btn_completed.config(text=t("completed", lang))

    def on_show(self):
        self.refresh_texts()
        self.rebuild_sidebar()
        self.load_orders()
