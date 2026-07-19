import os
import json

K = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app", "knowledge")

def clean(f, key_fn):
    p = os.path.join(K, f)
    if not os.path.exists(p):
        return
    with open(p, "r", encoding="utf-8") as f_in:
        data = json.load(f_in)
    seen, res = set(), []
    for x in data:
        k = key_fn(x)
        if k not in seen:
            seen.add(k)
            res.append(x)
    with open(p, "w", encoding="utf-8") as f_out:
        json.dump(res, f_out, indent=2, ensure_ascii=False)
    print(f"Cleaned {f}, remaining: {len(res)}")

if __name__ == "__main__":
    clean("ingredients.json", lambda x: x.get("ingredient_id", "").strip())
    clean("safety.json", lambda x: x.get("ingredient", "").strip().lower())
    clean("pairing.json", lambda x: x.get("ingredient", "").strip().lower())
    clean("suppliers.json", lambda x: (x.get("supplier_name", "").strip().lower(), x.get("ingredient", "").strip().lower()))
    clean("chef_notes.json", lambda x: (x.get("recipe", "").strip().lower(), x.get("tip", "").strip().lower()))
    print("Database cleaned successfully!")
