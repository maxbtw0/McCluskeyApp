import customtkinter as ctk
from pathlib import Path
import json
import os
import random
import math

APPDATA_DIR = Path(os.getenv("APPDATA")) / "maxbtw0" / "McCluskeyApp"
APPDATA_DIR.mkdir(parents=True, exist_ok=True)

SETTINGS_FILE = APPDATA_DIR / "settings.json"

# ---------------------- Grund-Setup ----------------------
ctk.set_appearance_mode("dark")      # Start im Dark Mode
ctk.set_default_color_theme("dark-blue")

APP_TITLE = "Verfahren nach Quine und McCluskey"

def onlyOneBitDiff(a, b):
    return (a ^ b) & ((a ^ b) - 1) == 0

def DezToBit(x, n_bits):
    a = bin(x).replace("0b", "").zfill(n_bits)
    return a

def bits_to_expr(bits, n_bits):
    bits = DezToBit(bits, n_bits)
    letters = list(reversed([chr(ord('A') + i) for i in range(len(bits))]))
    return " ".join(letter + '\u0305' if bit == '0' else letter for bit, letter in zip(bits, letters))

def bits_to_expr2(bits):
    abc = list(reversed([chr(ord('A') + i) for i in range(len(bits))]))
    result = []
    for a,b in enumerate(bits):
        if b == '0':
            result.append(abc[a] + '\u0305')
        elif b == '1':
            result.append(abc[a])
        else:
            result.append('')
    return " ".join(result)

def StringBubbleSort(arr):
    for i in range(len(arr)):
        for j in range(len(arr) - i - 1):
            if arr[j].count("1") > arr[j + 1].count("1"):
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr

def NewStringFromBits(i, j, nbits):
    i = DezToBit(i, nbits)
    j = DezToBit(j, nbits)
    for v in range(len(i)):
        if i[v] != j[v]:
            return f"{i[:v] + '-' + i[v+1:]}"

def NewStringFromBits2(i, j):
    for v in range(len(i)):
        if i[v] != j[v]:
            return f"{i[:v] + '-' + i[v+1:]}"

def stringDiff(a, b):
    diff = 0
    for i in range(len(a)):
        if a[i] != b[i]:
            diff += 1
    if diff == 1:
        return True
    else:
        return False


class CTkTable:
    def __init__(self, parent, headers, editable=False, numHeaders=None, anchor="w"):
        import customtkinter as ctk
        self.ctk = ctk
        self.editable = editable

        # Spaltenanzahl bestimmen
        if numHeaders is None:
            numHeaders = len(headers)
        self.num_cols = int(numHeaders)

        self.headers = list(headers[:self.num_cols]) + [""] * max(0, self.num_cols - len(headers))

        # Scrollbarer Container
        self.container = ctk.CTkScrollableFrame(parent, corner_radius=8, fg_color="transparent")
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Karte mit Grid
        self.card = ctk.CTkFrame(self.container, corner_radius=10)
        self.card.grid(row=0, column=0, sticky="nsew")
        self.card.grid_columnconfigure(tuple(range(self.num_cols)), weight=1, uniform="tblcols")

        # Header
        hdr_font = ctk.CTkFont(size=13, weight="bold")
        self._header_widgets = []
        for c, title in enumerate(self.headers):
            w = ctk.CTkLabel(self.card, text=str(title), font=hdr_font, anchor=anchor)
            w.grid(row=0, column=c, sticky="nsew", padx=6, pady=(6, 4))
            self._header_widgets.append(w)

        # dünne Trennlinie
        self.ctk.CTkFrame(self.card, height=1).grid(
            row=1, column=0, columnspan=self.num_cols, sticky="ew", padx=6, pady=(0, 4)
        )

        # Daten
        self._rows = []         # Rohwerte
        self._cell_widgets = [] # Widgets

        # untere Dehnzeile
        self._bottom_spacer_row = 2
        self.card.grid_rowconfigure(self._bottom_spacer_row, weight=1)

    # ---- API ----
    def add_row(self, values, anchor="w"):
        vals = list(map(lambda x: "" if x is None else str(x), values[:self.num_cols]))
        vals += [""] * (self.num_cols - len(vals))

        insert_at = self._bottom_spacer_row
        self.card.grid_rowconfigure(insert_at, weight=0)

        widgets_row = []
        cell_font = self.ctk.CTkFont(size=12)
        for c, v in enumerate(vals):
            if self.editable:
                w = self.ctk.CTkEntry(self.card)
                w.insert(0, v)
            else:
                w = self.ctk.CTkLabel(self.card, text=v, anchor=anchor, font=cell_font)
            w.grid(row=insert_at, column=c, sticky="nsew", padx=6, pady=2)
            widgets_row.append(w)

        self._rows.append(vals)
        self._cell_widgets.append(widgets_row)

        self._bottom_spacer_row += 1
        self.card.grid_rowconfigure(self._bottom_spacer_row, weight=1)

    def add_separator(self, thickness=1, pady=(4, 4)):
        """Optischer Trenner über die ganze Breite, ohne Datenzeile anzulegen."""
        insert_at = self._bottom_spacer_row
        self.card.grid_rowconfigure(insert_at, weight=0)

        sep = self.ctk.CTkFrame(
            self.card,
            height=thickness,
            fg_color=("gray25", "gray70"),  # dunkles/helles Theme
        )
        sep.grid(
            row=insert_at,
            column=0,
            columnspan=self.num_cols,
            sticky="ew",
            padx=6,
            pady=pady,
        )

        self._bottom_spacer_row += 1
        self.card.grid_rowconfigure(self._bottom_spacer_row, weight=1)

    def get_value(self, row, col):
        w = self._cell_widgets[row][col]
        if isinstance(w, self.ctk.CTkEntry):
            return w.get()
        return w.cget("text")

    def set_value(self, row, col, value):
        value = "" if value is None else str(value)
        w = self._cell_widgets[row][col]
        if isinstance(w, self.ctk.CTkEntry):
            w.delete(0, "end")
            w.insert(0, value)
        else:
            w.configure(text=value)
        self._rows[row][col] = value

    def color_cell(self, row, col, text_color=None, bg_color=None):
        w = self._cell_widgets[row][col]
        kwargs = {}
        if text_color is not None:
            kwargs["text_color"] = text_color
        if bg_color is not None:
            kwargs["fg_color"] = bg_color
        if kwargs:
            w.configure(**kwargs)

    def get_all(self):
        out = []
        for row_widgets in self._cell_widgets:
            row_vals = []
            for w in row_widgets:
                if isinstance(w, self.ctk.CTkEntry):
                    row_vals.append(w.get())
                else:
                    row_vals.append(w.cget("text"))
            out.append(row_vals)
        return out


