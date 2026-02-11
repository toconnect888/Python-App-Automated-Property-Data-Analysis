import time
import requests
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from playwright.sync_api import sync_playwright
import csv
import os
from PIL import Image
import folium
import io
import base64
from reportlab.lib.pagesizes import letter
# excel first three coloumns must be: No, Address, City
page_width, page_height = letter  #page_width 612 points , page_height 792 points
bottom_margin = 60          # 60 points margin at bottom

CACHE_FILE = "geocode_cache.csv"
margin = 50           # 50 points margin to left and right of letter size

image_width = int((page_width - 2 * margin) / 72 * 300 )       #2133 pixels, image width that fits well in pdf 
image_height = int(page_height / 72 * 300 * 0.45)           #1485 pixels , image height that fits well in pdf 
map_scale= 1  # scale factor for the real folium map size
viewpoint_scale= 1  # scale factor for viewport size

map_width = int(image_width * map_scale)      #2133 * map_scale pixels, folium  map size , larger than image size to allow for cropping 
map_height = int(image_height * map_scale)     #1485 *map_scale  pixels , folium amap size height

width_px = int(image_width * viewpoint_scale)      #viewpoint width in pixels 
height_px = int(image_height * viewpoint_scale)    #viewpoint height in pixels 

print(f"Acual Folium Map size: {map_width} x {map_height} pixels, viewpoint size: {width_px} x {height_px} pixels")
def load_cache():
    cache = {}
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                cache[row["address"]] = (float(row["lat"]), float(row["lon"]))
    return cache

def save_to_cache(address, lat, lon):
    file_exists = os.path.exists(CACHE_FILE)
    with open(CACHE_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["address", "lat", "lon"])
        if not file_exists:
            writer.writeheader()
        writer.writerow({"address": address, "lat": lat, "lon": lon})

GEOAPIFY_API_KEY = "65f96b6f18dc4d42a7ed0f26e5d5e6e6"
nominatim = Nominatim(user_agent="numbered_map", timeout=15)

def geoapify_geocode(address):
    url = "https://api.geoapify.com/v1/geocode/search"
    params = {"text": address, "limit": 1, "apiKey": GEOAPIFY_API_KEY}
    r = requests.get(url, params=params, timeout=15)
    r.raise_for_status()
    data = r.json()
    if data["features"]:
        lon, lat = data["features"][0]["geometry"]["coordinates"]
        return lat, lon
    return None

def geocode_with_fallback(address):
    # Try Geoapify first
    try:
        coords = geoapify_geocode(address)
        if coords:
            return coords
    except Exception as e:
        print(f"Geoapify failed for {address}: {e}")

    # Fallback to Nominatim
    try:
        loc = nominatim.geocode(address)
        if loc:
            return loc.latitude, loc.longitude
    except (GeocoderTimedOut, GeocoderServiceError) as e:
        print(f"Nominatim failed for {address}: {e}")

    return None

def html_to_png(html_file, output_png, width_px, height_px):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": width_px, "height": height_px})   ##The viewport is the “size of the browser window”, in pixcels
        page.goto(f"file:///{os.path.abspath(html_file)}")
        page.wait_for_timeout(3000)  # wait for tiles to load

        page.evaluate(f"""
        () => {{
             // Hide legend
            const legend = document.querySelector('.custom-legend');
            if (legend) {{
                legend.style.display = 'none';
            }}
            const map = document.querySelector('div.folium-map');
            if (map) {{
                map.style.width = '{width_px}px';
                map.style.height = '{height_px}px';
            }}

            // Force Leaflet to re-render after resize
            if (window._leaflet_map) {{
                window._leaflet_map.invalidateSize();
            }}
        }}
        """)

        element = page.query_selector("div.folium-map")
        if element:
            element.screenshot(path=output_png)
            print(f"High-res screenshot saved to {output_png}")
        else:
            # fallback: full page screenshot
            page.screenshot(path=output_png, full_page=True)
            print(f"No map div found. Full-page screenshot saved to {output_png}")

        # page.screenshot(path=output_png, full_page=True)
        browser.close()

def scale_image_to_pdf(input_png, output_png):
    img = Image.open(input_png)
    img = img.resize((image_width, image_height), Image.LANCZOS)
    img.save(output_png)

