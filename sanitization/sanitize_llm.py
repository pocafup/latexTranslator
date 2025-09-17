import re
def sanitize_for_xelatex(tex: str) -> str:
    # Remove any CJK environments (if the model ignores instructions)
    tex = re.sub(r'\\begin\{CJK\}.*?\\end\{CJK\}', '', tex, flags=re.S|re.I)
    tex = re.sub(r'\\begin\{CJK\*?\}.*?\\end\{CJK\*?\}', '', tex, flags=re.S|re.I)
    tex = re.sub(r'\\end\{CJK\*?\}', '', tex, flags=re.I)
    tex = re.sub(r'\\begin\{CJK\*?\}(?:\[[^\]]*\])?(?:\{[^}]*\}){0,3}', '', tex, flags=re.I)
    # Remove package lines if they slip in
    tex = re.sub(r'\\usepackage(?:\[[^\]]*\])?\{CJK\*?u?t?f?8?\}', '', tex, flags=re.I)
    return tex

def latex_escape(text: str) -> str:
    # Minimal escaping for common special chars in LaTeX titles
    repl = {
        "\\": r"\textbackslash{}", 
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    for k, v in repl.items():
        text = text.replace(k, v)
    return text

