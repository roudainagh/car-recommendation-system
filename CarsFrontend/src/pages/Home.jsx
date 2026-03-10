import { Link } from "react-router-dom"
import './Home.css'; 

function Home() {
  return (
    <div className="home-container">
      {/* Éléments d'arrière-plan décoratifs */}
      <div className="bg-circle circle-1"></div>
      <div className="bg-circle circle-2"></div>
      
      <div className="hero-content">
        <div className="badge">🚀 Premium Car Matching</div>
        
        <h1 className="hero-title">
          Find Your 
          <span className="gradient-text"> Perfect Ride</span>
        </h1>
        
        <p className="hero-subtitle">
          Répondez à quelques questions et découvrez la voiture 
          <span className="highlight"> idéale</span> pour votre style de vie
        </p>
        
        <div className="feature-bubbles">
          <div className="bubble">
            <span className="bubble-icon">⚡</span>
            <span>Sportive</span>
          </div>
          <div className="bubble">
            <span className="bubble-icon">🏠</span>
            <span>Familiale</span>
          </div>
          <div className="bubble">
            <span className="bubble-icon">💰</span>
            <span>Économique</span>
          </div>
          <div className="bubble">
            <span className="bubble-icon">🌟</span>
            <span>Luxe</span>
          </div>
        </div>
        
        <Link to="/form">
          <button className="cta-button">
            <span>Commencer la recommandation</span>
            <svg className="arrow-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M5 12H19M19 12L13 6M19 12L13 18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </button>
        </Link>
        
        <div className="stats-container">
          <div className="stat-item">
            <span className="stat-number">500+</span>
            <span className="stat-label">Voitures analysées</span>
          </div>
          <div className="stat-item">
            <span className="stat-number">98%</span>
            <span className="stat-label">Satisfaction</span>
          </div>
          <div className="stat-item">
            <span className="stat-number">24/7</span>
            <span className="stat-label">Support</span>
          </div>
        </div>
      </div>
      
      {/* Image décorative de voiture (optionnelle) */}
      <div className="car-illustration">
        <div className="car-shape"></div>
      </div>
    </div>
  )
}

export default Home