import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Hadence — Your career, backed by evidence",
  description:
    "Hadence is an Application Intelligence Workspace: a Career Evidence Graph that maps job requirements to verifiable evidence.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-paper text-ink antialiased">{children}</body>
    </html>
  );
}
