
import subprocess, os
master_path = "/latextranslator/translated_output/master.tex"

def compile_pdf(tex_path: str, engine: str = "xelatex", passes: int = 2) -> None:
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
        if proc.returncode != 0:
            raise subprocess.CalledProcessError(proc.returncode, proc.args, output=proc.stdout)
    for i in range(passes): 
        run_once()
try:
    compile_pdf(master_path, engine="xelatex")
except Exception as e:
    print(e)