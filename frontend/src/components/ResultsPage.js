// frontend/src/components/ResultsPage.js
import { useState } from "react";
import axios from "axios";
import { Container } from "@mui/material";
import ResultFilter from "./ResultFilter";
import ResultPosters from "./ResultPosters";
import API_BASE_URL from '../apiConfig'; 

function ResultsPage() {
  const [posters, setPosters] = useState([]);
  const [hasSearched, setHasSearched] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  // This function is called by the filter component when the user clicks "Get Result"
  const handleFilter = (filters) => {
    // Don't do anything if no event is selected
    if (!filters.event) {
      setHasSearched(false);
      return;
    }

    // --- Start the search process ---
    setHasSearched(true);
    setIsLoading(true);
    setPosters([]); // Immediately clear old posters

    const fetchPosters = async () => {
      try {
        // Call the backend to generate and get the poster URLs
        const response = await axios.get(
          `${API_BASE_URL}/api/generate-event-posters/${filters.event}/`,
        );
        
        // This is the key: we log the data to see what the API is sending
        console.log("Received data from API:", response.data);

        // Update the state with the new posters
        setPosters(response.data);

      } catch (error) {
        console.error("Error fetching posters!", error);
        setPosters([]); // Ensure posters are cleared if an error occurs
      } finally {
        setIsLoading(false); // Stop the loading animation
      }
    };

    fetchPosters();
  };

  return (
    <Container maxWidth="lg" sx={{ pt: 4 }}>
      {/* The ResultFilter component, which you have styled, goes here */}
      <ResultFilter onFilter={handleFilter} />

      {/* This will now correctly display the posters or a loading spinner */}
      {hasSearched && <ResultPosters posters={posters} isLoading={isLoading} />}
    </Container>
  );
}

export default ResultsPage;