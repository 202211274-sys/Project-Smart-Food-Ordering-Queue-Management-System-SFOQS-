import tkinter as tk
from tkinter import messagebox, ttk

from database import create_order, get_categories, get_latest_order_for_customer, get_menu_item, get_menu_items, get_order_items

from ui_styles import (
    COLORS, FONT_TITLE, FONT_TEXT, FONT_LABEL,
    t, is_rtl,   apply_text_direction,
    pack_side_for_language, build_sidebar,
    make_card, base_button, ghost_button,
    set_sidebar_active, make_stat_card,
    anchor_for_language
)


class CustomerFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["bg"])
        self.controller = controller
        self.cart_items = []
        self.category_value = "All"
        self.current_view = "menu"
        self.menu_rows = []
        self.category_buttons = []

        self.build_layout()
        self.show_view("menu")

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
            t("customer_dashboard", self.controller.language),
            [
                {"text": f"🍽  {t('menu', self.controller.language)}", "command": lambda: self.show_view("menu")},
                {"text": f"🛒  {t('cart', self.controller.language)}", "command": lambda: self.show_view("cart")},
                {"text": f"📦  {t('track_order', self.controller.language)}", "command": lambda: self.show_view("track")},
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
            "menu": tk.Frame(self.view_area, bg=COLORS["bg"]),
            "cart": tk.Frame(self.view_area, bg=COLORS["bg"]),
            "track": tk.Frame(self.view_area, bg=COLORS["bg"]),
        }

        self.build_menu_view()
        self.build_cart_view()
        self.build_track_view()
        self.refresh_texts()

    def rebuild_sidebar(self):
        self.sidebar.destroy()
        self.build_sidebar_panel()
        self.show_view(self.current_view)

    def build_menu_view(self):
        page = self.views["menu"]

        stats_row = tk.Frame(page, bg=COLORS["bg"])
        stats_row.pack(fill="x", pady=(0, 10))
        self.stat_menu = make_stat_card(stats_row, "🍽", t("menu_preview", self.controller.language), "0", COLORS["secondary"])
        self.stat_menu.pack(side="left", fill="x", expand=True, padx=4)
        self.stat_cart = make_stat_card(stats_row, "🛒", t("item_count", self.controller.language), "0", COLORS["success"])
        self.stat_cart.pack(side="left", fill="x", expand=True, padx=4)
        self.stat_total = make_stat_card(stats_row, "💳", t("total_price", self.controller.language), "OMR 0.000", COLORS["warning"])
        self.stat_total.pack(side="left", fill="x", expand=True, padx=4)

        filters_card = make_card(page, t("digital_menu", self.controller.language))
        filters_card.pack(fill="x", pady=(0, 10))

        top_search = tk.Frame(filters_card, bg=COLORS["surface"])
        top_search.pack(fill="x")
        self.lbl_search = tk.Label(top_search, text="", bg=COLORS["surface"], font=FONT_LABEL)
        self.lbl_search.pack(side=pack_side_for_language(self.controller.language, "left"), padx=(0, 6))
        self.entry_search = tk.Entry(top_search, font=FONT_TEXT)
        self.entry_search.pack(side=pack_side_for_language(self.controller.language, "left"), fill="x", expand=True)
        self.entry_search.bind("<KeyRelease>", lambda _e: self.load_menu_items())

        self.categories_wrap = tk.Frame(filters_card, bg=COLORS["surface"])
        self.categories_wrap.pack(fill="x", pady=(12, 0))

        body = tk.Frame(page, bg=COLORS["bg"])
        body.pack(fill="both", expand=True)

        menu_card = make_card(body, t("menu", self.controller.language))
        details_card = make_card(body, t("summary", self.controller.language))

        menu_card.pack(side=pack_side_for_language(self.controller.language, "left"), fill="both", expand=True, padx=(0, 6))
        details_card.pack(side=pack_side_for_language(self.controller.language, "right"), fill="both", expand=False, padx=(6, 0))

        self.menu_tree = ttk.Treeview(menu_card, columns=("id", "name", "category", "price"), show="headings", height=15, style="App.Treeview")
        self.menu_tree.pack(fill="both", expand=True)
        self.menu_tree.column("id", width=60, anchor="center")
        self.menu_tree.column("name", width=180, anchor="center")
        self.menu_tree.column("category", width=120, anchor="center")
        self.menu_tree.column("price", width=90, anchor="center")
        self.menu_tree.bind("<<TreeviewSelect>>", self.on_menu_select)

        self.lbl_selected = tk.Label(details_card, text="", bg=COLORS["surface"], font=("Arial", 14, "bold"), fg=COLORS["primary"])
        self.lbl_selected.pack(anchor="w")
        self.lbl_selected_desc = tk.Label(details_card, text="", bg=COLORS["surface"], font=FONT_LABEL, wraplength=260)
        self.lbl_selected_desc.pack(fill="x", pady=(8, 10))

        qty_row = tk.Frame(details_card, bg=COLORS["surface"])
        qty_row.pack(fill="x", pady=(4, 12))
        self.lbl_qty = tk.Label(qty_row, text="", bg=COLORS["surface"], font=FONT_LABEL)
        self.lbl_qty.pack(side=pack_side_for_language(self.controller.language, "left"))
        self.spin_qty = tk.Spinbox(qty_row, from_=1, to=20, width=8, font=FONT_TEXT)
        self.spin_qty.pack(side=pack_side_for_language(self.controller.language, "right"))

        self.btn_add_to_cart = base_button(details_card, "", self.add_to_cart, bg=COLORS["success"], width=18)
        self.btn_add_to_cart.pack(fill="x", pady=(0, 8))
        self.btn_open_cart = ghost_button(details_card, "", lambda: self.show_view("cart"), width=18)
        self.btn_open_cart.pack(fill="x")

    def build_cart_view(self):
        page = self.views["cart"]
        main = tk.Frame(page, bg=COLORS["bg"])
        main.pack(fill="both", expand=True)

        left = make_card(main, t("your_cart", self.controller.language))
        right = make_card(main, t("summary", self.controller.language))
        left.pack(side=pack_side_for_language(self.controller.language, "left"), fill="both", expand=True, padx=(0, 6))
        right.pack(side=pack_side_for_language(self.controller.language, "right"), fill="both", expand=False, padx=(6, 0))

        self.cart_tree = ttk.Treeview(left, columns=("name", "qty", "unit", "total"), show="headings", height=16, style="App.Treeview")
        self.cart_tree.pack(fill="both", expand=True)
        self.cart_tree.column("name", width=180, anchor="center")
        self.cart_tree.column("qty", width=70, anchor="center")
        self.cart_tree.column("unit", width=90, anchor="center")
        self.cart_tree.column("total", width=90, anchor="center")

        self.lbl_cart_msg = tk.Label(right, text="", bg=COLORS["surface"], font=FONT_LABEL, wraplength=260)
        self.lbl_cart_msg.pack(fill="x", pady=(0, 12))

        self.lbl_total_caption = tk.Label(right, text="", bg=COLORS["surface"], font=FONT_LABEL, fg=COLORS["muted"])
        self.lbl_total_caption.pack(anchor="w")
        self.lbl_total_value = tk.Label(right, text="OMR 0.000", bg=COLORS["surface"], font=("Arial", 20, "bold"), fg=COLORS["primary"])
        self.lbl_total_value.pack(anchor="w", pady=(4, 16))

        self.btn_place_order = base_button(right, "", self.place_order, bg=COLORS["secondary"], width=18)
        self.btn_place_order.pack(fill="x", pady=(0, 8))
        self.btn_clear_cart = ghost_button(right, "", self.clear_cart, width=18)
        self.btn_clear_cart.pack(fill="x", pady=(0, 8))
        self.btn_go_menu = ghost_button(right, "", lambda: self.show_view("menu"), width=18)
        self.btn_go_menu.pack(fill="x")

    def build_track_view(self):
        page = self.views["track"]
        top_stats = tk.Frame(page, bg=COLORS["bg"])
        top_stats.pack(fill="x", pady=(0, 10))

        self.track_order_card = make_stat_card(top_stats, "🧾", t("order_id", self.controller.language), "-", COLORS["secondary"])
        self.track_order_card.pack(side="left", fill="x", expand=True, padx=4)
        self.track_queue_card = make_stat_card(top_stats, "🔢", t("queue_position", self.controller.language), "-", COLORS["warning"])
        self.track_queue_card.pack(side="left", fill="x", expand=True, padx=4)
        self.track_status_card = make_stat_card(top_stats, "📦", t("order_status", self.controller.language), "-", COLORS["success"])
        self.track_status_card.pack(side="left", fill="x", expand=True, padx=4)

        lower = tk.Frame(page, bg=COLORS["bg"])
        lower.pack(fill="both", expand=True)
        left = make_card(lower, t("latest_order", self.controller.language))
        right = make_card(lower, t("order_items", self.controller.language))
        left.pack(side=pack_side_for_language(self.controller.language, "left"), fill="both", expand=True, padx=(0, 6))
        right.pack(side=pack_side_for_language(self.controller.language, "right"), fill="both", expand=True, padx=(6, 0))

        self.txt_track = tk.Text(left, height=18, font=FONT_TEXT, relief="flat", bg=COLORS["surface"])
        self.txt_track.pack(fill="both", expand=True)

        self.track_items_tree = ttk.Treeview(right, columns=("name", "qty", "unit", "total"), show="headings", height=18, style="App.Treeview")
        self.track_items_tree.pack(fill="both", expand=True)
        self.track_items_tree.column("name", width=180, anchor="center")
        self.track_items_tree.column("qty", width=70, anchor="center")
        self.track_items_tree.column("unit", width=90, anchor="center")
        self.track_items_tree.column("total", width=90, anchor="center")

        self.btn_refresh_track = base_button(page, "", self.load_latest_order, bg=COLORS["secondary"], width=16)
        
        self.btn_refresh_track.pack(
        pady=(10, 0),
        anchor=anchor_for_language(self.controller.language, "w")
        )
    def show_view(self, name):
        self.current_view = name
        mapping = {"menu": 0, "cart": 1, "track": 2}
        set_sidebar_active(self.sidebar_buttons, mapping[name])
        for frame in self.views.values():
            frame.pack_forget()
        self.views[name].pack(fill="both", expand=True)
        self.refresh_texts()
        if name == "menu":
            self.load_categories()
            self.load_menu_items()
        elif name == "cart":
            self.refresh_cart()
        elif name == "track":
            self.load_latest_order()

    def load_categories(self):
        for btn in self.category_buttons:
            btn.destroy()
        self.category_buttons.clear()

        lang = self.controller.language
        categories = ["All"] + get_categories()

        cap = tk.Label(self.categories_wrap, text=f"{t('categories', lang)}:", bg=COLORS["surface"], font=FONT_LABEL)
        cap.pack(side=pack_side_for_language(lang, "left"), padx=(0, 8))
        self.category_buttons.append(cap)

        for cat in categories:
            display = t("all", lang) if cat == "All" else cat
            btn = ghost_button(self.categories_wrap, display, lambda c=cat: self.set_category(c), width=12)
            btn.pack(side=pack_side_for_language(lang, "left"), padx=4)
            self.category_buttons.append(btn)

    def set_category(self, category):
        self.category_value = category
        self.load_menu_items()

    def load_menu_items(self):
        search_text = self.entry_search.get().strip() if hasattr(self, "entry_search") else ""
        self.menu_rows = get_menu_items(search_text, self.category_value)
        for row in self.menu_tree.get_children():
            self.menu_tree.delete(row)
        for item in self.menu_rows:
            self.menu_tree.insert("", tk.END, values=(item["id"], item["item_name"], item["category"], f"OMR {item['price']:.3f}"))
        self.update_summary_cards()

    def on_menu_select(self, _event=None):
        lang = self.controller.language
        selected = self.menu_tree.selection()
        if not selected:
            return
        item_id = int(self.menu_tree.item(selected[0])["values"][0])
        row = get_menu_item(item_id)
        if not row:
            return
        self.lbl_selected.config(text=row["item_name"])
        self.lbl_selected_desc.config(
            text=f"{row['description']}\n\n{t('category', lang)}: {row['category']}\n{t('price', lang)}: OMR {row['price']:.3f}"
        )
        apply_text_direction(self.lbl_selected_desc, lang)

    def add_to_cart(self):
        lang = self.controller.language
        selected = self.menu_tree.selection()
        if not selected:
            messagebox.showwarning(t("warning", lang), t("select_item", lang))
            return
        try:
            qty = int(self.spin_qty.get())
        except ValueError:
            messagebox.showerror(t("error", lang), t("invalid_quantity", lang))
            return
        if qty <= 0:
            messagebox.showerror(t("error", lang), t("invalid_quantity", lang))
            return

        item_id = int(self.menu_tree.item(selected[0])["values"][0])
        row = get_menu_item(item_id)
        if not row:
            return

        unit_price = float(row["price"])
        total_price = unit_price * qty
        self.cart_items.append(
            {
                "item_name": row["item_name"],
                "quantity": qty,
                "unit_price": unit_price,
                "total_price": total_price,
            }
        )
        self.refresh_cart()
        self.update_summary_cards()
        messagebox.showinfo(t("success", lang), t("item_added", lang))

    def refresh_cart(self):
        for row in self.cart_tree.get_children():
            self.cart_tree.delete(row)
        total = 0.0
        for item in self.cart_items:
            total += item["total_price"]
            self.cart_tree.insert(
                "",
                tk.END,
                values=(
                    item["item_name"],
                    item["quantity"],
                    f"OMR {item['unit_price']:.3f}",
                    f"OMR {item['total_price']:.3f}",
                ),
            )
        self.lbl_total_value.config(text=f"OMR {total:.3f}")
        self.update_summary_cards()

    def update_summary_cards(self):
        total_items = sum(item["quantity"] for item in self.cart_items)
        total_price = sum(item["total_price"] for item in self.cart_items)

        self.stat_menu.winfo_children()[1].config(text=str(len(self.menu_rows)))
        self.stat_cart.winfo_children()[1].config(text=str(total_items))
        self.stat_total.winfo_children()[1].config(text=f"OMR {total_price:.3f}")

    def clear_cart(self):
        self.cart_items.clear()
        self.refresh_cart()
        messagebox.showinfo(t("success", self.controller.language), t("cart_cleared", self.controller.language))

    def place_order(self):
        lang = self.controller.language
        if not self.cart_items:
            messagebox.showwarning(t("warning", lang), t("cart_empty", lang))
            return

        order_id, queue_position = create_order(self.controller.current_username, self.cart_items)
        self.cart_items.clear()
        self.refresh_cart()
        self.load_latest_order()
        self.show_view("track")
        messagebox.showinfo(t("success", lang), f"{t('order_saved', lang)}\n{t('order_id', lang)}: {order_id}\n{t('queue_position', lang)}: {queue_position}")

    def load_latest_order(self):
        lang = self.controller.language
        order = get_latest_order_for_customer(self.controller.current_username)
        self.txt_track.delete("1.0", tk.END)
        for row in self.track_items_tree.get_children():
            self.track_items_tree.delete(row)

        if not order:
            self.txt_track.insert(tk.END, t("no_orders", lang))
            self.track_order_card.winfo_children()[1].config(text="-")
            self.track_queue_card.winfo_children()[1].config(text="-")
            self.track_status_card.winfo_children()[1].config(text="-")
            return

        self.track_order_card.winfo_children()[1].config(text=str(order["id"]))
        self.track_queue_card.winfo_children()[1].config(text=str(order["queue_position"]))
        self.track_status_card.winfo_children()[1].config(text=order["status"])

        details = (
            f"{t('order_id', lang)}: {order['id']}\n"
            f"{t('total_price', lang)}: OMR {order['total_price']:.3f}\n"
            f"{t('order_status', lang)}: {order['status']}\n"
            f"{t('queue_position', lang)}: {order['queue_position']}\n"
            f"{t('created_at', lang)}: {order['created_at']}\n"
        )
        self.txt_track.insert(tk.END, details)
        apply_text_direction(self.txt_track, lang)

        for item in get_order_items(int(order["id"])):
            self.track_items_tree.insert(
                "",
                tk.END,
                values=(
                    item["item_name"],
                    item["quantity"],
                    f"OMR {item['unit_price']:.3f}",
                    f"OMR {item['total_price']:.3f}",
                ),
            )

    def refresh_texts(self):
        lang = self.controller.language
        self.lbl_title.config(text=t("customer_dashboard", lang))
        self.lbl_hint.config(text=t("customer_hint", lang), justify="right" if is_rtl(lang) else "left", anchor="e" if is_rtl(lang) else "w")
        self.btn_logout.config(text=t("logout", lang))
        self.lbl_search.config(text=f"{t('search', lang)}:")
        self.menu_tree.heading("id", text="ID")
        self.menu_tree.heading("name", text=t("item_name", lang))
        self.menu_tree.heading("category", text=t("category", lang))
        self.menu_tree.heading("price", text=t("price", lang))
        self.cart_tree.heading("name", text=t("item_name", lang))
        self.cart_tree.heading("qty", text=t("quantity", lang))
        self.cart_tree.heading("unit", text=t("price", lang))
        self.cart_tree.heading("total", text=t("total_price", lang))
        self.track_items_tree.heading("name", text=t("item_name", lang))
        self.track_items_tree.heading("qty", text=t("quantity", lang))
        self.track_items_tree.heading("unit", text=t("price", lang))
        self.track_items_tree.heading("total", text=t("total_price", lang))
        self.lbl_qty.config(text=f"{t('quantity', lang)}:")
        self.btn_add_to_cart.config(text=t("add_to_cart", lang))
        self.btn_open_cart.config(text=t("cart", lang))
        self.lbl_cart_msg.config(text=t("customer_hint", lang), justify="right" if is_rtl(lang) else "left", anchor="e" if is_rtl(lang) else "w")
        self.lbl_total_caption.config(text=t("total_price", lang))
        self.btn_place_order.config(text=t("place_order", lang))
        self.btn_clear_cart.config(text=t("clear_cart", lang))
        self.btn_go_menu.config(text=t("menu", lang))
        self.btn_refresh_track.config(text=t("refresh", lang))

    def on_show(self):
        self.refresh_texts()
        self.rebuild_sidebar()
        self.load_categories()
        if self.current_view == "menu":
            self.load_menu_items()
        elif self.current_view == "cart":
            self.refresh_cart()
        else:
            self.load_latest_order()
