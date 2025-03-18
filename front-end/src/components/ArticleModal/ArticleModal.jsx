import { useEffect, useState, useRef } from 'react';
import PropTypes from 'prop-types';

const ArticleModal = ({ selectedArticle, onClose }) => {
    const [viewStartTime, setViewStartTime] = useState(null);
    const [duration, setDuration] = useState(0);  // 用来存储停留时间
    const isFirstRender = useRef(true);  // 使用 useRef 来确保只执行一次测量

    const sendUserActionToKafka = async (duration, userEmail, user_id, action) => {
        const articleUrl = selectedArticle.url;

        try {
            const response = await fetch('http://localhost:5050/api/user-behavior', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email: userEmail,
                    user_id: user_id,
                    article_url: articleUrl,
                    duration: duration,
                    action: action,  // 传递不同的 action
                }),
            });

            if (!response.ok) {
                throw new Error(`Failed to fetch: ${response.statusText}`);
            }

            const responseData = await response.json();
            console.log('Backend response:', responseData);

        } catch (error) {
            console.error('Failed to send reading time to backend:', error);
        }
    };

    useEffect(() => {
        // 从 localStorage 获取 'user' 数据，并解析为对象
        const user = localStorage.getItem('user');
        if (user) {
            const parsedUser = JSON.parse(user);  // 解析字符串为对象
            const email = parsedUser.email;  // 提取 email
            const user_id = parsedUser.user_id; // 提取 user_id

            // 如果存在 email 和 user_id，发送阅读时长数据
            if (email && user_id) {
                const action = 'READ';  // 阅读文章时，使用 'READ' 作为 action
                sendUserActionToKafka(duration, email, user_id, action);  // 使用获取到的 email 和 user_id
            }
        } else {
            console.log("No user data in localStorage");
        }

        if (selectedArticle && isFirstRender.current) {
            setViewStartTime(Date.now());  // 记录打开文章的时间

            performance.clearMarks();
            performance.clearMeasures();

            performance.mark("start-reading");

            isFirstRender.current = false;  // 标记为已经执行过，防止后续重复执行
        }

        const interval = setInterval(() => {
            if (viewStartTime) {
                const currentDuration = Math.floor((Date.now() - viewStartTime) / 1000);
                setDuration(currentDuration);  // 每秒更新一次停留时间
            }
        }, 1000);

        return () => {
            clearInterval(interval);
            if (viewStartTime) {
                const finalDuration = Math.floor((Date.now() - viewStartTime) / 1000); // 最终停留时间（秒）

                if (isFirstRender.current === false) {
                    performance.mark("end-reading");
                    performance.measure("Reading Time", "start-reading", "end-reading");

                    const entries = performance.getEntriesByName("Reading Time");
                    console.log(`User spent a total of ${finalDuration} seconds reading the article.`);
                    console.log(entries);

                    // 获取用户的 email 和 user_id，假设保存在 localStorage 中
                    const user = localStorage.getItem('user');
                    if (user) {
                        const parsedUser = JSON.parse(user);
                        const email = parsedUser.email;
                        const user_id = parsedUser.user_id;

                        if (email || user_id) {
                            const action = 'READ';  // 阅读时的 action
                            sendUserActionToKafka(finalDuration, email, user_id, action);  // 发送数据到后端
                        }
                    }
                }
            }
        };
    }, [selectedArticle, viewStartTime]);

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 max-w-3xl max-h-[80vh] overflow-y-auto relative shadow-xl">
                <button className="absolute top-2 right-4 text-gray-500 hover:text-gray-700" onClick={onClose}>✕</button>

                <h2 className="text-2xl font-bold mb-4">{selectedArticle.title}</h2>
                <p className="text-sm text-gray-500 mb-4">Published: {selectedArticle.pub_date}</p>
                <div className="text-gray-700 whitespace-pre-wrap">
                    {selectedArticle.content}
                </div>

                <p className="text-sm text-gray-500 mt-4">Time spent reading: {duration} seconds</p>

                <a href={selectedArticle.url} target="_blank" rel="noopener noreferrer" className="inline-block mt-4 text-blue-600 hover:underline">
                    🔗 View Original Article
                </a>
            </div>
        </div>
    );
};

ArticleModal.propTypes = {
    selectedArticle: PropTypes.object,
    onClose: PropTypes.func.isRequired,
};

export default ArticleModal;
