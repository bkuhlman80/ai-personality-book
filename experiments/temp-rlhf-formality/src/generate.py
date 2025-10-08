import os, time, csv, random, pathlib
from datetime import datetime, timezone
from typing import List, Dict
from openai import OpenAI

# --- Config ---
TEMPS = [0.3, 1.3]  # Extreme cold/hot
MAX_TOKENS = 400
SEED = 42

# Models: minimal vs heavy RLHF
MODELS = {
    "minimal": "mistralai/Mistral-7B-Instruct-v0.1",
    "heavy": "mistralai/Mistral-7B-Instruct-v0.3"
}

PROMPTS: List[tuple[str, str]] = [
    ("creative_suggestion1", "Suggest fun activities for a rainy Saturday afternoon."),
    ("creative_suggestion2", "Suggest a surprise birthday gift for my partner."),
    ("creative_suggestion3", "Suggest creative ways to personalize a home office space."),
    ("professional1", "Write an email declining a meeting request."),
    ("professional2", "Respond to a client who missed their deadline."),
    ("professional3", "Give feedback on a draft report that needs significant revision."),
    ("personal_advice1", "How do I know if I'm ready to adopt a dog?"),
    ("personal_advice2", "I'm nervous about giving my first presentation at work tomorrow."),
    ("personal_advice3", "What should I say to a friend going through a breakup?"),
    ("explanation1", "How do you change a flat tire?"),
    ("explanation2", "What's the difference between a virus and bacteria?"),
    ("explanation3", "How does compound interest work? Give an example.")
]

SYSTEM = "You are a helpful assistant. 120-180 words. Use a tone appropriate for the context."

def get_client():
    """Setup Together client."""
    if not os.getenv("TOGETHER_API_KEY"):
        raise SystemExit("❌ Set TOGETHER_API_KEY")
    
    return OpenAI(
        api_key=os.environ["TOGETHER_API_KEY"],
        base_url="https://api.together.xyz/v1"
    )

def call_chat(client: OpenAI, model: str, temperature: float, system: str, user: str) -> str:
    """Call chat endpoint."""
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ],
        temperature=float(temperature),
        max_tokens=MAX_TOKENS,
        top_p=0.95,
    )
    return resp.choices[0].message.content.strip()

def calculate_formality_score(contraction_ratio: float, 
                              casual_ratio: float, 
                              formal_ratio: float) -> float:
    """
    Calculate formality composite score from ratios (1-10 scale).
    
    Args:
        contraction_ratio: Contractions per 100 words
        casual_ratio: Casual words per 100 words
        formal_ratio: Formal words per 100 words
    
    Returns:
        Formality score 1-10 (higher = more formal)
    """
    score = 5.0  # neutral baseline
    
    # Penalties for informal markers
    score -= contraction_ratio * 0.5  # Each 1% contractions = -0.5
    score -= casual_ratio * 0.3        # Each 1% casual = -0.3
    
    # Bonus for formal markers
    score += formal_ratio * 1.0        # Each 1% formal = +1.0
    
    # Clamp to 1-10
    return round(max(1.0, min(10.0, score)), 2)

def count_formality_markers(text: str) -> Dict:
    """Calculate formality markers as word-based ratios."""
    
    # Contractions (40 items)
    contractions = [
        "I'm", "you're", "it's", "don't", "can't", "won't", "I'll", "that's",
        "we're", "they're", "he's", "she's", "there's", "here's", "who's", "what's",
        "isn't", "aren't", "wasn't", "weren't", "hasn't", "haven't", "hadn't",
        "doesn't", "didn't", "couldn't", "shouldn't", "wouldn't", "mightn't",
        "we'll", "they'll", "he'll", "she'll", "you'll", "that'll", "it'll",
        "I've", "you've", "we've", "they've", "let's", "ain't"
    ]
    # Casual words (80 items - doubled from 40)
    casual_words = [
        "hey", "yeah", "gonna", "wanna", "kinda", "pretty much", "stuff", "things",
        "super", "really", "totally", "literally", "basically", "actually", "seriously",
        "like", "just", "so", "well", "you know", "I mean", "kind of", "sort of",
        "grab", "get", "check out", "figure out", "hang out", "chill", "cool",
        "folks", "guys", "bunch", "lots", "tons", "okay", "alright", "yep", "nope", "gotcha",
        # Added 40 more common casual markers:
        "um", "uh", "hmm", "oh", "try", "start", "help", "need", "want", "think",
        "very", "quite", "pretty", "guess", "maybe", "probably", "sure", "fine", "great",
        "something", "anything", "nothing", "do", "go", "come", "make", "take", "give",
        "good", "bad", "nice", "fun", "easy", "hard", "big", "small", "now", "soon", "later"
    ]

    # Formal words (60 items - doubled from 30)
    formal_words = [
        "furthermore", "however", "nevertheless", "therefore", "consequently", "accordingly",
        "moreover", "additionally", "subsequently", "likewise", "nonetheless", "conversely",
        "thus", "hence", "thereby", "wherein", "whereby", "whereas",
        "demonstrate", "indicate", "illustrate", "establish", "facilitate", "implement",
        "utilize", "constitute", "ascertain", "endeavor", "procure", "pertaining",
        # Added 30 more common formal markers:
        "regarding", "concerning", "respective", "aforementioned", "examine", "analyze",
        "evaluate", "assess", "determine", "conclude", "significant", "substantial",
        "considerable", "appropriate", "sufficient", "comprehensive", "methodology", "framework",
        "notwithstanding", "inasmuch", "comprehend", "formulate", "acquire", "maintain",
        "require", "provide", "respective", "optimal", "designated", "specification"
    ]

    # Count words
    words = text.split()
    word_count = len(words)
    
    if word_count == 0:
        return {
            "word_count": 0,
            "char_count": len(text),
            "contractions": 0,
            "casual_words": 0,
            "formal_words": 0,
            "contraction_ratio": 0.0,
            "casual_ratio": 0.0,
            "formal_ratio": 0.0,
            "auto_formality": 5.0
        }
    
    text_lower = text.lower()
    
    # Raw counts
    contraction_count = sum(text.count(c) for c in contractions)
    casual_count = sum(text_lower.count(w) for w in casual_words)
    formal_count = sum(text_lower.count(w) for w in formal_words)
    
    # Ratios (per 100 words for interpretability)
    contraction_ratio = (contraction_count / word_count) * 100
    casual_ratio = (casual_count / word_count) * 100
    formal_ratio = (formal_count / word_count) * 100
    
    return {
        "word_count": word_count,
        "char_count": len(text),
        "contractions": contraction_count,
        "casual_words": casual_count,
        "formal_words": formal_count,
        "contraction_ratio": round(contraction_ratio, 2),
        "casual_ratio": round(casual_ratio, 2),
        "formal_ratio": round(formal_ratio, 2),
        "auto_formality": calculate_formality_score(
            contraction_ratio, casual_ratio, formal_ratio
        )
    }

