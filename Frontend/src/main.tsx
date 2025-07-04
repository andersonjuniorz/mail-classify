import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'

//Rotas
import AppRoutes from './AppRoutes'

//CSS Global
import './styles/global-style.css'


createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <AppRoutes />
  </StrictMode>,
)
