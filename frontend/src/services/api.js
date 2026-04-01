import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Generar o recuperar ID único para esta pestaña (sessionStorage = no se comparte entre pestañas)
const getTabId = () => {
  let tabId = sessionStorage.getItem('tab_id')
  if (!tabId) {
    tabId = 'tab_' + Math.random().toString(36).substring(2, 15) + '_' + Date.now()
    sessionStorage.setItem('tab_id', tabId)
  }
  return tabId
}

const TAB_ID = getTabId()
console.log('Tab ID:', TAB_ID)

// Crear instancia de axios con configuración base
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
})

// Interceptor para agregar tab_id a todas las requests POST
api.interceptors.request.use(
  (config) => {
    if (config.method === 'post' || config.method === 'POST') {
      config.data = config.data || {}
      config.data.tab_id = TAB_ID
    }
    return config
  },
  (error) => Promise.reject(error)
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
  async registrarConexion(usuario = '') {
    try {
      const response = await api.post('/api/oyentes/registrar_conexion/', { usuario })
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
