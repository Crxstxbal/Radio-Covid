import React, { useState, useEffect } from 'react'
import { Users, TrendingUp, Activity, Radio } from 'lucide-react'
import { apiService } from '../services/api'
import { useWebSocket } from '../hooks/useWebSocket'

// Histogram data - simulated listening activity over time
const HISTOGRAM_DATA = [35, 52, 28, 65, 45, 78, 42, 88, 55, 72, 48, 95, 38, 82, 58, 68, 44, 75, 62, 90]

const UserCounter = () => {
  const [userCount, setUserCount] = useState(0)
  const [maxToday, setMaxToday] = useState(0)
  const [totalConnections, setTotalConnections] = useState(0)
  const [isConnected, setIsConnected] = useState(true)

  const { lastMessage } = useWebSocket('/ws/radio/')

  // Registrar conexión al montar el componente
  useEffect(() => {
    const registrarOyente = async () => {
      try {
        // Obtener nombre de usuario del localStorage
        const userData = JSON.parse(localStorage.getItem('user') || '{}')
        const username = userData.username || userData.email?.split('@')[0] || 'Anónimo'
        
        await apiService.registrarConexion(username)
        console.log('Conexión registrada para:', username)
      } catch (error) {
        console.error('Error al registrar conexión inicial:', error)
      }
    }
    registrarOyente()
  }, [])

  useEffect(() => {
    cargarEstadisticas()
    const interval = setInterval(cargarEstadisticas, 30000)
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    if (lastMessage) {
      try {
        const data = JSON.parse(lastMessage.data)
        if (data.type === 'conteo_actualizado') {
          setUserCount(data.oyentes_conectados)
        }
      } catch (e) {
        console.error('Error parsing WebSocket message:', e)
      }
    }
  }, [lastMessage])

  const cargarEstadisticas = async () => {
    try {
      const conteo = await apiService.getConteoActual()
      console.log('Conteo recibido:', conteo)
      
      // La API devuelve {conteo: number, timestamp: string}
      const count = conteo?.conteo ?? 0
      setUserCount(count)
      
      // Actualizar actividad del oyente actual
      await apiService.actualizarActividad()
      
      // Guardar en localStorage para referencia
      localStorage.setItem('user_count', count.toString())
      setMaxToday(prev => Math.max(prev, count))
      setTotalConnections(prev => prev + count)
    } catch (error) {
      console.error('Error al cargar estadísticas:', error)
    }
  }

  return (
    <div style={styles.container}>
      {/* Header */}
      <div style={styles.header}>
        <div style={styles.titleRow}>
          <Users size={18} style={{ color: '#AA00FF' }} />
          <span style={styles.title}>Oyentes en Vivo</span>
        </div>
        <div style={{
          width: '10px',
          height: '10px',
          borderRadius: '50%',
          background: isConnected ? '#FF1744' : 'rgba(245,240,255,0.3)',
          animation: isConnected ? 'rc-pulse 1.5s ease-in-out infinite' : 'none',
          boxShadow: isConnected ? '0 0 10px #FF1744' : 'none'
        }} />
      </div>

      {/* Main count */}
      <div style={styles.countSection}>
        <div style={styles.countNumber}>{userCount}</div>
        <div style={styles.countLabel}>
          {userCount === 1 ? 'persona escuchando' : 'personas escuchando'}
        </div>
      </div>

      {/* Animated Histogram */}
      <div style={styles.histogramContainer}>
        <div style={styles.histogramLabel}>
          <Activity size={12} />
          <span>Actividad reciente</span>
        </div>
        <div style={styles.histogramBars}>
          {HISTOGRAM_DATA.map((height, i) => (
            <div
              key={i}
              style={{
                ...styles.bar,
                height: `${height}%`,
                animationDelay: `${i * 0.1}s`,
                background: i % 3 === 0 ? '#FF1744' : i % 3 === 1 ? '#FF6D00' : '#AA00FF'
              }}
            />
          ))}
        </div>
      </div>

      {/* Stats grid */}
      <div style={styles.statsGrid}>
        <div style={styles.statBox}>
          <div style={styles.statIcon}><TrendingUp size={14} /></div>
          <div style={styles.statLabel}>Máximo hoy</div>
          <div style={styles.statValue}>{maxToday || userCount}</div>
        </div>
        <div style={styles.statBox}>
          <div style={styles.statIcon}><Radio size={14} /></div>
          <div style={styles.statLabel}>Total hoy</div>
          <div style={styles.statValue}>{totalConnections || userCount * 3}</div>
        </div>
      </div>

      {/* Connection status */}
      <div style={styles.statusBar}>
        <div style={{
          width: '6px',
          height: '6px',
          borderRadius: '50%',
          background: isConnected ? '#FF1744' : 'rgba(245,240,255,0.3)',
          animation: isConnected ? 'rc-pulse 1.5s ease-in-out infinite' : 'none'
        }} />
        <span style={styles.statusText}>
          {isConnected ? 'Conectado en tiempo real' : 'Conectándose...'}
        </span>
      </div>
    </div>
  )
}

const styles = {
  container: {
    background: 'rgba(26,0,51,0.7)',
    border: '1px solid rgba(170,0,255,0.3)',
    borderRadius: '16px',
    padding: '20px',
    backdropFilter: 'blur(20px)',
    fontFamily: 'Inter, system-ui, sans-serif',
    color: '#F5F0FF'
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '16px'
  },
  titleRow: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px'
  },
  title: {
    fontSize: '16px',
    fontWeight: '600',
    color: '#F5F0FF'
  },
  countSection: {
    textAlign: 'center',
    marginBottom: '20px'
  },
  countNumber: {
    fontSize: '48px',
    fontWeight: '700',
    background: 'linear-gradient(90deg, #FF1744 0%, #FF6D00 50%, #FFD600 100%)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
    backgroundClip: 'text',
    lineHeight: '1',
    marginBottom: '4px'
  },
  countLabel: {
    fontSize: '13px',
    color: 'rgba(245,240,255,0.55)'
  },
  histogramContainer: {
    marginBottom: '16px'
  },
  histogramLabel: {
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
    fontSize: '11px',
    color: 'rgba(245,240,255,0.5)',
    marginBottom: '8px',
    textTransform: 'uppercase',
    letterSpacing: '1px'
  },
  histogramBars: {
    display: 'flex',
    alignItems: 'flex-end',
    justifyContent: 'space-between',
    height: '50px',
    gap: '2px'
  },
  bar: {
    flex: '1',
    minWidth: '3px',
    borderRadius: '1px',
    animation: 'rc-histogram 1.2s ease-in-out infinite alternate',
    opacity: '0.8'
  },
  statsGrid: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: '10px',
    marginBottom: '16px'
  },
  statBox: {
    background: 'rgba(0,0,0,0.25)',
    border: '1px solid rgba(170,0,255,0.2)',
    borderRadius: '10px',
    padding: '12px',
    textAlign: 'center'
  },
  statIcon: {
    color: '#FF6D00',
    marginBottom: '4px',
    display: 'flex',
    justifyContent: 'center'
  },
  statLabel: {
    fontSize: '11px',
    color: 'rgba(245,240,255,0.5)',
    marginBottom: '2px'
  },
  statValue: {
    fontSize: '16px',
    fontWeight: '700',
    color: '#F5F0FF'
  },
  statusBar: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '8px',
    paddingTop: '14px',
    borderTop: '1px solid rgba(170,0,255,0.2)'
  },
  statusText: {
    fontSize: '11px',
    color: 'rgba(245,240,255,0.4)'
  }
}

export default UserCounter
