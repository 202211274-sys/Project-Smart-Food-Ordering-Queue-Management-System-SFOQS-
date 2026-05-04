import tkinter as tk
from tkinter import messagebox, ttk

from database import (
    create_order,
    get_categories,
    get_latest_order_for_customer,
    get_orders_for_customer,
    get_menu_item,
    get_menu_items,
    get_order_items,
    get_cart_items_for_user,
    save_cart_for_user,
    clear_cart_for_user,
)

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
        self.track_orders_cache = []
        self.selected_track_order_id = None
        self.selected_cart_index = None
        self.menu_view_mode = "table"
        self.menu_card_widgets = []
        self.build_layout()
        self.show_view("menu")

    def build_layout(self):
        self.sidebar_container = tk.Frame(self, bg=COLORS["bg"])
        self.sidebar_container.pack(fill="both", expand=True)
        self.sidebar_container.grid_rowconfigure(0, weight=1)
        self.sidebar_container.grid_columnconfigure(1, weight=1)
    
        self.sidebar_host = tk.Frame(self.sidebar_container, bg=COLORS["bg"], width=260)
        self.sidebar_host.grid(row=0, column=0, sticky="nsw")
        self.sidebar_host.grid_propagate(False)
    
        self.content_host = tk.Frame(self.sidebar_container, bg=COLORS["bg"])
        self.content_host.grid(row=0, column=1, sticky="nsew")
    
        self.build_sidebar_panel()
        self.build_topbar()
        self.build_views()
    
    def build_sidebar_panel(self):
        for child in self.sidebar_host.winfo_children():
            child.destroy()

        self.sidebar, self.sidebar_buttons = build_sidebar(
            self.sidebar_host,
            self.controller.language,
            t("customer_dashboard", self.controller.language),
            [
                {"text": t("menu", self.controller.language), "icon": "menu", "command": lambda: self.show_view("menu")},
                {"text": t("cart", self.controller.language), "icon": "cart", "command": lambda: self.show_view("cart")},
                {"text": t("track_order", self.controller.language), "icon": "track", "command": lambda: self.show_view("track")},
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
        self.build_sidebar_panel()
        set_sidebar_active(self.sidebar_buttons, {"menu": 0, "cart": 1, "track": 2}[self.current_view])
        
        
    def show_inline_notice(self, message, bg="#dff6dd", fg="#1e4620"):
        self.lbl_menu_notice.pack_forget()
        self.lbl_menu_notice.config(text=message, bg=bg, fg=fg)

        # place notice always above the currently visible menu content
        if self.menu_view_mode == "table":
            self.lbl_menu_notice.pack(fill="x", pady=(0, 8), before=self.menu_tree)
        else:
            self.lbl_menu_notice.pack(fill="x", pady=(0, 8), before=self.menu_cards_container)

        self.after(2500, lambda: self.lbl_menu_notice.pack_forget())


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
        
        
        self.menu_topbar = tk.Frame(menu_card, bg=COLORS["surface"])
        self.menu_topbar.pack(fill="x", pady=(0, 8))

        self.btn_toggle_menu_view = ghost_button(
            self.menu_topbar,
            "",
            self.toggle_menu_view,
            width=18
        )
        self.btn_toggle_menu_view.pack(side="right")

        self.lbl_menu_notice = tk.Label(
            menu_card,
            text="",
            font=FONT_LABEL,
            anchor="w",
            padx=10,
            pady=6
        )

        self.menu_tree = ttk.Treeview(
            menu_card,
            columns=("id", "name", "category", "price"),
            show="headings",
            height=15,
            style="App.Treeview"
        )
        self.menu_tree.pack(fill="both", expand=True)
        self.menu_tree.column("id", width=60, anchor="center")
        self.menu_tree.column("name", width=180, anchor="center")
        self.menu_tree.column("category", width=120, anchor="center")
        self.menu_tree.column("price", width=90, anchor="center")
        self.menu_tree.bind("<<TreeviewSelect>>", self.on_menu_select)
        
        self.menu_cards_container = tk.Frame(menu_card, bg=COLORS["surface"])

        self.menu_cards_canvas = tk.Canvas(
            self.menu_cards_container,
            bg=COLORS["surface"],
            highlightthickness=0
        )
        self.menu_cards_scrollbar = tk.Scrollbar(
            self.menu_cards_container,
            orient="vertical",
            command=self.menu_cards_canvas.yview
        )
        self.menu_cards_inner = tk.Frame(self.menu_cards_canvas, bg=COLORS["surface"])

        self.menu_cards_inner.bind(
            "<Configure>",
            lambda e: self.menu_cards_canvas.configure(scrollregion=self.menu_cards_canvas.bbox("all"))
        )

        self.menu_cards_canvas.create_window((0, 0), window=self.menu_cards_inner, anchor="nw")
        self.menu_cards_canvas.configure(yscrollcommand=self.menu_cards_scrollbar.set)

        self.menu_cards_canvas.pack(side="left", fill="both", expand=True)
        self.menu_cards_scrollbar.pack(side="right", fill="y")

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
        self.update_menu_view_mode()

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
        self.cart_tree.bind("<<TreeviewSelect>>", self.on_cart_select)
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
        self.lbl_selected_cart_item_title = tk.Label(
            right,
            text="",
            bg=COLORS["surface"],
            font=FONT_LABEL,
            fg=COLORS["muted"]
        )
        self.lbl_selected_cart_item_title.pack(anchor="w", pady=(0, 4))
        self.lbl_selected_cart_item = tk.Label(
            right,
            text="-",
            bg=COLORS["surface"],
            font=("Arial", 12, "bold"),
            fg=COLORS["primary"]
        )
        self.lbl_selected_cart_item.pack(anchor="w", pady=(0, 10))

        qty_control = tk.Frame(right, bg=COLORS["surface"])
        qty_control.pack(fill="x", pady=(0, 12))

        self.btn_decrease_qty = ghost_button(qty_control, "-", self.decrease_cart_quantity, width=6)
        self.btn_decrease_qty.pack(side="left")

        self.lbl_selected_qty = tk.Label(
            qty_control,
            text="0",
            bg=COLORS["surface"],
            font=("Arial", 12, "bold"),
            width=6
        )
        self.lbl_selected_qty.pack(side="left", padx=8)

        self.btn_increase_qty = ghost_button(qty_control, "+", self.increase_cart_quantity, width=6)
        self.btn_increase_qty.pack(side="left")

        self.btn_remove_item = base_button(right, "", self.remove_selected_cart_item, bg=COLORS["danger"], width=18)
        self.btn_remove_item.pack(fill="x", pady=(0, 10))

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

        self.track_order_card = make_stat_card(
            top_stats, "🧾", t("order_id", self.controller.language), "-", COLORS["secondary"]
        )
        self.track_order_card.pack(side="left", fill="x", expand=True, padx=4)

        self.track_queue_card = make_stat_card(
            top_stats, "🔢", t("queue_position", self.controller.language), "-", COLORS["warning"]
        )
        self.track_queue_card.pack(side="left", fill="x", expand=True, padx=4)

        self.track_status_card = make_stat_card(
            top_stats, "📦", t("order_status", self.controller.language), "-", COLORS["success"]
        )
        self.track_status_card.pack(side="left", fill="x", expand=True, padx=4)

        # Main content area
        lower = tk.Frame(page, bg=COLORS["bg"])
        lower.pack(fill="both", expand=True)

        lower.grid_columnconfigure(0, weight=3, minsize=520)
        lower.grid_columnconfigure(1, weight=2, minsize=340)
        lower.grid_columnconfigure(2, weight=1, minsize=260)
        lower.grid_rowconfigure(0, weight=1)

        history_card = make_card(lower, t("order_history", self.controller.language))
        items_card  = make_card(lower, t("order_details", self.controller.language))
        details_card = make_card(lower, t("order_items", self.controller.language))
        
        history_card.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        items_card.grid(row=0, column=1, sticky="nsew", padx=6)
        details_card.grid(row=0, column=2, sticky="nsew", padx=(6, 0))

        # Order history
        self.track_orders_tree = ttk.Treeview(
            history_card,
            columns=("id", "status", "queue", "created"),
            show="headings",
            height=16,
            style="App.Treeview"
        )
        self.track_orders_tree.pack(fill="both", expand=True)

        self.track_orders_tree.column("id", width=75, anchor="center")
        self.track_orders_tree.column("status", width=130, anchor="center")
        self.track_orders_tree.column("queue", width=100, anchor="center")
        self.track_orders_tree.column("created", width=190, anchor="center")

        self.track_orders_tree.bind("<<TreeviewSelect>>", self.on_track_order_select)

        # Order details
        self.txt_track = tk.Text(
            details_card,
            height=18,
            font=FONT_TEXT,
            relief="flat",
            bg=COLORS["surface"],
            wrap="word",
            padx=12,
            pady=12
        )
        self.txt_track.pack(fill="both", expand=True)

        # Order items
        self.track_items_tree = ttk.Treeview(
            items_card,
            columns=("name", "qty", "unit", "total"),
            show="headings",
            height=18,
            style="App.Treeview"
        )
        self.track_items_tree.pack(fill="both", expand=True)

        self.track_items_tree.column("name", width=140, anchor="center")
        self.track_items_tree.column("qty", width=70, anchor="center")
        self.track_items_tree.column("unit", width=95, anchor="center")
        self.track_items_tree.column("total", width=95, anchor="center")

        # Refresh button
        self.btn_refresh_track = base_button(
            page, "", self.load_customer_orders, bg=COLORS["secondary"], width=16
        )
        self.btn_refresh_track.pack(
            pady=(10, 0),
            anchor=anchor_for_language(self.controller.language, "w")
        )

    def  show_view(self, name):
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
            self.load_cart_from_db()
            self.refresh_cart()
        elif name == "track":
            self.load_customer_orders()

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
            self.menu_tree.insert(
                "",
                tk.END,
                values=(item["id"], item["item_name"], item["category"], f"OMR {item['price']:.3f}")
            )

        self.update_summary_cards()
        self.update_menu_view_mode()

    def toggle_menu_view(self):
        if self.menu_view_mode == "table":
            self.menu_view_mode = "cards"
        else:
            self.menu_view_mode = "table"

        self.update_menu_view_mode()


    def update_menu_view_mode(self):
        if self.menu_view_mode == "table":
            self.menu_cards_container.pack_forget()
            self.menu_tree.pack(fill="both", expand=True)
            self.btn_toggle_menu_view.config(
                text="Cards View"
                if self.controller.language == "en"
                else "عرض البطاقات"
            )
        else:
            self.menu_tree.pack_forget()
            self.menu_cards_container.pack(fill="both", expand=True)
            self.build_menu_cards()
            self.btn_toggle_menu_view.config(
                text="Table View"
                if self.controller.language == "en"
                else "عرض الجدول"
            )


    def build_menu_cards(self):
        for child in self.menu_cards_inner.winfo_children():
            child.destroy()

        self.menu_card_widgets = []

        columns = 3
        for i in range(columns):
            self.menu_cards_inner.grid_columnconfigure(i, weight=1)

        for idx, item in enumerate(self.menu_rows):
            row = idx // columns
            col = idx % columns

            card = tk.Frame(
                self.menu_cards_inner,
                bg=COLORS["surface_2"],
                bd=1,
                relief="solid",
                cursor="hand2",
                padx=10,
                pady=10
            )
            card.grid(row=row, column=col, sticky="nsew", padx=8, pady=8)

            lbl_name = tk.Label(
                card,
                text=item["item_name"],
                bg=COLORS["surface_2"],
                fg=COLORS["primary"],
                font=("Arial", 12, "bold"),
                wraplength=180,
                justify="center"
            )
            lbl_name.pack(fill="x", pady=(0, 8))

            lbl_cat = tk.Label(
                card,
                text=f"{t('category', self.controller.language)}: {item['category']}",
                bg=COLORS["surface_2"],
                fg=COLORS["muted"],
                font=FONT_LABEL
            )
            lbl_cat.pack()

            lbl_price = tk.Label(
                card,
                text=f"OMR {float(item['price']):.3f}",
                bg=COLORS["surface_2"],
                fg=COLORS["success"],
                font=("Arial", 12, "bold")
            )
            lbl_price.pack(pady=(8, 0))

            # click card to add directly
            card.bind("<Button-1>", lambda e, item_id=item["id"]: self.add_menu_item_directly(item_id))
            lbl_name.bind("<Button-1>", lambda e, item_id=item["id"]: self.add_menu_item_directly(item_id))
            lbl_cat.bind("<Button-1>", lambda e, item_id=item["id"]: self.add_menu_item_directly(item_id))
            lbl_price.bind("<Button-1>", lambda e, item_id=item["id"]: self.add_menu_item_directly(item_id))

            self.menu_card_widgets.append(card)


    def add_menu_item_directly(self, item_id):
        row = get_menu_item(int(item_id))
        if not row:
            return

        unit_price = float(row["price"])
        qty = 1
        total_price = unit_price * qty

        found = False
        for item in self.cart_items:
            if item["item_name"] == row["item_name"] and float(item["unit_price"]) == unit_price:
                item["quantity"] += qty
                item["total_price"] = item["quantity"] * unit_price
                found = True
                break

        if not found:
            self.cart_items.append(
                {
                    "item_name": row["item_name"],
                    "quantity": qty,
                    "unit_price": unit_price,
                    "total_price": total_price,
                }
            )

        self.update_menu_summary(row)
        self.spin_qty.delete(0, tk.END)
        self.spin_qty.insert(0, "1")

        self.save_cart_to_db()
        self.refresh_cart()
        self.update_summary_cards()

        message = (
            f"{row['item_name']} added to cart"
            if self.controller.language == "en"
            else f"تمت إضافة {row['item_name']} إلى السلة"
        )
        self.show_inline_notice(message)

    
    
    def on_menu_select(self, _event=None):
        selected = self.menu_tree.selection()
        if not selected:
            return

        item_id = int(self.menu_tree.item(selected[0])["values"][0])
        row = get_menu_item(item_id)
        if not row:
            return

        self.update_menu_summary(row)

    def update_menu_summary(self, row):
        if not row:
            return

        lang = self.controller.language
        self.lbl_selected.config(text=row["item_name"])
        self.lbl_selected_desc.config(
            text=f"{row['description']}\n\n{t('category', lang)}: {row['category']}\n{t('price', lang)}: OMR {float(row['price']):.3f}"
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
        found = False
        for item in self.cart_items:
            if item["item_name"] == row["item_name"] and float(item["unit_price"]) == unit_price:
                item["quantity"] += qty
                item["total_price"] = item["quantity"] * unit_price
                found = True
                break
            
        if not found:
            self.cart_items.append(
                {
                    "item_name": row["item_name"],
                    "quantity": qty,
                    "unit_price": unit_price,
                    "total_price": total_price,
                }
            )
        self.update_menu_summary(row)

        self.save_cart_to_db()
        self.refresh_cart()
        self.update_summary_cards()

        selected_name = row["item_name"]
        message = (
            f"{selected_name} added to cart"
            if lang == "en"
            else f"تمت إضافة {selected_name} إلى السلة"
        )
        self.show_inline_notice(message)

    def on_cart_select(self, _event=None):
        selected = self.cart_tree.selection()
        if not selected:
            self.selected_cart_index = None
            self.update_cart_selection_panel()
            return

        item_id = selected[0]
        index = self.cart_tree.index(item_id)

        if index < 0 or index >= len(self.cart_items):
            self.selected_cart_index = None
        else:
            self.selected_cart_index = index

        self.update_cart_selection_panel()


    def update_cart_selection_panel(self):
        if self.selected_cart_index is None or self.selected_cart_index >= len(self.cart_items):
            self.lbl_selected_cart_item.config(text="-")
            self.lbl_selected_qty.config(text="0")
            return

        item = self.cart_items[self.selected_cart_index]
        self.lbl_selected_cart_item.config(text=item["item_name"])
        self.lbl_selected_qty.config(text=str(item["quantity"]))


    def increase_cart_quantity(self):
        if self.selected_cart_index is None:
            return

        if self.selected_cart_index >= len(self.cart_items):
            self.selected_cart_index = None
            self.update_cart_selection_panel()
            return

        self.cart_items[self.selected_cart_index]["quantity"] += 1
        qty = self.cart_items[self.selected_cart_index]["quantity"]
        unit_price = float(self.cart_items[self.selected_cart_index]["unit_price"])
        self.cart_items[self.selected_cart_index]["total_price"] = qty * unit_price

        self.refresh_cart()
        self.save_cart_to_db()


    def decrease_cart_quantity(self):
        if self.selected_cart_index is None:
            return

        if self.selected_cart_index >= len(self.cart_items):
            self.selected_cart_index = None
            self.update_cart_selection_panel()
            return

        current_qty = self.cart_items[self.selected_cart_index]["quantity"]

        if current_qty > 1:
            self.cart_items[self.selected_cart_index]["quantity"] -= 1
            qty = self.cart_items[self.selected_cart_index]["quantity"]
            unit_price = float(self.cart_items[self.selected_cart_index]["unit_price"])
            self.cart_items[self.selected_cart_index]["total_price"] = qty * unit_price
        else:
            del self.cart_items[self.selected_cart_index]
            self.selected_cart_index = None

        self.refresh_cart()
        self.save_cart_to_db()


    def remove_selected_cart_item(self):
        if self.selected_cart_index is None:
            messagebox.showwarning(t("warning", self.controller.language), t("select_item", self.controller.language))
            return

        if self.selected_cart_index >= len(self.cart_items):
            self.selected_cart_index = None
            self.update_cart_selection_panel()
            return

        del self.cart_items[self.selected_cart_index]
        self.selected_cart_index = None
        self.refresh_cart()
        self.save_cart_to_db()

    def refresh_cart(self):
        selected_name = None
        selected_qty = None

        if self.selected_cart_index is not None and self.selected_cart_index < len(self.cart_items):
            selected_name = self.cart_items[self.selected_cart_index]["item_name"]
            selected_qty = self.cart_items[self.selected_cart_index]["quantity"]

        for row in self.cart_tree.get_children():
            self.cart_tree.delete(row)

        total = 0.0
        new_selected_item_id = None

        for idx, item in enumerate(self.cart_items):
            total += item["total_price"]
            inserted_id = self.cart_tree.insert(
                "",
                tk.END,
                values=(
                    item["item_name"],
                    item["quantity"],
                    f"OMR {item['unit_price']:.3f}",
                    f"OMR {item['total_price']:.3f}",
                ),
            )

            if (
                selected_name is not None
                and item["item_name"] == selected_name
                and item["quantity"] == selected_qty
                and new_selected_item_id is None
            ):
                new_selected_item_id = inserted_id
                self.selected_cart_index = idx

        self.lbl_total_value.config(text=f"OMR {total:.3f}")
        self.update_summary_cards()

        if new_selected_item_id:
            self.cart_tree.selection_set(new_selected_item_id)
            self.cart_tree.focus(new_selected_item_id)
        else:
            if not self.cart_items:
                self.selected_cart_index = None

        self.update_cart_selection_panel()

    def update_summary_cards(self):
        total_items = sum(item["quantity"] for item in self.cart_items)
        total_price = sum(item["total_price"] for item in self.cart_items)

        self.stat_menu.winfo_children()[1].config(text=str(len(self.menu_rows)))
        self.stat_cart.winfo_children()[1].config(text=str(total_items))
        self.stat_total.winfo_children()[1].config(text=f"OMR {total_price:.3f}")

    def clear_cart(self):
        self.cart_items.clear()
        self.selected_cart_index = None
        self.refresh_cart()
        clear_cart_for_user(self.controller.current_username)
        messagebox.showinfo(
            t("success", self.controller.language),
            t("cart_cleared", self.controller.language)
        )
        
    def load_cart_from_db(self):
        self.cart_items = []

        rows = get_cart_items_for_user(self.controller.current_username)
        for row in rows:
            self.cart_items.append(
                {
                    "item_name": row["item_name"],
                    "quantity": int(row["quantity"]),
                    "unit_price": float(row["unit_price"]),
                    "total_price": float(row["total_price"]),
                }
            )
            
    def save_cart_to_db(self):
        save_cart_for_user(self.controller.current_username, self.cart_items)
    
    def place_order(self):
        lang = self.controller.language
        if not self.cart_items:
            messagebox.showwarning(t("warning", lang), t("cart_empty", lang))
            return

        order_id, queue_position = create_order(self.controller.current_username, self.cart_items)
        self.cart_items.clear()
        self.refresh_cart()
        clear_cart_for_user(self.controller.current_username)
        self.show_view("track")
        messagebox.showinfo(t("success", lang), f"{t('order_saved', lang)}\n{t('order_id', lang)}: {order_id}\n{t('queue_position', lang)}: {queue_position}")

    def load_customer_orders(self):
        lang = self.controller.language
        self.track_orders_cache = get_orders_for_customer(self.controller.current_username)

        for row in self.track_orders_tree.get_children():
            self.track_orders_tree.delete(row)

        self.txt_track.delete("1.0", tk.END)
        for row in self.track_items_tree.get_children():
            self.track_items_tree.delete(row)

        if not self.track_orders_cache:
            self.track_order_card.winfo_children()[1].config(text="-")
            self.track_queue_card.winfo_children()[1].config(text="-")
            self.track_status_card.winfo_children()[1].config(text="-")
            self.txt_track.insert(tk.END, t("no_orders", lang))
            apply_text_direction(self.txt_track, lang)
            self.selected_track_order_id = None
            return

        for order in self.track_orders_cache:
            self.track_orders_tree.insert(
                "",
                tk.END,
                values=(
                    order["id"],
                    order["status"],
                    order["queue_position"],
                    order["created_at"],
                ),
            )

        first_order = self.track_orders_cache[0]
        self.selected_track_order_id = int(first_order["id"])

        first_item = self.track_orders_tree.get_children()[0]
        self.track_orders_tree.selection_set(first_item)
        self.track_orders_tree.focus(first_item)

        self.display_track_order_details(first_order)


    def display_track_order_details(self, order):
        lang = self.controller.language

        self.track_order_card.winfo_children()[1].config(text=str(order["id"]))
        self.track_queue_card.winfo_children()[1].config(text=str(order["queue_position"]))
        self.track_status_card.winfo_children()[1].config(text=order["status"])

        self.txt_track.delete("1.0", tk.END)
        for row in self.track_items_tree.get_children():
            self.track_items_tree.delete(row)

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


    def on_track_order_select(self, _event=None):
        selected = self.track_orders_tree.selection()
        if not selected:
            return

        values = self.track_orders_tree.item(selected[0])["values"]
        selected_order_id = int(values[0])

        for order in self.track_orders_cache:
            if int(order["id"]) == selected_order_id:
                self.selected_track_order_id = selected_order_id
                self.display_track_order_details(order)
                break
        
    
    def refresh_texts(self):
        lang = self.controller.language
        self.lbl_title.config(text=t("customer_dashboard", lang))
        self.lbl_hint.config(text=t("customer_hint", lang), justify="left" if is_rtl(lang) else "left", anchor="e" if is_rtl(lang) else "w")
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
        self.lbl_selected_cart_item_title.config(text="Selected Item:" if lang == "en" else "الصنف المحدد:")
        self.btn_remove_item.config(text="Remove Item" if lang == "en" else "حذف الصنف")
        self.btn_place_order.config(text=t("place_order", lang))
        self.btn_clear_cart.config(text=t("clear_cart", lang))
        self.btn_go_menu.config(text=t("menu", lang))
        self.btn_refresh_track.config(text=t("refresh", lang))
        self.track_orders_tree.heading("id", text=t("order_id", lang))
        self.track_orders_tree.heading("status", text=t("order_status", lang))
        self.track_orders_tree.heading("queue", text=t("queue_position", lang))
        self.track_orders_tree.heading("created", text=t("created_at", lang))
        if self.menu_view_mode == "table":
            self.btn_toggle_menu_view.config(text=t("cards_view", lang))
        else:
            self.btn_toggle_menu_view.config(text=t("table_view", lang))
            
        self.stat_menu.winfo_children()[0].winfo_children()[1].config(text=t("menu_preview", lang))
        self.stat_cart.winfo_children()[0].winfo_children()[1].config(text=t("item_count", lang))
        self.stat_total.winfo_children()[0].winfo_children()[1].config(text=t("total_price", lang))
        self.track_order_card.winfo_children()[0].winfo_children()[1].config(text=t("order_id", lang))
        self.track_queue_card.winfo_children()[0].winfo_children()[1].config(text=t("queue_position", lang))
        self.track_status_card.winfo_children()[0].winfo_children()[1].config(text=t("order_status", lang))
        self.rebuild_sidebar()
        


    def on_show(self):
        self.refresh_texts()
        self.rebuild_sidebar()
        self.load_cart_from_db()
        self.load_categories()
        if self.current_view == "menu":
            self.load_menu_items()
        elif self.current_view == "cart":
            self.refresh_cart()
        else:
            self.load_customer_orders()
