from matplotlib.pyplot import xlabel
import requests
import pytesseract
import pdf2image
from pdf2image import convert_from_path
import PyPDF2
import io
import gzip
from nltk.tokenize import sent_tokenize
import re

class ScrapPDFData:
    def __init__(self,URL,invoice_ID):
        self.URL = URL+str(invoice_ID)
        self.arr = []
        self.final = []
        self.unwanted_chars = [',', ':', '£']
        self.invoice_ID = invoice_ID
        
    def splitToLines(self):
        # path to poppler (windows binary installation)
        poppler_path = r'C:\\Program Files\\poppler-0.68.0\\bin'
        # Path OCR ( Windows binary installation)
        pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
        pdf = requests.get(self.URL, stream=True)
        images = pdf2image.convert_from_bytes(pdf.content)
        data = []
        for image in images:
             page = pytesseract.image_to_pdf_or_hocr(image, extension='pdf')
             pdf = PyPDF2.PdfFileReader(io.BytesIO(page))
             data.append(pdf.getPage(0).extractText())
             #print(pdf.getPage(0).extractText())
        segmented_data = data[0].splitlines()
        return segmented_data

    def get_items(self,segmented_data):
        index_tracking=[]
        for data in segmented_data:
            if self.has_price(data):
                index_tracking.append(segmented_data.index(data))
        
        result=self.get_price_with_items(segmented_data[index_tracking[0] -
                                                1: index_tracking[-1]])
        
        return result


    def has_price(self,inputString):
        return any(self.isMoney(i) for i in inputString.split())


    def isMoney(self,num):
        

        for sc in self.unwanted_chars:
            num= num.replace(sc,'')
            print(num)
        if re.match("^(£[0-9]+[\, ])?([0-9]+[\., ])+([0-9]{2})+", num):
            return True
        else:
            return False


    def has_numbers(self,inputString):
        return bool(re.search(r'\d', inputString))



    def get_price_with_items(self,received_result):
        j=0
        try:
            for i in range(j,len(received_result)):
                if self.has_price(received_result[i]):
                    self.arr.append(received_result[i])
                    j=i+1
                    while not self.has_price(received_result[j]):
                        self.arr.append(received_result[j])
                        j=j+1
                    self.final.append(received_result[i:j])
            
            return [' '.join(sentence) for sentence in self.final]
        except IndexError:
            result = self.data_structuring([' '.join(sentence)
                                  for sentence in self.final])
            return result
    
    def data_structuring(self,semi_clean_data):
        
        data=[s for s in semi_clean_data if 'VAT' not in s]
        data = [s for s in data if 'Subtotal' not in s]
        #print(data)
        total=[]
        for sent in data:
            numbers = []
            items = []
            
            for word in sent.split():
                if(self.isMoney(word)):
                        numbers.append(word)
                else:
                        items.append(word)
           
            for word in items:
                if '£' in word:
                    numbers.append(word)
            

            total.append((self.invoice_ID,' '.join(items), numbers[-1]))
        

        
        #extra cleaning step

        
                    

        return total
            

# initialize the Scraper
scraper = ScrapPDFData(
    'http://search.electoralcommission.org.uk/Api/Spending/Invoices/', 66755)

print(scraper.get_items(scraper.splitToLines())) # simple print to check the output



