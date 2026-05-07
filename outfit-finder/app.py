import streamlit as st
import requests
import base64
import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_VISION_API_KEY = os.getenv("GOOGLE_VISION_API_KEY", "")
SERP_API_KEY = os.getenv("SERP_API_KEY", "")

def rgb_to_name(r, g, b):
    if r < 60 and g < 60 and b < 60:
        return "black"
    elif r > 200 and g > 200 and b > 200:
        return "white"
    elif b > r and b > g:
        return "blue"
    elif r > g and r > b:
        return "red"
    elif g > r and g > b:
        return "green"
    elif r > 150 and g > 100 and b < 80:
        return "brown"
    elif r > 180 and g > 140 and b < 100:
        return "tan"
    elif r > 150 and g > 150 and b < 100:
        return "yellow"
    elif r > 150 and b > 150 and g < 100:
        return "purple"
    elif r > 180 and g > 180 and b > 180:
        return "grey"
    else:
        return "grey"

st.title("Outfit Finder")
st.write("Upload a clothing item and find matching outfits or accessories!")

uploaded_file = st.file_uploader("Upload an image of your clothing item", type=["jpg", "jpeg", "png"])

if uploaded_file:

    # Step 1 — Gender
    st.write("**Step 1: Who is this for?**")
    col1, col2 = st.columns(2)
    with col1:
        btn_men = st.button("👨 Men", use_container_width=True)
    with col2:
        btn_women = st.button("👩 Women", use_container_width=True)

    if btn_men:
        st.session_state.gender = "men"
    elif btn_women:
        st.session_state.gender = "women"

    gender = st.session_state.get("gender")

    if gender:
        st.success(f"Selected: **{gender.capitalize()}**")

        # Step 2 — Search type
        st.write("**Step 2: What are you looking for?**")
        col3, col4 = st.columns(2)
        with col3:
            btn_outfits = st.button("👔 Matching Outfits", use_container_width=True, type="primary")
        with col4:
            btn_accessories = st.button("👜 Matching Accessories", use_container_width=True, type="primary")

        if btn_outfits:
            search_type = "Matching Outfits"
        elif btn_accessories:
            search_type = "Matching Accessories"
        else:
            search_type = None

        if search_type:

            with st.spinner("Analyzing your clothing item..."):
                image_bytes = uploaded_file.read()
                image_b64 = base64.standard_b64encode(image_bytes).decode("utf-8")

                vision_url = f"https://vision.googleapis.com/v1/images:annotate?key={GOOGLE_VISION_API_KEY}"
                vision_payload = {
                    "requests": [{
                        "image": {"content": image_b64},
                        "features": [
                            {"type": "LABEL_DETECTION", "maxResults": 10},
                            {"type": "IMAGE_PROPERTIES", "maxResults": 10},
                        ],
                    }]
                }

                vision_response = requests.post(vision_url, json=vision_payload)
                vision_data = vision_response.json()

                labels = vision_data["responses"][0].get("labelAnnotations", [])
                label_descriptions = [l["description"].lower() for l in labels]

                # Clothing type detection
                label_map = {
                    "jeans": "jeans", "denim": "jeans", "cargo pants": "cargo pants",
                    "pants": "pants", "trousers": "trousers", "chinos": "chinos",
                    "shorts": "shorts", "joggers": "joggers", "sweatpants": "sweatpants",
                    "track pants": "track pants", "dress pants": "dress pants",
                    "shirt": "shirt", "t-shirt": "t-shirt", "dress shirt": "dress shirt",
                    "polo shirt": "polo shirt", "polo": "polo shirt", "henley": "henley shirt",
                    "flannel": "flannel shirt", "oxford shirt": "oxford shirt",
                    "button-up shirt": "button-up shirt", "linen shirt": "linen shirt",
                    "turtleneck": "turtleneck", "tank top": "tank top", "vest": "vest",
                    "top": "top", "active shirt": "shirt",
                    "jacket": "jacket", "outerwear": "jacket", "coat": "coat",
                    "blazer": "blazer", "suit": "suit", "overcoat": "overcoat",
                    "trench coat": "trench coat", "puffer jacket": "puffer jacket",
                    "bomber jacket": "bomber jacket", "denim jacket": "denim jacket",
                    "leather jacket": "leather jacket", "windbreaker": "windbreaker",
                    "sweater": "sweater", "hoodie": "hoodie", "sweatshirt": "sweatshirt",
                    "cardigan": "cardigan", "knitwear": "knit sweater", "pullover": "pullover",
                    "shoes": "shoes", "sneakers": "sneakers", "boots": "boots",
                    "footwear": "sneakers", "athletic shoe": "sneakers",
                    "loafers": "loafers", "dress shoes": "dress shoes", "sandals": "sandals",
                    "activewear": "activewear", "sportswear": "sportswear",
                    "dress": "dress", "skirt": "skirt", "leggings": "leggings",
                    "blouse": "blouse", "crop top": "crop top", "jumpsuit": "jumpsuit",
                    "tuxedo": "tuxedo", "waistcoat": "waistcoat",
                }

                detected_item = None
                for label in label_descriptions:
                    if label in label_map:
                        detected_item = label_map[label]
                        break
                if not detected_item:
                    detected_item = label_descriptions[0] if label_descriptions else "clothing item"

                # Color detection — pick top 3 dominant colors with >10% pixel coverage
                raw_colors = (
                    vision_data["responses"][0]
                    .get("imagePropertiesAnnotation", {})
                    .get("dominantColors", {})
                    .get("colors", [])
                )

                color_names = []
                for c in raw_colors[:6]:
                    frac = c.get("pixelFraction", 0)
                    if frac < 0.08:
                        continue
                    r = c["color"].get("red", 0)
                    g = c["color"].get("green", 0)
                    b = c["color"].get("blue", 0)
                    name = rgb_to_name(r, g, b)
                    if name not in color_names:
                        color_names.append(name)
                    if len(color_names) == 2:
                        break

                if len(color_names) >= 2:
                    color_str = f"{color_names[0]} and {color_names[1]}"
                elif color_names:
                    color_str = color_names[0]
                else:
                    color_str = ""

                full_item = f"{color_str} {detected_item}".strip()
                st.success(f"Detected item: **{full_item}**")

            with st.spinner("Searching..."):
                if search_type == "Matching Outfits":
                    query = f"outfits that go with {full_item} for {gender}"
                else:
                    query = f"accessories that go with {full_item} for {gender}"
                st.write(f"Searching for: _{query}_")

                params = {
                    "engine": "google",
                    "q": query,
                    "tbm": "isch",
                    "num": "50",
                    "api_key": SERP_API_KEY,
                }
                search_response = requests.get("https://serpapi.com/search", params=params)
                results = search_response.json()

                image_results = results.get("images_results", [])
                if image_results:
                    st.subheader(f"{search_type} for {gender.capitalize()}")
                    cols = st.columns(4)
                    for i, item_result in enumerate(image_results[:50]):
                        with cols[i % 4]:
                            img_url = item_result.get("original") or item_result.get("thumbnail")
                            if img_url:
                                st.image(img_url, use_container_width=True)
                            st.write(item_result.get("title", ""))
                            if item_result.get("link"):
                                st.markdown(f"[View source]({item_result['link']})")
                else:
                    st.warning("No results found. Try a different image.")
                    st.write("Raw response:", results)
