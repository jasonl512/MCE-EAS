# Manhattan Street Network Flow Map Prototype

A Jupyter Notebook prototype that models a maximum-flow problem on a Manhattan street network and displays the street segments on an interactive map. The notebook is an early network-analysis prototype; it does not calculate a NYC GreenScore or Seattle Green Factor score.

## Folder contents

```text
manhattan-map-prototype/
├── README.md
├── requirements.txt
└── manhattan_street_network_prototype.ipynb
```

- `manhattan_street_network_prototype.ipynb` — imports the street-network CSV, builds and solves the flow optimization model, calculates a relative flow measure for the segments, and draws the network map.
- `requirements.txt` — lists the third-party Python libraries imported by the notebook.
- `README.md` — project overview, data requirements, setup, run instructions, and prototype limitations.

## What the notebook does

1. Reads a CSV street graph into a pandas DataFrame.
2. Treats each street segment as a directed edge with a capacity.
3. Uses OR-Tools' GLOP linear solver to maximize flow from the selected source node to the selected sink node, subject to edge capacities and flow conservation at intermediate nodes.
4. Merges the solved edge flows with the street data and calculates `utilization` as each edge's solved flow divided by the largest solved edge flow.
5. Displays Manhattan street segments using Plotly's map visualization.

The notebook comments identify the intended source as the World Trade Center (`42453395`) and the sink as Hunter College (`42431678`). Confirm that these node IDs are present and correspond to the intended places in your dataset before interpreting results.

## Required input data

The notebook expects a street-capacity CSV. The original notebook reads this local file:

```text
C:\Users\DELL\Downloads\manhattan_street_capacities (1).csv
```

That data file is not included in this folder. Add the dataset you are authorized to use, then update the `file_path` value in the first notebook cell to point to its location. The CSV is expected to contain these columns:

| Column | Use in notebook |
| --- | --- |
| `source_osm` | Origin node ID for a directed street segment |
| `target_osm` | Destination node ID for a directed street segment |
| `capacity` | Capacity assigned to the segment |
| `u_lat`, `u_lon` | Coordinates for one endpoint of the segment |
| `v_lat`, `v_lon` | Coordinates for the other endpoint |

Capacity units and the method used to estimate capacity come from the input dataset; the notebook does not define or validate them. Make sure the dataset's direction conventions and capacity values are suitable for your analysis.

## Requirements

- Python with Jupyter Notebook or JupyterLab
- Python packages listed in `requirements.txt`

Install the packages from a terminal with:

```bash
python -m pip install -r requirements.txt
```

## Run the prototype

1. Download or place the street-capacity CSV where you can access it.
2. Open `manhattan_street_network_prototype.ipynb` in Jupyter.
3. Edit `file_path` in the first cell so it points to your CSV.
4. Run the notebook cells from top to bottom.
5. Review the solver's objective value and printed segment results, then inspect the interactive map output.

## Current map output and limitations

- The current map draws all street segments as neutral gray lines over a Carto Dark Matter basemap. It does not color or size streets by flow, and it does not mark the source and sink on the map.
- `utilization` is a relative measure normalized by the largest solved edge flow. It is not the fraction of a segment's capacity that is being used.
- The notebook is a prototype and does not currently validate the solver status, data schema, missing values, capacity units, or whether the chosen node IDs exist in the graph.
- Results depend on the input street graph, its edge directions, capacities, and the chosen source and sink.
- This notebook models street-network flow. It does not evaluate green infrastructure projects, estimate project costs or construction duration, or calculate a green-factor score.

## Suggested next steps

- Include the permitted source dataset and document its origin, license, capacity units, and preparation method.
- Check solver status and validate the input columns, node IDs, capacities, and coordinate values before interpreting results.
- If desired, update the visualization to encode edge flow or capacity usage and to mark the source and sink.
