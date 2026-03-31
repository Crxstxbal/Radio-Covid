import { useState, useEffect, useRef } from 'react'

export const useWebSocket = (url) => {
  const [lastMessage, setLastMessage] = useState(null)
  const [readyState, setReadyState] = useState(WebSocket.CONNECTING)
  const [isConnected, setIsConnected] = useState(false)
  const ws = useRef(null)
  const reconnectTimeout = useRef(null)
  const reconnectAttempts = useRef(0)
  const maxReconnectAttempts = 5

  const connect = () => {
    // Usar API_URL como base para WebSocket, reemplazando http con ws
    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
    const wsBase = apiUrl.replace('https://', 'wss://').replace('http://', 'ws://')
    const wsUrl = `${wsBase}${url}`
    
    console.log('Connecting to WebSocket:', wsUrl)
    
    try {
      ws.current = new WebSocket(wsUrl)
      
      ws.current.onopen = () => {
        console.log('WebSocket connected')
        setReadyState(WebSocket.OPEN)
        setIsConnected(true)
        reconnectAttempts.current = 0
        
        // Enviar nombre de usuario al conectar
        const userData = localStorage.getItem('user_data')
        if (userData) {
          try {
            const user = JSON.parse(userData)
            ws.current.send(JSON.stringify({ 
              type: 'identificar',
              usuario: user.username 
            }))
          } catch (e) {
            console.log('No user data available')
          }
        }
        
        // Enviar heartbeat cada 30 segundos
        const heartbeatInterval = setInterval(() => {
          if (ws.current && ws.current.readyState === WebSocket.OPEN) {
            ws.current.send(JSON.stringify({ type: 'heartbeat' }))
          } else {
            clearInterval(heartbeatInterval)
          }
        }, 30000)
        
        // Limpiar interval al desconectar
        ws.current.onclose = () => {
          clearInterval(heartbeatInterval)
          handleDisconnect()
        }
      }
      
      ws.current.onmessage = (event) => {
        setLastMessage(event)
      }
      
      ws.current.onerror = (error) => {
        console.error('WebSocket error:', error)
        setReadyState(WebSocket.CLOSED)
        setIsConnected(false)
      }
      
      ws.current.onclose = () => {
        handleDisconnect()
      }
      
    } catch (error) {
      console.error('Error creating WebSocket:', error)
      handleDisconnect()
    }
  }

  const handleDisconnect = () => {
    setReadyState(WebSocket.CLOSED)
    setIsConnected(false)
    
    // Intentar reconectar
    if (reconnectAttempts.current < maxReconnectAttempts) {
      reconnectAttempts.current++
      const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 30000)
      
      console.log(`Attempting to reconnect in ${delay}ms (attempt ${reconnectAttempts.current})`)
      
      reconnectTimeout.current = setTimeout(() => {
        connect()
      }, delay)
    } else {
      console.log('Max reconnection attempts reached')
    }
  }

  useEffect(() => {
    connect()
    
    return () => {
      if (reconnectTimeout.current) {
        clearTimeout(reconnectTimeout.current)
      }
      if (ws.current) {
        ws.current.close()
      }
    }
  }, [url])

  const sendMessage = (message) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(message)
      return true
    }
    return false
  }

  return {
    lastMessage,
    readyState,
    isConnected,
    sendMessage,
    reconnect: () => {
      if (reconnectTimeout.current) {
        clearTimeout(reconnectTimeout.current)
      }
      reconnectAttempts.current = 0
      connect()
    }
  }
}
