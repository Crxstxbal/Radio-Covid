import React, { useState, useEffect, useRef } from 'react'
import { motion } from 'framer-motion'
import { Play, Pause, Volume2, VolumeX } from 'lucide-react'
import toast from 'react-hot-toast'
import { apiService } from '../services/api'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const RadioPlayer = () => {
  const [isPlaying, setIsPlaying] = useState(false)
  const [volume, setVolume] = useState(() => {
    // Recuperar volumen guardado o usar default 0.72
    const savedVolume = localStorage.getItem('radio_volume')
    return savedVolume ? parseFloat(savedVolume) : 0.72
  })
  const [isMuted, setIsMuted] = useState(() => {
    // Recuperar estado de mute
    const savedMuted = localStorage.getItem('radio_muted')
    return savedMuted === 'true'
  })
  const [isConnecting, setIsConnecting] = useState(false)
  const [estacion, setEstacion] = useState(null)
  const audioRef = useRef(null)

  // Guardar volumen cuando cambie
  useEffect(() => {
    localStorage.setItem('radio_volume', volume.toString())
  }, [volume])

  // Guardar estado de mute
  useEffect(() => {
    localStorage.setItem('radio_muted', isMuted.toString())
  }, [isMuted])

  // Guardar estado de reproducción
  useEffect(() => {
    localStorage.setItem('radio_was_playing', isPlaying.toString())
  }, [isPlaying])

  // Auto-reproducir si estaba escuchando antes
  useEffect(() => {
    const wasPlaying = localStorage.getItem('radio_was_playing') === 'true'
    if (wasPlaying && estacion) {
      // Esperar a que el audio esté listo
      const timer = setTimeout(() => {
        if (audioRef.current) {
          togglePlayPause()
        }
      }, 1000)
      return () => clearTimeout(timer)
    }
  }, [estacion])

  useEffect(() => {
    cargarEstacion()
    return () => {
      if (audioRef.current) {
        audioRef.current.pause()
      }
    }
  }, [])

  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.volume = isMuted ? 0 : volume
    }
  }, [volume, isMuted])

  useEffect(() => {
    if (!audioRef.current || !estacion) return

    const audio = audioRef.current
    
    const handleCanPlay = () => {
      console.log('Audio listo para reproducir')
    }
    
    const handleError = (e) => {
      console.error('Error de audio:', e)
      toast.error('Error al cargar el audio: ' + (e.target.error?.message || 'Error desconocido'))
      setIsPlaying(false)
      setIsConnecting(false)
    }

    const handleLoadStart = () => {
      console.log('Comenzando a cargar audio')
    }

    const handleLoad = () => {
      console.log('Audio cargado completamente')
    }

    audio.addEventListener('canplay', handleCanPlay)
    audio.addEventListener('error', handleError)
    audio.addEventListener('loadstart', handleLoadStart)
    audio.addEventListener('load', handleLoad)
    
    return () => {
      audio.removeEventListener('canplay', handleCanPlay)
      audio.removeEventListener('error', handleError)
      audio.removeEventListener('loadstart', handleLoadStart)
      audio.removeEventListener('load', handleLoad)
    }
  }, [estacion])

  const cargarEstacion = async () => {
    try {
      const data = await apiService.getEstacionActiva()
      // SIEMPRE usar proxy del backend para evitar bloqueos CORS y de User-Agent
      const estacionFinal = {
        ...data,
        stream_url: `${API_URL}/api/stream/`
      }
      setEstacion(estacionFinal)
    } catch (error) {
      toast.error('Error al cargar la estación de radio')
    }
  }

  const togglePlayPause = async () => {
    if (!audioRef.current || !estacion) {
      toast.error('No hay estación configurada')
      return
    }

    try {
      if (isPlaying) {
        audioRef.current.pause()
        setIsPlaying(false)
        toast.success('Radio pausada')
      } else {
        setIsConnecting(true)
        
        if (audioRef.current.readyState < 2) {
          audioRef.current.load()
        }
        
        await audioRef.current.play()
        setIsPlaying(true)
        toast.success('¡Conectado a la radio!')
      }
    } catch (error) {
      console.error('Error en reproductor:', error)
      toast.error('Error al ' + (isPlaying ? 'pausar' : 'reproducir') + ' la radio')
      setIsPlaying(false)
    } finally {
      setIsConnecting(false)
    }
  }

  const toggleMute = () => {
    setIsMuted(!isMuted)
  }

  const handleVolumeChange = (e) => {
    const newVolume = parseFloat(e.target.value)
    setVolume(newVolume)
    if (newVolume > 0 && isMuted) {
      setIsMuted(false)
    }
  }

  // Waveform bars data - purely visual for radio
  const WAVE_HEIGHTS = [30,60,45,80,35,70,55,90,40,65,50,85,38,72,48,88,42,68,52,95,36,74,46,82,55,70,42,78,50,88,44,66]
  const WAVE_COLORS  = ["#FF1744","#FF6D00","#FFD600","#FF6D00","#FF1744","#AA00FF","#FF6D00","#FF1744"]

  return (
    <div className="rc-card">
      {estacion && (
        <audio
          ref={audioRef}
          src={estacion.stream_url}
          type="audio/mpeg"
          crossOrigin="anonymous"
          preload="none"
        />
      )}

      {/* Radio status header */}
      <div className="rc-now-playing">
        <span className="rc-dot" />
        {isPlaying ? 'Radio en vivo' : 'Radio detenida'}
      </div>

      {/* Station name */}
      <div className="rc-song-title">Radio Covid</div>
      <div className="rc-song-artist">Transmisión en vivo 24/7</div>

      {/* Waveform visualization */}
      <div className="rc-waveform">
        {WAVE_HEIGHTS.map((h, i) => (
          <div
            key={i}
            className={`rc-wave-bar${isPlaying ? "" : " paused"}`}
            style={{
              height: `${h}%`,
              background: WAVE_COLORS[i % WAVE_COLORS.length],
              "--dur": `${(0.5 + (i % 7) * 0.12).toFixed(2)}s`,
              animationDelay: `${(i * 0.04).toFixed(2)}s`,
            }}
          />
        ))}
      </div>

      {/* Controls - solo play/pause para radio */}
      <div className="rc-controls" style={{ marginBottom: '24px' }}>
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={togglePlayPause}
          disabled={isConnecting || !estacion}
          className={`rc-play-btn${isPlaying ? " playing" : ""}`}
        >
          {isConnecting ? (
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white"></div>
          ) : isPlaying ? (
            <Pause size={28} />
          ) : (
            <Play size={28} style={{ marginLeft: 2 }} />
          )}
        </motion.button>
      </div>

      {/* Volume control */}
      <div className="rc-volume-row">
        <button onClick={toggleMute} className="rc-vol-icon">
          {isMuted || volume === 0 ? <VolumeX size={16} /> : <Volume2 size={16} />}
        </button>
        <input 
          type="range" 
          className="rc-vol-slider" 
          min="0" 
          max="1" 
          step="0.01"
          value={isMuted ? 0 : volume}
          onChange={handleVolumeChange}
        />
        <span className="rc-vol-icon" style={{ fontSize: '11px', minWidth: '28px', textAlign: 'right' }}>
          {Math.round((isMuted ? 0 : volume) * 100)}%
        </span>
      </div>

      {/* Status indicator */}
      <div style={{ textAlign: 'center', marginTop: '16px', fontSize: '11px' }}>
        {isPlaying ? (
          <span style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px', color: '#FF1744' }}>
            <span style={{ width: '6px', height: '6px', background: '#FF1744', borderRadius: '50%', animation: 'rc-pulse 1s ease-in-out infinite' }}></span>
            <span style={{ fontWeight: 600, letterSpacing: '1px' }}>EN VIVO</span>
          </span>
        ) : (
          <span style={{ color: 'rgba(245,240,255,0.4)' }}>Presiona play para conectar</span>
        )}
      </div>
    </div>
  )
}

export default RadioPlayer
