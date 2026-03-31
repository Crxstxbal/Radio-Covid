import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Crear instancia de axios con configuración base
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Para cookies de sesión
})

// Interceptor para manejar errores
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export const apiService = {
  // Estación de radio
  async getEstacionActiva() {
    const response = await api.get('/api/estacion/activa/')
    return response.data
  },

  async getStreamingInfo() {
    const response = await api.get('/api/estacion/activa/')
    const estacion = response.data
    return {
      stream_url: `${API_URL}/api/stream/`, // Usar nuestro proxy
      ...estacion
    }
  },

  // Oyentes
  async registrarConexion() {
    try {
      const response = await api.post('/api/oyentes/registrar_conexion/')
      return response.data
    } catch (error) {
      console.error('Error al registrar conexión:', error)
      throw error
    }
  },

  async actualizarActividad() {
    try {
      const response = await api.post('/api/oyentes/actualizar_actividad/')
      return response.data
    } catch (error) {
      console.error('Error al actualizar actividad:', error)
      throw error
    }
  },

  async registrarDesconexion() {
    try {
      const response = await api.post('/api/oyentes/desconexion/')
      return response.data
    } catch (error) {
      console.error('Error al registrar desconexión:', error)
      throw error
    }
  },

  async getConteoActual() {
    const response = await api.get('/api/oyentes/conteo_actual/')
    return response.data
  },

  // Estadísticas
  async getEstadisticasRecientes() {
    try {
      const response = await api.get('/api/estadisticas/recientes/')
      return response.data
    } catch (error) {
      console.error('Error al obtener estadísticas:', error)
      return null
    }
  },

  // Usuarios
  async login(email, password) {
    const response = await api.post('/api/auth/users/login/', { email, password })
    return response.data
  },

  async logout() {
    const response = await api.post('/api/auth/users/logout/')
    return response.data
  },

  async registrar(userData) {
    const response = await api.post('/api/auth/users/', userData)
    return response.data
  },

  async getPerfil() {
    const response = await api.get('/api/auth/users/perfil/')
    return response.data
  },

  async actualizarPerfil(userData) {
    const response = await api.patch('/api/auth/users/actualizar_perfil/', userData)
    return response.data
  },
}

export default api
