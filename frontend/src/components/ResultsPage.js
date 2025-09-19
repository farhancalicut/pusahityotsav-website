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

  const handleFilter = (filters) => {
    if (!filters.event) {
      setHasSearched(false);
      return;
    }

    setHasSearched(true);
    setIsLoading(true);
    setPosters([]);

    const fetchPosters = async () => {
      try {
        const response = await axios.get(
          `${API_BASE_URL}/api/generate-event-posters/${filters.event}/`,
        );
        setPosters(response.data);
      } catch (error) {
        console.error("Error fetching posters!", error);
        setPosters([]);
      } finally {
        setIsLoading(false);
      }
    };

    fetchPosters();
  };

  return (
    <Container maxWidth="lg" sx={{ pt: 4 }}>
      <ResultFilter onFilter={handleFilter} />
      {hasSearched && <ResultPosters posters={posters} isLoading={isLoading} />}
    </Container>
  );
}

export default ResultsPage;