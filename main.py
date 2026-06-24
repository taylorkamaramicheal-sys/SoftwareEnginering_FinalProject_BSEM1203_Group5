"""
main.py - Tkinter frontend for the Water Quality Monitoring System.

This file ONLY handles UI: building screens, widgets, and wiring button
clicks to DataManager methods. No business logic or file I/O lives here.
"""

import tkinter as tk
from tkinter import messagebox
from data import DataManager


# ----------------------------------------------------------------------
# Theme constants
# ----------------------------------------------------------------------
COLOR_BG = "#FFFFFF"
COLOR_LIGHT_BLUE = "#EAF2FB"
COLOR_DARK_BLUE = "#1A4D8F"
COLOR_BLUE = "#2E73C9"
COLOR_TEXT_DARK = "#1B1B1B"
COLOR_TEXT_MUTED = "#6B7280"
COLOR_GREEN = "#1E8E3E"
COLOR_RED = "#D93025"
COLOR_ORANGE = "#E8920B"
COLOR_BORDER = "#D6E2F0"

FONT_TITLE = ("Helvetica", 20, "bold")
FONT_SUBTITLE = ("Helvetica", 11)
FONT_LABEL = ("Helvetica", 10, "bold")
FONT_NORMAL = ("Helvetica", 10)
FONT_BUTTON = ("Helvetica", 11, "bold")
FONT_SMALL = ("Helvetica", 9)

STATUS_COLORS = {
    "safe": COLOR_GREEN,
    "unsafe": COLOR_RED,
    "moderate": COLOR_ORANGE,
}


class WaterQualityApp(tk.Tk):
    """Main application window that manages all screens."""

    def __init__(self):
        super().__init__()
        self.title("Water Quality Monitoring System")
        self.geometry("420x720")
        self.configure(bg=COLOR_BG)
        self.resizable(True, True)

        self.data_manager = DataManager()

        # Holds the currently logged-in user's email; None if logged out.
        self.current_user_email = None

        # Container that holds all screen frames stacked on top of each other.
        self.container = tk.Frame(self, bg=COLOR_BG)
        self.container.pack(fill="both", expand=True)

        self.frames = {}
        self._build_screens()

        self.show_screen("InitialScreen")

    # ------------------------------------------------------------------
    # Screen management
    # ------------------------------------------------------------------

    def _build_screens(self):
        screen_classes = (
            InitialScreen,
            LoginScreen,
            SignupScreen,
            DashboardScreen,
            ReportIssueScreen,
            MapScreen,
            WaterStatusSearchScreen,
            AlertsScreen,
            ProfileScreen,
            AdminDashboardScreen,
        )
        for ScreenClass in screen_classes:
            frame = ScreenClass(parent=self.container, app=self)
            self.frames[ScreenClass.__name__] = frame
            frame.place(x=0, y=0, relwidth=1, relheight=1)

    def show_screen(self, screen_name):
        frame = self.frames[screen_name]
        if hasattr(frame, "on_show"):
            frame.on_show()
        frame.tkraise()

    # ------------------------------------------------------------------
    # Session helpers
    # ------------------------------------------------------------------

    def login_user(self, email):
        self.current_user_email = email.strip().lower()

    def logout_user(self):
        self.current_user_email = None
        self.show_screen("InitialScreen")

    def get_current_user(self):
        if not self.current_user_email:
            return None
        return self.data_manager.get_user(self.current_user_email)


# ==========================================================================
# Reusable small widgets / helpers
# ==========================================================================

def make_nav_bar(parent, app, active="Home"):
    """Bottom navigation bar shown on user-facing screens."""
    nav = tk.Frame(parent, bg=COLOR_BG, height=55, highlightbackground=COLOR_BORDER,
                   highlightthickness=1)
    nav.pack(side="bottom", fill="x")

    items = [
        ("Home", "DashboardScreen"),
        ("Reports", "WaterStatusSearchScreen"),
        ("Map", "MapScreen"),
        ("Alerts", "AlertsScreen"),
        ("Profile", "ProfileScreen"),
    ]

    for label, screen_name in items:
        color = COLOR_DARK_BLUE if label == active else COLOR_TEXT_MUTED
        btn = tk.Button(
            nav, text=label, font=FONT_SMALL, fg=color, bg=COLOR_BG,
            bd=0, activebackground=COLOR_BG, cursor="hand2",
            command=lambda s=screen_name: app.show_screen(s)
        )
        btn.pack(side="left", expand=True, fill="both")

    return nav


def make_header(parent, title_text, app=None, back_screen=None, light=False):
    """Top header bar. If back_screen is given, shows a back arrow."""
    bg = COLOR_DARK_BLUE if not light else COLOR_BG
    fg = "white" if not light else COLOR_TEXT_DARK

    header = tk.Frame(parent, bg=bg, height=70)
    header.pack(side="top", fill="x")

    if back_screen and app:
        back_btn = tk.Button(
            header, text="\u2190", font=("Helvetica", 14, "bold"),
            fg=fg, bg=bg, bd=0, activebackground=bg, cursor="hand2",
            command=lambda: app.show_screen(back_screen)
        )
        back_btn.pack(side="left", padx=10, pady=15)

    title = tk.Label(header, text=title_text, font=FONT_BUTTON, fg=fg, bg=bg)
    title.pack(side="left", padx=10, pady=20)

    return header


def make_entry(parent, placeholder, show=None):
    """A simple styled entry with a placeholder label above it."""
    label = tk.Label(parent, text=placeholder, font=FONT_LABEL,
                      fg=COLOR_TEXT_DARK, bg=COLOR_BG, anchor="w")
    label.pack(fill="x", padx=30, pady=(10, 2))

    entry = tk.Entry(parent, font=FONT_NORMAL, bg=COLOR_LIGHT_BLUE,
                      relief="flat", highlightthickness=1,
                      highlightbackground=COLOR_BORDER,
                      highlightcolor=COLOR_BLUE, show=show if show else "")
    entry.pack(fill="x", padx=30, pady=(0, 4), ipady=8)
    return entry


def make_primary_button(parent, text, command):
    btn = tk.Button(
        parent, text=text, font=FONT_BUTTON, bg=COLOR_DARK_BLUE, fg="white",
        activebackground=COLOR_BLUE, activeforeground="white",
        relief="flat", bd=0, cursor="hand2", command=command
    )
    btn.pack(fill="x", padx=30, pady=(15, 5), ipady=10)
    return btn


def make_link_button(parent, text, command):
    btn = tk.Button(
        parent, text=text, font=FONT_NORMAL, bg=COLOR_BG, fg=COLOR_BLUE,
        bd=0, activebackground=COLOR_BG, cursor="hand2", command=command
    )
    return btn


def status_badge_color(status):
    return STATUS_COLORS.get(status, COLOR_TEXT_MUTED)


# ==========================================================================
# 1. INITIAL / WELCOME SCREEN
# ==========================================================================

class InitialScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLOR_LIGHT_BLUE)
        self.app = app

        center = tk.Frame(self, bg=COLOR_LIGHT_BLUE)
        center.place(relx=0.5, rely=0.42, anchor="center")

        drop = tk.Label(center, text="\U0001F4A7", font=("Helvetica", 60),
                         bg=COLOR_LIGHT_BLUE, fg=COLOR_BLUE)
        drop.pack(pady=(0, 10))

        title = tk.Label(center, text="WATER QUALITY", font=("Helvetica", 18, "bold"),
                          bg=COLOR_LIGHT_BLUE, fg=COLOR_DARK_BLUE)
        title.pack()
        subtitle = tk.Label(center, text="MONITORING SYSTEM", font=("Helvetica", 12, "bold"),
                             bg=COLOR_LIGHT_BLUE, fg=COLOR_DARK_BLUE)
        subtitle.pack(pady=(0, 15))

        tagline = tk.Label(center, text="Clean Water, Safe Communities\nBetter Water, Better Future.",
                            font=FONT_SUBTITLE, bg=COLOR_LIGHT_BLUE, fg=COLOR_TEXT_MUTED,
                            justify="center")
        tagline.pack()

        bottom = tk.Frame(self, bg=COLOR_LIGHT_BLUE)
        bottom.place(relx=0.5, rely=0.82, anchor="center")

        get_started_btn = tk.Button(
            bottom, text="Get Started", font=FONT_BUTTON, bg=COLOR_DARK_BLUE, fg="white",
            relief="flat", bd=0, cursor="hand2", width=22,
            command=lambda: app.show_screen("LoginScreen")
        )
        get_started_btn.pack(pady=10, ipady=8)


# ==========================================================================
# 2. LOGIN SCREEN
# ==========================================================================

class LoginScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLOR_BG)
        self.app = app

        header = tk.Frame(self, bg=COLOR_DARK_BLUE, height=160)
        header.pack(side="top", fill="x")

        tk.Label(header, text="Welcome Back!", font=("Helvetica", 18, "bold"),
                 fg="white", bg=COLOR_DARK_BLUE).pack(pady=(35, 5))
        tk.Label(header, text="Sign in to continue", font=FONT_SUBTITLE,
                 fg="white", bg=COLOR_DARK_BLUE).pack()

        body = tk.Frame(self, bg=COLOR_BG)
        body.pack(fill="both", expand=True)

        self.email_entry = make_entry(body, "Email")
        self.password_entry = make_entry(body, "Password", show="*")

        make_primary_button(body, "Login", self.handle_login)

        bottom = tk.Frame(body, bg=COLOR_BG)
        bottom.pack(pady=10)
        tk.Label(bottom, text="Don't have an account?", font=FONT_NORMAL,
                 bg=COLOR_BG, fg=COLOR_TEXT_MUTED).pack(side="left")
        signup_link = make_link_button(bottom, "Sign Up",
                                        lambda: app.show_screen("SignupScreen"))
        signup_link.pack(side="left")

    def on_show(self):
        self.email_entry.delete(0, "end")
        self.password_entry.delete(0, "end")

    def handle_login(self):
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()

        if not email or not password:
            messagebox.showerror("Login Failed", "Please enter both email and password.")
            return

        success, result = self.app.data_manager.validate_login(email, password)
        if not success:
            messagebox.showerror("Login Failed", result)
            return

        self.app.login_user(email)

        if self.app.data_manager.is_admin(email):
            self.app.show_screen("AdminDashboardScreen")
        else:
            self.app.show_screen("DashboardScreen")


# ==========================================================================
# 3. SIGNUP SCREEN
# ==========================================================================

class SignupScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLOR_BG)
        self.app = app

        make_header(self, "Create Account", app=app, back_screen="LoginScreen", light=True)

        tk.Label(self, text="Join us to help monitor water quality", font=FONT_SUBTITLE,
                 bg=COLOR_BG, fg=COLOR_TEXT_MUTED).pack(pady=(0, 10))

        body = tk.Frame(self, bg=COLOR_BG)
        body.pack(fill="both", expand=True)

        self.username_entry = make_entry(body, "Full Name")
        self.email_entry = make_entry(body, "Email (must be @gmail.com)")
        self.phone_entry = make_entry(body, "Phone Number (8-12 digits)")
        self.password_entry = make_entry(body, "Password (min 6 chars)", show="*")
        self.confirm_entry = make_entry(body, "Confirm Password", show="*")

        make_primary_button(body, "Register", self.handle_register)

        bottom = tk.Frame(body, bg=COLOR_BG)
        bottom.pack(pady=10)
        tk.Label(bottom, text="Already have an account?", font=FONT_NORMAL,
                 bg=COLOR_BG, fg=COLOR_TEXT_MUTED).pack(side="left")
        login_link = make_link_button(bottom, "Login",
                                       lambda: app.show_screen("LoginScreen"))
        login_link.pack(side="left")

    def on_show(self):
        for entry in (self.username_entry, self.email_entry, self.phone_entry,
                      self.password_entry, self.confirm_entry):
            entry.delete(0, "end")

    def handle_register(self):
        username = self.username_entry.get().strip()
        email = self.email_entry.get().strip()
        phone = self.phone_entry.get().strip()
        password = self.password_entry.get().strip()
        confirm = self.confirm_entry.get().strip()

        if not username:
            messagebox.showerror("Registration Failed", "Please enter your full name.")
            return

        if not email.lower().endswith("@gmail.com"):
            messagebox.showerror("Registration Failed", "Email must be a valid @gmail.com address.")
            return

        if not (phone.isdigit() and 8 <= len(phone) <= 12):
            messagebox.showerror("Registration Failed", "Phone number must be 8-12 digits.")
            return

        if len(password) < 6:
            messagebox.showerror("Registration Failed", "Password must be at least 6 characters.")
            return

        if password != confirm:
            messagebox.showerror("Registration Failed", "Passwords do not match.")
            return

        user = {
            "username": username,
            "email": email,
            "password": password,
            "phone": phone,
        }
        success, message = self.app.data_manager.add_user(user)

        if not success:
            messagebox.showerror("Registration Failed", message)
            return

        messagebox.showinfo("Success", message)
        self.app.show_screen("LoginScreen")


# ==========================================================================
# 4. DASHBOARD SCREEN
# ==========================================================================

class DashboardScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLOR_BG)
        self.app = app

        self.header = tk.Frame(self, bg=COLOR_DARK_BLUE, height=80)
        self.header.pack(side="top", fill="x")

        self.greeting_label = tk.Label(self.header, text="Hello!", font=("Helvetica", 16, "bold"),
                                        fg="white", bg=COLOR_DARK_BLUE)
        self.greeting_label.pack(anchor="w", padx=20, pady=(15, 0))
        tk.Label(self.header, text="Stay informed, stay safe.", font=FONT_SMALL,
                 fg="white", bg=COLOR_DARK_BLUE).pack(anchor="w", padx=20)

        self.scroll_body = tk.Frame(self, bg=COLOR_BG)
        self.scroll_body.pack(fill="both", expand=True)

        # ---- Overall status card ----
        self.status_card = tk.Frame(self.scroll_body, bg=COLOR_LIGHT_BLUE,
                                     highlightbackground=COLOR_BORDER, highlightthickness=1)
        self.status_card.pack(fill="x", padx=20, pady=15)

        tk.Label(self.status_card, text="Overall Water Status", font=FONT_LABEL,
                 bg=COLOR_LIGHT_BLUE, fg=COLOR_TEXT_DARK).pack(anchor="w", padx=15, pady=(12, 0))

        self.status_value_label = tk.Label(self.status_card, text="MODERATE",
                                            font=("Helvetica", 16, "bold"),
                                            bg=COLOR_LIGHT_BLUE, fg=COLOR_ORANGE)
        self.status_value_label.pack(anchor="w", padx=15)

        self.status_desc_label = tk.Label(self.status_card, text="", font=FONT_SMALL,
                                           bg=COLOR_LIGHT_BLUE, fg=COLOR_TEXT_MUTED,
                                           wraplength=320, justify="left")
        self.status_desc_label.pack(anchor="w", padx=15, pady=(0, 12))

        # ---- Stats boxes ----
        stats_frame = tk.Frame(self.scroll_body, bg=COLOR_BG)
        stats_frame.pack(fill="x", padx=20)

        self.total_box = self._make_stat_box(stats_frame, "Total", "0", COLOR_DARK_BLUE)
        self.safe_box = self._make_stat_box(stats_frame, "Safe", "0", COLOR_GREEN)
        self.unsafe_box = self._make_stat_box(stats_frame, "Unsafe", "0", COLOR_RED)
        self.moderate_box = self._make_stat_box(stats_frame, "Moderate", "0", COLOR_ORANGE)

        # ---- Quick actions ----
        tk.Label(self.scroll_body, text="Quick Actions", font=FONT_LABEL,
                 bg=COLOR_BG, fg=COLOR_TEXT_DARK).pack(anchor="w", padx=20, pady=(15, 5))

        actions_frame = tk.Frame(self.scroll_body, bg=COLOR_BG)
        actions_frame.pack(fill="x", padx=20)

        self._make_action_button(actions_frame, "Report Issue",
                                  lambda: app.show_screen("ReportIssueScreen"))
        self._make_action_button(actions_frame, "View Map",
                                  lambda: app.show_screen("MapScreen"))
        self._make_action_button(actions_frame, "Alerts",
                                  lambda: app.show_screen("AlertsScreen"))

        # ---- Admin-only button ----
        self.admin_btn = tk.Button(
            self.scroll_body, text="Go to Admin Dashboard", font=FONT_BUTTON,
            bg=COLOR_ORANGE, fg="white", relief="flat", bd=0, cursor="hand2",
            command=lambda: app.show_screen("AdminDashboardScreen")
        )
        # Packed conditionally in on_show()

        make_nav_bar(self, app, active="Home")

    def _make_stat_box(self, parent, label_text, value_text, color):
        box = tk.Frame(parent, bg=COLOR_LIGHT_BLUE, highlightbackground=COLOR_BORDER,
                        highlightthickness=1)
        box.pack(side="left", fill="both", expand=True, padx=4, pady=4)

        value_label = tk.Label(box, text=value_text, font=("Helvetica", 15, "bold"),
                                bg=COLOR_LIGHT_BLUE, fg=color)
        value_label.pack(pady=(10, 0))
        tk.Label(box, text=label_text, font=FONT_SMALL, bg=COLOR_LIGHT_BLUE,
                 fg=COLOR_TEXT_MUTED).pack(pady=(0, 10))

        box.value_label = value_label
        return box

    def _make_action_button(self, parent, text, command):
        btn = tk.Button(
            parent, text=text, font=FONT_NORMAL, bg=COLOR_LIGHT_BLUE, fg=COLOR_DARK_BLUE,
            relief="flat", bd=0, cursor="hand2", command=command
        )
        btn.pack(side="left", fill="both", expand=True, padx=4, pady=4, ipady=12)
        return btn

    def on_show(self):
        app = self.app
        user = app.get_current_user()
        if not user:
            return

        self.greeting_label.config(text=f"Hello, {user['username']}!")

        email = user["email"]
        total = app.data_manager.count_user_reports(email)
        safe = app.data_manager.count_status(email, "safe")
        unsafe = app.data_manager.count_status(email, "unsafe")
        moderate = app.data_manager.count_status(email, "moderate")
        overall = app.data_manager.get_overall_status(email)

        self.total_box.value_label.config(text=str(total))
        self.safe_box.value_label.config(text=str(safe))
        self.unsafe_box.value_label.config(text=str(unsafe))
        self.moderate_box.value_label.config(text=str(moderate))

        status_styles = {
            "GOOD": (COLOR_GREEN, "Water quality is acceptable in most areas."),
            "BAD": (COLOR_RED, "Unsafe water reported. Please take precautions."),
            "MODERATE": (COLOR_ORANGE, "Water quality varies. Stay cautious."),
        }
        color, desc = status_styles.get(overall, status_styles["MODERATE"])
        self.status_value_label.config(text=overall, fg=color)
        self.status_desc_label.config(text=desc)

        if app.data_manager.is_admin(email):
            self.admin_btn.pack(fill="x", padx=20, pady=(10, 15), ipady=10)
        else:
            self.admin_btn.pack_forget()


# ==========================================================================
# 5. REPORT ISSUE SCREEN
# ==========================================================================

class ReportIssueScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLOR_BG)
        self.app = app
        self.selected_status = tk.StringVar(value="")

        make_header(self, "Report Water Issue", app=app, back_screen="DashboardScreen")

        body = tk.Frame(self, bg=COLOR_BG)
        body.pack(fill="both", expand=True)

        self.location_entry = make_entry(body, "Location")

        tk.Label(body, text="Issue Status", font=FONT_LABEL, bg=COLOR_BG,
                 fg=COLOR_TEXT_DARK, anchor="w").pack(fill="x", padx=30, pady=(10, 4))

        status_frame = tk.Frame(body, bg=COLOR_BG)
        status_frame.pack(fill="x", padx=30)

        self.status_buttons = {}
        for status, color in (("safe", COLOR_GREEN), ("unsafe", COLOR_RED), ("moderate", COLOR_ORANGE)):
            btn = tk.Button(
                status_frame, text=status.capitalize(), font=FONT_NORMAL,
                bg=COLOR_LIGHT_BLUE, fg=color, relief="flat", bd=0, cursor="hand2",
                command=lambda s=status: self.select_status(s)
            )
            btn.pack(side="left", fill="both", expand=True, padx=3, ipady=8)
            self.status_buttons[status] = btn

        tk.Label(body, text="Description", font=FONT_LABEL, bg=COLOR_BG,
                 fg=COLOR_TEXT_DARK, anchor="w").pack(fill="x", padx=30, pady=(15, 2))

        self.description_text = tk.Text(body, font=FONT_NORMAL, bg=COLOR_LIGHT_BLUE,
                                         relief="flat", height=5, highlightthickness=1,
                                         highlightbackground=COLOR_BORDER,
                                         highlightcolor=COLOR_BLUE, wrap="word")
        self.description_text.pack(fill="x", padx=30, pady=(0, 4))

        make_primary_button(body, "Submit Report", self.handle_submit)

        exit_btn = tk.Button(
            body, text="Cancel", font=FONT_NORMAL, bg=COLOR_BG, fg=COLOR_TEXT_MUTED,
            bd=0, cursor="hand2", command=lambda: app.show_screen("DashboardScreen")
        )
        exit_btn.pack(pady=5)

    def select_status(self, status):
        self.selected_status.set(status)
        for s, btn in self.status_buttons.items():
            if s == status:
                btn.config(bg=status_badge_color(s), fg="white")
            else:
                btn.config(bg=COLOR_LIGHT_BLUE, fg=status_badge_color(s))

    def on_show(self):
        self.location_entry.delete(0, "end")
        self.description_text.delete("1.0", "end")
        self.selected_status.set("")
        for s, btn in self.status_buttons.items():
            btn.config(bg=COLOR_LIGHT_BLUE, fg=status_badge_color(s))

    def handle_submit(self):
        app = self.app
        user = app.get_current_user()
        if not user:
            messagebox.showerror("Error", "You must be logged in to submit a report.")
            return

        location = self.location_entry.get().strip()
        description = self.description_text.get("1.0", "end").strip()
        status = self.selected_status.get()

        if not location:
            messagebox.showerror("Invalid Input", "Please enter a location.")
            return
        if location.isdigit():
            messagebox.showerror("Invalid Input", "Location cannot be only numbers.")
            return

        if not status:
            messagebox.showerror("Invalid Input", "Please select an issue status.")
            return

        if not description:
            messagebox.showerror("Invalid Input", "Please enter a description.")
            return
        if description.isdigit():
            messagebox.showerror("Invalid Input", "Description cannot be only numbers.")
            return

        success, message = app.data_manager.add_report(
            email=user["email"],
            username=user["username"],
            location=location,
            status=status,
            description=description,
        )

        if not success:
            messagebox.showerror("Submission Failed", message)
            return

        messagebox.showinfo("Success", message)
        app.show_screen("DashboardScreen")


