
import subprocess, os
master_path = "/Users/pocafup/latexTranslator/translated_output/master.tex"

def compile_pdf(tex_path: str, engine: str = "xelatex") -> None:
    tex_dir = os.path.dirname(os.path.abspath(tex_path)) or "."
    fname = os.path.basename(tex_path)

    def run_once():
        proc = subprocess.run(
            [engine, "-interaction=nonstopmode", fname],
            cwd=tex_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        # Always echo the output so you can see warnings/errors
        print(proc.stdout)
        if proc.returncode != 0:
            # Re-raise with the captured log attached
            raise subprocess.CalledProcessError(proc.returncode, proc.args, output=proc.stdout)

    run_once()  # 1st pass
    run_once()  # 2nd pass


def make_master_preamble(title: str = "Translated Document") -> str:
    t = latex_escape(title)
    return r"""\documentclass[11pt]{article}
\usepackage[margin=1in]{geometry}

% --- Unicode + multilingual ---
\usepackage{fontspec}   % Unicode fonts
\usepackage[english,spanish]{babel}
\usepackage{babel}      % Language/hyphenation for Latin scripts
\babelprovide[import, main]{english}
\babelprovide[import]{spanish}
\babeltags{es=spanish}

% --- CJK support (Chinese/Japanese/Korean) ---
\usepackage{xeCJK}      % Proper CJK line breaking/spacing

% Base Latin fonts (change to what you have installed)
\setmainfont{TeX Gyre Termes}   % Times-like
\setsansfont{TeX Gyre Heros}    % Helvetica/Arial-like
\setmonofont{TeX Gyre Cursor}   % Courier-like

% Base CJK font (Han)
\setCJKmainfont{FandolSong-Regular}   % Chinese serif
\setCJKsansfont{FandolHei-Regular}    % Chinese sans
\setCJKfamilyfont{jp}{HaranoAjiMincho}   % Japanese Mincho (Source Han Serif JP)
\setCJKfamilyfont{kr}{UnBatang}          % Korean serif (if missing, see Option B)

% Fallbacks by Unicode range (JP/KR)
\setCJKfallbackfamilyfont{rm}{Noto Serif CJK JP}[
  Range = {"3040-"309F, "30A0-"30FF} % Hiragana, Katakana
]
\setCJKfallbackfamilyfont{rm}{Noto Serif CJK KR}[
  Range = {"1100-"11FF, "3130-"318F, "AC00-"D7AF, "A960-"A97F, "D7B0-"D7FF}
]

\setCJKsansfont{Noto Sans CJK SC}
\setCJKfamilyfont{jp}{Noto Serif CJK JP}
\setCJKfamilyfont{kr}{Noto Serif CJK KR}

\newcommand{\jp}[1]{{\CJKfamily{jp}#1}}
\newcommand{\kr}[1]{{\CJKfamily{kr}#1}}

\defaultfontfeatures{Ligatures=TeX,Renderer=Harfbuzz}
\linespread{1.05}

\usepackage{amsmath,amssymb,mathtools}
\usepackage{tikz}
\usepackage{hyperref}

\setlength{\parskip}{0.6em}
\setlength{\parindent}{0pt}
\title{""" + t + r"""}
\date{}
\begin{document}
\maketitle
"""

try:
    compile_pdf(master_path, engine="xelatex")
except Exception as e:
    print(e)