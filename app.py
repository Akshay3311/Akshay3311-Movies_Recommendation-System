import streamlit as st
import pickle
import pandas as pd
import requests

st.set_page_config(page_title="Movie Recommender System", layout="wide")


movies = pickle.load(open('movie_dict.pkl', 'rb'))
movies_df = pd.DataFrame(movies)

similirity = pickle.load(open('similirity.pkl', 'rb'))

def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
        print("Fetching URL:", url)
        response = requests.get(url, timeout=5)
        data = response.json()
        poster_path = data.get('poster_path')
        print("Poster Path:", poster_path)

        if poster_path:
            return "https://image.tmdb.org/t/p/w500" + poster_path
        else:
            return "https://via.placeholder.com/300x450?text=No+Image"
    except Exception as e:
        print(f"Error fetching poster: {e}")
        return "https://via.placeholder.com/300x450?text=No+Image"


# Recommend movies
def recommend(movie):
    index = movies_df[movies_df['title'] == movie].index[0]
    distances = similirity[index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_posters = []
    for i in movie_list:
        movie_id = movies_df.iloc[i[0]].movie_id
        recommended_movies.append(movies_df.iloc[i[0]].title)
        recommended_posters.append(fetch_poster(movie_id))
    return recommended_movies, recommended_posters

# UI
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


def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        poster_path = data.get('poster_path')
        if poster_path:
            return "https://image.tmdb.org/t/p/w500" + poster_path
        else:
            return "https://via.placeholder.com/300x450?text=No+Poster"
    except Exception as e:
        print("Error fetching poster:", e)
        return "https://via.placeholder.com/300x450?text=Error"