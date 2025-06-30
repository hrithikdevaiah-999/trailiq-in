import React from 'react';
import Lottie from 'lottie-react';
import loaderData from '../assets/animations/trailIQ_loader.json';

export default function Loader() {
  return (
    <div style={{ width: 300, height: 300 }}>
      <Lottie
        animationData={loaderData}
        loop
        autoplay
      />
    </div>
  );
}