import customtkinter
import tkinter 
from tkinter import filedialog, messagebox, simpledialog
from tkinter import ttk
import subprocess
import os
import sys
import json
import re
import shlex
import webbrowser
import importlib.util
import shutil
from PIL import Image, ImageTk

# System Configuration
IS_WINDOWS = sys.platform == "win32"
IS_MAC = sys.platform == "darwin"
IS_HAIKU = sys.platform.startswith("haiku")
IS_BSD = "bsd" in sys.platform or sys.platform.startswith("dragonfly")

# Dynamic modifier key based on Operating System
CMD = "Command" if IS_MAC else "Control"

customtkinter.set_appearance_mode("Dark")

# --- FONTS AND SIZES CONFIGURATION ---
FONT_FAMILY_CODE = "Cascadia Code" if IS_WINDOWS else ("Menlo" if IS_MAC else "Consolas")
FONT_FAMILY_UI = "Segoe UI" if IS_WINDOWS else ("SF Pro Text" if IS_MAC else "Arial")

FONT_UI = (FONT_FAMILY_UI, 11)
FONT_UI_SMALL = (FONT_FAMILY_UI, 10)
FONT_UI_BOLD = (FONT_FAMILY_UI, 11, "bold")
FONT_CODE = (FONT_FAMILY_CODE, 13)

# Specific fonts for menu bar
FONT_MENU = (FONT_FAMILY_UI, 13)
FONT_MENU_BOLD = (FONT_FAMILY_UI, 13, "bold")

# --- DYNAMIC RESOURCE & USER DATA MANAGEMENT ---
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def get_user_data_dir():
    """ Returns AppData/Local/CodeZone (Windows) or ~/.config/CodeZone (Linux/macOS) to prevent PermissionError in Program Files """
    if IS_WINDOWS:
        base_dir = os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))
    else:
        base_dir = os.path.expanduser("~/.config")
    
    data_dir = os.path.join(base_dir, "CodeZone")
    os.makedirs(data_dir, exist_ok=True)
    return data_dir

# User writable data directory
USER_DATA_DIR = get_user_data_dir()

# Writable directories & files saved in AppData/User space
SYNTAX_DIR = os.path.join(USER_DATA_DIR, "syntax")
CONFIG_FILE = os.path.join(USER_DATA_DIR, "config.json")
PLUGIN_FILE = os.path.join(USER_DATA_DIR, "plugins.py")
GLOBAL_KEYWORDS_FILE = os.path.join(SYNTAX_DIR, "keywords.txt")

# Read-only static assets bundle
ICONS_DIR = resource_path("icons")
ICO_LOGO_FILE = os.path.abspath(os.path.join(ICONS_DIR, "logo.ico"))
PNG_LOGO_FILE = os.path.abspath(os.path.join(ICONS_DIR, "logo.png"))

os.makedirs(SYNTAX_DIR, exist_ok=True)
os.makedirs(ICONS_DIR, exist_ok=True)

if not os.path.exists(GLOBAL_KEYWORDS_FILE):
    default_keywords_content = (
        "# PYTHON\n"
        "def class import from return if elif else while for in try except finally with as lambda pass yield async await raise global nonlocal assert break continue True False None print len range list dict set tuple int float str bool input open self\n\n"
        "# C / C++\n"
        "include define void int char float double long short struct enum typedef const static sizeof return if else switch case default while for do break continue goto sizeof NULL true false std vector string cout cin printf scanf\n\n"
        "# JAVA\n"
        "public private protected class interface extends implements static final void int boolean char double float byte short long return if else switch case default while for do break continue try catch finally throw throws import package new This super null true false System out println\n\n"
        "# NIM\n"
        "proc func type var let const import export return if elif else while for in block break continue case of discarding nil true false echo result system seq array string int float bool discard\n\n"
        "# GO\n"
        "func type struct interface package import return var const if else switch case default for range break continue fallthrough map chan go select defer nil true false fmt Println Printf\n\n"
        "# RUBY\n"
        "def class module require import return if elsif else unless while until for in do end yield break next rescue ensure nil true false puts print attr_accessor self\n\n"
        "# LUA\n"
        "function local end if then else elseif do while repeat until for in return break true false nil print require type pairs ipairs\n\n"
        "# CSS\n"
        "color background background-color font-family font-size font-weight margin padding border border-radius display flex grid align-items justify-content position absolute relative fixed width height max-width min-width top bottom left right opacity z-index box-shadow overflow cursor transition transform text-align line-height\n"
    )
    with open(GLOBAL_KEYWORDS_FILE, "w", encoding="utf-8") as f:
        f.write(default_keywords_content)


################---------------- ICON AND LOGO MANAGEMENT ###################

ICON_CACHE = {}

FILE_MAP_ICONS = {
    "py": "python",
    "rb": "ruby",
    "cpp": "cplusplus", "cxx": "cplusplus", "cc": "cplusplus", "h": "cplusplus", "hpp": "cplusplus",
    "c": "c",
    "lua": "lua",
    "cs": "csharp",
    "css": "css3",
    "html": "html5", "htm": "html5",
    "js": "javascript",
    "ts": "typescript",
    "md": "markdown",
    "sh": "bash", "bash": "bash", "zsh": "bash",
    "krk": "kuroko",
    "rs": "rust",
    "jl": "julia",
    "go": "go",
    "nim": "nim",
    "zig": "zig",
    "php": "php",
    "ps1": "powershell",
    "sql": "sqlite",
    "json": "json",
    "png": "image", "jpg": "image", "jpeg": "image", "gif": "image", "bmp": "image", "svg": "image",
    "pdf": "pdf",
    "txt": "file", "log": "file", "cfg": "file", "conf": "file",
    "zip": "archive", "tar": "archive", "gz": "archive", "7z": "archive"
}

