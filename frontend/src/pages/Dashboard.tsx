import { Card, CardContent } from "@/components/ui/card";
import { useAppStore } from "@/store/useAppStore";
import PatientCaseForm from "@/components/PatientCaseForm";
import AIAgentsPanel from "@/components/AIAgentsPanel";
import WorkflowPanel from "@/components/WorkflowPanel";
import ResultsPanel from "@/components/ResultsPanel";
import MainNavbar from "@/components/MainNavbar";

const Dashboard = () => {
  const { stats } = useAppStore();

  const statCards = [
    {
      title: "Active Agents",
      value: stats.activeAgents
    },
    {
      title: "Completed",
      value: stats.completedCases
    },
    {
      title: "Cases Analyzed",
      value: stats.casesAnalyzed.toLocaleString()
    },
    {
      title: "Progress",
      value: `${stats.progress}%`
    }
  ];

  return (
    <div className="min-h-screen bg-muted/20">
      <MainNavbar />

      <div className="container py-8 space-y-8">
        <div className="bg-gradient-card rounded-lg p-6 shadow-card">
          <h1 className="text-3xl font-bold text-foreground mb-2">
            Better Healthcare Access for Rural Areas
          </h1>
          <p className="text-muted-foreground">
            Use AI-powered multi-agent diagnostics to bridge healthcare gaps.
          </p>
        </div>

        {/* Stats Bar */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {statCards.map((stat, index) => (
            <Card key={index} className="shadow-card">
              <CardContent className="p-6">
                <p className="text-sm font-medium text-muted-foreground">
                  {stat.title}
                </p>
                <p className="text-2xl font-bold text-foreground">
                  {stat.value}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Left Column - Patient Input */}
          <div className="lg:col-span-1 space-y-6">
            <PatientCaseForm />
            <AIAgentsPanel />
          </div>

          {/* Right Column - Workflow and Results */}
          <div className="lg:col-span-2 space-y-6">
            <WorkflowPanel />
            <ResultsPanel />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;