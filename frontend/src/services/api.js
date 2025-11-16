import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const sendMessage = async (query) => {
  try {
    const response = await api.post('/chat', { query })
    return response.data
  } catch (error) {
    if (error.response) {
      throw new Error(error.response.data.detail || 'Failed to get response')
    } else if (error.request) {
      throw new Error('Unable to connect to server. Please make sure the backend is running.')
    } else {
      throw new Error('An error occurred while sending the message')
    }
  }
}

export const getHealth = async () => {
  try {
    const response = await api.get('/health')
    return response.data
  } catch (error) {
    throw new Error('Health check failed')
  }
}

export const getSchemes = async () => {
  try {
    const response = await api.get('/schemes')
    return response.data
  } catch (error) {
    throw new Error('Failed to fetch schemes')
  }
}