def load_png_icon(base_name, size=(16, 16)):
    cache_key = f"{base_name}_{size[0]}x{size[1]}"
    if cache_key in ICON_CACHE:
        return ICON_CACHE[cache_key]

    png_path = os.path.join(ICONS_DIR, f"{base_name}.png")
    if os.path.exists(png_path):
        try:
            img = Image.open(png_path).resize(size, Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            ICON_CACHE[cache_key] = photo
            return photo
        except Exception:
            pass
    return None

def load_logo_image(size=(80, 80)):
    if os.path.exists(ICO_LOGO_FILE):
        try:
            img = Image.open(ICO_LOGO_FILE).resize(size, Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(img)
        except Exception:
            pass
    if os.path.exists(PNG_LOGO_FILE):
        try:
            img = Image.open(PNG_LOGO_FILE).resize(size, Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(img)
        except Exception:
            pass
    return None

def get_file_icon(file_name):
    ext = os.path.splitext(file_name)[1].lower().replace(".", "")
    icon_name = FILE_MAP_ICONS.get(ext, ext)
    
    icon = load_png_icon(icon_name)
    if not icon:
        icon = load_png_icon("file")
    return icon

def apply_window_logo(window):
    window.update_idletasks()
    if os.path.exists(ICO_LOGO_FILE):
        try:
            window.wm_iconbitmap(ICO_LOGO_FILE)
        except Exception:
            pass
    elif os.path.exists(PNG_LOGO_FILE):
        try:
            img = Image.open(PNG_LOGO_FILE)
            photo = ImageTk.PhotoImage(img)
            window.wm_iconphoto(True, photo)
            window._icon_photo_ref = photo
        except Exception:
            pass


def load_all_keywords():
    keywords_set = set()
    if os.path.exists(SYNTAX_DIR):
        for file in os.listdir(SYNTAX_DIR):
            path = os.path.join(SYNTAX_DIR, file)
            if os.path.isfile(path) and file.endswith(".txt"):
                with open(path, "r", encoding="utf-8") as f:
                    for line in f:
                        clean_line = line.strip()
                        if clean_line and not clean_line.startswith("#"):
                            keywords_set.update(clean_line.split())
    return list(keywords_set)


def load_executables_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    
    if getattr(sys, 'frozen', False):
        python_cmd = "python" if IS_WINDOWS else "python3"
    else:
        python_cmd = sys.executable

    return {
        ".py": python_cmd,
        ".js": "node",
        ".go": "go run",
        ".nim": "nim r",
        ".rb": "ruby",
        ".c": "gcc",
        ".cpp": "g++",
        ".lua": "lua",
        ".krk": "kuroko",
        ".java": "java",
        ".html": "browser",
        ".css": "echo"
    }


def save_executables_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)


def open_external_file(path):
    try:
        if IS_WINDOWS:
            os.startfile(path)
        elif IS_MAC:
            subprocess.run(["open", path], check=False)
        else:
            subprocess.run(["xdg-open", path], check=False)
    except Exception as e:
        messagebox.showerror("Error", f"Could not open external file:\n{e}")


config_executables = load_executables_config()
main_working_dir = ""
open_tabs = {}

plugin_blue_words = []
plugin_red_words = []
plugin_green_words = []

autocompletion_popup = None
suggestions_listbox = None
current_auto_word = ""


################---------------- MARKDOWN PREVIEW ###################

def show_markdown_preview(editor_dict):
    raw_text = editor_dict["textbox"].get("1.0", "end-1c")
    
    md_window = customtkinter.CTkToplevel(app)
    md_window.title("Markdown Preview")
    md_window.geometry("700x550")
    md_window.configure(fg_color="#0e1311")
    apply_window_logo(md_window)

    viewer = customtkinter.CTkTextbox(
        md_window, corner_radius=0, fg_color="#0e1311", text_color="#e0e0e0",
        font=FONT_UI, border_width=0
    )
    viewer.pack(fill="both", expand=True, padx=10, pady=10)

    lines = raw_text.split("\n")
    for line in lines:
        if line.startswith("# "):
            viewer.insert("end", f"\n{line[2:].upper()}\n", "h1")
        elif line.startswith("## "):
            viewer.insert("end", f"\n{line[3:]}\n", "h2")
        elif line.startswith("- ") or line.startswith("* "):
            viewer.insert("end", f"  • {line[2:]}\n")
        else:
            viewer.insert("end", f"{line}\n")

    raw = viewer._textbox
    raw.tag_config("h1", font=(FONT_FAMILY_UI, 16, "bold"), foreground="#7bc69e")
    raw.tag_config("h2", font=(FONT_FAMILY_UI, 13, "bold"), foreground="#4fc1ff")
    viewer.configure(state="disabled")


################---------------- EDITING & LEXER HIGHLIGHTING LOGIC ###################

def update_line_numbers(editor_dict):
    textbox = editor_dict["textbox"]
    line_numbers = editor_dict["line_numbers"]
    
    lines = textbox.get("1.0", "end-1c").split("\n")
    line_count = len(lines)
    line_string = "\n".join(str(i) for i in range(1, line_count + 1))
    
    line_numbers.config(state="normal")
    line_numbers.delete("1.0", "end")
    line_numbers.insert("1.0", line_string)
    line_numbers.config(state="disabled")
    
    digits = len(str(line_count))
    line_numbers.config(width=max(4, digits + 1))
    
    line_numbers.yview_moveto(textbox._textbox.yview()[0])
    update_status_bar()


def apply_global_syntax_highlighting(editor_dict):
    raw_widget = editor_dict["textbox"]._textbox
    
    start_idx = raw_widget.index("@0,0 linestart")
    end_idx = raw_widget.index(f"@0,{raw_widget.winfo_height()} lineend")
    
    syntax_tags = [
        "comment", "string", "control_kw", "type_kw", "function", 
        "number", "operator", "bracket", "css_prop", "css_val", 
        "html_tag", "variable"
    ]
    
    for tag in syntax_tags:
        raw_widget.tag_remove(tag, start_idx, end_idx)

    content = raw_widget.get(start_idx, end_idx)
    if not content.strip():
        return

    file_path = editor_dict.get("file_path", "")
    ext = os.path.splitext(file_path)[1].lower() if file_path else ""

    CONTROL_KEYWORDS = {
        "if", "elif", "else", "while", "for", "in", "try", "except", "finally",
        "with", "as", "return", "yield", "break", "continue", "pass", "raise",
        "import", "from", "def", "class", "async", "await", "public", "private",
        "protected", "static", "final", "void", "const", "let", "var", "func",
        "proc", "type", "struct", "enum", "interface", "package", "do", "switch",
        "case", "default", "goto", "fn", "mod", "pub", "use", "impl", "trait"
    }

    TYPE_KEYWORDS = {
        "int", "float", "str", "bool", "list", "dict", "set", "tuple", "bytes",
        "char", "double", "long", "short", "unsigned", "signed", "boolean",
        "byte", "string", "vector", "map", "array", "auto", "i8", "i16", "i32",
        "i64", "u8", "u16", "u32", "u64", "f32", "f64", "usize", "isize", "self", "Self"
    }

    # Combined Lexer Rules (Precedence: Comments > Strings > Keywords/Numbers > Tokens)
    token_patterns = [
        ("comment", r'(?:#.*|//.*|<!--.*?-->|/\*[\s\S]*?\*/)'),
        ("string", r'(?:\x22[^\x22\\\n]*(?:\\.[^\x22\\\n]*)*\x22|\x27[^\x27\\\n]*(?:\\.[^\x27\\\n]*)*\x27|`[^`\\\n]*(?:\\.[^`\\\n]*)*`)'),
        ("html_tag", r'</?[a-zA-Z0-9\-]+(?:\s+[^>]*?)?>'),
        ("function", r'\b[a-zA-Z_][a-zA-Z0-9_]*(?=\s*\()'),
        ("number", r'\b0x[0-9a-fA-F]+\b|\b\d+(?:\.\d+)?\b'),
        ("word", r'\b[a-zA-Z_][a-zA-Z0-9_]*\b'),
        ("operator", r'[\+\-\*\/\%\=\!\<\>\&\|\^\~\:]+'),
        ("bracket", r'[\(\)\[\]\{\}]'),
    ]

    if ext == ".css":
        token_patterns.insert(2, ("css_rule", r'([a-zA-Z\-]+)\s*:\s*([^;\}]+)'))

    lexer_regex = re.compile("|".join(f"(?P<{name}>{pattern})" for name, pattern in token_patterns))

    for match in lexer_regex.finditer(content):
        group_name = match.lastgroup
        m_start, m_end = match.start(), match.end()
        start_pos = f"{start_idx} + {m_start} chars"
        end_pos = f"{start_idx} + {m_end} chars"

        if group_name == "comment":
            raw_widget.tag_add("comment", start_pos, end_pos)
        elif group_name == "string":
            raw_widget.tag_add("string", start_pos, end_pos)
        elif group_name == "html_tag":
            raw_widget.tag_add("html_tag", start_pos, end_pos)
        elif group_name == "function":
            raw_widget.tag_add("function", start_pos, end_pos)
        elif group_name == "number":
            raw_widget.tag_add("number", start_pos, end_pos)
        elif group_name == "word":
            word_text = match.group("word")
            if word_text in CONTROL_KEYWORDS or word_text in plugin_blue_words:
                raw_widget.tag_add("control_kw", start_pos, end_pos)
            elif word_text in TYPE_KEYWORDS or word_text in plugin_green_words:
                raw_widget.tag_add("type_kw", start_pos, end_pos)
            elif word_text in plugin_red_words:
                raw_widget.tag_add("css_prop", start_pos, end_pos)
            else:
                raw_widget.tag_add("variable", start_pos, end_pos)
        elif group_name == "operator":
            raw_widget.tag_add("operator", start_pos, end_pos)
        elif group_name == "bracket":
            raw_widget.tag_add("bracket", start_pos, end_pos)
        elif group_name == "css_rule":
            prop_m = match.group(0).split(":")
            if len(prop_m) >= 2:
                p_end = m_start + len(prop_m[0])
                raw_widget.tag_add("css_prop", start_pos, f"{start_idx} + {p_end} chars")
                raw_widget.tag_add("css_val", f"{start_idx} + {p_end + 1} chars", end_pos)


def auto_close_pair(event, closing_char, editor_dict):
    is_alt_gr = (event.state & 0x0001 and event.state & 0x0004) or (event.state & 0x0006 == 0x0006) or (event.state & 0x0080) or (event.keysym == "ISO_Level3_Shift")
    if event.state & 0x0004 or event.state & 0x0008 or is_alt_gr:
        return None
        
    raw_widget = editor_dict["textbox"]._textbox
    raw_widget.insert("insert", event.char + closing_char)
    raw_widget.mark_set("insert", "insert - 1 char")
    return "break"


def handle_newline(event, editor_dict):
    if autocompletion_popup:
        return confirm_autocompletion(editor_dict)

    raw_widget = editor_dict["textbox"]._textbox
    cursor_index = raw_widget.index("insert")
    line_num = cursor_index.split('.')[0]
    line_text = raw_widget.get(f"{line_num}.0", cursor_index)

    indentation = re.match(r'^\s*', line_text).group(0)
    if line_text.rstrip().endswith(":") or line_text.rstrip().endswith("{"):
        indentation += "    "

    raw_widget.insert("insert", "\n" + indentation)
    update_line_numbers(editor_dict)
    apply_global_syntax_highlighting(editor_dict)
    raw_widget.see("insert")
    return "break"


def handle_key_event(event, editor_dict):
    update_line_numbers(editor_dict)
    if event and event.keysym in ["Up", "Down", "Return", "Escape", "Tab", "Shift_L", "Shift_R", "Control_L", "Control_R", "Alt_L", "ISO_Level3_Shift", "F5"]:
        return
    apply_global_syntax_highlighting(editor_dict)
    handle_autocompletion(editor_dict)


################---------------- SHORTCUTS AND SYSTEM ACTIONS ####################

def undo_action(event=None):
    path, data = get_active_editor()
    if not data:
        return
    try:
        data["textbox"]._textbox.edit_undo()
        update_line_numbers(data)
        apply_global_syntax_highlighting(data)
    except Exception:
        pass
    return "break"

def redo_action(event=None):
    path, data = get_active_editor()
    if not data:
        return
    try:
        data["textbox"]._textbox.edit_redo()
        update_line_numbers(data)
        apply_global_syntax_highlighting(data)
    except Exception:
        pass
    return "break"

def select_all(event=None):
    path, data = get_active_editor()
    if not data:
        return
    raw = data["textbox"]._textbox
    raw.tag_add("sel", "1.0", "end")
    return "break"

def duplicate_current_line(event=None):
    path, data = get_active_editor()
    if not data:
        return
    raw = data["textbox"]._textbox
    cursor = raw.index("insert")
    line_num = cursor.split('.')[0]
    line_text = raw.get(f"{line_num}.0", f"{line_num}.end")
    raw.insert(f"{line_num}.end", "\n" + line_text)
    update_line_numbers(data)
    apply_global_syntax_highlighting(data)
    return "break"


def toggle_line_comment(event=None):
    path, data = get_active_editor()
    if not data:
        return
    raw = data["textbox"]._textbox
    try:
        start = raw.index("sel.first")
        end = raw.index("sel.last")
    except Exception:
        start = raw.index("insert")
        end = start

    start_line = int(start.split('.')[0])
    end_line = int(end.split('.')[0])

    ext = os.path.splitext(path)[1].lower() if path else ""
    symbol = "// " if ext in [".c", ".cpp", ".js", ".java", ".go", ".nim", ".zig", ".ts", ".cs", ".css"] else "# "
    if ext == ".lua":
        symbol = "-- "

    for l in range(start_line, end_line + 1):
        line_start = f"{l}.0"
        line_text = raw.get(line_start, f"{l}.end")
        if line_text.lstrip().startswith(symbol.strip()):
            idx = line_text.find(symbol.strip())
            raw.delete(f"{l}.{idx}", f"{l}.{idx + len(symbol.strip())}")
            if raw.get(f"{l}.{idx}") == " ":
                raw.delete(f"{l}.{idx}")
        else:
            raw.insert(line_start, symbol)

    update_line_numbers(data)
    apply_global_syntax_highlighting(data)
    return "break"


def search_text(event=None):
    path, data = get_active_editor()
    if not data:
        return

    search_win = customtkinter.CTkToplevel(app)
    search_win.title("Search")
    search_win.geometry("320x110")
    search_win.configure(fg_color="#121815")
    search_win.attributes("-topmost", True)
    apply_window_logo(search_win)

    customtkinter.CTkLabel(search_win, text="Search in this file:", font=FONT_UI, text_color="#e0e0e0").pack(pady=(10, 2))
    entry = customtkinter.CTkEntry(search_win, fg_color="#0e1311", text_color="#e0e0e0", font=FONT_UI)
    entry.pack(fill="x", padx=15, pady=5)
    entry.focus()

    def do_search(e=None):
        query = entry.get()
        raw = data["textbox"]._textbox
        raw.tag_remove("search_highlight", "1.0", "end")
        raw.tag_config("search_highlight", background="#3e5048", foreground="#ffffff")
        if not query:
            return
        idx = "1.0"
        while True:
            idx = raw.search(query, idx, stopindex="end", nocase=True)
            if not idx:
                break
            last_idx = f"{idx}+{len(query)}c"
            raw.tag_add("search_highlight", idx, last_idx)
            idx = last_idx

    entry.bind("<Return>", do_search)
    customtkinter.CTkButton(search_win, text="Search", fg_color="#1c2722", hover_color="#7bc69e", command=do_search, font=FONT_UI, height=24).pack(pady=5)
    return "break"


################---------------- AUTOCOMPLETION ###################

def handle_autocompletion(editor_dict):
    raw_widget = editor_dict["textbox"]._textbox
    cursor_index = raw_widget.index("insert")
    line_start = f"{cursor_index.split('.')[0]}.0"
    line_text = raw_widget.get(line_start, cursor_index)
    
    words = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*$', line_text)
    if not words or len(words[0]) < 2:
        hide_autocompletion(editor_dict)
        return

    current_word = words[0]
    file_words = set(re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', raw_widget.get("1.0", "end-1c")))
    all_words = set(load_all_keywords()).union(file_words)

    suggestions = sorted([m for m in all_words if m.startswith(current_word) and m != current_word])
    if not suggestions:
        hide_autocompletion(editor_dict)
        return

    show_autocompletion_popup(suggestions, current_word, editor_dict)


def show_autocompletion_popup(suggestions, current_word, editor_dict):
    global autocompletion_popup, suggestions_listbox, current_auto_word
    raw_widget = editor_dict["textbox"]._textbox
    bbox = raw_widget.bbox("insert")
    if not bbox:
        return
        
    x, y, width, height = bbox
    root_x = raw_widget.winfo_rootx() + x
    root_y = raw_widget.winfo_rooty() + y + height + 5

    if not autocompletion_popup:
        autocompletion_popup = tkinter.Toplevel(app)
        autocompletion_popup.wm_overrideredirect(True)
        autocompletion_popup.attributes("-topmost", True)

        suggestions_listbox = tkinter.Listbox(
            autocompletion_popup, bg="#121815", fg="#e0e0e0",
            selectbackground="#1c2722", selectforeground="#ffffff",
            font=FONT_UI, bd=0, highlightthickness=0
        )
        suggestions_listbox.pack(fill="both", expand=True)

        raw_widget.bind("<Down>", lambda e: navigate_autocompletion_down())
        raw_widget.bind("<Up>", lambda e: navigate_autocompletion_up())
        raw_widget.bind("<Tab>", lambda e: confirm_autocompletion(editor_dict))
        raw_widget.bind("<Escape>", lambda e: hide_autocompletion(editor_dict))

    autocompletion_popup.wm_geometry(f"200x120+{root_x}+{root_y}")
    suggestions_listbox.delete(0, "end")

    for word in suggestions[:12]:
        suggestions_listbox.insert("end", word)

    suggestions_listbox.select_set(0)
    current_auto_word = current_word


def navigate_autocompletion_down():
    if autocompletion_popup and suggestions_listbox:
        cur = suggestions_listbox.curselection()
        if cur and cur[0] < suggestions_listbox.size() - 1:
            suggestions_listbox.select_clear(cur[0])
            suggestions_listbox.select_set(cur[0] + 1)
        return "break"


def navigate_autocompletion_up():
    if autocompletion_popup and suggestions_listbox:
        cur = suggestions_listbox.curselection()
        if cur and cur[0] > 0:
            suggestions_listbox.select_clear(cur[0])
            suggestions_listbox.select_set(cur[0] - 1)
        return "break"


def confirm_autocompletion(editor_dict):
    global autocompletion_popup, suggestions_listbox
    if autocompletion_popup and suggestions_listbox:
        cur = suggestions_listbox.curselection()
        if cur:
            selection = suggestions_listbox.get(cur[0])
        else:
            selection = suggestions_listbox.get(tkinter.ACTIVE)
            
        if selection:
            raw_widget = editor_dict["textbox"]._textbox
            cursor_index = raw_widget.index("insert")
            start_index = f"{cursor_index} - {len(current_auto_word)} chars"
            
            raw_widget.delete(start_index, cursor_index)
            raw_widget.insert("insert", selection)
            
            hide_autocompletion(editor_dict)
            apply_global_syntax_highlighting(editor_dict)
            return "break"


def hide_autocompletion(editor_dict=None):
    global autocompletion_popup, suggestions_listbox
    if autocompletion_popup:
        autocompletion_popup.destroy()
        autocompletion_popup = None
        suggestions_listbox = None
        if editor_dict:
            raw = editor_dict["textbox"]._textbox
            raw.unbind("<Down>")
            raw.unbind("<Up>")


################---------------- PLUGIN ENGINE ###################

def read_and_apply_plugin():
    global plugin_blue_words, plugin_red_words, plugin_green_words

    if not os.path.exists(PLUGIN_FILE):
        return

    try:
        spec = importlib.util.spec_from_file_location("plugins", PLUGIN_FILE)
        plugin_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(plugin_module)

        redraw_components()
    except Exception as e:
        messagebox.showerror("Plugin Error", f"Could not apply plugin:\n{e}")


def redraw_components():
    app.configure(fg_color="#0b0f0d")
    custom_navbar.configure(fg_color="#121815")
    menu_separator.configure(fg_color="#1c2722")
    explorer_zone.configure(fg_color="#121815")
    code_zone.configure(fg_color="#121815")
    status_bar.configure(fg_color="#121815")

    style.configure(".", background="#121815", foreground="#e0e0e0", font=FONT_UI)
    style.configure("Treeview", background="#121815", foreground="#e0e0e0", fieldbackground="#121815", font=FONT_UI)
    style.map("Treeview", background=[("selected", "#1c2722")], foreground=[("selected", "#ffffff")])

    for data in open_tabs.values():
        data["container"].configure(fg_color="#0e1311")
        data["line_numbers"].config(background="#121815", foreground="#888888", font=FONT_CODE)
        data["textbox"].configure(fg_color="#0e1311", text_color="#e0e0e0", font=FONT_CODE)
        
        raw_text = data["textbox"]._textbox
        # Modern Palette Configuration
        raw_text.tag_config("control_kw", foreground="#C586C0") # Magenta/Purple
        raw_text.tag_config("type_kw", foreground="#569CD6")    # Blue
        raw_text.tag_config("function", foreground="#DCDCAA")   # Soft Yellow
        raw_text.tag_config("string", foreground="#CE9178")     # Soft Orange/Coral
        raw_text.tag_config("comment", foreground="#6A9955")    # Soft Green
        raw_text.tag_config("number", foreground="#B5CEA8")     # Light Olive Green
        raw_text.tag_config("operator", foreground="#D4D4D4")   # Light Gray
        raw_text.tag_config("bracket", foreground="#FFD700")    # Gold
        raw_text.tag_config("css_prop", foreground="#9CDCFE")   # Light Cyan
        raw_text.tag_config("css_val", foreground="#CE9178")    # Soft Coral
        raw_text.tag_config("html_tag", foreground="#569CD6")   # Blue
        raw_text.tag_config("variable", foreground="#9CDCFE")   # Light Cyan

        update_line_numbers(data)
        apply_global_syntax_highlighting(data)


def open_plugin_window():
    create_or_switch_tab(os.path.abspath(PLUGIN_FILE))


################---------------- EXTERNAL TERMINAL EXECUTION ###################

def get_active_editor():
    active_tab_id = notebook.select()
    if not active_tab_id:
        return None, None
    
    for path, data in open_tabs.items():
        if str(data["frame"]) == active_tab_id:
            return path, data
    return None, None


def launch_linux_terminal(cmd_executable, clean_file, folder_path):
    term_cmd = f'{cmd_executable} "{clean_file}"; echo ""; read -p "Press Enter to continue..."'
    
    terminals = [
        ["/boot/system/apps/Terminal", "-e", f"bash -c '{term_cmd}'"],
        ["x-terminal-emulator", "-e", f"bash -c '{term_cmd}'"],
        ["gnome-terminal", "--", "bash", "-c", term_cmd],
        ["konsole", "-e", "bash", "-c", term_cmd],
        ["xfce4-terminal", "-e", f"bash -c '{term_cmd}'"],
        ["alacritty", "-e", "bash", "-c", term_cmd],
        ["kitty", "bash", "-c", term_cmd],
        ["xterm", "-e", f"bash -c '{term_cmd}'"]
    ]

    for term_args in terminals:
        term_bin = term_args[0]
        if shutil.which(term_bin) or os.path.exists(term_bin):
            subprocess.Popen(term_args, cwd=folder_path)
            return True

    return False


def run_code(event=None):
    file_path, data = get_active_editor()
    if not data:
        return "break"

    editor = data["textbox"]
    
    if editor is None or file_path is None or not os.path.exists(file_path):
        messagebox.showwarning("Save Required", "Please save the file before running.")
        return "break"

    new_content = editor.get("1.0", "end-1c")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    if os.path.basename(file_path) == PLUGIN_FILE:
        read_and_apply_plugin()

    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".md":
        show_markdown_preview(data)
        return "break"

    if ext == ".html":
        webbrowser.open(os.path.abspath(file_path))
        return "break"

    cmd_executable = config_executables.get(ext)

    if not cmd_executable:
        messagebox.showerror("Execution Error", f"No runner configured for '{ext}'.")
        return "break"

    folder_path = os.path.dirname(file_path)
    clean_file = os.path.normpath(os.path.abspath(file_path))
    filename = os.path.basename(clean_file)
    
    try:
        if IS_WINDOWS:
            title = f"Code Zone Console - {filename}"
            cmd = f'"{cmd_executable}" "{clean_file}" & pause'
            subprocess.Popen(f'start "{title}" cmd /k "{cmd}"', cwd=folder_path, shell=True)
        elif IS_MAC:
            script = f'tell application "Terminal" to do script "cd \\"{folder_path}\\" && {cmd_executable} \\"{clean_file}\\"; read -p \\"Press enter to exit...\\""'
            subprocess.Popen(["osascript", "-e", script])
        else:
            success = launch_linux_terminal(cmd_executable, clean_file, folder_path)
            if not success:
                messagebox.showerror(
                    "Terminal Error",
                    "No supported terminal emulator was found on your system.\n"
                    "Please install x-terminal-emulator, gnome-terminal, konsole, or xterm."
                )
    except Exception as e:
        messagebox.showerror("Execution Error", f"Failed to launch external terminal:\n{e}")

    return "break"


################---------------- TAB MANAGEMENT & EMPTY STATE ###########################

def check_empty_state():
    if not open_tabs:
        empty_state_frame.pack(fill="both", expand=True)
        notebook.pack_forget()
    else:
        empty_state_frame.pack_forget()
        notebook.pack(fill="both", expand=True)
    update_status_bar()


def close_specific_tab(key):
    if key in open_tabs:
        frame = open_tabs[key]["frame"]
        notebook.forget(frame)
        del open_tabs[key]
        check_empty_state()


def close_active_tab(event=None):
    active_id = notebook.select()
    if not active_id:
        return
    
    key_to_close = None
    for key, data in open_tabs.items():
        if str(data["frame"]) == active_id:
            key_to_close = key
            break
            
    if key_to_close:
        close_specific_tab(key_to_close)


def create_or_switch_tab(file_path=None, default_title="untitled.txt"):
    global main_working_dir
    
    search_key = file_path if file_path else default_title
    
    if search_key in open_tabs:
        notebook.select(open_tabs[search_key]["frame"])
        check_empty_state()
        return

    ext = os.path.splitext(search_key)[1].lower().replace(".", "")
    if ext in ["png", "jpg", "jpeg", "gif", "bmp", "pdf", "zip", "tar", "gz", "7z", "exe"]:
        open_external_file(file_path)
        return

    content = ""
    if file_path and os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            messagebox.showerror("Error", f"Could not read file: {e}")
            return

    tab_name = os.path.basename(file_path) if file_path else default_title
    
    new_tab = customtkinter.CTkFrame(notebook, fg_color="#0e1311", border_width=0, corner_radius=0)
    
    img_icon = get_file_icon(tab_name)
    if img_icon:
        notebook.add(new_tab, text=f"  {tab_name}  ", image=img_icon, compound="left")
    else:
        notebook.add(new_tab, text=f"  {tab_name}  ")

    editor_container = customtkinter.CTkFrame(new_tab, fg_color="#0e1311", corner_radius=0, border_width=0)
    editor_container.pack(fill="both", expand=True)

    line_numbers = tkinter.Text(
        editor_container, width=5, padx=5, pady=8, takefocus=0, border=0,
        background="#121815", foreground="#888888", font=FONT_CODE, state="disabled", relief="flat", highlightthickness=0
    )
    line_numbers.pack(side="left", fill="y", padx=0)

    textbox = customtkinter.CTkTextbox(
        editor_container, corner_radius=0, fg_color="#0e1311", text_color="#e0e0e0",
        font=FONT_CODE, border_width=0, undo=True
    )
    textbox.pack(side="right", fill="both", expand=True)

    editor_dict = {
        "frame": new_tab,
        "container": editor_container,
        "line_numbers": line_numbers,
        "textbox": textbox,
        "file_path": file_path
    }

    raw = textbox._textbox
    raw.config(relief="flat", highlightthickness=0, borderwidth=0)
    
    def on_text_scroll(*args):
        line_numbers.yview_moveto(args[0])
        apply_global_syntax_highlighting(editor_dict)

    raw.config(yscrollcommand=on_text_scroll)
    
    # Modern Tags Setup
    raw.tag_config("control_kw", foreground="#C586C0")
    raw.tag_config("type_kw", foreground="#569CD6")
    raw.tag_config("function", foreground="#DCDCAA")
    raw.tag_config("string", foreground="#CE9178")
    raw.tag_config("comment", foreground="#6A9955")
    raw.tag_config("number", foreground="#B5CEA8")
    raw.tag_config("operator", foreground="#D4D4D4")
    raw.tag_config("bracket", foreground="#FFD700")
    raw.tag_config("css_prop", foreground="#9CDCFE")
    raw.tag_config("css_val", foreground="#CE9178")
    raw.tag_config("html_tag", foreground="#569CD6")
    raw.tag_config("variable", foreground="#9CDCFE")

    raw.bind("<KeyRelease>", lambda e: handle_key_event(e, editor_dict))
    raw.bind("<MouseWheel>", lambda e: update_line_numbers(editor_dict))
    raw.bind("<Button-1>", lambda e: [hide_autocompletion(editor_dict), update_line_numbers(editor_dict)])
    raw.bind("<Return>", lambda e: handle_newline(e, editor_dict))

    pairs = {"<parenleft>": ")", "<bracketleft>": "]", "<braceleft>": "}", "<quotedbl>": '"', "<quoteright>": "'", "<less>": ">"}
    for evt, char_f in pairs.items():
        raw.bind(evt, lambda e, c=char_f: auto_close_pair(e, c, editor_dict))

    if content:
        textbox.insert("1.0", content)
        update_line_numbers(editor_dict)
        apply_global_syntax_highlighting(editor_dict)

    open_tabs[search_key] = editor_dict

    notebook.select(new_tab)
    if file_path:
        main_working_dir = os.path.dirname(file_path)

    check_empty_state()


def prompt_create_file(target_folder=None):
    folder = target_folder if target_folder else (main_working_dir if main_working_dir else os.getcwd())
    
    dialog = customtkinter.CTkToplevel(app)
    dialog.title("New File")
    dialog.geometry("320x130")
    dialog.configure(fg_color="#121815")
    dialog.attributes("-topmost", True)
    apply_window_logo(dialog)

    customtkinter.CTkLabel(dialog, text="File name:", font=FONT_UI, text_color="#e0e0e0").pack(pady=(12, 2))
    entry = customtkinter.CTkEntry(dialog, fg_color="#0e1311", text_color="#e0e0e0", font=FONT_UI)
    entry.pack(fill="x", padx=20, pady=5)
    entry.focus()

    def confirm():
        filename = entry.get().strip()
        if filename:
            full_path = os.path.join(folder, filename)
            open(full_path, "w", encoding="utf-8").close()
            
            refresh_explorer()
            create_or_switch_tab(full_path)
        dialog.destroy()

    entry.bind("<Return>", lambda e: confirm())
    customtkinter.CTkButton(dialog, text="Create", fg_color="#1c2722", hover_color="#7bc69e", command=confirm, font=FONT_UI, height=26).pack(pady=5)


def new_file(event=None):
    prompt_create_file()


def open_file(event=None):
    path = filedialog.askopenfilename(
        title="Open File...",
        filetypes=[("All Files", "*.*")]
    )
    if path:
        create_or_switch_tab(path)


def save_file_as(event=None):
    current_path, data = get_active_editor()
    if not data:
        return
    editor = data["textbox"]

    path = filedialog.asksaveasfilename(
        title="Save As...",
        defaultextension=".py",
        filetypes=[("All Files", "*.*")]
    )
    if path:
        new_content = editor.get("1.0", "end-1c")
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_content)

        if current_path and current_path in open_tabs:
            close_specific_tab(current_path)
        create_or_switch_tab(path)
            
        if os.path.basename(path) == PLUGIN_FILE:
            read_and_apply_plugin()


def save_file(event=None):
    current_path, data = get_active_editor()
    if not data:
        return
    editor = data["textbox"]

    if not current_path or not os.path.exists(current_path):
        save_file_as()
    else:
        new_content = editor.get("1.0", "end-1c")
        with open(current_path, "w", encoding="utf-8") as f:
            f.write(new_content)

        if os.path.basename(current_path) == PLUGIN_FILE:
            read_and_apply_plugin()


################---------------- STATUS BAR ###########################

def update_status_bar():
    path, data = get_active_editor()
    if not data:
        status_pos_label.configure(text="Ln 0, Col 0")
        status_lang_label.configure(text="No File", image="")
        return

    raw = data["textbox"]._textbox
    cursor_pos = raw.index("insert")
    line, col = cursor_pos.split('.')
    status_pos_label.configure(text=f"Ln {line}, Col {int(col) + 1}")

    filename = os.path.basename(path) if path else "untitled.txt"
    ext = os.path.splitext(filename)[1].lower().replace(".", "")
    lang_name = ext.upper() if ext else "TEXT"
    
    icon = get_file_icon(filename)
    if icon:
        status_lang_label.configure(text=f"  {lang_name}", image=icon, compound="left")
    else:
        status_lang_label.configure(text=f"  {lang_name}", image="")


################---------------- EXPLORER AND CONTEXT MENU ###########################

def populate_treeview(parent, target_dir):
    try:
        files = os.listdir(target_dir)
    except Exception:
        return

    dirs_list = sorted([f for f in files if os.path.isdir(os.path.join(target_dir, f)) and not f.startswith('.')])
    files_list = sorted([f for f in files if os.path.isfile(os.path.join(target_dir, f)) and not f.startswith('.')])

    img_folder = load_png_icon("folder")
    
    for d in dirs_list:
        full_path = os.path.join(target_dir, d)
        kw = {"image": img_folder} if img_folder else {}
        node = explorer.insert(parent, 'end', text=f" {d}", values=[full_path], open=False, **kw)
        explorer.insert(node, 'end', text="loading...")

    for f in files_list:
        full_path = os.path.join(target_dir, f)
        img_file = get_file_icon(f)
        kw = {"image": img_file} if img_file else {}
        explorer.insert(parent, 'end', text=f" {f}", values=[full_path], **kw)


def refresh_explorer():
    if main_working_dir and os.path.exists(main_working_dir):
        explorer.delete(*explorer.get_children())
        populate_treeview('', main_working_dir)


def trigger_expansion(event):
    node = explorer.focus()
    if not node:
        return
        
    children = explorer.get_children(node)
    if children and explorer.item(children[0])['text'] == "loading...":
        explorer.delete(children[0])
        values = explorer.item(node, 'values')
        if values:
            populate_treeview(node, values[0])


def load_folder():
    global main_working_dir
    folder = filedialog.askdirectory(title="Select Working Folder")
    if folder:
        main_working_dir = folder
        refresh_explorer()


def explorer_double_click(event):
    item = explorer.selection()
    if item:
        values = explorer.item(item[0], 'values')
        if values:
            path = values[0]
            if os.path.isfile(path):
                create_or_switch_tab(path)


def show_explorer_context_menu(event):
    item = explorer.identify_row(event.y)
    if item:
        explorer.selection_set(item)
        values = explorer.item(item, 'values')
        selected_path = values[0] if values else None
    else:
        selected_path = main_working_dir if main_working_dir else os.getcwd()

    target_folder = selected_path if os.path.isdir(selected_path) else os.path.dirname(selected_path)

    context_menu = customtkinter.CTkToplevel(app)
    context_menu.overrideredirect(True)
    context_menu.attributes("-topmost", True)
    apply_window_logo(context_menu)

    frame = customtkinter.CTkFrame(context_menu, fg_color="#121815", border_width=1, border_color="#2a3b32", corner_radius=0)
    frame.pack(fill="both", expand=True)

    def action_new_file():
        context_menu.destroy()
        prompt_create_file(target_folder)

    def action_new_folder():
        context_menu.destroy()
        dialog = customtkinter.CTkToplevel(app)
        dialog.title("New Folder")
        dialog.geometry("320x130")
        dialog.configure(fg_color="#121815")
        dialog.attributes("-topmost", True)
        apply_window_logo(dialog)

        customtkinter.CTkLabel(dialog, text="Folder name:", font=FONT_UI, text_color="#e0e0e0").pack(pady=(12, 2))
        entry = customtkinter.CTkEntry(dialog, fg_color="#0e1311", text_color="#e0e0e0", font=FONT_UI)
        entry.pack(fill="x", padx=20, pady=5)
        entry.focus()

        def confirm():
            foldername = entry.get().strip()
            if foldername:
                os.makedirs(os.path.join(target_folder, foldername), exist_ok=True)
                refresh_explorer()
            dialog.destroy()

        entry.bind("<Return>", lambda e: confirm())
        customtkinter.CTkButton(dialog, text="Create", fg_color="#1c2722", hover_color="#7bc69e", command=confirm, font=FONT_UI, height=26).pack(pady=5)

    def action_delete():
        context_menu.destroy()
        if selected_path and os.path.exists(selected_path):
            if selected_path == os.getcwd() and not main_working_dir:
                messagebox.showwarning("Warning", "Cannot delete current working directory.")
                return
            if messagebox.askyesno("Confirmation", f"Delete '{os.path.basename(selected_path)}' ?"):
                try:
                    if os.path.isdir(selected_path):
                        os.rmdir(selected_path)
                    else:
                        os.remove(selected_path)
                        close_specific_tab(selected_path)
                    refresh_explorer()
                except Exception as e:
                    messagebox.showerror("Error", f"Could not delete:\n{e}")

    actions = [
        ("New File", action_new_file),
        ("New Folder", action_new_folder),
        ("-", None),
        ("Delete", action_delete)
    ]

    for label, cmd in actions:
        if label == "-":
            sep = customtkinter.CTkFrame(frame, height=1, fg_color="#2a3b32")
            sep.pack(fill="x", padx=10, pady=4)
        else:
            btn = customtkinter.CTkButton(
                frame, text=label, fg_color="transparent", hover_color="#1c2722",
                text_color="#e0e0e0", font=FONT_UI, anchor="w", corner_radius=0, height=26,
                command=cmd
            )
            btn.pack(fill="x", padx=4, pady=1)

    context_menu.geometry(f"+{event.x_root}+{event.y_root}")
    open_menus.append(context_menu)


################---------------- CUSTOM SUBMENUS ###########################

open_menus = []
menu_buttons = []

def close_all_menus():
    global open_menus
    for m in list(open_menus):
        try:
            m.destroy()
        except Exception:
            pass
    open_menus.clear()

def create_menu_action(cmd):
    def action():
        close_all_menus()
        if cmd:
            cmd()
    return action

def show_custom_menu(parent_button, commands):
    global open_menus
    x_btn = parent_button.winfo_rootx()
    
    already_open = False
    for m in list(open_menus):
        try:
            if m.winfo_rootx() == x_btn:
                already_open = True
            m.destroy()
        except Exception:
            pass
    open_menus.clear()
    
    if already_open:
        return

    menu = customtkinter.CTkToplevel(app)
    menu.overrideredirect(True)
    menu.attributes("-topmost", True)
    apply_window_logo(menu)
    
    frame = customtkinter.CTkFrame(menu, fg_color="#121815", border_width=1, border_color="#2a3b32", corner_radius=0, width=240)
    frame.pack(fill="both", expand=True)

    for label, command in commands:
        if label == "-":
            sep = customtkinter.CTkFrame(frame, height=1, fg_color="#2a3b32")
            sep.pack(fill="x", padx=10, pady=4)
        else:
            btn = customtkinter.CTkButton(
                frame, text=label, fg_color="transparent", hover_color="#1c2722",
                text_color="#e0e0e0", font=FONT_MENU, anchor="w", corner_radius=0, height=34
            )
            if command:
                btn.configure(command=create_menu_action(command))
            btn.pack(fill="x", padx=4, pady=1)

    menu.update_idletasks()
    y_btn = parent_button.winfo_rooty() + parent_button.winfo_height()
    menu.geometry(f"+{x_btn}+{y_btn}")
    open_menus.append(menu)

def handle_global_click(event):
    if not open_menus:
        return
    try:
        x, y = event.x_root, event.y_root
        for btn in menu_buttons:
            if btn.winfo_exists():
                bx1 = btn.winfo_rootx()
                by1 = btn.winfo_rooty()
                bx2 = bx1 + btn.winfo_width()
                by2 = by1 + btn.winfo_height()
                if bx1 <= x <= bx2 and by1 <= y <= by2:
                    return
                    
        for m in list(open_menus):
            if m.winfo_exists():
                x1 = m.winfo_rootx()
                y1 = m.winfo_rooty()
                x2 = x1 + m.winfo_width()
                y2 = y1 + m.winfo_height()
                if not (x1 <= x <= x2 and y1 <= y <= y2):
                    m.destroy()
                    open_menus.remove(m)
    except Exception:
        pass


def configure_executors():
    win = customtkinter.CTkToplevel(app)
    win.title("Executors Configuration")
    win.geometry("520x400")
    win.configure(fg_color="#121815")
    win.attributes("-topmost", True)
    apply_window_logo(win)

    customtkinter.CTkLabel(win, text="Executors by extension", font=FONT_UI_BOLD, text_color="#e0e0e0").pack(pady=(10, 5))

    frame_list = customtkinter.CTkScrollableFrame(win, fg_color="#0e1311", height=230)
    frame_list.pack(fill="both", expand=True, padx=15, pady=5)

    rows = []

    def add_executor_row(ext="", cmd=""):
        r = customtkinter.CTkFrame(frame_list, fg_color="transparent")
        r.pack(fill="x", pady=3)

        ext_entry = customtkinter.CTkEntry(r, width=80, fg_color="#121815", text_color="#7bc69e", border_width=1, font=FONT_UI)
        ext_entry.insert(0, ext)
        ext_entry.pack(side="left", padx=(0, 5))

        cmd_entry = customtkinter.CTkEntry(r, fg_color="#121815", text_color="#e0e0e0", border_width=1, font=FONT_UI)
        cmd_entry.insert(0, cmd)
        cmd_entry.pack(side="left", fill="x", expand=True, padx=5)

        del_btn = customtkinter.CTkButton(
            r, text="✕", width=28, height=28, fg_color="#5a1d1d", hover_color="#8b0000",
            text_color="#ffffff", font=FONT_UI_BOLD, command=lambda: remove_row(r, row_tuple)
        )
        del_btn.pack(side="right", padx=(5, 0))

        row_tuple = (r, ext_entry, cmd_entry)
        rows.append(row_tuple)

    def remove_row(row_frame, row_tuple):
        if row_tuple in rows:
            rows.remove(row_tuple)
        row_frame.destroy()

    for ext, cmd in config_executables.items():
        add_executor_row(ext, cmd)

    btn_frame = customtkinter.CTkFrame(win, fg_color="transparent")
    btn_frame.pack(fill="x", padx=15, pady=10)

    customtkinter.CTkButton(
        btn_frame, text="+ Add Language", fg_color="#1b4d3e", hover_color="#7bc69e",
        text_color="#ffffff", font=FONT_UI_BOLD, command=lambda: add_executor_row(".", "")
    ).pack(side="left")

    def save_config():
        new_config = {}
        for _, ext_e, cmd_e in rows:
            ext_val = ext_e.get().strip()
            cmd_val = cmd_e.get().strip()
            if ext_val and cmd_val:
                if not ext_val.startswith("."):
                    ext_val = "." + ext_val
                new_config[ext_val] = cmd_val

        global config_executables
        config_executables = new_config
        save_executables_config(config_executables)
        win.destroy()

    customtkinter.CTkButton(
        btn_frame, text="Save", fg_color="#1c2722", hover_color="#7bc69e",
        text_color="#ffffff", font=FONT_UI, command=save_config
    ).pack(side="right")


def manage_syntax_keywords():
    create_or_switch_tab(os.path.abspath(GLOBAL_KEYWORDS_FILE))


################---------------- MAIN WINDOW CONFIGURATION ###################

app = customtkinter.CTk()
app.geometry("1100x650")
app.title("CODE ZONE — IDE")
app.configure(fg_color="#0b0f0d")
apply_window_logo(app)

# Shortcuts
app.bind("<F5>", run_code)
app.bind(f"<{CMD}-n>", new_file)
app.bind(f"<{CMD}-o>", open_file)
app.bind(f"<{CMD}-s>", save_file)
app.bind(f"<{CMD}-Shift-S>", save_file_as)
app.bind(f"<{CMD}-w>", close_active_tab)
app.bind(f"<{CMD}-d>", duplicate_current_line)
app.bind(f"<{CMD}-slash>", toggle_line_comment)
app.bind(f"<{CMD}-f>", search_text)

# Editing shortcuts
app.bind(f"<{CMD}-z>", undo_action)
app.bind(f"<{CMD}-y>", redo_action)
app.bind(f"<{CMD}-Shift-Z>", redo_action)
app.bind(f"<{CMD}-a>", select_all)

app.bind_all("<Button-1>", handle_global_click, add="+")

# Advanced TTK styling
style = ttk.Style()
style.theme_use("clam")

style.configure(".", background="#121815", foreground="#e0e0e0", borderwidth=0, font=FONT_UI)

# Notebook style
style.configure(
    "TNotebook", 
    background="#121815", 
    borderwidth=0, 
    highlightthickness=0, 
    darkcolor="#121815", 
    lightcolor="#121815",
    bordercolor="#121815"
)
style.configure(
    "TNotebook.Tab", 
    background="#121815", 
    foreground="#888888", 
    padding=[16, 8], 
    borderwidth=0, 
    font=FONT_UI, 
    focuscolor="#121815",
    bordercolor="#121815",
    lightcolor="#121815",
    darkcolor="#121815"
)
style.map(
    "TNotebook.Tab", 
    background=[("selected", "#0e1311")], 
    foreground=[("selected", "#e0e0e0")],
    bordercolor=[("selected", "#0e1311")],
    lightcolor=[("selected", "#0e1311")],
    darkcolor=[("selected", "#0e1311")]
)
style.layout("TNotebook", [('Notebook.client', {'sticky': 'nswe'})])
style.layout("TNotebook.Tab", [('Notebook.tab', {'sticky': 'nswe', 'children': [('Notebook.padding', {'side': 'top', 'sticky': 'nswe', 'children': [('Notebook.label', {'side': 'top', 'sticky': ''})]})]})])

# Treeview style
style.configure(
    "Treeview",
    background="#121815",
    foreground="#e0e0e0",
    fieldbackground="#121815",
    borderwidth=0,
    highlightthickness=0,
    bordercolor="#121815",
    lightcolor="#121815",
    darkcolor="#121815",
    relief="flat",
    rowheight=26,
    font=FONT_UI
)
style.map("Treeview", background=[("selected", "#1c2722")], foreground=[("selected", "#ffffff")])
style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})])

