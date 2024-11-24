from typing import Final
from openai import OpenAI
import json
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from tinydb import TinyDB, Query, JSONStorage
import numpy as np
import faiss


class CustomJSONStorage(JSONStorage):
    def __init__(self, path):
        super().__init__(path)  # Llamar al constructor de la clase base
        self.path = path  # Asegurarse de que la propiedad 'path' esté definida

    def write(self, data):
        # Guardar los datos en formato JSON permitiendo caracteres especiales
        with open(self.path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)  # Permitir caracteres especiales

with open("keys.json") as f:
    keys = json.load(f)

db = TinyDB('db.json', storage=CustomJSONStorage)
table = db.table('knowledge_base')
Procedure = Query()

# OPENAI API
OPENAI_API_KEY: Final= keys["openai"]["api_key"]
TOKEN: Final = keys["telegram"]["token"]
model = "text-embedding-3-small"
openai_client = OpenAI(api_key=OPENAI_API_KEY)



def add_query_to_procedure(query_text, procedure_name):
    query_embedding = get_embedding(query_text)

    procedure = table.search(Procedure.procedure_name == procedure_name)

    if procedure:
        procedure = procedure[0]
        if "queries" not in procedure:
            procedure["queries"] = []
        procedure["queries"].append({
            "text": query_text,
            "embedding": query_embedding
        })

        table.update(procedure, Procedure.procedure_name == procedure_name)
        print(f"Consulta añadida al procedimiento: {procedure_name}")
    else:
        print(f"No se encontró el procedimiento con nombre {procedure_name}")



index = faiss.IndexFlatL2(1536)


def update_faiss_index(procedure_embedding):
    global index
    embedding = np.array(procedure_embedding).astype("float32").reshape(1, -1)
    index.add(embedding)


def search_procedure(query_embedding, top_k=2):
    query_embedding = np.array(query_embedding).astype("float32").reshape(1, -1)
    distances, indices = index.search(query_embedding, top_k)

    results = []
    for i, idx in enumerate(indices[0]):
        if idx < len(table):
            procedure = table.all()[idx]
            results.append({
                "name": procedure.get("procedure_name", "Desconocido"),
                "description": procedure.get("description", "Sin descripción"),
                "distance": distances[0][i]
            })

    return results


def get_embedding(text):
    try:
        response = openai_client.embeddings.create(input=[text], model=model)
        embedding = response.data[0].embedding
        return embedding
    except Exception as e:
        print(f"Error al generar embedding: {e}")
        return None



def generate_embeddings_for_each_item(items):
    for item in items:
        item_in_text = json.dumps(item)
        embedding = get_embedding(item_in_text)
        item["embeddings"] = embedding
    return items


def handle_user_query(query_text):
    query_embedding = get_embedding(query_text)
    results = search_procedure(query_embedding, top_k=2)

    if not results:
        return "Lo siento, no pude encontrar información relevante para tu consulta."

    response = "He encontrado los siguientes procedimientos relevantes:\n\n"
    for i, result in enumerate(results, 1):
        response += f"{i}. {result['name']} (Distancia: {result['distance']:.2f})\n"
        response += f"   Descripción: {result['description']}\n\n"

    return response.strip()


def add_procedure(procedure):
    procedure_embedding = get_embedding(procedure["description"])

    table.insert(procedure)

    update_faiss_index(procedure_embedding)

def initialize_faiss_index():
    global index
    procedures = table.all()
    for procedure in procedures:
        if "embeddings" in procedure:
            embedding = np.array(procedure["embeddings"]).astype("float32").reshape(1, -1)
            index.add(embedding)
    print(f"Índice FAISS inicializado con {len(procedures)} procedimientos.")


# TELEGRAM BOT
BOT_USERNAME: Final = "@ProcessExpertBot"


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hola! Soy un chatbot. Creado con Python y la API de Telegram.")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Soy un chatbot. Puedo ayudarte con tus consultas. ¡Solo pregúntame!")



def handle_response(text: str) -> str:
    processed: str = text.lower()

    if "hola" in processed:
        return "Hola! ¿En qué puedo ayudarte?"

    if "chao" in processed:
        return "Hasta luego! Que tengas un buen día."

    return "No entiendo, por favor intenta de nuevo."


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f"User: {update.message.chat.id}[{update.message.chat.username}] in {message_type}: {text}")

    if message_type == "group":
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, "").strip()
            response: str = handle_response(new_text)
        else:
            return
    else:
        response = handle_user_query(text)  # Llamada a la función que maneja la consulta y responde con el procedimiento
        if not response:
            response = "Lo siento, no pude encontrar información relevante para tu consulta."  # Respuesta por defecto

    print(f"Bot: {response}")
    await update.message.reply_text(response)



async def handle_error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused an error: {context.error}")


if __name__ == '__main__':
    initialize_faiss_index()
    app = Application.builder().token(TOKEN).build()
    print("Starting Bot...")

    # Comandos
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))

    # Mensajes
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Errores
    app.add_error_handler(handle_error)

    # Polling
    print("Polling...")
    app.run_polling(poll_interval=3)
