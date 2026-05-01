import type { Metadata } from "next";
import { Inter } from "next/font/google"; // Using Inter for a more professional university feel
import "./globals.css";

// We use Inter as the primary font for high-end enterprise apps
const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "ILES1 | Internship Management Portal",
  description: "Internship Learning Evaluation System for professional student monitoring.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="h-full">
      <body 
        className={`${inter.className} h-full bg-[#0a0f1d] antialiased selection:bg-indigo-500/30`}
      >
        {/* The bg-[#0a0f1d] here ensures that your 
            glassy layers always have a dark background to 'frost' over.
        */}
        {children}
      </body>
    </html>
  );
}