# Top navigation bar
custom_navbar = customtkinter.CTkFrame(app, height=44, fg_color="#121815", corner_radius=0, border_width=0)
custom_navbar.pack(fill="x", side="top")

# Separator under menu bar
menu_separator = customtkinter.CTkFrame(app, height=2, fg_color="#1c2722", corner_radius=0)
menu_separator.pack(fill="x", side="top")

btn_file = customtkinter.CTkButton(
    custom_navbar, text="File", width=90, height=34, fg_color="transparent", 
    hover_color="#1c2722", text_color="#e0e0e0", font=FONT_MENU_BOLD, anchor="w"
)
btn_file.pack(side="left", padx=3, pady=5)

lbl_cmd = "Cmd" if IS_MAC else "Ctrl"
file_commands = [
    (f"New File                {lbl_cmd}+N", new_file),
    (f"Open File...            {lbl_cmd}+O", open_file),
    ("Open Folder...", load_folder),
    ("-", None),
    (f"Save                    {lbl_cmd}+S", save_file),
    (f"Save As...              {lbl_cmd}+Shift+S", save_file_as),
    ("-", None),
    ("Exit", app.quit)
]
btn_file.bind("<Button-1>", lambda e: show_custom_menu(btn_file, file_commands))

btn_options = customtkinter.CTkButton(
    custom_navbar, text="Options", width=90, height=34, fg_color="transparent", 
    hover_color="#1c2722", text_color="#e0e0e0", font=FONT_MENU_BOLD, anchor="w"
)
btn_options.pack(side="left", padx=3, pady=5)

