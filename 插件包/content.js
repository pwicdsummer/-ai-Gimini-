let lastAiContent = ""; 

function getLatestConversation() {
    // 专门针对 Gemini 的选择器
    // 获取用户的提问
    const userQueries = document.querySelectorAll('user-query, .user-query-text, [data-message-author-role="user"]');
    // 获取 AI 的回答
    const aiResponses = document.querySelectorAll('model-response, .message-content, [data-message-author-role="assistant"]');

    if (userQueries.length === 0 || aiResponses.length === 0) return null;

    // 分别获取最后一条用户提问和最后一条 AI 回答
    const latestUserMessage = userQueries[userQueries.length - 1].innerText.trim();
    const latestAiMessage = aiResponses[aiResponses.length - 1].innerText.trim();

    return {
        user_prompt: latestUserMessage,
        ai_response: latestAiMessage
    };
}

setInterval(() => {
    const data = getLatestConversation();
    if (!data) return;

    // 核心优化：只在 AI 的回答内容发生增长/变化时才发送请求
    if (data.ai_response !== lastAiContent) {
        lastAiContent = data.ai_response; 

        fetch('http://localhost:5000/save_chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                user_prompt: data.user_prompt,
                ai_response: data.ai_response,
                source: window.location.hostname
            })
        })
        .then(() => console.log(`来自 ${window.location.hostname} 的内容已同步 (长度: ${data.ai_response.length})`))
        .catch(err => console.warn("后端未启动"));
    }
}, 2500);
