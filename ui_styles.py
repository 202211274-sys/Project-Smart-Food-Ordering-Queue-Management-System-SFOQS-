import tkinter as tk
from tkinter import ttk

COLORS = {
    "bg": "#eef3f8",
    "surface": "#ffffff",
    "surface_2": "#f8fbff",
    "primary": "#17324d",
    "primary_2": "#20476b",
    "secondary": "#2d89ef",
    "success": "#1fa971",
    "warning": "#f39c12",
    "danger": "#d64545",
    "muted": "#6c7a89",
    "text": "#17212b",
    "border": "#dbe5ef",
    "sidebar": "#12283d",
    "sidebar_hover": "#1c3b58",
    "card": "#ffffff",
}

FONT_TITLE = ("Arial", 18, "bold")
FONT_SUBTITLE = ("Arial", 14, "bold")
FONT_HEADER = ("Arial", 13, "bold")
FONT_LABEL = ("Arial", 11)
FONT_BUTTON = ("Arial", 10, "bold")
FONT_TEXT = ("Arial", 11)
FONT_BIG = ("Arial", 24, "bold")

TRANSLATIONS = {
    "app_title": {"en": "Smart Food Ordering & Queue Management System", "ar": "نظام الطلب الذكي وإدارة الطوابير"},
    "welcome_title": {"en": "Fast ordering. Clear queue. Better service.", "ar": "طلب أسرع. طابور أوضح. خدمة أفضل."},
    "welcome_desc": {"en": "A modern campus cafeteria system for customers, staff, and administrators.", "ar": "نظام حديث لإدارة طلبات الكافتيريا الجامعية للعملاء والموظفين والإدارة."},
    "login": {"en": "Sign In", "ar": "تسجيل الدخول"},
    "username": {"en": "Username", "ar": "اسم المستخدم"},
    "password": {"en": "Password", "ar": "كلمة المرور"},
    "role": {"en": "Role", "ar": "الدور"},
    "customer": {"en": "Customer", "ar": "العميل"},
    "staff": {"en": "Staff", "ar": "الموظف"},
    "administrator": {"en": "Administrator", "ar": "المدير"},
    "exit": {"en": "Exit", "ar": "خروج"},
    "logout": {"en": "Logout", "ar": "تسجيل الخروج"},
    "not_logged_in": {"en": "Not logged in", "ar": "لم يتم تسجيل الدخول"},
    "logged_in_as": {"en": "Logged in as", "ar": "تم تسجيل الدخول باسم"},
    "language": {"en": "Language", "ar": "اللغة"},
    "menu": {"en": "Menu", "ar": "القائمة"},
    "cart": {"en": "Cart", "ar": "السلة"},
    "track_order": {"en": "Track Order", "ar": "تتبع الطلب"},
    "dashboard": {"en": "Dashboard", "ar": "الرئيسية"},
    "orders": {"en": "Orders", "ar": "الطلبات"},
    "queue_control": {"en": "Queue Control", "ar": "إدارة الطابور"},
    "reports": {"en": "Reports", "ar": "التقارير"},
    "menu_management": {"en": "Menu Management", "ar": "إدارة القائمة"},
    "search": {"en": "Search", "ar": "بحث"},
    "all": {"en": "All", "ar": "الكل"},
    "categories": {"en": "Categories", "ar": "التصنيفات"},
    "digital_menu": {"en": "Digital Menu", "ar": "القائمة الرقمية"},
    "quantity": {"en": "Quantity", "ar": "الكمية"},
    "add_to_cart": {"en": "Add to Cart", "ar": "إضافة إلى السلة"},
    "clear_cart": {"en": "Clear Cart", "ar": "تفريغ السلة"},
    "place_order": {"en": "Place Order", "ar": "تنفيذ الطلب"},
    "your_cart": {"en": "Your Cart", "ar": "سلتك"},
    "order_tracking": {"en": "Order Tracking", "ar": "تتبع الطلب"},
    "latest_order": {"en": "Latest Order", "ar": "آخر طلب"},
    "queue_position": {"en": "Queue Position", "ar": "رقمك في الطابور"},
    "order_status": {"en": "Order Status", "ar": "حالة الطلب"},
    "refresh": {"en": "Refresh", "ar": "تحديث"},
    "item_name": {"en": "Item Name", "ar": "اسم الصنف"},
    "category": {"en": "Category", "ar": "التصنيف"},
    "description": {"en": "Description", "ar": "الوصف"},
    "price": {"en": "Price", "ar": "السعر"},
    "total_price": {"en": "Total Price", "ar": "الإجمالي"},
    "summary": {"en": "Summary", "ar": "الملخص"},
    "order_id": {"en": "Order ID", "ar": "رقم الطلب"},
    "created_at": {"en": "Created At", "ar": "تاريخ الإنشاء"},
    "queued": {"en": "Queued", "ar": "في الانتظار"},
    "preparing": {"en": "Preparing", "ar": "قيد التحضير"},
    "ready": {"en": "Ready", "ar": "جاهز"},
    "completed": {"en": "Completed", "ar": "مكتمل"},
    "select_item": {"en": "Please select an item", "ar": "يرجى اختيار صنف"},
    "select_order": {"en": "Please select an order", "ar": "يرجى اختيار طلب"},
    "invalid_login": {"en": "Invalid username, password, or role", "ar": "اسم المستخدم أو كلمة المرور أو الدور غير صحيح"},
    "enter_credentials": {"en": "Please enter username and password", "ar": "يرجى إدخال اسم المستخدم وكلمة المرور"},
    "invalid_quantity": {"en": "Invalid quantity", "ar": "الكمية غير صحيحة"},
    "cart_empty": {"en": "Your cart is empty", "ar": "السلة فارغة"},
    "item_added": {"en": "Item added successfully", "ar": "تمت إضافة الصنف بنجاح"},
    "cart_cleared": {"en": "Cart cleared", "ar": "تم تفريغ السلة"},
    "order_saved": {"en": "Order saved successfully", "ar": "تم حفظ الطلب بنجاح"},
    "no_orders": {"en": "No orders found for this customer.", "ar": "لا توجد طلبات لهذا العميل."},
    "status_updated": {"en": "Order status updated successfully", "ar": "تم تحديث حالة الطلب بنجاح"},
    "fill_menu_fields": {"en": "Please enter all menu fields", "ar": "يرجى إدخال جميع بيانات الصنف"},
    "invalid_price": {"en": "Invalid price", "ar": "السعر غير صحيح"},
    "item_deleted": {"en": "Item deleted successfully", "ar": "تم حذف الصنف بنجاح"},
    "summary_report": {"en": "Order Summary Report", "ar": "تقرير ملخص الطلبات"},
    "most_ordered_item": {"en": "Most Ordered Item", "ar": "الأكثر طلبًا"},
    "active_orders": {"en": "Active Orders", "ar": "الطلبات النشطة"},
    "total_orders": {"en": "Total Orders", "ar": "إجمالي الطلبات"},
    "success": {"en": "Success", "ar": "نجاح"},
    "warning": {"en": "Warning", "ar": "تنبيه"},
    "error": {"en": "Error", "ar": "خطأ"},
    "customer_dashboard": {"en": "Customer Dashboard", "ar": "لوحة العميل"},
    "staff_dashboard": {"en": "Staff Dashboard", "ar": "لوحة الموظف"},
    "admin_dashboard": {"en": "Administrator Dashboard", "ar": "لوحة المدير"},
    "order_items": {"en": "Order Items", "ar": "عناصر الطلب"},
    "item_count": {"en": "Items", "ar": "العناصر"},
    "quick_stats": {"en": "Quick Stats", "ar": "إحصاءات سريعة"},
    "customer_hint": {"en": "Choose items, build your cart, then place your order with one click.", "ar": "اختر الأصناف، كوّن سلتك، ثم نفذ الطلب بضغطة واحدة."},
    "team_hint": {"en": "Monitor queue positions and update order progress clearly.", "ar": "تابع الطابور وحدّث تقدم الطلبات بشكل واضح."},
    "menu_preview": {"en": "Menu Preview", "ar": "عرض القائمة"},
    "add_item": {"en": "Add Item", "ar": "إضافة صنف"},
    "delete_item": {"en": "Delete Item", "ar": "حذف الصنف"},
    "clear": {"en": "Clear", "ar": "مسح"},
}


