Questions under development
===========================

1. How should gui.set() work?
===============================

Q. When gui.set() is called, should all widget value be initialized with defaults before setting with argument?

A. Yes.

2. How should gui.clear() work?
================================

Q. Does gui.clear() 'erase contents of widgets' or 'fill with default value?'

A. 'fill with default value' looks better. From Q1, clear() is almost same as set({})

3. How should gui.get() work?
================================

Q. Does gui.get() starts at 'd={} (NULL member)' or 'd=default_value'? 

A. ...

