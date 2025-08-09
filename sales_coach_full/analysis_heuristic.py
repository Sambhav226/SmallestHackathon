# This file contains the previous heuristic analysis implementation.
import statistics, random
FEATURE_KEYWORDS = ["battery","range","mAh","watt","hp","cc","km","mph","speed","memory","ram","gb","processor","cpu","benchmark"]
OBJECTION_KEYWORDS = ["not sure","i'll think","maybe","too expensive","expensive","too high","no thanks","not convinced","don't know"]

def contains_empathy(s):
    return any(w in s.lower() for w in ["understand", "totally", "i get", "i see", "sounds like", "sorry to hear"])

def rewrite_rep_message(msg):
    msg = msg.strip()
    if len(msg.split()) <= 3:
        return f"I understand — that's a valid concern. One thing that helps is that this product {mock_benefit_phrase()}. Would that address your concern?"
    else:
        return f"I hear you. To be clear: {msg}. Would you like me to arrange a demo or send a comparison?"

def mock_benefit_phrase():
    options = [
        "offers a 2-year warranty and a free trial",
        "delivers 20% better battery life than our competitor",
        "comes with complimentary on-site setup and training",
        "has a 30-day money-back guarantee",
    ]
    return random.choice(options)

def analyze_conversation_heuristic(messages):
    rep_texts = [m["text"] for m in messages if m["role"] in ("rep","sales","agent_rep")]
    cust_texts = [m["text"] for m in messages if m["role"] in ("customer","agent","persona")]
    full_transcript = "\n".join([f"{m['role']}: {m['text']}" for m in messages])

    rep_lengths = [len(t.split()) for t in rep_texts] or [0]
    cust_lengths = [len(t.split()) for t in cust_texts] or [0]
    avg_rep = statistics.mean(rep_lengths) if rep_lengths else 0
    avg_cust = statistics.mean(cust_lengths) if cust_lengths else 0
    rapport_score = max(1, min(10, int(10 * (0.5 + 0.5*(1 - (avg_rep/(avg_cust+1))) ) )))
    if any(contains_empathy(t) for t in rep_texts):
        rapport_score = min(10, rapport_score + 1)

    pk_count = sum(1 for t in rep_texts for kw in FEATURE_KEYWORDS if kw.lower() in t.lower())
    product_knowledge_score = min(10, 3 + pk_count*2)

    objection_count = sum(1 for t in cust_texts for kw in OBJECTION_KEYWORDS if kw in t.lower())
    rep_resolution_terms = ["discount","warranty","guarantee","trial","return","demo","save","promo","price match"]
    rep_handling_count = sum(1 for t in rep_texts for kw in rep_resolution_terms if kw in t.lower())
    if objection_count == 0:
        objection_handling_score = 8 + min(2, rep_handling_count)
    else:
        ratio = min(1.0, rep_handling_count / (objection_count+0.001))
        objection_handling_score = max(1, int(10 * ratio))

    closing_phrases = ["would you like","shall we","can i","ready to","how about we","book a test","sign up","purchase now","order now"]
    close_attempts = sum(1 for t in rep_texts for p in closing_phrases if p in t.lower())
    closing_score = min(10, 2 + close_attempts*3)

    improvements = []
    if not any(contains_empathy(t) for t in rep_texts):
        improvements.append({"tip": "Use brief empathy statements early", "why": "Empathy builds trust and raises willingness to share info."})
    if product_knowledge_score < 6:
        improvements.append({"tip": "Share one clear product fact and one benefit per objection", "why": "Customers need specific facts to evaluate high-value purchases."})
    if objection_count > 0 and rep_handling_count == 0:
        improvements.append({"tip": "Address objections with concrete offers (warranty/trial/discount)", "why": "Concrete options reduce perceived risk."})
    if close_attempts == 0:
        improvements.append({"tip": "Try a soft close within 2-3 exchanges", "why": "Soft closes test buying signals without being pushy."})
    improvements.append({"tip": "Be concise and ask open questions", "why": "Short, targeted questions guide customers to reveal buying intent."})

    missed_facts = []
    for t in cust_texts:
        if "what is the" in t.lower() or "how many" in t.lower() or any(kw in t.lower() for kw in FEATURE_KEYWORDS):
            found = any(kw in " ".join(rep_texts).lower() for kw in FEATURE_KEYWORDS)
            if not found:
                missed_facts.append(t)

    candidate_msgs = sorted(rep_texts, key=lambda s: len(s.split()))[:3]
    rewrites = []
    for msg in candidate_msgs:
        rewrites.append({"original": msg, "rewrite": rewrite_rep_message(msg)})

    coaching = {
        "scores": {
            "rapport": rapport_score,
            "objection_handling": objection_handling_score,
            "product_knowledge": product_knowledge_score,
            "closing": closing_score
        },
        "improvements": improvements[:5],
        "missed_facts_examples": list(dict.fromkeys(missed_facts))[:10],
        "rewrites": rewrites,
        "transcript": full_transcript
    }
    return coaching
