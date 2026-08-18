"""Sphinx configuration for the local HTML edition."""

project = "数独を解こう"
language = "ja"

extensions = ["sphinx.ext.extlinks", "sphinx.ext.mathjax", "sphinxcontrib.bibtex"]
root_doc = "index"
source_suffix = {".rst": "restructuredtext"}

bibtex_bibfiles = ["bibliography/references.bib"]
bibtex_default_style = "unsrt"
bibtex_reference_style = "label"
# Each chapter owns a local bibliography whose numbering intentionally restarts at 1.
suppress_warnings = ["bibtex.duplicate_label"]

extlinks = {
    "repo-file": ("https://github.com/45deg/sudoku-book/blob/main/%s", "%s"),
    "repo-dir": ("https://github.com/45deg/sudoku-book/tree/main/%s", "%s"),
}

exclude_patterns = [
    ".agents/**",
    ".codex/**",
    ".uv-cache/**",
    ".venv/**",
    "AUTHORING.rst",
    "bibliography/generated/**",
    "build/**",
    "chapter-template.rst",
    "examples/**/README.rst",
]

html_theme = "furo"
html_title = project
html_baseurl = "https://45deg.github.io/sudoku-book/"
html_search_language = "ja"
templates_path = ["_templates"]
html_static_path = ["_static"]
html_css_files = ["book.css"]
html_copy_source = False
html_show_sourcelink = False
html_show_sphinx = False
html_use_index = False

html_theme_options = {
    "navigation_with_keys": True,
    "top_of_page_buttons": [],
    "light_css_variables": {
        "color-brand-primary": "#0072B2",
        "color-brand-content": "#0067A0",
        "font-stack": '"Hiragino Sans", "Yu Gothic", "Noto Sans JP", sans-serif',
        "font-stack--headings": '"Hiragino Sans", "Yu Gothic", "Noto Sans JP", sans-serif',
        "font-stack--monospace": 'ui-monospace, "SFMono-Regular", Consolas, monospace',
    },
    "dark_css_variables": {
        "color-brand-primary": "#56B4E9",
        "color-brand-content": "#7CCBEE",
    },
}

pygments_style = "friendly"
pygments_dark_style = "monokai"
