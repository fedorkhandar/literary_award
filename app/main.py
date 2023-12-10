import wikipedia_parsers as wp


def main():    
    bb = wp.BigBookParser(
        year1=2006, 
        year2=2023,
        prefix = 'bigbook',
        template = "https://ru.wikipedia.org/wiki/%D0%A1%D0%BF%D0%B8%D1%81%D0%BE%D0%BA_%D0%BD%D0%BE%D0%BC%D0%B8%D0%BD%D0%B0%D0%BD%D1%82%D0%BE%D0%B2_%D0%BD%D0%B0_%D0%BF%D1%80%D0%B5%D0%BC%D0%B8%D1%8E_%C2%AB%D0%91%D0%BE%D0%BB%D1%8C%D1%88%D0%B0%D1%8F_%D0%BA%D0%BD%D0%B8%D0%B3%D0%B0%C2%BB_xxxx_%D0%B3%D0%BE%D0%B4%D0%B0",
        cats = {'Победители':10, 'Список_финалистов':5, 'Длинный_список':1}
    )
    bb.process()

    nb = wp.NatBestParser(
        year1=2001, 
        year2=2022,
        prefix = 'natbest',
        template = "https://ru.wikipedia.org/wiki/%D0%A1%D0%BF%D0%B8%D1%81%D0%BE%D0%BA_%D0%BD%D0%BE%D0%BC%D0%B8%D0%BD%D0%B0%D0%BD%D1%82%D0%BE%D0%B2_%D0%BD%D0%B0_%D0%BF%D1%80%D0%B5%D0%BC%D0%B8%D1%8E_%C2%AB%D0%9D%D0%B0%D1%86%D0%B8%D0%BE%D0%BD%D0%B0%D0%BB%D1%8C%D0%BD%D1%8B%D0%B9_%D0%B1%D0%B5%D1%81%D1%82%D1%81%D0%B5%D0%BB%D0%BB%D0%B5%D1%80%C2%BB_xxxx_%D0%B3%D0%BE%D0%B4%D0%B0",
        cats = {'Победитель':10, 'Короткий_список':5, 'Длинный_список':1}
    )
    nb.process()
     

if __name__ == "__main__":
    main()