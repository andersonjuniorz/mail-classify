# Responsavel pelas rotas

from flask import request, jsonify
import PyPDF2

def upload_files():
    processed_contents = []
    
    # Lógica para lidar com UPLOAD DE ARQUIVOS
    # Verifica se há arquivos enviados e se a lista não está vazia
    if 'files' in request.files and request.files.getlist('files'):
        uploaded_files = request.files.getlist('files')
        
        for file in uploaded_files:
            if file.filename == '':
                continue # Pula se o nome do arquivo for vazio (pode ocorrer com campos vazios)
            
            file_content = file.read() # Lê o conteúdo binário do arquivo
            file.seek(0) # Volta o ponteiro do arquivo para o início (importante para PyPDF2)
            
            file_info = {
                'filename': file.filename,
                'content_type': file.content_type,
                'size': len(file_content)
            }

            if file.content_type == 'text/plain':
                try:
                    # Decodifica para UTF-8 e limpa espacos com o .strip()
                    file_info['extracted_text'] = file_content.decode('utf-8').strip()
                except UnicodeDecodeError:
                    file_info['extracted_text'] = 'Não foi possível decodificar o arquivo TXT (codificação inválida).'
            elif file.content_type == 'application/pdf':
                try:
                    pdf_reader = PyPDF2.PdfReader(file.stream)
                    pdf_text = ""
                    for page_num in range(len(pdf_reader.pages)):
                        page = pdf_reader.pages[page_num]
                        pdf_text += page.extract_text() or ""
                    # Aplica .strip() ao texto extraído do PDF
                    file_info['extracted_text'] = pdf_text.strip()
                except Exception as e:
                    file_info['extracted_text'] = f'Não foi possível extrair texto do PDF: {str(e)}'
            else:
                file_info['extracted_text'] = 'Tipo de arquivo não suportado para extração de texto.'
            
            processed_contents.append(file_info)

    # Logica para lidar com TEXTO DIRETO INSERIDO
    # Verifica se a chave 'email_text' está presente nos dados do formulário
    elif 'email_text' in request.form:
        email_text_data = request.form['email_text']
        
        # Aplica .strip() para limpar espaços em branco do inicio e fim
        cleaned_email_text = email_text_data.strip()

        # Verifica se o texto limpo não está vazio
        if not cleaned_email_text:
            return jsonify({'error': 'O texto do e-mail fornecido está vazio ou contém apenas espaços em branco.'}), 400

        text_info = {
            'filename': 'email_digitado.txt',
            'content_type': 'text/plain',
            'size': len(cleaned_email_text.encode('utf-8')),
            'extracted_text': cleaned_email_text
        }
        
        processed_contents.append(text_info)

    # Verificação final para garantir que algum conteúdo foi recebido e processado
    if not processed_contents:
        return jsonify({'error': 'Nenhum conteúdo de e-mail válido fornecido para processamento.'}), 400

    # Retorna uma resposta unificada para ambos os tipos de entrada
    return jsonify({
        'message': 'Conteúdo(s) processado(s) com sucesso!',
        'files': processed_contents
    }), 200