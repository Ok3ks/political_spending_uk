

import os
from os.path import join
from typing import List, Optional, Dict, Any
import sys
import uvicorn

module_path = os.path.abspath(os.path.join(os.pardir, os.pardir))
if module_path not in sys.path:
    sys.path.append(module_path)

import urllib.request
from pathlib import Path
from fastapi import FastAPI, File
from fastapi import Request
from pydantic import BaseModel, Field
from classifier import Classifier

import sys


class InferenceInput(BaseModel):
    r"""Input, Pdf should be passed through a url"""

    doc_url: str = Field(..., 
        example = "https://drive.google.com/uploads/mani.pdf", 
        title= "url to pdf")

class InferenceResult(BaseModel):
    r"""Inference outputs from the model"""
    purpose: str = Field(..., example = "Advertisement")

class InferenceResponse(BaseModel):
    r"""Output response for model inference """
    error : str = Field(..., example = False, title = 'error?')
    results: str = Field(..., example = "Advertising", title = "Purpose of invoice")

class ErrorResponse(BaseModel):
    r"""Error response for the API"""
    error: str = Field(..., example = True, title = 'error?')
    message: str = Field(..., example = '', title = 'error message')
    traceback: Optional[str] = Field(None, example = '', title = 'detailed traceback of the error')

app: FastAPI = FastAPI(
    title = 'Intelligent document processing',
    description= 'Processes the intended purpose of a document')

@app.on_event("startup")
async def startup_event():
    r"""Initialize FastAPI"""
    print(f'Loading model')
    system = Classifier()
    print('Model loaded successfully')

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/classify",
        response_model = InferenceResponse,
        responses = {422: {'model': ErrorResponse}, 500:{'model'
        :ErrorResponse}})

def classify(request: Request, body: InferenceInput):
    print('`/api/v1/predict` endpoint called.')

    file_name: str = os.path.basename(body.doc_url)
    cache_dir: str = os.path.abspath('base/file')
    os.makedirs(cache_dir, exist_ok= True)
    local_path: str = os.path.abspath(join(cache_dir, file_name))

    opener = urllib.request.build_opener()
    opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64), AppleWebKit/537.36 \
        #(KHTML, like Gecko), (Chrome/36.0.1941.0 Safari/537.36')]
    urllib.request.install_opener(opener)
    urllib.request.urlretrieve(body.doc_url, local_path)

    system = app.package['system']
    results: Dict[str, Any] = {'purpose': None}

    system._read_data(body)
    purpose = system.classify()
    #os.remove(body)

    return {
        'results' : purpose
    }