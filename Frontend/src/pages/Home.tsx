import { useState, type ChangeEvent, type FormEvent } from 'react';
import type { ServerResponse } from '../interfaces/ServerResponse';

import '../styles/home.css';


const Home = () => {
    // Estados para o input de arquivo (Form 1)
    const [selectedFiles, setSelectedFiles] = useState<FileList | null>(null);
    const [selectedFileNames, setSelectedFileNames] = useState<string[]>([]);

    // Estados para o Form de e-mail (Form 2 e Texto direto)
    const [sendTo, setSendTo] = useState<string>('');
    const [subject, setSubject] = useState<string>('');
    const [message, setMessage] = useState<string>('');

    // Estado para exibir a resposta do servidor
    const [serverResult, setServerResult] = useState<ServerResponse | null>(null);

    // Obtem a URL base da API do backend
    const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

    // Handler para o input de arquivo (permanece separado, pois lida com FileList)
    const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {

        const files = event.target.files;

        if (files && files.length > 0) {

            setSelectedFiles(files);
            const newFileNames = Array.from(files).map(file => file.name);
            setSelectedFileNames(newFileNames);

            setServerResult(null);

        } else {
            setSelectedFiles(null);
            setSelectedFileNames([]);
        }
    };

    // Cria um handler de 'onChange' para campos de texto, usando a funcao 'setter' fornecida
    const handleChange = (setter: React.Dispatch<React.SetStateAction<string>>) => 
        (event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {

            setter(event.target.value);
            setServerResult(null); // Reset de estado
        };

    // Logica de Envio do Form (Upload)
    const handleFileUploadSubmit = async (event: FormEvent) => {
        event.preventDefault();

        if (!selectedFiles || selectedFiles.length === 0) {
            alert('Por favor, selecione pelo menos um arquivo para enviar.');
            return;
        }

        const formData = new FormData();
        for (let i = 0; i < selectedFiles.length; i++) {
            formData.append('files', selectedFiles[i]);
        }

        try {
            const response = await fetch(`${API_BASE_URL}/upload`, { 
                method: 'POST',
                body: formData,
            });

            if (response.ok) {

                const data: ServerResponse = await response.json();
                console.log('Resposta do servidor (Upload):', data);

                setServerResult(data);
                alert('Arquivos enviados e processados! Veja os resultados abaixo.');

                setSelectedFiles(null); 
                setSelectedFileNames([]);

            } else {
                const errorData = await response.json();
                console.error('Erro ao enviar arquivos:', response.status, errorData);

                setServerResult(null);
                alert(`Erro ao enviar arquivos: ${errorData.error || response.statusText}`);
            }

        } catch (error) {

            console.error('Erro de rede ou ao processar (Upload):', error);
            setServerResult(null);

            alert('Erro de rede ao tentar enviar arquivos. Verifique sua conexão ou o servidor.');
        }
    };

    // Logica de Envio para o Form onde insiro o texto diretamente
    const handleEmailTextSubmit = async (event: FormEvent) => {
        event.preventDefault();

        // Removendo espacos e verificando se os campos estao preenchidos
        if (sendTo.trim() === '' && subject.trim() === '' && message.trim() === '') {
            alert('Por favor, preencha os campos do e-mail para enviar.');
            return;
        }

        const formData = new FormData();
        const emailContent = `Assunto: ${subject.trim()}\n` +
                             (sendTo.trim() ? `De: ${sendTo.trim()}\n` : '') +
                             `Mensagem:\n${message.trim()}`;
        
        formData.append('email_text', emailContent);

        try {
            const response = await fetch(`${API_BASE_URL}/upload`, { 
                method: 'POST',
                body: formData,
            });

            if (response.ok) {
                const data: ServerResponse = await response.json();
                console.log('Resposta do servidor (Texto Direto):', data);

                setServerResult(data);
                alert('E-mail enviado e processado! Veja os resultados abaixo.');

                setSendTo('');
                setSubject('');
                setMessage('');

            } else {
                const errorData = await response.json();
                console.error('Erro ao enviar e-mail:', response.status, errorData);

                setServerResult(null);
                alert(`Erro ao enviar e-mail: ${errorData.error || response.statusText}`);
            }

        } catch (error) {
            console.error('Erro de rede ou ao processar (Texto Direto):', error);
            setServerResult(null);

            alert('Erro de rede ao tentar enviar e-mail. Verifique sua conexão ou o servidor.');
        }
    };

    return (
        <div className='home-container'>
            <h1>Classificador de E-mails</h1>
            
            {/* Formulario para upload de arquivos */}
            <div className='form-section'>
                <h2 className='center'>Upload de Arquivos</h2>

                <fieldset>
                    <form onSubmit={handleFileUploadSubmit}>
                        <label htmlFor="email-file" className="label-input-file">
                            <span className='span-file'>Escolha um arquivo (.txt ou .pdf)</span>

                            <input
                                type="file"
                                accept="text/plain,application/pdf"
                                className='email-file'
                                id="email-file"
                                multiple
                                onChange={handleFileChange}
                            />
                        </label>

                        {selectedFileNames.length > 0 ? (
                            <div className="files-feedback-container">
                                <p>Arquivos selecionados:</p>
                                <ul>
                                    {selectedFileNames.map((fileName, index) => (
                                        <li key={index} className="file-feedback">
                                            <strong>{fileName}</strong>
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        ) : (
                            <p className="no-file-feedback">Nenhum arquivo selecionado.</p>
                        )}
                        <input type="submit" className='submit-button' value="Classificar Arquivos" />
                    </form>
                </fieldset>
            </div>

            <p className="or-separator">--- OU ---</p>

            {/* Form de email */}
            <div className='form-section'>
                <h2 className='center'>Inserir E-mail Manualmente</h2>
                <fieldset>
                    <form onSubmit={handleEmailTextSubmit}>
                        <div className="email-input-fields">
                            <label htmlFor="sendTo">Enviar Para:</label>
                            
                            <input
                                type="email"
                                name="sendTo"
                                id="sendTo"
                                value={sendTo}
                                onChange={handleChange(setSendTo)}
                                placeholder="email@exemplo.com"
                            />

                            <label htmlFor="subject">Assunto:</label>
                            <input
                                type="text"
                                name="subject-input"
                                id="subject-input"
                                value={subject}
                                onChange={handleChange(setSubject)}
                                placeholder="Dúvida sobre o sistema..."
                            />


                            <label htmlFor="message">Mensagem:</label>
                            <textarea
                                name="message"
                                id="message"
                                cols={30}
                                rows={10}
                                value={message}
                                onChange={handleChange(setMessage)} 
                                placeholder="Escreva o corpo do e-mail aqui..."
                            ></textarea>

                        </div>
                        <input type="submit" className='submit-button' value="Classificar E-mail" />
                    </form>
                </fieldset>
            </div>

            {/* Area de Exibicao de Resultados */}
            {serverResult && (
                <div className="results-container">
                    <h2>Resultado do Processamento:</h2>
                    <p><strong>Status:</strong> {serverResult.message}</p>

                    {serverResult.files && serverResult.files.length > 0 && (
                        serverResult.files.map((file, index) => (
                            <div key={index} className="file-result-card">
                                <h3>{file.filename}</h3>
                                <p><strong>Tipo:</strong> {file.content_type}</p>
                                <p><strong>Tamanho:</strong> {file.size} bytes</p>
                                
                                {/* Exibe a Categoria da IA */}
                                {file.category && (
                                    <p>
                                        <strong>Categoria: </strong>
                                        <span className={`category-tag ${file.category.toLowerCase()}`}>
                                            {file.category}
                                        </span>
                                        
                                        {/* Exibe probabilidade de acerto */}
                                        {file.probabilities && (
                                            <span>
                                                {/* Probabilidade da categoria prevista */}
                                                {' '} ({file.probabilities[0] > file.probabilities[1] ? (file.probabilities[0] * 100).toFixed(2) : (file.probabilities[1] * 100).toFixed(2)}%)
                                            </span>
                                        )}
                                    </p>
                                )}

                                {/* Exibe a Resposta Sugerida da IA */}
                                {file.suggested_response && (
                                    <>
                                        <h4>Resposta Sugerida:</h4>
                                        <p className="suggested-response">{file.suggested_response}</p>
                                    </>
                                )}

                                <h4>Texto Processado:</h4>
                                <p className="extracted-text">{file.extracted_text}</p>
                            </div>
                        ))
                    )}

                    {(!serverResult.files || serverResult.files.length === 0) && (
                        <p>Nenhum conteudo processado exibivel (pode ser texto vazio ou erro).</p>
                    )}
                </div>
            )}
        </div>
    );
};

export default Home;