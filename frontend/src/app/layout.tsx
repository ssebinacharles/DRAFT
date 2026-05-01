import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

// 1. IMPORT YOUR AUTH PROVIDER HERE:
import { AuthProvider } from "@/context/AuthContext"; 

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "ILES Dashboard",
  description: "Internship Learning Evaluation System",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>
        
        {/* 2. WRAP YOUR CHILDREN IN THE AUTH PROVIDER */}
        <AuthProvider>
          {children}
        </AuthProvider>
        
      </body>
    </html>
  );
}