# ==========================================================================
# 6. MAP SCREEN
# ==========================================================================

class MapScreen(tk.Frame):
    """
    A built-in (no external map API) visual map of reported water locations.
    Each unique location is plotted as a colored pin on a canvas using
    deterministic coordinates from DataManager.get_map_pins(). Clicking a
    pin shows its details. A legend explains the color coding, matching
    the Figma 'Map Screen' design (Safe / Moderate / Unsafe).
    """

    CANVAS_WIDTH = 400
    CANVAS_HEIGHT = 480
    PIN_RADIUS = 9

    def __init__(self, parent, app):
        super().__init__(parent, bg=COLOR_BG)
        self.app = app
        self.pin_items = {}  # canvas item id -> pin dict

        make_header(self, "Water Quality Map", app=app, back_screen="DashboardScreen")

        toolbar = tk.Frame(self, bg=COLOR_BG)
        toolbar.pack(fill="x", padx=15, pady=(8, 4))

        tk.Label(toolbar, text="Tap a pin to see report details", font=FONT_SMALL,
                 bg=COLOR_BG, fg=COLOR_TEXT_MUTED).pack(side="left")

        refresh_btn = tk.Button(
            toolbar, text="Refresh", font=FONT_SMALL, bg=COLOR_LIGHT_BLUE, fg=COLOR_DARK_BLUE,
            relief="flat", bd=0, cursor="hand2", command=self.refresh_map
        )
        refresh_btn.pack(side="right", ipadx=8, ipady=3)

        canvas_frame = tk.Frame(self, bg=COLOR_BG, highlightbackground=COLOR_BORDER,
                                 highlightthickness=1)
        canvas_frame.pack(padx=15, pady=(0, 8))

        self.canvas = tk.Canvas(canvas_frame, width=self.CANVAS_WIDTH, height=self.CANVAS_HEIGHT,
                                 bg="#DCEBFA", highlightthickness=0)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        # Legend matching the Figma map screen (Safe / Moderate / Unsafe).
        legend = tk.Frame(self, bg=COLOR_BG)
        legend.pack(fill="x", padx=15, pady=(0, 5))

        for status, color in (("Safe", COLOR_GREEN), ("Moderate", COLOR_ORANGE), ("Unsafe", COLOR_RED)):
            item = tk.Frame(legend, bg=COLOR_BG)
            item.pack(side="left", expand=True)
            dot = tk.Canvas(item, width=14, height=14, bg=COLOR_BG, highlightthickness=0)
            dot.create_oval(2, 2, 12, 12, fill=color, outline="")
            dot.pack(side="left")
            tk.Label(item, text=status, font=FONT_SMALL, bg=COLOR_BG,
                     fg=COLOR_TEXT_DARK).pack(side="left", padx=(4, 0))

        # Detail panel shown when a pin is tapped.
        self.detail_frame = tk.Frame(self, bg=COLOR_LIGHT_BLUE, highlightbackground=COLOR_BORDER,
                                      highlightthickness=1)
        self.detail_status = tk.Label(self.detail_frame, text="", font=FONT_LABEL, bg=COLOR_LIGHT_BLUE)
        self.detail_status.pack(anchor="w", padx=12, pady=(8, 0))
        self.detail_location = tk.Label(self.detail_frame, text="", font=FONT_NORMAL, bg=COLOR_LIGHT_BLUE,
                                         fg=COLOR_TEXT_DARK)
        self.detail_location.pack(anchor="w", padx=12)
        self.detail_meta = tk.Label(self.detail_frame, text="", font=FONT_SMALL, bg=COLOR_LIGHT_BLUE,
                                     fg=COLOR_TEXT_MUTED, wraplength=360, justify="left")
        self.detail_meta.pack(anchor="w", padx=12, pady=(0, 8))

        make_nav_bar(self, app, active="Map")

    def on_show(self):
        self.detail_frame.pack_forget()
        self.refresh_map()

    def refresh_map(self):
        canvas = self.canvas
        canvas.delete("all")
        self.pin_items = {}

        # Light "water grid" background texture for visual depth.
        step = 40
        for x in range(0, self.CANVAS_WIDTH, step):
            canvas.create_line(x, 0, x, self.CANVAS_HEIGHT, fill="#CFE3F7")
        for y in range(0, self.CANVAS_HEIGHT, step):
            canvas.create_line(0, y, self.CANVAS_WIDTH, y, fill="#CFE3F7")

        app = self.app
        pins = app.data_manager.get_map_pins()

        if not pins:
            canvas.create_text(
                self.CANVAS_WIDTH / 2, self.CANVAS_HEIGHT / 2,
                text="No reports yet.\nSubmit a report to see it on the map.",
                font=FONT_NORMAL, fill=COLOR_TEXT_MUTED, justify="center"
            )
            return

        for pin in pins:
            x = pin["x_ratio"] * self.CANVAS_WIDTH
            y = pin["y_ratio"] * self.CANVAS_HEIGHT
            color = status_badge_color(pin["status"])
            r = self.PIN_RADIUS

            # Pin body (circle) plus a small triangular point underneath
            # to look more like a map marker than a plain dot.
            body = canvas.create_oval(x - r, y - r, x + r, y + r,
                                       fill=color, outline="white", width=2)
            point = canvas.create_polygon(
                x - 4, y + r - 2, x + 4, y + r - 2, x, y + r + 8,
                fill=color, outline=""
            )
            label = canvas.create_text(
                x, y - r - 10, text=pin["location"], font=FONT_SMALL, fill=COLOR_TEXT_DARK
            )

            for item_id in (body, point, label):
                self.pin_items[item_id] = pin

    def on_canvas_click(self, event):
        clicked = self.canvas.find_closest(event.x, event.y)
        if not clicked:
            return
        item_id = clicked[0]
        pin = self.pin_items.get(item_id)
        if not pin:
            self.detail_frame.pack_forget()
            return

        color = status_badge_color(pin["status"])
        self.detail_status.config(text=pin["status"].upper(), fg=color)
        self.detail_location.config(text=pin["location"])
        verified_text = "Verified report" if pin.get("verified") else "Pending verification"
        self.detail_meta.config(
            text=f"{pin['description']}\nReported by {pin['username']} on {pin['timestamp']} \u2022 {verified_text}"
        )
        self.detail_frame.pack(fill="x", padx=15, pady=(0, 10))