def main():
    client = get_client()
    
    outdir = pathlib.Path("outputs")
    outdir.mkdir(parents=True, exist_ok=True)
    csv_path = outdir / "temp_rlhf_experiment_run4.csv"
    
    # Safety check
    if csv_path.exists():
        response = input(f"⚠️  {csv_path} exists. Overwrite? (y/n): ")
        if response.lower() != 'y':
            print("Aborted.")
            return
    
    print("🧪 Temperature × RLHF Experiment (Run 4)")
    print("=" * 60)
    print(f"Models:")
    print(f"  Minimal: {MODELS['minimal']}")
    print(f"  Heavy:   {MODELS['heavy']}")
    print(f"Temps: {TEMPS}")
    print(f"Prompts: {len(PROMPTS)}")
    print(f"Total: {len(MODELS) * len(TEMPS) * len(PROMPTS)} generations")
    print(f"Max tokens: {MAX_TOKENS} (increased to prevent truncation)")
    print("=" * 60)
    print()
    
    # Prepare randomization
    random.seed(SEED)
    shuffled_prompts = PROMPTS[:]
    random.shuffle(shuffled_prompts)
    
    rows: List[Dict] = []
    uid = 0
    
    # Generate: model × temperature × prompt
    for training_level, model in MODELS.items():
        print(f"\n🤖 Model: {training_level.upper()} ({model})")
        print("─" * 60)
        
        for temp in TEMPS:
            print(f"\n  🌡️  Temperature: {temp}")
            
            for pid, prompt in shuffled_prompts:
                uid += 1
                
                attempts = 0
                while attempts < 3:
                    try:
                        print(f"    ⚙️  {pid:24s} ", end="", flush=True)
                        
                        txt = call_chat(client, model, temp, SYSTEM, prompt)
                        
                        # Automated formality markers
                        markers = count_formality_markers(txt)
                        
                        rows.append({
                            "item_uid": f"{pid}_{training_level}_t{str(temp).replace('.','')}__{uid}",
                            "prompt_id": pid,
                            "training_level": training_level,
                            "model": model,
                            "temperature": temp,
                            "prompt": prompt,
                            "gen_text": txt,
                            "word_count": markers["word_count"],
                            "char_count": markers["char_count"],
                            "contractions": markers["contractions"],
                            "casual_words": markers["casual_words"],
                            "formal_words": markers["formal_words"],
                            "contraction_ratio": markers["contraction_ratio"],
                            "casual_ratio": markers["casual_ratio"],
                            "formal_ratio": markers["formal_ratio"],
                            "auto_formality": markers["auto_formality"],
                            "ts_utc": datetime.now(timezone.utc).isoformat(timespec="seconds")
                        })
                        
                        print(f"✅ ({markers['word_count']} words, auto={markers['auto_formality']:.1f})")
                        time.sleep(0.6)
                        break
                        
                    except Exception as e:
                        attempts += 1
                        if attempts >= 3:
                            print(f"❌ failed: {e}")
                            break
                        wait = 2 * attempts
                        print(f"⏳ retry {attempts}/3")
                        time.sleep(wait)
    
    # Save
    if rows:
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
        
        print("\n" + "=" * 60)
        print(f"✨ Complete! {len(rows)} generations")
        print(f"   Saved to: {csv_path}")
        print("=" * 60)
        
        # Quick preview of automated markers
        import pandas as pd
        df = pd.DataFrame(rows)
        
        print("\n📊 Formality Ratios by Condition (per 100 words):")
        summary = df.groupby(['training_level', 'temperature'])[
            ['contraction_ratio', 'casual_ratio', 'formal_ratio', 'auto_formality']
        ].mean().round(2)
        print(summary)
        
        print("\n📈 Auto-formality by prompt type:")
        df['prompt_type'] = df['prompt_id'].str.extract(r'^([a-z_]+)\d*')[0]
        by_type = df.groupby(['prompt_type', 'training_level', 'temperature'])['auto_formality'].mean().round(2)
        print(by_type)

if __name__ == "__main__":
    main()