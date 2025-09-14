// frontend/src/components/ResultPosters.js
// import React from 'react';
import { Grid, Paper, Button, Typography, Box, CircularProgress } from '@mui/material';
import axios from 'axios'; // Import axios

function ResultPosters({ posters, isLoading }) {
  if (isLoading) {
    return <Box sx={{ display: 'flex', justifyContent: 'center', my: 5 }}><CircularProgress /></Box>;
  }

  if (!posters || posters.length === 0) {
    return <Typography sx={{ mt: 4, textAlign: 'center' }}>No winner posters to display for this program.</Typography>;
  }

  // --- NEW: Function to handle the download ---
  const handleDownload = async (imageUrl, posterId) => {
    try {
      // 1. Fetch the image data from the URL as a 'blob'
      const response = await axios.get(imageUrl, {
        responseType: 'blob',
      });

      // 2. Create a temporary URL from the blob data
      const url = window.URL.createObjectURL(new Blob([response.data]));
      
      // 3. Create a temporary link element
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `result-poster-${posterId}.png`); // Set the filename
      
      // 4. Programmatically click the link to trigger the download
      document.body.appendChild(link);
      link.click();
      
      // 5. Clean up by removing the link
      link.parentNode.removeChild(link);
      window.URL.revokeObjectURL(url); // Free up memory
    } catch (error) {
      console.error('Error downloading the file!', error);
    }
  };

  return (
    <Box sx={{ my: 4 }}>
      <Typography variant="h4" gutterBottom sx={{ fontWeight: 'bold' }}>Posters</Typography>
      <Grid container spacing={4} justifyContent="center">
        {posters.map((poster) => (
          <Grid item xs={12} sm={6} md={4} key={poster.id}>
            <Paper elevation={3} sx={{ textAlign: 'center', p: 2, borderRadius: 2 }}>
              <img 
                src={poster.url} 
                alt="Result Poster" 
                style={{ 
                  width: '100%', 
                  height: 'auto', 
                  display: 'block',
                  borderRadius: '4px' 
                }} 
              />
              {/* --- UPDATED: Button now uses onClick --- */}
              <Button 
                variant="contained" 
                onClick={() => handleDownload(poster.url, poster.id)} // Use the new handler
                fullWidth
                sx={{ mt: 2 }}
              >
                Download
              </Button>
            </Paper>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}

export default ResultPosters;