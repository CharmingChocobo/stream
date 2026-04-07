# Configuration file for the Sphinx documentation builder.

project = 'streamsim'
copyright = '2026, Fenna Feenstra'
author = 'Fenna Feenstra'
release = '0.1'

import os
import sys

# Point to streamsim/ (the parent of src/)
sys.path.insert(0, os.path.abspath('../../'))
#sys.path.insert(0, os.path.abspath('../../streamsim'))

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',  # For Google/NumPy style docstrings
    'sphinx.ext.intersphinx',
]
html_theme = 'sphinx_rtd_theme'

html_theme_options = {
    'collapse_navigation': True,  # Zet dit op True om alles ingeklikt te starten
    'navigation_depth': 4,        # Hoe diep de menu's mogen zijn (optioneel)
    'titles_only': False,         # Toon alleen titels of ook pagina's (optioneel)
}
html_sidebars = { '**': ['globaltoc.html', 'relations.html', 'sourcelink.html', 'searchbox.html'] }



