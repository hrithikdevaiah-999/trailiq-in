import React from 'react';
import Lottie from 'lottie-react';
import heroData from '../assets/animations/trailIQ_hero_map.json';

export default function Hero() {
  return (
    <div style={{ width: 1280, height: 950 }}>
      <Lottie
        animationData={heroData}
        loop
        autoplay
      />
    </div>
  );
}