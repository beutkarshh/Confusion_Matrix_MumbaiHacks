import MainNavbar from "@/components/MainNavbar";

const Prescriptions = () => (
  <div className="min-h-screen bg-muted/20">
    <MainNavbar />
    <div className="container py-8">
      <h1 className="text-2xl font-bold mb-2">My Prescriptions</h1>
      <p className="text-muted-foreground">
        Placeholder page for viewing and managing prescriptions.
      </p>
    </div>
  </div>
);

export default Prescriptions;
