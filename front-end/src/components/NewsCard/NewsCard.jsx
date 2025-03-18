
import PropTypes from 'prop-types';
import LikeButton from '../LikeButton/LikeButton';

const NewsCard = ({ article, likedArticles, likes, onLike, onClick }) => {
    return (
        <div
            key={article.url}
            className="bg-white shadow-lg rounded-lg p-5 cursor-pointer hover:bg-gray-100 transition"
            onClick={() => onClick(article)} // Open the article modal
        >
            <h2 className="text-xl font-semibold">{article.title}</h2>
            <p className="text-sm text-gray-500">{article.pub_date}</p>

            {/* Add LikeButton component */}
            <LikeButton
                articleUrl={article.url} // Ensure article.url is passed correctly
                likedArticles={likedArticles}
                likes={likes}
                onLike={onLike}
            />
        </div>
    );
};

NewsCard.propTypes = {
    article: PropTypes.object.isRequired, // Ensure article is passed correctly
    likedArticles: PropTypes.object.isRequired,
    likes: PropTypes.object.isRequired,
    onLike: PropTypes.func.isRequired,
    onClick: PropTypes.func.isRequired,
};

export default NewsCard;