options_commands = [
    ("Configure Executors...", configure_executors),
    ("Syntax Keywords...", manage_syntax_keywords),
    ("Edit Python Plugin...", open_plugin_window)
]
btn_options.bind("<Button-1>", lambda e: show_custom_menu(btn_options, options_commands))

btn_run_menu = customtkinter.CTkButton(
    custom_navbar, text="Run", width=90, height=34, fg_color="transparent", 
    hover_color="#1c2722", text_color="#e0e0e0", font=FONT_MENU_BOLD, anchor="w"
)
btn_run_menu.pack(side="left", padx=3, pady=5)

run_commands = [
    ("Run Code / Markdown   F5", run_code)
]
btn_run_menu.bind("<Button-1>", lambda e: show_custom_menu(btn_run_menu, run_commands))

menu_buttons.extend([btn_file, btn_options, btn_run_menu])

# Main panel
main_panel = customtkinter.CTkFrame(app, fg_color="#0b0f0d", corner_radius=0, border_width=0)
main_panel.pack(fill="both", expand=True)

# Left: File explorer
explorer_zone = customtkinter.CTkFrame(main_panel, width=240, fg_color="#121815", corner_radius=0, border_width=0)
explorer_zone.pack(side="left", fill="y", padx=0)

lbl_exp = customtkinter.CTkLabel(explorer_zone, text="EXPLORER", font=FONT_UI_BOLD, text_color="#888888")
lbl_exp.pack(anchor="w", padx=10, pady=(10, 5))

