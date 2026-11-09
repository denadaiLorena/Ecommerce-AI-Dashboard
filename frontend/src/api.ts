import axios from 'axios'

// Em produção: VITE_API_URL=https://seu-backend.onrender.com (sem /api e sem barra no final)
// Localmente, sem a variável, usa o Flask na porta 5000
const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:5000'

export const API_BASE_URL = `${BASE_URL}/api`

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000
})