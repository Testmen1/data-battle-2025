import json
import random
import ollama
import h5py
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import sys
import re



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


def generate(filename, out):

    with open(filename) as f:
        data = json.load(f)

    data = flatten_json(data)


    embeddings_list = []
    count = 0
    for line in data:

        response = ollama.embeddings(model='nomic-embed-text', prompt=line)
        embeddings_list.append(response.embedding)
        print(f'{count}/{len(data)}')  
        count += 1

    embeddings_array = np.array(embeddings_list)

    with h5py.File(out, 'w') as h5_file:
        h5_file.create_dataset('embeddings', data=embeddings_array)



if __name__ == "__main__":
    if len(sys.argv) != 3:

        print("Usage: python generate_doc_embeds.py <file> <output_filename>")
    else:
        generate(sys.argv[1],sys.argv[2])