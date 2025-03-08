import {useState, useContext} from "react";
import {AuthContext} from "../context/AuthContext";

const HomePage = () => {
    const auth = useContext(AuthContext);
    const [formData, setFormData] = useState({email: "", password: ""});
    const [loadingRegister, setLoadingRegister] = useState(false);
    const [loadingLogin, setLoadingLogin] = useState(false);
    const [error, setError] = useState("");

    // Display loading state if authentication context is not ready
    if (!auth) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <p className="text-gray-600">Loading...</p>
            </div>
        );
    }

    const {user, register, login, logout} = auth;

    const handleChange = (e) => {
        setFormData((prev) => ({...prev, [e.target.name]: e.target.value}));
    };

    // Handle user registration
    const handleRegister = async (e) => {
        e.preventDefault();
        setLoadingRegister(true);
        setError("");

        if (!formData.email || !formData.password) {
            setError("Email and password cannot be empty.");
            setLoadingRegister(false);
            return;
        }

        try {
            await register(formData.email, formData.password);
        } catch (err) {
            setError("Registration failed. Please try again.");
            console.error(err);
        }

        setLoadingRegister(false);
    };

    // Handle user login
    const handleLogin = async (e) => {
        e.preventDefault();
        setLoadingLogin(true);
        setError("");

        if (!formData.email || !formData.password) {
            setError("Email and password cannot be empty.");
            setLoadingLogin(false);
            return;
        }

        try {
            await login(formData.email, formData.password);
        } catch (err) {
            setError("Login failed. Please check your credentials.");
            console.error(err);
        }

        setLoadingLogin(false);
    };

    return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50 text-center px-4">

            {/* ✅ Display user info if logged in */}
            {user ? (
                <div className="bg-white p-10 rounded-lg shadow-lg text-center w-full max-w-md">
                    <h2 className="text-2xl font-bold mb-4">Welcome, {user.email}!</h2>
                    <p className="text-gray-600">You are successfully logged in.</p>
                    <button
                        className="mt-4 px-4 py-2 bg-red-500 text-white rounded-md hover:bg-red-600 w-full"
                        onClick={logout}
                    >
                        Logout
                    </button>
                </div>
            ) : (
                <div className="w-full max-w-md bg-white p-8 rounded-lg shadow-lg">
                    <h2 className="text-2xl font-bold text-center mb-4">User Authentication</h2>
                    {error && <p className="text-red-500 text-sm text-center mb-4">{error}</p>}

                    <form className="space-y-4">
                        <input
                            type="email"
                            name="email"
                            placeholder="Enter your email"
                            value={formData.email}
                            onChange={handleChange}
                            required
                            className="w-full px-3 py-2 border rounded-md focus:ring focus:ring-blue-300"
                        />
                        <input
                            type="password"
                            name="password"
                            placeholder="Enter your password"
                            value={formData.password}
                            onChange={handleChange}
                            required
                            className="w-full px-3 py-2 border rounded-md focus:ring focus:ring-blue-300"
                        />

                        {/* ✅ Separate Register Button */}
                        <button
                            onClick={handleRegister}
                            className={`w-full px-3 py-2 text-white rounded-md ${
                                loadingRegister ? "bg-gray-400 cursor-not-allowed" : "bg-green-500 hover:bg-green-600"
                            }`}
                            disabled={loadingRegister}
                        >
                            {loadingRegister ? "Processing..." : "Register"}
                        </button>

                        {/* ✅ Separate Login Button */}
                        <button
                            onClick={handleLogin}
                            className={`w-full px-3 py-2 text-white rounded-md ${
                                loadingLogin ? "bg-gray-400 cursor-not-allowed" : "bg-blue-500 hover:bg-blue-600"
                            }`}
                            disabled={loadingLogin}
                        >
                            {loadingLogin ? "Processing..." : "Login"}
                        </button>
                    </form>
                </div>
            )}

            {/* ✅ News Recommendation System Description */}
            <div className="mt-10 flex flex-col items-center justify-center text-center
                bg-gradient-to-r from-yellow-200 via-yellow-100 to-yellow-50
                shadow-xl hover:shadow-2xl transition-shadow duration-500
                rounded-3xl p-6 w-full max-w-md hover:ring-4 hover:ring-yellow-300 animate-fadeIn">

                <h1 className="text-3xl font-bold text-gray-900 hover:text-yellow-600 transition-colors duration-300">
                    Welcome to the News Recommendation System
                </h1>

                <p className="mt-4 text-gray-700">
                    Stay informed with personalized news tailored to your interests.
                </p>

                <p className="mt-2 text-gray-600 italic">
                    * This project is a high-concurrency, distributed news recommendation system that integrates
                    <span className="font-bold text-gray-800"> DynamoDB, Kafka, Redis, Spark,</span> and
                    <span className="font-bold text-gray-800"> LLM (Large Language Models)</span>
                    for personalized user recommendations.
                </p>

                <p className="text-yellow-700 font-semibold mt-2">- S.X.SUN</p>
            </div>

        </div>
    );
};

export default HomePage;
