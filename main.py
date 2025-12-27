from tkinter import *
import re
import sympy as sp

# --- Constants for Superscript Mapping ---
# Mapping visual superscript characters to their normal string equivalents
SUPERSCRIPTS = {
    '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴',
    '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹',
    'n': 'ⁿ', '': ''
}
SUPERSCRIPTS_INV = {v: k for k, v in SUPERSCRIPTS.items() if v}

# --- Regex Patterns for Math Parsing ---
# Pattern to find a base followed by superscripts (e.g., x²)
RE_SUPERSCRIPTS_SEQ = re.compile(r'([A-Za-z0-9\)\]])([⁰¹²³⁴⁵⁶⁷⁸⁹ⁿ]+)')
# Pattern for roots with a specific index (e.g., ³√(x))
RE_ROOT_WITH_INDEX = re.compile(r'([⁰¹²³⁴⁵⁶⁷⁸⁹ⁿ]+)√\(([^)]+)\)')
# Pattern for plain square roots with parentheses (e.g., √(x))
RE_ROOT_PLAIN = re.compile(r'√\(([^)]+)\)')
# Pattern for simple roots without parentheses (e.g., √n)
RE_ROOT_NO_PARENS = re.compile(r'√([A-Za-z0-9]+)')
# Pattern to detect superscripts appearing before a root symbol
RE_SUPER_AT_START = re.compile(r'([⁰¹²³⁴⁵⁶⁷⁸⁹ⁿ]+)(?=[A-Za-z0-9]*√)')

# --- GUI Setup ---
root = Tk()
root.title("Series Convergence Analyzer. D'Alembert's Ratio Test")
root.attributes("-fullscreen", True)


def supers_to_normal(sup_seq: str) -> str:
    """Converts a string of superscript characters to normal characters."""
    out = []
    for ch in sup_seq:
        normal = SUPERSCRIPTS_INV.get(ch)
        if normal is None:
            continue
        out.append(normal)
    return "".join(out)


def replace_superscripts(expr: str) -> str:
    """Replaces visual superscripts (e.g., n²) with Python power syntax (n**(2))."""

    def repl(m):
        base = m.group(1)
        sup = m.group(2)
        normal = supers_to_normal(sup)
        return f"{base}**({normal})"

    return RE_SUPERSCRIPTS_SEQ.sub(repl, expr)


def replace_root_with_index(expr: str) -> str:
    """Replaces roots with indices (e.g., ³√(n)) with fractional powers (n**(1/3))."""

    def repl(m):
        sup = m.group(1)
        inside = m.group(2)
        normal = supers_to_normal(sup)
        return f"({inside})**(1/{normal})"

    return RE_ROOT_WITH_INDEX.sub(repl, expr)


def replace_plain_root(expr: str) -> str:
    """Replaces standard square roots (√n) with power of 0.5."""
    expr = RE_ROOT_WITH_INDEX.sub(lambda m: m.group(0), expr)
    expr = RE_ROOT_PLAIN.sub(lambda m: f"({m.group(1)})**(1/2)", expr)
    expr = RE_ROOT_NO_PARENS.sub(lambda m: f"{m.group(1)}**(1/2)", expr)
    return expr


def replace_factorial(expr: str) -> str:
    """Replaces 'n!' notation with a function call 'fact(n)'."""
    expr = re.sub(r'([A-Za-z0-9\)\]]+)!', r'fact(\1)', expr)
    return expr


def convert_visual_to_python(expr: str) -> str:
    """
    Main pipeline to convert the visual mathematical string from the GUI
    into a valid Python syntax string compatible with SymPy.
    """
    s = expr
    s = replace_root_with_index(s)
    s = replace_plain_root(s)
    s = replace_superscripts(s)
    s = replace_factorial(s)
    s = s.strip()
    return s


def to_superscript(text):
    """Converts normal text to superscript characters."""
    return "".join(SUPERSCRIPTS.get(char, char) for char in str(text))


# --- Event Handlers ---

def apply_power():
    """Inserts a superscript power into the active entry field."""
    power_value = power_entry.get()
    if not power_value.isdigit() and power_value != "n":
        return
    focused_widget = root.focus_get()
    if focused_widget in (entry_num, entry_den):
        current_text = focused_widget.get()
        new_text = current_text + to_superscript(power_value)
        focused_widget.delete(0, END)
        focused_widget.insert(0, new_text)


def apply_factorial():
    """Appends '!' to the current input in the active entry field."""
    focused_widget = root.focus_get()
    if focused_widget in (entry_num, entry_den):
        current_text = focused_widget.get()
        if not current_text.endswith('!'):
            focused_widget.delete(0, END)
            focused_widget.insert(0, current_text + '!')


