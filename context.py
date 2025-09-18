class Context:
    def __init__(self):
        self.pages = 0
        self.translated_page = 1

    def setPages(self,pages):
        self.pages = pages
    
    def setTranslatedPage(self,translated_page):
        self.translated_page = translated_page
    
    def getPages(self) -> int:
        return self.pages
    
    def getTranslatedPage -> int:
        return self.translated_page


