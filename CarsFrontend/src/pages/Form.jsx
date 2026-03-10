import { useState } from "react"
import { useNavigate } from "react-router-dom"
import './Form.css'

function Form() {
  const navigate = useNavigate()

  const [formData, setFormData] = useState({
    budget_max: 50000,
    energie_preferee: "",
    min_required_seats: 5,
    carrosserie_preferee: "",
    boite_preferee: "Automatique",
    importance_consommation: 3,
    importance_performance: 3,
    importance_confort: 3,
    importance_prix: 3,
    needs_awd: false,
    has_children: false,
    long_commute: false
  })

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : 
              type === 'number' ? parseInt(value) || 0 : value
    })
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    
    // Convert fuel types to match API expected values
    let fuelValue = formData.energie_preferee
    if (formData.energie_preferee === "petrol") fuelValue = "Essence"
    else if (formData.energie_preferee === "diesel") fuelValue = "Diesel"
    else if (formData.energie_preferee === "electric") fuelValue = "Electrique"
    else if (formData.energie_preferee === "hybrid") fuelValue = "Hybride"
    
    // Prepare data for API
    const apiData = {
      ...formData,
      energie_preferee: fuelValue,
      min_required_seats: parseInt(formData.min_required_seats) || 5
    }
    
    navigate("/loading", { state: apiData })
  }

  // Body types list
  const bodyTypes = [
    "Berline", "SUV", "Citadine", "Compacte", "Coupé",
    "Cabriolet", "Monospace", "Minibus", "Pick up", "Utilitaire"
  ]

  // Fuel types list
  const fuelTypes = [
    { value: "petrol", label: "Essence - Dynamisme et performance" },
    { value: "diesel", label: "Diesel - Économique et durable" },
    { value: "hybrid", label: "Hybride - Le meilleur des deux mondes" },
    { value: "electric", label: "Électrique - Zéro émission" }
  ]

  return (
    <div className="form-page">
      {/* Éléments d'arrière-plan */}
      <div className="form-bg-circle circle-1"></div>
      <div className="form-bg-circle circle-2"></div>
      
      <div className="form-container">
        <div className="form-header">
          <div className="form-badge">🚗 Étape 1/3</div>
          <h2 className="form-title">
            Personnalisez votre <span className="gradient-text">recherche</span>
          </h2>
          <p className="form-subtitle">
            Répondez à ces quelques questions pour trouver la voiture de vos rêves
          </p>
        </div>

        <form onSubmit={handleSubmit} className="car-form">
          {/* Budget Field - Now Number Input */}
          <div className="form-group">
            <label className="form-label">
              <span className="label-icon">💰</span>
              Budget (en DT)
            </label>
            <div className="input-wrapper">
              <input
                type="number"
                name="budget_max"
                value={formData.budget_max}
                onChange={handleChange}
                required
                min="0"
                step="1000"
                placeholder="ex: 50000"
                className="form-input"
              />
              <span className="input-suffix">DT</span>
            </div>
          </div>

          {/* Fuel Type Field - Updated with Diesel */}
          <div className="form-group">
            <label className="form-label">
              <span className="label-icon">⛽</span>
              Type de carburant
            </label>
            <div className="select-wrapper">
              <select 
                name="energie_preferee" 
                onChange={handleChange} 
                value={formData.energie_preferee}
                required
                className="form-select"
              >
                <option value="" disabled>Choisissez votre type de motorisation</option>
                {fuelTypes.map(type => (
                  <option key={type.value} value={type.value}>{type.label}</option>
                ))}
              </select>
              <span className="select-arrow">▼</span>
            </div>
          </div>

          {/* Body Type Field - Complete List */}
          <div className="form-group">
            <label className="form-label">
              <span className="label-icon">🚗</span>
              Type de carrosserie
            </label>
            <div className="select-wrapper">
              <select 
                name="carrosserie_preferee" 
                onChange={handleChange} 
                value={formData.carrosserie_preferee}
                className="form-select"
              >
                <option value="">Tous types</option>
                {bodyTypes.map(type => (
                  <option key={type} value={type}>{type}</option>
                ))}
              </select>
              <span className="select-arrow">▼</span>
            </div>
          </div>

          {/* Seats Field */}
          <div className="form-group">
            <label className="form-label">
              <span className="label-icon">👥</span>
              Nombre de places
            </label>
            <div className="input-wrapper">
              <input
                type="number"
                name="min_required_seats"
                value={formData.min_required_seats}
                onChange={handleChange}
                required
                min="2"
                max="9"
                placeholder="ex: 5"
                className="form-input"
              />
              <span className="input-suffix">places</span>
            </div>
          </div>

          {/* Transmission Field */}
          <div className="form-group">
            <label className="form-label">
              <span className="label-icon">⚙️</span>
              Boîte de vitesse
            </label>
            <div className="select-wrapper">
              <select 
                name="boite_preferee" 
                onChange={handleChange} 
                value={formData.boite_preferee}
                className="form-select"
              >
                <option value="Automatique">Automatique</option>
                <option value="Manuelle">Manuelle</option>
              </select>
              <span className="select-arrow">▼</span>
            </div>
          </div>

          {/* Importance Sliders - All 4 */}
          <div className="sliders-container">
            <div className="form-group">
              <label className="form-label">
                <span className="label-icon">📊</span>
                Importance de la consommation (1-5)
              </label>
              <input
                type="range"
                name="importance_consommation"
                min="1"
                max="5"
                value={formData.importance_consommation}
                onChange={handleChange}
                className="form-range"
              />
              <span className="range-value">{formData.importance_consommation}/5</span>
            </div>

            <div className="form-group">
              <label className="form-label">
                <span className="label-icon">⚡</span>
                Importance de la performance (1-5)
              </label>
              <input
                type="range"
                name="importance_performance"
                min="1"
                max="5"
                value={formData.importance_performance}
                onChange={handleChange}
                className="form-range"
              />
              <span className="range-value">{formData.importance_performance}/5</span>
            </div>

            <div className="form-group">
              <label className="form-label">
                <span className="label-icon">🛋️</span>
                Importance du confort (1-5)
              </label>
              <input
                type="range"
                name="importance_confort"
                min="1"
                max="5"
                value={formData.importance_confort}
                onChange={handleChange}
                className="form-range"
              />
              <span className="range-value">{formData.importance_confort}/5</span>
            </div>

            <div className="form-group">
              <label className="form-label">
                <span className="label-icon">💰</span>
                Importance du prix (1-5)
              </label>
              <input
                type="range"
                name="importance_prix"
                min="1"
                max="5"
                value={formData.importance_prix}
                onChange={handleChange}
                className="form-range"
              />
              <span className="range-value">{formData.importance_prix}/5</span>
            </div>
          </div>

          {/* Checkboxes */}
          <div className="checkbox-group">
            <div className="form-group checkbox-group">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  name="needs_awd"
                  checked={formData.needs_awd}
                  onChange={handleChange}
                />
                <span>Besoin de 4 roues motrices (AWD)</span>
              </label>
            </div>

            <div className="form-group checkbox-group">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  name="has_children"
                  checked={formData.has_children}
                  onChange={handleChange}
                />
                <span>J'ai des enfants</span>
              </label>
            </div>

            <div className="form-group checkbox-group">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  name="long_commute"
                  checked={formData.long_commute}
                  onChange={handleChange}
                />
                <span>Longs trajets quotidiens (+50 km)</span>
              </label>
            </div>
          </div>

          {/* Submit Button */}
          <button type="submit" className="submit-button">
            <span>Obtenir mes recommandations</span>
            <svg className="button-arrow" viewBox="0 0 24 24" fill="none">
              <path d="M5 12H19M19 12L13 6M19 12L13 18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </button>

          {/* Progress Indicator */}
          <div className="form-progress">
            <div className="progress-step active"></div>
            <div className="progress-step"></div>
            <div className="progress-step"></div>
          </div>
        </form>

        {/* Trust Badges */}
        <div className="trust-badges">
          <div className="trust-item">
            <span className="trust-icon">🔒</span>
            <span>Données sécurisées</span>
          </div>
          <div className="trust-item">
            <span className="trust-icon">⚡</span>
            <span>Résultats instantanés</span>
          </div>
          <div className="trust-item">
            <span className="trust-icon">🎯</span>
            <span>Recommandations précises</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Form