import axios from 'axios'

// Em produção, define a URL do backend via variável de ambiente ou fallback para localhost
export const API_BASE_URL = process.env.API_URL || 'http://localhost:5000/api'

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000
})
