import React, { useState } from 'react'
import toast from 'react-hot-toast'

// ─── CSS inline con estilos exactos ─────────────────────────────────
const styles = `
  @import url('https://fonts.googleapis.com/css2?family=Black+Ops+One&family=Rajdhani:wght@400;600;700&display=swap');

  :root {
    --neon-red:    #FF1744;
    --neon-orange: #FF6D00;
    --neon-yellow: #FFD600;
    --neon-purple: #AA00FF;
    --dark-purple: #1A0033;
    --base-black:  #0A000F;
    --soft-white:  #F5F0FF;
  }

  .rl-page {
    font-family: 'Rajdhani', sans-serif;
    background: linear-gradient(135deg, #4A0080 0%, #2D0060 20%, #1A0033 50%, #0A000F 100%);
    min-height: 100vh;
    color: var(--soft-white);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 20px;
  }

  /* Card centrada */
  .rl-card {
    background: rgba(26,0,51,0.7);
    border: 1px solid rgba(170,0,255,0.4);
    border-radius: 20px;
    padding: 40px 32px;
    width: 100%;
    max-width: 400px;
    backdrop-filter: blur(20px);
    box-shadow: 0 0 60px rgba(170,0,255,0.15);
  }

  .rl-title {
    font-family: 'Black Ops One', cursive;
    font-size: 24px;
    text-align: center;
    background: linear-gradient(90deg, var(--neon-red), var(--neon-orange), var(--neon-yellow));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 8px;
    letter-spacing: 2px;
  }

  .rl-subtitle {
    text-align: center;
    font-size: 14px;
    color: rgba(245,240,255,0.5);
    margin-bottom: 32px;
    letter-spacing: 1px;
  }

  /* Form fields exactos como en la imagen */
  .rl-form-group {
    margin-bottom: 20px;
  }

  .rl-label {
    display: block;
    font-size: 12px;
    font-weight: 600;
    color: rgba(245,240,255,0.7);
    margin-bottom: 8px;
    letter-spacing: 1px;
    text-transform: uppercase;
  }

  .rl-input {
    width: 100%;
    padding: 14px 16px;
    background: rgba(10,0,15,0.5);
    border: 1px solid rgba(170,0,255,0.3);
    border-radius: 10px;
    color: var(--soft-white);
    font-size: 15px;
    font-family: 'Rajdhani', sans-serif;
    outline: none;
    transition: border-color 0.2s, box-shadow 0.2s;
  }

  .rl-input::placeholder {
    color: rgba(245,240,255,0.35);
  }

  .rl-input:focus {
    border-color: var(--neon-purple);
    box-shadow: 0 0 12px rgba(170,0,255,0.3);
  }

  /* Botón primario */
  .rl-btn-primary {
    width: 100%;
    padding: 14px;
    background: linear-gradient(90deg, var(--neon-red), var(--neon-orange));
    color: white;
    border: none;
    border-radius: 10px;
    font-family: 'Rajdhani', sans-serif;
    font-size: 16px;
    font-weight: 700;
    letter-spacing: 1px;
    cursor: pointer;
    margin-top: 10px;
    box-shadow: 0 4px 20px rgba(255,23,68,0.35);
    transition: transform 0.15s, box-shadow 0.2s;
  }

  .rl-btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 24px rgba(255,23,68,0.45);
  }

  .rl-btn-primary:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
  }

  /* Mensaje de éxito */
  .rl-success-message {
    text-align: center;
    padding: 20px;
  }

  .rl-success-icon {
    font-size: 48px;
    margin-bottom: 16px;
  }

  .rl-success-text {
    font-size: 16px;
    color: rgba(245,240,255,0.8);
    line-height: 1.5;
    margin-bottom: 24px;
  }

  /* Links */
  .rl-links {
    text-align: center;
    margin-top: 24px;
  }

  .rl-text {
    font-size: 14px;
    color: rgba(245,240,255,0.5);
  }

  .rl-link {
    color: var(--neon-purple);
    font-weight: 600;
    cursor: pointer;
    transition: color 0.2s;
  }

  .rl-link:hover {
    color: var(--neon-red);
  }

  .rl-back {
    text-align: center;
    margin-top: 16px;
    font-size: 13px;
    color: rgba(245,240,255,0.35);
    cursor: pointer;
    transition: color 0.2s;
  }

  .rl-back:hover {
    color: rgba(245,240,255,0.7);
  }
`;

const ForgotPassword = () => {
  const [email, setEmail] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isSuccess, setIsSuccess] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setIsLoading(true)

    try {
      const response = await fetch('http://localhost:8000/api/auth/password-reset/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email })
      })

      const data = await response.json()

      if (data.success) {
        setIsSuccess(true)
        toast.success('Correo enviado exitosamente')
      } else {
        toast.error(data.error?.email?.[0] || 'Error al enviar el correo')
      }
    } catch (error) {
      toast.error('Error de conexión. Intenta nuevamente.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="rl-page">
      <style>{styles}</style>
      <div className="rl-card">
        <h2 className="rl-title">RECUPERAR CONTRASEÑA</h2>
        <p className="rl-subtitle">
          {isSuccess ? 'Revisa tu correo' : 'Ingresa tu email para recibir instrucciones'}
        </p>

        {isSuccess ? (
          <div className="rl-success-message">
            <div className="rl-success-icon">✉️</div>
            <p className="rl-success-text">
              Se ha enviado un correo electrónico con instrucciones para restablecer tu contraseña.
              Revisa tu bandeja de entrada.
            </p>
            <button
              className="rl-btn-primary"
              onClick={() => window.location.href = '/login'}
            >
              VOLVER AL LOGIN
            </button>
          </div>
        ) : (
          <form onSubmit={handleSubmit}>
            <div className="rl-form-group">
              <label className="rl-label">Email</label>
              <input
                type="email"
                name="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="rl-input"
                placeholder="tu@email.com"
                autoFocus
              />
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="rl-btn-primary"
            >
              {isLoading ? 'Enviando...' : 'ENVIAR INSTRUCCIONES'}
            </button>
          </form>
        )}

        <div className="rl-links">
          <span className="rl-text">¿Recordaste tu contraseña? </span>
          <span className="rl-link" onClick={() => window.location.href = '/login'}>
            Iniciar sesión
          </span>
        </div>

        <div className="rl-back" onClick={() => window.location.href = '/'}>
          ← Volver al inicio
        </div>
      </div>
    </div>
  )
}

export default ForgotPassword
