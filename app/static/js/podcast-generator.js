// 播客生成器功能脚本
document.addEventListener('DOMContentLoaded', function() {
    const textInput = document.getElementById('textInput');
    const charCount = document.getElementById('charCount');
    const clearBtn = document.getElementById('clearBtn');
    const generateBtn = document.getElementById('generateBtn');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const resultSection = document.getElementById('resultSection');
    const dialogOutput = document.getElementById('dialogOutput');
    const copyBtn = document.getElementById('copyBtn');
    const exportBtn = document.getElementById('exportBtn');
    const regenerateBtn = document.getElementById('regenerateBtn');
    const dialogStyle = document.getElementById('dialogStyle');
    const participants = document.getElementById('participants');

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
        
        // 调用后端真实接口
        fetch('/generate-script', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: content, style: dialogStyle.value, participants: parseInt(participants.value) })
        })
        .then(r => r.json())
        .then(resp => {
            if (!resp || !resp.ok) throw new Error(resp && resp.error ? resp.error : '生成错误');
            // 将结构化脚本转换为前端显示格式
            const script = resp.script;
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
            displayDialog(dialog);
            loadingIndicator.classList.add('hidden');
            resultSection.classList.remove('hidden');
        })
            .catch(error => {
                alert('生成对话时出错：' + error.message);
                loadingIndicator.classList.add('hidden');
                generateBtn.disabled = false;
            });
    });

    // 复制对话文本
    copyBtn.addEventListener('click', function() {
        const dialogText = getDialogText();
        navigator.clipboard.writeText(dialogText)
            .then(() => {
                alert('对话文本已复制到剪贴板！');
            })
            .catch(err => {
                alert('复制失败，请手动选择文本复制');
            });
    });

    // 导出为文本文件
    exportBtn.addEventListener('click', function() {
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

    // 重新生成
    regenerateBtn.addEventListener('click', function() {
        generateBtn.click();
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

            dialogItem.appendChild(header);
            dialogItem.appendChild(textDiv);
            list.appendChild(dialogItem);
        });

        dialogOutput.appendChild(list);
        generateBtn.disabled = false;
    }

    // 获取对话文本
    function getDialogText() {
        let text = '';
        const items = dialogOutput.querySelectorAll('.dialog-item');
        
        items.forEach(item => {
            text += item.textContent + '\n\n';
        });
        
        return text;
    }

    // 模拟API调用
    function simulateAPICall(content, style, participantCount) {
        return new Promise((resolve, reject) => {
            setTimeout(() => {
                try {
                    // 模拟生成对话逻辑
                    const sentences = content.split(/[。！？.!?]/).filter(s => s.trim().length > 0);
                    const dialog = [];
                    const speakers = ['主持人'];
                    
                    // 添加嘉宾
                    for (let i = 1; i < participantCount; i++) {
                        speakers.push(`嘉宾${i}`);
                    }
                    
                    sentences.forEach((sentence, index) => {
                        if (sentence.trim().length > 0) {
                            const speakerIndex = index % speakers.length;
                            const role = speakerIndex === 0 ? 'host' : 'guest';
                            
                            dialog.push({
                                role: role,
                                speaker: speakers[speakerIndex],
                                text: sentence.trim() + (index < sentences.length - 1 ? '。' : '')
                            });
                        }
                    });
                    
                    // 添加开场和结束语
                    if (dialog.length > 0) {
                        dialog.unshift({
                            role: 'host',
                            speaker: '主持人',
                            text: getOpeningByStyle(style)
                        });
                        
                        dialog.push({
                            role: 'host',
                            speaker: '主持人',
                            text: getClosingByStyle(style)
                        });
                    }
                    
                    resolve(dialog);
                } catch (error) {
                    reject(error);
                }
            }, 2000);
        });
    }

    function getOpeningByStyle(style) {
        const openings = {
            casual: '大家好，欢迎收听今天的节目！',
            professional: '各位听众大家好，欢迎收听本期专业播客。',
            entertainment: '嘿，朋友们！准备好享受一段有趣的对话了吗？'
        };
        return openings[style] || openings.casual;
    }

    function getClosingByStyle(style) {
        const closings = {
            casual: '感谢大家的收听，我们下期再见！',
            professional: '以上就是本期的全部内容，谢谢收听。',
            entertainment: '今天的节目就到这里，保持微笑，下次见！'
        };
        return closings[style] || closings.casual;
    }
});