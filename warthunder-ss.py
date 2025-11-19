import bs4
import httpx
import asyncio
import json
from fastapi import FastAPI

app = FastAPI()
client = httpx.AsyncClient()

async def get_squadron_page_html(squadronName):
    squadronInfoLink = "https://warthunder.com/en/community/claninfo/" + "%20".join(squadronName.split())
    response = await client.get(squadronInfoLink)
    return response  # Use response.text instead of response.content


async def get_players_ratings_from_squadron(squadronName):
    html = await get_squadron_page_html(squadronName)
    soup = bs4.BeautifulSoup(html.content, "html.parser")
    table = soup.find(class_="squadrons-members__table")
    tableElements = table.find_all(class_="squadrons-members__grid-item")
    playerData = {}
    rowCounter = 0
    for row in tableElements:
        if rowCounter == 1:
            playerKey = row.text.strip()
        elif rowCounter == 2:
            # Strip the text and check if it's a valid integer
            playerRating_str = row.text.strip()
            if playerRating_str.isdigit():  # Ensure the text is numeric
                playerRating = int(playerRating_str)
            else:
                playerRating = None  # Set to None if the value isn't valid
        elif rowCounter == 3:
            playerActivity_str = row.text.strip()
            playerActivity = int(playerActivity_str) if playerActivity_str.isdigit() else None
        elif rowCounter == 4:
            playerRank = row.text.strip()
        elif rowCounter == 5:
            playerJoinDate = row.text.strip()
            playerData[playerKey] = {
                "rating": playerRating,
                "activity": playerActivity,
                "rank": playerRank,
                "joindate": playerJoinDate,
            }
        rowCounter = (rowCounter + 1) % 6
    return playerData

@app.get("/squadron/{squadronName}")
async def get_squadron_data(squadronName: str):
    playerData = await get_players_ratings_from_squadron(squadronName)
    return playerData

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
