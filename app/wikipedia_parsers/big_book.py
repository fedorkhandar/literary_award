from wikipedia_parsers.base import BaseParser


class BigBookParser(BaseParser):       
    def extract_authors(self, a):
        authors = []
        author = {}
        buffer = ''
        brackets_are_open = False
        for i, c in enumerate(a):
            if c == '(' and not brackets_are_open:
                brackets_are_open = True
                author['name'] = buffer
                buffer = ''
            elif c == ')' and brackets_are_open:
                brackets_are_open = False
                author['details'] = buffer
                buffer = ''
            elif c == ',':
                if brackets_are_open:
                    buffer = ''
                else:
                    author['name'] = buffer
                    authors.append(author)
                    author = {}
                    buffer = ''
            else:
                buffer += c
        
        if len(author)>0:
            authors.append(author)
            
        if len(buffer.strip()) > 0:
            author = {}
            author['name'] = buffer
            authors.append(author)
            
        return authors
    
    def extract_parts(self, t):
        return [p.strip() for p in t.split('—')]
        
    def extract_book(self, t):
        book_author, book_title, book_details = '', '', ''
        
        parts = self.extract_parts(t)
        
        if len(parts) == 3:
            if parts[0].find('Рукопись') == 0:
                book_details = parts[0]
                book_author = parts[1]
                book_title = parts[2]
            else:
                book_author = parts[0]
                book_title = parts[1]
                book_details = parts[2]
        elif len(parts) == 2:
            if parts[0].find('Рукопись') == 0:
                book_details = parts[0]
                book_title = parts[1] 
                book_author = ''
            else:
                book_author = parts[0]
                book_title = parts[1]
                book_details = ''
        elif len(parts) == 1:
            a = parts[0].find('«')
            b = parts[0].find('»')
            book_author = parts[0][:a].strip()
            book_title = parts[0][a+1:b]
            book_details = parts[0][b+1:].strip()
        else:
            print(f"WARNING: {self.prefix}: extra parts {len(parts)}: {parts}")


        book_title, book_details = self.extract_book_title(book_title, book_details)
        book_authors = self.extract_authors(book_author)
        book_authors = list(map(lambda a: {"details": a["details"].strip().replace('  ','') if "details" in a else "", "name":a["name"].strip().replace('  ','').replace('ё','е')}, book_authors))
        
        return book_authors, self.clr(book_title), self.clr(book_details)
 
