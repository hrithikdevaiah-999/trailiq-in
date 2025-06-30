import { Box } from "@mui/material";
import Lottie   from "lottie-react";
import bgAnim   from "../assets/animations/LottieBackground.json";

export default function AnimatedBackground() {
  return (
    <Box
      sx={{
        position: "fixed",
        inset:    0,              // full-viewport
        zIndex:  0,
        pointerEvents: "none",    // let clicks through
        overflow: "hidden"             // tune to taste
      }}
    >
    <Lottie
        animationData={bgAnim}
        loop
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          width: "100vw",
          height: "100vh",
        }}
        rendererSettings={{ preserveAspectRatio: "xMidYMid slice" }}
      />
    </Box>
  );
}