explorer = ttk.Treeview(explorer_zone, show="tree", selectmode="browse")
explorer.pack(fill="both", expand=True, padx=5, pady=5)
explorer.bind("<Double-1>", explorer_double_click)
explorer.bind("<<TreeviewOpen>>", trigger_expansion)
explorer.bind("<Button-3>", show_explorer_context_menu)

# Right: Code editor
right_zone = customtkinter.CTkFrame(main_panel, fg_color="#0b0f0d", corner_radius=0, border_width=0)
right_zone.pack(side="right", fill="both", expand=True)

code_zone = customtkinter.CTkFrame(right_zone, fg_color="#121815", corner_radius=0, border_width=0)
code_zone.pack(fill="both", expand=True, side="top", pady=0)

editor_action_bar = customtkinter.CTkFrame(code_zone, height=36, fg_color="#121815", corner_radius=0, border_width=0)
editor_action_bar.pack(fill="x", side="top")

btn_run = customtkinter.CTkButton(
    editor_action_bar, text="▶ Run (F5)", fg_color="#1b4d3e", 
    hover_color="#7bc69e", text_color="#ffffff", font=FONT_UI_BOLD, height=28, width=100, command=run_code
)
btn_run.pack(side="left", padx=5, pady=3)

btn_close = customtkinter.CTkButton(
    editor_action_bar, text=f"✕ Close ({lbl_cmd}+W)", fg_color="#5a1d1d", 
    hover_color="#8b0000", text_color="#ffffff", font=FONT_UI, height=28, command=close_active_tab
)
btn_close.pack(side="left", padx=5, pady=3)