def apply_sqrt():
    """Wraps selected text or inserts a square root symbol."""
    focused_widget = root.focus_get()
    if focused_widget not in (entry_num, entry_den):
        return
    try:
        start = focused_widget.index(SEL_FIRST)
        end = focused_widget.index(SEL_LAST)
        text = focused_widget.get()
        selected = text[start:end]
        new_text = text[:start] + f"√({selected})" + text[end:]
        focused_widget.delete(0, END)
        focused_widget.insert(0, new_text)
        focused_widget.icursor(start + len(f"√({selected})"))
    except:
        pos = focused_widget.index(INSERT)
        text = focused_widget.get()
        new_text = text[:pos] + "√" + text[pos:]
        focused_widget.delete(0, END)
        focused_widget.insert(0, new_text)
        focused_widget.icursor(pos + 1)


def apply_root_power():
    """Inserts a root with a specific index (N-th root)."""
    focused_widget = root.focus_get()
    if focused_widget not in (entry_num, entry_den):
        return
    root_power = root_power_entry.get().strip()
    root_super = to_superscript(root_power) if root_power else ""
    try:
        start = focused_widget.index(SEL_FIRST)
        end = focused_widget.index(SEL_LAST)
        text = focused_widget.get()
        selected = text[start:end]
        new_text = text[:start] + f"{root_super}√({selected})" + text[end:]
        focused_widget.delete(0, END)
        focused_widget.insert(0, new_text)
        focused_widget.icursor(start + len(f"{root_super}√({selected})"))
    except:
        pos = focused_widget.index(INSERT)
        text = focused_widget.get()
        new_text = text[:pos] + root_super + "√" + text[pos:]
        focused_widget.delete(0, END)
        focused_widget.insert(0, new_text)
        focused_widget.icursor(pos + len(root_super) + 1)


def analyze_dalamber():
    """
    Performs the D'Alembert Ratio Test using SymPy.
    Calculates lim (n->inf) |a_n+1 / a_n|.
    """
    numerator = entry_num.get()
    denominator = entry_den.get()

    if not numerator or not denominator:
        result_text.delete(1.0, END)
        result_text.insert(END, "Error: Please enter both numerator and denominator!")
        return

    try:
        # Define 'n' as a positive integer symbol
        n = sp.Symbol('n', positive=True, integer=True)

        # Convert visual input strings to Python expressions
        num_expr = convert_visual_to_python(numerator)
        den_expr = convert_visual_to_python(denominator)

        # Map our 'fact' placeholder to SymPy's factorial
        num_expr = num_expr.replace('fact', 'sp.factorial')
        den_expr = den_expr.replace('fact', 'sp.factorial')

        # Create a safe evaluation context
        local_dict = {'n': n, 'sp': sp}

        # Evaluate expressions to create SymPy objects
        num_sympy = eval(num_expr, {"__builtins__": {}}, local_dict)
        den_sympy = eval(den_expr, {"__builtins__": {}}, local_dict)

        # Define the general term a_n
        a_n = num_sympy / den_sympy

        # Define the next term a_{n+1}
        a_n_plus_1 = a_n.subs(n, n + 1)

        # Calculate the ratio
        ratio = sp.simplify(a_n_plus_1 / a_n)

        # Calculate the limit as n approaches infinity
        limit_value = sp.limit(ratio, n, sp.oo)

        # --- Display Results ---
        result_text.delete(1.0, END)
        result_text.insert(END, "═" * 60 + "\n")
        result_text.insert(END, "D'ALEMBERT'S RATIO TEST ANALYSIS\n")
        result_text.insert(END, "═" * 60 + "\n\n")

        result_text.insert(END, f"General term of the series:\n")
        result_text.insert(END, f"aₙ = {numerator} / {denominator}\n\n")

        result_text.insert(END, f"Next term of the series:\n")
        result_text.insert(END, f"aₙ₊₁ = {a_n_plus_1}\n\n")

        result_text.insert(END, f"Ratio aₙ₊₁ / aₙ:\n")
        result_text.insert(END, f"{ratio}\n\n")

        result_text.insert(END, f"Limit of ratio as n → ∞:\n")
        result_text.insert(END, f"lim(n→∞) |aₙ₊₁ / aₙ| = {limit_value}\n\n")

        result_text.insert(END, "─" * 60 + "\n")
        result_text.insert(END, "CONCLUSION:\n")
        result_text.insert(END, "─" * 60 + "\n")

        if limit_value == sp.oo or limit_value == -sp.oo:
            result_text.insert(END, "Limit = ∞\n")
            result_text.insert(END, "Series DIVERGES (by Ratio Test)\n", "divergent")
        elif limit_value.is_number:
            limit_float = float(limit_value.evalf())
            result_text.insert(END, f"Limit = {limit_float:.6f}\n")

            if limit_float < 1:
                result_text.insert(END, "Limit < 1\n")
                result_text.insert(END, "Series CONVERGES (by Ratio Test)\n", "convergent")
            elif limit_float > 1:
                result_text.insert(END, "Limit > 1\n")
                result_text.insert(END, "Series DIVERGES (by Ratio Test)\n", "divergent")
            else:
                result_text.insert(END, "Limit = 1\n")
                result_text.insert(END, "Ratio Test is INCONCLUSIVE\n", "unclear")
                result_text.insert(END, "Other convergence tests are required\n")
        else:
            result_text.insert(END, f"Limit = {limit_value}\n")
            result_text.insert(END, "Could not calculate numeric value of the limit\n", "unclear")

        result_text.insert(END, "\n" + "═" * 60 + "\n")

        result_text.tag_config("convergent", foreground="green", font=("Helvetica", 12, "bold"))
        result_text.tag_config("divergent", foreground="red", font=("Helvetica", 12, "bold"))
        result_text.tag_config("unclear", foreground="orange", font=("Helvetica", 12, "bold"))

    except Exception as e:
        result_text.delete(1.0, END)
        result_text.insert(END, f"Calculation Error:\n{str(e)}\n\n")
        result_text.insert(END, "Please check the validity of the input expression.")


