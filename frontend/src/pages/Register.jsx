import React, { useState } from 'react'

const Register = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password1: '',
    password2: ''
  })
  const [isLoading, setIsLoading] = useState(false)

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setIsLoading(true)

    try {
      // Validaciones básicas
      if (formData.password1 !== formData.password2) {
        alert('Las contraseñas no coinciden')
        setIsLoading(false)
        return
      }

      if (formData.password1.length < 6) {
        alert('La contraseña debe tener al menos 6 caracteres')
        setIsLoading(false)
        return
      }

      // Enviar datos como form-data (compatible con Django)
      const formDataToSend = new FormData()
      formDataToSend.append('username', formData.username)
      formDataToSend.append('email', formData.email)
      formDataToSend.append('password1', formData.password1)
      formDataToSend.append('password2', formData.password2)

      const response = await fetch('http://localhost:8000/api/auth/register/', {
        method: 'POST',
        body: formDataToSend
      })

      const data = await response.json()
      
      if (data.success) {
        // Guardar datos del usuario en localStorage
        localStorage.setItem('user_data', JSON.stringify(data.user))
        localStorage.setItem('is_logged_in', 'true')
        
        alert('¡Cuenta creada exitosamente! Bienvenido, ' + data.user.username)
        // Redirigir al home (ya está logueado)
        window.location.href = '/'
      } else {
        alert('Error: ' + data.error)
        console.error('Error response:', data)
      }
    } catch (error) {
      console.error('Error:', error)
      alert('Error de conexión. Intenta nuevamente.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen gradient-bg flex items-center justify-center">
      <div className="max-w-md w-full mx-4">
        <div className="card-panel rounded-2xl p-8">
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold text-soft-white mb-2">Crear Cuenta</h2>
            <p className="text-soft-white/60">Únete a nuestra comunidad de Radio Covid</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-soft-white/80 mb-2">
                Nombre de Usuario
              </label>
              <input
                type="text"
                name="username"
                value={formData.username}
                onChange={handleChange}
                required
                className="w-full px-4 py-3 bg-base-black/50 border border-neon-purple/30 rounded-lg text-soft-white placeholder-soft-white/40 focus:outline-none focus:ring-2 focus:ring-neon-purple focus:border-transparent"
                placeholder="Elige un nombre de usuario"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-soft-white/80 mb-2">
                Correo Electrónico
              </label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                required
                className="w-full px-4 py-3 bg-base-black/50 border border-neon-purple/30 rounded-lg text-soft-white placeholder-soft-white/40 focus:outline-none focus:ring-2 focus:ring-neon-purple focus:border-transparent"
                placeholder="tu@email.com"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-soft-white/80 mb-2">
                Contraseña
              </label>
              <input
                type="password"
                name="password1"
                value={formData.password1}
                onChange={handleChange}
                required
                className="w-full px-4 py-3 bg-base-black/50 border border-neon-purple/30 rounded-lg text-soft-white placeholder-soft-white/40 focus:outline-none focus:ring-2 focus:ring-neon-purple focus:border-transparent"
                placeholder="Crea una contraseña"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-soft-white/80 mb-2">
                Confirmar Contraseña
              </label>
              <input
                type="password"
                name="password2"
                value={formData.password2}
                onChange={handleChange}
                required
                className="w-full px-4 py-3 bg-base-black/50 border border-neon-purple/30 rounded-lg text-soft-white placeholder-soft-white/40 focus:outline-none focus:ring-2 focus:ring-neon-purple focus:border-transparent"
                placeholder="Confirma tu contraseña"
              />
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full btn-primary rounded-lg font-semibold py-3 px-4 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Creando cuenta...' : 'Crear Cuenta'}
            </button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-soft-white/60">
              ¿Ya tienes cuenta?{' '}
              <button
                onClick={() => window.location.href = '/login'}
                className="text-neon-purple hover:text-neon-red font-medium transition-colors"
              >
                Inicia Sesión
              </button>
            </p>
          </div>

          <div className="mt-4 text-center">
            <button
              onClick={() => window.location.href = '/'}
              className="text-soft-white/40 hover:text-soft-white text-sm transition-colors"
            >
              ← Volver al inicio
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Register
