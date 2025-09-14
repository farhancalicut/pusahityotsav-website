// frontend/src/components/ResultFilter.js
import { useState, useEffect } from 'react';
import axios from 'axios';
import { Paper, Typography, FormControl, InputLabel, Select, MenuItem, Button } from '@mui/material';

function ResultFilter({ onFilter }) {
  const [categories, setCategories] = useState([]);
  const [allEvents, setAllEvents] = useState([]); // Store all events
  const [filteredEvents, setFilteredEvents] = useState([]); // Events for the dropdown
  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedEvent, setSelectedEvent] = useState('');

  // Fetch initial data
  useEffect(() => {
    const fetchData = async () => {
      try {
        const [catResponse, eventResponse] = await Promise.all([
          axios.get('http://127.0.0.1:8000/api/categories/'),
          axios.get('http://127.0.0.1:8000/api/events/')
        ]);
        setCategories(catResponse.data);
        setAllEvents(eventResponse.data);
        setFilteredEvents(eventResponse.data); // Initially show all
      } catch (error) {
        console.error('Error fetching filter data!', error);
      }
    };
    fetchData();
  }, []);

  // When a category is selected, filter the events dropdown
  const handleCategoryChange = (e) => {
    const categoryId = e.target.value;
    setSelectedCategory(categoryId);
    setSelectedEvent(''); // Reset selected event

    if (categoryId) {
      // Find the category name from the ID
      const categoryName = categories.find(c => c.id === categoryId)?.name;
      // Filter events that belong to that category
      setFilteredEvents(allEvents.filter(event => event.category === categoryName));
    } else {
      // If no category is selected, show all events
      setFilteredEvents(allEvents);
    }
  };

  const handleFilter = () => {
    onFilter({
      category: selectedCategory,
      event: selectedEvent,
    });
  };

  return (
    <Paper
      elevation={3}
      sx={{
        p: 4, borderRadius: 3, backgroundColor: '#e3f2fd',
        border: '1px solid #90caf9', maxWidth: '600px', margin: '0 auto 40px auto'
      }}
    >
      <Typography variant="h5" sx={{ fontWeight: 'bold', color: '#0d47a1', mb: 3 }}>
        Check Results
      </Typography>
      <FormControl fullWidth sx={{ mb: 2 }}>
        <InputLabel id="category-select-label">Category</InputLabel>
        <Select
          labelId="category-select-label"
          value={selectedCategory}
          label="Category"
          onChange={handleCategoryChange} // Use the new handler
          sx={{ backgroundColor: 'white' }}
        >
          <MenuItem value=""><em>All Categories</em></MenuItem>
          {categories.map((cat) => (
            <MenuItem key={cat.id} value={cat.id}>{cat.name}</MenuItem>
          ))}
        </Select>
      </FormControl>
      <FormControl fullWidth sx={{ mb: 3 }}>
        <InputLabel id="program-select-label">Program</InputLabel>
        <Select
          labelId="program-select-label"
          value={selectedEvent}
          label="Program"
          onChange={(e) => setSelectedEvent(e.target.value)}
          sx={{ backgroundColor: 'white' }}
        >
          <MenuItem value=""><em>All Programs</em></MenuItem>
          {/* Now maps over the filtered list */}
          {filteredEvents.map((event) => (
            <MenuItem key={event.id} value={event.id}>{event.name}</MenuItem>
          ))}
        </Select>
      </FormControl>
      <Button 
        variant="contained" 
        onClick={handleFilter}
        fullWidth
        sx={{ py: 1.5, backgroundColor: '#1976d2', fontWeight: 'bold' }}
      >
        Get Results
      </Button>
    </Paper>
  );
}

export default ResultFilter;