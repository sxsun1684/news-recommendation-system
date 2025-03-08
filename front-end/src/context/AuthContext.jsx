import {createContext, useState, useEffect} from "react";
import PropTypes from "prop-types";
import axios from "axios";

// Create authentication context
const AuthContext = createContext(null);

const API_BASE = "http://localhost:5050";

export const AuthProvider = ({children}) => {
    const [user, setUser] = useState(() => {
        // Retrieve user data from localStorage to maintain session state
        const savedUser = localStorage.getItem("user");
        return savedUser ? JSON.parse(savedUser) : null;
    });

    useEffect(() => {
        // Check if the user is already authenticated
        axios.get(`${API_BASE}/api/auth/me`, {withCredentials: true})
            .then(res => {
                setUser(res.data);
                localStorage.setItem("user", JSON.stringify(res.data)); // Store user data persistently
            })
            .catch(() => {
                setUser(null);
                localStorage.removeItem("user");
            });
    }, []);

    // Register a new user (does not auto-login)
    const register = async (email, password) => {
        try {
            await axios.post(`${API_BASE}/api/auth/register`, {email, password}, {withCredentials: true});
            alert("Registration successful! You can now log in.");
            return true;  // Registration successful
        } catch (error) {
            if (error.response) {
                if (error.response.status === 409) alert("Email is already registered");  // Friendly error message
                return error.response.data.message || "Registration failed, please try again later";
            }
            return "Network error, please try again later";
        }
    };

    // Handle user login
    const login = async (email, password) => {
        try {
            const res = await axios.post(`${API_BASE}/api/auth/login`, {email, password}, {withCredentials: true});
            setUser(res.data.user);
            localStorage.setItem("user", JSON.stringify(res.data.user)); // Store user data persistently
            return true;
        } catch (error) {
            console.error("Login failed", error);
            alert("Login failed, please check your email and password");
        }
    };

    // Handle user logout
    const logout = async () => {
        await axios.post(`${API_BASE}/api/auth/logout`, {}, {withCredentials: true});
        setUser(null);
        localStorage.removeItem("user"); // Clear user data
    };

    return (
        <AuthContext.Provider value={{user, register, login, logout}}>
            {children}
        </AuthContext.Provider>
    );
};

AuthProvider.propTypes = {
    children: PropTypes.node.isRequired,
};

export {AuthContext};
export default AuthProvider;
