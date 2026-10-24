"""
gui.py - Graphical User Interface for AI Requirement Validator
--------------------------------------------------------------
Features a warm, professional Brown and Half-White color palette:
- Deep espresso brown headers and buttons
- Warm half-white / cream background and cards
- Quick Samples dropdown
- Real-time Rule Analysis (10 rules evaluated)
- Structured problem diagnostics with severity indicators
- Recommended improved requirement templates
- Audit persistence to CSV
"""

import os
import csv
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import validator

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
TEST_REQUIREMENTS_PATH = os.path.join(DATA_DIR, "test_requirements.csv")


class RequirementValidatorGUI:
    """
    Tkinter GUI Application with Brown and Half-White theme.
    Provides requirement input, live rule evaluation, structured diagnostics, and CSV export.
    """

    def __init__(self, root):
        self.root = root
        self.root.title("AI Requirement Validator for Software Development")
        self.root.geometry("960x860")
        self.root.minsize(880, 720)
        # Half-White / Warm Cream background
        self.root.configure(bg="#FAF7F2")

        self.current_requirement = ""
        self.latest_result = None

        self._configure_styles()
        self._build_ui()
        self._load_sample_data()

    def _configure_styles(self):
        """Configure ttk styles with Brown and Half-White theme."""
        style = ttk.Style()
        style.theme_use("clam")

        # Global backgrounds
        style.configure("TLabel", background="#FAF7F2", font=("Segoe UI", 10), foreground="#3E2723")
        style.configure("TFrame", background="#FAF7F2")

        # Primary Action Button - Warm Chocolate Brown
        style.configure(
            "Primary.TButton",
            font=("Segoe UI", 10, "bold"),
            background="#5D4037",
            foreground="#FFFFFF",
            padding=(15, 7)
        )
        style.map("Primary.TButton",
                  background=[("active", "#3E2723"), ("disabled", "#BCAAA4")])

        # Secondary Action Button - Half-White / Warm Almond
        style.configure(
            "Secondary.TButton",
            font=("Segoe UI", 10),
            background="#EFEBE9",
            foreground="#3E2723",
            padding=(13, 7)
        )
        style.map("Secondary.TButton",
                  background=[("active", "#D7CCC8")])

        # Save Button - Earthy Warm Forest / Bronze
        style.configure(
            "Success.TButton",
            font=("Segoe UI", 10, "bold"),
            background="#4E6A34",
            foreground="#FFFFFF",
            padding=(14, 7)
        )
        style.map("Success.TButton",
                  background=[("active", "#334A21"), ("disabled", "#C5D6B6")])

    def _build_ui(self):
        """Constructs layout: header banner, input box, rule analysis, problems, and suggestions."""
        # Top Header Banner - Deep Espresso Brown with Half-White Text
        header_frame = tk.Frame(self.root, bg="#3E2723", padx=22, pady=13)
        header_frame.pack(fill="x")

        title_label = tk.Label(
            header_frame,
            text="AI Requirement Validator for Software Development",
            font=("Segoe UI", 15, "bold"),
            fg="#FFF8F0",
            bg="#3E2723"
        )
        title_label.pack(anchor="w")

        subtitle_label = tk.Label(
            header_frame,
            text="Rule-Based Quality Verification Engine (PASS / NEEDS IMPROVEMENT / INVALID)",
            font=("Segoe UI", 9),
            fg="#D7CCC8",
            bg="#3E2723"
        )
        subtitle_label.pack(anchor="w")

        # Main Scrollable / Fillable Container - Half-White Background
        main_container = tk.Frame(self.root, bg="#FAF7F2", padx=20, pady=12)
        main_container.pack(fill="both", expand=True)

        # ---------------- INPUT SECTION ----------------
        input_header = tk.Frame(main_container, bg="#FAF7F2")
        input_header.pack(fill="x", pady=(0, 4))

        input_title = tk.Label(
            input_header,
            text="Requirement Input:",
            font=("Segoe UI", 11, "bold"),
            bg="#FAF7F2",
            fg="#3E2723"
        )
        input_title.pack(side="left")

        # Quick Samples Dropdown
        sample_label = tk.Label(
            input_header,
            text="Quick Samples:",
            font=("Segoe UI", 9, "bold"),
            bg="#FAF7F2",
            fg="#6D4C41"
        )
        sample_label.pack(side="left", padx=(25, 6))

        self.sample_combo = ttk.Combobox(input_header, state="readonly", width=54)
        self.sample_combo.pack(side="left")
        self.sample_combo.bind("<<ComboboxSelected>>", self._on_sample_selected)

        # Text input box - Half-White with warm border
        self.input_text = scrolledtext.ScrolledText(
            main_container,
            height=3,
            wrap=tk.WORD,
            font=("Segoe UI", 10),
            bg="#FFFFFF",
            fg="#2E1C14",
            relief="solid",
            borderwidth=1
        )
        self.input_text.pack(fill="x", pady=(0, 8))
        self.input_text.focus_set()
        self.input_text.bind("<Control-Return>", lambda event: self.on_validate())

        # Buttons Row
        button_row = tk.Frame(main_container, bg="#FAF7F2")
        button_row.pack(fill="x", pady=(0, 10))

        self.btn_validate = ttk.Button(
            button_row,
            text="✔ VALIDATE REQUIREMENT",
            style="Primary.TButton",
            command=self.on_validate
        )
        self.btn_validate.pack(side="left", padx=(0, 10))

        self.btn_clear = ttk.Button(
            button_row,
            text="✖ Clear",
            style="Secondary.TButton",
            command=self.on_clear
        )
        self.btn_clear.pack(side="left", padx=(0, 12))

        hint_label = tk.Label(
            button_row,
            text="(Ctrl + Enter to Validate immediately)",
            font=("Segoe UI", 9),
            fg="#8D6E63",
            bg="#FAF7F2"
        )
        hint_label.pack(side="left")

        # ---------------- RESULTS CONTAINER (Half-White Card) ----------------
        results_card = tk.Frame(main_container, bg="#FFFFFF", relief="solid", borderwidth=1, padx=16, pady=12)
        results_card.pack(fill="both", expand=True)

        # Top Summary Bar: Status Badge and Quality Score
        summary_bar = tk.Frame(results_card, bg="#FFFFFF")
        summary_bar.pack(fill="x", pady=(0, 8))

        status_heading = tk.Label(
            summary_bar,
            text="Validation Status:",
            font=("Segoe UI", 11, "bold"),
            bg="#FFFFFF",
            fg="#3E2723"
        )
        status_heading.pack(side="left")

        self.status_badge = tk.Label(
            summary_bar,
            text="NOT EVALUATED",
            font=("Segoe UI", 11, "bold"),
            bg="#EFEBE9",
            fg="#5D4037",
            padx=14,
            pady=4,
            relief="flat"
        )
        self.status_badge.pack(side="left", padx=(10, 30))

        score_heading = tk.Label(
            summary_bar,
            text="Quality Score:",
            font=("Segoe UI", 11, "bold"),
            bg="#FFFFFF",
            fg="#3E2723"
        )
        score_heading.pack(side="left")

        self.score_label = tk.Label(
            summary_bar,
            text="-- / --",
            font=("Segoe UI", 11, "bold"),
            bg="#FFFFFF",
            fg="#6D4C41"
        )
        self.score_label.pack(side="left", padx=(8, 0))

        # Separator line
        sep = tk.Frame(results_card, height=1, bg="#D7CCC8")
        sep.pack(fill="x", pady=(0, 8))

        # Middle Content Layout: Left = Rule Analysis, Right = Problems & Suggestions
        content_frame = tk.Frame(results_card, bg="#FFFFFF")
        content_frame.pack(fill="both", expand=True, pady=(0, 8))

        # --- LEFT COLUMN: RULE ANALYSIS SECTION ---
        rule_analysis_col = tk.Frame(content_frame, bg="#FFFFFF", width=255)
        rule_analysis_col.pack(side="left", fill="y", padx=(0, 10))

        lbl_rule_analysis = tk.Label(
            rule_analysis_col,
            text="Rule Analysis:",
            font=("Segoe UI", 10, "bold"),
            bg="#FFFFFF",
            fg="#4A2E18"
        )
        lbl_rule_analysis.pack(anchor="w", pady=(0, 4))

        self.rule_analysis_text = tk.Text(
            rule_analysis_col,
            width=29,
            height=13,
            font=("Consolas", 9),
            bg="#FDFBF7",
            fg="#2E1C14",
            relief="solid",
            borderwidth=1,
            padx=6,
            pady=6
        )
        self.rule_analysis_text.pack(fill="both", expand=True)

        # --- RIGHT COLUMN: PROBLEMS & SUGGESTIONS ---
        details_col = tk.Frame(content_frame, bg="#FFFFFF")
        details_col.pack(side="right", fill="both", expand=True)

        # Problems Detected
        lbl_prob = tk.Label(
            details_col,
            text="Problems Detected:",
            font=("Segoe UI", 10, "bold"),
            bg="#FFFFFF",
            fg="#A62626"
        )
        lbl_prob.pack(anchor="w", pady=(0, 2))

        self.problems_box = scrolledtext.ScrolledText(
            details_col,
            height=6,
            wrap=tk.WORD,
            font=("Segoe UI", 9),
            bg="#FFF9F8",
            fg="#2E1C14",
            relief="solid",
            borderwidth=1
        )
        self.problems_box.pack(fill="both", expand=True, pady=(0, 6))

        # Suggestions for Improvement
        lbl_sugg = tk.Label(
            details_col,
            text="Suggestions for Improvement:",
            font=("Segoe UI", 10, "bold"),
            bg="#FFFFFF",
            fg="#33691E"
        )
        lbl_sugg.pack(anchor="w", pady=(0, 2))

        self.suggestions_box = scrolledtext.ScrolledText(
            details_col,
            height=4,
            wrap=tk.WORD,
            font=("Segoe UI", 9),
            bg="#F7FAF7",
            fg="#2E1C14",
            relief="solid",
            borderwidth=1
        )
        self.suggestions_box.pack(fill="both", expand=True)

        # Recommended Improved Requirement Box
        improved_label = tk.Label(
            results_card,
            text="Recommended Improved Requirement:",
            font=("Segoe UI", 10, "bold"),
            bg="#FFFFFF",
            fg="#4A2E18"
        )
        improved_label.pack(anchor="w", pady=(4, 2))

        self.improved_entry = tk.Text(
            results_card,
            height=2,
            wrap=tk.WORD,
            font=("Segoe UI", 9, "italic"),
            bg="#FDF8EE",
            fg="#3E2723",
            relief="solid",
            borderwidth=1,
            padx=8,
            pady=4
        )
        self.improved_entry.pack(fill="x", pady=(0, 8))

        # Bottom Controls: Save Button and Status
        bottom_bar = tk.Frame(results_card, bg="#FFFFFF")
        bottom_bar.pack(fill="x")

        self.btn_save = ttk.Button(
            bottom_bar,
            text="💾 SAVE RESULT TO CSV",
            style="Success.TButton",
            command=self.on_save_result,
            state="disabled"
        )
        self.btn_save.pack(side="left")

        self.save_status_label = tk.Label(
            bottom_bar,
            text="Validate a requirement to enable saving.",
            font=("Segoe UI", 9, "italic"),
            fg="#8D6E63",
            bg="#FFFFFF"
        )
        self.save_status_label.pack(side="left", padx=(14, 0))

        # Window Bottom Status Bar - Warm Half-White / Linen
        self.status_bar = tk.Label(
            self.root,
            text="Ready. Enter a requirement or select a sample, then click Validate.",
            font=("Segoe UI", 9),
            bg="#EFEBE9",
            fg="#4E342E",
            anchor="w",
            padx=10,
            pady=4
        )
        self.status_bar.pack(side="bottom", fill="x")

    def _load_sample_data(self):
        """Loads categorized sample requirements into the combobox."""
        self.samples = []
        if os.path.exists(TEST_REQUIREMENTS_PATH):
            try:
                with open(TEST_REQUIREMENTS_PATH, "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        req = row.get("Requirement", "").strip()
                        cat = row.get("Category", "").strip()
                        if req:
                            label = f"{cat}: \"{req}\"" if cat else req
                            self.samples.append((label, req))
            except Exception:
                pass

        if not self.samples:
            default_cases = [
                ("Good Requirement", "The system shall authenticate a valid user within 2 seconds."),
                ("Incomplete - Dangling Preposition", "The system shall provide users with"),
                ("Incomplete - Dangling Conjunction", "The user can log in when"),
                ("Incomplete - Dangling Modal", "The system should"),
                ("Incomplete - Trailing Ellipsis", "The system should allow users to..."),
                ("Vague Requirement", "The system should respond quickly."),
                ("Ambiguous Requirement", "The system should process requests as soon as possible."),
                ("Escape Clause", "The system shall backup records if possible."),
                ("Compound Requirement", "The system shall process orders as well as the system shall notify managers."),
                ("Performance Requirement", "The system shall process 100 requests within 5 seconds."),
                ("System Actor", "The system shall generate a monthly report."),
                ("Short / Unusable", "Login.")
            ]
            self.samples = [(f"{cat}: \"{req}\"", req) for cat, req in default_cases]

        self.sample_combo["values"] = [item[0] for item in self.samples]

    def _on_sample_selected(self, event=None):
        """Places selected sample into the input area and validates immediately."""
        idx = self.sample_combo.current()
        if idx >= 0 and idx < len(self.samples):
            req_text = self.samples[idx][1]
            self.input_text.delete("1.0", tk.END)
            self.input_text.insert(tk.END, req_text)
            self.on_validate()

    def on_validate(self):
        """Runs the validation engine and updates all UI displays."""
        raw_text = self.input_text.get("1.0", tk.END).strip()
        self.current_requirement = raw_text

        result = validator.validate_requirement(raw_text)
        self.latest_result = result

        # 1. Update Validation Status Badge
        status = result["status"]
        if status == "PASS":
            self.status_badge.config(text="PASS", bg="#2E7D32", fg="#FFFFFF")
        elif status == "NEEDS IMPROVEMENT":
            self.status_badge.config(text="NEEDS IMPROVEMENT", bg="#D84315", fg="#FFFFFF")
        else:  # INVALID
            self.status_badge.config(text="INVALID", bg="#C62828", fg="#FFFFFF")

        # 2. Update Quality Score
        score = result["score"]
        total = result["total_rules"]
        self.score_label.config(text=f"{score}/{total} rules passed")

        # 3. Update Rule Analysis Section
        self.rule_analysis_text.delete("1.0", tk.END)
        for r in result.get("rule_analysis", []):
            icon = r.get("icon", "✓")
            name = r.get("name", "")
            st = r.get("status", "")
            line = f"{icon} {name:<18} {st:>4}\n"
            self.rule_analysis_text.insert(tk.END, line)

        # 4. Populate Problems Detected with Structured Explanations
        self.problems_box.delete("1.0", tk.END)
        problems = result["problems"]
        if problems:
            for i, p in enumerate(problems, start=1):
                sev = p.get("severity", "MEDIUM")
                p_type = p.get("problem_type") or p.get("rule")
                detected = p.get("detected") or "Identified in input"
                why = p.get("why") or p.get("message")
                sugg = p.get("suggestion") or "Refine the requirement statement."

                block = (
                    f"{i}. [{sev}] Problem: {p_type}\n"
                    f"   Detected:   {detected}\n"
                    f"   Why:        {why}\n"
                    f"   Suggestion: {sugg}\n\n"
                )
                self.problems_box.insert(tk.END, block)
        else:
            self.problems_box.insert(tk.END, "✔ No quality problems detected.\nAll checked rules satisfied.\n")

        # 5. Populate Suggestions List
        self.suggestions_box.delete("1.0", tk.END)
        suggestions = result["suggestions"]
        if suggestions:
            for i, s in enumerate(suggestions, start=1):
                self.suggestions_box.insert(tk.END, f"{i}. {s}\n")
        else:
            self.suggestions_box.insert(tk.END, "✔ Requirement adheres to standard quality rules.\n")

        # 6. Populate Improved Requirement
        self.improved_entry.delete("1.0", tk.END)
        self.improved_entry.insert(tk.END, result["improved_requirement"])

        # 7. Enable Save Result Button
        self.btn_save.config(state="normal")
        self.save_status_label.config(
            text="Ready to save. Click button to record in CSV.",
            fg="#4E6A34"
        )
        self.status_bar.config(
            text=f"Validation completed: Status: {status} | Score: {score}/{total} rules passed."
        )

    def on_clear(self):
        """Clears all inputs and resets result panels."""
        self.input_text.delete("1.0", tk.END)
        self.sample_combo.set("")
        self.current_requirement = ""
        self.latest_result = None

        self.status_badge.config(text="NOT EVALUATED", bg="#EFEBE9", fg="#5D4037")
        self.score_label.config(text="-- / --")

        self.rule_analysis_text.delete("1.0", tk.END)
        self.problems_box.delete("1.0", tk.END)
        self.suggestions_box.delete("1.0", tk.END)
        self.improved_entry.delete("1.0", tk.END)

        self.btn_save.config(state="disabled")
        self.save_status_label.config(
            text="Validate a requirement to enable saving.",
            fg="#8D6E63"
        )
        self.status_bar.config(text="Cleared. Ready for new requirement input.")
        self.input_text.focus_set()

    def on_save_result(self):
        """Saves current validation record to results/validation_results.csv."""
        if not self.latest_result:
            messagebox.showwarning("Warning", "Please validate a requirement first before saving.")
            return

        try:
            saved_path = validator.save_validation_result(
                self.current_requirement,
                self.latest_result
            )
            filename = os.path.basename(saved_path)
            self.save_status_label.config(
                text=f"Saved successfully to results/{filename}!",
                fg="#4E6A34"
            )
            self.status_bar.config(text=f"Record saved to {saved_path}")
            messagebox.showinfo(
                "Result Saved",
                f"Validation result was successfully saved to:\n\n{saved_path}"
            )
        except Exception as ex:
            messagebox.showerror("Save Error", f"Failed to save result:\n{str(ex)}")


def launch_app():
    """Main function to launch GUI."""
    root = tk.Tk()
    app = RequirementValidatorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    launch_app()
