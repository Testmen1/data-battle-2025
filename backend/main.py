from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import json
import ollama
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import h5py
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
import re
from transformers import pipeline

pipe = pipeline("translation", model="Helsinki-NLP/opus-mt-fr-en")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  
    allow_credentials=True,
    allow_methods=["*"],  # Autorise toutes les méthodes (GET, POST, etc.)
    allow_headers=["*"],  # Autorise tous les headers
)


app = FastAPI()


stop_words = set(stopwords.words('english'))

def flatten_json(json_obj, parent_title='', parent_number=''):
    """
    Aplatit une structure JSON imbriquée en une liste de chaînes de texte avec contexte.

    :param json_obj: Dictionnaire JSON à aplatir.
    :param parent_title: Titre parent pour le contexte.
    :param parent_number: Numéro parent pour le contexte.
    :return: Liste de chaînes de texte aplaties avec contexte.
    """
    items = []

    if isinstance(json_obj, dict):
        article_title = json_obj.get("article_title","")
        article_number = json_obj.get("article_number","")
        main_article = json_obj.get("main_article", "")

        # Construire le titre complet avec contexte
        full_title = f"{parent_title}, {article_number} {article_title}".strip(", ")
        if main_article:
            items.append(f"{full_title} : {main_article}")

        # Parcourir les sous-articles récursivement
        sub_articles = json_obj.get("sub_articles", [])
        for sub_article in sub_articles:
            items.extend(flatten_json(sub_article, full_title, article_number))

    elif isinstance(json_obj, list):
        for item in json_obj:
            items.extend(flatten_json(item, parent_title, parent_number))

    return items




data_path_file = "../extr/data/clean"

json_files = [f'{data_path_file}/json/guidelines_examination_articles.json', f'{data_path_file}/json/epc_rules.json', f'{data_path_file}/json/epc_articles.json']
h5_files = [f'{data_path_file}/h5/guidelines_examination_articles.h5', f'{data_path_file}/h5/epc_rules.h5', f'{data_path_file}/h5/epc_articles.h5']

data_array = []
for file in json_files:
    with open(file) as f:
        data = json.load(f)
        data = flatten_json(data)
        data_array.append(data)

embeddings_array = []
for file in h5_files:
    with h5py.File(file, 'r') as h5_file:
        embeddings = h5_file['embeddings'][:]
        embeddings_array.append(embeddings)

def get_best_results(prompt: str):

    prompt_embedding_response = ollama.embeddings(model='nomic-embed-text', prompt=prompt)
    prompt_embedding = np.array(prompt_embedding_response.embedding).reshape(1, -1)

    best_results = []

    # Iterate through each file's embeddings and data
    for embeddings, data in zip(embeddings_array, data_array):
        # Calculate similarities between the prompt and the paragraphs
        similarities = cosine_similarity(prompt_embedding, embeddings)
        print(similarities)
        # Sort indices by descending similarity
        
        best_indices = np.argsort(similarities[0])[::-1]

        file_best_results = [
            data[i] for i in best_indices[:4] if similarities[0][i] >= 0.6
        ]


        # Add the results for this file to the overall results
        best_results.extend(file_best_results)

    # Combine all filtered paragraphs into a single string
    best_results = "\n".join(best_results)
    

    return best_results



class PromptRequest(BaseModel):
    prompt: str


@app.post("/generate")
def generate_response(request: PromptRequest):

    pipe = pipeline("translation", model="Helsinki-NLP/opus-mt-fr-en")
    translated = pipe(request.prompt)

    new_prompt = translated[0]['translation_text']
   
    best_results = get_best_results(new_prompt)
  
    # URL de l'API Ollama
    url = "http://localhost:11434/api/generate"

    # Payload pour la requête
    payload = {
        "model": "onizukai",

        "prompt": f"Chat history: None\n\nContext: {best_results}\n\n Question: {request.prompt}",
    }

    # Headers pour la requête
    headers = {
        "Content-Type": "application/json"
    }

    try:
        # Envoyer la requête POST à l'API Ollama
        with requests.post(url, headers=headers, data=json.dumps(payload), stream=True) as response:
            if response.status_code == 200:
                complete_response = ""
                buffer = ""
                # Traiter la réponse en streaming
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        buffer += chunk.decode('utf-8')
                        try:
                            data = json.loads(buffer)
                            complete_response += data.get("response", "")
                            buffer = ""
                        except json.JSONDecodeError:
                            continue
                return [{"response": complete_response}, best_results]
            else:
                raise HTTPException(status_code=response.status_code, detail="Error in Ollama API request")
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Request failed: {str(e)}")

# puis utilisez la commande suivante dans le terminal :
# uvicorn main:app --reload

@app.post("/questions")
def generate_questions(request: PromptRequest):
    
    pipe = pipeline("translation", model="Helsinki-NLP/opus-mt-fr-en")
    translated = pipe(request.prompt)

    new_prompt = translated[0]['translation_text']

    best_results = get_best_results(new_prompt)

    # URL de l'API Ollama
    url = "http://localhost:11434/api/generate"

    # Payload pour la requête
    payload = {
        "model": "onizukai-mcq",
        "prompt": f"Context: {best_results}",
        "format": "json",
    }

    # Headers pour la requête
    headers = {
        "Content-Type": "application/json"
    }

    try:
        # envoyer la requête POST à l'API Ollama
        response = requests.post(url, headers=headers, data=json.dumps(payload),  stream=False)
        if response.status_code == 200:
            complete_response = ""
            # Process each line in the response
            for line in response.text.splitlines():
                if line.strip():
                    try:
                        data = json.loads(line)
                        complete_response += data.get("response", "")
                    except json.JSONDecodeError:
                        continue
            
            # Try to parse the complete response as a JSON object
            try:
                question_data = json.loads(complete_response)
                return question_data
            except json.JSONDecodeError:
                # If parsing fails, return the raw response
                return {"response": complete_response, "context": best_results}
        else:
            raise HTTPException(status_code=response.status_code, detail="Error in Ollama API request")
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Request failed: {str(e)}")
    
# puis utilisez la commande suivante dans le terminal :
# uvicorn main:app --reload

