import pandas as pd
import urllib.request
from io import BytesIO, StringIO
from PyPDF2 import PdfReader
from src.config import invoices_base_url, default_path_to_csv

class Scraper:
    def __init__(self, path_to_csv, base_url=invoices_base_url, verbose=True, fetch_on_init=False):
        self.path_to_csv = path_to_csv
        self.base_url = base_url # URL containing all invoices
        self.verbose = verbose # Log processes

        self._csv = None # CSV file
        self.cleaned_column = None # All columns with values
        self.invoices = [] # All invoices

        # Read files
        self._read_files()

        if fetch_on_init:
            # Get all invoices on init
            self.get_all_invoices()

    def _read_files(self):
        """
        Read csv file and import into dataframe
        """
        self._csv = pd.read_csv(self.path_to_csv)

        # From pandas to list
        column_values = self._csv['RedactedSupportingInvoiceId'].tolist()

        # cleaned columns from nan value
        self.cleaned_column = [int(x) for x in column_values if x == x]

    def _get_lines(self, invoice_index):
        """
        Retrieve data from an invoice

        :param invoice_index: Index of the invoice in the dataframe
        """
        # read hosted document with index doc  w.m: we only checking the first document for now
        wFile = urllib.request.urlopen(self.base_url + str(self.cleaned_column[invoice_index]))
        bytes_stream = BytesIO(wFile.read())
        reader_ = PdfReader(bytes_stream)
        # get the first page from the document
        page = reader_.pages[0]

        pages_text = page.extractText()

        # get lines
        lines = []
        # iterate through lines
        for line in StringIO(pages_text):
            lines.append(line)

        return lines

    def get_all_invoices(self):
        """
        Fetches all invoices' data into memory

        :param invoice_id: Id of the invoice
        """
        print("Fetching data from all invoices")
        for id in self.cleaned_column:
            self.invoices.append(self.get_invoice(id))

        return self.invoices

    def get_invoice(self, invoice_id):
        """
        Get a specific invoice's data

        :param invoice_id: Id of the invoice
        """
        if invoice_id in self.cleaned_column:
            return self._get_lines(self.cleaned_column.index(invoice_id))
        else:
            return FileNotFoundError

# For running from terminal
if __name__ == "__main__":
    scraper = Scraper(path_to_csv=default_path_to_csv)
    print(scraper.invoices)