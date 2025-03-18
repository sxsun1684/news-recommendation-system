// import { useEffect, useState } from 'react';
// import { useParams } from 'react-router-dom';
//
// function CategoryPage() {
//     const { categoryName } = useParams();
//     const [news, setNews] = useState([]);
//     const [loading, setLoading] = useState(true);
//     const [error, setError] = useState("");
//     const [selectedArticle, setSelectedArticle] = useState(null);
//     const [likes, setLikes] = useState({});
//     const [likedArticles, setLikedArticles] = useState({});
//
//     useEffect(() => {
//         const controller = new AbortController();
//
//         const fetchNews = async () => {
//             setLoading(true);
//             setError("");
//
//             try {
//                 console.log(`Fetching news for category: ${categoryName}`);
//                 const response = await fetch(`http://127.0.0.1:5050/category/${categoryName}`, {
//                     signal: controller.signal,
//                 });
//
//                 if (!response.ok) {
//                     throw new Error(`Failed to fetch news: ${response.status}`);
//                 }
//
//                 const data = await response.json();
//                 if (!data.news) throw new Error("Invalid JSON format");
//
//                 setNews(data.news);
//             } catch (err) {
//                 if (err.name !== "AbortError") {
//                     setError("Failed to load news.");
//                     console.error("Error fetching news:", err);
//                 }
//             } finally {
//                 setLoading(false);
//             }
//         };
//
//         fetchNews();
//
//         return () => controller.abort();
//     }, [categoryName]);
//
//     // 获取用户点赞的文章列表（页面加载时）
//     useEffect(() => {
//         const fetchLikes = async () => {
//             try {
//                 const user = JSON.parse(localStorage.getItem("user"));
//                 if (!user || !user.email) return;
//
//                 const response = await fetch(`http://127.0.0.1:5050/user-likes?email=${user.email}`);
//                 if (!response.ok) throw new Error("Failed to fetch likes");
//
//                 const data = await response.json();
//                 const likedMap = {};
//                 data.liked_articles.forEach(url => likedMap[url] = true);
//
//                 setLikedArticles(likedMap);
//             } catch (error) {
//                 console.error("❌ Error fetching likes:", error);
//             }
//         };
//
//         fetchLikes();
//     }, []);
//
//     // 处理点赞逻辑
//     const handleLike = async (article) => {
//         const id = encodeURIComponent(article.url);
//         const newLikedStatus = !likedArticles[id];
//
//         // ✅ 获取用户信息
//         const user = JSON.parse(localStorage.getItem("user"));
//         if (!user || !user.email) {
//             alert("Please log in to like articles.");
//             return;
//         }
//
//         // ✅ 立即更新 UI（先本地更新，提升用户体验）
//         setLikedArticles((prev) => ({
//             ...prev,
//             [id]: newLikedStatus,
//         }));
//
//         setLikes((prev) => ({
//             ...prev,
//             [id]: (prev[id] || 0) + (newLikedStatus ? 1 : -1),
//         }));
//
//         try {
//             console.log(`Liking article: ${article.url}, Email: ${user.email}`);
//             const response = await fetch(`http://127.0.0.1:5050/like/${id}`, {
//                 method: "POST",
//                 mode: "cors",
//                 headers: { "Content-Type": "application/json" },
//                 body: JSON.stringify({
//                     email: user.email,
//                     like: newLikedStatus,
//                 }),
//             });
//
//             if (!response.ok) {
//                 throw new Error("Failed to update like");
//             }
//
//             const updatedLikes = await response.json();
//
//             // ✅ 确保状态最终与服务器同步
//             setLikes((prev) => ({
//                 ...prev,
//                 [id]: updatedLikes.total_likes, // 从后端获取总点赞数
//             }));
//
//         } catch (error) {
//             console.error("❌ Error updating like:", error);
//
//             // ❌ 如果请求失败，撤销 UI 状态更新
//             setLikedArticles((prev) => ({
//                 ...prev,
//                 [id]: !newLikedStatus,
//             }));
//
//             setLikes((prev) => ({
//                 ...prev,
//                 [id]: (prev[id] || 0) - (newLikedStatus ? 1 : -1),
//             }));
//         }
//     };
//
//     return (
//         <div className="min-h-screen bg-gray-100 py-8">
//             <div className="container mx-auto px-6">
//                 {loading && <p className="text-blue-400">Loading news...</p>}
//                 {error && <p className="text-red-400">{error}</p>}
//
//                 <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
//                     {news.map((article, index) => (
//                         <div
//                             key={article.url || index}
//                             className="bg-white shadow-lg rounded-lg p-5 cursor-pointer hover:bg-gray-100 transition"
//                             onClick={() => setSelectedArticle(article)}
//                         >
//                             <h2 className="text-xl font-semibold">{article.title}</h2>
//                             <p className="text-sm text-gray-500">{article.pub_date}</p>
//
//                             {/* 点赞按钮 */}
//                             <div className="flex items-center mt-3">
//                                 <button
//                                     className={`transition ${likedArticles[article.url] ? "text-red-500" : "text-gray-400"}`}
//                                     onClick={(e) => {
//                                         e.stopPropagation();
//                                         handleLike(article);
//                                     }}
//                                 >
//                                     {/* SVG 点赞图标 */}
//                                     <svg
//                                         xmlns="http://www.w3.org/2000/svg"
//                                         fill="currentColor"
//                                         viewBox="0 0 24 24"
//                                         width="24"
//                                         height="24"
//                                     >
//                                         <path
//                                             d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"
//                                         />
//                                     </svg>
//                                 </button>
//                                 <span className="ml-2 text-gray-700">{likes[article.url] || 0}</span>
//                             </div>
//                         </div>
//                     ))}
//                 </div>
//             </div>
//
//             {/* 文章详情 Modal */}
//             {selectedArticle && (
//                 <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
//                     <div className="bg-white rounded-lg p-6 max-w-3xl max-h-[80vh] overflow-y-auto relative shadow-xl">
//                         {/* 关闭按钮 */}
//                         <button
//                             className="absolute top-2 right-4 text-gray-500 hover:text-gray-700"
//                             onClick={() => setSelectedArticle(null)}
//                         >
//                             ✕
//                         </button>
//
//                         <h2 className="text-2xl font-bold mb-4">{selectedArticle.title}</h2>
//                         <p className="text-sm text-gray-500 mb-4">Published: {selectedArticle.pub_date}</p>
//
//                         <div className="text-gray-700 whitespace-pre-wrap">
//                             {selectedArticle.content}
//                         </div>
//
//                         <a
//                             href={selectedArticle.url}
//                             target="_blank"
//                             rel="noopener noreferrer"
//                             className="inline-block mt-4 text-blue-600 hover:underline"
//                         >
//                             🔗 View Original Article
//                         </a>
//                     </div>
//                 </div>
//             )}
//         </div>
//     );
// }
//
// export default CategoryPage;
import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom'; // 使用 useParams 获取 categoryName
import NewsCard from '../components/NewsCard/NewsCard';
import ArticleModal from '../components/ArticleModal/ArticleModal';

