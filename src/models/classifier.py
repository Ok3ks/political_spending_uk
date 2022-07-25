from calendar import day_abbr
import os
import pandas as pd
from transformers import pipeline
from src.config import output_path, output_filetype, labels

class Classifier:
    def __init__(self, data_filetype="json", labels=labels, output_filetype=output_filetype):
        self.data_filetype = data_filetype

        self.data_points = None
        self.labels = labels
        self.output_filetype = output_filetype
        self.hypothesis_template = "This text is about {}."

        self.predictions = []
        self.predictions_as_df = None

        self._init_model()
        self._read_data()

    def _init_model(self):
        self.model = pipeline('zero-shot-classification', model='facebook/bart-large-mnli')

    def _read_data(self):
        data_file = output_path + 'out.' + self.data_filetype

        if self.data_filetype == "json":
            data_points = pd.read_json(data_file)
        elif self.data_filetype == "csv":
            data_points = pd.read_csv(data_file)
        elif self.data_filetype == "excel":
            data_points = pd.read_excel(data_file)
        else:
            raise ValueError("Data file type unsupported")

        self.data_points = data_points.iloc[: , :3]

    def _tokenizer(self, text):
        return self.tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=500)

    def _classify_data_point(self, data_point):
        prediction = self.model(data_point, self.labels, hypothesis_template=self.hypothesis_template, multi_label=True)
        return prediction['labels'][0]

    def _save_predictions(self):
        os.makedirs(output_path, exist_ok=True)
        file_path = output_path + "predictions." + self.output_filetype

        try:
            if self.output_filetype == "csv":
                self.predictions_as_df.to_csv(file_path)
            elif self.output_filetype == "json":
                self.predictions_as_df.to_json(file_path)
            elif self.output_filetype == "excel":
                self.predictions_as_df.to_excel(file_path)
            else:
                print(f"Save unsuccesful: {self.output_filetype} is unsupported")
        except:
            print("Save unsuccesful: something went wrong. View predictions at classifier_instance.predictions")

    def classify(self):
        print(f"Classifying {len(self.data_points)} data points")

        for index, data_point in self.data_points.iterrows():
            id = data_point[0]
            description = data_point[1]
            amount = data_point[2]
            label = self._classify_data_point(data_point=description)
            
            self.predictions.append((id, description, amount, label))

        print(f"Saving predictions")
        self.predictions_as_df = pd.DataFrame(self.predictions)
        self.save_predictions()