def render_timeline():
    import pandas as pd
    import plotly.express as px
    from pathlib import Path
    import json

    memory_path = Path("ingested/memory.jsonl")
    if not memory_path.exists():
        st.info("Aucune donnée mémoire disponible.")
        return

    with open(memory_path, encoding="utf-8") as f:
        entries = [json.loads(line) for line in f]

    data = []
    for e in entries:
        data.append({
            "date": e["metadata"]["created_at"][:10],
            "event": e["metadata"]["filename"],
            "category": e["metadata"]["source"]
        })

    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["date"])
    fig = px.timeline(df, x_start="date", x_end="date", y="category", color="category", text="event")
    fig.update_yaxes(autorange="reversed")
    st.plotly_chart(fig, use_container_width=True)
