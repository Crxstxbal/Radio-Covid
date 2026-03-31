import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Radio, Menu, X, Facebook, Twitter, Instagram, Youtube, User, LogOut, Settings } from 'lucide-react'
import logo from '../img/Logo_de_Radio_COVID_sin_fondo.png'

const Header = () => {
  const [isScrolled, setIsScrolled] = useState(false)
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
  const [user, setUser] = useState(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 50)
    }

    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  useEffect(() => {
    // Verificar si hay sesión activa
    checkAuthStatus()
  }, [])

  const checkAuthStatus = async () => {
    try {
      // Simular verificación de autenticación
      // En una implementación real, esto verificaría con el backend
      const token = localStorage.getItem('auth_token')
      const userData = localStorage.getItem('user_data')
      
      if (token && userData) {
        setUser(JSON.parse(userData))
      }
      setIsLoading(false)
    } catch (error) {
      console.error('Error checking auth status:', error)
      setIsLoading(false)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('auth_token')
    localStorage.removeItem('user_data')
    setUser(null)
    window.location.href = '/'
  }

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen)
  }

  if (isLoading) {
    return (
      <motion.header
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
          isScrolled 
            ? 'bg-base-black/95 backdrop-blur-lg border-b border-neon-purple/30' 
            : 'bg-transparent'
        }`}
      >
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between w-full">
            {/* Logo */}
            <motion.div
              whileHover={{ scale: 1.05 }}
              className="flex items-center gap-2"
            >
              <div className="w-10 h-10 bg-gradient-to-br from-neon-red to-neon-orange rounded-full flex items-center justify-center shadow-lg shadow-neon-red/30">
                <Radio size={20} className="text-soft-white" />
              </div>
              <img src={logo} alt="Radio Covid" className="h-10 w-auto" />
            </motion.div>

            {/* Desktop Navigation */}
            <nav className="hidden md:flex items-center gap-8 absolute left-1/2 transform -translate-x-1/2">
              {user ? (
                <>
                  <span className="text-soft-white/60">
                    Bienvenido, <span className="text-soft-white font-semibold">{user.username}</span>
                  </span>
                  <button
                    onClick={handleLogout}
                    className="text-soft-white/60 hover:text-neon-red transition-colors flex items-center gap-2"
                  >
                    <LogOut size={18} />
                    Cerrar Sesión
                  </button>
                </>
              ) : (
                <>
                  <a href="/register" className="text-soft-white/60 hover:text-soft-white transition-colors">
                    Registrarse
                  </a>
                  <a href="/login" className="text-soft-white/60 hover:text-soft-white transition-colors">
                    Iniciar Sesión
                  </a>
                </>
              )}
            </nav>

            {/* Social Links & Mobile Menu - Right */}
            <div className="flex items-center gap-4">
              {/* Desktop Social Links */}
              <div className="hidden md:flex items-center gap-4">
                <a
                  href="#"
                  className="text-soft-white/40 hover:text-neon-purple transition-colors"
                  aria-label="Facebook"
                >
                  <Facebook size={18} />
                </a>
                <a
                  href="#"
                  className="text-soft-white/40 hover:text-neon-purple transition-colors"
                  aria-label="Twitter"
                >
                  <Twitter size={18} />
                </a>
                <a
                  href="#"
                  className="text-soft-white/40 hover:text-neon-purple transition-colors"
                  aria-label="Instagram"
                >
                  <Instagram size={18} />
                </a>
                <a
                  href="#"
                  className="text-soft-white/40 hover:text-neon-purple transition-colors"
                  aria-label="YouTube"
                >
                  <Youtube size={18} />
                </a>
              </div>

              {/* Mobile Menu Button */}
              <button
                onClick={toggleMobileMenu}
                className="md:hidden text-soft-white hover:text-neon-yellow transition-colors p-2 rounded-lg hover:bg-white/10"
                aria-label="Toggle menu"
              >
                {isMobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
              </button>
            </div>
          </div>

          {/* Mobile Menu */}
          {isMobileMenuOpen && (
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="md:hidden bg-base-black/95 backdrop-blur-lg rounded-xl mt-2 p-4 border border-neon-purple/30 shadow-xl"
            >
              <nav className="flex flex-col gap-4 mb-4">
                {user ? (
                  <>
                    <div className="text-soft-white/60 pb-4 border-b border-neon-purple/30">
                      Bienvenido, <span className="text-soft-white font-semibold">{user.username}</span>
                    </div>
                    <button
                      onClick={handleLogout}
                      className="text-soft-white/60 hover:text-neon-red transition-colors py-2 flex items-center gap-2"
                    >
                      <LogOut size={18} />
                      Cerrar Sesión
                    </button>
                  </>
                ) : (
                  <>
                    <a
                      href="/register"
                      className="text-soft-white/60 hover:text-soft-white transition-colors py-2"
                      onClick={() => setIsMobileMenuOpen(false)}
                    >
                      Registrarse
                    </a>
                    <a
                      href="/login"
                      className="text-soft-white/60 hover:text-soft-white transition-colors py-2"
                      onClick={() => setIsMobileMenuOpen(false)}
                    >
                      Iniciar Sesión
                    </a>
                  </>
                )}
              </nav>

              {/* Mobile Social Links */}
              <div className="flex items-center gap-4 pt-4 border-t border-neon-purple/30">
                <a
                  href="#"
                  className="text-soft-white/40 hover:text-neon-purple transition-colors"
                  aria-label="Facebook"
                >
                  <Facebook size={18} />
                </a>
                <a
                  href="#"
                  className="text-soft-white/40 hover:text-neon-purple transition-colors"
                  aria-label="Twitter"
                >
                  <Twitter size={18} />
                </a>
                <a
                  href="#"
                  className="text-soft-white/40 hover:text-neon-purple transition-colors"
                  aria-label="Instagram"
                >
                  <Instagram size={18} />
                </a>
                <a
                  href="#"
                  className="text-soft-white/40 hover:text-neon-purple transition-colors"
                  aria-label="YouTube"
                >
                  <Youtube size={18} />
                </a>
              </div>
            </motion.div>
          )}
        </div>
      </motion.header>
    )
  }

  return (
    <motion.header
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        isScrolled 
          ? 'bg-base-black/95 backdrop-blur-lg border-b border-neon-purple/30' 
          : 'bg-transparent'
      }`}
    >
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between w-full">
          {/* Left Section: Logo and Desktop Navigation */}
          <div className="flex items-center gap-4 lg:gap-8">
            {/* Logo */}
            <motion.div
              whileHover={{ scale: 1.05 }}
              className="flex items-center gap-2"
            >
              <img src={logo} alt="Radio Covid" className="h-12 w-auto md:h-20" />
              <span className="text-lg md:text-xl font-bold text-soft-white tracking-wider hidden sm:inline">RADIO COVID</span>
            </motion.div>

            {/* Desktop Navigation - Hidden on smaller tablets */}
            <nav className="hidden lg:flex items-center gap-6">
              <a href="/" className="text-soft-white/60 hover:text-neon-orange transition-colors">
                Inicio
              </a>
              <a href="/programacion" className="text-soft-white/60 hover:text-neon-orange transition-colors">
                Programación
              </a>
              <a href="/podcasts" className="text-soft-white/60 hover:text-neon-orange transition-colors">
                Podcasts
              </a>
              <a href="/contacto" className="text-soft-white/60 hover:text-neon-orange transition-colors">
                Contacto
              </a>
            </nav>
          </div>

          {/* Right Section: Social Links, User Menu & Mobile Menu */}
          <div className="flex items-center gap-2 lg:gap-4">
            {/* Desktop Social Links & User Menu */}
            <div className="hidden lg:flex items-center gap-4">
              {user ? (
                <>
                  <span className="text-soft-white/60 text-sm">
                    Hola, <span className="text-soft-white font-semibold">{user.username}</span>
                  </span>
                  <button
                    onClick={handleLogout}
                    className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-neon-red to-neon-orange rounded-lg text-soft-white text-sm font-semibold hover:shadow-lg hover:shadow-neon-red/30 transition-all"
                  >
                    <LogOut size={16} />
                    Cerrar Sesión
                  </button>
                </>
              ) : (
                <>
                  <a
                    href="/login"
                    className="flex items-center gap-2 px-3 py-2 border border-neon-purple/50 rounded-lg text-soft-white text-sm font-semibold hover:bg-neon-purple/20 transition-all"
                  >
                    <User size={16} />
                    <span className="hidden xl:inline">Iniciar Sesión</span>
                  </a>
                  <a
                    href="/register"
                    className="flex items-center gap-2 px-3 py-2 bg-gradient-to-r from-neon-purple to-neon-orange rounded-lg text-soft-white text-sm font-semibold hover:shadow-lg hover:shadow-neon-purple/30 transition-all"
                  >
                    <User size={16} />
                    <span className="hidden xl:inline">Registrarse</span>
                  </a>
                </>
              )}
              <div className="w-px h-6 bg-neon-purple/30 mx-2"></div>
              <a
                href="#"
                className="text-soft-white/40 hover:text-neon-purple transition-colors"
                aria-label="Facebook"
              >
                <Facebook size={18} />
              </a>
              <a
                href="#"
                className="text-soft-white/40 hover:text-neon-purple transition-colors"
                aria-label="Twitter"
              >
                <Twitter size={18} />
              </a>
              <a
                href="#"
                className="text-soft-white/40 hover:text-neon-purple transition-colors"
                aria-label="Instagram"
              >
                <Instagram size={18} />
              </a>
              <a
                href="#"
                className="text-soft-white/40 hover:text-neon-purple transition-colors"
                aria-label="YouTube"
              >
                <Youtube size={18} />
              </a>
            </div>

            {/* Tablet and Mobile Menu Button */}
            <button
              onClick={toggleMobileMenu}
              className="lg:hidden text-soft-white hover:text-neon-purple transition-colors p-2 rounded-lg hover:bg-white/10"
              aria-label="Toggle menu"
            >
              {isMobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {isMobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="md:hidden bg-base-black/95 backdrop-blur-lg rounded-xl mt-2 p-4 border border-neon-purple/30 shadow-xl"
          >
            <nav className="flex flex-col gap-4 mb-4">
              <a
                href="/"
                className="text-soft-white/60 hover:text-soft-white transition-colors py-2"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                Inicio
              </a>
              <a
                href="/programacion"
                className="text-soft-white/60 hover:text-soft-white transition-colors py-2"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                Programación
              </a>
              <a
                href="/podcasts"
                className="text-soft-white/60 hover:text-soft-white transition-colors py-2"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                Podcasts
              </a>
              <a
                href="/contacto"
                className="text-soft-white/60 hover:text-soft-white transition-colors py-2"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                Contacto
              </a>
              
              <div className="border-t border-neon-purple/30 pt-4 mt-2">
                {user ? (
                  <>
                    <div className="text-soft-white/60 pb-2">
                      Hola, <span className="text-soft-white font-semibold">{user.username}</span>
                    </div>
                    <button
                      onClick={() => {
                        handleLogout()
                        setIsMobileMenuOpen(false)
                      }}
                      className="w-full text-left text-neon-red hover:text-neon-orange transition-colors py-2 flex items-center gap-2"
                    >
                      <LogOut size={18} />
                      Cerrar Sesión
                    </button>
                  </>
                ) : (
                  <>
                    <a
                      href="/login"
                      className="text-soft-white/60 hover:text-soft-white transition-colors py-2 block"
                      onClick={() => setIsMobileMenuOpen(false)}
                    >
                      Iniciar Sesión
                    </a>
                    <a
                      href="/register"
                      className="text-neon-purple hover:text-neon-orange transition-colors py-2 block"
                      onClick={() => setIsMobileMenuOpen(false)}
                    >
                      Registrarse
                    </a>
                  </>
                )}
              </div>
            </nav>

            {/* Mobile Social Links */}
            <div className="flex items-center gap-4 pt-4 border-t border-neon-purple/30">
              <a
                href="#"
                className="text-soft-white/40 hover:text-neon-purple transition-colors"
                aria-label="Facebook"
              >
                <Facebook size={18} />
              </a>
              <a
                href="#"
                className="text-soft-white/40 hover:text-neon-purple transition-colors"
                aria-label="Twitter"
              >
                <Twitter size={18} />
              </a>
              <a
                href="#"
                className="text-soft-white/40 hover:text-neon-purple transition-colors"
                aria-label="Instagram"
              >
                <Instagram size={18} />
              </a>
              <a
                href="#"
                className="text-soft-white/40 hover:text-neon-purple transition-colors"
                aria-label="YouTube"
              >
                <Youtube size={18} />
              </a>
            </div>
          </motion.div>
        )}
      </div>
    </motion.header>
  )
}

export default Header
