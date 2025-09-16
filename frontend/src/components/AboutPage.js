// import React from 'react';
import { Box, Typography, Container } from "@mui/material";

function AboutPage() {
  return (
    <Container maxWidth="xl" sx={{ py: 6, px: { xs: 4, sm: 8, md: 10 } }}>
      <Box
        sx={{
          display: "flex",
          flexDirection: { xs: "column", md: "row" },
          alignItems: "center",
          gap: 4,
        }}
      >
        <Box
          component="img"
          src="/images/about_logo.png"
          alt="Aynul Haqqeel"
          sx={{
            maxWidth: "200px",
            width: "100%",
            height: "auto",
            flexShrink: 0,
          }}
        />

        <Box>
          <Typography
            variant="h5"
            sx={{
              fontWeight: "bold",
              textAlign: { xs: "left", md: "left" },
              mb: 2,
            }}
          >
            About Sahityotsav
          </Typography>

          <Typography
            variant="body1"
            sx={{ fontSize: "1.0rem", lineHeight: 1.4 }}
          >
            Incepted 32 years ago in 1993, it has its commencement from the
            grassroot level - that is a family Sahityotsav. Crossing the levels
            of units, sectors, divisions, districts and 26 states in the
            country, it finds its actualization in the national level each year.
            As a prime aim, Sahityotsav is focusing on the embellishment of the
            creativity of thousands and more students across the country, and
            now it became one of the towering figures in the realm of cultural
            festivals of India. Sahityotsav has its assets of thousands of young
            vibrant studentdom who have came forward to meet the need of the
            time in its various aspects. They are ready to question all the anti
            social hullabaloos using their talents like writing, drawing,
            criticizing...etc.
          </Typography>
        </Box>
      </Box>
    </Container>
  );
}

export default AboutPage;
