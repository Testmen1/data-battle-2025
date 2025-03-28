// server/server.js
import express from "express";
import mongoose from "mongoose";
import cors from "cors";
import dotenv from "dotenv";

dotenv.config();

const app = express();
app.use(cors());
app.use(express.json());

// Connexion à MongoDB
mongoose.connect(process.env.MONGO_URI)
  .then(() => console.log("MongoDB connecté"))
  .catch(err => console.error(err));

// Définition du schéma pour les chats
const chatSchema = new mongoose.Schema({
  title: { type: String, required: true },
  messages: [
    {
      text: String,
      isUser: Boolean,
      timestamp: { type: Date, default: Date.now }
    }
  ],
  createdAt: { type: Date, default: Date.now },
});

const Chat = mongoose.model("Chat", chatSchema);

// Route pour récupérer tous les chats
app.get("/chats", async (req, res) => {
  try {
    const chats = await Chat.find().sort({ createdAt: -1 });
    res.json(chats);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Route pour créer un nouveau chat
app.post("/chats/new", async (req, res) => {
  try {
    const { title } = req.body;
    const newChat = new Chat({ title, messages: [] });
    await newChat.save();
    res.status(201).json(newChat);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Route pour récupérer le dernier chat créé
app.get("/chats/latest", async (req, res) => {
  try {
    const latestChat = await Chat.findOne().sort({ createdAt: -1 });
    res.json(latestChat || {}); // Retourne un objet vide si aucun chat n'existe
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});


// Route pour récupérer un chat par ID
app.get("/chats/:id", async (req, res) => {
  const { id } = req.params;
  try {
    const chat = await Chat.findById(id);
    if (!chat) return res.status(404).json({ error: "Chat non trouvé" });
    res.json(chat);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});


// Route pour ajouter un message à un chat
app.post("/chats/:id/message", async (req, res) => {
  try {
    const { text, isUser } = req.body;
    const chat = await Chat.findById(req.params.id);
    if (!chat) return res.status(404).json({ error: "Chat non trouvé" });

    // Ajouter le nouveau message au tableau des messages
    chat.messages.push({ text, isUser });
    await chat.save();

    res.json(chat);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Route pour supprimer un chat
app.delete("/chats/:id", async (req, res) => {
  try {
    const chat = await Chat.findByIdAndDelete(req.params.id);
    if (!chat) return res.status(404).json({ error: "Chat non trouvé" });
    res.json(chat);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`Serveur démarré sur le port ${PORT}`));
