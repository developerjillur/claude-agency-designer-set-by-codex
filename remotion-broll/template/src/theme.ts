import { loadFont } from "@remotion/google-fonts/Poppins";

export const { fontFamily: POPPINS } = loadFont("normal", {
  weights: ["500", "600", "700", "800"],
  subsets: ["latin"],
});

// Dark-brown outline shared by the drawn characters, close to the AI illustration's line colour.
export const INK = "#2B1D16";

export const COLORS = {
  cream: "#FFF4E4",
  orange: "#FF7A2F",
  orangeDeep: "#E85D1C",
  yellow: "#FFC43D",
} as const;

export const clamp = {
  extrapolateLeft: "clamp",
  extrapolateRight: "clamp",
} as const;
