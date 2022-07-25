import requests
import pytesseract
import pdf2image
import PyPDF2
import io
import re
import os
import pandas as pd
from src.config import invoices_base_url, default_path_to_csv, output_path

class Scraper:
    def __init__(self, path_to_csv=default_path_to_csv, base_url=invoices_base_url, output_path=output_path, verbose=True, output_filetype="json"):
        self.arr = []
        self.final = []
        self.unwanted_chars = [',', ':', '£']

        self.path_to_csv = path_to_csv
        self.base_url = base_url # URL containing all invoices
        self.verbose = verbose # Log processes
        self.output_filetype = output_filetype
        self.output_path = output_path

        self._csv = None # CSV file
        self.cleaned_column = None # All columns with values
        self.invoices = [] # All invoices

        # Read files
        self._read_files()

    def _read_files(self):
        """
        Read csv file and import into dataframe
        """
        self._csv = pd.read_csv(self.path_to_csv)

        # From pandas to list
        column_values = self._csv['RedactedSupportingInvoiceId'].tolist()

        # cleaned columns from nan value
        self.cleaned_column = [int(x) for x in column_values if x == x]

    def _is_money(self,num):
        for sc in self.unwanted_chars:
            num= num.replace(sc,'')
        if re.match("^(£[0-9]+[\, ])?([0-9]+[\., ])+([0-9]{2})+", num):
            return True
        else:
            return False

    def _data_structuring(self, semi_clean_data, invoice_id):
        data=[s for s in semi_clean_data if 'VAT' not in s]
        data = [s for s in data if 'Subtotal' not in s]
        total=[]
        for sent in data:
            numbers = []
            items = []
            
            for word in sent.split():
                if(self._is_money(word)):
                        numbers.append(word)
                else:
                        items.append(word)
           
            for word in items:
                if '£' in word:
                    numbers.append(word)
            

            total.append((invoice_id,' '.join(items), numbers[-1]))
        
        #extra cleaning step
        return total
        
    def _has_price(self,inputString):
        return any(self._is_money(i) for i in inputString.split())

    def has_numbers(self,inputString):
        return bool(re.search(r'\d', inputString))

    def _get_price_with_items(self,received_result, invoice_id):
        j=0
        try:
            for i in range(j,len(received_result)):
                if self._has_price(received_result[i]):
                    self.arr.append(received_result[i])
                    j=i+1
                    while not self._has_price(received_result[j]):
                        self.arr.append(received_result[j])
                        j=j+1
                    self.final.append(received_result[i:j])
            
            return [' '.join(sentence) for sentence in self.final]
        except IndexError:
            
            result = self._data_structuring([' '.join(sentence)
                                  for sentence in self.final], invoice_id=invoice_id)
            return result
        
    def _split_to_lines(self, invoice_index):
        # path to poppler (windows binary installation)
        poppler_path = r'C:\\Program Files\\poppler-0.68.0\\bin'
        
        # Path OCR ( Windows binary installation)
        # pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

        pdf = requests.get(self.base_url + str(self.cleaned_column[invoice_index]), stream=True)
        images = pdf2image.convert_from_bytes(pdf.content)
        data = []
        for image in images:
            page = pytesseract.image_to_pdf_or_hocr(image, extension='pdf')
            pdf = PyPDF2.PdfFileReader(io.BytesIO(page))

            #  TODO: get all pages
            data.append(pdf.getPage(0).extractText())
        
        segmented_data = data[0].splitlines()
        return segmented_data

    def _get_items(self, segmented_data, invoice_id):
        index_tracking=[]
        for data in segmented_data:
            if self._has_price(data):
                index_tracking.append(segmented_data.index(data))
        try:
            result=self._get_price_with_items(segmented_data[index_tracking[0] -
                                                1: index_tracking[-1]], invoice_id=invoice_id)
            return result
        except:
            return 'The file is either empty or not readable, please edit the file'
            
    def get_invoice(self, invoice_id, page=None):
        """
        Get a specific invoice's data

        :param invoice_id: Id of the invoice
        """
        if invoice_id in self.cleaned_column:
            lines = self._split_to_lines(self.cleaned_column.index(invoice_id))
            invoice = self._get_items(lines, invoice_id=invoice_id)
            return invoice
        else:
            raise FileNotFoundError

    def get_all_invoices(self):
        """
        Fetches all invoices' data into memory

        :param save_as: Save to file
        """
        print("Fetching data from all invoices")

        try: 
            for id in self.cleaned_column:
                self.invoices.extend(self.get_invoice(id))
        except:
            print(f"Parsing unsuccessfull: something went wrong")

        if self.output_filetype is not None:
            df = pd.DataFrame(self.invoices)
            os.makedirs(self.output_path, exist_ok=True)
            file_path = self.output_path + "out." + self.output_filetype

            try:
                if self.output_filetype == "csv":
                    df.to_csv(file_path)
                elif self.output_filetype == "json":
                    df.to_json(file_path)
                elif self.output_filetype == "excel":
                    df.to_excel(file_path)
                else:
                    print(f"Save unsuccesful: {self.output_filetype} is unsupported")
            except:
                print("Save unsuccesful: something went wrong")

        return self.invoices



