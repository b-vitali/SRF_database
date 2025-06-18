# Database for SRF cavities
This project wants to be a database of the test results of SRF cavities

> [!WARNING]
>
> The project is in an early phase... Much could be wrong and much will change

The main idea is the following:
1. Use a combination of `python` + `SQLite` to collect the data
2. Use a `python` based UI to query, browse and visualize the data

## Use
### Create database (if missing)
The data (see structure below) is stored in the `data` folder.

To generate the database run `python collect_database.py`

### Streamlit
The streamlit interface to query, plot and create add new data can be run online via a streamlit.app or locally running it in the browser

To open the browsing UI run `streamlit run SRF_database.py`

> [!IMPORTANT]
>
> This second command will depend on the UI design
>
> Currently `sltreamlit` is being used but this might change

Refer to the [streamlit_README.md](utils/streamlit_README.md) for more details on the user interface.

### Add new data/results
The streamlit UI has a dedicated page to add new data

After filling the info, a zip is downloaded: **Un-zip** it and to place it in `data`

At this point is sufficent to run `python collect_database.py`

## Requirements
In addition to a working `python` installation (`sqlite3` should be in `python3`), you will need 
```
pip install pandas matplotlib streamlit
``` 
As Mentioned, `sltreamlit` might be later dropped in favour of another UI

## Structure
The aim is to structure the project as follows (please ignore the temporary test files) 

```
📁 SRF_database
├── 📄 README.md
├── 📄 requirements.txt
├── 🐍 collect_database.py
├── 🐍 SRF_database.py
├── 📁 utils
│ │ ├── 🐍 new_experiment.py
│ │ └── 🐍 utils.py
├── 📁 data
│ ├── 💾 srf_database.db
│ ├── 📁 cavity1
│ │ ├── 📄 metadata.json
│ │ ├── 📄 cavity1_data.txt
│ │ ├── 🖼️ plot1.png
│ │ ...
│ │ └── 🖼️ plotn.png
│ ├── 📁 cavity2
│ ...
```

The final structure of the `data.txt` is still under discussion

The structure of the `metadata.json` will probably resemble something like this

```
{
  "experiment_name": "FNAL_103.1",
  "lab_name": "FNAL",
  "description": "Lore lipsium (data)",
  "date": "2025-01-28",
  "article_url": "https://arxiv.org/abs/2401.12345", 
  "processing_steps": [
    {
      "process_type": "EP",
      "description": "EP 120um",
      "tags": "EP"
    },
    {
      "process_type": "baking",
      "description": "baking 75C for 3h",
      "temperature C": 75,
      "duration h": 3,
      "tags": "lowT"
    },
    {
      "process_type": "BCP",
      "description": "BCP 20um",
      "tags": "BCP"
    }
  ]
}
```

What information will be stored in the metadata is under discussion

