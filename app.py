from fastapi import FastAPI, HTTPException
import psycopg2
from decouple import config

app = FastAPI()

# PostgreSQL connection parameters
db_params = {
    "dbname": config('dbname'),
    "user": config('user'),
    "password": config('password'),
    "host": config('host'),
    "port": config('port'),
}

def execute_query(query, params=None):
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
    result = cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()
    return result

@app.get("/")
async def root():
    return {"page": "Main page!", "info": "Python FastAPI and Postgres API", "availableRoutes": ["/cookie/all", "/cookie/random", "/cookie/add"]}

@app.post("/cookie/add/")
def add_message(message: str):
    query = "INSERT INTO fortune_messages (message) VALUES (%s) RETURNING id, message"
    result = execute_query(query, (message,))
    return {"id": result[0][0], "message": result[0][1]}

@app.get("/cookie/all/")
def show_all_messages():
    query = "SELECT id, message FROM fortune_messages"
    result = execute_query(query)
    messages = [{"id": row[0], "message": row[1]} for row in result]
    return messages

@app.delete("/cookie/delete/{message_id}")
def delete_message(message_id: int):
    query = "DELETE FROM fortune_messages WHERE id = %s RETURNING id, message"
    result = execute_query(query, (message_id,))
    if not result:
        raise HTTPException(status_code=404, detail="Message not found")
    return {"id": result[0][0], "message": result[0][1]}

@app.get("/cookie/random/")
def get_random_message():
    query = "SELECT id, message FROM fortune_messages ORDER BY random() LIMIT 1"
    result = execute_query(query)
    if not result:
        raise HTTPException(status_code=404, detail="No messages available")
    return {"id": result[0][0], "message": result[0][1]}


import uvicorn
if __name__ == "__main__":
  uvicorn.run("server.api:app", host="0.0.0.0", port=8000, reload=True)