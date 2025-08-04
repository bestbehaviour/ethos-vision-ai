import os
import requests # Menggunakan library requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template

# Inisialisasi Aplikasi Flask
app = Flask(__name__)

# Muat environment variables
load_dotenv()

# Route untuk halaman utama (frontend)
@app.route('/')
def index():
    return render_template('index.html')

# Route untuk API chat
@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get("message")
    if not user_message:
        return jsonify({"error": "Message cannot be empty"}), 400

    try:
        api_key = os.environ["GEMINI_API_KEY"]
        # URL endpoint diubah menjadi gemini-2.0-flash agar sesuai dengan curl
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"

        # Gabungkan instruksi dan pertanyaan user menjadi satu prompt
        # Ini adalah cara paling sederhana untuk memberi konteks pada model
        prompt_with_instruction = f"""
        CONTEXT: You are Ethos Vision, an AI assistant for the EthereumOS ecosystem. Your personality is helpful, optimistic, and slightly technical. Answer questions strictly within the context of EthereumOS. If a question is outside this scope, politely state your specialization.

        QUESTION: {user_message}
        """

        # Siapkan data (payload) dalam format JSON yang benar
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt_with_instruction}
                    ]
                }
            ]
        }

        headers = {
            "Content-Type": "application/json"
        }

        # Kirim request ke API menggunakan library requests
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()  # Ini akan memunculkan error jika request gagal

        response_data = response.json()
        
        # Ekstrak jawaban dari struktur JSON yang dikembalikan oleh API
        reply = response_data['candidates'][0]['content']['parts'][0]['text']

        return jsonify({"reply": reply})

    except requests.exceptions.RequestException as e:
        print(f"API Request Error: {e}")
        return jsonify({"error": "Failed to connect to the AI service."}), 500
    except (KeyError, IndexError) as e:
        print(f"API Response Parsing Error: {e}")
        return jsonify({"error": "Received an unexpected response from the AI service."}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({"error": "An unexpected error occurred."}), 500

# Baris ini hanya untuk testing di komputer lokal
if __name__ == '__main__':
    app.run(debug=True)