// ===============================================================================
// ---- Interfaces para tipagem dos dados recebidos do backend na homepage --------
// ================================================================================

export interface FileData {
    filename: string;
    content_type: string;
    size: number;
    extracted_text: string;
    category?: string;
    probabilities?: number[];
    suggested_response?: string;
}