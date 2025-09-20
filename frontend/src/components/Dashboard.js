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
    }, 5000); // Change image every 5 seconds

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
    <Box sx={{ py: { xs: 2, md: 4 }, backgroundColor: '#FFD700', minHeight: '60vh' }}>
      <Container maxWidth="lg" sx={{ px: { xs: 1, sm: 2, md: 3 } }}>
        <style jsx>{`
          .slide-container {
            position: relative;
            overflow: hidden;
            width: 100%;
            height: 80vh;
            display: flex;
            justify-content: center;
            align-items: center;
          }
          
          .slide-track {
            display: flex;
            width: ${carouselImages.length * 100}%;
            height: 100%;
            transform: translateX(-${currentImageIndex * 100}%);
            transition: transform 1s ease-in-out;
          }
          
          .slide-item {
            width: 100%;
            height: 100%;
            display: flex;
            justify-content: center;
            align-items: center;
            flex-shrink: 0;
            padding: 10px;
          }
          
          .slide-image {
            max-width: 100%;
            max-height: 100%;
            width: auto;
            height: auto;
            object-fit: contain;
            display: block;
            border-radius: 8px;
          }
          
          /* Mobile specific styles */
          @media (max-width: 768px) {
            .slide-container {
              height: 70vh;
            }
            
            .slide-item {
              padding: 5px;
            }
            
            .slide-image {
              border-radius: 4px;
            }
          }
          
          /* Small mobile devices */
          @media (max-width: 480px) {
            .slide-container {
              height: 60vh;
            }
            
            .slide-item {
              padding: 3px;
            }
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
              mt: { xs: 2, md: 3 },
              gap: { xs: 0.5, md: 1 },
              pb: 2
            }}
          >
            {carouselImages.map((_, index) => (
              <Box
                key={index}
                onClick={() => handleDotClick(index)}
                sx={{
                  width: { xs: 10, md: 12 },
                  height: { xs: 10, md: 12 },
                  borderRadius: '50%',
                  backgroundColor: index === currentImageIndex ? '#1976d2' : '#ccc',
                  cursor: 'pointer',
                  transition: 'background-color 0.3s ease',
                  '&:hover': {
                    backgroundColor: index === currentImageIndex ? '#1976d2' : '#999'
                  },
                  // Larger touch target for mobile
                  '&::before': {
                    content: '""',
                    position: 'absolute',
                    width: { xs: 24, md: 20 },
                    height: { xs: 24, md: 20 },
                    top: '50%',
                    left: '50%',
                    transform: 'translate(-50%, -50%)',
                    display: { xs: 'block', md: 'none' }
                  },
                  position: 'relative'
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