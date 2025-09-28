#!/usr/bin/env python3
"""
生成测试音频文件
用于STT功能测试
"""

import numpy as np
import wave
import os

def generate_test_audio(text="你好，这是语音识别测试", filename="test_audio.wav", duration=3):
    """
    生成测试音频文件
    
    Args:
        text: 要合成的文本（仅用于文件名）
        filename: 输出文件名
        duration: 音频时长（秒）
    """
    print(f"🎵 生成测试音频: {filename}")
    
    # 音频参数
    sample_rate = 16000  # 16kHz采样率
    frequency = 440  # 440Hz频率（A4音符）
    
    # 生成正弦波
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    audio_data = np.sin(2 * np.pi * frequency * t)
    
    # 添加一些变化，模拟语音
    audio_data += 0.3 * np.sin(2 * np.pi * frequency * 2 * t)  # 谐波
    audio_data += 0.1 * np.random.normal(0, 1, len(audio_data))  # 噪声
    
    # 归一化
    audio_data = audio_data / np.max(np.abs(audio_data))
    
    # 转换为16位整数
    audio_data = (audio_data * 32767).astype(np.int16)
    
    # 保存为WAV文件
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)  # 单声道
        wav_file.setsampwidth(2)  # 16位
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_data.tobytes())
    
    print(f"✅ 音频文件已生成: {filename}")
    print(f"   时长: {duration}秒")
    print(f"   采样率: {sample_rate}Hz")
    print(f"   格式: WAV (16位单声道)")

def generate_multiple_test_files():
    """生成多个测试音频文件"""
    test_cases = [
        ("你好，这是语音识别测试", "test_hello.wav", 2),
        ("我是哈利波特，很高兴认识你", "test_harry.wav", 3),
        ("夏洛克福尔摩斯，有什么案件需要我帮助吗", "test_sherlock.wav", 4),
        ("苏格拉底，让我们探讨哲学问题", "test_socrates.wav", 3),
    ]
    
    print("🎵 生成多个测试音频文件")
    print("=" * 50)
    
    for text, filename, duration in test_cases:
        generate_test_audio(text, filename, duration)
        print()
    
    print("✅ 所有测试音频文件已生成！")
    print("\n📁 生成的文件:")
    for _, filename, _ in test_cases:
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            print(f"   {filename} ({size} bytes)")

def main():
    """主函数"""
    print("🎵 测试音频文件生成器")
    print("=" * 50)
    
    # 生成单个测试文件
    generate_test_audio()
    print()
    
    # 生成多个测试文件
    generate_multiple_test_files()
    
    print("\n🎉 音频文件生成完成！")
    print("\n💡 使用说明:")
    print("   1. 使用生成的音频文件测试STT功能")
    print("   2. 运行: python test_voice.py test_hello.wav")
    print("   3. 或者直接运行: python test_voice.py")

if __name__ == "__main__":
    main()
