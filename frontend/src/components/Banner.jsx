import React from "react";

import banner from "../assets/banner.jpg";

export default function Banner() {
  return (
    <img
      src={banner}
      alt="Treks of India"
      style={{ width: "100%", borderRadius: 8 }}
    />
  );
}