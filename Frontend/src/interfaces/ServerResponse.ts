// ===============================================================================
// ---- Interfaces para tipagem dos dados recebidos do backend na homepage --------
// ================================================================================

import type { FileData } from "./FileData";

export interface ServerResponse {
    message: string;
    files?: FileData[];
}