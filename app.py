import streamlit as st 
import pickle
import pandas as pd
import requests 
import time

MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

def fetch_poster(movie_id):
    retries = 0
    while retries < MAX_RETRIES:
        try:
            url = "https://api.themoviedb.org/3/movie/{}?api_key=818e8b42f49256e36cbf23df0786bd85".format(movie_id)
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for 4XX or 5XX status codes
            data = response.json()
            poster_path = data['poster_path']
            full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
            return full_path
        except requests.exceptions.RequestException as e:
            if isinstance(e, requests.exceptions.ConnectionError) and retries < MAX_RETRIES - 1:
                st.warning("Error fetching data from the API. Retrying...")
                retries += 1
                time.sleep(RETRY_DELAY)
            else:
                st.error("Error fetching data from the API. Please try again later.")
                st.error(str(e))  # Display the specific error message for debugging
                return None

def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movie_list = sorted(list(enumerate(distances)),reverse=True,key = lambda x: x[1])[1:6]
    
    recommended_movies = []
    recommended_movies_posters = []
    for i in movie_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        poster = fetch_poster(movie_id)
        if poster:  # Check if the poster is fetched successfully
            recommended_movies_posters.append(poster)
        
    return recommended_movies, recommended_movies_posters

movies_dict = pickle.load(open('movie_list.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

st.title('Movie Recommender System')

selected_movie_name = st.selectbox("Select a movie:", movies['title'].values)

if st.button('Recommend'):
    names, posters = recommend(selected_movie_name)
    
    columns = st.columns(len(names))  # Create columns based on the number of recommended movies
    for i, (name, poster) in enumerate(zip(names, posters)):
        with columns[i]:  # Iterate through the columns
            st.text(name)
            st.image(poster)
