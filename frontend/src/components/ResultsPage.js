// frontend/src/components/ResultsPage.js
import { useState } from "react";
import axios from "axios";
import { Container } from "@mui/material";
import ResultFilter from "./ResultFilter";
import ResultPosters from "./ResultPosters";
import { API_BASE_URL } from "../apiConfig";

function ResultsPage() {
  const [posters, setPosters] = useState([]);
  const [hasSearched, setHasSearched] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  // This function is called by the filter component
  const handleFilter = (filters) => {
    // Don't search if no program is selected
    if (!filters.event) {
      setHasSearched(false);
      return;
    }

    setHasSearched(true);
    setIsLoading(true); // Start loading animation
    setPosters([]); // Clear any old posters

    const fetchPosters = async () => {
      try {
        const response = await axios.get(
          `${API_BASE_URL}/api/generate-event-posters/${filters.event}/`,
        );
        setPosters(response.data);
      } catch (error) {
        console.error("Error fetching posters!", error);
        setPosters([]); // Ensure posters are cleared on error
      } finally {
        setIsLoading(false); // Stop loading animation
      }
    };

    fetchPosters();
  };

  return (
    <Container maxWidth="lg" sx={{ pt: 4 }}>
      <ResultFilter onFilter={handleFilter} />

      {/* Conditionally render the posters component or a loading spinner */}
      {hasSearched && <ResultPosters posters={posters} isLoading={isLoading} />}
    </Container>
  );
}

export default ResultsPage;
