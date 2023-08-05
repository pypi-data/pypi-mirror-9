Gmail Filter for `Chrome Edit Server <https://github.com/coddingtonbear/chrome-edit-server>`_
=============================================================================================

Converts a (tiny) subset of HTML -> text and back.
Empirically this should be enough to edit "plain text"
in gmail's new compose window, but it's somewhat fragile.

>>> c = GmailCodec()
>>> content = ("3<div><br></div><div><br></div><div><br></div><div>"
...            "2</div><div><br></div><div><br></div><div>"
...            "1</div><div><br></div><div>"
...            "0</div><div>"
...            "EOF</div>")

>>> plaintext = c.decode(content)
>>> print plaintext
3
<BLANKLINE>
<BLANKLINE>
<BLANKLINE>
2
<BLANKLINE>
<BLANKLINE>
1
<BLANKLINE>
0
EOF
>>> html = c.encode(plaintext)
>>> print html
3<br><br><br><br>2<br><br><br>1<br><br>0<br>EOF


Also, for entities and preserving of unknown tags:

>>> print c.encode(c.decode('&lt;<foo x="1">foo!</foo>'))
&lt;<foo x="1">foo!</foo>

Entities:

>>> print repr(c.decode(" &nbsp;"))
'  '
>>> print repr(c.encode(c.decode(" &nbsp;")))
'&nbsp; '

Tabs:

>>> print repr(c.encode('\t'))
'&nbsp;&nbsp;&nbsp; '

Spacing:

>>> print c.encode('>    1')
&gt; &nbsp;&nbsp; 1


Requirements
------------

* `chrome-edit-server <https://github.com/coddingtonbear/chrome-edit-server>`_

Installation
------------

Install from PyPI by running::

    pip install chrome-edit-server-gmail-filter

When you next use an "Edit server"-compatible chrome plugin (like "TextAid" or
"Edit With Emacs") from Gmail, this filter will be invoked automatically.

