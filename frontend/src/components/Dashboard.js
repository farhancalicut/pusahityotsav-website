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
    <Box sx={{ py: { xs: 1, md: 2 }, backgroundColor: '#FFD700', minHeight: '80vh' }}>
      <Container maxWidth="md" sx={{ px: { xs: 2, sm: 3, md: 4 } }}>
        <Typography 
          variant="h4" 
          component="h1" 
          sx={{ 
            textAlign: 'center', 
            mb: { xs: 1.5, md: 2 }, 
            mt: { xs: 1, md: 1.5 },
            fontWeight: 'bold',
            fontFamily: 'Poppins-Bold, Arial, sans-serif',
            color: '#1e1e1eff',
            fontSize: { xs: '1.5rem', md: '2rem' }
          }}
        >
          - Updates -
        </Typography>

        <style jsx>{`
          @font-face {
            font-family: 'Poppins-Bold';
            src: url('./assets/fonts/Poppins-Bold.ttf') format('truetype');
            font-weight: bold;
            font-style: normal;
          }
          
          .slide-container {
            position: relative;
            overflow: hidden;
            width: 100%;
            height: 55vh;
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 0 auto;
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
            padding: 15px;
          }
          
          .slide-image {
            max-width: 80%;
            max-height: 80%;
            width: auto;
            height: auto;
            object-fit: contain;
            display: block;
            border-radius: 12px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
          }
          
          /* Mobile specific styles */
          @media (max-width: 768px) {
            .slide-container {
              height: 45vh;
            }
            
            .slide-item {
              padding: 12px;
            }
            
            .slide-image {
              max-width: 85%;
              max-height: 85%;
              border-radius: 10px;
            }
          }
          
          /* Small mobile devices */
          @media (max-width: 480px) {
            .slide-container {
              height: 40vh;
            }
            
            .slide-item {
              padding: 10px;
            }
            
            .slide-image {
              max-width: 90%;
              max-height: 90%;
              border-radius: 8px;
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
              mt: { xs: 1.5, md: 2 },
              mb: { xs: 1, md: 1.5 },
              gap: { xs: 0.8, md: 1.2 },
              pb: 1
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