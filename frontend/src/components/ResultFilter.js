// frontend/src/components/ResultFilter.js
import { useState, useEffect } from 'react';
import axios from 'axios';
import { Paper, Typography, FormControl, InputLabel, Select, MenuItem, Button } from '@mui/material';
import API_BASE_URL from '../apiConfig';

function ResultFilter({ onFilter }) {
  const [categories, setCategories] = useState([]);
  const [events, setEvents] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedEvent, setSelectedEvent] = useState('');

  // Fetch all categories when the component first loads
  useEffect(() => {
    axios.get(`${API_BASE_URL}/api/categories/`)
      .then(response => {
        setCategories(response.data);
      })
      .catch(error => console.error('Error fetching categories:', error));
  }, []);

  // Fetch the correct list of events whenever a category is selected
  useEffect(() => {
    if (selectedCategory) {
      // Use the smart API endpoint to get category-specific + general events
      axios.get(`${API_BASE_URL}/api/events-for-registration/${selectedCategory}/`)
        .then(response => {
          setEvents(response.data);
        })
        .catch(error => console.error('Error fetching events:', error));
    } else {
      setEvents([]); // Clear the event list if no category is selected
    }
  }, [selectedCategory]);

  const handleFilterClick = () => {
    onFilter({ event: selectedEvent });
  };

  // This JSX is based on the previous code you shared, restoring your design
  return (
    <Paper
      elevation={3}
      sx={{
        p: 4,
        borderRadius: 3,
        backgroundColor: "#e3f2fd",
        border: "1px solid #90caf9",
        maxWidth: "600px",
        margin: "0 auto 40px auto",
      }}
    >
      <Typography
        variant="h5"
        sx={{ fontWeight: "bold", color: "#0d47a1", mb: 3, textAlign: "center" }}
      >
        Check Results
      </Typography>
      <FormControl fullWidth sx={{ mb: 2 }}>
        <InputLabel id="category-select-label">Category</InputLabel>
        <Select
          labelId="category-select-label"
          value={selectedCategory}
          label="Category"
          onChange={(e) => {
            setSelectedCategory(e.target.value);
            setSelectedEvent(''); // Reset event selection when category changes
          }}
          sx={{ backgroundColor: "white" }}
        >
          <MenuItem value="">
            <em>Select a Category</em>
          </MenuItem>
          {categories.map((cat) => (
            <MenuItem key={cat.id} value={cat.id}>
              {cat.name}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
      <FormControl fullWidth sx={{ mb: 3 }} disabled={!selectedCategory}>
        <InputLabel id="program-select-label">Program</InputLabel>
        <Select
          labelId="program-select-label"
          value={selectedEvent}
          label="Program"
          onChange={(e) => setSelectedEvent(e.target.value)}
          sx={{ backgroundColor: "white" }}
        >
          <MenuItem value="">
            <em>Select a Program</em>
          </MenuItem>
          {events.map((event) => (
            <MenuItem key={event.id} value={event.id}>
              {event.name}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
      <Button
        variant="contained"
        onClick={handleFilterClick}
        disabled={!selectedEvent}
        fullWidth
        sx={{ py: 1.5, backgroundColor: "#1976d2", fontWeight: "bold", mb: 2 }}
      >
        Get Results
      </Button>
      
      {/* Export Buttons */}
     {/* <Typography
        variant="h6"
        sx={{ fontWeight: "bold", color: "#0d47a1", mb: 2, textAlign: "center" }}
      >
        Export Winners
      </Typography>
      
      <Button
        variant="outlined"
        onClick={() => window.open(`${API_BASE_URL}/api/export-winners/`, '_blank')}
        fullWidth
        sx={{ py: 1.5, mb: 1, borderColor: "#1976d2", color: "#1976d2", fontWeight: "bold" }}
      >
        Export All Winners CSV
      </Button>
      
      {selectedEvent && (
        <Button
          variant="outlined"
          onClick={() => window.open(`${API_BASE_URL}/api/export-winners/${selectedEvent}/`, '_blank')}
          fullWidth
          sx={{ py: 1.5, borderColor: "#4caf50", color: "#4caf50", fontWeight: "bold" }}
        >
          Export Selected Event Winners CSV
        </Button> */}
      )}
    </Paper>
  );
}

export default ResultFilter;