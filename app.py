import streamlit as st
import networkx as nx
import random
import matplotlib.pyplot as plt
import pandas as pd

st.set_page_config(layout="wide")

st.title(" Network Load Simulation Dashboard")

# -----------------------------
# SIDEBAR INPUT (BETTER UI)
# -----------------------------
st.sidebar.header("Simulation Settings")

num_pcs = st.sidebar.number_input("Workstations", min_value=1, value=5, step=1)
time_steps = st.sidebar.number_input("Time Steps", min_value=1, value=5, step=1)

min_bw = st.sidebar.number_input("Min Bandwidth (Mbps)", value=50)
max_bw = st.sidebar.number_input("Max Bandwidth (Mbps)", value=100)

if min_bw > max_bw:
    st.sidebar.error("Min > Max not allowed")
    st.stop()

# -----------------------------
# CREATE NETWORK
# -----------------------------
G = nx.DiGraph()
server = "Server1"
pcs = [f"PC{i}" for i in range(1, int(num_pcs)+1)]

G.add_node(server)
G.add_nodes_from(pcs)

for pc in pcs:
    bandwidth = random.randint(int(min_bw), int(max_bw))
    G.add_edge(server, pc, capacity=bandwidth)

# -----------------------------
# RUN BUTTON CENTERED
# -----------------------------
col1, col2, col3 = st.columns([1,2,1])
with col2:
    run = st.button("Run Simulation")

if run:

    combined_data = []
    avg_utils = []
    max_utils = []
    min_utils = []

    for t in range(int(time_steps)):

        traffic = {}
        utilization_list = []

        for pc in pcs:
            load = random.randint(10, 120)
            traffic[(server, pc)] = load

        for edge in G.edges:
            capacity = G.edges[edge]['capacity']
            load = traffic[edge]

            utilization = load / capacity
            utilization_list.append(utilization)

            if load > capacity:
                status = "Bottleneck"
            elif utilization > 0.8:
                status = "Near Peak"
            else:
                status = "Normal"

            combined_data.append({
                "T": t + 1,
                "Conn": f"{edge[0]}→{edge[1]}",
                "Load": load,
                "Cap": capacity,
                "Util": round(utilization, 2),
                "Status": status
            })

        avg_utils.append(sum(utilization_list)/len(utilization_list))
        max_utils.append(max(utilization_list))
        min_utils.append(min(utilization_list))

    # -----------------------------
    # METRICS (TOP CARDS)
    # -----------------------------
    st.subheader("Overview")

    col1, col2, col3 = st.columns(3)
    col1.metric("Avg Utilization", round(sum(avg_utils)/len(avg_utils), 2))
    col2.metric("Peak Utilization", round(max(max_utils), 2))
    col3.metric("Min Utilization", round(min(min_utils), 2))

    # -----------------------------
    # COMPACT TABLE
    # -----------------------------
    st.subheader("Simulation Data")

    df = pd.DataFrame(combined_data)

    # 👉 MINIMIZE TABLE (small + clean)
    st.dataframe(
        df,
        use_container_width=True,
        height=250   # 👈 compact height
    )

    # -----------------------------
    # GRAPH
    # -----------------------------
    st.subheader("Utilization Trend")

    fig, ax = plt.subplots()

    ax.plot(range(1, int(time_steps)+1), avg_utils, marker='o', label="Avg")
    ax.plot(range(1, int(time_steps)+1), max_utils, linestyle='--', label="Max")
    ax.plot(range(1, int(time_steps)+1), min_utils, linestyle=':', label="Min")

    ax.axhline(y=0.8, linestyle='--', label="80%")
    ax.axhline(y=1.0, linestyle='-', label="100%")

    ax.set_xlabel("Time")
    ax.set_ylabel("Utilization")
    ax.legend()
    ax.grid(True)

    st.pyplot(fig)