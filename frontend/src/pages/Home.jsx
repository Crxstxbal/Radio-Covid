import React, { useState, useEffect } from 'react'
import Header from '../components/Header'
import Footer from '../components/Footer'
import RadioPlayer from '../components/RadioPlayer'
import UserCounter from '../components/UserCounter'
import Chat from '../components/Chat'
import djImage from '../img/DJ_virus_en_la_estación_radiofónica-removebg-preview.png'

// ─── CSS inline con fuentes y estilos exactos ─────────────────────────────────
const styles = `
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

  :root {
    --neon-red:    #FF1744;
    --neon-orange: #FF6D00;
    --neon-yellow: #FFD600;
    --neon-purple: #AA00FF;
    --dark-purple: #1A0033;
    --base-black:  #0A000F;
    --soft-white:  #F5F0FF;
  }

  .rc-page {
    font-family: 'Inter', system-ui, -apple-system, sans-serif;
    background: linear-gradient(135deg, #4A0080 0%, #2D0060 20%, #1A0033 50%, #0A000F 100%);
    min-height: 100vh;
    color: var(--soft-white);
    position: relative;
    overflow-x: hidden;
  }

  .rc-page::before {
    content: '';
    position: absolute;
    top: -200px; left: -200px;
    width: 600px; height: 600px;
    background: radial-gradient(circle, rgba(170,0,255,0.15) 0%, transparent 70%);
    pointer-events: none;
    z-index: 1;
  }

  .rc-hero {
    text-align: center;
    padding: 60px 32px 28px;
    position: relative;
    z-index: 5;
  }
  .rc-hero h1 {
    font-family: 'Inter', system-ui, sans-serif;
    font-weight: 800;
    font-size: clamp(48px, 8vw, 90px);
    line-height: 1;
    background: linear-gradient(90deg, var(--neon-red) 0%, var(--neon-orange) 40%, var(--neon-yellow) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 8px;
    letter-spacing: 2px;
  }
  .rc-hero p {
    font-size: 15px;
    color: rgba(245,240,255,0.55);
    letter-spacing: 2px;
    text-transform: uppercase;
  }

  .rc-main-grid {
    display: grid;
    grid-template-columns: 1fr 340px;
    gap: 24px;
    padding: 40px 32px 32px;
    max-width: 1100px;
    margin: 0 auto;
    position: relative;
    z-index: 5;
  }

  .rc-sidebar { display: flex; flex-direction: column; gap: 20px; }

  /* ─── RadioPlayer card ─── */
  .rc-card {
    background: rgba(26,0,51,0.7);
    border: 1px solid rgba(170,0,255,0.3);
    border-radius: 16px;
    padding: 28px;
    backdrop-filter: blur(20px);
  }
  .rc-now-playing {
    font-size: 11px;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: var(--neon-orange);
    margin-bottom: 18px;
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .rc-dot {
    width: 8px; height: 8px;
    background: var(--neon-red);
    border-radius: 50%;
    animation: rc-pulse 1s ease-in-out infinite;
  }
  @keyframes rc-pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.5; transform: scale(0.8); }
  }
  .rc-song-title {
    font-size: 26px;
    font-weight: 700;
    color: var(--soft-white);
    margin-bottom: 4px;
    letter-spacing: 0.5px;
  }
  .rc-song-artist {
    font-size: 14px;
    color: rgba(245,240,255,0.55);
    margin-bottom: 22px;
  }
  .rc-waveform {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 3px;
    height: 70px;
    margin-bottom: 20px;
  }
  .rc-wave-bar {
    width: 4px;
    border-radius: 2px;
    animation: rc-wave var(--dur, 0.6s) ease-in-out infinite alternate;
  }
  .rc-wave-bar.paused { animation-play-state: paused; }
  @keyframes rc-wave {
    from { transform: scaleY(0.3); opacity: 0.4; }
    to   { transform: scaleY(1);   opacity: 1; }
  }

  .rc-controls {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
    margin-bottom: 18px;
  }
  .rc-ctrl-btn {
    background: rgba(255,255,255,0.08);
    border: none;
    color: var(--soft-white);
    width: 36px;
    height: 36px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.2s;
  }
  .rc-ctrl-btn:hover { background: rgba(255,255,255,0.15); }
  .rc-play-btn {
    width: 64px;
    height: 64px;
    border-radius: 50%;
    border: none;
    background: linear-gradient(135deg, var(--neon-red), var(--neon-orange));
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    box-shadow: 0 4px 20px rgba(255,23,68,0.4);
    transition: transform 0.15s, box-shadow 0.15s;
  }
  .rc-play-btn:hover { transform: scale(1.05); box-shadow: 0 6px 28px rgba(255,23,68,0.5); }
  .rc-play-btn.playing {
    background: linear-gradient(135deg, var(--neon-purple), var(--neon-red));
    box-shadow: 0 4px 20px rgba(170,0,255,0.4);
  }
  .rc-volume-row {
    display: flex;
    align-items: center;
    gap: 10px;
  }
  .rc-vol-icon {
    background: none;
    border: none;
    color: rgba(245,240,255,0.6);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 4px;
  }
  .rc-vol-slider {
    flex: 1;
    height: 4px;
    -webkit-appearance: none;
    appearance: none;
    background: rgba(255,255,255,0.15);
    border-radius: 2px;
    outline: none;
  }
  .rc-vol-slider::-webkit-slider-thumb {
    -webkit-appearance: none;
    width: 14px;
    height: 14px;
    background: var(--neon-orange);
    border-radius: 50%;
    cursor: pointer;
    box-shadow: 0 0 10px rgba(255,109,0,0.5);
  }
  .rc-vol-slider::-moz-range-thumb {
    width: 14px;
    height: 14px;
    background: var(--neon-orange);
    border-radius: 50%;
    cursor: pointer;
    border: none;
    box-shadow: 0 0 10px rgba(255,109,0,0.5);
  }

  .rc-features-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    padding: 0 32px;
    max-width: 1100px;
    margin: 0 auto 24px;
    position: relative;
    z-index: 5;
  }
  .rc-features-left {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }
  .rc-feat-card {
    background: rgba(26,0,51,0.5);
    border: 1px solid rgba(170,0,255,0.2);
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    backdrop-filter: blur(10px);
    flex: 1;
  }
  .rc-feat-card-dj {
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(26,0,51,0.5);
    border: 1px solid rgba(170,0,255,0.2);
    border-radius: 12px;
    padding: 20px;
    backdrop-filter: blur(10px);
  }
  .rc-dj-image {
    max-height: 180px;
    width: auto;
    object-fit: contain;
    filter: drop-shadow(0 0 15px rgba(170,0,255,0.5));
  }
  .rc-feat-icon { font-size: 24px; margin-bottom: 10px; }
  .rc-feat-title { font-size: 16px; font-weight: 700; color: var(--soft-white); margin-bottom: 6px; }
  .rc-feat-desc { font-size: 13px; color: rgba(245,240,255,0.45); }

  .rc-cta-section {
    padding: 0 32px 40px;
    max-width: 480px;
    margin: 0 auto;
    position: relative;
    z-index: 5;
  }
  .rc-cta-card {
    background: rgba(26,0,51,0.65);
    border: 1px solid rgba(170,0,255,0.3);
    border-radius: 20px;
    padding: 32px;
    text-align: center;
    backdrop-filter: blur(20px);
    box-shadow: 0 0 40px rgba(170,0,255,0.1);
  }
  .rc-cta-title { font-size: 20px; font-weight: 700; margin-bottom: 20px; color: var(--soft-white); }
  .rc-btn-primary {
    display: block;
    width: 100%;
    padding: 14px;
    background: linear-gradient(135deg, var(--neon-red), var(--neon-orange));
    color: white;
    border: none;
    border-radius: 12px;
    font-family: 'Inter', system-ui, sans-serif;
    font-size: 15px;
    font-weight: 700;
    letter-spacing: 2px;
    cursor: pointer;
    margin-bottom: 12px;
    box-shadow: 0 4px 20px rgba(255,23,68,0.4), 0 0 30px rgba(255,23,68,0.3), inset 0 1px 0 rgba(255,255,255,0.2);
    transition: all 0.2s ease;
    text-transform: uppercase;
    text-shadow: 0 0 10px rgba(255,255,255,0.3);
  }
  .rc-btn-primary:hover { 
    transform: translateY(-2px); 
    box-shadow: 0 6px 25px rgba(255,23,68,0.6), 0 0 50px rgba(255,23,68,0.4), inset 0 1px 0 rgba(255,255,255,0.3);
    text-shadow: 0 0 15px rgba(255,255,255,0.5);
  }
  .rc-btn-secondary {
    display: block;
    width: 100%;
    padding: 14px;
    background: transparent;
    color: var(--soft-white);
    border: 2px solid rgba(170,0,255,0.6);
    border-radius: 12px;
    font-family: 'Inter', system-ui, sans-serif;
    font-size: 15px;
    font-weight: 700;
    letter-spacing: 2px;
    cursor: pointer;
    transition: all 0.2s ease;
    text-transform: uppercase;
    margin-bottom: 0;
    box-shadow: 0 0 20px rgba(170,0,255,0.2), inset 0 1px 0 rgba(255,255,255,0.1);
    text-shadow: 0 0 8px rgba(170,0,255,0.3);
  }
  .rc-btn-secondary:hover { 
    border-color: var(--neon-purple); 
    background: rgba(170,0,255,0.15);
    box-shadow: 0 0 30px rgba(170,0,255,0.4), inset 0 1px 0 rgba(255,255,255,0.2);
    text-shadow: 0 0 15px rgba(170,0,255,0.5);
    color: white;
  }
  .rc-cta-hint { font-size: 13px; color: rgba(245,240,255,0.35); margin-top: 14px; }

  .rc-loading {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--base-black);
  }
  .rc-loading-wave {
    display: flex;
    gap: 4px;
    margin-bottom: 24px;
    justify-content: center;
  }
  .rc-loading-bar {
    width: 6px;
    height: 30px;
    border-radius: 3px;
    animation: rc-loading-anim 0.8s ease-in-out infinite alternate;
  }
  .rc-loading-bar:nth-child(1) { background: var(--neon-red); animation-delay: 0s; }
  .rc-loading-bar:nth-child(2) { background: var(--neon-orange); animation-delay: 0.1s; }
  .rc-loading-bar:nth-child(3) { background: var(--neon-yellow); animation-delay: 0.2s; }
  .rc-loading-bar:nth-child(4) { background: var(--neon-orange); animation-delay: 0.3s; }
  .rc-loading-bar:nth-child(5) { background: var(--neon-red); animation-delay: 0.4s; }

  @keyframes rc-loading-anim {
    from { transform: scaleY(0.5); opacity: 0.5; }
    to { transform: scaleY(1); opacity: 1; }
  }

  @keyframes rc-histogram {
    from { transform: scaleY(0.3); opacity: 0.4; }
    to { transform: scaleY(1); opacity: 1; }
  }

  @media (max-width: 900px) {
    .rc-main-grid { grid-template-columns: 1fr; }
    .rc-features-grid { grid-template-columns: 1fr; }
    .rc-dj-image { max-height: 150px; }
    .rc-main-grid, .rc-features-grid, .rc-cta-section { padding-left: 16px; padding-right: 16px; }
    .rc-hero { padding: 24px 16px; }
  }
`;

