# main.py
from dotenv import load_dotenv
import os
import streamlit as st
from recommend import df, recommend_movies
from omdb_utils import get_movie_details
import requests

load_dotenv()
OMDB_API_KEY = os.getenv("OMDB_API_KEY")


st.set_page_config(
    page_title="Movie Recommender",
    page_icon="🎬",
    layout="centered"
)

st.title("🎬 Movie Recommender")

# --- Initialize session states ---
if "saved_movies" not in st.session_state:
    st.session_state["saved_movies"] = []

if "show_recommendations" not in st.session_state:
    st.session_state["show_recommendations"] = False

# --- Movie Selection ---
movie_list = sorted(df['title'].dropna().unique())
selected_movie = st.selectbox("🎬 Select a movie:", movie_list)

min_rating = st.slider("⭐ Minimum IMDb Rating:", 0.0, 10.0, 0.0, 0.5)

# --- Recommend Button ---
if st.button("🚀 Recommend Similar Movies"):
    st.session_state["show_recommendations"] = True
    st.session_state["current_movie"] = selected_movie

# --- Show Recommendations ---
if st.session_state.get("show_recommendations", False):
    movie = st.session_state["current_movie"]
    recommendations = recommend_movies(movie)

    if recommendations is None or recommendations.empty:
        st.warning("Sorry, no recommendations found.")
    else:
        # Filter by IMDb rating using OMDb API
        filtered_recs = []
        for _, row in recommendations.iterrows():
            title = row['title']
            plot, poster = get_movie_details(title, OMDB_API_KEY)
            url = f"http://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}"
            res = requests.get(url).json()
            rating = float(res.get("imdbRating", 0)) if res.get("imdbRating", "N/A") != "N/A" else 0
            if rating >= min_rating:
                filtered_recs.append((title, plot, poster, rating))

        if not filtered_recs:
            st.warning(f"No movies found with IMDb rating ≥ {min_rating}.")
        else:
            st.success(f"Top movies similar to: {movie} with rating ≥ {min_rating}")
            for title, plot, poster, rating in filtered_recs:
                with st.container():
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        if poster != "N/A":
                            st.image(poster, width=100)
                    with col2:
                        st.markdown(f"### {title} ⭐ {rating}")
                        st.markdown(f"*{plot}*" if plot != "N/A" else "_Plot not available_")
                        youtube_search = f"https://www.youtube.com/results?search_query={title.replace(' ', '+')}+trailer"
                        st.markdown(f"[▶️ Watch Trailer]({youtube_search})", unsafe_allow_html=True)

                        if st.button(f"💾 Save '{title}'", key=f"save_{title}"):
                            if title not in st.session_state["saved_movies"]:
                                st.session_state["saved_movies"].append(title)
                                st.success(f"✅ Saved '{title}'!")


# --- "For You" Section ---
if st.session_state["saved_movies"]:
    st.markdown("---")
    st.subheader("🎯 For You (Personalized Recommendations)")

    for saved in st.session_state["saved_movies"]:
        with st.expander(f"📌 {saved}"):
            recs = recommend_movies(saved)
            if recs is not None:
                for _, row in recs.iterrows():
                    title = row['title']
                    plot, poster = get_movie_details(title, OMDB_API_KEY)
                    with st.container():
                        col1, col2 = st.columns([1, 3])
                        with col1:
                            if poster != "N/A":
                                st.image(poster, width=100)
                        with col2:
                            st.markdown(f"**{title}**")
                            st.markdown(f"*{plot}*" if plot != "N/A" else "_Plot not available_")
            else:
                st.warning("No recommendations found.")