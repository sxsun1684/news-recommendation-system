import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';

function CategoryPage() {
    const { categoryName } = useParams();
    const [news, setNews] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [selectedArticle, setSelectedArticle] = useState(null);

    useEffect(() => {
        const controller = new AbortController();

        const fetchNews = async () => {
            setLoading(true);
            setError("");
            try {
                const response = await fetch(`http://127.0.0.1:5050/category/${categoryName}`, {
                    signal: controller.signal,
                });

                if (!response.ok) {
                    throw new Error(`Error: ${response.status}`);
                }

                const data = await response.json();
                setNews(data.news);
            } catch (err) {
                if (err.name !== "AbortError") {
                    setError("Failed to load news.");
                    console.error(err);
                }
            } finally {
                setLoading(false);
            }
        };

        fetchNews();

        return () => controller.abort();
    }, [categoryName]);

    return (
        <div className="min-h-screen bg-gray-100 py-8">
            <div className="container mx-auto px-6">
                {/*<h1 className="text-4xl font-bold capitalize mb-6">{categoryName} News</h1>*/}

                {loading && <p className="text-blue-400">Loading news...</p>}
                {error && <p className="text-red-400">{error}</p>}

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {news.map(article => (
                        <div
                            key={article.id || article.url || Math.random()}
                            className="bg-white shadow-lg rounded-lg cursor-pointer p-5 transition duration-300 hover:bg-gray-50"
                            onClick={() => setSelectedArticle(article)}
                        >
                            <h2 className="text-xl font-semibold mb-2">{article.title}</h2>
                            <p className="text-sm text-gray-500">Date：{article.pub_date}</p>
                        </div>
                    ))}
                </div>

                {news.length === 0 && !loading && !error && (
                    <p className="text-gray-400 mt-6">No news found for this category.</p>
                )}

                {/* Modal 显示完整文章内容 */}
                {selectedArticle && (
                    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                        <div className="bg-white rounded-lg p-6 max-w-3xl max-h-[80vh] overflow-y-auto relative shadow-xl">
                            <button
                                className="absolute top-2 right-4 text-gray-500 hover:text-gray-700"
                                onClick={() => setSelectedArticle(null)}
                            >
                                ✕
                            </button>
                            <h2 className="text-2xl font-bold mb-4">{selectedArticle.title}</h2>
                            <p className="text-sm text-gray-500 mb-4">Published: {selectedArticle.pub_date}</p>
                            <div className="text-gray-700 whitespace-pre-wrap">
                                {selectedArticle.content}
                            </div>
                            <a href={selectedArticle.url} target="_blank" rel="noopener noreferrer"
                                className="inline-block mt-4 text-blue-600 hover:underline">
                                🔗 View Original Article
                            </a>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}

export default CategoryPage;