def t(key, language="en"):
    return TRANSLATIONS.get(key, {}).get(language, key)


def is_rtl(language: str) -> bool:
    return language == "ar"


def configure_styles():
    style = ttk.Style()
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure("App.Treeview", font=FONT_TEXT, rowheight=30, background="white", fieldbackground="white", foreground=COLORS["text"])
    style.configure("App.Treeview.Heading", font=FONT_BUTTON, background=COLORS["surface_2"], foreground=COLORS["text"])
    style.map("App.Treeview", background=[("selected", "#dbeafe")], foreground=[("selected", COLORS["text"])])


def base_button(parent, text, command, bg=None, fg="white", width=14, padx=10, pady=8):
    btn = tk.Button(
        parent,
        text=text,
        command=command,
        bg=bg or COLORS["secondary"],
        fg=fg,
        activebackground=bg or COLORS["secondary"],
        activeforeground=fg,
        relief="flat",
        bd=0,
        width=width,
        font=FONT_BUTTON,
        cursor="hand2",
        padx=padx,
        pady=pady,
    )
    return btn


def ghost_button(parent, text, command, width=12):
    return tk.Button(
        parent,
        text=text,
        command=command,
        bg=COLORS["surface"],
        fg=COLORS["primary"],
        activebackground="#edf4fb",
        activeforeground=COLORS["primary"],
        relief="solid",
        bd=1,
        highlightthickness=0,
        width=width,
        font=FONT_BUTTON,
        cursor="hand2",
        padx=10,
        pady=7,
    )