const CategoryPage = () => {
    const { categoryName } = useParams();  // 使用 useParams 来获取 categoryName 参数
    const [news, setNews] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [selectedArticle, setSelectedArticle] = useState(null);
    const [likes, setLikes] = useState({});
    const [likedArticles, setLikedArticles] = useState({});

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
                    throw new Error(`Failed to fetch news: ${response.status}`);
                }

                const data = await response.json();
                setNews(data.news);
            } catch (err) {
                if (err.name !== "AbortError") {
                    setError("Failed to load news.");
                    console.error("Error fetching news:", err);
                }
            } finally {
                setLoading(false);
            }
        };

        fetchNews();

        return () => controller.abort();
    }, [categoryName]);  // 在 categoryName 变化时重新获取数据

    const handleLike = async (articleUrl) => {
        const newLikedStatus = !likedArticles[articleUrl];

        const user = JSON.parse(localStorage.getItem("user"));
        if (!user || !user.email) {
            alert("Please log in to like articles.");
            return;
        }

        setLikedArticles((prev) => ({
            ...prev,
            [articleUrl]: newLikedStatus,
        }));

        setLikes((prev) => ({
            ...prev,
            [articleUrl]: (prev[articleUrl] || 0) + (newLikedStatus ? 1 : -1),
        }));

        try {
            const response = await fetch(`http://127.0.0.1:5050/like/${articleUrl}`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    email: user.email,
                    like: newLikedStatus,
                }),
            });

            if (!response.ok) {
                throw new Error("Failed to update like");
            }

            const updatedLikes = await response.json();

            setLikes((prev) => ({
                ...prev,
                [articleUrl]: updatedLikes.total_likes,
            }));
        } catch (error) {
            console.error("❌ Error updating like:", error);
            setLikedArticles((prev) => ({
                ...prev,
                [articleUrl]: !newLikedStatus,
            }));
            setLikes((prev) => ({
                ...prev,
                [articleUrl]: (prev[articleUrl] || 0) - (newLikedStatus ? 1 : -1),
            }));
        }
    };

    return (
        <div className="min-h-screen bg-gray-100 py-8">
            <div className="container mx-auto px-6">
                {loading && <p className="text-blue-400">Loading news...</p>}
                {error && <p className="text-red-400">{error}</p>}

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {news.map((article, index) => (
                        <NewsCard
                            key={article.url || index}
                            article={article}
                            likedArticles={likedArticles}
                            likes={likes}
                            onLike={handleLike}
                            onClick={setSelectedArticle}
                        />
                    ))}
                </div>
            </div>

            {selectedArticle && (
                <ArticleModal
                    selectedArticle={selectedArticle}
                    onClose={() => setSelectedArticle(null)}
                />
            )}
        </div>
    );
};

export default CategoryPage;
