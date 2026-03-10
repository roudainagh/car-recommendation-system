import { useState } from "react"
import { useLocation, useNavigate } from "react-router-dom"
import './Result.css'

function Result() {
  const location = useLocation()
  const navigate = useNavigate()
  const { recommendations = [], userPreferences = {}, error, totalFound } = location.state || {}
  const [selectedCar, setSelectedCar] = useState(null)
  const [showDetails, setShowDetails] = useState(false)

  const handleCarSelect = (index) => {
    setSelectedCar(index)
    setShowDetails(true)
    setTimeout(() => {
      document.getElementById('comparison-section')?.scrollIntoView({ 
        behavior: 'smooth', 
        block: 'center' 
      })
    }, 100)
  }

  // Format price
  const formatPrice = (price) => {
    return new Intl.NumberFormat('fr-TN', {
      style: 'currency',
      currency: 'TND',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(price).replace('TND', 'DT')
  }

  // Get fuel type in French
  const getFuelLabel = (fuel) => {
    const labels = {
      'Essence': 'Essence',
      'Diesel': 'Diesel',
      'Hybride': 'Hybride',
      'Electrique': 'Électrique'
    }
    return labels[fuel] || fuel
  }

  return (
    <div className="result-page">
      {/* Cercles d'arrière-plan */}
      <div className="result-bg-circle"></div>
      <div className="result-bg-circle"></div>
      <div className="result-bg-circle"></div>
      
      {/* Boutons de navigation */}
      <div className="nav-buttons">
        <button className="nav-btn" onClick={() => navigate('/')}>
          <span>🏠</span> Accueil
        </button>
        <button className="nav-btn" onClick={() => navigate('/form')}>
          <span>📝</span> Nouvelle recherche
        </button>
      </div>
      
      <div className="result-container">
        {/* En-tête avec les préférences */}
        <div className="result-header">
          <div className="success-badge">
            <span className="badge-icon">✅</span>
            {error ? 'Erreur' : `${recommendations.length} véhicules trouvés`}
          </div>
          
          <h1 className="result-title">
            Vos <span className="gradient-text">recommandations</span>
          </h1>
          
          {userPreferences && (
            <div className="preference-summary">
              <div className="preference-chip">
                <span className="chip-icon">💰</span>
                {formatPrice(userPreferences.budget_max)}
              </div>
              <div className="preference-chip">
                <span className="chip-icon">⛽</span>
                {getFuelLabel(userPreferences.energie_preferee)}
              </div>
              <div className="preference-chip">
                <span className="chip-icon">👥</span>
                {userPreferences.min_required_seats} places
              </div>
              {userPreferences.carrosserie_preferee && (
                <div className="preference-chip">
                  <span className="chip-icon">🚗</span>
                  {userPreferences.carrosserie_preferee}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Error Message */}
        {error && (
          <div className="no-results">
            <div className="no-results-icon">❌</div>
            <h3>Une erreur est survenue</h3>
            <p>{error}</p>
            <button 
              className="back-button"
              onClick={() => navigate('/form')}
            >
              Réessayer
            </button>
          </div>
        )}

        {/* Liste des recommandations */}
        {!error && recommendations.length > 0 ? (
          <>
            <div className="cars-grid">
              {recommendations.map((car, index) => (
                <div 
                  key={index} 
                  className={`car-card ${selectedCar === index ? 'selected' : ''}`}
                  onClick={() => handleCarSelect(index)}
                >
                  <div className="car-card-header">
                    <span className="car-emoji">
                      {car.body_type === 'SUV' ? '🚙' : 
                       car.body_type === 'Citadine' ? '🚗' :
                       car.body_type === 'Berline' ? '🚘' : '🚗'}
                    </span>
                    <span className="car-rating">
                      {'★'.repeat(Math.floor(car.similarity_score / 20))}
                      {'☆'.repeat(5 - Math.floor(car.similarity_score / 20))}
                    </span>
                  </div>
                  
                  <h3 className="car-name">{car.brand} {car.model}</h3>
                  <div className="car-price">{formatPrice(car.price)}</div>
                  
                  <div className="car-features">
                    <div className="feature">
                      <span className="feature-icon">⚡</span>
                      <span>{car.power}</span>
                    </div>
                    <div className="feature">
                      <span className="feature-icon">⛽</span>
                      <span>{getFuelLabel(car.fuel_type)}</span>
                    </div>
                    <div className="feature">
                      <span className="feature-icon">👥</span>
                      <span>{car.seats} places</span>
                    </div>
                  </div>
                  
                  <div className="match-score">
                    <div className="score-bar">
                      <div 
                        className="score-fill" 
                        style={{ width: `${car.similarity_score}%` }}
                      ></div>
                    </div>
                    <span className="score-text">{car.similarity_score.toFixed(1)}% match</span>
                  </div>
                  
                  <button className="view-details-btn">
                    Voir détails
                  </button>
                </div>
              ))}
            </div>

            {/* Section comparateur */}
            {selectedCar !== null && recommendations[selectedCar] && (
              <div id="comparison-section" className="comparison-section">
                <h3 className="comparison-title">
                  <span className="comparison-icon">📊</span>
                  Détails - {recommendations[selectedCar].brand} {recommendations[selectedCar].model}
                </h3>
                <div className="comparison-details">
                  <div className="detail-row">
                    <span>💰 Prix</span>
                    <strong>{formatPrice(recommendations[selectedCar].price)}</strong>
                  </div>
                  <div className="detail-row">
                    <span>⛽ Carburant</span>
                    <strong>{getFuelLabel(recommendations[selectedCar].fuel_type)}</strong>
                  </div>
                  <div className="detail-row">
                    <span>🔋 Puissance</span>
                    <strong>{recommendations[selectedCar].power}</strong>
                  </div>
                  <div className="detail-row">
                    <span>🚗 Carrosserie</span>
                    <strong>{recommendations[selectedCar].body_type}</strong>
                  </div>
                  <div className="detail-row">
                    <span>⚙️ Transmission</span>
                    <strong>{recommendations[selectedCar].transmission}</strong>
                  </div>
                  <div className="detail-row">
                    <span>👥 Places</span>
                    <strong>{recommendations[selectedCar].seats}</strong>
                  </div>
                  <div className="detail-row">
                    <span>🎯 Score de match</span>
                    <strong>{recommendations[selectedCar].similarity_score.toFixed(1)}%</strong>
                  </div>
                  {recommendations[selectedCar].explanation && (
                    <div className="detail-row explanation">
                      <span>📝 Explication</span>
                      <strong>{recommendations[selectedCar].explanation}</strong>
                    </div>
                  )}
                </div>
              </div>
            )}
          </>
        ) : !error && (
          <div className="no-results">
            <div className="no-results-icon">🔍</div>
            <h3>Aucune recommandation trouvée</h3>
            <p>Essayez d'ajuster vos critères de recherche</p>
            <button 
              className="back-button"
              onClick={() => navigate('/form')}
            >
              Modifier mes préférences
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

export default Result