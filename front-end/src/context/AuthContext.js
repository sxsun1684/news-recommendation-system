import { createContext, useState, useEffect } from "react";
import axios from "axios";

// Create authentication context
const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null); // State to store authenticated user
    const [news, setNews] = useState([]); // State to store news data

    useEffect(() => {
        // Check for stored token when the component mounts
        const token = localStorage.getItem("token");
        if (token) {
            axios.get("/api/auth/me", {
                headers: { Authorization: `Bearer ${token}` }
            })
            .then(res => {
                setUser(res.data); // Set authenticated user
                fetchNews(); // Fetch news for authenticated user
            })
            .catch(() => {
                localStorage.removeItem("token"); // Remove invalid token on error
            });
        }
    }, []);

    // Login function to authenticate the user
    const login = async (email, password) => {
        try {
            const res = await axios.post("/api/auth/login", { email, password });
            localStorage.setItem("token", res.data.token); // Store token in local storage
            setUser(res.data.user); // Set authenticated user
            fetchNews(); // Fetch news after login
        } catch (error) {
            console.error("Login failed", error);
        }
    };

    // Logout function to clear user data and token
    const logout = () => {
        localStorage.removeItem("token"); // Remove token from storage
        setUser(null); // Reset user state
        setNews([]); // Clear news data
    };

    // Function to fetch news for the authenticated user
    const fetchNews = async () => {
        try {
            const res = await axios.get("/api/news", {
                headers: { Authorization: `Bearer ${localStorage.getItem("token")}` }
            });
            setNews(res.data); // Update news state with fetched data
        } catch (error) {
            console.error("Failed to fetch news", error);
        }
    };

    return (
        <AuthContext.Provider value={{ user, login, logout, news }}>
            {children} {/* Render child components within the context */}
        </AuthContext.Provider>
    );
};

export default AuthContext;
