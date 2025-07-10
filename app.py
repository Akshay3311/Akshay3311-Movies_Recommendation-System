import streamlit as st
import pickle
import pandas as pd
import requests
import os

st.set_page_config(page_title="Movie Recommender System", layout="wide")

# --- Utility: Download from Google Drive ---
def download_file_from_google_drive(file_id, destination):
    URL = "https://docs.google.com/uc?export=download"

    session = requests.Session()
    response = session.get(URL, params={'id': file_id}, stream=True)

    # Get confirmation token for large files
    def get_confirm_token(response):
        for key, value in response.cookies.items():
            if key.startswith('download_warning'):
                return value
        return None

    token = get_confirm_token(response)

    if token:
        params = {'id': file_id, 'confirm': token}
        response = session.get(URL, params=params, stream=True)

    CHUNK_SIZE = 32768
    with open(destination, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk:
                f.write(chunk)


# --- Download pickle files if not already available ---
if not os.path.exists("movie_dict.pkl"):
    download_file_from_google_drive("1YRnkQWvKLRBuYEEuRKr_3aSs6CJtOS_P", "movie_dict.pkl")

if not os.path.exists("similirity.pkl"):
    download_file_from_google_drive("1b-7pReOsOBD1a__hQVj0ZI8E0a3wauXL", "similirity.pkl")

# --- Load data ---
movies = pickle.load(open('movie_dict.pkl', 'rb'))
movies_df = pd.DataFrame(movies)
similarity = pickle.load(open('similirity.pkl', 'rb'))

# --- Poster Fetch Function ---
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        poster_path = data.get('poster_path')
        if poster_path:
            return "https://image.tmdb.org/t/p/w500" + poster_path
        else:
            return "https://via.placeholder.com/300x450?text=No+Image"
    except Exception as e:
        print(f"Error fetching poster: {e}")
        return "https://via.placeholder.com/300x450?text=Error"

# --- Recommendation Logic ---
def recommend(movie):
    index = movies_df[movies_df['title'] == movie].index[0]
    distances = similarity[index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_posters = []
    for i in movie_list:
        movie_id = movies_df.iloc[i[0]].movie_id
        recommended_movies.append(movies_df.iloc[i[0]].title)
        recommended_posters.append(fetch_poster(movie_id))
    return recommended_movies, recommended_posters

# --- UI ---
st.markdown("<h1 style='text-align: center; color: white;'>🎬 Movie Recommender System</h1>", unsafe_allow_html=True)
selected_movie_name = st.selectbox("Select a movie:", movies_df['title'].values)

if st.button("Show Recommendation"):
    names, posters = recommend(selected_movie_name)

    st.markdown("## Top 5 Recommendations")
    cols = st.columns(5)
    for idx, col in enumerate(cols):
        with col:
            st.image(posters[idx])
            st.caption(names[idx])
