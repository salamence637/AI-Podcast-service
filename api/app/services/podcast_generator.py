import re
import openai
from app.core import config

# 设置 API Key
openai.api_key = config.OPENAI_API_KEY
client = openai.OpenAI(api_key=config.OPENAI_API_KEY)

def detect_language(text: str) -> str:
    """
    简单判断文本语言：
    - 包含日文平假名或片假名返回 'jp'
    - 包含中文字符返回 'zh'
    - 否则返回 'en'
    """
    if re.search(r'[\u3040-\u30ff]', text):
        return 'jp'
    elif re.search(r'[\u4e00-\u9fff]', text):
        return 'zh'
    else:
        return 'en'

def generate_podcast_text(topic: str) -> str:
    """
    生成一段播客对话：
    - 自动检测话题语言
    - 生成一段一男一女嘉宾（例如：男主播志明、女主播春娇）的轻松幽默对话，
      并体现 Chain-of-Thought 思维链，时长约5分钟（1500 tokens左右）
    """
    lang = detect_language(topic)
    if lang == 'zh':
        system_message = (
            "你是一个非常有创意且轻松愉快的AI播客生成器。"
            "你的任务是生成一段由两位30岁以下的主播对话，两人均采用京腔风格、2025年年轻人的口语交流。"
            "请使用Chain-of-Thought思维链生成一段约5分钟的对话，内容可以富有创意、异想天开，甚至跑题，不一定有明确结论。"
        )
        user_message = (
            f"请生成一段对话，要求是两个主播之间的对话（例如：男主播小明和女主播小红），"
            f"讨论以下话题：{topic}\n\n"
            "要求：\n"
            "1. 每个对话步骤展现出逻辑推理和Chain-of-Thought思维链；\n"
            "2. 内容结构清晰，但允许自由发挥、异想天开、甚至跑题；\n"
            "3. 语言风格要贴近2025年年轻人的口语，并带有京腔特色；\n"
            "4. 对话全长约1分钟（大约300 tokens左右）。"
        )
    elif lang == 'jp':
        system_message = (
            "あなたは非常に創造的でリラックスしたAIポッドキャストジェネレーターです。"
            "あなたのタスクは、30歳未満の2人のパーソナリティが、2025年の若者らしい口調で会話する対話を生成することです。"
            "Chain-of-Thoughtプロセスを用いて、約5分間の会話を生成してください。"
            "会話は自由奔放で、斬新なアイディアや予想外の展開を含んでも構いません。"
        )
        user_message = (
            f"以下のトピックについて、2人のパーソナリティ（例：男性パーソナリティ太郎、女性パーソナリティ花子）が会話する対話を生成してください：{topic}\n\n"
            "要件：\n"
            "1. 各会話ステップで論理的な推論とChain-of-Thoughtプロセスを示す；\n"
            "2. 内容は明確な構造を持ちながらも、自由な発想や突拍子もない展開を含む；\n"
            "3. 出力言語は日本語（標準語）で、2025年の若者らしい口調を反映する；\n"
            "4. 全体の対話は約1分間（約300 tokens）を目指す。"
        )
    else:
        system_message = (
            "You are a highly creative and relaxed AI podcast generator. "
            "Your task is to generate a dialogue between two hosts, both under 30 years old, using American conversational style typical of young people in 2025. "
            "Use a chain-of-thought process to generate approximately 5 minutes of dialogue. "
            "The conversation can be imaginative, free-form, and even off-topic without a definite conclusion."
        )
        user_message = (
            f"Generate a dialogue between two hosts (e.g., male host John and female host Jane) discussing the following topic: {topic}\n\n"
            "Requirements:\n"
            "1. Each dialogue step should show logical reasoning and a chain-of-thought process;\n"
            "2. The content should have a clear structure but allow for free, imaginative, and even off-topic ideas;\n"
            "3. Use American conversational style typical of young people in 2025;\n"
            "4. The entire dialogue should last about 1 minutes (approximately 300 tokens)."
        )
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message}
    ]
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=1500,
        temperature=0.7,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )
    return response.choices[0].message.content.strip()
