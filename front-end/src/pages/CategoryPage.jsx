import {useEffect, useState} from 'react';
import {useParams} from 'react-router-dom';

function CategoryPage() {
    const {categoryName} = useParams();  // 获取 URL 中的分类名
    const [news, setNews] = useState([]);  // 保存新闻数据

    useEffect(() => {
        const fetchNews = async () => {
            try {
                const response = await fetch(`http://127.0.0.1:5000/category/${categoryName}`);
                const data = await response.json();
                setNews(data.news);  // 更新状态
            } catch (err) {
                console.error("Error fetching data:", err);  // 捕获错误
            }
        };

        fetchNews();  // 调用异步请求函数
    }, [categoryName]);  // 依赖 categoryName，当 categoryName 改变时重新请求

    return (
        <div>
            <h2>{categoryName} News</h2>
            <ul>
                {news.map((article, index) => (
                    <li key={index}>{article.title}</li>  // 渲染每篇新闻的标题
                ))}
            </ul>
        </div>
    );
}

export default CategoryPage;
