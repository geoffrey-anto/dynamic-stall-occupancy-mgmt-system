"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Download } from "lucide-react";

export default function Gen() {
  const [file, setFile] = useState<File | null>();

  const handleDownload = () => {
    alert("Floor plan generation and download would happen here!");
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="relative w-full max-w-2xl">
        {/* Decorative element */}
        <div className="absolute top-0 left-0 w-72 h-72 bg-blue-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob"></div>
        <div className="absolute top-0 right-0 w-72 h-72 bg-purple-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-2000"></div>
        <div className="absolute bottom-0 left-0 w-72 h-72 bg-pink-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-4000"></div>

        {/* Content */}
        <div className="relative bg-gray-800 p-8 rounded-2xl shadow-2xl border border-gray-700">
          <h1 className="text-4xl font-bold mb-8 text-center bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-500">
            AI Dynamic Occupancy System
          </h1>
          <div className="space-y-6">
            <div>
              <label
                htmlFor="floorPlan"
                className="block text-lg font-medium text-gray-300 mb-2"
              >
                Upload your floor plan
              </label>
              <div className="relative">
                <Input
                  type="file"
                  id="floorPlan"
                  placeholder="e.g., Modern 3-bedroom house with open kitchen and large windows..."
                  onChange={(e) => setFile(e.target.files?.item(0))}
                />
                <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-purple-500 rounded-xl opacity-20 filter blur-xl pointer-events-none"></div>
              </div>
            </div>
            <Button
              onClick={handleDownload}
              className="w-full text-lg py-6 rounded-xl bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 transition-all duration-200 ease-in-out transform hover:scale-105"
              disabled={!file}
            >
              <Download className="mr-2 h-6 w-6" /> Submit & Generate Dashboard
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
