from flask import Flask, request, jsonify, send_file
import os
import PyPDF2
import traceback
import base64
import shutil
import fitz

app = Flask(__name__)

@app.route('/process_pdf', methods=['POST'])
def process_pdf():
    try:
        user = request.form['user'].upper()
        pdf = request.files['pdf']

        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        default_dir = os.path.join(os.getcwd(), user)
        os.makedirs(default_dir, exist_ok=True)
        
        pdf_path_origin = os.path.join(default_dir, f"{str(pdf.filename).replace(".pdf", "")}.pdf")
        pdf.save(pdf_path_origin)

        pdf_file = fitz.open(pdf_path_origin)
        for page_number in range(len(pdf_file)):
            pdf_page = fitz.open()
            pdf_page.insert_pdf(pdf_file, from_page=page_number, to_page=page_number)

            pdf_path_end = os.path.join(default_dir, f'{str(pdf.filename).replace(".pdf", "")}_{page_number + 1}.pdf')
            pdf_page.save(pdf_path_end)
            pdf_page.close()

        pdf_file.close()
        os.remove(pdf_path_origin)

        pdf_files = os.listdir(default_dir)

        for pdf_file in pdf_files:
            with open(os.path.join(default_dir, pdf_file), 'rb') as pdf:
                encoded_str = base64.b64encode(pdf.read()).decode('utf-8')
                app.logger.info(encoded_str)
                app.logger.info('\n')
                
        shutil.rmtree(default_dir)
        
        return jsonify({"result": "Processo Finalizado.", "message": 'Arquivo foi processado com sucesso.'})
    except Exception as e:

        traceback_text = traceback.format_exc()
        return jsonify({"result": "error", "message": str(traceback_text)})

if __name__ == '__main__':
    app.run(debug=True)