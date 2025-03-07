import {useParams} from 'react-router-dom';
import {useEffect, useState} from 'react';

function CategoryPage() {
    const {categoryName} = useParams();
    const [news, setNews] = useState([]);

    useEffect(() => {
        fetch(`http://127.0.0.1:5000/category/${categoryName}`)
            .then((res) => res.json())
            .then((data) => setNews(data.news))
            .catch(err => console.error("Error fetching data:", err));
    }, [categoryName]);

    return (
        <div>
            <h2>{categoryName} News</h2>
            <ul>
                {news.map((article, index) => (
                    <li key={index}>{article.title}</li>
                ))}
            </ul>
        </div>
    );
}

export default CategoryPage;
