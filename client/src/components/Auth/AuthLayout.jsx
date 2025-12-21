import React from 'react';
import './AuthLayout.css';
import authBg from '../../assets/auth-bg.png';

const AuthLayout = ({ children }) => {
    // Generate vehicles for the animation overlay
    const vehicles = Array.from({ length: 6 }, (_, i) => ({
        id: i,
        lane: i % 3,
        direction: 'right',
        delay: Math.random() * 5,
        duration: 3 + Math.random() * 2,
        type: Math.random() > 0.7 ? 'truck' : 'car',
    }));

    return (
        <div className="auth-layout">
            {/* Left Side - Branding & Visualization */}
            <div className="auth-visual-panel">
                {/* Background Image */}
                <div
                    className="auth-bg-image"
                    style={{ backgroundImage: `url(${authBg})` }}
                ></div>

                {/* Overlay Gradient */}
                <div className="auth-bg-overlay"></div>

                {/* Animated Traffic Layer */}
                <div className="road-overlay">
                    {vehicles.map((vehicle) => (
                        <div
                            key={vehicle.id}
                            className={`vehicle-overlay ${vehicle.type} lane-${vehicle.lane}`}
                            style={{
                                animationDelay: `${vehicle.delay}s`,
                                animationDuration: `${vehicle.duration}s`,
                            }}
                        >
                            <div className="light-trail"></div>
                        </div>
                    ))}
                </div>

                {/* Branding Content */}
                <div className="branding-content">
                    <h1 className="brand-title">
                        <span className="text-white">Project </span>
                        <span className="text-blue-500">DAAN </span>
                        <span className="text-white">Express</span>
                    </h1>

                    <p className="brand-subtitle">
                        Digital Analytics for Asset-based Navigation of Roads
                    </p>

                    <div className="feature-grid">
                        <div className="feature-item">
                            <span className="feature-icon">📊</span>
                            <span className="feature-text">IRI Analysis</span>
                        </div>
                        <div className="feature-item">
                            <span className="feature-icon">🗺️</span>
                            <span className="feature-text">Road Mapping</span>
                        </div>
                        <div className="feature-item">
                            <span className="feature-icon">🚦</span>
                            <span className="feature-text">Traffic Monitoring</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Right Side - Clerk Form (Using Clerk's default styling) */}
            <div className="auth-form-panel">
                {children}
            </div>
        </div>
    );
};

export default AuthLayout;
