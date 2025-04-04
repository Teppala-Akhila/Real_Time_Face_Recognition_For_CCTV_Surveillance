import cv2
import numpy as np
import face_recognition
import os
import json
from datetime import datetime
import pandas as pd

class FaceRecognitionSystem:
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_metadata = []
        # Ensure data directory exists
        if not os.path.exists('data/faces'):
            os.makedirs('data/faces')
        # Initialize or create face_data.xlsx if it doesn't exist
        if not os.path.exists('data/face_data.xlsx'):
            df = pd.DataFrame(columns=['name', 'age', 'gender', 'phone', 'aadhar', 'image_filename'])
            df.to_excel('data/face_data.xlsx', index=False)
        self.load_known_faces()

    def load_known_faces(self):
        """Load all known faces from the data directory"""
        try:
            # Clear existing data
            self.known_face_encodings = []
            self.known_face_metadata = []
            
            # Read the Excel file
            if os.path.exists('data/face_data.xlsx'):
                df = pd.read_excel('data/face_data.xlsx')
                
                # Load each face and its metadata
                for index, row in df.iterrows():
                    image_path = os.path.join('data/faces', str(row['image_filename']))
                    
                    if os.path.exists(image_path):
                        # Load and encode face
                        face_image = face_recognition.load_image_file(image_path)
                        face_encodings = face_recognition.face_encodings(face_image)
                        
                        if len(face_encodings) > 0:
                            self.known_face_encodings.append(face_encodings[0])
                            self.known_face_metadata.append({
                                'name': str(row['name']),
                                'age': str(row['age']),
                                'gender': str(row['gender']),
                                'phone': str(row['phone']),
                                'aadhar': str(row['aadhar']),
                                'image_filename': str(row['image_filename'])
                            })
                            print(f"Loaded face: {row['name']}")
                        else:
                            print(f"No face found in image: {image_path}")
                    else:
                        print(f"Image file not found: {image_path}")
                
                print(f"Loaded {len(self.known_face_encodings)} faces")
            else:
                print("face_data.xlsx not found")
                
        except Exception as e:
            print(f"Error loading known faces: {e}")

    def register_new_face(self, image_data, metadata):
        """Register a new face with the system"""
        try:
            # Create faces directory if it doesn't exist
            if not os.path.exists("data/faces"):
                os.makedirs("data/faces")

            # Generate unique filename using timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_filename = f"{metadata['name']}_{timestamp}.jpg"
            metadata_filename = f"{metadata['name']}_{timestamp}.json"

            # Save the image
            image_path = os.path.join("data/faces", image_filename)
            cv2.imwrite(image_path, image_data)

            # Compute face encoding
            face_encodings = face_recognition.face_encodings(image_data)
            if len(face_encodings) == 0:
                raise ValueError("No face found in the image")

            face_encoding = face_encodings[0]

            # Save metadata
            metadata_path = os.path.join("data/faces", metadata_filename)
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f)

            # Add to known faces
            self.known_face_encodings.append(face_encoding)
            self.known_face_metadata.append(metadata)

            return True, "Face registered successfully"

        except Exception as e:
            return False, f"Error registering face: {str(e)}"

    def process_frame(self, frame):
        """Process a video frame and return recognition results"""
        try:
            # Resize frame for faster processing
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            
            # Find face locations
            face_locations = face_recognition.face_locations(rgb_small_frame)
            
            if not face_locations:
                return frame, None
            
            # Get face encodings
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
            
            for face_encoding, (top, right, bottom, left) in zip(face_encodings, face_locations):
                # Check if we have any known faces
                if len(self.known_face_encodings) > 0:
                    # Compare faces
                    matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding, tolerance=0.6)
                    face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                    
                    if True in matches:
                        best_match_index = np.argmin(face_distances)
                        if matches[best_match_index]:
                            # Get matching person's data
                            person_data = self.known_face_metadata[best_match_index]
                            match_percentage = (1 - face_distances[best_match_index]) * 100
                            
                            # Scale back up face locations
                            top *= 4
                            right *= 4
                            bottom *= 4
                            left *= 4
                            
                            # Draw rectangle and label
                            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
                            font = cv2.FONT_HERSHEY_DUPLEX
                            cv2.putText(frame, person_data['name'], 
                                      (left + 6, bottom - 6), font, 0.6, (255, 255, 255), 1)
                            
                            return frame, {
                                'match_percentage': f"{match_percentage:.1f}",
                                'name': person_data['name'],
                                'age': person_data['age'],
                                'gender': person_data['gender'],
                                'phone': person_data['phone'],
                                'aadhar': person_data['aadhar']
                            }
            
            return frame, None
            
        except Exception as e:
            print(f"Error in face recognition: {e}")
            return frame, None

    def add_new_face(self, image: np.ndarray, metadata: dict) -> bool:
        """Add a new face to the recognition system"""
        try:
            # Convert image to RGB if it's in BGR
            if len(image.shape) == 3 and image.shape[2] == 3:
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            else:
                rgb_image = image

            # Get face encodings
            face_encodings = face_recognition.face_encodings(rgb_image)
            
            if len(face_encodings) == 0:
                print("No face detected in the image")
                return False
            
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_filename = f"{metadata['name'].lower().replace(' ', '_')}_{timestamp}.jpg"
            
            # Add face encoding and metadata
            self.known_face_encodings.append(face_encodings[0])
            metadata['image_filename'] = image_filename
            self.known_face_metadata.append(metadata)
            
            # Save image to faces directory
            cv2.imwrite(os.path.join('data/faces', image_filename), image)
            
            # Update Excel file
            df = pd.DataFrame(self.known_face_metadata)
            df.to_excel('data/face_data.xlsx', index=False)
            
            print(f"Successfully added new face: {metadata['name']}")
            return True
            
        except Exception as e:
            print(f"Error adding new face: {e}")
            return False 