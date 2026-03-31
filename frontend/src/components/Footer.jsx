import React from 'react'

const Footer = () => {
  return (
    <footer className="w-full py-6 mt-8" style={{ background: 'var(--glass-bg)', borderTop: '1px solid var(--glass-border)' }}>
      <div className="container mx-auto px-4 text-center">
        <p className="text-sm" style={{ color: 'var(--soft-white)', opacity: 0.8 }}>
          © 2024 Radio Covid. Todos los derechos reservados.
        </p>
        <div className="flex justify-center gap-4 mt-3">
          <a href="#" className="text-sm hover:text-[var(--neon-red)] transition-colors" style={{ color: 'var(--soft-white)', opacity: 0.6 }}>
            Términos
          </a>
          <a href="#" className="text-sm hover:text-[var(--neon-red)] transition-colors" style={{ color: 'var(--soft-white)', opacity: 0.6 }}>
            Privacidad
          </a>
          <a href="#" className="text-sm hover:text-[var(--neon-red)] transition-colors" style={{ color: 'var(--soft-white)', opacity: 0.6 }}>
            Contacto
          </a>
        </div>
      </div>
    </footer>
  )
}

export default Footer
