"use client";

import { useEffect, useState } from "react";
import {
  Search,
  ChevronLeft,
  ChevronRight,
  Tag,
  User,
  Check,
  X,
} from "lucide-react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";

interface Device {
  id: string;
  project: string;
  occupancy: string;
  name?: string;
  tag?: string;
}

export default function IoTDashboard({ projectId }: { projectId: string }) {
  const [devices, setDevices] = useState<Device[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [showOccupiedOnly, setShowOccupiedOnly] = useState(false);
  const [nameFilter, setNameFilter] = useState("");
  const [tagFilter, setTagFilter] = useState("");
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editName, setEditName] = useState("");
  const [editTag, setEditTag] = useState("");
  const itemsPerPage = 5;

  const filteredDevices = devices.filter(
    (device) =>
      device.id.toLowerCase().includes(searchTerm.toLowerCase()) &&
      (!showOccupiedOnly || device.occupancy) &&
      (nameFilter === "" ||
        (device.name &&
          device.name.toLowerCase().includes(nameFilter.toLowerCase()))) &&
      (tagFilter === "" ||
        (device.tag &&
          device.tag.toLowerCase().includes(tagFilter.toLowerCase())))
  );

  const totalPages = Math.ceil(filteredDevices.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const currentDevices = filteredDevices.slice(startIndex, endIndex);

  const handleEdit = (device: Device) => {
    setEditingId(device.id);
    setEditName(device.name || "");
    setEditTag(device.tag || "");
  };

  const handleSave = () => {
    setDevices(
      devices.map((device) =>
        device.id === editingId
          ? {
              ...device,
              name: editName || undefined,
              tag: editTag || undefined,
            }
          : device
      )
    );
    setEditingId(null);
  };

  const handleCancel = () => {
    setEditingId(null);
  };

  useEffect(() => {
    async function fetchDevices() {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_SERVER_URL}/v1/occupancies?project=${projectId}`
      );

      if (!response.ok) {
        console.error("Failed to fetch devices");
        return;
      }

      const data = await response.json();

      setDevices(data);
    }
    const it = setInterval(() => {
      fetchDevices();
    }, 1000);

    return () => clearInterval(it);
  }, []);

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">IoT Devices Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
        <div className="relative">
          <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search devices..."
            className="pl-8"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        <div className="relative">
          <User className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Filter by name..."
            className="pl-8"
            value={nameFilter}
            onChange={(e) => setNameFilter(e.target.value)}
          />
        </div>
        <div className="relative">
          <Tag className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Filter by tag..."
            className="pl-8"
            value={tagFilter}
            onChange={(e) => setTagFilter(e.target.value)}
          />
        </div>
        <div className="flex items-center space-x-2">
          <Switch
            id="occupied-filter"
            checked={showOccupiedOnly}
            onCheckedChange={setShowOccupiedOnly}
          />
          <Label htmlFor="occupied-filter">Show occupied only</Label>
        </div>
      </div>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Device ID</TableHead>
            <TableHead>Project ID</TableHead>
            <TableHead>Name</TableHead>
            <TableHead>Tag</TableHead>
            <TableHead>Occupancy</TableHead>
            <TableHead>Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {currentDevices.map((device) => (
            <TableRow key={device.id}>
              <TableCell>{device.id}</TableCell>
              <TableCell>{device.project}</TableCell>
              <TableCell>
                {editingId === device.id ? (
                  <Input
                    value={editName}
                    onChange={(e) => setEditName(e.target.value)}
                    className="w-full"
                  />
                ) : (
                  device.name || "-"
                )}
              </TableCell>
              <TableCell>
                {editingId === device.id ? (
                  <Input
                    value={editTag}
                    onChange={(e) => setEditTag(e.target.value)}
                    className="w-full"
                  />
                ) : (
                  device.tag || "-"
                )}
              </TableCell>
              <TableCell>
                <span
                  className={`px-2 py-1 rounded-full text-xs font-semibold ${
                    device.occupancy === "false"
                      ? "bg-green-100 text-green-800"
                      : "bg-red-100 text-red-800"
                  }`}
                >
                  {device.occupancy === "true" ? "Occupied" : "Vacant"}
                </span>
              </TableCell>
              <TableCell>
                {editingId === device.id ? (
                  <div className="flex space-x-2">
                    <Button size="sm" onClick={handleSave}>
                      <Check className="h-4 w-4" />
                    </Button>
                    <Button size="sm" variant="outline" onClick={handleCancel}>
                      <X className="h-4 w-4" />
                    </Button>
                  </div>
                ) : (
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleEdit(device)}
                  >
                    Edit
                  </Button>
                )}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
      <div className="flex justify-between items-center mt-4">
        <div>
          Showing {startIndex + 1} to{" "}
          {Math.min(endIndex, filteredDevices.length)} of{" "}
          {filteredDevices.length} devices
        </div>
        <div className="flex space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setCurrentPage((prev) => Math.max(prev - 1, 1))}
            disabled={currentPage === 1}
          >
            <ChevronLeft className="h-4 w-4" />
            Previous
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() =>
              setCurrentPage((prev) => Math.min(prev + 1, totalPages))
            }
            disabled={currentPage === totalPages}
          >
            Next
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}
