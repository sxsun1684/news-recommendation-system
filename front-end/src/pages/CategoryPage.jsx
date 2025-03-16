import {useEffect, useState} from "react";
import {useParams} from "react-router-dom";

const CategoryPage = () => {
    const {category_name} = useParams(); // 获取 URL 里的类别
    const [news, setNews] = useState([]);
    const [lastKey, setLastKey] = useState(null);

    useEffect(() => {
        fetchNews(category_name);
    }, [category_name]);

    const fetchNews = (category, lastKey = null) => {
        let url = `http://localhost:5000/category/${category}?limit=10`;
        if (lastKey) url += `&last_key=${lastKey}`;

        fetch(url)
            .then(res => res.json())
            .then(data => {
                setNews([...news, ...data.news]);  // 追加新数据
                setLastKey(data.last_key);  // 记录下一页的起始点
            })
            .catch(err => console.error("获取新闻失败", err));
    };

    // 加载更多新闻
    const loadMore = () => {
        if (lastKey) fetchNews(category_name, lastKey);
    };

    return (
        <div>
            <h2>{category_name} 新闻</h2>
            <div style={{display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "20px"}}>
                {news.map((item) => (
                    <div key={item.news_id} style={{
                        border: "1px solid #ddd", padding: "15px", borderRadius: "8px", background: "#f9f9f9"
                    }}>
                        <h3>
                            <a href={item.url} target="_blank" rel="noopener noreferrer" style={{textDecoration: "none", color: "#007BFF"}}>
                                {item.title}
                            </a>
                        </h3>
                        <p>{item.content.substring(0, 100)}...</p> {/* 显示前 100 个字符 */}
                        <a href={item.url} target="_blank" rel="noopener noreferrer" style={{
                            display: "inline-block", marginTop: "10px", padding: "8px 12px", background: "#007BFF",
                            color: "white", borderRadius: "5px", textDecoration: "none"
                        }}>
                            查看详情
                        </a>
                    </div>
                ))}
            </div>
            {lastKey && <button onClick={loadMore} style={{
                marginTop: "20px",
                padding: "10px 15px",
                background: "#007BFF",
                color: "white",
                borderRadius: "5px",
                border: "none"
            }}>加载更多</button>}
        </div>
    );
};

export default CategoryPage;
