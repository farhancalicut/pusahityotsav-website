// frontend/src/components/ThemeNote.js
import { useState } from 'react';
import { Box, Typography, Button } from '@mui/material';

function ThemeNote() {
  const [isExpanded, setIsExpanded] = useState(false);

  const handleToggle = () => {
    setIsExpanded(!isExpanded);
  };

  return (
    <Box sx={{ backgroundColor: 'black', color: 'white', py: 8, px: 2 }}>
      <Box 
        sx={{ 
          maxWidth: '1200px', 
          margin: '0 auto',
          display: 'flex',
          flexDirection: { xs: 'column', md: 'row' }, // column on mobile, row on desktop
          alignItems: 'flex-start',
          gap: 4
        }}
      >
        {/* === Image (Left) === */}
        <Box
          component="img"
          src="/images/theme logo.png"
          alt="Theme Logo"
          sx={{
            maxWidth: { xs: '200px', md: '250px' },
            width: '100%',
            height: 'auto',
            objectFit: 'contain',
            margin: { xs: '0 auto', md: 3 }, // center on mobile
          }}
        />

        
        <Box sx={{ flex: 1, textAlign: { xs: 'center', md: 'left' } }}>
          <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 3 , color: '#fffb00ff'}}>
            Theme Note: Chronicling the Coromandel
          </Typography>
          <Typography variant="body1" sx={{ lineHeight: 1.8, mb: 3 }}>
            This year, Pondicherry University adds a unique dimension to SSF Sahithyolsav by embracing the theme “Chronicling the Coromandel,” inviting students to explore the region’s layered history of trade, colonialism, spirituality, and linguistic diversity through creative expression.
          </Typography>

          <Typography variant="body1" sx={{ lineHeight: 1.8, mb: 3 }}>
            From poetry that captures the coastal breeze to essays on forgotten ports and visual art reflecting cultural vibrancy, the theme encourages a rediscovery of the stories that shaped the southern shoreline of India.
          </Typography>

          {/** Expandable part */}
          <Box
            sx={{
              display: { xs: isExpanded ? 'block' : 'none', md: 'block' },
            }}
          >
            <Typography variant="body1" sx={{ lineHeight: 1.8, mb: 4 }}>
              By spotlighting the Coromandel, the festival bridges regional identity with national and global conversations, empowering students to become thoughtful storytellers rooted in heritage yet inspired to reach beyond borders.
            </Typography>
          </Box>

          {/* Read More Button */}
          <Button
            variant="contained"
            onClick={handleToggle}
            sx={{
              backgroundColor: '#ffab00',
              color: 'black',
              fontWeight: 'bold',
              borderRadius: '4px',
              textTransform: 'uppercase',
              mt: 2,
              display: { xs: 'inline-flex', md: 'none' }, // only mobile
              '&:hover': {
                backgroundColor: '#e69900',
              },
            }}
          >
            {isExpanded ? 'Read Less' : 'Read More'}
          </Button>
        </Box>
      </Box>
    </Box>
  );
}

export default ThemeNote;
