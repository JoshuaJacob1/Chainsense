import uvicorn
import os

if __name__ == "__main__":
    print("Starting ChainSense backend...")
    
    # Ensure data directory exists
    os.makedirs(os.path.join(os.path.dirname(__file__), "../data"), exist_ok=True)
    
    # Run the FastAPI server
    uvicorn.run("server:app", host="127.0.0.1", port=8001, reload=True)
