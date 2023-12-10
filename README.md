A template of the script downloading Literary Awards lists from various sources.

# To add a new source:
1. Add a file to wikipedia_parsers, e.g. `some_award.py` 
2. Edit this file: you should import BaseParser and implement a class with three methods:
```python
from wikipedia_parsers.base import BaseParser

class SomeAwardParser(BaseParser):
    def extract_authors(self, a):
        pass
    def extract_parts(self, t):
        pass
    def extract_book(self, t):
        pass
```

3. Do edit `__init__.py` in `wikipedia_parsers` -- ad this line:
```
from .some_award import SomeAwardParser
```

4. Declare an object of new class in `main()` and call `process()`:
```python
    nb = wp.SomeAwardParser(
        year1=2001, 
        year2=2022,
        prefix = 'someaward',
        template = "https://ru.wikipedia.org/wiki/%D0%A1%D0%BF%D0%B8%D1%81%D0%BE%D0%BA_%D0%BD%D0%BE%D0%BC%D0%B8%D0%BD%D0%B0%D0%BD%D1%82%D0%BE%D0%B2_%D0%BD%D0%B0_%D0%BF%D1%80%D0%B5%D0%BC%D0%B8%D1%8E_%C2%AB%D0%9D%D0%B0%D1%86%D0%B8%D0%BE%D0%BD%D0%B0%D0%BB%D1%8C%D0%BD%D1%8B%D0%B9_%D0%B1%D0%B5%D1%81%D1%82%D1%81%D0%B5%D0%BB%D0%BB%D0%B5%D1%80%C2%BB_xxxx_%D0%B3%D0%BE%D0%B4%D0%B0",
        cats = {'Победитель':10, 'Короткий_список':5, 'Длинный_список':1}
    )
    nb.process()
```
Notice! You have to declare points for various categories: `cats = {'Победитель':10, 'Короткий_список':5, 'Длинный_список':1}`

5. After the first run, the folder `cache` would contain cached data from Wikipedia. If you have to renew those -- just delete/rename files in the folder `cache`.
