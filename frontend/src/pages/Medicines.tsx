import MainNavbar from "@/components/MainNavbar";
import { useAppStore } from "@/store/useAppStore";

const Medicines = () => {
  const user = useAppStore((state) => state.user);
  const isPharmacist = user?.role === "Pharmacist";
  const medicines = [
    { id: 1, name: "Paracetamol 500mg", quantity: 120, price: 1.5, expiry: "2026-01-15" },
    { id: 2, name: "Amoxicillin 250mg", quantity: 20, price: 5.2, expiry: "2024-12-01" },
    { id: 3, name: "ORS Solution", quantity: 0, price: 0.8, expiry: null },
    { id: 4, name: "Ibuprofen 400mg", quantity: 18, price: 2.3, expiry: "2025-05-10" },
  ];

  const getAvailabilityStatus = (medicine: (typeof medicines)[number]) => {
    const isExpired = medicine.expiry && new Date(medicine.expiry) < new Date();
    if (isExpired) return { text: "Expired", className: "bg-red-100 text-red-800" };
    if (!medicine.quantity || medicine.quantity === 0)
      return { text: "Out of Stock", className: "bg-red-100 text-red-800" };
    if (medicine.quantity <= 30)
      return { text: "Low Stock", className: "bg-yellow-100 text-yellow-800" };
    return { text: "Available", className: "bg-green-100 text-green-800" };
  };

  return (
    <div className="min-h-screen bg-muted/20">
      <MainNavbar />
      <div className="max-w-3xl mx-auto p-4">
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Medicines</h1>
          <div className="flex items-center justify-between mb-4 gap-4 flex-wrap">
            <p className="text-sm text-gray-600">
              Sample medicine availability table inspired by your previous project.
            </p>
            {isPharmacist && (
              <button
                type="button"
                className="px-3 py-1.5 text-xs font-medium rounded-md bg-blue-600 text-white hover:bg-blue-700"
              >
                + Add / Update Medicines (Pharmacist)
              </button>
            )}
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Name
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Quantity
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Price (₹)
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Expiry
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Availability
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {medicines.map((m) => {
                  const availability = getAvailabilityStatus(m);
                  return (
                    <tr key={m.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {m.name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {m.quantity}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        ₹{m.price.toFixed(2)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {m.expiry ? new Date(m.expiry).toLocaleDateString() : "N/A"}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${availability.className}`}>
                          {availability.text}
                        </span>
                      </td>
                      {isPharmacist && (
                        <td className="px-6 py-4 whitespace-nowrap text-right text-xs text-blue-600 cursor-pointer">
                          Edit
                        </td>
                      )}
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Medicines;
