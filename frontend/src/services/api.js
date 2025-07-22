export async function fetchTrends(county, month){
    const res = await fetch("https://localhost:8000/api/trends?county=${county}&month=${month}")
    return res.json()
}

