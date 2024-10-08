import IoTDashboard from "@/components/iot-dashboard";

export default function DashboardPage() {
  // get project id from cookie

  return (
    <main>
      <IoTDashboard projectId={"geo-project"} />
    </main>
  );
}
