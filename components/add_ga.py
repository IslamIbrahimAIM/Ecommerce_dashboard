# from bs4 import BeautifulSoup
# import pathlib
# import shutil
# import streamlit as st


# GA_ID = "Google_Analytics"
# GA_SCRIPT = """

# <!-- Google tag (gtag.js) -->
# <script async src="https://www.googletagmanager.com/gtag/js?id=G-CPK41EM5P3"></script>
# <script>
#   window.dataLayer = window.dataLayer || [];
#   function gtag(){dataLayer.push(arguments);}
#   gtag('js', new Date());

#   gtag('config', 'G-CPK41EM5P3');
# </script>
#  """
# def inject_ga():
#     index_path = pathlib.Path(st.__file__).parent / "static" / "index.html"
#     soup = BeautifulSoup(index_path.read_text(), features="html.parser")
#     if not soup.find(id=GA_ID):
#         bck_index = index_path.with_suffix('.bck')
#         if bck_index.exists():
#             shutil.copy(bck_index, index_path)
#         else:
#             shutil.copy(index_path, bck_index)
#         html = str(soup)
#         new_html = html.replace('<head>', '<head>\n' + GA_SCRIPT)
#         index_path.write_text(new_html)
# inject_ga()

import streamlit as st
import streamlit.components.v1 as components

GA_SCRIPT = """
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-CPK41EM5P3"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-CPK41EM5P3');
</script>
"""

def inject_ga():
    components.html(GA_SCRIPT, height=0, width=0)