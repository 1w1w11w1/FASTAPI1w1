import os
import json
from typing import Dict, List, Optional, Tuple
from pathlib import Path

class TTSManager:
    def __init__(self):
        self.speakers = {
            "host": {
                "name": "主持人",
                "voice_id": "zh-CN-YunxiNeural",  # 微软Azure语音
                "style": "default"
            },
            "guest": {
                "name": "嘉宾",
                "voice_id": "zh-CN-YunjianNeural",  # 微软Azure语音
                "style": "default"
            },
            "guestA": {
                "name": "嘉宾A",
                "voice_id": "zh-CN-YunjianNeural",  # 微软Azure语音
                "style": "default"
            },
            "guestB": {
                "name": "嘉宾B",
                "voice_id": "zh-CN-YunxiaNeural",  # 微软Azure语音
                "style": "default"
            }
        }
        
        # 确保音频输出目录存在
        self.audio_output_dir = Path(__file__).parent.parent / "audio"
        self.audio_output_dir.mkdir(exist_ok=True)
    
    def generate_speech(self, text: str, speaker_id: str, audio_format: str = "mp3") -> Optional[str]:
        """
        生成语音文件
        :param text: 要转换的文本
        :param speaker_id: 说话人ID
        :param audio_format: 音频格式
        :return: 生成的音频文件路径
        """
        try:
            # 获取说话人配置
            speaker = self.speakers.get(speaker_id, self.speakers["host"])
            
            # 生成唯一的文件名
            import hashlib
            import time
            timestamp = int(time.time())
            text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
            filename = f"{speaker_id}_{text_hash}_{timestamp}.{audio_format}"
            output_path = self.audio_output_dir / filename
            
            # 这里是预留的API调用接口
            # 实际使用时，需要替换为真实的TTS API调用
            # 例如微软Azure TTS、百度语音、科大讯飞等
            
            # 模拟生成音频文件（实际实现时需要替换）
            with open(output_path, 'w') as f:
                f.write(f"{speaker['name']}: {text}")
            
            return str(output_path)
        except Exception as e:
            print(f"语音生成失败: {e}")
            return None
    
    def process_dialog(self, dialog: List[Dict]) -> List[Dict]:
        """
        处理对话，为每个对话生成语音
        :param dialog: 对话列表，每个元素包含role、speaker和text
        :return: 带语音文件路径的对话列表
        """
        processed_dialog = []
        
        for item in dialog:
            role = item.get("role", "host")
            speaker = item.get("speaker", "主持人")
            text = item.get("text", "")
            
            # 生成语音
            audio_path = self.generate_speech(text, role)
            
            # 添加到处理后的对话
            processed_item = {
                "role": role,
                "speaker": speaker,
                "text": text,
                "audio_path": audio_path
            }
            processed_dialog.append(processed_item)
        
        return processed_dialog
    
    def create_podcast(self, dialog: List[Dict], podcast_title: str) -> Optional[str]:
        """
        创建完整的播客节目
        :param dialog: 对话列表，每个元素包含role、speaker、text和audio_path
        :param podcast_title: 播客标题
        :return: 生成的播客文件路径
        """
        try:
            # 生成唯一的文件名
            import hashlib
            import time
            timestamp = int(time.time())
            title_hash = hashlib.md5(podcast_title.encode()).hexdigest()[:8]
            filename = f"podcast_{title_hash}_{timestamp}.json"
            output_path = self.audio_output_dir / filename
            
            # 保存播客信息
            podcast_info = {
                "title": podcast_title,
                "created_at": timestamp,
                "dialog": dialog
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(podcast_info, f, ensure_ascii=False, indent=2)
            
            return str(output_path)
        except Exception as e:
            print(f"播客创建失败: {e}")
            return None
    
    def get_speakers(self) -> Dict[str, Dict]:
        """
        获取可用的说话人列表
        :return: 说话人列表
        """
        return self.speakers
    
    def update_speaker(self, speaker_id: str, voice_id: str, style: str = "default") -> bool:
        """
        更新说话人配置
        :param speaker_id: 说话人ID
        :param voice_id: 语音ID
        :param style: 语音风格
        :return: 是否更新成功
        """
        try:
            if speaker_id in self.speakers:
                self.speakers[speaker_id]["voice_id"] = voice_id
                self.speakers[speaker_id]["style"] = style
                return True
            return False
        except Exception as e:
            print(f"说话人更新失败: {e}")
            return False

# 全局TTS管理器实例
tts_manager = TTSManager()