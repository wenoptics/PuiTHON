# puithon (Python UI Framework)

A python UI framework that enables cross-platform compatibility, embraces web technologies and 
python language features.

## Install

```bash
python setup.py install
```

## Usage

```python
from puithon import Window, RuntimeManager

class MyWindow(Window):
    def page_uri(self):
        return self.html_to_data_uri("""
            <html>
            <body>
                <p>Hello PuiTHON</p>
            </body>
            </html>
        """)
```

See [`doc/Tutorial.md`](./doc/Tutorial.md) for a walk-thru tutorial.

Also, check [`./example`](./example/) for some snippets.

---
 
## Features

todo

 - [ ] Window Manager
 - [ ] |-- Messaging 
 - [ ] |---- frontend data binding
 - [ ] |---- messaging across windows
 
## Benefits

 - Decoupled `views`, easy migrate from _Platform Application_ -> _Web Application_ or vice versa.
 
 ## Todo
 
 - [x] Set Window size
 
 ## Roadmap
 
 - Initiative: A framework for easy gluing HTML based frontend with Python backend, for desktop-based applications.
 
 - Phrase 2: Python encapsulated HTML view components for modular platform specific frontend development, provide 
    decoupled view modules.
    
 - Phrase 3: A WYSIWYG editor for desktop GUI development.
 