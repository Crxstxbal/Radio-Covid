import React, { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Send, MessageSquare, Users, X, Lock, Shield, Ban, AlertTriangle, Trash2, Gavel } from 'lucide-react'
import { useWebSocket } from '../hooks/useWebSocket'
import toast from 'react-hot-toast'

const Chat = ({ user }) => {
  const [messages, setMessages] = useState([])
  const [newMessage, setNewMessage] = useState('')
  const [onlineUsers, setOnlineUsers] = useState(0)
  const [isExpanded, setIsExpanded] = useState(false)
  const [hasUnread, setHasUnread] = useState(false)
  const [advertencias, setAdvertencias] = useState([])
  const [showAdvertencias, setShowAdvertencias] = useState(false)
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)
  const messageIdsRef = useRef(new Set())

  // Estados para moderación
  const [selectedMessage, setSelectedMessage] = useState(null)
  const [showModeracionModal, setShowModeracionModal] = useState(false)
  const [moderacionTipo, setModeracionTipo] = useState(null)
  const [moderacionRazon, setModeracionRazon] = useState('')
  const [bloqueoPermanente, setBloqueoPermanente] = useState(true)
  const [bloqueoDuracion, setBloqueoDuracion] = useState(24)

  const { lastMessage, sendMessage, isConnected } = useWebSocket('/ws/chat/')

  // Lista de administradores (usernames que pueden moderar)
  const adminUsers = ['admin', 'moderador', 'mod']
  const esModerador = user && (user.is_staff || user.is_superuser || adminUsers.includes(user.username?.toLowerCase()))

  // Cargar mensajes históricos
  useEffect(() => {
    cargarMensajesHistoricos()
    if (user) {
      cargarAdvertenciasPendientes()
    }
  }, [user])

  // Scroll al último mensaje cuando se recibe uno nuevo
  useEffect(() => {
    if (messagesEndRef.current && isExpanded) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [messages, isExpanded])

  // Manejar mensajes del WebSocket
  useEffect(() => {
    if (lastMessage) {
      try {
        const data = JSON.parse(lastMessage.data)
        
        switch (data.type) {
          case 'mensaje_chat':
            // Evitar duplicados: verificar si el ID ya existe
            const msgId = data.id || `${data.usuario}-${data.timestamp}`
            if (messageIdsRef.current.has(msgId)) {
              break // Mensaje duplicado, ignorar
            }
            messageIdsRef.current.add(msgId)
            
            // Si el mensaje tiene un temp_id, reemplazar el mensaje temporal
            if (data.temp_id && messageIdsRef.current.has(data.temp_id)) {
              setMessages(prev => prev.map(msg => 
                msg.id === data.temp_id 
                  ? { id: data.id, usuario: data.usuario, mensaje: data.mensaje, timestamp: data.timestamp }
                  : msg
              ))
            } else {
              // Agregar mensaje nuevo
              setMessages(prev => [...prev, {
                id: data.id || msgId,
                usuario: data.usuario,
                mensaje: data.mensaje,
                timestamp: data.timestamp || new Date().toISOString()
              }])
            }
            if (!isExpanded) {
              setHasUnread(true)
            }
            // Actualizar advertencias si vienen en el mensaje
            if (data.advertencias_usuario && data.advertencias_usuario.length > 0 && data.usuario === user?.username) {
              setAdvertencias(data.advertencias_usuario)
              if (!showAdvertencias) {
                toast.warning(`Tienes ${data.advertencias_usuario.length} advertencia(s) pendiente(s)`)
              }
            }
            break
          case 'usuarios_conectados':
            setOnlineUsers(data.cantidad)
            break
          case 'historial_mensajes':
            // Limpiar IDs al cargar historial
            messageIdsRef.current.clear()
            data.mensajes?.forEach(msg => {
              const id = msg.id || `${msg.usuario}-${msg.timestamp}`
              messageIdsRef.current.add(id)
            })
            setMessages(data.mensajes || [])
            break
          case 'error_chat':
            toast.error(data.error)
            break
          case 'notificacion_moderacion':
            if (data.accion === 'bloqueo' && data.username_objetivo === user?.username) {
              toast.error(`Has sido bloqueado del chat. Razón: ${data.razon}`)
            } else if (data.accion === 'advertencia' && data.username_objetivo === user?.username) {
              toast.warning(`Has recibido una advertencia: ${data.razon}`)
              cargarAdvertenciasPendientes()
            }
            break
          default:
            break
        }
      } catch (e) {
        console.error('Error parsing chat message:', e)
      }
    }
  }, [lastMessage, isExpanded])

  const cargarMensajesHistoricos = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/chat/mensajes/')
      if (response.ok) {
        const data = await response.json()
        if (data.mensajes) {
          messageIdsRef.current.clear()
          data.mensajes.forEach(msg => {
            const id = msg.id || `${msg.usuario}-${msg.timestamp}`
            messageIdsRef.current.add(id)
          })
          setMessages(data.mensajes)
        }
      }
    } catch (error) {
      console.log('No se pudieron cargar mensajes históricos')
    }
  }

  const cargarAdvertenciasPendientes = async () => {
    if (!user) return
    try {
      const response = await fetch(`http://localhost:8000/api/chat/advertencias/${user.username}/`)
      if (response.ok) {
        const data = await response.json()
        if (data.success) {
          setAdvertencias(data.advertencias || [])
          if (data.no_leidas > 0) {
            setShowAdvertencias(true)
          }
        }
      }
    } catch (error) {
      console.log('No se pudieron cargar advertencias')
    }
  }

  const marcarAdvertenciasLeidas = async () => {
    if (!user) return
    try {
      await fetch(`http://localhost:8000/api/chat/advertencias/${user.username}/?marcar_leidas=true`)
      setAdvertencias([])
      setShowAdvertencias(false)
    } catch (error) {
      console.log('No se pudieron marcar advertencias como leídas')
    }
  }

  const handleSendMessage = async (e) => {
    e.preventDefault()
    
    if (!newMessage.trim()) return
    
    if (!user) {
      toast.error('Debes iniciar sesión para enviar mensajes')
      return
    }

    // Verificar si el usuario está bloqueado antes de enviar
    try {
      const response = await fetch(`http://localhost:8000/api/chat/bloqueados/${user.username}/`)
      if (response.ok) {
        const data = await response.json()
        if (data.bloqueado) {
          toast.error(`Estás bloqueado del chat. Razón: ${data.bloqueo_info?.razon || 'Contacta a un administrador'}`)
          return
        }
      }
    } catch (error) {
      console.log('No se pudo verificar bloqueo')
    }

    // Generar ID único temporal para evitar duplicados
    const tempId = `temp-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
    const timestamp = new Date().toISOString()
    
    // Agregar el mensaje localmente inmediatamente (optimistic UI)
    const mensajeLocal = {
      id: tempId,
      usuario: user.username,
      mensaje: newMessage.trim(),
      timestamp: timestamp,
      temp: true
    }
    
    // Agregar a la lista de IDs para evitar duplicados cuando regrese del servidor
    messageIdsRef.current.add(tempId)
    setMessages(prev => [...prev, mensajeLocal])

    const mensajeData = {
      type: 'mensaje_chat',
      id: tempId, // Incluir el ID temporal para que el servidor lo devuelva
      usuario: user.username,
      mensaje: newMessage.trim(),
      timestamp: timestamp
    }

    sendMessage(JSON.stringify(mensajeData))

    try {
      await fetch('http://localhost:8000/api/chat/mensajes/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          usuario: user.username,
          mensaje: newMessage.trim()
        })
      })
    } catch (error) {
      console.error('Error guardando mensaje:', error)
    }

    setNewMessage('')
  }

  const toggleChat = () => {
    setIsExpanded(!isExpanded)
    if (!isExpanded) {
      setHasUnread(false)
      setTimeout(() => inputRef.current?.focus(), 100)
    }
  }

  const formatTime = (timestamp) => {
    if (!timestamp) return ''
    const date = new Date(timestamp)
    return date.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })
  }

  // Si no hay usuario, mostrar versión bloqueada
  if (!user) {
    return (
      <div className="rc-chat-container">
        <style>{`
          .rc-chat-container {
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 100;
          }
          .rc-chat-locked {
            background: rgba(26,0,51,0.9);
            border: 1px solid rgba(170,0,255,0.4);
            border-radius: 16px;
            padding: 16px 20px;
            backdrop-filter: blur(20px);
            display: flex;
            align-items: center;
            gap: 12px;
            color: var(--soft-white);
            box-shadow: 0 4px 30px rgba(0,0,0,0.3);
            cursor: pointer;
            transition: all 0.2s;
          }
          .rc-chat-locked:hover {
            border-color: var(--neon-purple);
            transform: translateY(-2px);
          }
          .rc-chat-lock-icon {
            width: 40px;
            height: 40px;
            background: linear-gradient(135deg, var(--neon-red), var(--neon-orange));
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
          }
          .rc-chat-lock-text {
            font-size: 14px;
            font-weight: 600;
          }
          .rc-chat-lock-hint {
            font-size: 11px;
            color: rgba(245,240,255,0.5);
            margin-top: 2px;
          }
        `}</style>
        <motion.div 
          className="rc-chat-locked"
          onClick={() => window.location.href = '/login'}
          whileHover={{ scale: 1.02 }}
        >
          <div className="rc-chat-lock-icon">
            <Lock size={18} color="white" />
          </div>
          <div>
            <div className="rc-chat-lock-text">Chat en Vivo</div>
            <div className="rc-chat-lock-hint">Inicia sesión para participar</div>
          </div>
        </motion.div>
      </div>
    )
  }

  return (
    <div className={`rc-chat-container ${isExpanded ? 'expanded' : ''}`}>
      <style>{`
        .rc-chat-container {
          position: fixed;
          bottom: 20px;
          right: 20px;
          z-index: 100;
          transition: all 0.3s ease;
        }
        .rc-chat-container.expanded {
          width: 380px;
          height: 500px;
        }
        .rc-chat-button {
          background: linear-gradient(135deg, var(--neon-red), var(--neon-orange));
          border: none;
          border-radius: 50%;
          width: 60px;
          height: 60px;
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          box-shadow: 0 4px 20px rgba(255,23,68,0.4), 0 0 30px rgba(255,23,68,0.2);
          position: relative;
          transition: all 0.2s;
        }
        .rc-chat-button:hover {
          transform: scale(1.1);
          box-shadow: 0 6px 25px rgba(255,23,68,0.5), 0 0 40px rgba(255,23,68,0.3);
        }
        .rc-chat-badge {
          position: absolute;
          top: -5px;
          right: -5px;
          width: 22px;
          height: 22px;
          background: var(--neon-purple);
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 11px;
          font-weight: 700;
          color: white;
          animation: rc-pulse-badge 2s infinite;
        }
        @keyframes rc-pulse-badge {
          0%, 100% { transform: scale(1); }
          50% { transform: scale(1.1); }
        }
        .rc-chat-window {
          background: rgba(26,0,51,0.95);
          border: 1px solid rgba(170,0,255,0.4);
          border-radius: 20px;
          height: 100%;
          display: flex;
          flex-direction: column;
          overflow: hidden;
          backdrop-filter: blur(20px);
          box-shadow: 0 10px 40px rgba(0,0,0,0.4);
        }
        .rc-chat-header {
          padding: 16px 20px;
          border-bottom: 1px solid rgba(170,0,255,0.2);
          display: flex;
          align-items: center;
          justify-content: space-between;
          background: rgba(170,0,255,0.1);
        }
        .rc-chat-title {
          display: flex;
          align-items: center;
          gap: 10px;
          font-weight: 700;
          color: var(--soft-white);
          font-size: 15px;
        }
        .rc-chat-status {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 12px;
          color: rgba(245,240,255,0.6);
        }
        .rc-chat-status-dot {
          width: 8px;
          height: 8px;
          background: #00E676;
          border-radius: 50%;
          animation: rc-pulse-dot 1.5s infinite;
        }
        @keyframes rc-pulse-dot {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
        .rc-chat-close {
          background: none;
          border: none;
          color: rgba(245,240,255,0.6);
          cursor: pointer;
          padding: 4px;
          transition: color 0.2s;
        }
        .rc-chat-close:hover {
          color: var(--neon-red);
        }
        .rc-chat-moderator-badge {
          display: flex;
          align-items: center;
          gap: 4px;
          font-size: 10px;
          color: var(--neon-purple);
          background: rgba(170,0,255,0.2);
          padding: 2px 6px;
          border-radius: 4px;
          margin-left: 8px;
        }
        .rc-chat-advertencias-banner {
          background: linear-gradient(135deg, rgba(255,193,7,0.2), rgba(255,152,0,0.2));
          border: 1px solid rgba(255,193,7,0.4);
          border-radius: 12px;
          padding: 12px 16px;
          margin-bottom: 12px;
        }
        .rc-chat-advertencias-header {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 12px;
          font-weight: 600;
          color: #FFC107;
          margin-bottom: 8px;
        }
        .rc-chat-advertencia-item {
          font-size: 11px;
          color: rgba(245,240,255,0.8);
          padding: 6px 0;
          border-bottom: 1px solid rgba(255,193,7,0.2);
        }
        .rc-chat-advertencia-item:last-child {
          border-bottom: none;
        }
        .rc-chat-advertencias-close {
          font-size: 10px;
          color: rgba(245,240,255,0.5);
          cursor: pointer;
          text-align: right;
          margin-top: 8px;
        }
        .rc-chat-advertencias-close:hover {
          color: var(--soft-white);
        }
        .rc-chat-messages {
          flex: 1;
          overflow-y: auto;
          padding: 16px 20px;
          display: flex;
          flex-direction: column;
          gap: 12px;
        }
        .rc-chat-messages::-webkit-scrollbar {
          width: 6px;
        }
        .rc-chat-messages::-webkit-scrollbar-track {
          background: transparent;
        }
        .rc-chat-messages::-webkit-scrollbar-thumb {
          background: rgba(170,0,255,0.3);
          border-radius: 3px;
        }
        .rc-chat-message {
          display: flex;
          flex-direction: column;
          gap: 4px;
        }
        .rc-chat-message-own {
          align-items: flex-end;
        }
        .rc-chat-message-other {
          align-items: flex-start;
        }
        .rc-chat-message-header {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 11px;
        }
        .rc-chat-message-username {
          font-weight: 600;
          color: var(--neon-orange);
        }
        .rc-chat-message-time {
          color: rgba(245,240,255,0.4);
        }
        .rc-chat-message-bubble {
          max-width: 85%;
          padding: 10px 14px;
          border-radius: 14px;
          font-size: 13px;
          line-height: 1.4;
          word-break: break-word;
        }
        .rc-chat-message-actions {
          display: flex;
          gap: 4px;
          margin-top: 4px;
          opacity: 0;
          transition: opacity 0.2s;
        }
        .rc-chat-message:hover .rc-chat-message-actions {
          opacity: 1;
        }
        .rc-chat-action-btn {
          width: 24px;
          height: 24px;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 12px;
          transition: all 0.2s;
        }
        .rc-chat-action-btn:hover {
          transform: scale(1.1);
        }
        .rc-chat-action-btn.delete {
          background: rgba(255,23,68,0.2);
          color: var(--neon-red);
        }
        .rc-chat-action-btn.delete:hover {
          background: var(--neon-red);
          color: white;
        }
        .rc-chat-action-btn.warn {
          background: rgba(255,193,7,0.2);
          color: #FFC107;
        }
        .rc-chat-action-btn.warn:hover {
          background: #FFC107;
          color: black;
        }
        .rc-chat-action-btn.block {
          background: rgba(156,39,176,0.2);
          color: var(--neon-purple);
        }
        .rc-chat-action-btn.block:hover {
          background: var(--neon-purple);
          color: white;
        }
        .rc-chat-message-own .rc-chat-message-bubble {
          background: linear-gradient(135deg, var(--neon-red), var(--neon-orange));
          color: white;
          border-bottom-right-radius: 4px;
        }
        .rc-chat-message-other .rc-chat-message-bubble {
          background: rgba(170,0,255,0.2);
          color: var(--soft-white);
          border-bottom-left-radius: 4px;
          border: 1px solid rgba(170,0,255,0.3);
        }
        .rc-chat-input-area {
          padding: 12px 16px;
          border-top: 1px solid rgba(170,0,255,0.2);
          background: rgba(170,0,255,0.05);
        }
        .rc-chat-form {
          display: flex;
          gap: 10px;
          align-items: center;
        }
        .rc-chat-input {
          flex: 1;
          padding: 12px 16px;
          background: rgba(255,255,255,0.08);
          border: 1px solid rgba(170,0,255,0.3);
          border-radius: 24px;
          color: var(--soft-white);
          font-size: 14px;
          outline: none;
          transition: all 0.2s;
        }
        .rc-chat-input::placeholder {
          color: rgba(245,240,255,0.4);
        }
        .rc-chat-input:focus {
          border-color: var(--neon-purple);
          background: rgba(255,255,255,0.12);
          box-shadow: 0 0 15px rgba(170,0,255,0.2);
        }
        .rc-chat-send {
          width: 44px;
          height: 44px;
          background: linear-gradient(135deg, var(--neon-red), var(--neon-orange));
          border: none;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          transition: all 0.2s;
          box-shadow: 0 4px 15px rgba(255,23,68,0.3);
        }
        .rc-chat-send:hover {
          transform: scale(1.05);
          box-shadow: 0 6px 20px rgba(255,23,68,0.4);
        }
        .rc-chat-send:disabled {
          opacity: 0.5;
          cursor: not-allowed;
          transform: none;
        }
        .rc-chat-empty {
          text-align: center;
          padding: 40px 20px;
          color: rgba(245,240,255,0.4);
          font-size: 13px;
        }
        .rc-chat-modal-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0,0,0,0.7);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 1000;
          backdrop-filter: blur(5px);
        }
        .rc-chat-modal {
          background: rgba(26,0,51,0.95);
          border: 1px solid rgba(170,0,255,0.4);
          border-radius: 16px;
          padding: 24px;
          width: 90%;
          max-width: 400px;
          box-shadow: 0 20px 60px rgba(0,0,0,0.5);
        }
        .rc-chat-modal-title {
          display: flex;
          align-items: center;
          gap: 10px;
          font-size: 16px;
          font-weight: 700;
          color: var(--soft-white);
          margin-bottom: 16px;
        }
        .rc-chat-modal-subtitle {
          font-size: 13px;
          color: rgba(245,240,255,0.7);
          margin-bottom: 12px;
        }
        .rc-chat-modal-user {
          background: rgba(170,0,255,0.2);
          padding: 8px 12px;
          border-radius: 8px;
          font-weight: 600;
          color: var(--neon-orange);
          margin-bottom: 16px;
        }
        .rc-chat-modal-input {
          width: 100%;
          padding: 12px 16px;
          background: rgba(255,255,255,0.08);
          border: 1px solid rgba(170,0,255,0.3);
          border-radius: 12px;
          color: var(--soft-white);
          font-size: 13px;
          outline: none;
          margin-bottom: 16px;
          resize: vertical;
          min-height: 80px;
        }
        .rc-chat-modal-input::placeholder {
          color: rgba(245,240,255,0.4);
        }
        .rc-chat-modal-options {
          margin-bottom: 16px;
        }
        .rc-chat-modal-option {
          display: flex;
          align-items: center;
          gap: 8px;
          margin-bottom: 8px;
          font-size: 13px;
          color: rgba(245,240,255,0.8);
        }
        .rc-chat-modal-option input[type="checkbox"] {
          width: 16px;
          height: 16px;
          accent-color: var(--neon-purple);
        }
        .rc-chat-modal-option input[type="number"] {
          width: 60px;
          padding: 4px 8px;
          background: rgba(255,255,255,0.08);
          border: 1px solid rgba(170,0,255,0.3);
          border-radius: 6px;
          color: var(--soft-white);
          font-size: 13px;
        }
        .rc-chat-modal-buttons {
          display: flex;
          gap: 12px;
        }
        .rc-chat-modal-btn {
          flex: 1;
          padding: 12px 20px;
          border: none;
          border-radius: 10px;
          font-size: 13px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s;
        }
        .rc-chat-modal-btn.cancel {
          background: rgba(255,255,255,0.1);
          color: rgba(245,240,255,0.7);
        }
        .rc-chat-modal-btn.cancel:hover {
          background: rgba(255,255,255,0.2);
        }
        .rc-chat-modal-btn.confirm {
          background: linear-gradient(135deg, var(--neon-red), var(--neon-orange));
          color: white;
        }
        .rc-chat-modal-btn.confirm:hover {
          transform: translateY(-1px);
          box-shadow: 0 4px 15px rgba(255,23,68,0.4);
        }
      `}</style>

      {!isExpanded ? (
        <motion.button
          className="rc-chat-button"
          onClick={toggleChat}
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.95 }}
        >
          <MessageSquare size={26} color="white" />
          {hasUnread && (
            <span className="rc-chat-badge">{hasUnread ? '!' : ''}</span>
          )}
        </motion.button>
      ) : (
        <motion.div
          className="rc-chat-window"
          initial={{ opacity: 0, scale: 0.9, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.9, y: 20 }}
        >
          {/* Header */}
          <div className="rc-chat-header">
            <div>
              <div className="rc-chat-title">
                <MessageSquare size={18} color="#FF6D00" />
                Chat en Vivo
                {esModerador && (
                  <span className="rc-chat-moderator-badge">
                    <Shield size={10} />
                    MOD
                  </span>
                )}
              </div>
              <div className="rc-chat-status">
                <span className="rc-chat-status-dot"></span>
                <Users size={12} />
                <span>{onlineUsers} en línea</span>
              </div>
            </div>
            <button className="rc-chat-close" onClick={toggleChat}>
              <X size={20} />
            </button>
          </div>

          {/* Messages */}
          <div className="rc-chat-messages">
            {/* Banner de advertencias */}
            <AnimatePresence>
              {showAdvertencias && advertencias.length > 0 && (
                <motion.div
                  className="rc-chat-advertencias-banner"
                  initial={{ opacity: 0, y: -20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                >
                  <div className="rc-chat-advertencias-header">
                    <AlertTriangle size={14} />
                    Tienes {advertencias.length} advertencia(s)
                  </div>
                  {advertencias.slice(0, 3).map((adv, idx) => (
                    <div key={idx} className="rc-chat-advertencia-item">
                      <strong>{adv.advertido_por}:</strong> {adv.razon}
                    </div>
                  ))}
                  <div className="rc-chat-advertencias-close" onClick={marcarAdvertenciasLeidas}>
                    Marcar como leídas
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            {messages.length === 0 ? (
              <div className="rc-chat-empty">
                <MessageSquare size={32} style={{ marginBottom: 12, opacity: 0.3 }} />
                <p>Sé el primero en escribir algo...</p>
              </div>
            ) : (
              <AnimatePresence>
                {messages.map((msg, index) => (
                  <motion.div
                    key={msg.id || index}
                    className={`rc-chat-message ${msg.usuario === user?.username ? 'rc-chat-message-own' : 'rc-chat-message-other'}`}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.2 }}
                  >
                    <div className="rc-chat-message-header">
                      <span className="rc-chat-message-username">{msg.usuario}</span>
                      <span className="rc-chat-message-time">{formatTime(msg.timestamp)}</span>
                    </div>
                    <div className="rc-chat-message-bubble">{msg.mensaje}</div>
                    {/* Botones de moderación */}
                    {esModerador && msg.usuario !== user?.username && (
                      <div className="rc-chat-message-actions">
                        <button
                          className="rc-chat-action-btn delete"
                          onClick={() => abrirModalModeracion('eliminar', msg)}
                          title="Eliminar mensaje"
                        >
                          <Trash2 size={12} />
                        </button>
                        <button
                          className="rc-chat-action-btn warn"
                          onClick={() => abrirModalModeracion('advertir', msg)}
                          title="Advertir usuario"
                        >
                          <AlertTriangle size={12} />
                        </button>
                        <button
                          className="rc-chat-action-btn block"
                          onClick={() => abrirModalModeracion('bloquear', msg)}
                          title="Bloquear usuario"
                        >
                          <Ban size={12} />
                        </button>
                      </div>
                    )}
                  </motion.div>
                ))}
              </AnimatePresence>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="rc-chat-input-area">
            <form className="rc-chat-form" onSubmit={handleSendMessage}>
              <input
                ref={inputRef}
                type="text"
                className="rc-chat-input"
                placeholder="Escribe un mensaje..."
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                maxLength={200}
              />
              <button
                type="submit"
                className="rc-chat-send"
                disabled={!newMessage.trim()}
              >
                <Send size={18} color="white" />
              </button>
            </form>
          </div>
        </motion.div>
      )}

      {/* Modal de moderación */}
      <AnimatePresence>
        {showModeracionModal && (
          <motion.div
            className="rc-chat-modal-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={cerrarModalModeracion}
          >
            <motion.div
              className="rc-chat-modal"
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
            >
              <div className="rc-chat-modal-title">
                {moderacionTipo === 'eliminar' && <Trash2 size={18} color="#FF1744" />}
                {moderacionTipo === 'advertir' && <AlertTriangle size={18} color="#FFC107" />}
                {moderacionTipo === 'bloquear' && <Ban size={18} color="#9C27B0" />}
                {moderacionTipo === 'eliminar' && 'Eliminar Mensaje'}
                {moderacionTipo === 'advertir' && 'Advertir Usuario'}
                {moderacionTipo === 'bloquear' && 'Bloquear Usuario'}
              </div>
              
              <div className="rc-chat-modal-subtitle">
                Usuario objetivo:
              </div>
              <div className="rc-chat-modal-user">
                <Gavel size={14} style={{ marginRight: 6 }} />
                {selectedMessage?.usuario}
              </div>

              {moderacionTipo === 'bloquear' && (
                <div className="rc-chat-modal-options">
                  <label className="rc-chat-modal-option">
                    <input
                      type="checkbox"
                      checked={bloqueoPermanente}
                      onChange={(e) => setBloqueoPermanente(e.target.checked)}
                    />
                    Bloqueo permanente
                  </label>
                  {!bloqueoPermanente && (
                    <label className="rc-chat-modal-option">
                      Duración (horas):
                      <input
                        type="number"
                        min="1"
                        max="168"
                        value={bloqueoDuracion}
                        onChange={(e) => setBloqueoDuracion(parseInt(e.target.value) || 24)}
                      />
                    </label>
                  )}
                </div>
              )}

              <textarea
                className="rc-chat-modal-input"
                placeholder="Razón de la moderación..."
                value={moderacionRazon}
                onChange={(e) => setModeracionRazon(e.target.value)}
              />

              <div className="rc-chat-modal-buttons">
                <button className="rc-chat-modal-btn cancel" onClick={cerrarModalModeracion}>
                  Cancelar
                </button>
                <button className="rc-chat-modal-btn confirm" onClick={ejecutarModeracion}>
                  Confirmar
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export default Chat
