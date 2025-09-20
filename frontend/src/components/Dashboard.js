// frontend/src/components/Dashboard.js
import React, { useState, useEffect } from 'react';
import { Box, Container, Typography } from '@mui/material';
import API_BASE_URL from '../apiConfig';

function Dashboard() {
  const [carouselImages, setCarouselImages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [isSliding, setIsSliding] = useState(false);

  useEffect(() => {
    fetchCarouselImages();
  }, []);

  const fetchCarouselImages = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/carousel/`);
      if (!response.ok) {
        throw new Error(`Failed to fetch carousel images. Status: ${response.status}`);
      }
      const data = await response.json();
      setCarouselImages(data);
    } catch (err) {
      console.error('Error fetching carousel images:', err);
      setError(`Failed to load carousel images: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Auto-advance to next image with slide effect
  useEffect(() => {
    if (carouselImages.length === 0) return;

    const interval = setInterval(() => {
      setIsSliding(true);
      
      setTimeout(() => {
        setCurrentImageIndex((prevIndex) => 
          (prevIndex + 1) % carouselImages.length
        );
        setIsSliding(false);
      }, 500); // Half of the slide duration
    }, 4000); // Change image every 4 seconds

    return () => clearInterval(interval);
  }, [carouselImages]);

  const handleDotClick = (index) => {
    if (index !== currentImageIndex) {
      setIsSliding(true);
      setTimeout(() => {
        setCurrentImageIndex(index);
        setIsSliding(false);
      }, 500);
    }
  };

  if (loading) {
    return (
      <Box sx={{ py: 8, textAlign: 'center' }}>
        <Typography variant="h6">Loading...</Typography>
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

  if (carouselImages.length === 0) {
    return (
      <Box sx={{ py: 8, textAlign: 'center' }}>
        <Typography variant="h6" color="text.secondary">
          No images available
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ py: 4, backgroundColor: '#FFD700', minHeight: '80vh' }}>
      <Container maxWidth="lg">
        <style jsx>{`
          .slide-container {
            position: relative;
            overflow: hidden;
            width: 100%;
            height: 70vh;
            display: flex;
            justify-content: center;
            align-items: center;
          }
          
          .slide-track {
            display: flex;
            width: ${carouselImages.length * 100}%;
            height: 100%;
            transform: translateX(-${(currentImageIndex * 100) / carouselImages.length}%);
            transition: transform 1s ease-in-out;
          }
          
          .slide-item {
            width: ${100 / carouselImages.length}%;
            height: 100%;
            display: flex;
            justify-content: center;
            align-items: center;
            flex-shrink: 0;
          }
          
          .slide-image {
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
            display: block;
          }
        `}</style>
        
        <Box className="slide-container">
          <Box className="slide-track">
            {carouselImages.map((image, index) => (
              <Box key={image.id} className="slide-item">
                <img
                  src={image.image}
                  alt={`Slide ${index + 1}`}
                  className="slide-image"
                  onError={(e) => {
                    console.error('Image failed to load:', image.image);
                    e.target.style.display = 'none';
                  }}
                />
              </Box>
            ))}
          </Box>
        </Box>

        {/* Image indicators */}
        {carouselImages.length > 1 && (
          <Box 
            sx={{ 
              display: 'flex', 
              justifyContent: 'center', 
              mt: 3,
              gap: 1
            }}
          >
            {carouselImages.map((_, index) => (
              <Box
                key={index}
                onClick={() => handleDotClick(index)}
                sx={{
                  width: 12,
                  height: 12,
                  borderRadius: '50%',
                  backgroundColor: index === currentImageIndex ? '#1976d2' : '#ccc',
                  cursor: 'pointer',
                  transition: 'background-color 0.3s ease',
                  '&:hover': {
                    backgroundColor: index === currentImageIndex ? '#1976d2' : '#999'
                  }
                }}
              />
            ))}
          </Box>
        )}
      </Container>
    </Box>
  );
}

export default Dashboard;