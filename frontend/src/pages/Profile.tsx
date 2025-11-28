import MainNavbar from "@/components/MainNavbar";
import { useAppStore } from "@/store/useAppStore";
import { useState } from "react";

const Profile = () => {
  const { user } = useAppStore();
  const [isEditing, setIsEditing] = useState(false);
  const [message, setMessage] = useState("");
  const [formData, setFormData] = useState({
    fullName: user?.name || "",
    email: user?.email || "",
    phone: "",
    dateOfBirth: "",
    emergencyContact: "",
    bloodType: "",
    allergies: "",
    medications: "",
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setMessage("Profile updated locally for demo. Connect to backend to persist.");
    setIsEditing(false);
  };

  return (
    <div className="min-h-screen bg-muted/20">
      <MainNavbar />
      <div className="max-w-4xl mx-auto py-8 px-4 space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Profile</h1>
          <p className="text-gray-600">
            Manage your personal information and healthcare preferences.
          </p>
        </div>

        <div className="bg-white rounded-xl shadow-card p-6 space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold text-gray-900">Personal Information</h2>
            <button
              type="button"
              onClick={() => {
                setIsEditing((v) => !v);
                setMessage("");
              }}
              className="px-4 py-2 rounded-lg border border-gray-300 text-sm font-medium hover:bg-gray-50"
            >
              {isEditing ? "Cancel" : "Edit Profile"}
            </button>
          </div>

          {message && (
            <div className="mb-4 p-3 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-700 text-sm">
              {message}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="fullName">
                  Full Name
                </label>
                <input
                  id="fullName"
                  name="fullName"
                  type="text"
                  value={formData.fullName}
                  onChange={handleChange}
                  disabled={!isEditing}
                  className="w-full px-3 py-2 rounded-lg border border-gray-300 text-sm disabled:bg-gray-50"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="email">
                  Email Address
                </label>
                <input
                  id="email"
                  name="email"
                  type="email"
                  value={formData.email}
                  disabled
                  className="w-full px-3 py-2 rounded-lg border border-gray-300 text-sm bg-gray-50 cursor-not-allowed"
                />
                <p className="text-xs text-gray-500 mt-1">Email comes from Supabase and cannot be changed here.</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="phone">
                  Phone Number
                </label>
                <input
                  id="phone"
                  name="phone"
                  type="tel"
                  value={formData.phone}
                  onChange={handleChange}
                  disabled={!isEditing}
                  className="w-full px-3 py-2 rounded-lg border border-gray-300 text-sm disabled:bg-gray-50"
                  placeholder="Enter your phone number"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="dateOfBirth">
                  Date of Birth
                </label>
                <input
                  id="dateOfBirth"
                  name="dateOfBirth"
                  type="date"
                  value={formData.dateOfBirth}
                  onChange={handleChange}
                  disabled={!isEditing}
                  className="w-full px-3 py-2 rounded-lg border border-gray-300 text-sm disabled:bg-gray-50"
                />
              </div>
            </div>

            <div className="border-t border-gray-200 pt-6 space-y-4">
              <h3 className="text-lg font-semibold text-gray-900">Healthcare Information</h3>
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="bloodType">
                    Blood Type
                  </label>
                  <select
                    id="bloodType"
                    name="bloodType"
                    value={formData.bloodType}
                    onChange={handleChange}
                    disabled={!isEditing}
                    className="w-full px-3 py-2 rounded-lg border border-gray-300 text-sm disabled:bg-gray-50"
                  >
                    <option value="">Select blood type</option>
                    <option value="A+">A+</option>
                    <option value="A-">A-</option>
                    <option value="B+">B+</option>
                    <option value="B-">B-</option>
                    <option value="AB+">AB+</option>
                    <option value="AB-">AB-</option>
                    <option value="O+">O+</option>
                    <option value="O-">O-</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="emergencyContact">
                    Emergency Contact
                  </label>
                  <input
                    id="emergencyContact"
                    name="emergencyContact"
                    type="text"
                    value={formData.emergencyContact}
                    onChange={handleChange}
                    disabled={!isEditing}
                    className="w-full px-3 py-2 rounded-lg border border-gray-300 text-sm disabled:bg-gray-50"
                    placeholder="Name and phone number"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="allergies">
                  Allergies
                </label>
                <textarea
                  id="allergies"
                  name="allergies"
                  rows={3}
                  value={formData.allergies}
                  onChange={handleChange}
                  disabled={!isEditing}
                  className="w-full px-3 py-2 rounded-lg border border-gray-300 text-sm disabled:bg-gray-50"
                  placeholder="List any known allergies or 'None'"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="medications">
                  Current Medications
                </label>
                <textarea
                  id="medications"
                  name="medications"
                  rows={3}
                  value={formData.medications}
                  onChange={handleChange}
                  disabled={!isEditing}
                  className="w-full px-3 py-2 rounded-lg border border-gray-300 text-sm disabled:bg-gray-50"
                  placeholder="List current medications or 'None'"
                />
              </div>
            </div>

            {isEditing && (
              <div className="flex justify-end space-x-4 pt-6 border-t border-gray-200">
                <button
                  type="button"
                  onClick={() => {
                    setIsEditing(false);
                    setMessage("");
                  }}
                  className="px-4 py-2 rounded-lg border border-gray-300 text-sm font-medium hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-lg bg-emerald-600 text-white text-sm font-medium hover:bg-emerald-700"
                >
                  Save Changes
                </button>
              </div>
            )}
          </form>
        </div>
      </div>
    </div>
  );
};

export default Profile;
