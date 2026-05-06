import streamlit as st
import requests
import base64
import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_VISION_API_KEY = os.getenv("GOOGLE_VISION_API_KEY", "")
SERP_API_KEY = os.getenv("SERP_API_KEY", "")

st.title("Outfit Finder")
st.write("Upload a clothing item and we'll find matching outfits for men!")

uploaded_file = st.file_uploader("Upload an image of your clothing item", type=["jpg", "jpeg", "png"])

if uploaded_file and st.button("Find Matching Outfits"):

    with st.spinner("Analyzing your clothing item..."):
        image_bytes = uploaded_file.read()
        image_b64 = base64.standard_b64encode(image_bytes).decode("utf-8")

        vision_url = f"https://vision.googleapis.com/v1/images:annotate?key={GOOGLE_VISION_API_KEY}"
        vision_payload = {
            "requests": [
                {
                    "image": {"content": image_b64},
                    "features": [
                        {"type": "LABEL_DETECTION", "maxResults": 10},
                        {"type": "IMAGE_PROPERTIES", "maxResults": 5},
                    ],
                }
            ]
        }

        vision_response = requests.post(vision_url, json=vision_payload)
        vision_data = vision_response.json()

        labels = vision_data["responses"][0].get("labelAnnotations", [])
        label_descriptions = [l["description"].lower() for l in labels]

        clothing_keywords = ["jeans", "shirt", "pants", "jacket", "dress", "shorts",
                             "coat", "sweater", "hoodie", "skirt", "suit", "trousers",
                             "blazer", "top", "chinos", "sneakers", "shoes", "boots"]
        detected_item = next((word for word in label_descriptions if word in clothing_keywords), None)

        if not detected_item:
            if "denim" in label_descriptions:
                detected_item = "jeans"
            else:
                detected_item = label_descriptions[0] if label_descriptions else "clothing item"

        colors = vision_data["responses"][0].get("imagePropertiesAnnotation", {}).get("dominantColors", {}).get("colors", [])
        detected_color = ""
        if colors:
            r = colors[0]["color"].get("red", 0)
            g = colors[0]["color"].get("green", 0)
            b = colors[0]["color"].get("blue", 0)

            if b > r and b > g:
                detected_color = "blue"
            elif r > g and r > b:
                detected_color = "red"
            elif g > r and g > b:
                detected_color = "green"
            elif r > 200 and g > 200 and b > 200:
                detected_color = "white"
            elif r < 60 and g < 60 and b < 60:
                detected_color = "black"
            elif r > 150 and g > 100 and b < 80:
                detected_color = "brown"
            else:
                detected_color = "grey"

        full_item = f"{detected_color} {detected_item}".strip()
        st.success(f"Detected item: **{full_item}**")

    with st.spinner("Searching for matching outfits..."):
        query = f"outfits that go with {full_item} for men"
        st.write(f"Searching for: _{query}_")

        params = {
            "engine": "google",
            "q": query,
            "tbm": "isch",
            "api_key": SERP_API_KEY,
        }
        search_response = requests.get("https://serpapi.com/search", params=params)
        results = search_response.json()

        image_results = results.get("images_results", [])
        if image_results:
            st.subheader("Matching Outfits")
            cols = st.columns(3)
            for i, item in enumerate(image_results[:9]):
                with cols[i % 3]:
                    if item.get("thumbnail"):
                        st.image(item["thumbnail"], use_container_width=True)
                    st.write(item.get("title", ""))
                    if item.get("link"):
                        st.markdown(f"[View source]({item['link']})")
        else:
            st.warning("No results found. Try a different image.")
            st.write("Raw response:", results)
