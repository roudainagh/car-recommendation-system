import { useEffect, useState } from "react"
import { useNavigate, useLocation } from "react-router-dom"
import './Loading.css'

function Loading() {
  const navigate = useNavigate()
  const location = useLocation()
  const userData = location.state
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchRecommendations = async () => {
      try {
        // Call your FastAPI backend
        const response = await fetch('http://localhost:8000/api/recommend/by-preferences?top_n=10', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(userData)
        })

        if (!response.ok) {
          throw new Error('Failed to get recommendations')
        }

        const data = await response.json()
        
        // Navigate to results with the real recommendations
        setTimeout(() => {
          navigate("/result", { 
            state: { 
              recommendations: data.recommendations,
              userPreferences: userData,
              totalFound: data.total_found
            } 
          })
        }, 2000) // Keep the loading animation for UX
        
      } catch (err) {
        console.error('Error:', err)
        setError(err.message)
        // Still navigate but with error state
        setTimeout(() => {
          navigate("/result", { 
            state: { 
              error: err.message,
              userPreferences: userData 
            } 
          })
        }, 2000)
      }
    }

    fetchRecommendations()
  }, [navigate, userData])

  if (error) {
    return (
      <div className="loading-page">
        <div className="loading-container">
          <div className="error-message">
            <span className="error-icon">❌</span>
            <h2>Une erreur est survenue</h2>
            <p>{error}</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="loading-page">
      {/* Éléments d'arrière-plan */}
      <div className="loading-bg-circle"></div>
      <div className="loading-bg-circle"></div>
      
      <div className="loading-container">
        {/* Animation de voiture */}
        <div className="car-animation">
          <div className="car-body">
            <div className="car-roof"></div>
            <div className="car-window front-window"></div>
            <div className="car-window back-window"></div>
            <div className="car-light front-light"></div>
            <div className="car-light back-light"></div>
          </div>
          <div className="car-wheels">
            <div className="wheel left-wheel">
              <div className="wheel-spin"></div>
            </div>
            <div className="wheel right-wheel">
              <div className="wheel-spin"></div>
            </div>
          </div>
          <div className="road-lines"></div>
        </div>

        {/* Barre de progression */}
        <div className="progress-container">
          <div className="progress-bar">
            <div className="progress-fill"></div>
          </div>
        </div>

        {/* Texte de chargement */}
        <h2 className="loading-title">
          Recherche du véhicule idéal
        </h2>
        
        <p className="loading-subtitle">
          Analyse de vos préférences en cours
        </p>

        {/* Messages dynamiques */}
        <div className="loading-messages">
          <div className="message-bubble">
            <span className="message-icon">💰</span>
            <span>Analyse du budget: {userData?.budget_max} DT...</span>
          </div>
          <div className="message-bubble">
            <span className="message-icon">⛽</span>
            <span>Vérification des motorisations {userData?.energie_preferee}...</span>
          </div>
          <div className="message-bubble">
            <span className="message-icon">🎯</span>
            <span>Sélection des meilleures options...</span>
          </div>
        </div>

        {/* Statistiques en temps réel (simulées) */}
        <div className="live-stats">
          <div className="stat-pill">
            <span className="stat-pulse"></span>
            <span>548 véhicules analysés</span>
          </div>
          <div className="stat-pill">
            <span>⏱️ Recherche en cours...</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Loading