// frontend/src/components/GalleryPage.js
import { useState, useEffect } from "react";
import axios from "axios";
import {
  Box,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  IconButton,
} from "@mui/material";
import DownloadIcon from "@mui/icons-material/Download";
import "./GalleryPage.css";
import API_BASE_URL from '../apiConfig'; 

function GalleryPage() {
  const [allImages, setAllImages] = useState([]);
  const [filteredImages, setFilteredImages] = useState([]);
  const [years, setYears] = useState([]);
  // --- THIS IS THE KEY CHANGE ---
  // Set the default selected year to 2025
  const [selectedYear, setSelectedYear] = useState(2025);

  useEffect(() => {
    axios
      .get(`${API_BASE_URL}/api/gallery/`)
      .then((response) => {
        const images = response.data;
        setAllImages(images);

        // Filter for the default year (2025) as soon as data arrives
        setFilteredImages(images.filter((img) => img.year === 2025));

        const uniqueYears = [...new Set(images.map((img) => img.year))];
        setYears(uniqueYears.sort((a, b) => b - a));
      })
      .catch((error) => {
        console.error("Error fetching gallery images!", error);
      });
  }, []);

  const handleYearChange = (event) => {
    const year = event.target.value;
    setSelectedYear(year);
    // Filter images based on the newly selected year
    setFilteredImages(allImages.filter((img) => img.year === year));
  };

  // --- NEW: Function to handle the download ---
  const handleDownload = async (imageUrl, caption) => {
    try {
      const response = await axios.get(imageUrl, {
        responseType: "blob",
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `${caption}.png`);
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Error downloading the file!", error);
    }
  };

  return (
    <Box sx={{ maxWidth: "1200px", margin: "0 auto", p: 4 }}>
      <Box
        sx={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          mb: 4,
        }}
      >
        <Typography variant="h5" sx={{ fontWeight: "bold" }}>
          Photo Gallery
        </Typography>

        <FormControl sx={{ minWidth: 120 }} size="small">
          <InputLabel>Year</InputLabel>
          <Select value={selectedYear} label="Year" onChange={handleYearChange}>
            {/* "All Years" MenuItem has been removed */}
            {years.map((year) => (
              <MenuItem key={year} value={year}>
                {year}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </Box>

      {filteredImages.length > 0 ? (
        <div className="gallery-grid">
          {filteredImages.map((image) => (
            <div key={image.id} className="gallery-item">
              <img src={image.image_url} alt={image.caption} />
              <IconButton
  component="a" // <-- Make the button act like a link
  href={image.image_url}// <-- The direct URL to the Cloudinary image
  download={`${image.caption}.png`} // <-- Suggest a filename to the browser
  target="_blank" // <-- Helps with compatibility
  rel="noopener noreferrer" // <-- Good security practice for new tabs
  sx={{
    position: 'absolute',
    bottom: 8,
    right: 8,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    color: 'white',
    '&:hover': {
      backgroundColor: 'rgba(0, 0, 0, 0.7)',
    },
  }}
>
  <DownloadIcon />
</IconButton>
            </div>
          ))}
        </div>
      ) : (
        // Updated message
        <Typography variant="body2">
          Images for the year 2025 have not been uploaded yet.
        </Typography>
      )}
    </Box>
  );
}

export default GalleryPage;
