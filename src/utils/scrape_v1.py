import os
import pandas as pd
import urllib.request
from io import BytesIO, StringIO
from PyPDF2 import PdfReader
from src.utils.preprocessing import Preprocessor
from src.config import invoices_base_url, default_path_to_csv, output_path

class Scraper:
    def __init__(self, path_to_csv, base_url=invoices_base_url, verbose=True, output_filetype="csv"):
        self.path_to_csv = path_to_csv
        self.base_url = base_url # URL containing all invoices
        self.verbose = verbose # Log processes
        self.output_filetype = output_filetype

        self._csv = None # CSV file
        self.cleaned_column = None # All columns with values
        self.invoices = [] # All invoices

        self.preprocessor = Preprocessor()

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


    def _retrieve_output(self):
        """
        Read csv file and import into dataframe
        """
        try: 
            if self.output_filetype is not None:
                file_path = output_path + "/out." + self.output_filetype
                if self.output_filetype == "csv":
                    self.invoices = pd.read_csv(file_path)
                elif self.output_filetype == "json":
                    self.invoices = pd.read_csv(file_path)
                elif self.output_filetype == "excel":
                    self.invoices = pd.read_excel(file_path)
                else:
                    print(f"Retrieval unsuccessfull: {self.output_filetype} is unsupported")
        except:
            raise NotImplementedError

    def _to_lines(self, page):
        """
        Returns lines in a page

        :param page: PageObject
        """
        lines = []
        text = page.extractText()

        # iterate through lines
        for line in StringIO(text):
            lines.append(line)

        return lines

    def _get_document(self, invoice_index, page_index=None):
        """
        Retrieve data from an invoice

        :param invoice_index: Index of the invoice in the dataframe
        """
        # read hosted document with index doc  w.m: we only checking the first document for now
        wFile = urllib.request.urlopen(self.base_url + str(self.cleaned_column[invoice_index]))
        bytes_stream = BytesIO(wFile.read())
        reader_ = PdfReader(bytes_stream)

        document = []

        if page_index == None:
            # default to all pages
            for page in reader_.pages:
                output = self._to_lines(page)
                document.extend(output)
        else:
            # get the given page from the document
            if page_index >= 0 and page_index <= reader_.numPages:
                output = self._to_lines(reader_.pages[page_index])
                document.extend(output)
            else: 
                print(f"Page {page_index} does not exist")

        return document

    def _clean_up(self, document):
        pass

    def get_invoice(self, invoice_id, page=None):
        """
        Get a specific invoice's data

        :param invoice_id: Id of the invoice
        """
        if invoice_id in self.cleaned_column:
            invoice = self._get_document(self.cleaned_column.index(invoice_id), page_index=page)
            return self.preprocessor.clean(' '.join(invoice))
        else:
            raise FileNotFoundError

    def get_all_invoices(self):
        """
        Fetches all invoices' data into memory

        :param save_as: Save to file
        """
        try:
            # TODO: Can be refactored to check if output file exists first 
            if self.output_filetype is not None:
                file_path = output_path + "/out." + self.output_filetype
                if self.output_filetype == "csv":
                    self.invoices = pd.read_csv(file_path)
                elif self.output_filetype == "json":
                    self.invoices = pd.read_csv(file_path)
                elif self.output_filetype == "excel":
                    self.invoices = pd.read_excel(file_path)
                else:
                    print(f"Retrieval unsuccessfull: {self.output_filetype} is unsupported")
        except: 
            print("Retrieval unsuccessfull: something went wrong")
            print("Now fetching data from all invoices")

            # Do not fall into the try-except nest hole. Just a bit won't hurt haha :)
            try: 
                for id in self.cleaned_column:
                    self.invoices.append({'id': id, 'data': self.get_invoice(id)})
            except:
                print(f"Parsing unsuccessfull: something went wrong")

        if self.output_filetype is not None:
            df = pd.DataFrame(self.invoices)
            os.makedirs(output_path, exist_ok=True)
            file_path = output_path + "out." + self.output_filetype

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

# For running from terminal
if __name__ == "__main__":
    scraper = Scraper(path_to_csv=default_path_to_csv)
    print(scraper.get_all_invoices())
