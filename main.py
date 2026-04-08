import tkinter as tk
from tkinter import messagebox

from admin import AdminFrame
from customer import CustomerFrame
from database import init_db, validate_user
from staff import StaffFrame
from ui_styles import (
    COLORS,
    FONT_BIG,
    FONT_LABEL,
    FONT_SUBTITLE,
    FONT_TEXT,
    base_button,
    configure_styles,
    ghost_button,
    is_rtl,
    lang_button_text,
    make_card,
    pack_side_for_language,
    t,
)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        init_db()
        configure_styles()

        self.language = "en"
        self.current_username = ""
        self.current_role = "Customer"
        self.role_var = tk.StringVar(value="Customer")

        self.title(t("app_title", self.language))
        self.geometry("1320x780")
        self.minsize(1180, 700)
        self.configure(bg=COLORS["bg"])

        self.build_header()
        self.build_container()
        self.build_login_frame()
        self.build_role_frames()
        self.show_frame("login")

    def build_header(self):
        self.header = tk.Frame(self, bg=COLORS["primary"], height=68)
        self.header.pack(fill="x")
        self.header.pack_propagate(False)

        self.title_wrap = tk.Frame(self.header, bg=COLORS["primary"])
        self.title_wrap.pack(side="left", padx=18)
        self.lbl_app_title = tk.Label(self.title_wrap, text=t("app_title", self.language), font=("Arial", 18, "bold"), fg="white", bg=COLORS["primary"])
        self.lbl_app_title.pack(anchor="w")
        self.lbl_user = tk.Label(self.title_wrap, text=t("not_logged_in", self.language), font=FONT_LABEL, fg="#dce7f2", bg=COLORS["primary"])
        self.lbl_user.pack(anchor="w")

        self.actions_wrap = tk.Frame(self.header, bg=COLORS["primary"])
        self.actions_wrap.pack(side="right", padx=16)
        self.btn_language = ghost_button(self.actions_wrap, lang_button_text(self.language), self.toggle_language, width=6)
        self.btn_language.pack(side="right")

    def build_container(self):
        self.container = tk.Frame(self, bg=COLORS["bg"])
        self.container.pack(fill="both", expand=True)

    def build_login_frame(self):
        self.login_frame = tk.Frame(self.container, bg=COLORS["bg"])

        wrapper = tk.Frame(self.login_frame, bg=COLORS["bg"])
        wrapper.pack(fill="both", expand=True, padx=24, pady=24)

        welcome = tk.Frame(wrapper, bg=COLORS["primary"], width=520)
        welcome.pack(side=pack_side_for_language(self.language, "left"), fill="both", expand=True, padx=(0, 12))
        welcome.pack_propagate(False)

        tk.Label(welcome, text="🍔", bg=COLORS["primary"], fg="white", font=("Arial", 52)).pack(anchor="w", padx=30, pady=(40, 10))
        self.lbl_welcome_title = tk.Label(welcome, text="", bg=COLORS["primary"], fg="white", font=FONT_BIG, wraplength=420)
        self.lbl_welcome_title.pack(anchor="w", padx=30)
        self.lbl_welcome_desc = tk.Label(welcome, text="", bg=COLORS["primary"], fg="#dbe8f4", font=FONT_TEXT, wraplength=420)
        self.lbl_welcome_desc.pack(anchor="w", padx=30, pady=(14, 30))

        features = [
            "✔ Smart menu browsing",
            "✔ Cart and order tracking",
            "✔ Queue monitoring for staff",
            "✔ Reports for administrators",
        ]
        self.features_labels = []
        for line in features:
            lbl = tk.Label(welcome, text=line, bg=COLORS["primary"], fg="white", font=FONT_LABEL)
            lbl.pack(anchor="w", padx=32, pady=6)
            self.features_labels.append(lbl)

        right = tk.Frame(wrapper, bg=COLORS["bg"], width=520)
        right.pack(side=pack_side_for_language(self.language, "right"), fill="both", expand=True, padx=(12, 0))

        self.login_card = make_card(right, "")
        self.login_card.place(relx=0.5, rely=0.5, anchor="center", width=460, height=500)

        self.lbl_login_title = tk.Label(self.login_card, text="", bg=COLORS["surface"], fg=COLORS["text"], font=FONT_BIG)
        self.lbl_login_title.pack(anchor="w", pady=(6, 8))

        self.lbl_login_subtitle = tk.Label(self.login_card, text="", bg=COLORS["surface"], fg=COLORS["muted"], font=FONT_LABEL)
        self.lbl_login_subtitle.pack(anchor="w", pady=(0, 18))

        self.lbl_username = tk.Label(self.login_card, text="", bg=COLORS["surface"], font=FONT_LABEL)
        self.lbl_username.pack(anchor="w")
        self.entry_username = tk.Entry(self.login_card, font=FONT_TEXT)
        self.entry_username.pack(fill="x", pady=(4, 12))

        self.lbl_password = tk.Label(self.login_card, text="", bg=COLORS["surface"], font=FONT_LABEL)
        self.lbl_password.pack(anchor="w")
        self.entry_password = tk.Entry(self.login_card, font=FONT_TEXT, show="*")
        self.entry_password.pack(fill="x", pady=(4, 12))

        self.lbl_role = tk.Label(self.login_card, text="", bg=COLORS["surface"], font=FONT_LABEL)
        self.lbl_role.pack(anchor="w", pady=(0, 8))

        self.role_buttons_wrap = tk.Frame(self.login_card, bg=COLORS["surface"])
        self.role_buttons_wrap.pack(fill="x", pady=(0, 16))
        self.btn_role_customer = tk.Button(self.role_buttons_wrap, text="", command=lambda: self.set_role("Customer"), relief="flat", cursor="hand2", font=("Arial", 10, "bold"), pady=8)
        self.btn_role_staff = tk.Button(self.role_buttons_wrap, text="", command=lambda: self.set_role("Staff"), relief="flat", cursor="hand2", font=("Arial", 10, "bold"), pady=8)
        self.btn_role_admin = tk.Button(self.role_buttons_wrap, text="", command=lambda: self.set_role("Administrator"), relief="flat", cursor="hand2", font=("Arial", 10, "bold"), pady=8)
        self.btn_role_customer.pack(side="left", fill="x", expand=True, padx=4)
        self.btn_role_staff.pack(side="left", fill="x", expand=True, padx=4)
        self.btn_role_admin.pack(side="left", fill="x", expand=True, padx=4)

        self.btn_login = base_button(self.login_card, "", self.login, bg=COLORS["secondary"], width=18)
        self.btn_login.pack(fill="x", pady=(8, 10))
        self.btn_exit = ghost_button(self.login_card, "", self.destroy, width=18)
        self.btn_exit.pack(fill="x")

    def build_role_frames(self):
        self.frames = {
            "login": self.login_frame,
            "customer": CustomerFrame(self.container, self),
            "staff": StaffFrame(self.container, self),
            "admin": AdminFrame(self.container, self),
        }

    def set_role(self, role):
        self.current_role = role
        self.role_var.set(role)
        self.refresh_login_texts()

    def style_role_buttons(self):
        active_bg = COLORS["secondary"]
        inactive_bg = COLORS["surface_2"]
        active_fg = "white"
        inactive_fg = COLORS["primary"]

        mapping = {
            "Customer": self.btn_role_customer,
            "Staff": self.btn_role_staff,
            "Administrator": self.btn_role_admin,
        }
        for role, btn in mapping.items():
            if self.current_role == role:
                btn.configure(bg=active_bg, fg=active_fg, activebackground=active_bg, activeforeground=active_fg)
            else:
                btn.configure(bg=inactive_bg, fg=inactive_fg, activebackground=inactive_bg, activeforeground=inactive_fg)

    def refresh_login_texts(self):
        lang = self.language
        self.title(t("app_title", lang))
        self.lbl_app_title.config(text=t("app_title", lang))
        self.lbl_user.config(text=(f"{t('logged_in_as', lang)}: {self.current_username}" if self.current_username else t("not_logged_in", lang)))
        self.btn_language.config(text=lang_button_text(lang))

        self.lbl_welcome_title.config(text=t("welcome_title", lang), justify="right" if is_rtl(lang) else "left")
        self.lbl_welcome_desc.config(text=t("welcome_desc", lang), justify="right" if is_rtl(lang) else "left")

        features_en = [
            "✔ Smart menu browsing",
            "✔ Cart and order tracking",
            "✔ Queue monitoring for staff",
            "✔ Reports for administrators",
        ]
        features_ar = [
            "✔ تصفح ذكي للقائمة",
            "✔ سلة وتتبع كامل للطلب",
            "✔ متابعة الطابور للموظفين",
            "✔ تقارير واضحة للإدارة",
        ]
        for lbl, text in zip(self.features_labels, features_ar if is_rtl(lang) else features_en):
            lbl.config(text=text, anchor="e" if is_rtl(lang) else "w", justify="right" if is_rtl(lang) else "left")

        self.lbl_login_title.config(text=t("login", lang), anchor="e" if is_rtl(lang) else "w", justify="right" if is_rtl(lang) else "left")
        self.lbl_login_subtitle.config(text=t("welcome_desc", lang), anchor="e" if is_rtl(lang) else "w", justify="right" if is_rtl(lang) else "left")
        self.lbl_username.config(text=f"{t('username', lang)}:", anchor="e" if is_rtl(lang) else "w")
        self.lbl_password.config(text=f"{t('password', lang)}:", anchor="e" if is_rtl(lang) else "w")
        self.lbl_role.config(text=f"{t('role', lang)}:", anchor="e" if is_rtl(lang) else "w")
        self.btn_role_customer.config(text=t("customer", lang))
        self.btn_role_staff.config(text=t("staff", lang))
        self.btn_role_admin.config(text=t("administrator", lang))
        self.btn_login.config(text=t("login", lang))
        self.btn_exit.config(text=t("exit", lang))
        self.style_role_buttons()

    def refresh_all_texts(self):
        self.refresh_login_texts()
        for key in ["customer", "staff", "admin"]:
            self.frames[key].refresh_texts()

    def toggle_language(self):
        self.language = "ar" if self.language == "en" else "en"
        self.refresh_all_texts()

    def show_frame(self, name):
        for frame in self.frames.values():
            frame.pack_forget()
        frame = self.frames[name]
        frame.pack(fill="both", expand=True)
        if hasattr(frame, "on_show"):
            frame.on_show()
        if name == "login":
            self.refresh_login_texts()

    def login(self):
        lang = self.language
        username = self.entry_username.get().strip()
        password = self.entry_password.get().strip()
        role = self.current_role

        if not username or not password:
            messagebox.showerror(t("error", lang), t("enter_credentials", lang))
            return

        user = validate_user(username, password, role)
        if not user:
            messagebox.showerror(t("error", lang), t("invalid_login", lang))
            return

        self.current_username = username
        self.lbl_user.config(text=f"{t('logged_in_as', lang)}: {username}")

        role_map = {"Customer": "customer", "Staff": "staff", "Administrator": "admin"}
        self.show_frame(role_map[role])

    def logout(self):
        self.current_username = ""
        self.entry_password.delete(0, tk.END)
        self.lbl_user.config(text=t("not_logged_in", self.language))
        self.show_frame("login")


if __name__ == "__main__":
    app = App()
    app.mainloop()