def lang_button_text(language: str) -> str:
    return "AR" if language == "en" else "EN"


def make_card(parent, title=""):
    frame = tk.LabelFrame(
        parent,
        text=title,
        bg=COLORS["card"],
        fg=COLORS["text"],
        font=FONT_HEADER,
        bd=1,
        relief="solid",
        highlightthickness=0,
        padx=12,
        pady=12,
    )
    return frame


def make_stat_card(parent, icon, title, value, color):
    card = tk.Frame(parent, bg=COLORS["surface"], bd=1, relief="solid", highlightthickness=0)
    top = tk.Frame(card, bg=COLORS["surface"])
    top.pack(fill="x", padx=12, pady=(10, 0))
    tk.Label(top, text=icon, font=("Arial", 18), bg=COLORS["surface"], fg=color).pack(side="left")
    tk.Label(top, text=title, font=FONT_LABEL, bg=COLORS["surface"], fg=COLORS["muted"]).pack(side="left", padx=8)
    tk.Label(card, text=value, font=("Arial", 20, "bold"), bg=COLORS["surface"], fg=COLORS["text"]).pack(anchor="w", padx=14, pady=(6, 12))
    return card


def apply_text_direction(widget, language):
    try:
        widget.configure(justify="right" if is_rtl(language) else "left")
    except Exception:
        pass
    try:
        widget.configure(anchor="e" if is_rtl(language) else "w")
    except Exception:
        pass


def pack_side_for_language(language, default_ltr="left"):
    if default_ltr == "left":
        return "right" if is_rtl(language) else "left"
    if default_ltr == "right":
        return "left" if is_rtl(language) else "right"
    return default_ltr


def build_sidebar(parent, language, title, menu_items):
    sidebar = tk.Frame(parent, bg=COLORS["sidebar"], width=220)
    sidebar.pack(side=pack_side_for_language(language, "left"), fill="y")
    sidebar.pack_propagate(False)

    tk.Label(sidebar, text=title, bg=COLORS["sidebar"], fg="white", font=FONT_SUBTITLE).pack(anchor="w", padx=16, pady=(18, 14))

    button_refs = []
    for item in menu_items:
        btn = tk.Button(
            sidebar,
            text=item["text"],
            command=item["command"],
            bg=COLORS["sidebar"],
            fg="white",
            activebackground=COLORS["sidebar_hover"],
            activeforeground="white",
            relief="flat",
            bd=0,
            anchor="w" if not is_rtl(language) else "e",
            justify="left" if not is_rtl(language) else "right",
            font=FONT_BUTTON,
            cursor="hand2",
            padx=18,
            pady=12,
        )
        btn.pack(fill="x", padx=8, pady=4)
        button_refs.append(btn)

    return sidebar, button_refs
def anchor_for_language(language, default_ltr="w"):
    if default_ltr == "w":
        return "e" if is_rtl(language) else "w"
    if default_ltr == "e":
        return "w" if is_rtl(language) else "e"
    return default_ltr

def set_sidebar_active(buttons, active_index):
    for idx, btn in enumerate(buttons):
        btn.configure(bg=COLORS["sidebar_hover"] if idx == active_index else COLORS["sidebar"])