# --- UI Layout ---
main_container = Frame(root)
main_container.pack(fill=BOTH, expand=True, pady=10, padx=10)

fraction_frame = Frame(main_container)
fraction_frame.pack(side=LEFT, padx=20, pady=20, fill=Y)

Label(fraction_frame, text="Enter fraction:", font=("Helvetica", 14)).pack(pady=10)

input_frame = Frame(fraction_frame)
input_frame.pack()

entry_num = Entry(input_frame, width=15, font=("Helvetica", 18), justify='center')
entry_num.grid(row=0, column=0, padx=5)
slash_label = Label(input_frame, text=("-" * 25), font=("Helvetica", 20, "bold"))
slash_label.grid(row=1, column=0)
entry_den = Entry(input_frame, width=15, font=("Helvetica", 18), justify='center')
entry_den.grid(row=2, column=0, padx=5)

actions_frame = Frame(main_container, bg="#f0f0f0", relief=GROOVE, borderwidth=2)
actions_frame.pack(side=LEFT, fill=Y, padx=10)

Label(actions_frame, text="Special Actions:", bg="#f0f0f0", font=("Helvetica", 12, "bold")).pack(pady=10)

btn_fact = Button(actions_frame, text="n! (Factorial)", command=apply_factorial, width=20)
btn_fact.pack(pady=5, padx=10)

power_frame = Frame(actions_frame, bg="#f0f0f0")
power_frame.pack(pady=5, padx=10)
power_entry = Entry(power_frame, width=5)
power_entry.pack(side=LEFT)
btn_power = Button(power_frame, text="^n (Power)", command=apply_power)
btn_power.pack(side=LEFT)

btn_sqrt = Button(actions_frame, text="√ (Root)", command=apply_sqrt, width=20)
btn_sqrt.pack(pady=5, padx=10)

root_power_frame = Frame(actions_frame, bg="#f0f0f0")
root_power_frame.pack(pady=5, padx=10)
root_power_entry = Entry(root_power_frame, width=5)
root_power_entry.pack(side=LEFT)
btn_root_power = Button(root_power_frame, text="N-th Root", command=apply_root_power)
btn_root_power.pack(side=LEFT)

analyze_button = Button(actions_frame, text="Analyze Series", command=analyze_dalamber,
                        bg="#4CAF50", fg="white", font=("Helvetica", 12, "bold"), width=20)
analyze_button.pack(pady=20, padx=10)

result_frame = Frame(main_container, relief=GROOVE, borderwidth=2)
result_frame.pack(side=RIGHT, fill=BOTH, expand=True, padx=10)

Label(result_frame, text="Analysis Result:", font=("Helvetica", 14, "bold")).pack(pady=10)

result_text = Text(result_frame, width=70, height=30, font=("Courier", 11), wrap=WORD)
result_text.pack(pady=10, padx=10, fill=BOTH, expand=True)

scrollbar = Scrollbar(result_frame, command=result_text.yview)
scrollbar.pack(side=RIGHT, fill=Y)
result_text.config(yscrollcommand=scrollbar.set)


def exit_app():
    root.destroy()


exit_button = Button(root, text="Exit (Esc)", command=exit_app)
exit_button.pack(side=BOTTOM, pady=20)

root.bind("<Escape>", lambda event: exit_app())

root.mainloop()