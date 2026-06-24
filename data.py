"""
data.py - Backend logic and storage for the Water Quality Monitoring System.

All data persistence (users.json, reports.json) and all business logic
lives here. main.py should ONLY call methods on DataManager - it should
never read/write the JSON files directly or duplicate any logic.
"""

import json
import os
from datetime import datetime


USERS_FILE = "users.json"
REPORTS_FILE = "reports.json"

VALID_STATUSES = ("safe", "unsafe", "moderate")

ADMIN_EMAIL = "admin@gmail.com"

# Preset avatar style names a user can choose from in their profile.
AVATAR_PRESETS = ("blue", "green", "orange", "purple", "teal", "red")


class DataManager:
    """Handles all data storage and business logic for the app."""

    def __init__(self, users_file=USERS_FILE, reports_file=REPORTS_FILE):
        self.users_file = users_file
        self.reports_file = reports_file
        self.users = self._load_json(self.users_file)
        self.reports = self._load_json(self.reports_file)

        # Seed a default admin account if no users exist yet.
        if not self.users:
            self.users.append({
                "username": "Admin",
                "email": ADMIN_EMAIL,
                "password": "admin123",
                "phone": "00000000",
                "is_admin": True,
                "avatar": "blue",
            })
            self._save_json(self.users_file, self.users)

    # ------------------------------------------------------------------
    # Internal file helpers
    # ------------------------------------------------------------------

    def _load_json(self, filepath):
        """Load a JSON file into a list. Returns [] if missing/corrupt."""
        if not os.path.exists(filepath):
            return []
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
                return []
        except (json.JSONDecodeError, OSError):
            return []

    def _save_json(self, filepath, data):
        """Save a list of dicts to a JSON file."""
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            return True
        except OSError:
            return False

    def _save_users(self):
        return self._save_json(self.users_file, self.users)

    def _save_reports(self):
        return self._save_json(self.reports_file, self.reports)

    # ------------------------------------------------------------------
    # User management
    # ------------------------------------------------------------------

    def email_exists(self, email):
        email = email.strip().lower()
        return any(u["email"].lower() == email for u in self.users)

    def add_user(self, user):
        """
        Add a new user.
        `user` should be a dict with: username, email, password, phone
        Returns (True, "message") on success, (False, "message") on failure.
        """
        if not isinstance(user, dict):
            return False, "Invalid user data."

        username = str(user.get("username", "")).strip()
        email = str(user.get("email", "")).strip().lower()
        password = str(user.get("password", ""))
        phone = str(user.get("phone", "")).strip()

        if not username or not email or not password or not phone:
            return False, "All fields are required."

        if self.email_exists(email):
            return False, "An account with this email already exists."

        new_user = {
            "username": username,
            "email": email,
            "password": password,
            "phone": phone,
            "is_admin": False,
            "avatar": AVATAR_PRESETS[len(username) % len(AVATAR_PRESETS)],
        }
        self.users.append(new_user)
        saved = self._save_users()
        if not saved:
            return False, "Could not save user data."
        return True, "Account created successfully."

    def validate_login(self, email, password):
        """
        Validate login credentials.
        Returns (True, user_dict) on success, (False, "message") on failure.
        """
        email = str(email).strip().lower()
        password = str(password)

        for user in self.users:
            if user["email"].lower() == email:
                if user["password"] == password:
                    return True, user
                return False, "Incorrect password."
        return False, "No account found with this email."

    def is_admin(self, email):
        email = str(email).strip().lower()
        for user in self.users:
            if user["email"].lower() == email:
                return bool(user.get("is_admin", False))
        return False

    def get_user(self, email):
        email = str(email).strip().lower()
        for user in self.users:
            if user["email"].lower() == email:
                return user
        return None

    def update_user(self, email, updates):
        """Update fields on a user record. `updates` is a dict of fields."""
        email = str(email).strip().lower()
        for user in self.users:
            if user["email"].lower() == email:
                user.update(updates)
                self._save_users()
                return True, "Profile updated."
        return False, "User not found."

    def change_password(self, email, old_password, new_password):
        ok, result = self.validate_login(email, old_password)
        if not ok:
            return False, "Current password is incorrect."
        if len(new_password) < 6:
            return False, "New password must be at least 6 characters."
        email = str(email).strip().lower()
        for user in self.users:
            if user["email"].lower() == email:
                user["password"] = new_password
                self._save_users()
                return True, "Password changed successfully."
        return False, "User not found."

    def set_avatar(self, email, avatar_name):
        """Set a user's chosen preset avatar style."""
        avatar_name = str(avatar_name).strip().lower()
        if avatar_name not in AVATAR_PRESETS:
            return False, "Invalid avatar choice."
        return self.update_user(email, {"avatar": avatar_name})

    def get_avatar_presets(self):
        return list(AVATAR_PRESETS)

    def get_all_users(self):
        return list(self.users)

    def count_users(self):
        return len(self.users)

    def delete_user(self, email):
        email = str(email).strip().lower()
        before = len(self.users)
        self.users = [u for u in self.users if u["email"].lower() != email]
        if len(self.users) < before:
            self._save_users()
            return True, "User deleted."
        return False, "User not found."

    # ------------------------------------------------------------------
    # Report management
    # ------------------------------------------------------------------

    def add_report(self, email, username, location, status, description):
        """
        Create and store a new water quality report.
        Returns (True, "message") on success, (False, "message") on failure.
        """
        email = str(email).strip().lower()
        username = str(username).strip()
        location = str(location).strip()
        status = str(status).strip().lower()
        description = str(description).strip()

        if not location:
            return False, "Location is required."
        if not description:
            return False, "Description is required."
        if status not in VALID_STATUSES:
            return False, "Invalid status type."

        report = {
            "id": self._next_report_id(),
            "email": email,
            "username": username,
            "location": location,
            "status": status,
            "description": description,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "verified": False,
        }
        self.reports.append(report)
        saved = self._save_reports()
        if not saved:
            return False, "Could not save report."
        return True, "Report submitted successfully."

    def _next_report_id(self):
        if not self.reports:
            return 1
        return max(r.get("id", 0) for r in self.reports) + 1

    def get_user_reports(self, email):
        email = str(email).strip().lower()
        reports = [r for r in self.reports if r["email"].lower() == email]
        # Most recent first.
        return sorted(reports, key=lambda r: r["id"], reverse=True)

    def count_user_reports(self, email):
        return len(self.get_user_reports(email))

    def count_status(self, email, status_type):
        """Count how many of a user's reports match a given status."""
        status_type = str(status_type).strip().lower()
        return len([
            r for r in self.get_user_reports(email)
            if r["status"] == status_type
        ])

    def get_overall_status(self, email):
        """
        Determine a user's overall water status based on their reports.
        GOOD if 'safe' is the most common, BAD if 'unsafe' is most common,
        MODERATE otherwise (including ties or no reports).
        Returns one of: "GOOD", "BAD", "MODERATE"
        """
        safe = self.count_status(email, "safe")
        unsafe = self.count_status(email, "unsafe")
        moderate = self.count_status(email, "moderate")

        if safe == 0 and unsafe == 0 and moderate == 0:
            return "MODERATE"

        highest = max(safe, unsafe, moderate)

        if safe == highest and safe > unsafe and safe > moderate:
            return "GOOD"
        if unsafe == highest and unsafe > safe and unsafe > moderate:
            return "BAD"
        return "MODERATE"

    def get_all_reports(self):
        return sorted(self.reports, key=lambda r: r["id"], reverse=True)

    def get_recent_reports(self, limit=3):
        return self.get_all_reports()[:limit]

    def count_all_status(self, status_type):
        status_type = str(status_type).strip().lower()
        return len([r for r in self.reports if r["status"] == status_type])

    def verify_report(self, report_id):
        """Mark a report as verified/approved by an admin."""
        for report in self.reports:
            if report.get("id") == report_id:
                report["verified"] = True
                self._save_reports()
                return True, "Report verified."
        return False, "Report not found."

    def unverify_report(self, report_id):
        for report in self.reports:
            if report.get("id") == report_id:
                report["verified"] = False
                self._save_reports()
                return True, "Report unverified."
        return False, "Report not found."

    def count_approved_reports(self, email):
        email = str(email).strip().lower()
        return len([
            r for r in self.get_user_reports(email) if r.get("verified")
        ])

    def get_community_score(self, email):
        """Simple community help score capped at 50: 5 points per approved report."""
        approved = self.count_approved_reports(email)
        return min(approved * 5, 50)

    def search_reports(self, email, keyword):
        """Filter a user's reports by a keyword found in location or status."""
        keyword = str(keyword).strip().lower()
        reports = self.get_user_reports(email)
        if not keyword:
            return reports
        return [
            r for r in reports
            if keyword in r["location"].lower() or keyword in r["status"].lower()
        ]

    def get_last_report(self, email):
        reports = self.get_user_reports(email)
        if reports:
            return reports[0]
        return None

    # ------------------------------------------------------------------
    # Map support
    # ------------------------------------------------------------------

    def get_location_coordinates(self, location):
        """
        Convert a location name into a deterministic (x_ratio, y_ratio) pair,
        each in the 0.0-1.0 range, so the same location always plots at the
        same spot on the map canvas. This avoids needing any external map
        API or library - pure built-in logic only.
        """
        location = str(location).strip().lower()
        if not location:
            return 0.5, 0.5

        # Simple deterministic hash using only built-ins.
        seed = 0
        for char in location:
            seed = (seed * 31 + ord(char)) % 100000

        x_ratio = 0.12 + ((seed % 76) / 100)
        y_ratio = 0.12 + (((seed // 76) % 76) / 100)
        return round(x_ratio, 3), round(y_ratio, 3)

    def get_map_pins(self):
        """
        Build a list of map pin dicts (one per unique location, using the
        most recent report for that location) ready for the Map screen to
        draw. Each pin: location, status, x_ratio, y_ratio, timestamp, id.
        """
        reports = self.get_all_reports()  # newest first
        seen_locations = set()
        pins = []
        for r in reports:
            loc_key = r["location"].strip().lower()
            if loc_key in seen_locations:
                continue
            seen_locations.add(loc_key)
            x_ratio, y_ratio = self.get_location_coordinates(r["location"])
            pins.append({
                "id": r["id"],
                "location": r["location"],
                "status": r["status"],
                "timestamp": r["timestamp"],
                "username": r["username"],
                "description": r["description"],
                "verified": r.get("verified", False),
                "x_ratio": x_ratio,
                "y_ratio": y_ratio,
            })
        return pins

    def get_system_log(self):
        """Combined chronological-ish log of users and report activity."""
        log_entries = []
        for u in self.users:
            log_entries.append(f"User registered: {u['username']} ({u['email']})")
        for r in self.reports:
            verified_tag = "verified" if r.get("verified") else "pending"
            log_entries.append(
                f"[{r['timestamp']}] Report #{r['id']} by {r['username']} "
                f"at {r['location']} - {r['status'].upper()} ({verified_tag})"
            )
        return log_entries