// frontend/src/components/Scoreboard.js
import { useState, useEffect } from "react";
import axios from "axios";
import { Box, Typography, Paper, Chip } from "@mui/material";
import ArrowForwardIosIcon from "@mui/icons-material/ArrowForwardIos";
import CountUp from "react-countup";
import { motion } from "framer-motion";
import { useInView } from "react-intersection-observer";
import API_BASE_URL from '../apiConfig'; 

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.2, // SLOWER: Increase the delay between each item
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 30 }, // Start slightly further down
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      type: "spring",
      stiffness: 80, // Make the spring a bit softer
      duration: 0.8, // SLOWER: Increase the duration of the animation
    },
  },
};
// --- END UPDATE ---

function Scoreboard() {
  const [points, setPoints] = useState([]);

  // --- UPDATED: useInView Hook ---
  const { ref, inView } = useInView({
    // triggerOnce: true, // REMOVED: This allows the animation to re-trigger
    threshold: 0.2, // Trigger when 20% of the component is visible
  });
  // --- END UPDATE ---

  const [hasAnimated, setHasAnimated] = useState(false);

  const fetchPoints = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/points/`);
      setPoints(response.data || []);
    } catch (error) {
      console.error("Error fetching points!", error);
      setPoints([]); // Ensure points is always an array
    }
  };

  useEffect(() => {
    fetchPoints();
    const interval = setInterval(fetchPoints, 10000);
    return () => clearInterval(interval);
  }, []);

  // Track if the animation has occurred
  useEffect(() => {
    if (inView) {
      setHasAnimated(true);
    }
  }, [inView]);

  const topThree = Array.isArray(points) ? points.slice(0, 3) : [];
  const restOfTeams = Array.isArray(points) ? points.slice(3) : [];

  return (
    <Box ref={ref} sx={{ py: 8, backgroundColor: "#ffffff" }}>
      <Box sx={{ px: { xs: 2, md: 4, lg: 6 } }}>
        <Box sx={{ display: "flex", alignItems: "center", mb: 4 }}>
          <Typography variant="h4" sx={{ fontWeight: "bold", mr: 2 }}>
            Team Score
          </Typography>
          <Chip
            label="LIVE"
            color="primary"
            size="small"
            sx={{ backgroundColor: "#1976d2" }}
          />
        </Box>

        {/* --- Main Flexbox Layout for the two halves --- */}
        <Box
          sx={{
            display: "flex",
            flexDirection: { xs: "column", md: "row" },
            gap: 5,
          }}
        >
          {/* Left Half */}
          <Box sx={{ flex: 1, minWidth: 0 }}>
            <Typography
              variant="h5"
              sx={{
                fontWeight: 600,
                mb: 3,
                textAlign: { xs: "center", md: "left" },
              }}
            >
              Current Status
            </Typography>
            <motion.div
              variants={containerVariants}
              initial="hidden"
              animate={inView ? "visible" : "hidden"}
            >
              {topThree.map((team, index) => (
                <motion.div key={team.group_name} variants={itemVariants}>
                  <Paper
                    elevation={0}
                    sx={{
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                      p: 2,
                      mb: 2,
                      borderRadius: 2,
                      backgroundColor: "#f5f5f5",
                    }}
                  >
                    <Box sx={{ display: "flex", alignItems: "center" }}>
                      <Box
                        sx={{
                          backgroundColor: "#1976d2",
                          color: "white",
                          width: 32,
                          height: 32,
                          borderRadius: 1,
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                          mr: 2,
                          fontWeight: "bold",
                          fontSize: "1rem",
                        }}
                      >
                        {index + 1}
                      </Box>
                      <Typography variant="h6" sx={{ fontWeight: 500 }}>
                        {team.group_name}
                      </Typography>
                    </Box>
                    <Typography variant="h6" sx={{ fontWeight: "bold" }}>
                      {hasAnimated && (
                        <CountUp end={team.total_points} duration={2} />
                      )}
                    </Typography>
                  </Paper>
                </motion.div>
              ))}
            </motion.div>
          </Box>

          {/* Right Half */}
          <Box sx={{ flex: 1, minWidth: 0 }}>
            <motion.div
              variants={containerVariants}
              initial="hidden"
              animate={inView ? "visible" : "hidden"}
            >
              <Paper
                variant="outlined"
                sx={{
                  p: { xs: 1, md: 2 },
                  borderRadius: 3,
                  borderColor: "#1976d2",
                  backgroundColor: "rgba(227, 242, 253, 0.5)",
                }}
              >
                {restOfTeams.map((team) => (
                  <motion.div key={team.group_name} variants={itemVariants}>
                    <Box
                      sx={{
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                        py: 1.5,
                        px: 1,
                        borderBottom: "1px solid #e0e0e0",
                        "&:last-child": { borderBottom: "none" },
                      }}
                    >
                      <Box sx={{ display: "flex", alignItems: "center" }}>
                        <ArrowForwardIosIcon
                          sx={{ fontSize: "1.2rem", color: "#1976d2", mr: 1.5 }}
                        />
                        <Typography variant="body1">
                          {team.group_name}
                        </Typography>
                      </Box>
                      <Typography sx={{ fontWeight: "bold" }}>
                        {hasAnimated && (
                          <CountUp end={team.total_points} duration={2} />
                        )}
                      </Typography>
                    </Box>
                  </motion.div>
                ))}
              </Paper>
            </motion.div>
          </Box>
        </Box>
      </Box>
    </Box>
  );
}

export default Scoreboard;
