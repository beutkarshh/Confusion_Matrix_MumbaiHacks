import MainNavbar from "@/components/MainNavbar";
import { useAppStore } from "@/store/useAppStore";

const schemes = [
  {
    name: "Ayushman Bharat - Pradhan Mantri Jan Arogya Yojana (PMJAY)",
    description:
      "Health insurance scheme providing cashless treatment up to ₹5 lakh per family per year at empanelled public and private hospitals.",
    target: "Poor and vulnerable families identified under SECC / PMJAY criteria.",
    link: "https://pmjay.gov.in/",
  },
  {
    name: "Ayushman Bharat - Health & Wellness Centres (HWCs)",
    description:
      "Upgradation of sub‑centres and primary health centres into Health & Wellness Centres offering comprehensive primary healthcare services.",
    target: "General population through public primary health facilities.",
    link: "https://ab-hwc.nhp.gov.in/",
  },
  {
    name: "Ayushman Bharat Digital Mission (ABDM)",
    description:
      "Creation of a digital health ecosystem including ABHA ID, digital health records, and interoperable health services.",
    target: "All citizens opting to create a digital ABHA health ID.",
    link: "https://abdm.gov.in/",
  },
  {
    name: "Janani Suraksha Yojana (JSY)",
    description:
      "Conditional cash transfer scheme to promote institutional deliveries and reduce maternal and neonatal mortality.",
    target:
      "Pregnant women, especially from BPL and vulnerable groups, with focus on rural and low‑performing states.",
    link:
      "https://nhm.gov.in/index1.php?lang=1&level=3&sublinkid=841&lid=309",
  },
  {
    name: "Pradhan Mantri Surakshit Matritva Abhiyan (PMSMA)",
    description:
      "Provision of free, fixed‑day comprehensive antenatal care services by specialists for pregnant women.",
    target: "Pregnant women in their second and third trimesters.",
    link: "https://pmsma.nhp.gov.in/",
  },
  {
    name: "Rashtriya Bal Swasthya Karyakram (RBSK)",
    description:
      "Child health screening and early intervention services for defects, deficiencies, diseases and development delays.",
    target: "Children from birth to 18 years through schools, anganwadis and communities.",
    link:
      "https://nhm.gov.in/index1.php?lang=1&level=3&sublinkid=1182&lid=364",
  },
];

const VaccinesSchemes = () => {
  const user = useAppStore((state) => state.user);
  const isAdmin = user?.role === "Admin";

  return (
    <div className="min-h-screen bg-muted/20">
      <MainNavbar />
      <div className="container py-8 space-y-6">
        <div className="flex items-start justify-between gap-4 flex-wrap">
          <div>
            <h1 className="text-2xl font-bold mb-2">Vaccines &amp; Schemes</h1>
            <p className="text-muted-foreground max-w-2xl">
              Key Indian government health schemes that support access to
              care, maternal and child health, and digital health services.
            </p>
          </div>
          {isAdmin && (
            <button
              type="button"
              className="px-3 py-1.5 text-xs font-medium rounded-md bg-primary text-primary-foreground hover:bg-primary/90"
            >
              + Add / Update Schemes (Admin)
            </button>
          )}
        </div>

        <div className="bg-card rounded-xl shadow-card border border-border p-6 space-y-4">
          <div className="flex items-center justify-between gap-4 flex-wrap">
            <div>
              <h2 className="font-semibold text-lg">Major National Health Schemes</h2>
              <p className="text-sm text-muted-foreground">
                Curated list of flagship programmes by the Government of India.
              </p>
            </div>
            <span className="text-[11px] rounded-full px-3 py-1 bg-primary/10 text-primary font-medium">
              Static reference (no live API)
            </span>
          </div>

          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {schemes.map((scheme) => (
              <div
                key={scheme.name}
                className="border border-border rounded-lg p-4 bg-muted/40 flex flex-col justify-between gap-3"
              >
                <div>
                  <h3 className="font-semibold mb-1 text-sm md:text-base">
                    {scheme.name}
                  </h3>
                  <p className="text-xs md:text-sm text-muted-foreground mb-2">
                    {scheme.description}
                  </p>
                  <p className="text-[11px] md:text-xs text-muted-foreground">
                    Target:&nbsp;
                    <span className="font-medium text-foreground">{scheme.target}</span>
                  </p>
                </div>
                <div className="flex items-center justify-between w-full mt-1">
                  <a
                    href={scheme.link}
                    target="_blank"
                    rel="noreferrer"
                    className="text-[11px] md:text-xs font-medium text-primary underline"
                  >
                    Learn more on official site
                  </a>
                  {isAdmin && (
                    <button
                      type="button"
                      className="text-[11px] md:text-xs font-medium text-blue-600 hover:text-blue-800"
                    >
                      Edit
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        <p className="text-xs text-muted-foreground max-w-2xl">
          This section is for quick reference only. For the most
          up-to-date eligibility rules and benefits, always refer to the
          official government websites linked above.
        </p>
      </div>
    </div>
  );
};

export default VaccinesSchemes;
