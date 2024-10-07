from flask import Flask, request, jsonify
import os
import PyPDF2
import traceback
import base64

app = Flask(__name__)

@app.route('/process_pdf', methods=['POST'])
def process_pdf():

    hash_64 = []

    try:
        user = request.form['user']
        pdf = request.files['pdf']

        input_dir = os.path.join("PDF_SPLITTER", user, "input_File")
        os.makedirs(input_dir, exist_ok=True)

        output_dir = os.path.join("PDF_SPLITTER", user, "output_File")
        os.makedirs(output_dir, exist_ok=True)

        pdf_path = os.path.join(input_dir, f"{str(pdf.filename).replace('.pdf', '')}.pdf")
        pdf.save(pdf_path)

        files_input = os.listdir(input_dir)

        for file_pdf_input in files_input:
            with open(os.path.join(input_dir, file_pdf_input), 'rb') as file_input:
                pdf_reader = PyPDF2.PdfReader(file_input)

                for page_num in range(len(pdf_reader.pages)):
                    pdf_writer = PyPDF2.PdfWriter()
                    pdf_writer.add_page(pdf_reader.pages[page_num])

                    files_output = os.path.join(output_dir, f"{str(pdf.filename).replace('.pdf', '')}_{page_num + 1}.pdf")
                    with open(files_output, 'wb') as output_file:
                        pdf_writer.write(output_file)

                    print(f"Página {page_num + 1} salva como {files_output}")

        files_output = os.listdir(output_dir)

        for file_pdf_output in files_output:
            with open(os.path.join(output_dir, file_pdf_output), 'rb') as file_output:
                encoded_str = base64.b64encode(file_output.read()).decode('utf-8')
                app.logger.info(encoded_str)
                app.logger.info('\n')

        return jsonify({"result": "Processo Finalizado.", "Hash 64:": 'Abacaxi'})
    
    except Exception as e:

        traceback_text = traceback.format_exc()
        return jsonify({"result": "error", "message": str(traceback_text)})
    
if __name__ == '__main__':
    app.run(debug=True)
