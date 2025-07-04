import { useState, type ChangeEvent } from 'react'
import '../styles/home.css'

const Home =() => {
   const [selectedFileNames, setSelectedFileNames] = useState<string[]>([]);

    // Handler: para quando o input file mudar
    const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
        const files = event.target.files; //Lista de arquivos

        if (files && files.length > 0) {
            
            // Converte o FileList para array de file names
            const newFileNames = Array.from(files).map(file => file.name);            
            setSelectedFileNames(newFileNames);

        } else {
            setSelectedFileNames([]);
        }
    };


    return(
        <div className='home-container'>
        
            <div>
                <h1>Home</h1>

                <fieldset>
                    <form action="" method="post">

                        {/* Entrada de arquivos: Permite Arquivos do tipo .txt e .pdf */}
                        <label htmlFor="email-file" className="label-input-file"> {/* Container File */}
                            
                            {/* Texto de orientacao */}
                            <span className='span-file'>
                                Escolha um arquivo (.txt ou .pdf)
                            </span>
                            
                            <input type="file"
                            accept="text/plain,application/pdf" 
                            className='email-file' id="email-file" 
                            multiple
                            onChange={handleFileChange}
                            />

                        </label>    

                        {/* Feedback pro usuario: Exibe todos os arquivos selecionados */}
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

                        {/* Botao de enviar */}
                        <input type="submit" className='submit-button' value="Enviar" />
                    </form>

                </fieldset>
            </div>

        </div>
    )
}

export default Home