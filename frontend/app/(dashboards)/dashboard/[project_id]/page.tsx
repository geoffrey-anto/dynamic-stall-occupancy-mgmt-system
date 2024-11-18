import IoTDashboard from "@/components/iot-dashboard";

export default function DashboardPage({
  params,
}: {
  params: {
    project_id: string;
  };
}) {
  return (
    <main>
      <IoTDashboard projectId={params.project_id} />
    </main>
  );
}
