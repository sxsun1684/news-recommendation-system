// import AuthContext from "../context/AuthContext";
//
// const HomePage = () => {
//     return (
//         <div className=" flex-col items-center justify-center min-h-screen pt-[40px] text-center">
//             <h1 className="text-3xl font-bold">Welcome to the News Recommendation System</h1>
//             <p className="mt-4 text-gray-600">
//                 Stay informed with personalized news tailored to your interests.
//             </p>
//         </div>
//     );
// };
//
// export default HomePage;
import { useState, useContext } from "react";
import { AuthContext } from "../context/AuthContext";

const HomePage = () => {
    const auth = useContext(AuthContext);
    const [formData, setFormData] = useState({ email: "", password: "" });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    // 确保 `auth` 可用
    if (!auth) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <p className="text-gray-600">Loading...</p>
            </div>
        );
    }

    const { user, register, login, logout } = auth;

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    // ✅ 处理注册
    const handleRegister = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError("");

        if (!formData.email || !formData.password) {
            setError("Email and password cannot be empty.");
            setLoading(false);
            return;
        }

        try {
            await register(formData.email, formData.password);
        } catch (err) {
            setError("Registration failed. Please try again.");
            console.error(err);
        }

        setLoading(false);
    };

    // ✅ 处理登录
    const handleLogin = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError("");

        if (!formData.email || !formData.password) {
            setError("Email and password cannot be empty.");
            setLoading(false);
            return;
        }

        try {
            await login(formData.email, formData.password);
        } catch (err) {
            setError("Login failed. Please check your credentials.");
            console.error(err);
        }

        setLoading(false);
    };

    return (
        <div className="mt-20 flex-col items-center justify-center min-h-screen text-center bg-gray-100">
            {user ? (
                <div className="bg-white p-10 rounded-lg shadow-lg text-center">
                    <h2 className="text-2xl font-bold mb-4">Welcome, {user.email}!</h2>
                    <p className="text-gray-600">You are successfully logged in.</p>
                    <button
                        className="mt-4 px-4 py-2 bg-red-500 text-white rounded-md hover:bg-red-600"
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
                            onChange={handleChange}
                            required
                            className="w-full px-3 py-2 border rounded-md focus:ring focus:ring-blue-300"
                        />
                        <input
                            type="password"
                            name="password"
                            placeholder="Enter your password"
                            onChange={handleChange}
                            required
                            className="w-full px-3 py-2 border rounded-md focus:ring focus:ring-blue-300"
                        />

                        {/* ✅ 分开注册和登录 */}
                        <button
                            onClick={handleRegister}
                            className={`w-full px-3 py-2 text-white rounded-md ${
                                loading ? "bg-gray-400 cursor-not-allowed" : "bg-green-500 hover:bg-green-600"
                            }`}
                            disabled={loading}
                        >
                            {loading ? "Processing..." : "Register"}
                        </button>

                        <button
                            onClick={handleLogin}
                            className={`w-full px-3 py-2 text-white rounded-md ${
                                loading ? "bg-gray-400 cursor-not-allowed" : "bg-blue-500 hover:bg-blue-600"
                            }`}
                            disabled={loading}
                        >
                            {loading ? "Processing..." : "Login"}
                        </button>
                    </form>

                    {/* ✅ 底部新闻推荐部分 */}
                    <div className="mt-10 flex flex-col items-center justify-center text-center bg-gray-100 shadow-lg rounded-lg p-6">
                        <h1 className="text-3xl font-bold">Welcome to the News Recommendation System</h1>
                        <p className="mt-4 text-gray-600">
                            Stay informed with personalized news tailored to your interests.
                        </p>
                    </div>
                </div>
            )}
        </div>
    );
};

export default HomePage;
