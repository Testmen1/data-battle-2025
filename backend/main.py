from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import json
import ollama
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import h5py

app = FastAPI()

data_path_file = "/home/leo/Documents/data-battle-2025/mcq-extr/data"

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
        article_title = json_obj.get("article_title", "")
        article_number = json_obj.get("article_number", "")
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


def load_embedings(file: str):
    with h5py.File(f'{data_path_file}/clean/h5/{file}', 'r') as h5_file:
        embeddings = h5_file['embeddings'][:]
    
    return embeddings

def load_data(file: list):
    
    with open(f'{data_path_file}/clean/json/{file}') as f:
        data = json.load(f)

    data = flatten_json(data)

    return data

def get_best_files(prompt: str):
    #TODO
    return None

def get_best_results(prompt: str):

    best_files = [["epc_rules.json", "epc_rules.h5"]]

    
    data_array = load_data(best_files[0][0]) 

    embeddings_array = load_embedings(best_files[0][1])


    prompt_embedding_response = ollama.embeddings(model='nomic-embed-text', prompt=prompt)
    prompt_embedding = np.array(prompt_embedding_response.embedding).reshape(1, -1)

    # Calculer les similarités entre le prompt et les paragraphes
    similarities = cosine_similarity(prompt_embedding, embeddings_array)


    # Trouver les indices des 5 paragraphes les plus similaires
    best_indices = similarities.argsort()[0][-10:][::-1]

    # Afficher les 5 paragraphes les plus similaires
    best_results = [data_array[i] for i in best_indices]

    # put top 5 paragraphs in a string variable
    best_results = "\n".join(best_results)

    return best_results



class PromptRequest(BaseModel):
    prompt: str
@app.post("/generate/")
def generate_response(request: PromptRequest):

    best_results = get_best_results(request.prompt)

    # URL de l'API Ollama
    url = "http://localhost:11434/api/generate"

    # Payload pour la requête
    payload = {
        "model": "mistral",
        "prompt": f"Chat history: None\n\nContext: {best_results}\n\n Answer the question based on the contect: {request.prompt}"
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

# Pour exécuter ce serveur, enregistrez le code dans un fichier, par exemple `main.py`,
# puis utilisez la commande suivante dans le terminal :
# uvicorn main:app --reload