class App(ctk.CTk):

    anzBits = 0
    
    def __init__(self,):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1980x1080")
        self.minsize(820, 520)

        # State
        self.current_mode = "dark"
        self.bit_choices = [str(i) for i in range(1, 7)]  # 1..8 Bits – bei Bedarf erhöhen
        self.selected_bits = ctk.StringVar(value="4")
        self.checkbox_vars = {}  # value(int) -> ctk.BooleanVar
        self.runCounter = int(0)
        self.count_mergeGroups = []
        self.count_mergeGroup = 0  # Zähler existiert
        self.letters = []
        self.Bits = []
        self.mergeGroup = []
        self.mode = "checkbox"
        self.randomscale = 5
        self.checked = []
        self.current_color = 1
        #Buchstaben von A bis ZZ
        for a in range(26):
            self.letters.append(chr(65 + a))
        for a in range(26):
            for b in range(26):
                self.letters.append(chr(65 + a) + chr(65 + b))

        # Grid-Konfiguration
        self.grid_columnconfigure(0, weight=0)  # Sidebar
        self.grid_columnconfigure(1, weight=1)  # Main
        self.grid_rowconfigure(0, weight=1)     # Content
        self.grid_rowconfigure(1, weight=0)     # Spacer
        self.grid_rowconfigure(2, weight=0)     # Log

        self.load_settings()
        self._build_full_ui()

    # ---------------------- Menü ----------------------
    def load_settings(self):
        # Defaults
        self.settings = {
            "theme": "dark",   # Default, falls nichts vorhanden
            "ftheme": "dark-blue",
            "mode": "checkbox",
            "color": 0
        }

        if SETTINGS_FILE.exists():
            try:
                with SETTINGS_FILE.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                    print(f"Loaded settings: {data}")
                    self.settings.update(data)   # überschreibt Defaults, falls vorhanden
            except json.JSONDecodeError:
                print("Settings-Datei beschädigt, verwende Defaults.")

        ctk.set_appearance_mode(self.settings.get("theme", "dark"))
        ctk.set_default_color_theme(self.settings.get("ftheme", "dark-blue"))
        self.mode = self.settings.get("mode", "checkbox")
        self.randomscale = self.settings.get("randomscale", 5)
        self.animation = self.settings.get("animation", False)
        print(self.mode)

    def save_settings(self):
        with SETTINGS_FILE.open("w", encoding="utf-8") as f:
            json.dump(self.settings, f, indent=4)
    

    
    def open_settings(self):
        # Doppelte Fenster verhindern
        if hasattr(self, "_settings_win") and self._settings_win.winfo_exists():
            self._settings_win.focus_force()
            return

        # Kopie der echten Einstellungen → für Undo
        temp_settings = self.settings.copy()
        original_theme = self.settings["theme"]     # "dark" oder "light"
        original_ftheme = self.settings["ftheme"]
        orginal_mode = self.settings["mode"]
        orginalColor = self.settings["color"]

        win = ctk.CTkToplevel(self)
        self._settings_win = win
        win.title("Einstellungen")
        win.geometry("800x500")
        win.attributes("-topmost", True)
        win.grab_set()
        win.focus_force()

        # --- Schließen (Undo) ---
        def on_close():
            # Theme zurücksetzen (falls Benutzer es geändert hat)
            ctk.set_appearance_mode(original_theme)
            ctk.set_default_color_theme(original_ftheme)
            self.mode = orginal_mode
            self.reset()
            self._rebuild_full_ui()
            win.destroy()

        # Anwenden → final speichern
        def anwenden():
            # temp_settings → self.settings
            self.settings.update(temp_settings)
            self.save_settings()
            win.destroy()
            self.reset()
            self._rebuild_full_ui()

        win.protocol("WM_DELETE_WINDOW", on_close)
        # ---------- UI-Neuaufbau als Funktion ----------
        def build_ui():
            # kompletten Inhalt des Fensters löschen, aber Toplevel selbst behalten
            for child in win.winfo_children():
                child.destroy()

            # --- Inhalt oben ---
            frame = ctk.CTkFrame(win)
            frame.pack(pady=20, padx=20, fill="x")

            frame2 = ctk.CTkFrame(win)
            frame2.pack(pady=10, padx=20, fill="x")

            frame3 = ctk.CTkFrame(win)
            frame3.pack(pady=10, padx=20, fill="x")

            

            # Labels
            ctk.CTkLabel(frame, text="Background:").pack(side="left", padx=10)
            ctk.CTkLabel(frame2, text="Theme:").pack(side="left", padx=10)
            ctk.CTkLabel(frame3, text="Mode:").pack(side="left", padx=10)
            
            

            # Initialer Wert für die Dropdowns:
            current_theme = temp_settings.get("theme", original_theme)
            current_ftheme = temp_settings.get("ftheme", original_ftheme)
            current_mode = temp_settings.get("mode", self.mode).lower()
            self.current_color = temp_settings.get("color", orginalColor)

            initial_mode = "Dark" if current_theme == "dark" else "Light"
            intial_ftheme = current_ftheme

            mode_var = ctk.StringVar(value=initial_mode)
            mode_var2 = ctk.StringVar(value=intial_ftheme)
            mode_var3 = ctk.StringVar(value=current_mode)
            mode_varColor = ctk.IntVar(value=self.current_color)
            
            # --- Live-Vorschau ---
            def on_mode_change(value):
                theme = value.lower()
                ctk.set_appearance_mode(theme)
                temp_settings["theme"] = theme
                # wenn du willst, kann hier auch build_ui() aufgerufen werden,
                # z.B. wenn sich irgendwas am Layout/Style ändert

            def on_mode_change2(value):
                temp_settings["ftheme"] = value
                ctk.set_default_color_theme(value)
                self._rebuild_full_ui()
                build_ui()
                # Settings-UI nach Theme-Wechsel neu aufbauen

            def on_mode_change3(value):
                mode = value.lower()
                self.mode = mode
                temp_settings["mode"] = mode
                self._rebuild_sidebar_full()
                build_ui()

            def on_toggle():
                x = color_switch.get()
                temp_settings["color"] = x
                self.current_color = x

            dropdown = ctk.CTkOptionMenu(
                frame, values=["Dark", "Light"],
                variable=mode_var,
                command=on_mode_change
            )
            dropdown.pack(side="right", padx=10)

            dropdown2 = ctk.CTkOptionMenu(
                frame2, values=["dark-blue", "blue", "green"],
                variable=mode_var2,
                command=on_mode_change2
            )
            dropdown2.pack(side="right", padx=10)

            dropdown3 = ctk.CTkOptionMenu(
                frame3, values=["checkbox", "random"],
                variable=mode_var3,
                command=on_mode_change3
            )
            dropdown3.pack(side="right", padx=10)

            # --- Randomscale-Slider ---
            frame_slider = ctk.CTkFrame(win)
            frame_slider.pack(pady=(0, 10), padx=20, fill="x")

            ctk.CTkLabel(frame_slider, text="Random scale:").pack(side="left", padx=10)
            
            # Label für aktuellen Wert
            current_random = temp_settings.get("randomscale", self.randomscale)
            self.randomscale = current_random  # App-State updaten

            value_label = ctk.CTkLabel(frame_slider, text=str(current_random))
            value_label.pack(side="right", padx=10)

            def on_slider_change(value):
                val = int(float(value))
                self.randomscale = val
                temp_settings["randomscale"] = val
                value_label.configure(text=str(val))

            slider = ctk.CTkSlider(
                frame_slider,
                from_=1,
                to=10,
                number_of_steps=9,
                command=on_slider_change
            )
            slider.pack(pady=10, padx=10, fill="x")
            slider.set(current_random)

            # Wenn aktueller Mode nicht random ist → Slider ausblenden
            if temp_settings["mode"] != "random":
                frame_slider.pack_forget()


            frame_color = ctk.CTkFrame(win)
            frame_color.pack(pady = 10, padx = 20, fill="x")

            lablecolor = ctk.CTkLabel(frame_color,text="toogle color in table 2")
            lablecolor.pack(side="left", padx = 10)
            color_switch = ctk.CTkSwitch(
                frame_color,
                variable=mode_varColor,
                text="",
                command=on_toggle
               
            )
            color_switch.pack(side="right", padx= 10)
            # --- Button-Leiste unten ---
            button_frame = ctk.CTkFrame(win)
            button_frame.pack(side="bottom", fill="x", pady=10, padx=10)

            ctk.CTkButton(button_frame, text="Anwenden", command=anwenden)\
                .pack(side="right", padx=10)

            ctk.CTkButton(button_frame, text="Schließen", command=on_close)\
                .pack(side="left", padx=10)

        # Erstes Mal UI aufbauen
        build_ui()

        
            
 
    def _rebuild_full_ui(self):
        """Zerstört alle Haupt-Widgets und baut die UI neu auf."""
        # Sidebar, Main, Log, Menü entfernen, falls vorhanden
        if hasattr(self, "sidebar") and self.sidebar.winfo_exists():
            self.sidebar.destroy()
        if hasattr(self, "main_area") and self.main_area.winfo_exists():
            
            for child in self.main_area.winfo_children():
                child.destroy()
            self.main_area.destroy()
        if hasattr(self, "log") and self.log.winfo_exists():
            self.log.destroy()

        # Menü-Leiste zurücksetzen
        self.config(menu="")  # altes tk.Menu entfernen

        # interne Tabellen-Referenzen leeren
        self._tables_top = []
        self._tables_bottom = []

        # UI neu aufbauen
        self._build_full_ui()

    def _build_full_ui(self):
        """Baut die komplette Haupt-Oberfläche neu auf."""
        self._build_sidebar()
        self._build_main_content()
        self._build_log()
        self._rebuild_checkboxes()


    # ---------------------- Sidebar ----------------------
    def _rebuild_sidebar_full(self):
        if hasattr(self, "sidebar") and self.sidebar.winfo_exists():
            self.sidebar.destroy()
        self._build_sidebar()
        self._rebuild_checkboxes()


    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, corner_radius=12)
        self.sidebar.grid(row=0, column=0, rowspan=3, sticky="nsw", padx=(10, 8), pady=10)
        self.sidebar.grid_propagate(False)
        self.sidebar.configure(width=240)

        """title = ctk.CTkLabel(self.sidebar, text="Einstellungen", font=ctk.CTkFont(size=16, weight="bold"))
        title.grid(row=0, column=0, padx=12, pady=(12, 6), sticky="w")"""
        settings_btn = ctk.CTkButton(
            self.sidebar,          # z.B. self.sidebar_frame
            text="Einstellungen",             # Zahnrad-Symbol
            command=self.open_settings,
            anchor="center",
            width=220
        )
        settings_btn.grid(row=0, column=0, padx=12, pady=12, sticky="w")

        bits_label = ctk.CTkLabel(self.sidebar, text="Anzahl Bits")
        bits_label.grid(row=1, column=0, padx=12, pady=(6, 4), sticky="w")

        self.bits_combo = ctk.CTkComboBox(
            self.sidebar, values=self.bit_choices, variable=self.selected_bits,
            command=lambda _=None: self._rebuild_checkboxes(), width=120
        )
        self.bits_combo.grid(row=2, column=0, padx=12, pady=(0, 8), sticky="w")

        cb_label = ctk.CTkLabel(self.sidebar, text="Zulässige Dezimalwerte")
        cb_label.grid(row=3, column=0, padx=12, pady=(10, 4), sticky="w")

        self.cb_scroll = ctk.CTkScrollableFrame(self.sidebar, height=360, corner_radius=10)
        self.cb_scroll.grid(row=4, column=0, padx=12, pady=(0, 10), sticky="nsew")

        self.run_btn = ctk.CTkButton(self.sidebar, text="Run", command=self._on_run, height=36)
        self.run_btn.grid(row=6, column=0, padx=12, pady=(0, 12), sticky="w")
        print(self.mode)
        if self.mode == "random":
            self.random_btn = ctk.CTkButton(self.sidebar, text="Generate Random", command=self._on_random, height=36)
            self.random_btn.grid(row=5, column=0, padx=12, pady=(0, 12), sticky="w")
        self.sidebar.grid_rowconfigure(4, weight=1)

    def _rebuild_checkboxes(self):
        # vorher merken, welche Werte angehakt waren
        old_checked = {v for v, var in self.checkbox_vars.items() if var.get()}
        if self.mode == "random":
            old_checked = self.checked
        # alles löschen
        for child in self.cb_scroll.winfo_children():
            child.destroy()
        self.checkbox_vars.clear()

        try:
            n_bits = int(self.selected_bits.get())
        except ValueError:
            n_bits = 1
            self.selected_bits.set("1")

        max_val = (1 << n_bits) - 1

        cols = 1
        for c in range(cols):
            self.cb_scroll.grid_columnconfigure(c, weight=1)

        for v in range(max_val + 1):
            # wieder anhaken, wenn vorher angehakt und noch im Bereich
            var = ctk.BooleanVar(value=(v in old_checked))
            self.checkbox_vars[v] = var

            col = v % cols
            row = v // cols
            if v < 10:
                text = f"{v}   {bits_to_expr(v, n_bits)}"
            elif v < 100:
                text = f"{v}  {bits_to_expr(v, n_bits)}"
            else:
                text = f"{v} {bits_to_expr(v, n_bits)}"

            cb = ctk.CTkCheckBox(self.cb_scroll, text=str(text), variable=var, font=("Consolas", 14))
            cb.grid(row=row, column=col, sticky="w", padx=6, pady=2)

    def checkbox_deactivate(self):
        for i in self.cb_scroll.winfo_children():
            i.configure(state="disabled")
    def checkbox_activate(self):
        for i in self.cb_scroll.winfo_children():
            i.configure(state="normal")
            




    # ---------------------- Main Content (2 übereinander) ----------------------
    def _build_main_content(self):
        self.main_area = ctk.CTkFrame(self, corner_radius=12)
        self.main_area.grid(row=0, column=1, sticky="nsew", padx=(0, 10), pady=(10, 6))
        self.main_area.grid_columnconfigure(0, weight=1)
        self.main_area.grid_rowconfigure(0, weight=1)
        self.main_area.grid_rowconfigure(1, weight=1)

        # Zwei Bereiche WIRKLICH anlegen
        self.top_frame = ctk.CTkFrame(self.main_area, corner_radius=10)
        self.bottom_frame = ctk.CTkFrame(self.main_area, corner_radius=10)
        self.top_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=(10, 5))
        self.bottom_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(5, 10))

        # Tabellen-Bereiche initialisieren
        self._init_tables_area()

    def _init_tables_area(self):
        self._tables_top = []     # nur oben
        self._tables_bottom = []  # nur unten
        self.top_frame.grid_rowconfigure(0, weight=1)
        self.bottom_frame.grid_rowconfigure(0, weight=1)

    def create_table(self, headers, editable=False, numHeaders=None):
        """Neue Tabelle OBEN. Gibt top_id zurück (int)."""
        col_index = len(self._tables_top)
        #print(f"col index: {col_index}")
        self.top_frame.grid_columnconfigure(col_index, weight=1, uniform="tables_top")
        tbl = CTkTable(self.top_frame, headers=headers, editable=editable, numHeaders=numHeaders)
        tbl.container.grid(row=0, column=col_index, sticky="nsew", padx=6, pady=6)
        self._tables_top.append(tbl)
        return col_index

    def create_tableBottom(self, headers, editable=False, numHeaders=None):
        """Neue Tabelle UNTEN. Gibt bottom_id zurück (int)."""
        col_index = len(self._tables_bottom)
        self.bottom_frame.grid_columnconfigure(col_index, weight=1, uniform="tables_bottom")
        tbl = CTkTable(self.bottom_frame, headers=headers, editable=editable, numHeaders=numHeaders, anchor="center")
        tbl.container.grid(row=0, column=col_index, sticky="nsew", padx=6, pady=6)
        self._tables_bottom.append(tbl)
        #self.log_write("Tabelle unten erstellt")
        return col_index

    # ---- oben ----
    def table_add_row(self, table_id, values):
        self._tables_top[table_id].add_row(values)

    def table_get(self, table_id, row, col):
        return self._tables_top[table_id].get_value(row, col)

    def table_set(self, table_id, row, col, value):
        self._tables_top[table_id].set_value(row, col, value)

    def table_color_cell(self, table_id, row, col, text_color=None, bg_color=None):
        self._tables_top[table_id].color_cell(row, col, text_color=text_color, bg_color=bg_color)

    def table_get_all(self, table_id):
        return self._tables_top[table_id].get_all()
    
    def table_add_separator(self, table_id):
        self._tables_top[table_id].add_separator()

    # ---- unten ----
    def table_add_row_bottom(self, table_id, values, anchor):
        self._tables_bottom[table_id].add_row(values, anchor)

    def table_get_bottom(self, table_id, row, col):
        return self._tables_bottom[table_id].get_value(row, col)

    def table_set_bottom(self, table_id, row, col, value):
        self._tables_bottom[table_id].set_value(row, col, value)

    def table_color_cell_bottom(self, table_id, row, col, text_color=None, bg_color=None):
        self._tables_bottom[table_id].color_cell(row, col, text_color=text_color, bg_color=bg_color)


    # Hilfsfunktion, von run_n genutzt (Top-Bereich)
    def getRowOfValue(self, table_id, column, value):
        for r in range(len(self._tables_top[table_id]._rows)):
            if self._tables_top[table_id]._rows[r][column] == str(value):
                return r
        return None

    def clear_tables_top(self):
        for tbl in self._tables_top:
            tbl.container.destroy()
        self._tables_top.clear()

    def clear_tables_bottom(self):
        for tbl in self._tables_bottom:
            tbl.container.destroy()
        self._tables_bottom.clear()

    def clear_tables(self):
        self.clear_tables_top()
        self.clear_tables_bottom()

    def _build_log(self):
        self.log = ctk.CTkTextbox(self, height=150)
        self.log.grid(row=2, column=1, sticky="nsew", padx=(0, 10), pady=(0, 10))
        spacer = ctk.CTkFrame(self, height=2)
        spacer.grid(row=1, column=1, sticky="ew", padx=(0, 10), pady=(0, 0))

    def log_write(self, text: str):
        self.log.configure(state="normal")
        self.log.insert("end", text + "\n")
        self.log.see("end")
        self.log.configure(state="normal")

    def first_run(self, checked):
        tid = self.create_table(["Nr", "0. Ordnung", "Verwendet"], editable=False, numHeaders=3)
        n_bits = int(self.selected_bits.get())
        self.Bits = []  # neu aufbauen
        for i in checked:
            self.Bits.append({
                "bit": i,
                "bitstring": bin(i).replace("0b", "").zfill(n_bits),
                "Ordnung": 0,
                "weight": bin(i).count("1")
            })
        # gruppiert nach weight
        for w in range(0, n_bits + 1):
            for v in self.Bits:
                if v["weight"] == w:
                    self.table_add_row(tid, [str(v["bit"]), v["bitstring"], ""])
            if w != n_bits:
                self.table_add_separator(tid)
                self.table_add_separator(tid)
        self.checkbox_deactivate()
        self.runCounter = 0
    def run_n(self, runcount):
        self.rn = runcount - 1
        self.bitlist1, self.bitlist2 = [], []
        cur_tbl = self._tables_top[self.rn]
        for v in range(len(cur_tbl._rows)):
            for w in range(v + 1, len(cur_tbl._rows)):
                if stringDiff(cur_tbl._rows[v][1], cur_tbl._rows[w][1]):
                    self.bitlist1.append(cur_tbl._rows[v][0])
                    self.bitlist2.append(cur_tbl._rows[w][0])

        if len(self.bitlist1) > 0:
            tid_next = self.create_table(
                ["Nr", f"{self.rn+1}. Ordnung", "Verwendet"], editable=False, numHeaders=3
            )
            # markiere verwendete
            list_table = []
            for i in range(len(self.bitlist1)):
                x = self.getRowOfValue(self.rn, 0, self.bitlist1[i])
                y = self.getRowOfValue(self.rn, 0, self.bitlist2[i])
                if x is not None:
                    self.table_set(self.rn, x, 2, "X")
                if y is not None:
                    self.table_set(self.rn, y, 2, "X")
                z = NewStringFromBits2(self.table_get(self.rn, int(x), 1), self.table_get(self.rn, int(y), 1))
                list_table.append(z)
                self.table_add_row(tid_next, [f"{self.bitlist1[i]}-{self.bitlist2[i]}", z, ""])
                if i+1 != len(self.bitlist1) and str(NewStringFromBits2(self.table_get(self.rn, int(x), 1), self.table_get(self.rn, int(y), 1))).count("1") < str(NewStringFromBits2(self.table_get(self.rn, int(self.getRowOfValue(self.rn, 0, self.bitlist1[i+1])), 1), self.table_get(self.rn, int(self.getRowOfValue(self.rn, 0, self.bitlist2[i+1])), 1))).count("1"):
                    self.table_add_separator(tid_next)
                    self.table_add_separator(tid_next)
        else:
            self.runCounter = 10
            self.run_btn.configure(text="Calculate Answer")

        self.bitStringList, self.listWDublicate, self.mergeValues, self.BitHolder = [], [], [], []
        for a in range(len(self._tables_top[self.rn]._rows)):
            if self._tables_top[self.rn]._rows[a][2] != "X":
                self.bitStringList.append(self._tables_top[self.rn]._rows[a][1])
                self.BitHolder.append(self._tables_top[self.rn]._rows[a][0])
        for i in self.bitStringList:
            if i not in self.listWDublicate:
                self.listWDublicate.append(i)
        for _ in self.listWDublicate:
            self.mergeValues.append(self.count_mergeGroup)
            self.count_mergeGroup += 1
        for v in range(len(self._tables_top[self.rn]._rows)):
            if self._tables_top[self.rn]._rows[v][2] != "X":
                u = self.listWDublicate.index(self._tables_top[self.rn]._rows[v][1])
                letter = self.letters[self.mergeValues[u]]
                self.table_set(self.rn, v, 2, letter)
        for val in self.listWDublicate:
            u = self.listWDublicate.index(val)
            letter = self.letters[self.mergeValues[u]]
            self.mergeGroup.append({"letter": letter, "value": [a for a in str(self.BitHolder[self.bitStringList.index(val)]).split("-")], "expres": val })

    def CalculateAnswer(self, checked):
        headers = [str(ch) for ch in checked]
        if not headers:
            return
        headers.insert(0, "")
        _ = self.create_tableBottom(headers, editable=False, numHeaders=len(headers))
        for val in self.mergeGroup:
            listVal = [a for a in checked]
            for i in range(len(listVal)):
                if str(listVal[i]) in val["value"]:
                    listVal[i] = "X"
                else:
                    listVal[i] = ""
            listVal.insert(0, val["letter"])
            self.table_add_row_bottom(0, listVal, anchor="center")
        letters, wegLetters, letterPrim = [], [], []
        for i in checked:
            for val in self.mergeGroup:
                if str(i) in val["value"]:
                    letters.append(val["letter"])
            if len(letters) == 1:
                for letter in letters:
                    if letter not in wegLetters:
                        wegLetters.append(letter)
                        letterPrim.append(i)
            letters.clear()
        print(wegLetters)
        replacement = {}
        if len(wegLetters) == len(self.mergeGroup):
            self.log_write("Alle Buchstaben sind wichtig.")
            lösung = []
            for val in self.mergeGroup:
                lösung.append(bits_to_expr2(val["expres"]))
            self.colorPrim = wegLetters.copy()

            
        else:
            self.colorPrim = wegLetters.copy()
            bitsUsed = []
            countVal = []
            for object in self.mergeGroup:
                if object["letter"] in wegLetters:
                    for a in object["value"]:
                        if a not in bitsUsed:
                            bitsUsed.append(a)
            
            while len(bitsUsed) < len(checked):
                for val in self.mergeGroup:
                    if val["letter"] not in wegLetters:
                        countValNum = 0
                        for a in val["value"]:
                            if a not in bitsUsed:
                                countValNum += 1
                                print(f" {val["letter"]} used {a} count {countValNum}")
                        countVal.append([val["letter"], countValNum])
                print(f"countVal: {countVal}")
                maxItem = max(countVal, key=lambda x: x[1])
                countVal.remove(maxItem)
                maxItem2 = max(countVal, key=lambda x: x[1]) if len(countVal) > 0 else None
                if maxItem[1] == maxItem2[1]:
                    if self.mergeGroup[[val["letter"] for val in self.mergeGroup].index(maxItem[0])]["expres"].count('-') > self.mergeGroup[[val["letter"] for val in self.mergeGroup].index(maxItem2[0])]["expres"].count('-'):
                        maxItem = maxItem2
                    else:
                        if maxItem[0] not in replacement.keys():
                            replacement[maxItem[0]] = [maxItem2[0]]
                        else:
                            replacement[maxItem[0]].append(maxItem2[0])
                for item in countVal:
                    if item[1] == maxItem[1] and item[0] != maxItem[0]:
                        a = [val for val in self.mergeGroup if val["letter"] == item[0]]
                        b = [val for val in self.mergeGroup if val["letter"] == maxItem[0]]
                        #print(a)
                        #print(b)
                        if a[0]["expres"].count('-') > b[0]["expres"].count('-'):
                            maxItem = item
                        elif item[0] == maxItem[0]:
                            replacement.update({maxItem[0]: [item[0]]})
                        else:
                            pass
                
                for val in self.mergeGroup:
                    if val["letter"] == maxItem[0]:
                        wegLetters.append(val["letter"])
                        for a in val["value"]:
                            if a not in bitsUsed:
                                bitsUsed.append(a)
                countVal.clear()
        lösung = []
        print(f"{wegLetters}")
        for val in self.mergeGroup:
            if val["letter"] in wegLetters:
                lösung.append(bits_to_expr2(val["expres"]))
        lösung1 = '   \u2228   '.join(lösung)
        self.log_write(f"Für Lösung 1 benutzte Buchstaben: {wegLetters}")
        self.log_write(f"Lösung ist: {lösung1}")

        solutions_letters = [set(wegLetters)]

        count = 2
        if len(replacement) > 0:
            checked_set = {int(i) for i in checked}

            for key, ersatz_liste in replacement.items():
                for ersatz in ersatz_liste:


                    alt_letters = [
                        (ersatz if l == key else l)
                        for l in wegLetters
                    ]

                    seen = set()
                    alt_letters_unique = []
                    for l in alt_letters:
                        if l not in seen:
                            seen.add(l)
                            alt_letters_unique.append(l)

                    covered = set()
                    for val in self.mergeGroup:
                        if val["letter"] in alt_letters_unique:
                            for x in val["value"]:
                                covered.add(int(x))

                    if not checked_set.issubset(covered):
                        continue

                    alt_set = set(alt_letters_unique)
                    if any(alt_set == s for s in solutions_letters):
                        continue

                    alt_lösung = []
                    for letter in alt_letters_unique:
                        exp = next(
                            v["expres"]
                            for v in self.mergeGroup
                            if v["letter"] == letter
                        )
                        alt_lösung.append(bits_to_expr2(exp))

                    lösung2 = '   \u2228   '.join(alt_lösung)
                    self.log_write(
                        f"Buchstaben für die {count}. Lösung ist {alt_letters_unique}"
                    )
                    self.log_write(f"{count}. Lösung ist: {lösung2}")
                    count += 1

                    solutions_letters.append(alt_set)

        #  Einfärben der unteren Tabelle 
        if self.current_color == 1:
            letterss = [a["letter"] for a in self.mergeGroup]

            
            for idx in range(len(self.colorPrim)):
                let = self.colorPrim[idx]
                if let not in letterss:
                    continue
                col = letterss.index(let)
                zif = letterPrim[idx]

                row = list(checked).index(zif) + 1

            
                for val in self.mergeGroup:
                    if val["letter"] == let:
                        for i in val["value"]:
                            r = list(checked).index(int(i)) + 1
                            self.table_color_cell_bottom(0, col, r, bg_color="#6e3c00")

                
                self.table_color_cell_bottom(0, col, row, bg_color="#420000")
                self.table_color_cell_bottom(0, col, 0, bg_color="#420000")

            
            if not solutions_letters:
                solutions_letters = [set(wegLetters)]

            
            common_letters = set.intersection(*solutions_letters)
            all_letters = set.union(*solutions_letters)
            variant_letters = all_letters - common_letters

            for let in variant_letters:
                if let in self.colorPrim:
                    continue
                if let not in letterss:
                    continue

                col = letterss.index(let)
                self.table_color_cell_bottom(0, col, 0, bg_color="#003366")
                for val in self.mergeGroup:
                    if val["letter"] == let:
                        for i in val["value"]:
                            r = list(checked).index(int(i)) + 1
                            self.table_color_cell_bottom(0, col, r, bg_color="#003366")

            green_letters = common_letters - set(self.colorPrim)

            for let in green_letters:
                if let not in letterss:
                    continue

                col = letterss.index(let)
                self.table_color_cell_bottom(0, col, 0, bg_color="#003300")
                for val in self.mergeGroup:
                    if val["letter"] == let:
                        for i in val["value"]:
                            r = list(checked).index(int(i)) + 1
                            self.table_color_cell_bottom(0, col, r, bg_color="#003300")

     
    def _clear_frame_grid(self, frame):
        # Alle Kinder löschen
        for child in frame.winfo_children():
            child.destroy()

        # Spalten-Konfig zurücksetzen
        cols, rows = frame.grid_size()
        for c in range(cols):
            frame.grid_columnconfigure(c, weight=0, minsize=0, uniform="")

        for r in range(rows):
            frame.grid_rowconfigure(r, weight=0, minsize=0)

    def reset(self):

        self.runCounter = -1
        self.count_mergeGroup = 0
        self.Bits = []
        self.mergeGroup = []
        self.bitStringList = []
        self.listWDublicate = []
        self.mergeValues = []
        self.BitHolder = []
        self.bitlist1 = []
        self.bitlist2 = []
        self.rn = -1

        self.clear_tables()  
        self._clear_frame_grid(self.top_frame)
        self._clear_frame_grid(self.bottom_frame)

        self.top_frame.grid_columnconfigure(0, weight=1)
        self.bottom_frame.grid_columnconfigure(0, weight=1)
        self._init_tables_area()
        self.run_btn.configure(text="Run")
        self.log_write("Reset completed.")
        self.top_frame.destroy()
        self._rebuild_full_ui()
        self._rebuild_checkboxes()
        self.checkbox_activate()

    def _on_random(self):
        if self.run_btn.cget("text") != "Run":
            return
        nbits = int(self.selected_bits.get())
        maxVal = 2**nbits -1
        self.checked.clear()
        Num = (maxVal/11)*self.randomscale
        Num = math.trunc(Num)
        self.checked = random.sample(range(0, maxVal), Num)
        self.checked.sort()
        self.log_write(f"Generierte Zufallswerte: {self.checked}")
        self._rebuild_checkboxes()

    def _on_run(self):
        try:
            n_bits = int(self.selected_bits.get())
        except ValueError:
            n_bits = 0

        checked = [v for v, var in self.checkbox_vars.items() if var.get()]
        n_bits = int(self.selected_bits.get())

        if len(checked) == 2**n_bits:
            self.log_write("Lösung ist immer 1 da alle Werte ausgewählt sind!")
            self.reset()
            return 

        if len(checked) == 0:
            self.log_write("Lösung ist immer 0 da kein Wert ausgewählt ist!")
            self.reset()
            return  
        print(self.runCounter)
        if self.run_btn.cget("text") == "Run":
            self.first_run(checked)
            self.run_btn.configure(text="Next")
        elif self.runCounter <= 9:
            self.run_n(self.runCounter)
        elif self.runCounter == 11:
            self.run_btn.configure(text="Reset")
            self.CalculateAnswer(checked)
        else:
            self.reset()

        self.runCounter += 1


if __name__ == "__main__":
    app = App()
    app.mainloop()

