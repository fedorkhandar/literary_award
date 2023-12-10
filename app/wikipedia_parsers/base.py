import codecs
import os
from dataclasses import dataclass
from typing import List, Any, Dict, Union, Tuple
from abc import abstractmethod, ABC
import orjson
import requests
from bs4 import BeautifulSoup

from config.config import settings

class BaseParser(ABC):
    """
    Base class for parsers used to extract data from Wikipedia pages.

    Attributes:
    - year1 (int): The starting year for data extraction.
    - year2 (int): The ending year for data extraction.
    - template (str): The URL template for the Wikipedia page.
    - cats (Dict[str, int]): A dictionary mapping category names to scores.
    - prefix (str): The prefix used for file names.
    - cache_fname (str): The file name for caching the page data.
    - result_fname (str): The file name for storing the extracted data.
    - table_fname (str): The file name for storing the table data.
    - results (Dict[str, Any]): The extracted data.

    Methods:
    - __init__: Initializes the BaseParser object.
    - get_year_page: Retrieves the HTML content of a Wikipedia page for a specific year.
    - extract_parts: Abstract method for extracting parts from a string.
    - extract_authors: Abstract method for extracting authors from a string.
    - extract_book: Abstract method for extracting book details from a string.
    - save: Saves the extracted data to a file.
    - extract_data: Extracts data from the Wikipedia pages for the specified range of years.
    - calc_table: Calculates the table data based on the extracted results.
    - save_table: Saves the table data to a file.
    - clr: Static method for cleaning up a string.
    - extract_book_title: Static method for extracting the book title and details from a string.
    - process: Executes the data extraction, saving, table calculation, and table saving steps.
    """
    year1: int
    year2: int
    template: str
    cats: Dict[str, int]
    prefix: str
    cache_fname: str
    result_fname: str
    table_fname: str
    results: Dict[str, Any]
    
    def __init__(
        self, 
        *,     
        year1: int,
        year2: int,
        template: str,
        cats: List[str],
        prefix: str
    ) -> None:
        """
        Initializes the BaseParser object.

        Parameters:
        - year1 (int): The starting year for data extraction.
        - year2 (int): The ending year for data extraction.
        - template (str): The URL template for the Wikipedia page.
        - cats (List[str]): The list of category names.
        - prefix (str): The prefix used for file names.
        """
        self.year1 = year1
        self.year2 = year2
        self.template = template
        self.cats = cats
        self.prefix = prefix
        self.cache_fname = settings.CACHE_FOLDER + "/" + self.prefix + '_cache.json'
        self.result_fname = settings.RESULT_FOLDER + "/" + self.prefix + '_awards.json'
        self.table_fname = settings.RESULT_FOLDER + "/" + self.prefix + '_table.csv'
        self.results = []  
    
    def get_year_page(self, year: Union[int, str]) -> str:
        """
        Retrieves the HTML content of a Wikipedia page for a specific year.

        Parameters:
        - year (int or str): The year for which to retrieve the page.

        Returns:
        - str: The HTML content of the Wikipedia page.
        """
        if isinstance(year, int):
            year = str(year)
            
        pdata = {}
        
        if not os.path.exists(settings.CACHE_FOLDER):
            os.makedirs(settings.CACHE_FOLDER, exist_ok=True)
        
        if os.path.exists(self.cache_fname):
            with open(self.cache_fname, "rb") as fin:
                jdata = fin.read()
            if jdata: 
                pdata = orjson.loads(jdata)
            
        if not pdata or not year in pdata:
            url = self.template.replace('xxxx', year)
            try:
                response = requests.get(url)
                response.encoding = 'utf-8'
                pdata[year] = response.text
            except Exception as E:
                print(f"Can't get page: {E}")
                
        with open(self.cache_fname, "wb") as fout:
            fout.write(orjson.dumps(pdata))
        
        return pdata[year]
        
    @abstractmethod
    def extract_parts(self, a: str) -> List[str]:
        """
        Abstract method for extracting parts from a string.

        Parameters:
        - a (str): The string to extract parts from.

        Returns:
        - Any: The extracted parts.
        """
        pass
        
    @abstractmethod
    def extract_authors(self, a: str) -> List[str]:
        """
        Abstract method for extracting authors from a string.

        Parameters:
        - a (str): The string to extract authors from.

        Returns:
        - Any: The extracted authors.
        """
        pass
    
    @abstractmethod
    def extract_book(self, t: str) -> Tuple[List[str], str, str]:
        """
        Abstract method for extracting book details from a string.

        Parameters:
        - t (str): The string to extract book details from.

        Returns:
        - Any: The extracted book details.
        """
        pass
           
    def save(self):
        """
        Saves the extracted data to a file.
        """
        if not os.path.exists(self.result_fname):
            os.makedirs(settings.RESULT_FOLDER, exist_ok=True)
        with open(self.result_fname, "wb")as fout:
            fout.write(orjson.dumps(self.results))
    
    def extract_data(self) -> None:
        """
        Extracts data from the Wikipedia pages for the specified range of years.
        """
        self.results = []
        for year in range(self.year1, self.year2+1):
            data = self.get_year_page(year)
            soup = BeautifulSoup(data, 'html.parser')
            
            headline_winners = soup.find_all('span', class_='mw-headline')
            for headline in headline_winners:
                if headline['id'] in self.cats:
                    hp = headline.parent
                    ne = hp.next_sibling
                    while ne is not None and ne.name != "ol":
                        ne = ne.next_sibling
                    if ne is not None:
                        titles = [t.text for t in ne.find_all('li')]
                    
                        for t in titles:
                            book_authors, book_title, book_details = self.extract_book(t)
                            record = {
                                "award":self.prefix,
                                "year":year,
                                "category": headline['id'],
                                "src": t,
                                "authors": book_authors,
                                "title": book_title,
                                "details": book_details
                            }
                            self.results.append(record)
    
    def calc_table(self) -> None:   
            """
            Calculates the table data based on the extracted results.

            Returns:
                None
            """
            table = {}
            
            for record in self.results:
                for author in record['authors']:
                    name1 = author['name']
                    name2 = " ".join(name1.split(' ')[::-1])
                    score = self.cats[record['category']]
                    year = record['year']
                    
                    if name1 in table:
                        if year in table[name1]:
                            table[name1][year] = max(table[name1][year], score)
                        else:    
                            table[name1][year] = score
                    elif name2 in table:
                        if year in table[name2]:
                            table[name2][year] = max(table[name2][year], score)
                        else:    
                            table[name2][year] = score
                    else:
                        table[name1] = {year: score}
            
            stats = {}
            for name, row in table.items():
                p = len(list(filter(lambda x: x == 10, list(row.values()))))
                s = len(list(filter(lambda x: x == 5, list(row.values()))))
                l = len(list(filter(lambda x: x == 3, list(row.values()))))
                stats[name] = {}
                stats[name]['prize'] = p
                stats[name]['short'] = s
                stats[name]['long'] = l
                
            self.table = {
                "table":table,
                "stats":stats
            }
                    
    def save_table(self):
        """
        Saves the table data to a file.
        """
        with codecs.open(self.table_fname, "w", "cp1251") as fout:
            header = "author;prize;short;long;;"
            header += ";".join([str(year) for year in range(self.year1, self.year2+1)])
            header += ";;"
            header += ";".join([str(year) for year in range(self.year1, self.year2+1)])
            print(header, file=fout)
            
            rows = []
            for name, results in self.table['table'].items():
                row = name +";"+ str(self.table['stats'][name]['prize']) + ";" + str(self.table['stats'][name]['short']) + ";" + str(self.table['stats'][name]['long']) + ";;"
                
                for year in range(self.year1, self.year2+1):
                    if year in results:
                        row += str(results[year]) + ";"
                    else:
                        row += "0;"
                row += ";"        
                cum_s = 0
                for year in range(self.year1, self.year2+1):
                    if year in results:
                        cum_s += results[year]
                    row += str(cum_s) + ";"
                rows.append(row)
                
            for row in sorted(rows, key = lambda row: -int(row[:-1].split(";")[-1])):
                print(row, file=fout)
                
    @staticmethod
    def clr(s: str)-> str:
        """
        Static method for cleaning up a string.

        Parameters:
        - s (str): The string to clean up.

        Returns:
        - str: The cleaned up string.
        """
        t = s.replace(u'\xa0', u' ')
        while len(t)> 0 and t[0] in '.,':
            t = t[1:]
        while len(t)> 0 and t[-1] in '.,':
            t = t[:-1]
        t = t.strip()
        return t
    
    @staticmethod
    def extract_book_title(book_title: str, book_details: str) -> Tuple[str, str]:
        """
        Static method for extracting the book title and details from a string.

        Parameters:
        - book_title (str): The string containing the book title.
        - book_details (str): The string containing additional book details.

        Returns:
        - Tuple[str, str]: The extracted book title and details.
        """
        a = book_title.find('«')
        b = book_title.find('»')
        ap = book_title[:a].strip()
        bp = book_title[b+1:].strip()
        if len(ap)>0: book_details +=", "+ap
        if len(bp)>0: book_details +=", "+bp
        book_title = book_title[a+1:b]
        return book_title, book_details
    
    def process(self):
        """
        Executes the data extraction, saving, table calculation, and table saving steps.
        """
        self.extract_data()
        self.save()
        self.calc_table()
        self.save_table()