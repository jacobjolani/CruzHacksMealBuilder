import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Meal Planner — UC Berkeley",
  description: "Set macro targets and get 3 daily meals from Berkeley dining menu.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="min-h-screen">{children}</body>
    </html>
  );
}
