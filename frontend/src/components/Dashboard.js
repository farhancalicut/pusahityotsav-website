// frontend/src/components/Dashboard.js
import React, { useState, useEffect, useRef } from 'react';
import { Box, Container, Typography, Paper } from '@mui/material';
import API_BASE_URL from '../apiConfig';

function Dashboard() {
  const [carouselImages, setCarouselImages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const scrollContainerRef = useRef(null);

  useEffect(() => {
    fetchCarouselImages();
  }, []);

  const fetchCarouselImages = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/carousel/`);
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

  // Auto-scroll effect
  useEffect(() => {
    if (carouselImages.length === 0) return;

    const scrollContainer = scrollContainerRef.current;
    if (!scrollContainer) return;

    let scrollPosition = 0;
    const scrollSpeed = 1; // pixels per interval
    const scrollInterval = 50; // milliseconds

    const autoScroll = () => {
      scrollPosition += scrollSpeed;
      
      // If we've scrolled past the first set of images, reset to beginning
      if (scrollPosition >= scrollContainer.scrollWidth / 2) {
        scrollPosition = 0;
      }
      
      scrollContainer.scrollLeft = scrollPosition;
    };

    const interval = setInterval(autoScroll, scrollInterval);

    // Pause scrolling on hover
    const handleMouseEnter = () => clearInterval(interval);
    const handleMouseLeave = () => {
      clearInterval(interval);
      setInterval(autoScroll, scrollInterval);
    };

    scrollContainer.addEventListener('mouseenter', handleMouseEnter);
    scrollContainer.addEventListener('mouseleave', handleMouseLeave);

    return () => {
      clearInterval(interval);
      if (scrollContainer) {
        scrollContainer.removeEventListener('mouseenter', handleMouseEnter);
        scrollContainer.removeEventListener('mouseleave', handleMouseLeave);
      }
    };
  }, [carouselImages]);

  if (loading) {
    return (
      <Box sx={{ py: 8, textAlign: 'center' }}>
        <Typography variant="h6">Loading dashboard...</Typography>
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

  // Duplicate images for seamless scrolling
  const duplicatedImages = [...carouselImages, ...carouselImages];

  return (
    <Box sx={{ py: 4, backgroundColor: '#f5f5f5', minHeight: '80vh' }}>
      <Container maxWidth="lg">
        <Typography 
          variant="h4" 
          component="h1" 
          gutterBottom 
          sx={{ 
            textAlign: 'center', 
            mb: 4, 
            fontWeight: 'bold',
            color: '#333'
          }}
        >
          Dashboard
        </Typography>

        {carouselImages.length > 0 ? (
          <Paper 
            elevation={3} 
            sx={{ 
              p: 3, 
              backgroundColor: '#fff',
              borderRadius: 2,
              overflow: 'hidden'
            }}
          >
            <Typography 
              variant="h6" 
              gutterBottom 
              sx={{ 
                textAlign: 'center', 
                mb: 3,
                color: '#555'
              }}
            >
              Featured Images
            </Typography>
            
            <Box
              ref={scrollContainerRef}
              sx={{
                display: 'flex',
                overflow: 'hidden',
                gap: 2,
                width: '100%',
                '&::-webkit-scrollbar': {
                  display: 'none'
                },
                scrollbarWidth: 'none',
                msOverflowStyle: 'none'
              }}
            >
              {duplicatedImages.map((image, index) => (
                <Box
                  key={`${image.id}-${index}`}
                  sx={{
                    minWidth: { xs: '280px', sm: '320px', md: '400px' },
                    height: { xs: '200px', sm: '240px', md: '300px' },
                    position: 'relative',
                    borderRadius: 2,
                    overflow: 'hidden',
                    boxShadow: '0 4px 8px rgba(0,0,0,0.1)',
                    transition: 'transform 0.3s ease',
                    '&:hover': {
                      transform: 'scale(1.02)'
                    }
                  }}
                >
                  <img
                    src={image.image}
                    alt={image.title}
                    style={{
                      width: '100%',
                      height: '100%',
                      objectFit: 'cover'
                    }}
                    onError={(e) => {
                      console.error('Image failed to load:', image.image);
                      e.target.style.display = 'none';
                    }}
                  />
                  
                  {/* Image overlay with title */}
                  <Box
                    sx={{
                      position: 'absolute',
                      bottom: 0,
                      left: 0,
                      right: 0,
                      background: 'linear-gradient(transparent, rgba(0,0,0,0.7))',
                      color: 'white',
                      p: 2
                    }}
                  >
                    <Typography 
                      variant="h6" 
                      sx={{ 
                        fontSize: { xs: '1rem', md: '1.25rem' },
                        fontWeight: 'bold'
                      }}
                    >
                      {image.title}
                    </Typography>
                  </Box>
                </Box>
              ))}
            </Box>
          </Paper>
        ) : (
          <Paper 
            elevation={3} 
            sx={{ 
              p: 6, 
              textAlign: 'center',
              backgroundColor: '#fff',
              borderRadius: 2
            }}
          >
            <Typography variant="h6" color="text.secondary">
              No carousel images available
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              Images can be uploaded through the admin panel
            </Typography>
          </Paper>
        )}
      </Container>
    </Box>
  );
}

export default Dashboard;