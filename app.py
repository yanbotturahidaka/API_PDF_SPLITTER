from flask import Flask, request, jsonify
from flask_cors import CORS
import traceback
import base64
import shutil
import fitz
import os

app = Flask(__name__)
CORS(app)

@app.route('/process_pdf', methods=['POST'])
def process_pdf():
    try:
        pdf = request.files['pdf'] # Recebe o PDF do FRONT END.
        pdf_pages = [] 
        
        # Seta um diretorio temporario de trabalho para processar o PDF.
        default_dir = os.path.join(os.getcwd(), 'PDF')
        os.makedirs(default_dir, exist_ok=True)
        
        # Salva o arquivo recebido do FRONT END temporariamente para processamento.
        pdf_path_origin = os.path.join(default_dir, f'{str(pdf.filename).replace(".pdf", "")}.pdf')
        pdf.save(pdf_path_origin)
        
        # Processa o PDF separando os em paginas.
        pdf_file = fitz.open(pdf_path_origin)
        for page_number in range(len(pdf_file)):
            pdf_page = fitz.open()
            pdf_page.insert_pdf(pdf_file, from_page=page_number, to_page=page_number)
            pdf_path_end = os.path.join(default_dir, f'{str(pdf.filename).replace(".pdf", "")}_{page_number + 1:03d}.pdf')
            pdf_page.save(pdf_path_end)
            pdf_page.close()
        pdf_file.close()
        
        os.remove(pdf_path_origin) # Remove o arquivo original do diretorio temporario.

        # Organiza a lista dos arquivos para garantir que sejam enviados em ordem corretamente.
        pdf_files = sorted(os.listdir(default_dir), key=lambda x: int(x.split('_')[-1].split('.')[0]))

        # Converter as paginas do PDF em BASE 64 para enviar de volta ao FRONT END.
        for pdf_file_name in pdf_files:
            with open(os.path.join(default_dir, pdf_file_name), 'rb') as pdf_file:
                pdf_page = base64.b64encode(pdf_file.read()).decode('utf-8')
                pdf_pages.append(pdf_page)
                
        shutil.rmtree(default_dir) # Remove o diretorio temporario apos finalizar o trabalho.

        return jsonify(pdf_pages) # Envia de volta uma lista com as paginas do PDF ja convertidas em BASE 64 de volta ao FRONT END.
    except Exception as e:
        traceback_text = traceback.format_exc()
        return jsonify({"result": "error", "message": str(traceback_text)})

if __name__ == '__main__':
    app.run(debug=True)