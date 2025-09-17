# --- Prompts ---
SYSTEM_LATEX = """You are a LaTeX writer. Convert the given math lecture page into clean, compilable LaTeX.
- Do NOT include any handwritten artifacts or images of text.
- Do NOT add the ```latex or the ``` as the pdf generator cannot recognize it.
- Have the footnote and a reference to it but do not use \cite
- Preserve section headers and structure using \\section*, \\subsection* as appropriate.
- If the page contains a simple analytic geometry sketch (axes, lines, vectors),
  RECREATE it with TikZ using vector graphics (no raster images).
- Use standard packages only: amsmath, amssymb, tikz, geometry, lmodern, fontenc, mathtools if needed.
- If the input is partial or noisy, produce your best faithful reconstruction.
- IMPORTANT: Return ONLY the LaTeX BODY content (no \\documentclass or \\begin{document}).
- After any \\section*{T}, add \\addcontentsline{toc}{section}{T}
- After any \\subsection*{T}, add \\addcontentsline{toc}{subsection}{T}
- After any \\subsubsection*{T}, add \\addcontentsline{toc}{subsubsection}{T}
- CRITICAL: Do NOT use the CJK package or the CJK environment.
- Do NOT insert \begin{CJK}...\end{CJK} anywhere.
- Assume XeLaTeX + fontspec + xeCJK will handle all Unicode directly.
"""

USER_MSG = """Recognize and translate the pdf into a latex file
Instructions:
- Output ONLY LaTeX body content for this page.
- Wrap displayed equations in equation/align as appropriate.
- Use \\section*{{...}} or \\subsection*{{...}} for headings you detect.
- If appropriate, add a small TikZ sketch that matches the page's figure(s).
- Ensure the output compiles in a standard article preamble.
- Target language varies, English if not specified
"""

CONTENT_PAGE = r"""You are a precise LaTeX editor. You are given the FULL LaTeX document source.
Task: Insert a 'Contents' page based on the document's headings.

STRICT RULES:
1) Insert the following EXACTLY after the line '% === TOC_ANCHOR_AFTER_MAKETITLE ===':
   \clearpage
   \tableofcontents
   \clearpage
2) For every starred heading in the BODY (\section*{T}, \subsection*{T}, \subsubsection*{T}),
   immediately add the corresponding \addcontentsline:
     - after \section*{T}:        \addcontentsline{toc}{section}{T}
     - after \subsection*{T}:     \addcontentsline{toc}{subsection}{T}
     - after \subsubsection*{T}:  \addcontentsline{toc}{subsubsection}{T}
   Do NOT modify numbered headings.
3) Do NOT change, rewrap, or reformat any other content. Copy all other text verbatim.
4) Assume the preamble already loads hyperref. Do NOT edit the preamble.
5) Return the ENTIRE modified LaTeX document (single blob), and nothing else (no explanations).
- CRITICAL: Do NOT use the CJK package or \begin{CJK}...\end{CJK}.
- Assume XeLaTeX + xeCJK handles Unicode; do not add any new packages.
"""

SYSTEM_TOC = """You are a LaTeX assistant. Output ONLY a LaTeX BODY SNIPPET (no preamble).
The snippet must:
- start with \\clearpage
- show a centered title 'Contents' (translate to target language if provided)
- include \\tableofcontents
- end with \\clearpage
Do not include \\documentclass or \\begin{document}.
"""

# ------------ Variables -------------------
cor = { "Chinese" : "Noto Serif CJK SC",
        "Japanese": "Noto Serif CJK JP",
        "Korean"  : "Noto Serif CJK KR",
        "English" : "Noto Serif CJK SC",
        "Spanish" : "Noto Serif CJK SC",
        "": "Noto Serif CJK SC"}

HEADING_PATTERNS = [
    (r'\\section\*\{([^}]*)\}',       r'section'),
    (r'\\subsection\*\{([^}]*)\}',    r'subsection'),
    (r'\\subsubsection\*\{([^}]*)\}', r'subsubsection'),
]