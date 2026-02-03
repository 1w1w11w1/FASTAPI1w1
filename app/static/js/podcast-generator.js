// 播客生成器功能脚本
document.addEventListener('DOMContentLoaded', function() {
    const textInput = document.getElementById('textInput');
    const charCount = document.getElementById('charCount');
    const clearBtn = document.getElementById('clearBtn');
    const generateBtn = document.getElementById('generateBtn');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const resultSection = document.getElementById('resultSection');
    const dialogOutput = document.getElementById('dialogOutput');
    const exportBtn = document.getElementById('exportBtn');
    const exportJsonBtn = document.getElementById('exportJsonBtn');
    const regenerateBtn = document.getElementById('regenerateBtn');
    const dialogStyle = document.getElementById('dialogStyle');
    const participants = document.getElementById('participants');
    const fileInput = document.getElementById('fileInput');
    const createPodcastBtn = document.getElementById('createPodcastBtn');
    const modelSelect = document.getElementById('model');
    const customModelInput = document.getElementById('customModel');
    
    let currentScript = null; // 保存当前脚本
    let currentTokenUsage = null; // 保存当前token使用量
    let currentDialog = null; // 保存当前对话
    let currentModel = null; // 保存当前使用的模型

    // 实时更新字数统计
    textInput.addEventListener('input', function() {
        charCount.textContent = textInput.value.length;
    });

    // 清空文本
    clearBtn.addEventListener('click', function() {
        textInput.value = '';
        charCount.textContent = '0';
        textInput.focus();
    });

    // 文件上传功能
    fileInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                textInput.value = e.target.result;
                charCount.textContent = textInput.value.length;
                alert('文件导入成功！');
            };
            reader.onerror = function() {
                alert('文件读取失败，请重试！');
            };
            reader.readAsText(file, 'utf-8');
        }
    });

    // 模型选择事件监听器
    modelSelect.addEventListener('change', function() {
        const isCustomModel = modelSelect.value === 'custom';
        customModelInput.disabled = !isCustomModel;
        if (!isCustomModel) {
            customModelInput.value = '';
        }
    });

    // 生成播客对话
    generateBtn.addEventListener('click', function() {
        const content = textInput.value.trim();
        
        if (!content) {
            alert('请输入文本内容！');
            textInput.focus();
            return;
        }
        
        if (content.length < 10) {
            alert('文本内容太短，请输入至少10个字符！');
            return;
        }
        
        // 显示加载指示器
        generateBtn.disabled = true;
        loadingIndicator.classList.remove('hidden');
        resultSection.classList.add('hidden');
        
        // 获取所选模型
        let model = modelSelect.value;
        if (model === 'custom') {
            const customModel = customModelInput.value.trim();
            if (!customModel) {
                alert('请输入自定义模型名称！');
                return;
            }
            model = customModel;
        }
        
        // 保存当前模型
        currentModel = model;
        
        // 调用后端真实接口
        fetch('/generate-script', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: content, style: dialogStyle.value, participants: parseInt(participants.value), model: model })
        })
        .then(r => r.json())
        .then(resp => {
            if (!resp || !resp.ok) throw new Error(resp && resp.error ? resp.error : '生成错误');
            // 将结构化脚本转换为前端显示格式
            const script = resp.script;
            currentScript = script; // 保存当前脚本
            currentTokenUsage = resp.token_usage || {}; // 保存当前token使用量
            
            // 检查是否存在模型错误
            const isModelError = script.model_error === true;
            const hasTokenError = (currentTokenUsage.total_tokens || 0) === 0;
            
            const dialog = [];
            const roleMap = {};
            if (script.roles && Array.isArray(script.roles)){
                script.roles.forEach(r => { 
                    const roleName = r.name || r.id;
                    roleMap[r.id] = roleName;
                });
            }
            if (script.segments && Array.isArray(script.segments)){
                script.segments.forEach(s => {
                    const speaker = roleMap[s.role] || s.role;
                    dialog.push({ role: s.role, speaker: speaker, text: s.text });
                });
            } else if (script.raw) {
                // 若只有 raw 文本，按句拆分并交替分配
                const parts = script.raw.split(/(?<=[。！？.!?])\s*/).filter(p => p.trim());
                const speakers = Object.values(roleMap).length > 0 ? Object.values(roleMap) : ['主持人', '嘉宾'];
                parts.forEach((p,i) => {
                    const speaker = speakers[i % speakers.length];
                    const roleId = Object.keys(roleMap)[i % Object.keys(roleMap).length] || (i % 2 === 0 ? 'host' : 'guest');
                    dialog.push({ role: roleId, speaker: speaker, text: p });
                });
            }
            currentDialog = dialog; // 保存当前对话
            displayDialog(dialog);
            displayTokenUsage(currentTokenUsage);
            loadingIndicator.classList.add('hidden');
            resultSection.classList.remove('hidden');
            
            // 如果是模型错误或token使用量为0，显示更明确的错误提示
            if (isModelError || hasTokenError) {
                alert('模型调用失败，请检查API配置和网络连接。\n\n排查思路：\n1. 检查.env文件中的API密钥是否正确\n2. 确保网络连接正常\n3. 尝试重启服务\n4. 如问题持续，请检查API提供商的服务状态');
            }
            
            // 自动保存生成的对话
            saveGeneratedDialog(script);
        })
            .catch(error => {
                alert('生成对话时出错：' + error.message);
                loadingIndicator.classList.add('hidden');
                generateBtn.disabled = false;
            });
    });

    // 自动保存生成的对话到result目录
    function saveGeneratedDialog(script) {
        const dialogText = getDialogText();
        
        // 生成简短摘要作为文件名
        let summary = '播客对话';
        if (script.segments && script.segments.length > 0) {
            const firstSegment = script.segments[0].text || '';
            summary = firstSegment.substring(0, 20).replace(/[^\u4e00-\u9fa5a-zA-Z0-9]/g, '') || '播客对话';
            if (summary.length > 7) {
                summary = summary.substring(0, 7);
            }
        }
        
        // 生成时间戳
        const now = new Date();
        const timestamp = now.getFullYear() + 
                         String(now.getMonth() + 1).padStart(2, '0') + 
                         String(now.getDate()).padStart(2, '0') + '_' +
                         String(now.getHours()).padStart(2, '0') + 
                         String(now.getMinutes()).padStart(2, '0') + 
                         String(now.getSeconds()).padStart(2, '0');
        
        const filename = `${summary}_${timestamp}.txt`;
        
        // 调用后端保存文件
        fetch('/save-dialog', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                content: dialogText, 
                filename: filename,
                script: script
            })
        })
        .then(r => r.json())
        .then(resp => {
            if (resp.ok) {
                console.log('对话已自动保存到result目录');
            } else {
                console.log('自动保存失败:', resp.error);
            }
        })
        .catch(error => {
            console.log('自动保存出错:', error);
        });
    }

    // 导出为文本文件
    exportBtn.addEventListener('click', function() {
        if (!currentScript) {
            alert('请先生成对话！');
            return;
        }
        
        const dialogText = getDialogText();
        const blob = new Blob([dialogText], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = '播客对话.txt';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    });

    // 导出为JSON文件
    exportJsonBtn.addEventListener('click', function() {
        if (!currentScript) {
            alert('请先生成对话！');
            return;
        }
        
        const blob = new Blob([JSON.stringify(currentScript, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = '播客对话.json';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    });

    // 重新生成
    regenerateBtn.addEventListener('click', function() {
        generateBtn.click();
    });

    // 创建播客音频
    createPodcastBtn.addEventListener('click', function() {
        if (!currentDialog) {
            alert('请先生成对话！');
            return;
        }
        
        // 显示加载指示器
        createPodcastBtn.disabled = true;
        loadingIndicator.classList.remove('hidden');
        
        // 处理对话，生成语音
        fetch('/process-dialog-tts', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ dialog: currentDialog })
        })
        .then(r => r.json())
        .then(resp => {
            if (!resp || !resp.ok) throw new Error(resp && resp.error ? resp.error : '处理对话失败');
            
            // 创建播客节目
            return fetch('/create-podcast', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    dialog: resp.dialog, 
                    podcast_title: '播客对话_' + new Date().toISOString().slice(0, 10) 
                })
            });
        })
        .then(r => r.json())
        .then(resp => {
            if (!resp || !resp.ok) throw new Error(resp && resp.error ? resp.error : '创建播客失败');
            
            alert('播客音频创建成功！');
            console.log('播客创建成功，路径:', resp.podcast_path);
        })
        .catch(error => {
            alert('创建播客时出错：' + error.message);
            console.error('创建播客失败:', error);
        })
        .finally(() => {
            loadingIndicator.classList.add('hidden');
            createPodcastBtn.disabled = false;
        });
    });

    // 显示生成的对话
    function displayDialog(dialog) {
        dialogOutput.innerHTML = '';

        // 使用容器列表支持左右气泡布局
        const list = document.createElement('div');
        list.className = 'dialog-list';

        dialog.forEach((item, index) => {
            const dialogItem = document.createElement('div');
            // 左右交替：主持人/首位左侧，其余交替右侧
            const side = (index % 2 === 0) ? 'left' : 'right';
            // 构造安全的角色类名，便于按角色上色
            const rawRole = item.role || 'unknown';
            const roleClass = 'role-' + String(rawRole).replace(/[^a-zA-Z0-9_-]/g, '-');
            dialogItem.className = `dialog-item ${side} ${roleClass}`;

            const header = document.createElement('div');
            header.className = 'dialog-header';
            header.textContent = item.speaker + (item.speaker ? ':' : '');

            const textDiv = document.createElement('div');
            textDiv.className = 'dialog-text';
            textDiv.textContent = item.text;

            // 添加语音播放按钮
            const audioBtn = document.createElement('button');
            audioBtn.className = 'audio-play-btn';
            audioBtn.textContent = '🔊 播放语音';
            audioBtn.onclick = function() {
                generateAndPlaySpeech(item.text, item.role, index);
            };

            dialogItem.appendChild(header);
            dialogItem.appendChild(textDiv);
            dialogItem.appendChild(audioBtn);
            list.appendChild(dialogItem);
        });

        dialogOutput.appendChild(list);
        generateBtn.disabled = false;
    }

    // 生成并播放语音
    function generateAndPlaySpeech(text, role, index) {
        // 显示加载指示器
        const loadingIndicator = document.getElementById('loadingIndicator');
        loadingIndicator.classList.remove('hidden');
        
        // 调用TTS API生成语音
        fetch('/generate-speech', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: text, speaker_id: role, audio_format: 'mp3' })
        })
        .then(r => r.json())
        .then(resp => {
            if (!resp || !resp.ok) throw new Error(resp && resp.error ? resp.error : '生成语音失败');
            
            // 播放语音
            const audioPath = resp.audio_path;
            if (audioPath) {
                const audio = new Audio(audioPath);
                audio.play().catch(error => {
                    console.error('播放语音失败:', error);
                    alert('播放语音失败，请检查浏览器设置');
                });
            }
        })
        .catch(error => {
            alert('生成语音时出错：' + error.message);
            console.error('生成语音失败:', error);
        })
        .finally(() => {
            loadingIndicator.classList.add('hidden');
        });
    }

    // 显示token使用量
    function displayTokenUsage(tokenUsage) {
        // 检查是否已存在token使用量显示元素
        let tokenUsageElement = document.getElementById('tokenUsageInfo');
        if (!tokenUsageElement) {
            // 创建新的token使用量显示元素
            tokenUsageElement = document.createElement('div');
            tokenUsageElement.id = 'tokenUsageInfo';
            tokenUsageElement.className = 'token-usage-info';
            resultSection.insertBefore(tokenUsageElement, dialogOutput);
        }
        
        // 计算总tokens
        const promptTokens = tokenUsage.prompt_tokens || 0;
        const completionTokens = tokenUsage.completion_tokens || 0;
        const totalTokens = tokenUsage.total_tokens || (promptTokens + completionTokens);
        
        // 检查是否为异常情况（token使用量为0）
        const isTokenZero = totalTokens === 0;
        
        // 更新token使用量显示
        let tokenUsageHtml = `
            <div class="token-usage-title">Token使用量：</div>
            <div class="token-usage-details">
                <span>输入：${promptTokens}</span>
                <span>输出：${completionTokens}</span>
                <span>总计：${totalTokens}</span>
            </div>
        `;
        
        // 如果token使用量为0，添加警告信息
        if (isTokenZero) {
            tokenUsageHtml += `
                <div class="token-usage-warning">
                    ⚠️ 可能产生模型调用失败，请检查API配置
                </div>
            `;
            tokenUsageElement.className = 'token-usage-info warning';
        } else {
            tokenUsageElement.className = 'token-usage-info';
        }
        
        tokenUsageElement.innerHTML = tokenUsageHtml;
    }

    // 获取对话文本
    function getDialogText() {
        let text = '';
        
        // 添加生成配置信息
        const style = dialogStyle.value;
        const participantsNum = participants.value;
        text += `生成配置：\n`;
        text += `语言风格：${style === 'casual' ? '轻松随意' : style === 'entertainment' ? '娱乐幽默' : '专业严谨'}\n`;
        text += `参与人数：${participantsNum}\n`;
        text += `使用模型：${currentModel || 'deepseek-v3.2'}\n\n`;
        
        // 添加token使用量信息（如果有）
        if (currentTokenUsage) {
            const promptTokens = currentTokenUsage.prompt_tokens || 0;
            const completionTokens = currentTokenUsage.completion_tokens || 0;
            const totalTokens = currentTokenUsage.total_tokens || (promptTokens + completionTokens);
            text += `Token使用量：\n`;
            text += `输入：${promptTokens}\n`;
            text += `输出：${completionTokens}\n`;
            text += `总计：${totalTokens}\n\n`;
            text += `================================\n\n`;
        }
        
        // 添加对话内容
        const items = dialogOutput.querySelectorAll('.dialog-item');
        items.forEach(item => {
            text += item.textContent + '\n\n';
        });
        
        return text;
    }
});