notebook = ttk.Notebook(code_zone)
notebook.pack(fill="both", expand=True)

# Empty State Frame
empty_state_frame = customtkinter.CTkFrame(code_zone, fg_color="#0e1311", corner_radius=0)

logo_img = load_logo_image((72, 72))
if logo_img:
    logo_label = customtkinter.CTkLabel(empty_state_frame, image=logo_img, text="")
    logo_label.image = logo_img
    logo_label.pack(pady=(120, 10))

customtkinter.CTkLabel(empty_state_frame, text="CODE ZONE", font=(FONT_FAMILY_UI, 22, "bold"), text_color="#e0e0e0").pack(pady=(0, 5))
customtkinter.CTkLabel(empty_state_frame, text="Lightweight, Extensible & Fast Editor", font=FONT_UI, text_color="#888888").pack(pady=(0, 25))

shortcuts_text = (
    f"{lbl_cmd} + N   •   New File\n"
    f"{lbl_cmd} + O   •  Open File\n"
    "F5         •   Run File"
)
customtkinter.CTkLabel(empty_state_frame, text=shortcuts_text, font=FONT_CODE, text_color="#7bc69e", justify="center").pack()

# Status Bar
status_bar = customtkinter.CTkFrame(app, height=26, fg_color="#121815", corner_radius=0)
status_bar.pack(fill="x", side="bottom")

status_pos_label = customtkinter.CTkLabel(status_bar, text="Ln 1, Col 1", font=FONT_UI_SMALL, text_color="#888888")
status_pos_label.pack(side="left", padx=10)

status_lang_label = customtkinter.CTkLabel(status_bar, text="TEXT", font=FONT_UI_SMALL, text_color="#e0e0e0")
status_lang_label.pack(side="right", padx=15)

status_enc_label = customtkinter.CTkLabel(status_bar, text="UTF-8   |   LF", font=FONT_UI_SMALL, text_color="#888888")
status_enc_label.pack(side="right", padx=15)

# Initialization
check_empty_state()
read_and_apply_plugin()

app.mainloop()