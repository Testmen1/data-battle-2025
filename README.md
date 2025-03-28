# Data battle 2025
L'équipe Saïtèque propose sa solution pour le Data Battle 2025 organisé par l'association IA Pau.

OnizukAI est une application web qui permet aux étudiants en droit des brevets de s'améliorer et d'apprendre dans ce domaine complexe. OnizukAI propose un Chat bot augmenté avec un RAG basé sur divers documents de loi et de recommendations en droit des brevets.

## Mise en place du projet en local

### Frontend

Naviguez dans `/frontend` et executez les commandes suivantes :

```bash
npm i
npm run dev
```
et dans un autre terminal :

```bash
node server.js
```

### Backend

Utilisez le fichier `requirements.txt` pour télécharger les librairies python nécéssaires :

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
Puis lancez le server avec `uvicorn` depuis `/backend` :

```
uvicorn main:app --reload
```
### Modèles

Installez l'API ollama : 
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Pour ce projet, vous aurez besoin du modèle mistral:7b (4,8Go) : 
```bash
ollama pull mistral
```

Puis créez les deux modèles utilisés dans notre solution :
```bash
ollama create onizukai -f models/onizukai_modelfile
ollama create onizukai-mcq -f models/onizukai-mcq_modelfile
```

Enfin, démarrez ces deux modèles dans deux terminaux distincts : 
```bash
ollama run onizukai
ollama run onizukai-mcq
```


#### Crédits
Léo-Paul Bigot,
Aventin Farret,
Matis Toniutti,
Dorian Cornec,
Sophie Longy
