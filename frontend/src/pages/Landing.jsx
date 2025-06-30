import { Button, Container, Typography, Box, Grid, Paper } from "@mui/material";
import { Link } from "react-router-dom";
import Lottie from "lottie-react";
import heroAnim from "../assets/animations/trailIQ_hero_map.json";
import mapPrev     from "../assets/preview_map.png";
import distPrev    from "../assets/preview_scatter.png";
import heatPrev    from "../assets/preview_heat.png";
import crowdPrev   from "../assets/preview_crowd.png";
import AnimatedBackground from "../components/AnimatedBackground";

function StoryCard({ img, title, text }) {
  return (
    <Paper elevation={3} sx={{ width: 265, p: 1.5, borderRadius: 2, backgroundColor: "#f8f8f8" }}>
      <img src={img} alt={title} width="100%" style={{ borderRadius: 6 }} />
      <Typography variant="h6" mt={1}>{title}</Typography>
      <Typography variant="body2">{text}</Typography>
    </Paper>
  );
}

export default function Landing() {
  return (
    <Box sx={{ minHeight: "100vh", position: "relative", overflowX:"hidden"}}>
      <AnimatedBackground/>
      <Container maxWidth="md" sx={{ textAlign:"center", py: 6, position: "relative", zIndex: 1, }}>
        {/* top hero --------------------------------------------------- */}
        <Lottie animationData={heroAnim} loop
                style={{ height: 320, margin:"0 auto" }} />

        <Typography variant="h3" sx={{ color:"#29475b", fontWeight:600, mt:1 }}>
          TrailIQ-IN
        </Typography>
        <Typography variant="h5" gutterBottom>
          Where data meets the Himalaya ⛰️
        </Typography>

        <Typography variant="body1" paragraph sx={{ maxWidth:650, mx:"auto" }}>
          We fused <strong>311 curated treks</strong>, <strong>NASA POWER</strong>
          climate normals, <strong>IMD rainfall</strong>&nbsp;and 2018 tourism
          statistics to build four interactive views that help you pick the
          right trail for <em>your</em> season, fitness and crowd tolerance.
        </Typography>

        {/* four-visual grid ------------------------------------------ */}
        <Grid container spacing={3} justifyContent="center" sx={{ my: 4 }}>
          <Grid item><StoryCard
            img={mapPrev}
            title="Heat-index Map"
            text="See every trek on an India map coloured by annual mean temp."/>
          </Grid>
          <Grid item><StoryCard
            img={distPrev}
            title="Distance × Rating"
            text="Scatter reveals hidden gems: short yet top-rated hikes."/>
          </Grid>
          <Grid item><StoryCard
            img={heatPrev}
            title="Temperature Spread"
            text="Histogram shows how alpine routes differ from coastal ones."/>
          </Grid>
          <Grid item><StoryCard
            img={crowdPrev}
            title="Crowd-Score Leaderboard"
            text="Tourism data highlights off-beat states to avoid queues."/>
          </Grid>
        </Grid>

        <Button component={Link} to="/dashboard"
                variant="contained" size="large"
                sx={{
                  bgcolor:"#2E3B4E",
                  "&:hover": { bgcolor:"#42566c" },
                  "&:focus": {
                    outline:"3px dashed #ffc400", outlineOffset:4 }
                }}>
          Launch the dashboard
        </Button>
      </Container>
    </Box>
  );
}

