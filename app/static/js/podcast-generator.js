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
        
        // 模拟API调用（实际使用时替换为真实的API调用）
        simulateAPICall(content, dialogStyle.value, parseInt(participants.value))
            .then(dialog => {
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
        
        dialog.forEach((item, index) => {
            const dialogItem = document.createElement('div');
            dialogItem.className = 'dialog-item';
            
            const roleSpan = document.createElement('span');
            roleSpan.className = item.role;
            roleSpan.textContent = `${item.speaker}: `;
            
            const textSpan = document.createElement('span');
            textSpan.textContent = item.text;
            
            dialogItem.appendChild(roleSpan);
            dialogItem.appendChild(textSpan);
            dialogOutput.appendChild(dialogItem);
        });
        
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
            educational: '同学们好，今天我们来学习一个有趣的话题。',
            entertaining: '嘿，朋友们！准备好享受一段有趣的对话了吗？'
        };
        return openings[style] || openings.casual;
    }

    function getClosingByStyle(style) {
        const closings = {
            casual: '感谢大家的收听，我们下期再见！',
            professional: '以上就是本期的全部内容，谢谢收听。',
            educational: '希望今天的讲解对大家有所帮助。',
            entertaining: '今天的节目就到这里，保持微笑，下次见！'
        };
        return closings[style] || closings.casual;
    }
});