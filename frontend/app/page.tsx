"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { ArrowRight, Cpu, Wifi, LayoutDashboard, Map, Zap } from "lucide-react";

export default function Home() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 to-gray-800 text-white">
      <nav className="container mx-auto px-6 py-4">
        <div className="flex justify-between items-center">
          <a href="#" className="text-2xl font-bold">
            Occupancy Management System
          </a>
          <div className="hidden md:flex space-x-6">
            <a href="#features" className="hover:text-blue-400 transition">
              Features
            </a>
            <a href="#how-it-works" className="hover:text-blue-400 transition">
              How It Works
            </a>
            <a href="#benefits" className="hover:text-blue-400 transition">
              Benefits
            </a>
          </div>
          <button className="bg-blue-500 hover:bg-blue-600 px-4 py-2 rounded-md transition">
            Get Started
          </button>
          <button
            className="md:hidden"
            onClick={() => setIsMenuOpen(!isMenuOpen)}
          >
            <svg
              className="w-6 h-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 6h16M4 12h16m-7 6h7"
              />
            </svg>
          </button>
        </div>
        {isMenuOpen && (
          <div className="mt-4 md:hidden">
            <a
              href="#features"
              className="block py-2 hover:text-blue-400 transition"
            >
              Features
            </a>
            <a
              href="#how-it-works"
              className="block py-2 hover:text-blue-400 transition"
            >
              How It Works
            </a>
            <a
              href="#benefits"
              className="block py-2 hover:text-blue-400 transition"
            >
              Benefits
            </a>
          </div>
        )}
      </nav>

      <header className="container mx-auto px-6 py-16 text-center">
        <motion.h1
          className="text-5xl md:text-6xl font-bold mb-4"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          Dynamic Occupancy Management
        </motion.h1>
        <motion.p
          className="text-xl md:text-2xl mb-8"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          AI-Powered. IoT-Enabled. Effortlessly Efficient.
        </motion.p>
        <motion.button
          className="bg-blue-500 hover:bg-blue-600 px-8 py-3 rounded-md text-lg transition"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
        >
          Discover More
        </motion.button>
      </header>

      <section id="features" className="container mx-auto px-6 py-16">
        <h2 className="text-3xl font-bold mb-8 text-center">Key Features</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {[
            {
              icon: <Cpu className="w-12 h-12 mb-4" />,
              title: "AI-Powered Analysis",
              description: "R-CNN model for accurate floor plan interpretation",
            },
            {
              icon: <Wifi className="w-12 h-12 mb-4" />,
              title: "Wireless Connectivity",
              description: "ESP32 & LoRa for seamless data transmission",
            },
            {
              icon: <LayoutDashboard className="w-12 h-12 mb-4" />,
              title: "Dynamic Dashboard",
              description: "Real-time occupancy monitoring and insights",
            },
          ].map((feature, index) => (
            <motion.div
              key={index}
              className="bg-gray-800 p-6 rounded-lg text-center"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
            >
              {feature.icon}
              <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
              <p>{feature.description}</p>
            </motion.div>
          ))}
        </div>
      </section>

      <section id="how-it-works" className="container mx-auto px-6 py-16">
        <h2 className="text-3xl font-bold mb-8 text-center">How It Works</h2>
        <div className="space-y-12">
          {[
            {
              step: 1,
              title: "Floor Plan Analysis",
              description:
                "Upload your floor plan and our AI model generates an intermediate sequence.",
            },
            {
              step: 2,
              title: "LLM Processing",
              description:
                "Our language model interprets the sequence to determine optimal device placement.",
            },
            {
              step: 3,
              title: "Device Setup",
              description:
                "Place the ESP32 devices within WiFi range. They'll auto-configure and register to the cloud.",
            },
            {
              step: 4,
              title: "Dashboard Creation",
              description:
                "A custom dashboard is generated based on the LLM output, ready for your use.",
            },
          ].map((step, index) => (
            <motion.div
              key={index}
              className="flex items-start"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
            >
              <div className="flex-shrink-0 bg-blue-500 rounded-full w-8 h-8 flex items-center justify-center mr-4">
                {step.step}
              </div>
              <div>
                <h3 className="text-xl font-semibold mb-2">{step.title}</h3>
                <p>{step.description}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </section>

      <section id="benefits" className="container mx-auto px-6 py-16">
        <h2 className="text-3xl font-bold mb-8 text-center">Benefits</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {[
            {
              icon: <Map className="w-8 h-8 mb-4" />,
              title: "Optimized Space Utilization",
              description: "Make informed decisions about your space usage",
            },
            {
              icon: <Zap className="w-8 h-8 mb-4" />,
              title: "Energy Efficiency",
              description: "Reduce energy consumption in unoccupied areas",
            },
            {
              icon: <ArrowRight className="w-8 h-8 mb-4" />,
              title: "Scalability",
              description: "Easily expand from small offices to large campuses",
            },
            {
              icon: <Cpu className="w-8 h-8 mb-4" />,
              title: "Data-Driven Insights",
              description: "Gain valuable occupancy trends and patterns",
            },
          ].map((benefit, index) => (
            <motion.div
              key={index}
              className="bg-gray-800 p-6 rounded-lg"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
            >
              {benefit.icon}
              <h3 className="text-xl font-semibold mb-2">{benefit.title}</h3>
              <p>{benefit.description}</p>
            </motion.div>
          ))}
        </div>
      </section>

      <section className="container mx-auto px-6 py-16 text-center">
        <h2 className="text-3xl font-bold mb-4">
          Ready to Optimize Your Space?
        </h2>
        <p className="text-xl mb-8">
          Get started with our Occupancy Management System today and transform
          your space utilization.
        </p>
        <button className="bg-blue-500 hover:bg-blue-600 px-8 py-3 rounded-md text-lg transition">
          Request a Demo
        </button>
      </section>

      <footer className="bg-gray-900 py-8">
        <div className="container mx-auto px-6 text-center">
          <p>&copy; 2023 Occupancy Management System. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}
