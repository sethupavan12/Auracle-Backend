import os, json, requests


def add_Item(query: str) -> str:

    url = "https://api.monday.com/v2"

    headers = {
    'Authorization': os.getenv("MONDAY_API_KEY"),
    'Content-Type': 'application/json'
}

    payload = json.dumps({
        "query": f"mutation {{create_item (board_id: 1216344722, group_id: \"topics\", item_name: \"{query}\") {{id}}}}"
    })

    response = requests.request("POST", url, headers=headers, data=payload)
    
    if response.status_code == 200:
        return "Item added successfully"
    else:
        return f"Request failed: {response.text}"
    
