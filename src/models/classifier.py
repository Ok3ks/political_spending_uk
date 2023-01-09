from calendar import day_abbr
import os
import sys
import pandas as pd
from transformers import pipeline
from src.config import output_path,labels
#import fastseq
import torch

module_path = os.path.abspath(os.path.join(os.pardir, os.pardir))
if module_path not in sys.path:
    sys.path.append(module_path)

if torch.has_mps: device = torch.device('mps')
elif torch.has_cuda: device = torch.device('cuda')
else: torch.device('cpu')


class Classifier:
    def __init__(self, labels=labels):
        
        self.data_points = None
        self.labels = labels
        self.hypothesis_template = "This text is about {}."

        self.predictions = []
        self.predictions_as_df = None

        self._init_model()

    def _init_model(self):
        self.model = pipeline('zero-shot-classification', model='facebook/bart-large-mnli', device = device)

    def _read_data(self,data_file):
        
        self.data_filetype = data_file.split(".")[-1]

        if self.data_filetype == "json":
            data_points = pd.read_json(data_file)
        elif self.data_filetype == "csv":
            data_points = pd.read_csv(data_file)
        elif self.data_filetype == "excel":
            data_points = pd.read_excel(data_file)
        else:
            raise ValueError("Data file type unsupported")

        self.data_points = data_points.iloc[: , :3]
        print("Data read successfully")

    def _tokenizer(self, text):
        return self.tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=500)

    def _classify_data_point(self, data_point):
        prediction = self.model(data_point, self.labels, hypothesis_template=self.hypothesis_template, multi_label=True)
        return prediction['labels'][0]

    def _save_predictions(self, output_filetype):
        os.makedirs(output_path, exist_ok=True)
        file_path = output_path + "predictions." + output_filetype

        try:
            if output_filetype == "csv":
                self.predictions_as_df.to_csv(file_path)
            elif output_filetype == "json":
                self.predictions_as_df.to_json(file_path)
            elif output_filetype == "excel":
                self.predictions_as_df.to_excel(file_path)
            else:
                print(f"Save unsuccesful: {output_filetype} is unsupported")
        except:
            print("Save unsuccesful: something went wrong. View predictions at classifier_instance.predictions")

    def classify(self):
        print(f"Classifying {len(self.data_points)} data points")

        for _, data_point in self.data_points.iterrows():
            id = data_point[0]
            description = data_point[1]
            amount = data_point[2]
            label = self._classify_data_point(data_point=description)
            
            self.predictions.append((id, description, amount, label))

        print(f"Saving predictions")
        self.predictions_as_df = pd.DataFrame(self.predictions)
        return label