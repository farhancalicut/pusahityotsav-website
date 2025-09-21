import React, { useState, useEffect } from 'react';
import { Box, Container, Typography, CircularProgress } from '@mui/material';
import axios from 'axios'; // Use Axios for consistency
import API_BASE_URL from '../apiConfig';
import './Dashboard.css'; // Import the new CSS file

function Dashboard() {
  const [carouselImages, setCarouselImages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [isPaused, setIsPaused] = useState(false);
  const [showArrows, setShowArrows] = useState(false);

  useEffect(() => {
    const fetchCarouselImages = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/api/carousel/`);
        setCarouselImages(response.data);
      } catch (err) {
        console.error('Error fetching carousel images:', err);
        setError(`Failed to load carousel images.`);
      } finally {
        setLoading(false);
      }
    };
    fetchCarouselImages();
  }, []);

  // Auto-advance to the next image
  useEffect(() => {
    if (carouselImages.length <= 1 || isPaused) return;

    const interval = setInterval(() => {
      setCurrentImageIndex((prevIndex) => (prevIndex + 1) % carouselImages.length);
    }, 3000); // Change image every 3 seconds

    return () => clearInterval(interval);
  }, [carouselImages, isPaused]);

  const handleDotClick = (index) => {
    setCurrentImageIndex(index);
  };

  const handlePrevious = () => {
    setCurrentImageIndex((prevIndex) => 
      prevIndex === 0 ? carouselImages.length - 1 : prevIndex - 1
    );
  };

  const handleNext = () => {
    setCurrentImageIndex((prevIndex) => (prevIndex + 1) % carouselImages.length);
  };

  const handleMouseEnter = () => {
    setIsPaused(true);
    setShowArrows(true);
  };

  const handleMouseLeave = () => {
    setIsPaused(false);
    setShowArrows(false);
  };

  const handleTouchStart = () => {
    setIsPaused(true);
    setShowArrows(true);
  };

  const handleTouchEnd = () => {
    // Add a small delay before hiding arrows on touch devices
    setTimeout(() => {
      setIsPaused(false);
      setShowArrows(false);
    }, 2000); // Hide arrows after 2 seconds on touch devices
  };

  if (loading) {
    return (
      <Box sx={{ py: 8, textAlign: 'center' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ py: 8, textAlign: 'center' }}>
        <Typography variant="h6" color="error">{error}</Typography>
      </Box>
    );
  }

  return (
    // Use a full-width Box instead of Container to remove side padding
    <Box sx={{ py: 2, backgroundColor: '#FFD700' }}>
      <Container maxWidth="lg">
        <Typography
          variant="h4"
          component="h1"
          sx={{
            textAlign: 'center',
            mb: 2, // Adjusted margin for better spacing
            fontWeight: 'bold',
            fontFamily: 'Poppins-Regular, sans-serif', // Correct font family usage
            color: '#1e1e1eff',
            fontSize: { xs: '1.3rem', md: '2rem' }
          }}
        >
          Updates
        </Typography>
      </Container>
      
      {carouselImages.length > 0 ? (
        <>
          <Box 
            className="slide-container"
            onMouseEnter={handleMouseEnter}
            onMouseLeave={handleMouseLeave}
            onTouchStart={handleTouchStart}
            onTouchEnd={handleTouchEnd}
            sx={{ position: 'relative' }}
          >
            <Box
              className="slide-track"
              style={{
                width: `${carouselImages.length * 100}%`,
                transform: `translateX(-${(currentImageIndex * 100) / carouselImages.length}%)`,
              }}
            >
              {carouselImages.map((image, index) => (
                <Box 
                  key={image.id} 
                  className="slide-item"
                  style={{
                    width: `${100 / carouselImages.length}%`,
                  }}
                >
                  <img
                    src={image.image}
                    alt="Carousel slide"
                    className="slide-image"
                    onError={(e) => console.error('Image failed to load:', image.image)}
                  />
                </Box>
              ))}
            </Box>

            {/* Navigation Arrows */}
            {showArrows && carouselImages.length > 1 && (
              <>
                <Box
                  onClick={handlePrevious}
                  sx={{
                    position: 'absolute',
                    left: 10,
                    top: '50%',
                    transform: 'translateY(-50%)',
                    backgroundColor: 'rgba(0, 0, 0, 0.7)',
                    color: 'white',
                    borderRadius: '50%',
                    width: 40,
                    height: 40,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    cursor: 'pointer',
                    fontSize: '18px',
                    fontWeight: 'bold',
                    transition: 'all 0.3s ease',
                    zIndex: 10,
                    '&:hover': {
                      backgroundColor: 'rgba(0, 0, 0, 0.9)',
                      transform: 'translateY(-50%) scale(1.1)',
                    },
                    '&:active': {
                      transform: 'translateY(-50%) scale(0.95)',
                    }
                  }}
                >
                  ‹
                </Box>
                <Box
                  onClick={handleNext}
                  sx={{
                    position: 'absolute',
                    right: 10,
                    top: '50%',
                    transform: 'translateY(-50%)',
                    backgroundColor: 'rgba(0, 0, 0, 0.7)',
                    color: 'white',
                    borderRadius: '50%',
                    width: 40,
                    height: 40,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    cursor: 'pointer',
                    fontSize: '18px',
                    fontWeight: 'bold',
                    transition: 'all 0.3s ease',
                    zIndex: 10,
                    '&:hover': {
                      backgroundColor: 'rgba(0, 0, 0, 0.9)',
                      transform: 'translateY(-50%) scale(1.1)',
                    },
                    '&:active': {
                      transform: 'translateY(-50%) scale(0.95)',
                    }
                  }}
                >
                  ›
                </Box>
              </>
            )}
          </Box>

          {/* Simplified Image indicators */}
          {carouselImages.length > 1 && (
            <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2, gap: 1.5 }}>
              {carouselImages.map((_, index) => (
                <Box
                  key={index}
                  onClick={() => handleDotClick(index)}
                  sx={{
                    width: 8,
                    height: 8,
                    borderRadius: '50%',
                    backgroundColor: index === currentImageIndex ? '#8f8300ff' : '#cdab00ff',
                    cursor: 'pointer',
                    transition: 'background-color 0.3s ease',
                    '&:hover': {
                      backgroundColor: '#999',
                    },
                  }}
                />
              ))}
            </Box>
          )}
        </>
      ) : (
        <Typography sx={{ textAlign: 'center', py: 5 }} color="text.secondary">
          No images available
        </Typography>
      )}
    </Box>
  );
}

export default Dashboard;