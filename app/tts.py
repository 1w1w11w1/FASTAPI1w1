import os
import json
import uuid
import httpx
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from dotenv import load_dotenv

# 获取日志记录器
logger = logging.getLogger(__name__)

class TTSManager:
    def __init__(self):
        # 加载环境变量
        load_dotenv()
        
        # 千问TTS配置
        self.dashscope_api_key = os.getenv("DASHSCOPE_API_KEY")
        # 修正TTS API端点URL
        self.dashscope_tts_endpoint = "https://dashscope.aliyuncs.com/api/v1/services/audio/speech_synthesis"
        
        # 说话人配置（使用千问TTS支持的音色）
        self.speakers = {
            "host": {
                "name": "主持人",
                "voice_id": "zh_female_qingxin",  # 千问语音合成模型
                "style": "default"
            },
            "guest": {
                "name": "嘉宾",
                "voice_id": "zh_male_zhichang",  # 千问语音合成模型
                "style": "default"
            },
            "guestA": {
                "name": "嘉宾A",
                "voice_id": "zh_male_zhichang",  # 千问语音合成模型
                "style": "default"
            },
            "guestB": {
                "name": "嘉宾B",
                "voice_id": "zh_female_youth",  # 千问语音合成模型
                "style": "default"
            }
        }
        
        # 确保音频输出目录存在
        self.audio_output_dir = Path(__file__).parent.parent / "audio"
        self.audio_output_dir.mkdir(exist_ok=True)
        
        logger.info("TTSManager初始化完成")
        logger.info(f"千问API密钥存在: {self.dashscope_api_key is not None}")
        logger.info(f"TTS API端点: {self.dashscope_tts_endpoint}")
    
    def generate_speech(self, text: str, speaker_id: str, audio_format: str = "mp3") -> Optional[str]:
        """
        生成语音文件
        :param text: 要转换的文本
        :param speaker_id: 说话人ID
        :param audio_format: 音频格式
        :return: 生成的音频文件路径
        """
        try:
            # 检查配置是否齐全
            if not self.dashscope_api_key:
                logger.error("千问TTS配置不完整，请在.env文件中设置DASHSCOPE_API_KEY")
                return None
            
            # 获取说话人配置
            speaker = self.speakers.get(speaker_id, self.speakers["host"])
            
            # 生成唯一的文件名
            import hashlib
            import time
            timestamp = int(time.time())
            text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
            filename = f"{speaker_id}_{text_hash}_{timestamp}.{audio_format}"
            output_path = self.audio_output_dir / filename
            
            # 构建请求参数
            request_data = {
                "model": "sambert-zh-general-v2",  # 千问语音合成模型
                "input": {
                    "text": text
                },
                "parameters": {
                    "voice": speaker["voice_id"],
                    "format": audio_format,
                    "sample_rate": 24000,
                    "speed": 1.0,
                    "pitch": 1.0,
                    "volume": 1.0
                }
            }
            
            # 构建请求头
            headers = {
                "Authorization": f"Bearer {self.dashscope_api_key}",
                "Content-Type": "application/json"
            }
            
            # 调用千问TTS API
            logger.info("调用千问TTS API生成语音...")
            logger.info(f"文本长度: {len(text)}, 前50个字符: {text[:50]}...")
            logger.info(f"说话人: {speaker['name']} ({speaker['voice_id']})")
            logger.info(f"请求URL: {self.dashscope_tts_endpoint}")
            logger.info(f"请求参数: {json.dumps(request_data, ensure_ascii=False)[:200]}...")
            
            with httpx.Client() as client:
                response = client.post(
                    self.dashscope_tts_endpoint,
                    json=request_data,
                    headers=headers,
                    timeout=30.0
                )
                
                # 检查响应状态
                logger.info(f"TTS API响应状态码: {response.status_code}")
                logger.info(f"TTS API响应文本: {response.text[:200]}...")
                
                if response.status_code == 200:
                    # 解析响应
                    response_data = response.json()
                    logger.info(f"TTS API响应数据: {json.dumps(response_data, ensure_ascii=False)[:200]}...")
                    
                    if response_data.get("status_code") == 200:
                        # 获取音频数据
                        audio_data = response_data.get("result", {}).get("audio_data")
                        if audio_data:
                            # 解码base64音频数据
                            import base64
                            audio_bytes = base64.b64decode(audio_data)
                            # 保存音频数据
                            with open(output_path, 'wb') as f:
                                f.write(audio_bytes)
                            logger.info(f"语音生成成功: {output_path}")
                            return str(output_path)
                        else:
                            logger.error("语音生成失败: 未返回音频数据")
                            return None
                    else:
                        logger.error(f"语音生成失败: {response_data.get('status_message', '未知错误')}")
                        return None
                else:
                    logger.error(f"语音生成失败，状态码: {response.status_code}")
                    logger.error(f"错误信息: {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"语音生成失败: {e}")
            import traceback
            logger.error(f"详细错误信息: {traceback.format_exc()}")
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
        
        logger.info(f"对话处理完成，共处理 {len(processed_dialog)} 个对话")
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
            
            logger.info(f"播客创建成功: {output_path}")
            return str(output_path)
        except Exception as e:
            logger.error(f"播客创建失败: {e}")
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
                logger.info(f"说话人 {speaker_id} 更新成功: {voice_id}, {style}")
                return True
            logger.warning(f"说话人 {speaker_id} 不存在")
            return False
        except Exception as e:
            logger.error(f"说话人更新失败: {e}")
            return False

# 全局TTS管理器实例
tts_manager = TTSManager()