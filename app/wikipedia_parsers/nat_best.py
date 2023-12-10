from wikipedia_parsers.base import BaseParser


class NatBestParser(BaseParser):       
    def extract_authors(self, a):
        # print(a)
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
            
        # print(f"authors='{authors}'")
        # input()
        return authors
    
    def extract_parts(self, t):
        buffer = ''
        is_brackets_open = False
        is_quotas_open = False
        
        parts = []
        
        for i, c in enumerate(t):
            if c in ',—':
                if not is_quotas_open and not is_brackets_open:
                    parts.append(buffer)
                    buffer = ''
                else:
                    buffer += c
                    
            elif c == '«':
                if not is_brackets_open:
                    if buffer.strip()!='':
                        parts.append(buffer)
                    buffer = c
                    if not is_quotas_open:
                        is_quotas_open = True
                else:
                    buffer += c
                        
            elif c == '»':
                buffer += c
                if not is_brackets_open:                
                    if is_quotas_open:
                        is_quotas_open = False
                        parts.append(buffer)
                        buffer = ''
                
            elif c == '(':
                buffer += c
                if not is_quotas_open:
                    if not is_brackets_open:
                        is_brackets_open = True
                    # else:
                        # buffer += c
                # else:
                    # buffer += c
                    
            elif c == ')':
                buffer += c
                if is_brackets_open:
                    is_brackets_open = False
            
            else:
                buffer += c
                
        if buffer.strip()!='':
            parts.append(buffer)
        
        parts = [self.clr(p) for p in parts if self.clr(p) != '']
        return parts
        
    def extract_book(self, t):
        book_author, book_title, book_details = '', '', ''
        
        parts = self.extract_parts(t)
            
        if len(parts) == 2:
            book_author = parts[0]
            book_title = parts[1] 
            book_details = ''        
        elif len(parts) == 3:
            book_author = parts[0]
            book_title = parts[1] 
            book_details = parts[2]
        elif len(parts)> 3:
            i = 0
            while i < len(parts) and not (parts[i][0] == '«' and parts[i][-1] == '»'):
                i+=1
            book_author = ", ".join(parts[:i])
            book_title = parts[i] 
            book_details = ", ".join(parts[i+1:])
        else:
            print(f"WARNING: extra parts {len(parts)}: {parts}")
                
        book_title, book_details = self.extract_book_title(book_title, book_details)
        book_author = self.extract_authors(book_author)
        book_author = list(map(lambda a: {"details": a["details"].strip().replace('  ','') if "details" in a else "", "name":a["name"].strip().replace('  ','').replace('ё','е')}, book_author))
        
        return book_author, self.clr(book_title), self.clr(book_details)
 
