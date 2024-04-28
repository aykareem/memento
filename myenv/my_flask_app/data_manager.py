from typing import List
from models import Profile  # Assuming Profile is defined in another file
import image_recognition as ir

# A list to store profiles
profiles = []  # This can be moved to a more persistent storage if needed

def add_profile(name: str, relation: str, picture: str):
    if not name:
        raise ValueError("Name cannot be empty")
    if not picture:
        raise ValueError("No Picture?")
    
    # Create a new profile
    new_profile = Profile(name=name, picture=picture)
    
    # Add to the list of profiles
    profiles.append(new_profile)
    
    return new_profile

def match(image: str):
    if(len(profiles) == 0):
        print("No profiles")
    maxperson = None
    max = 0.15
    for person in profiles:
        matching_score = ir.detect_and_compare_faces(image, person.picture)
        if(matching_score > max):
            max = matching_score
            maxperson = person
        
    return maxperson.name, maxperson.relation

