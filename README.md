# PDF → LaTeX Translator

Turn PDFs (including math) into clean **LaTeX** with equations and simple **TikZ** diagrams — right in your browser.

**Live app:** https://latextrans.pocafup.com/app/

---

## Quick Start

1. **Open**: Go to **https://latextrans.pocafup.com/app/**
2. **Choose your model backend** under **Engine & Model Settings**:
   - **OpenAI (cloud)** — uses your OpenAI API key
   - **Ollama (local)** — for locally hosted models (if available)
   - **Custom** — any compatible API endpoint
3. If you are using **OpenAI**, you’ll need an API key.  
   👉 [How to get an OpenAI API Key](#how-to-get-an-openai-api-key)
4. **Enter credentials**:
   - **Base URL**:
     - OpenAI: `https://api.openai.com/v1`
     - Ollama: `http://localhost:11434` (only if your server exposes it)
     - Custom: paste your endpoint
   - **Model**:
     - Examples: `gpt-4o`, `gpt-4.1-mini`, `llama3.1:8b`
   - **API Key**:
     - OpenAI: paste your key (starts with `sk-…`)
     - Ollama: any non-empty value is fine (e.g., `ollama`)
     - Custom: follow your provider’s instructions
5. **Upload your PDF** in the **PDF & Translation Settings** section.
6. **Generate**: click **Generate** and wait for the results.
7. **Download**: grab `master.tex` (and `master.pdf` if compiled) from the provided buttons.

## Tips for Best Results

- **Clear scans**: If your PDF is scanned or low-quality, OCR-like reconstruction may be imperfect. Clean, selectable text works best.
- **Math & text**: The app tries to keep prose outside math environments and wraps URLs/DOIs properly to reduce LaTeX warnings.
- **Pages**: Process a few pages first to validate formatting, then run larger ranges.
- **Compile setting**: If you only need LaTeX, you can disable “Compile to PDF” and use your own LaTeX toolchain later.

---

## Output Files

- **`master.tex`**: a combined LaTeX document with:
  - Unicode-friendly font setup
  - Page content stitched together
  - Equations converted to LaTeX
  - Diagrams approximated with TikZ where possible
- **`page_XXX.tex`**: per-page LaTeX (useful for manual tweaks)
- **`master.pdf`** (optional): the compiled PDF if “Compile to PDF” is enabled

---

## How to Get an OpenAI API Key

1. **Sign in to OpenAI**
   - Go to [https://platform.openai.com](https://platform.openai.com)
   - Log in with your OpenAI account (or create one if you don’t have it).

2. **Go to API Keys page**
   - Click your profile icon (top-right corner).
   - Select **View API keys** from the menu.
   - Or directly visit: [https://platform.openai.com/account/api-keys](https://platform.openai.com/account/api-keys)

3. **Create a new key**
   - Click **Create new secret key**.
   - Give it a name (e.g., “Latex Translator”).
   - Copy the generated key (it starts with `sk-...`).

4. **Keep it safe**
   - Paste the key into the **API Key** field in the translator app:  
     👉 [https://latextrans.pocafup.com/](https://latextrans.pocafup.com/)  
   - Do **not** share your key — it gives access to your usage/billing.

5. **Manage or revoke keys**
   - If a key is exposed or you no longer need it, you can revoke it anytime from the same API Keys page.

