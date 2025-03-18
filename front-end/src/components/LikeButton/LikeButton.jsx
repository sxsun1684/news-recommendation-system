import PropTypes from 'prop-types';
import { useState } from 'react';

const LikeButton = ({ articleUrl, likedArticles, onLike }) => {
    const liked = likedArticles[articleUrl];
    const [isLoading, setIsLoading] = useState(false);  // 用来跟踪请求状态

    const handleLike = async (e) => {
        e.stopPropagation(); // 防止触发其他事件（如打开模态框）

        // 获取用户信息
        const user = localStorage.getItem('user');
        const parsedUser = user ? JSON.parse(user) : null;

        if (parsedUser && !isLoading) {
            const { user_id, email } = parsedUser;
            setIsLoading(true); // 禁用按钮，避免重复点击

            const data = {
                userId: user_id,
                email: email,
                articleUrl: articleUrl,
                action: 'LIKE', // 操作类型（点赞）
            };

            try {
                const response = await fetch('http://localhost:5050/api/user-behavior', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data),
                });

                if (!response.ok) {
                    throw new Error(`Failed to send like data: ${response.statusText}`);
                }

                const responseData = await response.json();
                console.log('Backend response:', responseData);
                onLike(articleUrl); // 只有成功后才更新父组件状态
            } catch (error) {
                console.error('Error sending like data to backend:', error);
            } finally {
                setIsLoading(false); // 请求完成，恢复按钮状态
            }
        }
    };

    return (
        <div className="flex items-center mt-3">
            <button
                className={`transition ${liked ? "text-red-500" : "text-gray-400"}`}
                onClick={handleLike}
                disabled={isLoading}  // 禁用按钮，防止重复点击
            >
                <svg
                    xmlns="http://www.w3.org/2000/svg"
                    fill="currentColor"
                    viewBox="0 0 24 24"
                    width="24"
                    height="24"
                >
                    <path
                        d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"
                    />
                </svg>
            </button>
        </div>
    );
};

LikeButton.propTypes = {
    articleUrl: PropTypes.string.isRequired,  // Prop validation for articleUrl
    likedArticles: PropTypes.object.isRequired,  // Prop validation for likedArticles (object)
    onLike: PropTypes.func.isRequired,  // Prop validation for onLike (function)
};

export default LikeButton;
