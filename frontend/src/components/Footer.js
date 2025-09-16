// frontend/src/components/Footer.js
// import React from 'react';
import {
  Box,
  Container,
  Grid,
  Typography,
  Link,
  IconButton,
} from "@mui/material";

// Import Social Media Icons
import InstagramIcon from "@mui/icons-material/Instagram";
import FacebookIcon from "@mui/icons-material/Facebook";
// import YouTubeIcon from '@mui/icons-material/YouTube';
// import XIcon from '@mui/icons-material/X';
import WhatsAppIcon from "@mui/icons-material/WhatsApp";

function Footer() {
  return (
    <Box
      component="footer"
      sx={{
        backgroundColor: "#424242",
        color: "white",
        py: 4,
        mt: "auto",
      }}
    >
      <Container maxWidth="lg">
        {/* THIS IS THE KEY CHANGE */}
        <Grid
          container
          spacing={4}
          alignItems="center"
          justifyContent="space-between"
        >
          <Grid xs={12} sm="auto">
            <Typography variant="h6" gutterBottom sx={{ fontWeight: "bold" }}>
              Contact Us
            </Typography>
            <Typography variant="body2" sx={{ color: "#bdbdbd" /* mb: 1*/ }}>
              SSF Pondicherry University, Kalapet
            </Typography>
            <Typography
              variant="body2"
              sx={{ color: "#bdbdbd", fontSize: "0.65rem" }}
            >
              Email: ssfpondicherryuniversity@gmail.com
              {/* <br />
              DeveloperId: muhammedfarhant6@gmail.com */}
            </Typography>
          </Grid>

          {/* Column 2: Social Media - "item" prop removed */}
          <Grid
            xs={12}
            sm="auto"
            sx={{
              display: "flex",
              flexDirection: "column",
              alignItems: { xs: "flex-start", sm: "flex-end" },
            }}
          >
            <Box>
              <IconButton
                href="https://www.instagram.com/ssfpondicherryuniversity?utm_source=ig_web_button_share_sheet&igsh=MXZ3dHBpZjI3NHZnZQ=="
                target="_blank"
                sx={{ color: "white" }}
              >
                <InstagramIcon />
              </IconButton>
              <IconButton
                href="https://www.facebook.com/SSFPondicherryUniversity"
                target="_blank"
                sx={{ color: "white" }}
              >
                <FacebookIcon />
              </IconButton>
              {/* <IconButton href="https://www.youtube.com" target="_blank" sx={{ color: 'white' }}>
                <YouTubeIcon />
              </IconButton> */}
              {/* <IconButton href="https://www.twitter.com" target="_blank" sx={{ color: 'white' }}>
                <XIcon />
              </IconButton> */}
              <IconButton
                href="https://chat.whatsapp.com/JX3jdMNIOJaLUnwVSAXvH8?mode=ems_copy_t"
                target="_blank"
                sx={{ color: "white" }}
              >
                <WhatsAppIcon />
              </IconButton>
            </Box>
            <Typography
              variant="body2"
              sx={{ color: "#bdbdbd", mt: 0, pl: { xs: 1, md: 1 } }}
            >
              © 2025 SSF PU
            </Typography>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
}

export default Footer;
