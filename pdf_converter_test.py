
import subprocess, os
master_path = "/latextranslator/translated_output/master.tex"

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
            errors="ignore"
        )
        # Always echo the output so you can see warnings/errors
        print(proc.stdout)
        if proc.returncode != 0:
            # Re-raise with the captured log attached
            raise subprocess.CalledProcessError(proc.returncode, proc.args, output=proc.stdout)

    run_once()  # 1st pass
    run_once()  # 2nd pass
try:
    compile_pdf(master_path, engine="xelatex")
except Exception as e:
    print(e)