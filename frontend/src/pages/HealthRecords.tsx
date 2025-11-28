import MainNavbar from "@/components/MainNavbar";

const HealthRecords = () => (
  <div className="min-h-screen bg-muted/20">
    <MainNavbar />
    <div className="container py-8">
      <h1 className="text-2xl font-bold mb-2">Health Records</h1>
      <p className="text-muted-foreground">
        Placeholder page for managing patient health records.
      </p>
    </div>
  </div>
);

export default HealthRecords;
