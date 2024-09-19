# File containing our API built with FASTAPI

import json
import pathlib
from typing import List, Union

from fastapi import FastAPI, Response
from contextlib import asynccontextmanager


from models import Track

# instantiate the FastAPI app
app = FastAPI()

# create container for our data - to be loaded at app startup.
data = []

# define app start-up event but on_event() is depreciated
# we must use lifespan() syntax now...
# see https://www.youtube.com/watch?v=IfmsB6R9W4o

@asynccontextmanager
async def lifespan(app: FastAPI):
    
    # Perform here the startup tasks
    DATAFILE = pathlib.Path() / 'data' / 'tracks.json'
    with open(DATAFILE, 'r') as f:
        tracks = json.load(f)
        for track in tracks:
            data.append(Track(**track).model_dump())

    yield

    # Perform here the shutdown tasks if needed (optional)

app = FastAPI(lifespan=lifespan)

# Endpoint n°1 : Get All Tracks
@app.get('/tracks/', response_model=List[Track])
def tracks():
    return data

# Endpoint n°2 : Get Track by ID
@app.get('/tracks/{track_id}/', response_model=Union[Track, str])
def track(track_id: int, response: Response):
    # find the track with the given ID, or None if it does not exist
    track = next(
        (track for track in data if track["id"] == track_id), None
    )
    if track is None:
        # if a track with given ID doesn't exist, set 404 code and return string
        response.status_code = 404
        return "Track not found"
    return track

# Endpoint n°3 : Create a New Track
# To create a new track, we're going to use a POST request. This will add the new track - if it has a valid structure - to our global data list
@app.post("/tracks/", response_model=Track, status_code=201)
def create_track(track: Track):
    track_dict = track.dict()
    
    # assign track next sequential ID
    track_dict['id'] = max(data, key=lambda x: x['id']).get('id') + 1
    
    # append the track to our data and return 201 response with created resource
    data.append(track_dict)
    return track_dict