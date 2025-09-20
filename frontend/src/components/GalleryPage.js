// frontend/src/components/GalleryPage.js
import { useState, useEffect } from "react";
import axios from "axios";
import {
  Box, Typography, FormControl, InputLabel, Select, MenuItem, IconButton,
} from "@mui/material";
import DownloadIcon from "@mui/icons-material/Download";
import "./GalleryPage.css";
import API_BASE_URL from "../apiConfig";

function GalleryPage() {
  const [images, setImages] = useState([]);
  const [filteredImages, setFilteredImages] = useState([]);
  const [years, setYears] = useState([]);
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());

  // Function to handle direct image download
  const handleDownload = async (imageUrl, caption) => {
    try {
      const response = await fetch(imageUrl);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      
      const link = document.createElement('a');
      link.href = url;
      link.download = `${caption}.jpg`; // Set the filename
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      // Clean up the object URL
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Download failed:', error);
      // Fallback to opening in new tab
      window.open(imageUrl, '_blank');
    }
  };

  useEffect(() => {
    axios
      .get(`${API_BASE_URL}/api/gallery/`)
      .then((response) => {
        setImages(response.data);
        
        const currentYear = new Date().getFullYear();
        const uniqueYears = [...new Set(response.data.map((img) => img.year))].sort((a, b) => b - a);
        setYears(uniqueYears);

        const yearToFilter = uniqueYears.includes(currentYear) ? currentYear : (uniqueYears[0] || '');
        setSelectedYear(yearToFilter);
        setFilteredImages(response.data.filter((img) => img.year === yearToFilter));
      })
      .catch((error) => {
        console.error("Error fetching gallery images!", error);
      });
  }, []);

  const handleYearChange = (event) => {
    const year = event.target.value;
    setSelectedYear(year);
    setFilteredImages(images.filter((img) => img.year === year));
  };

  return (
    <Box sx={{ maxWidth: "1200px", margin: "0 auto", p: 4 }}>
      <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 4 }}>
        <Typography variant="h5" sx={{ fontWeight: "bold" }}>Poster Gallery</Typography>
        <FormControl sx={{ minWidth: 120 }} size="small">
          <InputLabel>Year</InputLabel>
          <Select value={selectedYear} label="Year" onChange={handleYearChange}>
            {years.map((year) => (
              <MenuItem key={year} value={year}>{year}</MenuItem>
            ))}
          </Select>
        </FormControl>
      </Box>

      {filteredImages.length > 0 ? (
        <div className="gallery-grid">
          {filteredImages.map((image) => (
            <div key={image.id} className="gallery-item">
              {/* Use image.image directly, which will now be the full Cloudinary URL */}
              <img 
                src={image.image} 
                alt={image.caption}
                onError={(e) => {
                  console.error(`Failed to load image: ${image.image}`);
                  e.target.src = '/placeholder-image.png'; // Add a placeholder image if needed
                }}
                loading="lazy"
              />
              
              {/* Direct download button */}
              <IconButton
                onClick={() => handleDownload(image.image, image.caption)}
                sx={{
                  position: "absolute", bottom: 8, right: 8,
                  backgroundColor: "rgba(0, 0, 0, 0.5)", color: "white",
                  "&:hover": { backgroundColor: "rgba(0, 0, 0, 0.7)" },
                }}
              >
                <DownloadIcon />
              </IconButton>
            </div>
          ))}
        </div>
      ) : (
        <Typography variant="body2">Images for the selected year have not been uploaded yet.</Typography>
      )}
    </Box>
  );
}

export default GalleryPage;