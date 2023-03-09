import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import uuid

# inicializar o SDK do Firebase
cred = credentials.Certificate("teste-firebase.json")
firebase_admin.initialize_app(cred)

# criar uma referência para a coleção desejada
db = firestore.client()
collection_ref = db.collection('teste-collection')

# gerar um novo ID único
new_doc_id = f"_id({uuid.uuid4()})"

# criar um novo documento com o ID personalizado
new_data = {
    'texto': 'vindo do pycharm com python',
    'id': new_doc_id
}

# adicionar o novo documento à coleção
collection_ref.document(new_doc_id).set(new_data)