import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Super Brain Contacts - Network Intelligence Dashboard",
  description: "Interactive dashboard for contact network analysis, influencer identification, and community detection",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
