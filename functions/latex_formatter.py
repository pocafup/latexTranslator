from sanitization.sanitize_llm import latex_escape
from constants.constants import cor
def make_master_preamble(title: str = "Translated Document", language: str = "English", ToC: bool = False) -> str:
    t = latex_escape(title)
    return r"""\documentclass[11pt]{article}
\usepackage[margin=1in]{geometry}
\usepackage{fontspec}
\usepackage{xeCJK}
\usepackage[english,spanish,es-noshorthands]{babel}
\usepackage{newunicodechar}
\usepackage{amsmath,amssymb,mathtools}
\newunicodechar{−}{\ensuremath{-}}
\usepackage{tikz}
\usepackage[hidelinks]{hyperref} % for clickable ToC links
""" + f"\\setCJKmainfont{{{cor[language]}}}\n" + r"""\defaultfontfeatures{Ligatures=TeX}
\setmainfont{Liberation Serif}
\setsansfont{Liberation Sans}
\setmonofont{Liberation Mono}
\setlength{\parskip}{0.6em}
\setlength{\parindent}{0pt}

\title{""" + t + r"""}
\date{}
\begin{document}
\maketitle
\setcounter{tocdepth}{2}
""" + r"""
\tableofcontents
\clearpage
""" if ToC else "\n"

def make_master_epilogue() -> str:
    return r"""\end{document}
"""