# ==========================================================================
# 7. WATER STATUS / SEARCH SCREEN
# ==========================================================================

class WaterStatusSearchScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLOR_BG)
        self.app = app

        make_header(self, "My Reports", app=app, back_screen="DashboardScreen")

        search_frame = tk.Frame(self, bg=COLOR_BG)
        search_frame.pack(fill="x", padx=20, pady=(10, 5))

        self.search_entry = tk.Entry(search_frame, font=FONT_NORMAL, bg=COLOR_LIGHT_BLUE,
                                      relief="flat", highlightthickness=1,
                                      highlightbackground=COLOR_BORDER,
                                      highlightcolor=COLOR_BLUE)
        self.search_entry.pack(side="left", fill="x", expand=True, ipady=7)
        self.search_entry.bind("<KeyRelease>", lambda e: self.refresh_list())

        search_btn = tk.Button(
            search_frame, text="Search", font=FONT_SMALL, bg=COLOR_DARK_BLUE, fg="white",
            relief="flat", bd=0, cursor="hand2", command=self.refresh_list
        )
        search_btn.pack(side="left", padx=(8, 0), ipady=7, ipadx=8)

        # Scrollable list area
        list_container = tk.Frame(self, bg=COLOR_BG)
        list_container.pack(fill="both", expand=True, padx=10)

        self.canvas = tk.Canvas(list_container, bg=COLOR_BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(list_container, orient="vertical", command=self.canvas.yview)
        self.list_frame = tk.Frame(self.canvas, bg=COLOR_BG)

        self.list_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.create_window((0, 0), window=self.list_frame, anchor="nw", width=380)
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        make_nav_bar(self, app, active="Reports")

    def on_show(self):
        self.search_entry.delete(0, "end")
        self.refresh_list()

    def refresh_list(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        app = self.app
        user = app.get_current_user()
        if not user:
            return

        keyword = self.search_entry.get().strip()
        reports = app.data_manager.search_reports(user["email"], keyword)

        if not reports:
            tk.Label(self.list_frame, text="No reports found.", font=FONT_NORMAL,
                     bg=COLOR_BG, fg=COLOR_TEXT_MUTED).pack(pady=30)
            return

        for report in reports:
            self._build_report_row(report)

    def _build_report_row(self, report):
        row = tk.Frame(self.list_frame, bg=COLOR_LIGHT_BLUE, highlightbackground=COLOR_BORDER,
                        highlightthickness=1)
        row.pack(fill="x", pady=5, padx=5)

        top_row = tk.Frame(row, bg=COLOR_LIGHT_BLUE)
        top_row.pack(fill="x", padx=10, pady=(8, 0))

        color = status_badge_color(report["status"])
        dot = tk.Label(top_row, text="\u25CF", font=("Helvetica", 12), fg=color, bg=COLOR_LIGHT_BLUE)
        dot.pack(side="left")

        status_label = tk.Label(top_row, text=report["status"].upper(), font=FONT_LABEL,
                                 fg=color, bg=COLOR_LIGHT_BLUE)
        status_label.pack(side="left", padx=(5, 0))

        verified_text = "Verified" if report.get("verified") else "Pending"
        verified_label = tk.Label(top_row, text=verified_text, font=FONT_SMALL,
                                   fg=COLOR_TEXT_MUTED, bg=COLOR_LIGHT_BLUE)
        verified_label.pack(side="right")

        tk.Label(row, text=report["location"], font=FONT_NORMAL, fg=COLOR_TEXT_DARK,
                 bg=COLOR_LIGHT_BLUE, anchor="w").pack(fill="x", padx=10, pady=(2, 0))

        tk.Label(row, text=report["description"], font=FONT_SMALL, fg=COLOR_TEXT_MUTED,
                 bg=COLOR_LIGHT_BLUE, anchor="w", wraplength=340, justify="left").pack(
            fill="x", padx=10, pady=(2, 0))

        tk.Label(row, text=report["timestamp"], font=FONT_SMALL, fg=COLOR_TEXT_MUTED,
                 bg=COLOR_LIGHT_BLUE, anchor="w").pack(fill="x", padx=10, pady=(2, 8))


# ==========================================================================
# 8. ALERTS SCREEN
# ==========================================================================

class AlertsScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLOR_BG)
        self.app = app

        make_header(self, "Alerts & Notifications", app=app, back_screen="DashboardScreen")

        self.badge_frame = tk.Frame(self, bg=COLOR_BG)
        self.badge_frame.pack(fill="x", padx=20, pady=10)

        self.badge_label = tk.Label(self.badge_frame, text="No alerts yet", font=("Helvetica", 12, "bold"),
                                     bg=COLOR_LIGHT_BLUE, fg=COLOR_TEXT_DARK, padx=15, pady=12)
        self.badge_label.pack(fill="x")
        self.badge_label.bind("<Button-1>", lambda e: self.clear_alert())

        tk.Label(self, text="Tap the alert above to mark it as read.", font=FONT_SMALL,
                 bg=COLOR_BG, fg=COLOR_TEXT_MUTED).pack(pady=(0, 10))

        list_container = tk.Frame(self, bg=COLOR_BG)
        list_container.pack(fill="both", expand=True, padx=10)

        self.canvas = tk.Canvas(list_container, bg=COLOR_BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(list_container, orient="vertical", command=self.canvas.yview)
        self.list_frame = tk.Frame(self.canvas, bg=COLOR_BG)

        self.list_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.create_window((0, 0), window=self.list_frame, anchor="nw", width=380)
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        make_nav_bar(self, app, active="Alerts")

        self.alert_cleared = False

    def on_show(self):
        self.refresh()

    def clear_alert(self):
        self.alert_cleared = True
        self.refresh()

    def refresh(self):
        app = self.app
        user = app.get_current_user()
        if not user:
            return

        last_report = app.data_manager.get_last_report(user["email"])

        if not last_report or self.alert_cleared:
            self.badge_label.config(text="No new alerts", bg=COLOR_LIGHT_BLUE, fg=COLOR_TEXT_MUTED)
        else:
            status = last_report["status"]
            color = status_badge_color(status)
            text_map = {
                "unsafe": "ALERT: Unsafe water reported recently!",
                "safe": "Good news: Water reported safe recently.",
                "moderate": "Notice: Moderate water quality reported.",
            }
            self.badge_label.config(text=text_map.get(status, "New alert"), bg=color, fg="white")

        for widget in self.list_frame.winfo_children():
            widget.destroy()

        reports = app.data_manager.get_user_reports(user["email"])
        grouped = {"unsafe": [], "moderate": [], "safe": []}
        for r in reports:
            grouped.setdefault(r["status"], []).append(r)

        any_alerts = False
        for status in ("unsafe", "moderate", "safe"):
            group = grouped.get(status, [])
            if not group:
                continue
            any_alerts = True
            section = tk.Label(self.list_frame, text=f"{status.upper()} ({len(group)})",
                                font=FONT_LABEL, fg=status_badge_color(status), bg=COLOR_BG,
                                anchor="w")
            section.pack(fill="x", padx=10, pady=(10, 2))

            for r in group:
                row = tk.Frame(self.list_frame, bg=COLOR_LIGHT_BLUE, highlightbackground=COLOR_BORDER,
                                highlightthickness=1)
                row.pack(fill="x", padx=5, pady=3)
                tk.Label(row, text=f"{r['location']}", font=FONT_NORMAL, bg=COLOR_LIGHT_BLUE,
                         fg=COLOR_TEXT_DARK, anchor="w").pack(fill="x", padx=10, pady=(6, 0))
                tk.Label(row, text=r["timestamp"], font=FONT_SMALL, bg=COLOR_LIGHT_BLUE,
                         fg=COLOR_TEXT_MUTED, anchor="w").pack(fill="x", padx=10, pady=(0, 6))

        if not any_alerts:
            tk.Label(self.list_frame, text="No reports yet.", font=FONT_NORMAL,
                     bg=COLOR_BG, fg=COLOR_TEXT_MUTED).pack(pady=30)


# ==========================================================================
# 9. PROFILE SCREEN
# ==========================================================================

class ProfileScreen(tk.Frame):
    AVATAR_COLORS = {
        "blue": "#2E73C9",
        "green": "#1E8E3E",
        "orange": "#E8920B",
        "purple": "#7B4FC9",
        "teal": "#149C9C",
        "red": "#D93025",
    }

    def __init__(self, parent, app):
        super().__init__(parent, bg=COLOR_BG)
        self.app = app

        header = tk.Frame(self, bg=COLOR_DARK_BLUE, height=160)
        header.pack(side="top", fill="x")

        self.avatar_canvas = tk.Canvas(header, width=70, height=70, bg=COLOR_DARK_BLUE,
                                        highlightthickness=0, cursor="hand2")
        self.avatar_canvas.pack(pady=(18, 5))
        self.avatar_canvas.bind("<Button-1>", lambda e: self.open_avatar_picker())

        tip = tk.Label(header, text="Tap avatar to change", font=("Helvetica", 7),
                        bg=COLOR_DARK_BLUE, fg="#CFE0F5")
        tip.pack()

        self.username_label = tk.Label(header, text="Username", font=("Helvetica", 14, "bold"),
                                        bg=COLOR_DARK_BLUE, fg="white")
        self.username_label.pack()

        self.email_label = tk.Label(header, text="email@example.com", font=FONT_SMALL,
                                     bg=COLOR_DARK_BLUE, fg="white")
        self.email_label.pack()

        body = tk.Frame(self, bg=COLOR_BG)
        body.pack(fill="both", expand=True)

        self.phone_label = tk.Label(body, text="Phone: -", font=FONT_NORMAL,
                                     bg=COLOR_BG, fg=COLOR_TEXT_MUTED)
        self.phone_label.pack(pady=(15, 10))

        stats_frame = tk.Frame(body, bg=COLOR_BG)
        stats_frame.pack(fill="x", padx=20)

        self.total_box, self.total_value = self._make_stat(stats_frame, "Reports")
        self.approved_box, self.approved_value = self._make_stat(stats_frame, "Approved")
        self.score_box, self.score_value = self._make_stat(stats_frame, "Score")

        tk.Button(body, text="Edit Profile", font=FONT_NORMAL, bg=COLOR_LIGHT_BLUE,
                  fg=COLOR_DARK_BLUE, relief="flat", bd=0, cursor="hand2",
                  command=self.edit_profile).pack(fill="x", padx=30, pady=(20, 5), ipady=10)

        tk.Button(body, text="Change Password", font=FONT_NORMAL, bg=COLOR_LIGHT_BLUE,
                  fg=COLOR_DARK_BLUE, relief="flat", bd=0, cursor="hand2",
                  command=self.change_password).pack(fill="x", padx=30, pady=5, ipady=10)

        tk.Button(body, text="Logout", font=FONT_BUTTON, bg=COLOR_RED, fg="white",
                  relief="flat", bd=0, cursor="hand2",
                  command=self.handle_logout).pack(fill="x", padx=30, pady=(15, 5), ipady=10)

        make_nav_bar(self, app, active="Profile")

    def _make_stat(self, parent, label_text):
        box = tk.Frame(parent, bg=COLOR_LIGHT_BLUE, highlightbackground=COLOR_BORDER,
                        highlightthickness=1)
        box.pack(side="left", fill="both", expand=True, padx=4)
        value_label = tk.Label(box, text="0", font=("Helvetica", 15, "bold"),
                                bg=COLOR_LIGHT_BLUE, fg=COLOR_DARK_BLUE)
        value_label.pack(pady=(10, 0))
        tk.Label(box, text=label_text, font=FONT_SMALL, bg=COLOR_LIGHT_BLUE,
                 fg=COLOR_TEXT_MUTED).pack(pady=(0, 10))
        return box, value_label

    def _draw_avatar(self, username, avatar_name):
        self.avatar_canvas.delete("all")
        color = self.AVATAR_COLORS.get(avatar_name, COLOR_DARK_BLUE)
        self.avatar_canvas.create_oval(2, 2, 68, 68, fill=color, outline="white", width=2)
        initial = username[0].upper() if username else "?"
        self.avatar_canvas.create_text(35, 35, text=initial, font=("Helvetica", 26, "bold"),
                                        fill="white")

    def on_show(self):
        app = self.app
        user = app.get_current_user()
        if not user:
            return

        email = user["email"]
        avatar_name = user.get("avatar", "blue")
        self._draw_avatar(user["username"], avatar_name)

        self.username_label.config(text=user["username"])
        self.email_label.config(text=user["email"])
        self.phone_label.config(text=f"Phone: {user.get('phone', '-')}")

        total = app.data_manager.count_user_reports(email)
        approved = app.data_manager.count_approved_reports(email)
        score = app.data_manager.get_community_score(email)

        self.total_value.config(text=str(total))
        self.approved_value.config(text=str(approved))
        self.score_value.config(text=str(score))

    def open_avatar_picker(self):
        AvatarPickerDialog(self.app, on_saved=self.on_show)

    def edit_profile(self):
        EditProfileDialog(self.app)

    def change_password(self):
        ChangePasswordDialog(self.app)

    def handle_logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.app.logout_user()


class AvatarPickerDialog(tk.Toplevel):
    """Lets the user pick one of the preset avatar colors/styles."""

    def __init__(self, app, on_saved=None):
        super().__init__(app)
        self.app = app
        self.on_saved = on_saved
        self.title("Choose Avatar")
        self.geometry("300x220")
        self.configure(bg=COLOR_BG)
        self.resizable(False, False)
        self.grab_set()

        tk.Label(self, text="Pick a preset avatar style", font=FONT_LABEL,
                 bg=COLOR_BG).pack(pady=(15, 10))

        grid = tk.Frame(self, bg=COLOR_BG)
        grid.pack()

        presets = app.data_manager.get_avatar_presets()
        for i, name in enumerate(presets):
            color = ProfileScreen.AVATAR_COLORS.get(name, COLOR_DARK_BLUE)
            canvas = tk.Canvas(grid, width=50, height=50, bg=COLOR_BG, highlightthickness=0,
                                cursor="hand2")
            canvas.create_oval(4, 4, 46, 46, fill=color, outline="")
            canvas.grid(row=i // 3, column=i % 3, padx=10, pady=10)
            canvas.bind("<Button-1>", lambda e, n=name: self.save(n))

    def save(self, avatar_name):
        email = self.app.current_user_email
        success, message = self.app.data_manager.set_avatar(email, avatar_name)
        if not success:
            messagebox.showerror("Error", message)
            return
        self.destroy()
        if self.on_saved:
            self.on_saved()


class EditProfileDialog(tk.Toplevel):
    def __init__(self, app):
        super().__init__(app)
        self.app = app
        self.title("Edit Profile")
        self.geometry("320x260")
        self.configure(bg=COLOR_BG)
        self.resizable(False, False)
        self.grab_set()

        user = app.get_current_user()

        tk.Label(self, text="Full Name", font=FONT_LABEL, bg=COLOR_BG).pack(anchor="w", padx=20, pady=(15, 2))
        self.username_entry = tk.Entry(self, font=FONT_NORMAL)
        self.username_entry.pack(fill="x", padx=20, ipady=6)
        self.username_entry.insert(0, user["username"])

        tk.Label(self, text="Phone Number", font=FONT_LABEL, bg=COLOR_BG).pack(anchor="w", padx=20, pady=(10, 2))
        self.phone_entry = tk.Entry(self, font=FONT_NORMAL)
        self.phone_entry.pack(fill="x", padx=20, ipady=6)
        self.phone_entry.insert(0, user.get("phone", ""))

        tk.Button(self, text="Save Changes", font=FONT_BUTTON, bg=COLOR_DARK_BLUE, fg="white",
                  relief="flat", bd=0, cursor="hand2", command=self.save).pack(
            fill="x", padx=20, pady=20, ipady=8)

    def save(self):
        username = self.username_entry.get().strip()
        phone = self.phone_entry.get().strip()

        if not username:
            messagebox.showerror("Invalid Input", "Name cannot be empty.")
            return
        if not (phone.isdigit() and 8 <= len(phone) <= 12):
            messagebox.showerror("Invalid Input", "Phone number must be 8-12 digits.")
            return

        email = self.app.current_user_email
        success, message = self.app.data_manager.update_user(
            email, {"username": username, "phone": phone}
        )
        if not success:
            messagebox.showerror("Error", message)
            return

        messagebox.showinfo("Success", message)
        self.destroy()
        self.app.show_screen("ProfileScreen")


class ChangePasswordDialog(tk.Toplevel):
    def __init__(self, app):
        super().__init__(app)
        self.app = app
        self.title("Change Password")
        self.geometry("320x280")
        self.configure(bg=COLOR_BG)
        self.resizable(False, False)
        self.grab_set()

        tk.Label(self, text="Current Password", font=FONT_LABEL, bg=COLOR_BG).pack(
            anchor="w", padx=20, pady=(15, 2))
        self.old_entry = tk.Entry(self, font=FONT_NORMAL, show="*")
        self.old_entry.pack(fill="x", padx=20, ipady=6)

        tk.Label(self, text="New Password (min 6 chars)", font=FONT_LABEL, bg=COLOR_BG).pack(
            anchor="w", padx=20, pady=(10, 2))
        self.new_entry = tk.Entry(self, font=FONT_NORMAL, show="*")
        self.new_entry.pack(fill="x", padx=20, ipady=6)

        tk.Label(self, text="Confirm New Password", font=FONT_LABEL, bg=COLOR_BG).pack(
            anchor="w", padx=20, pady=(10, 2))
        self.confirm_entry = tk.Entry(self, font=FONT_NORMAL, show="*")
        self.confirm_entry.pack(fill="x", padx=20, ipady=6)

        tk.Button(self, text="Update Password", font=FONT_BUTTON, bg=COLOR_DARK_BLUE, fg="white",
                  relief="flat", bd=0, cursor="hand2", command=self.save).pack(
            fill="x", padx=20, pady=20, ipady=8)

    def save(self):
        old_pw = self.old_entry.get().strip()
        new_pw = self.new_entry.get().strip()
        confirm_pw = self.confirm_entry.get().strip()

        if new_pw != confirm_pw:
            messagebox.showerror("Invalid Input", "New passwords do not match.")
            return

        email = self.app.current_user_email
        success, message = self.app.data_manager.change_password(email, old_pw, new_pw)

        if not success:
            messagebox.showerror("Error", message)
            return

        messagebox.showinfo("Success", message)
        self.destroy()


# ==========================================================================
# 10. ADMIN DASHBOARD SCREEN
# ==========================================================================

class AdminDashboardScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLOR_BG)
        self.app = app

        header = tk.Frame(self, bg=COLOR_DARK_BLUE, height=70)
        header.pack(side="top", fill="x")
        tk.Label(header, text="Admin Dashboard", font=FONT_BUTTON, fg="white",
                 bg=COLOR_DARK_BLUE).pack(side="left", padx=15, pady=20)
        tk.Button(header, text="Logout", font=FONT_SMALL, fg="white", bg=COLOR_DARK_BLUE,
                  bd=0, activebackground=COLOR_DARK_BLUE, cursor="hand2",
                  command=self.handle_logout).pack(side="right", padx=15)

        # Tabs
        tabs_frame = tk.Frame(self, bg=COLOR_BG)
        tabs_frame.pack(fill="x")

        self.tab_buttons = {}
        for tab in ("Overview", "Users", "Reports", "System Log"):
            btn = tk.Button(
                tabs_frame, text=tab, font=FONT_SMALL, bg=COLOR_LIGHT_BLUE, fg=COLOR_DARK_BLUE,
                relief="flat", bd=0, cursor="hand2", command=lambda t=tab: self.show_tab(t)
            )
            btn.pack(side="left", fill="both", expand=True, padx=2, pady=5, ipady=6)
            self.tab_buttons[tab] = btn

        # Scrollable content area
        content_container = tk.Frame(self, bg=COLOR_BG)
        content_container.pack(fill="both", expand=True, padx=10)

        self.canvas = tk.Canvas(content_container, bg=COLOR_BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(content_container, orient="vertical", command=self.canvas.yview)
        self.content_frame = tk.Frame(self.canvas, bg=COLOR_BG)

        self.content_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.create_window((0, 0), window=self.content_frame, anchor="nw", width=400)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.current_tab = "Overview"

    def on_show(self):
        self.show_tab("Overview")

    def show_tab(self, tab):
        self.current_tab = tab
        for t, btn in self.tab_buttons.items():
            if t == tab:
                btn.config(bg=COLOR_DARK_BLUE, fg="white")
            else:
                btn.config(bg=COLOR_LIGHT_BLUE, fg=COLOR_DARK_BLUE)

        for widget in self.content_frame.winfo_children():
            widget.destroy()

        if tab == "Overview":
            self._build_overview()
        elif tab == "Users":
            self._build_users()
        elif tab == "Reports":
            self._build_reports()
        elif tab == "System Log":
            self._build_system_log()

    # ---- Overview tab ----
    def _build_overview(self):
        dm = self.app.data_manager

        stats_frame = tk.Frame(self.content_frame, bg=COLOR_BG)
        stats_frame.pack(fill="x", pady=10)

        total_users = dm.count_users()
        total_reports = len(dm.get_all_reports())
        unsafe_count = dm.count_all_status("unsafe")

        for label, value, color in (
            ("Total Users", total_users, COLOR_DARK_BLUE),
            ("Total Reports", total_reports, COLOR_BLUE),
            ("Unsafe Reports", unsafe_count, COLOR_RED),
        ):
            box = tk.Frame(stats_frame, bg=COLOR_LIGHT_BLUE, highlightbackground=COLOR_BORDER,
                            highlightthickness=1)
            box.pack(side="left", fill="both", expand=True, padx=4)
            tk.Label(box, text=str(value), font=("Helvetica", 16, "bold"), bg=COLOR_LIGHT_BLUE,
                     fg=color).pack(pady=(10, 0))
            tk.Label(box, text=label, font=FONT_SMALL, bg=COLOR_LIGHT_BLUE,
                     fg=COLOR_TEXT_MUTED, wraplength=100, justify="center").pack(pady=(0, 10))

        tk.Label(self.content_frame, text="Recent Reports", font=FONT_LABEL, bg=COLOR_BG,
                 fg=COLOR_TEXT_DARK, anchor="w").pack(fill="x", pady=(15, 5))

        recent = dm.get_recent_reports(limit=5)
        if not recent:
            tk.Label(self.content_frame, text="No reports yet.", font=FONT_NORMAL,
                     bg=COLOR_BG, fg=COLOR_TEXT_MUTED).pack(pady=20)
        for r in recent:
            self._build_admin_report_row(self.content_frame, r, show_actions=False)

    # ---- Users tab ----
    def _build_users(self):
        dm = self.app.data_manager
        users = dm.get_all_users()

        tk.Label(self.content_frame, text=f"All Users ({len(users)})", font=FONT_LABEL,
                 bg=COLOR_BG, fg=COLOR_TEXT_DARK, anchor="w").pack(fill="x", pady=10)

        for user in users:
            row = tk.Frame(self.content_frame, bg=COLOR_LIGHT_BLUE, highlightbackground=COLOR_BORDER,
                            highlightthickness=1)
            row.pack(fill="x", pady=4)

            info_frame = tk.Frame(row, bg=COLOR_LIGHT_BLUE)
            info_frame.pack(side="left", fill="both", expand=True, padx=10, pady=8)

            name_text = user["username"]
            if user.get("is_admin"):
                name_text += "  (Admin)"
            tk.Label(info_frame, text=name_text, font=FONT_LABEL, bg=COLOR_LIGHT_BLUE,
                     fg=COLOR_TEXT_DARK, anchor="w").pack(fill="x")
            tk.Label(info_frame, text=user["email"], font=FONT_SMALL, bg=COLOR_LIGHT_BLUE,
                     fg=COLOR_TEXT_MUTED, anchor="w").pack(fill="x")

            if not user.get("is_admin"):
                del_btn = tk.Button(
                    row, text="Delete", font=FONT_SMALL, bg=COLOR_RED, fg="white",
                    relief="flat", bd=0, cursor="hand2",
                    command=lambda e=user["email"]: self.delete_user(e)
                )
                del_btn.pack(side="right", padx=10)

    def delete_user(self, email):
        if not messagebox.askyesno("Delete User", "Are you sure you want to delete this user?"):
            return
        success, message = self.app.data_manager.delete_user(email)
        if success:
            messagebox.showinfo("Success", message)
        else:
            messagebox.showerror("Error", message)
        self.show_tab("Users")

    # ---- Reports tab ----
    def _build_reports(self):
        dm = self.app.data_manager
        reports = dm.get_all_reports()

        tk.Label(self.content_frame, text=f"All Reports ({len(reports)})", font=FONT_LABEL,
                 bg=COLOR_BG, fg=COLOR_TEXT_DARK, anchor="w").pack(fill="x", pady=10)

        if not reports:
            tk.Label(self.content_frame, text="No reports yet.", font=FONT_NORMAL,
                     bg=COLOR_BG, fg=COLOR_TEXT_MUTED).pack(pady=20)

        for r in reports:
            self._build_admin_report_row(self.content_frame, r, show_actions=True)

    def _build_admin_report_row(self, parent, report, show_actions):
        row = tk.Frame(parent, bg=COLOR_LIGHT_BLUE, highlightbackground=COLOR_BORDER,
                        highlightthickness=1)
        row.pack(fill="x", pady=4)

        top = tk.Frame(row, bg=COLOR_LIGHT_BLUE)
        top.pack(fill="x", padx=10, pady=(8, 0))

        color = status_badge_color(report["status"])
        tk.Label(top, text=report["status"].upper(), font=FONT_LABEL, fg=color,
                 bg=COLOR_LIGHT_BLUE).pack(side="left")

        verified_text = "Verified" if report.get("verified") else "Pending"
        verified_color = COLOR_GREEN if report.get("verified") else COLOR_TEXT_MUTED
        tk.Label(top, text=verified_text, font=FONT_SMALL, fg=verified_color,
                 bg=COLOR_LIGHT_BLUE).pack(side="right")

        tk.Label(row, text=f"{report['location']} — by {report['username']}", font=FONT_NORMAL,
                 fg=COLOR_TEXT_DARK, bg=COLOR_LIGHT_BLUE, anchor="w").pack(fill="x", padx=10, pady=(2, 0))

        tk.Label(row, text=report["description"], font=FONT_SMALL, fg=COLOR_TEXT_MUTED,
                 bg=COLOR_LIGHT_BLUE, anchor="w", wraplength=340, justify="left").pack(
            fill="x", padx=10, pady=(2, 0))

        tk.Label(row, text=report["timestamp"], font=FONT_SMALL, fg=COLOR_TEXT_MUTED,
                 bg=COLOR_LIGHT_BLUE, anchor="w").pack(fill="x", padx=10, pady=(2, 6))

        if show_actions:
            action_frame = tk.Frame(row, bg=COLOR_LIGHT_BLUE)
            action_frame.pack(fill="x", padx=10, pady=(0, 8))

            if report.get("verified"):
                btn = tk.Button(
                    action_frame, text="Unverify", font=FONT_SMALL, bg=COLOR_ORANGE, fg="white",
                    relief="flat", bd=0, cursor="hand2",
                    command=lambda rid=report["id"]: self.toggle_verify(rid, False)
                )
            else:
                btn = tk.Button(
                    action_frame, text="Verify Report", font=FONT_SMALL, bg=COLOR_GREEN, fg="white",
                    relief="flat", bd=0, cursor="hand2",
                    command=lambda rid=report["id"]: self.toggle_verify(rid, True)
                )
            btn.pack(side="left")

    def toggle_verify(self, report_id, verify):
        dm = self.app.data_manager
        if verify:
            success, message = dm.verify_report(report_id)
        else:
            success, message = dm.unverify_report(report_id)

        if not success:
            messagebox.showerror("Error", message)
        self.show_tab(self.current_tab)

    # ---- System Log tab ----
    def _build_system_log(self):
        dm = self.app.data_manager
        logs = dm.get_system_log()

        tk.Label(self.content_frame, text="System Log", font=FONT_LABEL, bg=COLOR_BG,
                 fg=COLOR_TEXT_DARK, anchor="w").pack(fill="x", pady=10)

        if not logs:
            tk.Label(self.content_frame, text="No activity recorded yet.", font=FONT_NORMAL,
                     bg=COLOR_BG, fg=COLOR_TEXT_MUTED).pack(pady=20)
            return

        for entry in logs:
            tk.Label(self.content_frame, text=entry, font=FONT_SMALL, bg=COLOR_LIGHT_BLUE,
                     fg=COLOR_TEXT_DARK, anchor="w", wraplength=380, justify="left").pack(
                fill="x", pady=2, padx=2, ipady=6)

    def handle_logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.app.logout_user()


# ==========================================================================
# Entry point
# ==========================================================================

if __name__ == "__main__":
    app = WaterQualityApp()
    app.mainloop()