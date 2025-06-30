import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Box, Backdrop, Typography, Button } from "@mui/material";
import Lottie from "lottie-react";
import loaderAnim from "../assets/animations/trailIQ_loader.json";

export default function Dashboard() {
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const goHome = () => {
    setLoading(true);
    setTimeout(() => navigate("/"), 500);   // show the loader a bit longer
  };

  return (
    <Box sx={{ width: "100%", height: "100vh", position: "relative", background: "linear-gradient(180deg, #E0F7FA 0%, #FFFFFF 100%)" }}>
        {/* Home button */}
        <Button variant="outlined" onClick={goHome} sx={{ position:"absolute", top:16, left:16, zIndex:2 }}>🏠 Home</Button> 
        {/* Loader backdrop */}
        <Backdrop
            open={loading}
            sx={{
            color: "#fff",
            zIndex: (theme) => theme.zIndex.drawer + 1,
            flexDirection: "column",
            backgroundColor: "rgba(30,30,30,0.8)",
            }}>
            <Lottie animationData={loaderAnim} loop style={{ width: 200, marginBottom: 16 }} />
            <Typography variant="h6">Loading TrailIQ-IN…</Typography>
        </Backdrop>

      {/* Dash app iframe */}
      <iframe
        title="TrailIQ Dashboard"
        src="http://localhost:8050"
        width="100%"
        height="100%"
        style={{ border: "none" }}
        onLoad={() => setLoading(false)}
      />
    </Box>
  );
}