def create_image(summary_df, output_png):
    cache = load_cache()
    locations = []
    for _, row in summary_df.iterrows():
        address = f"{row['Address']},{row['City']}, Ontario, Canada"
        num = row["No"]

        if address in cache:
            lat, lon = cache[address]
        else:
            coords = geocode_with_fallback(address)
            if not coords:
                print(f"Skipping address: {address}")
                continue
            lat, lon = coords
            save_to_cache(address, lat, lon)
            time.sleep(0.8)  # safe free-tier pacing

        locations.append((lat, lon, num, address))

    if not locations:
        raise ValueError("No valid locations geocoded.")

    avg_lat = sum(x[0] for x in locations) / len(locations)
    avg_lon = sum(x[1] for x in locations) / len(locations)

    m = folium.Map(location=[avg_lat, avg_lon],tiles= "CartoDB positron", width= '50%', height= '50%', zoom_start=18)  
    # map style, Esri WorldStreetMap , OpenStreetMap , CartoDB positron      
    for lat, lon, num, addr in locations:
        folium.Marker(
            [lat, lon],
            ###1C9AD6 (blue background color for Marker alternative)
            icon=folium.DivIcon(html=f"""
                <div style="
                    width:60px;
                    height:60px;
                    border-radius:50%;
                    background:#ff4c00;  
                    color:white;
                    font-weight:bold;
                    font-size:28px; 
                    display:flex;
                    align-items:center;
                    justify-content:center;
                    border:2px solid white;">
                    {num}
                </div>
            """)
        ).add_to(m)

     # Auto-fit map to all markers
    bounds = [[lat, lon] for lat, lon, _, _ in locations]
    m.fit_bounds(bounds, padding=(20, 20))
    # html_file = "map.html"
    # m.save(html_file)

    legend_items = ""
    for lat, lon, num, addr in locations:
        legend_items += f"""
            <div style="margin-bottom:4px;">
                <span style="
                    display:inline-block;
                    width:18px;
                    height:18px;
                    line-height:18px;
                    text-align:center;
                    border-radius:50%;
                    background:#ff4c00;
                    color:white;
                    font-size:11px;
                    font-weight:bold;
                    margin-right:6px;">
                    {num}
                </span>
                <span style="font-size:12px;">{addr}</span>
            </div>
        """
    legend_html = f"""
    <div id="map-legend" class="custom-legend"  style="
        position: fixed;
        bottom: 30px;
        left: 30px;
        width: 280px;
        max-height: 240px;
        overflow-y: auto;
        background: white;
        border: 1px solid #ccc;
        border-radius: 6px;
        padding: 10px;
        font-family: Arial, sans-serif;
        font-size: 12px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.3);
        z-index: 9999;
    ">
        <div style="font-weight:bold; margin-bottom:6px;">
            Locations
        </div>
        {legend_items}
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))
    # Auto-fit map to all markers
    bounds = [[lat, lon] for lat, lon, _, _ in locations]
    m.fit_bounds(bounds, padding=(30, 30))
    html_file = "map.html"
    m.get_root().html.add_child(folium.Element("""
    <style>
    html, body {
        margin: 0;
        padding: 0;
        width: 100%;
        height: 100%;
    }

    .folium-map {
        width: 100vw !important;
        height: 100vh !important;
    }
    </style>
    """))
    m.save(html_file)

    temp_png = "highres_map.png"
    html_to_png(html_file, temp_png, width_px, height_px)
    #scale_image_to_pdf(temp_png, output_png)
    img = Image.open(temp_png)
    left = map_width * 0.25       # 25% from left
    upper = map_height * 0.2     # 25% from top
    right = map_width * 0.75      # 75% from left
    lower = map_height * 0.7    # 75% from top
    cropped_img = img.crop((left, upper, right, lower))
    cropped_img.save("map.png")

if __name__ == "__main__":
    import pandas as pd
    spaces_excel_path='CostarExport.xlsx'
    summary_df = pd.read_excel(spaces_excel_path, sheet_name=0)
    create_image(summary_df, "map.png")
    output_png = "map.png"


###
# Map div = the physical actual size of the map,   Folium map div.
# Viewport = the camera you take the photo , size of the camera