const Home = () => {
  const [isLoading, setIsLoading] = useState(true)
  const [user, setUser] = useState(null)

  useEffect(() => {
    const timer = setTimeout(() => setIsLoading(false), 1500)
    return () => clearTimeout(timer)
  }, [])

  // Verificar si hay usuario logueado
  useEffect(() => {
    const checkUser = () => {
      const userData = localStorage.getItem('user_data')
      const isLoggedIn = localStorage.getItem('is_logged_in')
      if (userData && isLoggedIn === 'true') {
        try {
          setUser(JSON.parse(userData))
        } catch (e) {
          console.error('Error parsing user data:', e)
        }
      }
    }
    checkUser()
    // Escuchar cambios en localStorage
    window.addEventListener('storage', checkUser)
    return () => window.removeEventListener('storage', checkUser)
  }, [])

  if (isLoading) {
    return (
      <div className="rc-loading">
        <style>{styles}</style>
        <div className="text-center">
          <div className="rc-loading-wave">
            <div className="rc-loading-bar"></div>
            <div className="rc-loading-bar"></div>
            <div className="rc-loading-bar"></div>
            <div className="rc-loading-bar"></div>
            <div className="rc-loading-bar"></div>
          </div>
          <h1 style={{ fontSize: '24px', fontWeight: '600', color: '#F5F0FF', fontFamily: 'Inter, system-ui, sans-serif', letterSpacing: '1px' }}>
            Cargando Radio Covid...
          </h1>
        </div>
      </div>
    )
  }

  return (
    <div className="rc-page">
      <style>{styles}</style>
      <Header />

      <section className="rc-hero">
        <h1>RADIO COVID</h1>
        <p>La mejor música 24/7 · Conoce cuántas personas están escuchando</p>
      </section>

      <div className="rc-main-grid">
        <RadioPlayer />

        <div className="rc-sidebar">
          <UserCounter />
        </div>
      </div>

      <div className="rc-features-grid">
        <div className="rc-features-left">
          <div className="rc-feat-card">
            <div className="rc-feat-title">Música Variada</div>
            <div className="rc-feat-desc">Los mejores éxitos y clásicos de todos los tiempos</div>
          </div>
          <div className="rc-feat-card">
            <div className="rc-feat-title">Programas en Vivo</div>
            <div className="rc-feat-desc">Con los mejores locutores de la región</div>
          </div>
        </div>
        <div className="rc-feat-card-dj">
          <img src={djImage} alt="DJ en la radio" className="rc-dj-image" />
        </div>
      </div>

      <div className="rc-cta-section">
        <div className="rc-cta-card">
          {user ? (
            <>
              <div className="rc-cta-title">Bienvenido, {user.username}</div>
              <p style={{ fontSize: '15px', color: 'rgba(245,240,255,0.6)', marginBottom: '20px' }}>
                Gracias por ser parte de nuestra comunidad. Disfruta de la mejor música 24/7.
              </p>
              <button className="rc-btn-primary" onClick={() => window.location.href = '/'}>
                Explorar Contenido
              </button>
            </>
          ) : (
            <>
              <div className="rc-cta-title">Únete a Nuestra Comunidad</div>
              <button className="rc-btn-primary" onClick={() => window.location.href = '/login'}>
                Iniciar Sesión
              </button>
              <button className="rc-btn-secondary" onClick={() => window.location.href = '/register'}>
                Crear Cuenta
              </button>
              <p className="rc-cta-hint">Regístrate para acceder a funciones exclusivas y chat en vivo</p>
            </>
          )}
        </div>
      </div>

      <Footer />
      <Chat user={user} />
    </div>
  )
}

export default Home