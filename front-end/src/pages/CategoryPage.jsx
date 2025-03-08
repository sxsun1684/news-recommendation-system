import {useEffect, useState} from 'react';
import {useParams} from 'react-router-dom';

function CategoryPage() {
    const {categoryName} = useParams();
    const [news, setNews] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        const controller = new AbortController();
        const fetchNews = async () => {
            try {
                setLoading(true);
                setError("");
                const response = await fetch(`http://127.0.0.1:5000/category/${categoryName}`, {
                    signal: controller.signal,
                });

                if (!response.ok) {
                    throw new Error(`Failed to fetch: ${response.status}`);
                }

                const data = await response.json();
                setNews(data.news);
            } catch (err) {
                if (err.name !== "AbortError") {
                    setError("Failed to load news. Please try again.");
                    console.error("Error fetching data:", err);
                }
            } finally {
                setLoading(false);
            }
        };

        fetchNews();
        return () => controller.abort();
    }, [categoryName]);

    return (
        <div
            className="relative min-h-screen flex flex-col items-center justify-center p-10 bg-[#0a0f1e] text-white overflow-hidden">

            {/* Animated background particles */}
            <div
                className="absolute inset-0 bg-[url('/particles.svg')] bg-cover bg-center opacity-20 animate-pulse"></div>

            {/* Soft light gradient effect */}
            <div
                className="absolute inset-0 bg-gradient-to-br from-blue-600 via-black to-purple-600 opacity-30 blur-2xl"></div>

            {/* Main content */}
            <div className="relative z-10 w-full max-w-3xl bg-white/10 backdrop-blur-lg border border-white/20
                            rounded-2xl shadow-lg p-8 md:p-6 sm:p-4">

                <h2 className="text-4xl font-extrabold text-white tracking-wide capitalize
                md:text-3xl sm:text-2xl xs:text-xl">
                    {categoryName} News
                </h2>

                {/* Loading indicator */}
                {loading && <p className="mt-4 text-lg text-blue-300 animate-pulse">Loading...</p>}

                {/* Error message */}
                {error && <p className="mt-4 text-lg text-red-400">{error}</p>}

                {/* News List */}
                {!loading && !error && (
                    <ul className="mt-6 space-y-4">
                        {news.length > 0 ? (
                            news.map((article, index) => (
                                <li key={index} className="py-3 px-4 border-b border-gray-600 last:border-none
                                transition duration-300 hover:bg-white/20 hover:scale-105 rounded-md">
                                    {article.title}
                                </li>
                            ))
                        ) : (
                            <p className="text-gray-400">No news available for this category.</p>
                        )}
                    </ul>
                )}
            </div>
        </div>
    );
}

export default CategoryPage;
